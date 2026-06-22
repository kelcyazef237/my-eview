import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    username = Column(String(64), nullable=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(32), nullable=False, default="public")
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    registration_status = Column(String(32), nullable=False, default="active", server_default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="users")
