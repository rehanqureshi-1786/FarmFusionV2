"""
Celery configuration and task definitions.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "farmfusion",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "fetch-mandi-prices": {
        "task": "app.workers.tasks.fetch_mandi_prices",
        "schedule": 3600.0,  # Every hour
    },
    "send-irrigation-alerts": {
        "task": "app.workers.tasks.send_irrigation_alerts",
        "schedule": 21600.0,  # Every 6 hours
    },
}
