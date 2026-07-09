import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AppSetting(Base):
    """Key-value store for admin-configured application settings.

    Holds things that must not be committed to the repo — e.g. the
    Ollama / Z.ai API key for AI-assisted reports. The admin sets these
    through the admin UI; they live in the DB and survive restarts.
    """

    __tablename__ = "app_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_by = Column(UUID(as_uuid=True), nullable=True)