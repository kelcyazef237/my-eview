import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(16), nullable=False)  # domain | subdomain | ip
    value = Column(String(253), nullable=False, index=True)
    discovered_via = Column(String(64), nullable=True)  # primary | ct_log | subdomain_reuse
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    active = Column(Boolean, nullable=False, default=True)

    organization = relationship("Organization", back_populates="assets")
    raw_evidence = relationship("RawEvidence", back_populates="asset", lazy="selectin")
    vector_findings = relationship("VectorFinding", back_populates="asset", lazy="selectin")
