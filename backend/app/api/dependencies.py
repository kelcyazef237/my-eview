from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.constants import UserRole
from app.database import get_db
from app.models.organization import Organization
from app.models.score import Score
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


def resolve_org_id(user: User, db: Session, org_id: str | None = None) -> str:
    """Get the org_id for a user.

    Global admin can pass an explicit ``org_id`` to view any org's data.
    Ops/global_admin users without org_id get the most recently created org
    (falling back to the most recently scored org).
    """
    if org_id and user.role == UserRole.GLOBAL_ADMIN.value:
        return org_id
    if user.org_id:
        return str(user.org_id)
    if user.role in (UserRole.OPS.value, UserRole.GLOBAL_ADMIN.value):
        newest_org = db.query(Organization).order_by(Organization.created_at.desc()).first()
        if newest_org:
            return str(newest_org.id)
        latest_score = db.query(Score).order_by(Score.computed_at.desc()).first()
        if latest_score:
            return str(latest_score.org_id)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User is not associated with an organization",
    )


def require_role(*roles: UserRole):
    def _checker(user: User | None = Depends(get_current_user)) -> User:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        # Global admin bypasses all role checks — superset of every role.
        if user.role == UserRole.GLOBAL_ADMIN.value:
            return user
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _checker


require_owner = require_role(UserRole.OWNER, UserRole.OWNER_TECHNICAL, UserRole.OPS)
require_owner_technical = require_role(UserRole.OWNER_TECHNICAL, UserRole.OPS)
require_ops = require_role(UserRole.OPS)
require_global_admin = require_role(UserRole.GLOBAL_ADMIN)
