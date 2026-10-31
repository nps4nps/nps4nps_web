import logging
import time

from app.core.celery_app import celery
from app.core.config import settings
from app.schemas.visualization import DummyModel

logger = logging.getLogger(__name__)


# TODO: replace with real function
@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.services.tasks.heavy_add",
)
def heavy_add(self, x, y):
    try:
        dummy = DummyModel()
        logger.info(f"Processing {x} + {y}")
        time.sleep(dummy.sleepint)
        return x + y
    except Exception as exc:
        logger.error(f"Error: {exc}, retrying...")
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
