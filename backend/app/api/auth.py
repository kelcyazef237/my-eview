import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.config import get_settings
from app.constants import UserRole
from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.services.jwt import create_access_token
from app.services.password import hash_password, verify_password

router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    identifier: str
    password: str
    # Backward-compat: legacy callers may still send `email` instead of `identifier`.
    email: str | None = None


class DevLoginRequest(BaseModel):
    email: EmailStr
    role: UserRole
    domain: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = ""
    org_id: str | None = None


class RegisterRequest(BaseModel):
    full_name: str
    organization_domain: str
    password: str
    password_repeat: str


class RegisterResponse(BaseModel):
    status: str = "pending"
    username: str
    message: str


def _derive_username(db: Session, full_name: str) -> str:
    """Derive a unique, case-insensitive username from a full name.

    Slug: lowercase, non-alphanumerics replaced with dots, collapsed, trimmed.
    Appends a numeric suffix on collision with an existing username.
    """
    base = re.sub(r"[^a-z0-9]+", ".", full_name.lower()).strip(".")
    if not base:
        base = "user"
    candidate = base
    suffix = 1
    while db.query(User).filter(func.lower(User.username) == candidate).first():
        suffix += 1
        candidate = f"{base}{suffix}"
    return candidate


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login by username OR email. Verifies the password against the database."""
    identifier = (payload.identifier or payload.email or "").strip()
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifier is required")

    if "@" in identifier:
        user = db.query(User).filter(User.email == identifier.lower()).first()
    else:
        user = db.query(User).filter(func.lower(User.username) == identifier.lower()).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled or awaiting admin validation",
        )
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "role": user.role,
        "org_id": str(user.org_id) if user.org_id else None,
    }


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user awaiting admin validation.

    Creates (or reuses) an Organization by the provided domain and a pending
    User with a derived username. The admin approves the registration and
    assigns a role; the user then logs in by username.
    """
    if payload.password != payload.password_repeat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if len(payload.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

    domain = payload.organization_domain.lower().strip()
    if "." not in domain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid organization domain")

    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name is required")

    username = _derive_username(db, full_name)

    # Find or create the organization by primary domain.
    org = db.query(Organization).filter(Organization.primary_domain == domain).first()
    if not org:
        derived_name = domain.split(".")[0].capitalize()
        org = Organization(name=derived_name, primary_domain=domain, country="CM")
        db.add(org)
        db.commit()
        db.refresh(org)

    user = User(
        username=username,
        full_name=full_name,
        email=None,
        role=UserRole.PUBLIC.value,
        hashed_password=hash_password(payload.password),
        org_id=org.id,
        is_active=False,
        registration_status="pending",
    )
    db.add(user)
    db.commit()

    return RegisterResponse(
        status="pending",
        username=username,
        message="Registration received. An administrator will validate your account and assign a role. You will log in with the username shown above once approved.",
    )


@router.post("/dev-login", response_model=TokenResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    """Development-only login that issues a JWT directly.

    Disabled when DEBUG=False. Do not use in production.
    If `domain` is provided, associates the user with that organization.
    """
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    org_id = None
    if payload.domain:
        org = db.query(Organization).filter(
            Organization.primary_domain == payload.domain.lower().strip()
        ).first()
        if org:
            org_id = str(org.id)

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            email=payload.email,
            role=payload.role.value,
            org_id=org_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif org_id and not user.org_id:
        user.org_id = org_id
        db.commit()
        db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "role": user.role, "org_id": str(user.org_id) if user.org_id else None}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "registration_status": user.registration_status,
        "org_id": str(user.org_id) if user.org_id else None,
    }
