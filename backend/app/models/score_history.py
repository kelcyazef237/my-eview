import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    overall_score = Column(Integer, nullable=False)
    is_full_report = Column(Boolean, nullable=False, default=False)
    computed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization")
    scan_run = relationship("ScanRun")
