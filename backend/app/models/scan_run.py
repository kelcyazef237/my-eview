import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(16), nullable=False, default="pending")
    is_full_report = Column(Boolean, nullable=False, default=False)
    ruleset_version = Column(String(16), nullable=False, default="v1")

    organization = relationship("Organization", back_populates="scan_runs")
    raw_evidence = relationship("RawEvidence", back_populates="scan_run", lazy="selectin")
    vector_findings = relationship("VectorFinding", back_populates="scan_run", lazy="selectin")
    category_scores = relationship("CategoryScore", back_populates="scan_run", lazy="selectin")
    tia_entries = relationship("TiaEntry", back_populates="scan_run", lazy="selectin")
    score = relationship("Score", back_populates="scan_run", lazy="selectin", uselist=False)
