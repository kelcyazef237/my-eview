import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RawEvidence(Base):
    __tablename__ = "raw_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    collector_name = Column(String(128), nullable=False, index=True)
    raw_payload = Column(JSONB, nullable=False, default=dict)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    attempt_count = Column(Integer, nullable=False, default=1)

    scan_run = relationship("ScanRun", back_populates="raw_evidence")
    asset = relationship("Asset", back_populates="raw_evidence")
