import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class ThreatFeedCache(Base):
    __tablename__ = "threat_feed_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method = Column(String(64), nullable=False)  # e.g. phishtank, openphish, feodo, otx, dnsbl
    source = Column(String(255), nullable=False)  # e.g. URL or zone name
    payload = Column(JSONB, nullable=False, default=dict)
    refreshed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("method", "source", name="uq_threat_feed_cache_method_source"),
    )
