import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TiaEntry(Base):
    __tablename__ = "tia_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(255), nullable=False)
    rendered_text = Column(JSONB, nullable=False, default=dict)

    scan_run = relationship("ScanRun", back_populates="tia_entries")
    category = relationship("Category", back_populates="tia_entries")
