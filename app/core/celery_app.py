from celery import Celery

from app.core.config import settings

celery = Celery(
    main=settings.app_name,
    broker=settings.broker_url,
    backend=settings.backend_url,
)
celery.conf.update(task_track_started=True, task_time_limit=settings.task_time_limit)
celery.autodiscover_tasks(["app.services"])
