from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.config import get_settings
from app.constants import UserRole
from app.database import get_db
from app.models.user import User
from app.services.jwt import create_access_token

router = APIRouter()
settings = get_settings()


class DevLoginRequest(BaseModel):
    email: EmailStr
    role: UserRole
    org_id: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/dev-login", response_model=TokenResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    """Development-only login that issues a JWT directly.

    Disabled when DEBUG=False. Do not use in production.
    """
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            email=payload.email,
            role=payload.role.value,
            org_id=payload.org_id,
        )
        db.add(user)
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
