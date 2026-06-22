from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.constants import UserRole
from app.database import get_db
from app.models.user import User
from app.services.jwt import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> User | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: UserRole):
    def _checker(user: User | None = Depends(get_current_user)) -> User:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _checker


require_owner = require_role(UserRole.OWNER, UserRole.OWNER_TECHNICAL, UserRole.OPS)
require_owner_technical = require_role(UserRole.OWNER_TECHNICAL, UserRole.OPS)
require_ops = require_role(UserRole.OPS)
