import pandas as pd

from app.services.uri_service import query_ols


def format_query_results(results: dict) -> pd.DataFrame:
    """Formats the raw sample nanopub results into a df usable for plotting"""
    rows = []

    for result in results["results"]["bindings"]:
        rows.append(
            {
                "np": result.get("np", {}).get("value"),
                "timepoint": result.get("timepoint", {}).get("value"),
            }
        )

    df = pd.DataFrame(rows)

    # TODO: cleanup for duplicates etc

    return df


def resolve_uris(df: pd.DataFrame) -> pd.DataFrame:
    """Resolves URIs to labels of sample context"""

    def _envo(uri: str) -> str:
        return query_ols(
            url="https://www.ebi.ac.uk/ols4/api/ontologies/envo/terms/", uri=uri
        )

    def _mesh(uri: str) -> str:
        return query_ols(
            url="https://www.ebi.ac.uk/ols4/api/ontologies/mesh/terms/", uri=uri
        )

    # TODO: resolve ncbi

    # TODO: add resolving of IDs, caching

    return df
