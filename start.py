#!/usr/bin/env python3
"""MYEVIEW — Service launcher.

Run:  python start.py

Starts all MYEVIEW services and streams colour-coded logs to the terminal.
Each service's output is also saved to a log file under logs/.

On every startup, start.py automatically:
  1. Checks if PostgreSQL + Redis are reachable; if not, starts them via
     docker-compose (no --docker-infra flag needed — it's automatic).
  2. Runs Alembic migrations (alembic upgrade head) so new migrations from
     a fresh git pull are applied before services start.
  3. Validates the scoring ruleset (reference_data + YAML consistency).

Services started:
  - Backend API (uvicorn)
  - Celery worker
  - Celery beat scheduler
  - Frontend (vite dev server or static serve of dist/)

Options:
  --docker-infra    Force docker-compose start (skips the reachability check)
  --dev             Run frontend in dev mode (vite) instead of serving dist/
  --no-celery       Skip Celery worker + beat (API + frontend only)
  --no-frontend     Skip frontend (backend + celery only)
  --host HOST       Bind backend to this host (default: 0.0.0.0)
  --port PORT       Bind backend to this port (default: 8000)
  --daemon          Run in the background (detached, survives SSH disconnect)
  --stop            Stop a running daemon (reads PID from logs/start.pid)
  --status          Show whether the daemon is running

Press Ctrl+C to stop all services gracefully (foreground mode).
In --daemon mode, use `python start.py --stop` to shut down.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = str(VENV_DIR / "bin" / "python")
VENV_BIN = str(VENV_DIR / "bin")
LOG_DIR = PROJECT_ROOT / "logs"

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

SERVICE_COLOURS = {
    "API": CYAN,
    "WORKER": MAGENTA,
    "BEAT": BLUE,
    "FRONTEND": GREEN,
    "INFRA": YELLOW,
}


def log(msg: str, level: str = "info") -> None:
    colours = {"info": GREEN + "✓", "warn": YELLOW + "!", "error": RED + "✗", "step": BOLD}
    prefix = colours.get(level, "")
    print(f"{prefix} {msg}{RESET}", flush=True)


# ---------------------------------------------------------------------------
# Log pump — reads subprocess stdout line-by-line, prints with prefix
# ---------------------------------------------------------------------------

class LogPump(threading.Thread):
    """Read lines from a process stdout/stderr and print with a coloured prefix."""

    def __init__(self, name: str, proc: subprocess.Popen, colour: str, log_file: Path | None = None):
        super().__init__(daemon=True)
        self.name = name
        self.proc = proc
        self.colour = colour
        self.log_file = log_file
        self._file_handle = None
        self._stop = threading.Event()

    def run(self) -> None:
        if self.log_file:
            self._file_handle = open(self.log_file, "a", buffering=1)
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            if self._stop.is_set():
                break
            text = line.rstrip("\n")
            # Print to terminal with coloured prefix
            print(f"{self.colour}[{self.name}]{RESET} {text}", flush=True)
            # Also write to log file (no colour codes)
            if self._file_handle:
                self._file_handle.write(f"{text}\n")
        if self._file_handle:
            self._file_handle.close()

    def stop(self) -> None:
        self._stop.set()


# ---------------------------------------------------------------------------
# Service definitions
# ---------------------------------------------------------------------------

class Service:
    """Wraps a subprocess + its log pump."""

    def __init__(self, name: str, cmd: list[str], cwd: Path, colour: str, env: dict | None = None):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.colour = colour
        self.env = env or os.environ.copy()
        self.proc: subprocess.Popen | None = None
        self.pump: LogPump | None = None
        self.log_file: Path | None = None

    def start(self) -> None:
        self.log_file = LOG_DIR / f"{self.name.lower().replace(' ', '_')}.log"
        log(f"Starting {self.name}…", "step")
        # Clear previous log
        if self.log_file.exists():
            self.log_file.unlink()

        self.proc = subprocess.Popen(
            self.cmd,
            cwd=str(self.cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=self.env,
        )
        self.pump = LogPump(self.name, self.proc, self.colour, self.log_file)
        self.pump.start()
        time.sleep(0.5)
        if self.proc.poll() is not None:
            log(f"{self.name} exited immediately with code {self.proc.returncode}", "error")
            raise RuntimeError(f"{self.name} failed to start")
        log(f"{self.name} started (PID {self.proc.pid})", "info")

    def stop(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            return
        log(f"Stopping {self.name}…", "warn")
        if self.pump:
            self.pump.stop()
        # Try graceful SIGTERM first
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            log(f"{self.name} didn't stop in 5s — sending SIGKILL", "warn")
            self.proc.kill()
            self.proc.wait(timeout=3)
        log(f"{self.name} stopped", "info")

    def is_alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def check_prerequisites() -> None:
    """Verify that setup.py has been run."""
    if not VENV_DIR.exists() or not (VENV_DIR / "bin" / "python").exists():
        log("Virtual environment not found — run setup.py first", "error")
        sys.exit(1)

    if not (BACKEND_DIR / ".env").exists():
        log("backend/.env not found — run setup.py first", "error")
        sys.exit(1)


def check_postgres() -> bool:
    """Check if PostgreSQL is reachable."""
    result = subprocess.run(
        [VENV_PYTHON, "-c", """
import sys
sys.path.insert(0, 'backend')
from app.config import get_settings
from sqlalchemy import create_engine, text
s = get_settings()
engine = create_engine(s.database_url)
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
print('OK')
"""],
        capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10,
    )
    return "OK" in result.stdout


def check_redis() -> bool:
    """Check if Redis is reachable."""
    result = subprocess.run(
        [VENV_PYTHON, "-c", """
import redis
import sys
sys.path.insert(0, 'backend')
from app.config import get_settings
s = get_settings()
r = redis.from_url(s.redis_url)
r.ping()
print('OK')
"""],
        capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=10,
    )
    return "OK" in result.stdout


def start_docker_infra() -> None:
    """Start PostgreSQL and Redis via docker-compose."""
    # Check if docker is available
    docker_check = subprocess.run(["docker", "--version"], capture_output=True)
    if docker_check.returncode != 0:
        log("Docker is not available — cannot start infrastructure automatically", "error")
        log("Start PostgreSQL and Redis manually, or install Docker.", "error")
        sys.exit(1)

    log("Starting PostgreSQL + Redis via docker-compose…", "step")
    subprocess.run(["docker", "compose", "up", "-d", "postgres", "redis"], cwd=PROJECT_ROOT)

    # Wait for postgres
    for i in range(30):
        if check_postgres():
            log("PostgreSQL is ready", "info")
            break
        time.sleep(1)
    else:
        log("PostgreSQL did not become ready in 30s", "error")
        sys.exit(1)

    # Wait for redis
    for i in range(15):
        if check_redis():
            log("Redis is ready", "info")
            break
        time.sleep(1)
    else:
        log("Redis did not become ready in 15s", "error")
        sys.exit(1)


def ensure_infrastructure() -> None:
    """Check if PostgreSQL + Redis are reachable; start them via docker if not."""
    log("Checking infrastructure…", "step")
    pg_ok = check_postgres()
    rd_ok = check_redis()

    if pg_ok and rd_ok:
        log("PostgreSQL and Redis are reachable", "info")
        return

    # Something is not reachable — try to start via docker-compose
    missing = []
    if not pg_ok:
        missing.append("PostgreSQL")
    if not rd_ok:
        missing.append("Redis")
    log(f"{' and '.join(missing)} not reachable — starting via docker-compose…", "warn")
    start_docker_infra()


def run_migrations() -> None:
    """Run Alembic migrations (alembic upgrade head). Idempotent — only applies pending ones."""
    log("Running database migrations…", "step")
    result = subprocess.run(
        [VENV_PYTHON, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log("Database migrations failed:", "error")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(1)
    # Alembic prints "INFO  [alembic.runtime.migration] ..." lines on success
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            if "INFO" in line:
                print(f"  {line.strip()}")
    log("Database migrations applied (all up to head)", "info")


def validate_scoring() -> None:
    """Validate that scoring rules sum to 1000 and reference data is consistent."""
    log("Validating scoring ruleset…", "step")
    result = subprocess.run(
        [VENV_PYTHON, "-c", """
import sys
sys.path.insert(0, 'backend')
from app.reference_data import validate_reference_data
from app.scoring.rules_loader import load_ruleset
validate_reference_data()
load_ruleset()
print('VALID')
"""],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if "VALID" not in result.stdout:
        log("Scoring validation failed:", "error")
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(1)
    log("Scoring ruleset validated (28 vectors, 1000 points)", "info")


# ---------------------------------------------------------------------------
# Daemon mode — detached background execution (survives SSH disconnect)
# ---------------------------------------------------------------------------

PID_FILE = LOG_DIR / "start.pid"
DAEMON_LOG = LOG_DIR / "daemon.log"


def _write_pid(pid: int) -> None:
    PID_FILE.write_text(str(pid))


def _read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text().strip())
    except (ValueError, OSError):
        return None


def _clear_pid() -> None:
    if PID_FILE.exists():
        PID_FILE.unlink()


def _pid_alive(pid: int) -> bool:
    """Check if a process with this PID exists (no permission/owner check)."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists but not ours — treat as alive for status
    return True


def _pids_on_port(port: int) -> list[int]:
    """Return PIDs of processes listening on the given TCP port. Tries lsof then fuser then ss."""
    # 1. lsof
    try:
        out = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            pids = [int(p) for p in out.stdout.split() if p.isdigit()]
            if pids:
                return pids
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 2. fuser
    try:
        out = subprocess.run(
            ["fuser", f"{port}/tcp"],
            capture_output=True, text=True, timeout=5,
        )
        # fuser prints PIDs to stderr in format "PORT/tcp:   PID PID"
        text = (out.stdout + out.stderr).strip()
        pids = [int(p) for p in text.replace(f"{port}/tcp:", "").split() if p.isdigit()]
        if pids:
            return pids
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. ss (present on most modern Linux)
    try:
        out = subprocess.run(
            ["ss", "-lptnH", f"sport = :{port}"],
            capture_output=True, text=True, timeout=5,
        )
        pids = []
        for line in out.stdout.splitlines():
            # lines look like: "... users:(("uvicorn",pid=12345,fd=...))"
            if "pid=" in line:
                after = line.split("pid=", 1)[1]
                num = ""
                for ch in after:
                    if ch.isdigit():
                        num += ch
                    else:
                        break
                if num:
                    pids.append(int(num))
        if pids:
            return pids
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return []


def free_port(port: int, label: str = "") -> None:
    """Kill any process listening on `port` so a stale instance can't block startup."""
    pids = _pids_on_port(port)
    if not pids:
        return
    desc = f" ({label})" if label else ""
    log(f"Port {port}{desc} is held by PID {', '.join(map(str, pids))} — killing…", "warn")
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
        except PermissionError:
            log(f"No permission to kill PID {pid} on port {port}", "error")
            continue
    # Give them a moment to release the socket
    time.sleep(2)
    # Force-kill any survivors
    survivors = _pids_on_port(port)
    for pid in survivors:
        try:
            os.kill(pid, signal.SIGKILL)
            log(f"Force-killed PID {pid} on port {port}", "warn")
        except (ProcessLookupError, PermissionError):
            pass
    time.sleep(1)
    if _pids_on_port(port):
        log(f"Port {port} still in use after kill attempts — startup may fail", "error")
    else:
        log(f"Port {port} is now free", "info")


def daemonize() -> None:
    """Double-fork detach: parent exits, child becomes session leader and runs main()."""
    LOG_DIR.mkdir(exist_ok=True)

    # Flush any buffered output before forking
    sys.stdout.flush()
    sys.stderr.flush()

    # First fork — parent returns immediately, child continues
    pid = os.fork()
    if pid > 0:
        # Parent — print the child PID and exit
        print(f"{GREEN}✓ {BOLD}MYEVIEW daemonized{RESET} (PID {pid})")
        print(f"  Logs:  {DAEMON_LOG}")
        print(f"  Stop:  python start.py --stop")
        print(f"  Status: python start.py --status")
        sys.exit(0)

    # Child — become its own session leader (no controlling terminal)
    os.setsid()

    # Second fork — prevents re-acquiring a controlling terminal
    pid = os.fork()
    if pid > 0:
        # Intermediate child — exit immediately
        os._exit(0)

    # Grandchild — the actual daemon process
    os.chdir(str(PROJECT_ROOT))
    os.umask(0)

    # Replace stdio: stdin from /dev/null, stdout+stderr to daemon log
    with open("/dev/null", "rb") as devnull_in:
        os.dup2(devnull_in.fileno(), sys.stdin.fileno())
    log_fd = open(DAEMON_LOG, "a", buffering=1)
    os.dup2(log_fd.fileno(), sys.stdout.fileno())
    os.dup2(log_fd.fileno(), sys.stderr.fileno())

    _write_pid(os.getpid())

    # Register cleanup on exit
    import atexit
    atexit.register(_clear_pid)


def stop_daemon() -> None:
    pid = _read_pid()
    if pid is None:
        log("No PID file found — daemon not running (or started without --daemon)", "warn")
        sys.exit(1)
    if not _pid_alive(pid):
        log(f"PID {pid} is not running — cleaning up stale PID file", "warn")
        _clear_pid()
        sys.exit(1)

    log(f"Stopping MYEVIEW daemon (PID {pid})…", "step")
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        _clear_pid()
        log("Process already gone", "warn")
        sys.exit(0)

    # Wait up to 15s for it to die
    for _ in range(15):
        time.sleep(1)
        if not _pid_alive(pid):
            _clear_pid()
            log("Daemon stopped", "info")
            # Clean up any orphaned children still holding ports
            free_port(8000, "API")
            free_port(5173, "FRONTEND")
            sys.exit(0)

    # Force kill
    log("Daemon did not stop in 15s — sending SIGKILL", "warn")
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _clear_pid()
    log("Daemon killed", "info")
    free_port(8000, "API")
    free_port(5173, "FRONTEND")


def status_daemon() -> None:
    pid = _read_pid()
    if pid is None:
        print(f"{YELLOW}MYEVIEW daemon is not running (no PID file){RESET}")
        sys.exit(0)
    if _pid_alive(pid):
        print(f"{GREEN}✓ MYEVIEW daemon is running (PID {pid}){RESET}")
        print(f"  Logs: {DAEMON_LOG}")
        print(f"  Stop: python start.py --stop")
        sys.exit(0)
    else:
        print(f"{RED}✗ PID file exists (PID {pid}) but process is dead — stale{RESET}")
        _clear_pid()
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]

    # Control flags (these exit before starting services)
    if "--stop" in args:
        stop_daemon()
        return
    if "--status" in args:
        status_daemon()
        return

    daemon_mode = "--daemon" in args

    # In daemon mode, fork off and let the grandchild continue past here.
    # daemonize() calls sys.exit(0) in the parent, so only the daemon reaches below.
    if daemon_mode:
        daemonize()

    use_docker_infra = "--docker-infra" in args
    dev_mode = "--dev" in args
    no_celery = "--no-celery" in args
    no_frontend = "--no-frontend" in args

    # Parse --host and --port
    host = "0.0.0.0"
    port = 8000
    for i, arg in enumerate(args):
        if arg == "--host" and i + 1 < len(args):
            host = args[i + 1]
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])

    print(f"{BOLD}MYEVIEW Service Launcher{RESET}")
    print()

    # Pre-flight
    check_prerequisites()
    LOG_DIR.mkdir(exist_ok=True)

    # Check / start infra (auto-starts via docker-compose if not reachable)
    if use_docker_infra:
        start_docker_infra()
    else:
        ensure_infrastructure()

    # Run database migrations (always — alembic upgrade head is idempotent)
    run_migrations()

    # Validate scoring ruleset (catches reference_data / YAML inconsistencies early)
    validate_scoring()

    # Build service list
    services: list[Service] = []

    # Backend env includes venv bin on PATH so uvicorn/celery are found
    backend_env = os.environ.copy()
    backend_env["PATH"] = VENV_BIN + ":" + backend_env.get("PATH", "")

    # Backend API
    services.append(Service(
        name="API",
        cmd=[VENV_PYTHON, "-m", "uvicorn", "app.main:app",
             "--host", host, "--port", str(port), "--reload"],
        cwd=BACKEND_DIR,
        colour=SERVICE_COLOURS["API"],
        env=backend_env,
    ))

    # Celery worker + beat
    if not no_celery:
        services.append(Service(
            name="WORKER",
            cmd=[VENV_PYTHON, "-m", "celery", "-A", "app.tasks.celery_app",
                 "worker", "-l", "info", "--queues=celery,verified"],
            cwd=BACKEND_DIR,
            colour=SERVICE_COLOURS["WORKER"],
            env=backend_env,
        ))
        services.append(Service(
            name="BEAT",
            cmd=[VENV_PYTHON, "-m", "celery", "-A", "app.tasks.celery_app",
                 "beat", "-l", "info"],
            cwd=BACKEND_DIR,
            colour=SERVICE_COLOURS["BEAT"],
            env=backend_env,
        ))

    # Frontend
    if not no_frontend:
        if dev_mode:
            services.append(Service(
                name="FRONTEND",
                cmd=["npm", "run", "dev"],
                cwd=FRONTEND_DIR,
                colour=SERVICE_COLOURS["FRONTEND"],
            ))
        else:
            dist_dir = FRONTEND_DIR / "dist"
            if not dist_dir.exists():
                log("frontend/dist/ not found — run setup.py first (or use --dev)", "error")
                sys.exit(1)
            # Serve the built frontend with vite preview
            services.append(Service(
                name="FRONTEND",
                cmd=["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"],
                cwd=FRONTEND_DIR,
                colour=SERVICE_COLOURS["FRONTEND"],
            ))

    # Start all services
    print()
    print(f"{BOLD}Starting {len(services)} services…{RESET}")

    # Free ports that the API and frontend will bind to, so a stale
    # process from a crashed/killed run can't block startup.
    free_port(port, "API")
    if not no_frontend:
        free_port(5173, "FRONTEND")

    print(f"Logs are saved to {LOG_DIR}/")
    if not daemon_mode:
        print(f"Press Ctrl+C to stop all services.")
    else:
        print(f"Running detached — use `python start.py --stop` to shut down.")
    print()

    started: list[Service] = []
    try:
        for svc in services:
            svc.start()
            started.append(svc)
            time.sleep(1)  # stagger starts slightly
    except RuntimeError as e:
        log(f"Failed to start services: {e}", "error")
        for svc in started:
            svc.stop()
        sys.exit(1)

    print()
    print(f"{BOLD}════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  MYEVIEW is running{RESET}")
    print(f"{BOLD}════════════════════════════════════════════════════════════{RESET}")
    print()
    print(f"  API:       http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    if dev_mode:
        print(f"  Frontend:  http://localhost:5173  (dev mode)")
    else:
        print(f"  Frontend:  http://localhost:5173  (production preview)")
    print()
    print(f"  Logs:      {LOG_DIR}/")
    print(f"  Stop:      Ctrl+C")
    print()

    # Wait for Ctrl+C or a service to die
    def handle_sigint(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        while True:
            time.sleep(2)
            dead = [s for s in started if not s.is_alive()]
            if dead:
                for svc in dead:
                    log(f"{svc.name} has exited (code {svc.proc.returncode})", "warn")
                # If the API dies, everything else is pointless
                api_svc = next((s for s in started if s.name == "API"), None)
                if api_svc and not api_svc.is_alive():
                    log("API process died — shutting down all services", "error")
                    break
    except KeyboardInterrupt:
        print()
        log("Received Ctrl+C — shutting down…", "warn")

    # Graceful shutdown
    for svc in reversed(started):
        svc.stop()

    log("All services stopped.", "info")


if __name__ == "__main__":
    main()