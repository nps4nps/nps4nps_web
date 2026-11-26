import logging
import time

from app.core.celery_app import celery
from app.core.config import settings
from app.services.plotting_service import create_sampling_map
from app.services.query_service import nanopub_query
from app.services.sample_mapping import format_query_results, prepare_mapping

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.tasks.sampling.sample_mapping",
)
def sample_mapping(self, query: str) -> str:
    """Generate the sample map, populated from nanopub data"""

    def update(msg: str) -> None:
        self.update_state(state="PROGRESS", meta={"message": msg})

    try:
        update("Querying the nanopublication network for samples")
        query_results = nanopub_query(query)
        formatted_results, format_msg = format_query_results(query_results)
        update(format_msg)

        update("Resolving URIs to labels, prepare mapping")
        formatted_results, format_msg = prepare_mapping(formatted_results)
        update(format_msg)

        update("Rendering the map")
        html = create_sampling_map(formatted_results)

        return html
    except Exception as e:
        logger.exception(
            "Error while generating sampling map (attempt %s/%s)",
            self.request.retries + 1,
            self.max_retries,
        )
        if self.request.retries < self.max_retries:
            raise self.retry(
                exc=e,
                countdown=2**self.request.retries,
            ) from e
        raise
