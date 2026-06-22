#!/usr/bin/env python3
"""Create or update an admin user for MYEVIEW.

Usage:
  python create_admin.py                          # interactive prompt
  python create_admin.py --email kelcy --password 'Terminal04.com'
  python create_admin.py --email kelcy --password 'Terminal04.com' --domain matrixtelecoms.com
  python create_admin.py --email kelcy@myeview.local --username Kelcy --password 'Terminal04.com' --role global_admin

The --domain flag associates the admin with a specific organization.
Without it, the user can access all orgs (the dashboard auto-picks
the most recently scanned org).

The --username flag sets a login username (case-insensitive). When set,
the user can log in by typing the username OR their email.
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
    parser.add_argument("--username", help="Login username (case-insensitive, optional)")
    parser.add_argument("--full-name", dest="full_name", help="User full name (optional)")
    parser.add_argument("--password", help="User password")
    parser.add_argument("--domain", help="Associate with this org's domain (optional)")
    parser.add_argument("--role", default="ops", help="User role (default: ops)")
    args = parser.parse_args()

    email = args.email or input("Email (blank for none): ").strip()
    if not email:
        email = None
    email = email.lower() if email else None

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
    username = args.username or None
    full_name = args.full_name or None

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
username = {username!r}
full_name = {full_name!r}

org_id = None
if domain:
    org = db.query(Organization).filter(Organization.primary_domain == domain.lower().strip()).first()
    if org:
        org_id = org.id
        print(f"Associated with org: {{org.name}} ({{org.primary_domain}})")
    else:
        print(f"WARNING: No organization found for domain {{domain}}")

# Look up existing user by email (if provided) or by username.
user = None
if email:
    user = db.query(User).filter(User.email == email).first()
if not user and username:
    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.username) == username.lower()).first()

if user:
    user.hashed_password = hash_password(password)
    user.role = role
    if org_id and not user.org_id:
        user.org_id = org_id
    if username:
        user.username = username
    if full_name:
        user.full_name = full_name
    user.is_active = True
    user.registration_status = "active"
    db.commit()
    ident = username or email
    print(f"Updated existing user: {{ident}} (role={{role}})")
else:
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        role=role,
        hashed_password=hash_password(password),
        org_id=org_id,
        is_active=True,
        registration_status="active",
    )
    db.add(user)
    db.commit()
    ident = username or email
    print(f"Created new user: {{ident}} (role={{role}})")

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
    if username:
        print(f"  Username: {username}")
    if email:
        print(f"  Email:    {email}")
    print(f"  Role:     {role}")


if __name__ == "__main__":
    main()