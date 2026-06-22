from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

app = Celery(
    "myeview",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.run_passive_scan",
        "app.tasks.run_full_report_cycle",
        "app.tasks.feed_refresh",
        "app.tasks.run_verified_portscan",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_ignore_result=False,
    result_expires=3600,
    beat_schedule={
        # Threat-feed cache refresh
        "refresh-phishtank": {
            "task": "app.tasks.feed_refresh.refresh_phishtank",
            "schedule": 3600.0,
        },
        "refresh-openphish": {
            "task": "app.tasks.feed_refresh.refresh_openphish",
            "schedule": 43200.0,
        },
        "refresh-feodo": {
            "task": "app.tasks.feed_refresh.refresh_feodo",
            "schedule": 1800.0,
        },
        # Weekly monitoring scans for all organizations (internal alerting/freshness)
        "weekly-monitoring-scans": {
            "task": "app.tasks.run_passive_scan.dispatch_monitoring_scans",
            "schedule": crontab(day_of_week="monday", hour=2, minute=17),
        },
        # Monthly full-report snapshots for all organizations (formal, feeds outlook)
        "monthly-full-report-cycles": {
            "task": "app.tasks.run_full_report_cycle.dispatch_full_report_cycles",
            "schedule": crontab(day_of_month=1, hour=3, minute=17),
        },
    },
)

app.conf.task_routes = {
    "app.tasks.run_verified_portscan.*": {"queue": "verified"},
}
