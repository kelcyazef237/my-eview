import uuid

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CategoryScore(Base):
    __tablename__ = "category_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_run_id = Column(UUID(as_uuid=True), ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    points_lost = Column(Integer, nullable=False, default=0)
    points_remaining = Column(Integer, nullable=False, default=0)

    scan_run = relationship("ScanRun", back_populates="category_scores")
    category = relationship("Category", back_populates="category_scores")
