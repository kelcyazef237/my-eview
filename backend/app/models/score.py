import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UUID as SAUUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Integer, nullable=False)
    shield_tier = Column(Integer, nullable=False)
    outlook = Column(String(64), nullable=False)
    ruleset_version = Column(String(16), nullable=False, default="v1")
    is_full_report = Column(Boolean, nullable=False, default=False)
    previous_full_report_id = Column(UUID(as_uuid=True), ForeignKey("scores.id", ondelete="SET NULL"), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    scan_run = relationship("ScanRun", back_populates="score")
    organization = relationship("Organization")
