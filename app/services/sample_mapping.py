import pandas as pd

from app.schemas.sample_mapping import SampleMapping
from app.services import plotting_service, query_service, uri_service


def resolve_uris(df: pd.DataFrame) -> pd.DataFrame:
    """Resolves URIs to labels of sample context"""


def generate_map(params: SampleMapping) -> str:
    """Maps sampling locations"""

    return "Hello world"  # TODO: remove after implementation

    query_results = query_service.nanopub_query(params.query)
    labeled_results = resolve_uris(query_results)
    html = plotting_service.create_sampling_map(labeled_results)

    return html
