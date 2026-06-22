#!/usr/bin/env python3
"""Create or update an admin (ops) user for MYEVIEW.

Usage:
  python create_admin.py                          # interactive prompt
  python create_admin.py --email kelcy --password 'Terminal04.com'
  python create_admin.py --email kelcy --password 'Terminal04.com' --domain matrixtelecoms.com

The --domain flag associates the admin with a specific organization.
Without it, the ops user can access all orgs (the dashboard auto-picks
the most recently scanned org).
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
VENV_PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update an admin user")
    parser.add_argument("--email", help="User email (login identifier)")
    parser.add_argument("--password", help="User password")
    parser.add_argument("--domain", help="Associate with this org's domain (optional)")
    parser.add_argument("--role", default="ops", help="User role (default: ops)")
    args = parser.parse_args()

    email = args.email or input("Email: ").strip()
    if not email:
        print(f"{RED}Email is required{RESET}")
        sys.exit(1)

    password = args.password
    if not password:
        password = getpass.getpass("Password: ").strip()
        if not password:
            print(f"{RED}Password is required{RESET}")
            sys.exit(1)
        confirm = getpass.getpass("Confirm password: ").strip()
        if password != confirm:
            print(f"{RED}Passwords do not match{RESET}")
            sys.exit(1)

    domain = args.domain or None
    role = args.role

    # Build the inline script
    script = f"""
import sys
sys.path.insert(0, 'backend')
from app.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.services.password import hash_password

db = SessionLocal()
email = {email!r}
password = {password!r}
domain = {domain!r}
role = {role!r}

org_id = None
if domain:
    org = db.query(Organization).filter(Organization.primary_domain == domain.lower().strip()).first()
    if org:
        org_id = org.id
        print(f"Associated with org: {{org.name}} ({{org.primary_domain}})")
    else:
        print(f"WARNING: No organization found for domain {{domain}}")

user = db.query(User).filter(User.email == email.lower()).first()
if user:
    user.hashed_password = hash_password(password)
    user.role = role
    if org_id and not user.org_id:
        user.org_id = org_id
    user.is_active = True
    db.commit()
    print(f"Updated existing user: {{email}} (role={{role}})")
else:
    user = User(
        email=email.lower(),
        role=role,
        hashed_password=hash_password(password),
        org_id=org_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"Created new user: {{email}} (role={{role}})")

db.close()
print("DONE")
"""

    import subprocess
    result = subprocess.run(
        [VENV_PYTHON, "-c", script],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        print(f"{RED}Failed to create admin user:{RESET}")
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    print(result.stdout.strip())
    print(f"{GREEN}Admin user created successfully.{RESET}")
    print(f"  Login at: http://localhost:5173/login")
    print(f"  Email:    {email}")
    print(f"  Role:     {role}")


if __name__ == "__main__":
    main()