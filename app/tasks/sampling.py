import logging
import time

from app.core.celery_app import celery
from app.core.config import settings
from app.schemas.sample_mapping import SampleMapping
from app.services.sample_mapping import generate_map

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.tasks.sampling.sample_mapping",
)
def sample_mapping(self, query: str) -> str:
    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "message": f"Doing some work",
            },
        )

        time.sleep(5)
        # TODO: perhaps move the whole sample mapping service in here to be able to give live updates

        return "Hello world"  # TODO: replace this with the map rendering
    except Exception as e:
        logger.error(f"Error: {e}, retrying...")
        raise self.retry(exc=e, countdown=2**self.request.retries) from e
