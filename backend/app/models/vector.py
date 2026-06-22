from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Vector(Base):
    __tablename__ = "vectors"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    data_source = Column(String(255), nullable=True)
    collection_method = Column(String(255), nullable=True)
    points_budget = Column(Integer, nullable=False, default=0)
    sort_order = Column(Integer, nullable=False, default=0)

    category = relationship("Category", back_populates="vectors")
    findings = relationship("VectorFinding", back_populates="vector", lazy="selectin")
