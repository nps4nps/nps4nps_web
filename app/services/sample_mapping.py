import pandas as pd


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

    # TODO: add resolving of IDs, caching

    return df
