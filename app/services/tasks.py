import logging
import time

from app.core.celery_app import celery
from app.core.config import settings

logger = logging.getLogger(__name__)


# TODO: replace with real function
@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.services.tasks.heavy_add",
)
def heavy_add(self, x, y):
    total_steps = 50
    try:
        for i in range(total_steps):
            time.sleep(0.2)

            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": total_steps,
                    "percent": int((i + 1) / total_steps * 100),
                    "message": f"Processing step {i + 1}...",
                },
            )
        logger.info(f"Processing {x} + {y}")
        return x + y
    except Exception as exc:
        logger.error(f"Error: {exc}, retrying...")
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
