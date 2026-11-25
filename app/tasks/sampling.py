import logging
import time

from app.core.celery_app import celery
from app.core.config import settings
from app.services.plotting_service import create_sampling_map
from app.services.query_service import nanopub_query
from app.services.sample_mapping import format_query_results, resolve_uris

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.tasks.sampling.sample_mapping",
)
def sample_mapping(self, query: str) -> str:
    try:

        def update(msg: str) -> None:
            self.update_state(state="PROGRESS", meta={"message": msg})

        update("Querying the nanopublication network for samples")
        query_results = nanopub_query(query)
        formatted_results = format_query_results(query_results)

        update("Resolving URIs to labels")
        formatted_results = resolve_uris(formatted_results)

        update("Rendering the map")
        html = create_sampling_map(formatted_results)
        time.sleep(2)

        return html
    except Exception as e:
        logger.error(f"Error: {e}, retrying...")
        raise self.retry(exc=e, countdown=2**self.request.retries) from e
