"""Threat-feed cache service backed by PostgreSQL JSONB."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.threat_feed_cache import ThreatFeedCache


def get_cache(db: Session, method: str, source: str) -> dict[str, Any] | None:
    row = db.query(ThreatFeedCache).filter_by(method=method, source=source).first()
    if row:
        return {
            "method": row.method,
            "source": row.source,
            "payload": row.payload,
            "refreshed_at": row.refreshed_at,
        }
    return None


def set_cache(db: Session, method: str, source: str, payload: dict[str, Any]) -> ThreatFeedCache:
    row = db.query(ThreatFeedCache).filter_by(method=method, source=source).first()
    if row:
        row.payload = payload
        row.refreshed_at = datetime.now(timezone.utc)
    else:
        row = ThreatFeedCache(
            method=method,
            source=source,
            payload=payload,
            refreshed_at=datetime.now(timezone.utc),
        )
        db.add(row)
    db.commit()
    return row


def is_fresh(row: dict[str, Any] | None, max_age_seconds: float) -> bool:
    if not row:
        return False
    refreshed = row.get("refreshed_at")
    if not refreshed:
        return False
    age = (datetime.now(timezone.utc) - refreshed).total_seconds()
    return age <= max_age_seconds
