import json
import logging
from datetime import UTC, datetime, timezone

import pandas as pd

from app.core.celery_app import celery
from app.core.config import settings
from app.schemas.sample_mapping import DefaultSampleMapping
from app.services.plotting_service import create_sampling_map
from app.services.query_service import nanopub_query
from app.services.sample_mapping import format_query_results, prepare_mapping

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    max_retries=settings.max_retries,
    name="app.tasks.sampling.sample_mapping",
)
def sample_mapping(self, query: str) -> dict:
    """Generate the sample map, populated from nanopub data

    Returns:
        A dict consisting of the map html and the csv used to populate it.
    """

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
        return {
            "html": create_sampling_map(formatted_results),
            "csv": formatted_results.to_csv(index=False),
        }
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


@celery.task(name="app.tasks.sampling.rfrsh_dflt_sample_map")
def rfrsh_dflt_sample_map():
    """Refreshes default sample map"""
    logger.info("Refreshing default sampling map")
    try:
        def_sample_map = DefaultSampleMapping()
        query_results = nanopub_query(def_sample_map.query)
        formatted_results, format_msg = format_query_results(query_results)
        logger.info(format_msg)
        logger.info("Resolving URIs to labels, prepare mapping")
        formatted_results, format_msg = prepare_mapping(formatted_results)
        logger.info(format_msg)
        logger.info("Rendering the map")
        html = create_sampling_map(formatted_results)

        settings.map_dir.mkdir(parents=True, exist_ok=True)
        temp_file = settings.map_dir / f"{settings.dflt_sample_map_name}.tmp"
        final_file = settings.map_dir / f"{settings.dflt_sample_map_name}.html"
        temp_json_file = settings.map_dir / f"{settings.dflt_sample_map_name}.json.tmp"
        final_json_file = settings.map_dir / f"{settings.dflt_sample_map_name}.json"
        temp_csv_file = settings.map_dir / f"{settings.dflt_sample_map_name}.csv.tmp"
        final_csv_file = settings.map_dir / f"{settings.dflt_sample_map_name}.csv"

        temp_file.write_text(html, encoding="utf-8")
        temp_file.replace(final_file)

        temp_json_file.write_text(
            json.dumps({"last_updated": datetime.now(UTC).isoformat()}),
            encoding="utf-8",
        )
        temp_json_file.replace(final_json_file)

        formatted_results.to_csv(temp_csv_file, index=False)
        temp_csv_file.replace(final_csv_file)

        logger.info("Default sampling map successfully refreshed")
        return "Map refreshed successfully"

    except Exception:
        logger.exception("Failed to refresh default sampling map")
        raise


@celery.task(name="app.tasks.sampling.init_dft_sample_map")
def init_dft_sample_map():
    """Generate sample map if not exists"""
    dflt_map = settings.map_dir / f"{settings.dflt_sample_map_name}.html"
    dflt_json = settings.map_dir / f"{settings.dflt_sample_map_name}.json"
    dflt_csv = settings.map_dir / f"{settings.dflt_sample_map_name}.csv"

    if dflt_map.exists() and dflt_json.exists() and dflt_csv.exists():
        logger.info("Default sample map already exists. Skipping initialization.")
        return

    logger.info("No default map found. Generating initial map.")

    rfrsh_dflt_sample_map.delay()
