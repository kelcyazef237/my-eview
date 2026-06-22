"""Celery tasks that refresh the local threat-feed cache."""

import csv
import io
from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.database import SessionLocal
from app.services.threat_feed_cache import set_cache
from app.tasks.celery_app import app

settings = get_settings()


def _bound_sync_client() -> httpx.Client:
    bind = settings.collector_bind_address
    if bind and bind not in ("0.0.0.0", "::", ""):
        transport = httpx.HTTPTransport(local_address=bind)
        return httpx.Client(transport=transport, timeout=60)
    return httpx.Client(timeout=60)


@app.task(bind=True, max_retries=3)
def refresh_phishtank(self) -> dict:
    url = "http://data.phishtank.com/data/online-valid.json"
    try:
        with _bound_sync_client() as client:
            r = client.get(url, headers={"User-Agent": "MYEVIEW/0.1"})
            r.raise_for_status()
            data = r.json()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc

    urls = [entry.get("url", "").strip() for entry in data if entry.get("url")]
    payload = {
        "source": url,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "count": len(urls),
        "urls": urls,
    }
    db = SessionLocal()
    try:
        set_cache(db, "phishtank", url, payload)
    finally:
        db.close()
    return {"source": "phishtank", "count": len(urls)}


@app.task(bind=True, max_retries=3)
def refresh_openphish(self) -> dict:
    url = "https://openphish.com/feed.txt"
    try:
        with _bound_sync_client() as client:
            r = client.get(url, headers={"User-Agent": "MYEVIEW/0.1"})
            r.raise_for_status()
            text = r.text
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc

    urls = [line.strip() for line in text.splitlines() if line.strip()]
    payload = {
        "source": url,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "count": len(urls),
        "urls": urls,
    }
    db = SessionLocal()
    try:
        set_cache(db, "openphish", url, payload)
    finally:
        db.close()
    return {"source": "openphish", "count": len(urls)}


@app.task(bind=True, max_retries=3)
def refresh_feodo(self) -> dict:
    url = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
    try:
        with _bound_sync_client() as client:
            r = client.get(url, headers={"User-Agent": "MYEVIEW/0.1"})
            r.raise_for_status()
            text = r.text
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc

    ips = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split(",")
        if parts:
            ip = parts[0].strip().strip('"')
            if ip:
                ips.append(ip)

    payload = {
        "source": url,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "count": len(ips),
        "ips": ips,
    }
    db = SessionLocal()
    try:
        set_cache(db, "feodo", url, payload)
    finally:
        db.close()
    return {"source": "feodo", "count": len(ips)}
