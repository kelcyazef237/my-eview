from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    key = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    points_total = Column(Integer, nullable=False)
    scored = Column(Boolean, nullable=False, default=True)
    parent_group = Column(String(128), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    vectors = relationship("Vector", back_populates="category", lazy="selectin", order_by="Vector.sort_order")
    category_scores = relationship("CategoryScore", back_populates="category", lazy="selectin")
    tia_entries = relationship("TiaEntry", back_populates="category", lazy="selectin")
