#!/usr/bin/env python3
"""MYEVIEW — One-shot deployment setup script.

Run:  python setup.py

This script is idempotent: it detects which steps have already been completed
and skips them on re-run.  It does NOT start or restart services that are already
running.

Steps performed:
  0. Install system dependencies (apt-get) if on Debian/Ubuntu
  1. Create backend/.env from .env.example (generates a random SECRET_KEY)
  1b. Create a Python virtual environment (.venv/) — needed for PEP 668
  2. Install Python dependencies (pip install -r backend/requirements.txt)
  3. Install Node dependencies (npm ci || npm install)
  4. Build the frontend (npm run build)
  5. Run Alembic migrations (creates tables if they don't exist)
  6. Verify reference data is seeded (seeds if empty)
  7. Print next-step instructions

Prerequisites:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL (running, accessible at DATABASE_URL)
  - Redis (running, accessible at REDIS_URL)

If PostgreSQL/Redis are not running, this script can start them via Docker:
  python setup.py --docker-infra
"""

from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SETUP_MARKER = BACKEND_DIR / ".setup_complete"
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = str(VENV_DIR / "bin" / "python")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(msg: str, level: str = "info") -> None:
    colors = {"info": GREEN + "✓", "warn": YELLOW + "!", "error": RED + "✗", "step": BOLD}
    prefix = colors.get(level, "")
    print(f"{prefix} {msg}{RESET}")


def run(cmd: list[str], cwd: Path | None = None, check: bool = True, show_output_on_error: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result. On failure, print stderr."""
    result = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    if check and result.returncode != 0:
        if show_output_on_error:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def command_exists(cmd: str) -> bool:
    """Check if a command is available on PATH."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True)
        return True
    except (FileNotFoundError, OSError):
        return False


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def create_virtualenv() -> None:
    """Create a Python virtual environment (needed for PEP 668 / externally-managed envs)."""
    log("Checking virtual environment…", "step")

    if VENV_DIR.exists() and (VENV_DIR / "bin" / "python").exists():
        # Verify the venv is actually functional
        test_result = subprocess.run(
            [str(VENV_DIR / "bin" / "python"), "-c", "import ensurepip"],
            capture_output=True, text=True,
        )
        if test_result.returncode == 0:
            log(".venv/ already exists — skipping", "info")
            return
        else:
            log(".venv/ exists but is broken — recreating", "warn")
            import shutil
            shutil.rmtree(VENV_DIR, ignore_errors=True)

    run([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=PROJECT_ROOT)
    log("Virtual environment created at .venv/", "info")


def install_system_deps() -> None:
    """Install system-level dependencies needed by Python packages (apt-based only)."""
    log("Checking system dependencies…", "step")

    # Only attempt apt-get on Debian/Ubuntu
    if not Path("/usr/bin/apt-get").exists():
        log("Not a Debian/Ubuntu system — skipping apt packages (install manually if needed)", "warn")
        return

    # Quick check: if libpango is present AND python3-venv works, assume system deps are installed
    result = subprocess.run(
        ["dpkg", "-l", "libpango-1.0-0"],
        capture_output=True, text=True,
    )
    venv_ok = subprocess.run(
        [sys.executable, "-c", "import venv; import ensurepip"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and "ii" in result.stdout and venv_ok.returncode == 0:
        log("System dependencies already installed — skipping", "info")
        return

    # Candidate packages — we filter to only those available in apt
    candidate_packages = [
        "python3-pip", "python3-dev", "build-essential",
        "libpq-dev", "libffi-dev", "libssl-dev",
        "libpango-1.0-0", "libpangoft2-1.0-0", "libcairo2",
        "libgdk-pixbuf-2.0-0",  # renamed from libgdk-pixbuf2.0-0 on newer Ubuntu
        "pkg-config", "nmap",
        "python3-venv",
    ]

    # On newer Ubuntu/Debian, the venv module needs a version-specific package
    # e.g. python3.13-venv on Ubuntu 24.04 with Python 3.13
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    venv_pkg = f"python{py_version}-venv"
    candidate_packages.append(venv_pkg)

    # Filter to only packages that actually exist in apt repos
    packages = []
    for pkg in candidate_packages:
        check_pkg = subprocess.run(
            ["apt-cache", "show", pkg],
            capture_output=True, text=True,
        )
        if check_pkg.returncode == 0:
            packages.append(pkg)
        else:
            log(f"  Package {pkg} not found in apt — skipping", "warn")

    if not packages:
        log("No installable packages found — something is wrong with apt", "error")
        sys.exit(1)

    log("Installing system packages via apt-get (requires sudo)…", "step")
    cmd = ["sudo", "apt-get", "update", "-y"]
    run(cmd)
    cmd = ["sudo", "apt-get", "install", "-y"] + packages
    run(cmd)
    log("System dependencies installed", "info")


def ensure_env_file() -> bool:
    """Create backend/.env from .env.example with a generated SECRET_KEY."""
    env_path = BACKEND_DIR / ".env"
    example_path = BACKEND_DIR / ".env.example"

    if env_path.exists():
        log("backend/.env already exists — skipping", "info")
        return False

    if not example_path.exists():
        log("backend/.env.example not found — creating minimal .env", "warn")
        env_path.write_text(
            f"DATABASE_URL=postgresql://myeview:myeview@localhost:5432/myeview\n"
            f"REDIS_URL=redis://localhost:6379/0\n"
            f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
            f"DEBUG=false\n"
            f"CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173\n"
            f"OTX_API_KEY=\n"
        )
    else:
        content = example_path.read_text()
        # Replace the placeholder secret with a real one
        content = content.replace(
            "SECRET_KEY=change-me-in-production",
            f"SECRET_KEY={secrets.token_urlsafe(48)}",
        )
        env_path.write_text(content)

    log("Created backend/.env with generated SECRET_KEY", "info")
    return True


def install_python_deps() -> None:
    """Install Python dependencies from requirements.txt into the virtual environment."""
    log("Checking Python dependencies…", "step")

    # Quick check: is fastapi importable in the venv?
    result = subprocess.run(
        [VENV_PYTHON, "-c", "import fastapi; import sqlalchemy; import celery"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("Python dependencies already installed — skipping", "info")
        return

    req_path = BACKEND_DIR / "requirements.txt"
    if not req_path.exists():
        log("backend/requirements.txt not found", "error")
        sys.exit(1)

    log("Installing Python dependencies (this may take a few minutes)…", "step")
    result = subprocess.run(
        [VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip"],
        capture_output=True, text=True,
    )
    result = subprocess.run(
        [VENV_PYTHON, "-m", "pip", "install", "-r", str(req_path)],
        capture_output=False,  # show live output for long installs
    )
    if result.returncode != 0:
        log("pip install failed — see output above", "error")
        sys.exit(1)
    log("Python dependencies installed", "info")


def install_node_deps() -> None:
    """Install Node.js dependencies."""
    log("Checking Node.js dependencies…", "step")

    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists():
        log("node_modules/ already exists — skipping", "info")
        return

    if not command_exists("npm"):
        log("npm not found on PATH — install Node.js 20+ first", "error")
        sys.exit(1)

    # Try ci first (needs package-lock.json), fall back to install
    lockfile = FRONTEND_DIR / "package-lock.json"
    if lockfile.exists():
        run(["npm", "ci"], cwd=FRONTEND_DIR)
    else:
        run(["npm", "install"], cwd=FRONTEND_DIR)

    log("Node.js dependencies installed", "info")


def build_frontend() -> None:
    """Build the frontend for production."""
    log("Building frontend…", "step")

    dist_dir = FRONTEND_DIR / "dist"
    # Rebuild if dist doesn't exist or is older than source files
    if dist_dir.exists():
        # Check if any source file is newer than dist
        src_dir = FRONTEND_DIR / "src"
        dist_mtime = dist_dir.stat().st_mtime
        needs_rebuild = False
        for src_file in src_dir.rglob("*"):
            if src_file.is_file() and src_file.stat().st_mtime > dist_mtime:
                needs_rebuild = True
                break
        if not needs_rebuild:
            log("frontend/dist/ is up to date — skipping build", "info")
            return

    run(["npm", "run", "build"], cwd=FRONTEND_DIR)
    log("Frontend built to frontend/dist/", "info")


def run_migrations() -> None:
    """Run Alembic database migrations."""
    log("Running database migrations…", "step")

    # Check if migrations have already been run by looking for the alembic_version table
    try:
        result = subprocess.run(
            [VENV_PYTHON, "-c", """
import sys
sys.path.insert(0, 'backend')
from app.config import get_settings
from sqlalchemy import create_engine, inspect
s = get_settings()
engine = create_engine(s.database_url)
insp = inspect(engine)
tables = insp.get_table_names()
if 'alembic_version' in tables:
    print('MIGRATIONS_RUN')
else:
    print('MIGRATIONS_NOT_RUN')
"""],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        if "MIGRATIONS_RUN" in result.stdout:
            log("Database migrations already applied — skipping", "info")
            return
    except Exception:
        pass  # If we can't check, run migrations anyway

    run([VENV_PYTHON, "-m", "alembic", "upgrade", "head"], cwd=BACKEND_DIR)
    log("Database migrations applied", "info")


def verify_reference_data() -> None:
    """Verify that the 8 categories and 27 vectors are seeded."""
    log("Verifying reference data…", "step")

    try:
        result = subprocess.run(
            [VENV_PYTHON, "-c", """
import sys
sys.path.insert(0, 'backend')
from app.config import get_settings
from sqlalchemy import create_engine, text
s = get_settings()
engine = create_engine(s.database_url)
with engine.connect() as conn:
    count = conn.execute(text("SELECT count(*) FROM categories")).scalar()
    if count and count > 0:
        print("SEEDED")
    else:
        print("NOT_SEEDED")
"""],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        if "SEEDED" in result.stdout:
            log("Reference data already seeded — skipping", "info")
            return
    except Exception:
        pass  # If we can't check, run the seed migration

    # Run the seed migration (0002) — it's idempotent (uses INSERT ... ON CONFLICT DO NOTHING)
    run([VENV_PYTHON, "-m", "alembic", "upgrade", "head"], cwd=BACKEND_DIR)
    log("Reference data seeded", "info")


def validate_scoring() -> None:
    """Validate that scoring rules sum to 1000 and reference data is consistent."""
    log("Validating scoring ruleset…", "step")

    result = subprocess.run(
        [VENV_PYTHON, "-c", """
import sys
sys.path.insert(0, 'backend')
from app.scoring.validators import validate_all
validate_all()
print("VALID")
"""],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if "VALID" not in result.stdout:
        log(f"Scoring validation failed:\n{result.stderr}", "error")
        sys.exit(1)
    log("Scoring ruleset validated (sum=1000, vector budgets match)", "info")


def start_docker_infra() -> None:
    """Start PostgreSQL and Redis via docker-compose if they're not running."""
    if not command_exists("docker"):
        log("Docker not found — cannot start infra automatically", "warn")
        log("Ensure PostgreSQL and Redis are running manually before continuing.", "warn")
        return

    log("Starting PostgreSQL and Redis via docker-compose…", "step")
    run(["docker", "compose", "up", "-d", "postgres", "redis"], cwd=PROJECT_ROOT)
    log("Infrastructure services started", "info")

    # Wait for postgres to be ready
    import time
    for i in range(30):
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", "myeview"],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
        )
        if result.returncode == 0:
            log("PostgreSQL is ready", "info")
            break
        time.sleep(1)
    else:
        log("PostgreSQL did not become ready in 30s", "error")
        sys.exit(1)


def print_next_steps() -> None:
    """Print instructions for what to do after setup."""
    print()
    print(f"{BOLD}════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  MYEVIEW Setup Complete{RESET}")
    print(f"{BOLD}════════════════════════════════════════════════════════════{RESET}")
    print()
    print("Next steps:")
    print()
    print("  1. Set the OTX API key (for malware threat intelligence):")
    print("     Edit backend/.env and set OTX_API_KEY=<your-key>")
    print("     Get a free key at: https://otx.alienvault.com/")
    print("     (Without this, the malware vector will produce no data.)")
    print()
    print("  2. Start all services with Docker Compose:")
    print("     docker compose up -d")
    print()
    print("  3. Or run services individually (activate venv first: source .venv/bin/activate):")
    print("     Backend:    cd backend && uvicorn app.main:app --reload")
    print("     Celery:     cd backend && celery -A app.tasks.celery_app worker -l info")
    print("     Celery Beat: cd backend && celery -A app.tasks.celery_app beat -l info")
    print("     Frontend:   cd frontend && npm run dev")
    print()
    print("  4. Access the application:")
    print("     Frontend:  http://localhost:5173  (dev)  or  http://localhost  (docker)")
    print("     API:       http://localhost:8000/docs")
    print()
    print("  5. For development login (DEBUG=true only):")
    print("     Set VITE_DEV_LOGIN=true in frontend/.env")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser_argv = sys.argv[1:]
    use_docker_infra = "--docker-infra" in parser_argv

    print(f"{BOLD}MYEVIEW Setup{RESET}")
    print(f"This script will install all dependencies and prepare the system for deployment.")
    print(f"It is idempotent — safe to re-run. Already-completed steps are skipped.")
    print()

    # Check prerequisites
    if sys.version_info < (3, 11):
        log("Python 3.11+ is required", "error")
        sys.exit(1)

    if not command_exists("npm"):
        log("npm not found — install Node.js 20+ first", "error")
        sys.exit(1)

    # 0. Install system deps (apt-based packages for WeasyPrint, psycopg2, nmap, etc.)
    install_system_deps()

    # 0b. Optionally start infra
    if use_docker_infra:
        start_docker_infra()

    # 1. Create .env
    ensure_env_file()

    # 1b. Create virtual environment (needed for PEP 668 / externally-managed envs)
    create_virtualenv()

    # 2. Install Python deps
    install_python_deps()

    # 3. Install Node deps
    install_node_deps()

    # 4. Build frontend
    build_frontend()

    # 5. Run migrations
    run_migrations()

    # 6. Seed / verify reference data
    verify_reference_data()

    # 7. Validate scoring
    validate_scoring()

    # 8. Mark setup as complete
    SETUP_MARKER.write_text("1")

    # 9. Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()