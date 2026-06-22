import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    sector = Column(String(128), nullable=True)
    country = Column(String(2), nullable=True, default="CM")
    primary_domain = Column(String(253), nullable=False, unique=True, index=True)
    ownership_verified = Column(Boolean, nullable=False, default=False)
    verified_portscan_authorized = Column(Boolean, nullable=False, default=False)
    verified_portscan_authorized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    assets = relationship("Asset", back_populates="organization", lazy="selectin")
    scan_runs = relationship("ScanRun", back_populates="organization", lazy="selectin")
    users = relationship("User", back_populates="organization", lazy="selectin")
    ownership_verifications = relationship("OwnershipVerification", back_populates="organization", lazy="selectin")
