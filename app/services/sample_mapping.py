import logging
from typing import Any

import pandas as pd

from app.services.formatting_services import (
    parse_date,
    parse_iso_coordinates,
    parse_label,
)

logger = logging.getLogger(__name__)


def format_query_results(results: dict) -> tuple[pd.DataFrame, str]:
    """Formats the raw sample nanopub results into a df usable for plotting"""
    columns = [
        "np",
        "label",
        "timepoint",
        "coordinates",
        "ecosystem",
        "ecosystem_label",
        "material",
        "material_label",
        "purpose",
        "purpose_label",
    ]

    rows = []

    for result in results["results"]["bindings"]:
        row = {}
        for column in columns:
            row[column] = result.get(column, {}).get("value")
        rows.append(row)

    df = pd.DataFrame(rows)
    return (
        df,
        f"Query retrieved {len(df)} rows, {df['np'].nunique()} distinct nanopublications.",
    )


def prepare_mapping(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Format raw SPARQL result into data appropriate for mapping"""

    def _run_date(v: str) -> Any | None:
        try:
            return parse_date(v)
        except ValueError as exc:
            logger.warning(f"Date formatting raised error: {exc!s}")
            return None

    def _run_label(v: str) -> str | None:
        try:
            return parse_label(v)
        except ValueError as exc:
            logger.warning(f"Label formatting raised error: {exc!s}")
            return None

    rows = []

    for _, row in df.iterrows():
        try:
            lat, lng, alt = parse_iso_coordinates(row["coordinates"])
        except ValueError as e:
            logger.warning(f"Coordinate formatting raised error: {e!s}")
            logger.warning(
                f"Nanopublication {row["np"]} has no usable coordinates and will be dropped."
            )
            continue

        new_row = {
            "np": row["np"],
            "label": row["label"],
            "date": _run_date(row["timepoint"]),
            "timepoint": row["timepoint"],
            "lat": lat,
            "lng": lng,
            "altitude": alt,
            "ecosystem": row["ecosystem"],
            "ecosystem_label": _run_label(row["ecosystem_label"]),
            "ecosystem_description": row["ecosystem_label"],
            "material": row["material"],
            "material_label": _run_label(row["material_label"]),
            "material_description": row["material_label"],
            "purpose": row["purpose"],
            "purpose_label": _run_label(row["purpose_label"]),
        }
        rows.append(new_row)

    formatted = pd.DataFrame(rows)

    formatted["ecosystem_label"] = formatted["ecosystem_label"].fillna("unknown biome")

    return (
        formatted,
        f"Formatting of {len(formatted)} sample nanopublications was validated.",
    )
