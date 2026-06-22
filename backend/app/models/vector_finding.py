import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class VectorFinding(Base):
    __tablename__ = "vector_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    vector_id = Column(Integer, ForeignKey("vectors.id", ondelete="CASCADE"), nullable=False, index=True)
    state = Column(String(16), nullable=False)
    evidence_ref = Column(String(255), nullable=True)  # collector_name or raw_evidence id

    scan_run = relationship("ScanRun", back_populates="vector_findings")
    asset = relationship("Asset", back_populates="vector_findings")
    vector = relationship("Vector", back_populates="findings")
