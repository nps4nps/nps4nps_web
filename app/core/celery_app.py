from celery import Celery

from app.core.config import settings

celery = Celery(
    main=settings.app_name,
    broker=settings.broker_url,
    backend=settings.backend_url,
)

celery.conf.update(
    task_track_started=True,
    task_time_limit=settings.task_time_limit,
    timezone="Europe/Vienna",
    enable_utc=True,
)

celery.autodiscover_tasks(settings.celery_tasks_import)

celery.conf.update(
    task_track_started=True,
    result_expires=60 * 60 * 24 * 7,
    beat_schedule={
        f"rfrsh-deflt-sample-map-{settings.time_update_defaults}-sec": {
            "task": "app.tasks.sampling.rfrsh_dflt_sample_map",
            "schedule": settings.time_update_defaults,
        },
    },
)

import app.core.celery_signals
