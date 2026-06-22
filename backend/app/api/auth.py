from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.config import get_settings
from app.constants import UserRole
from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.services.jwt import create_access_token

router = APIRouter()
settings = get_settings()


class DevLoginRequest(BaseModel):
    email: EmailStr
    role: UserRole
    domain: str | None = None  # domain to associate with (looks up org_id)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
    return {"access_token": token}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "org_id": str(user.org_id) if user.org_id else None,
    }
