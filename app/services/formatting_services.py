import logging
from datetime import datetime
from typing import Any

import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)


def parse_iso_coordinates(value: str) -> tuple:
    """Split '+lat+lng+alt' into three numbers. Returns None for missing parts.

    Raises:
        ValueError: No coordinates or do not match RegExp
    """
    if pd.isna(value):
        raise ValueError("No coordinates found")

    match = settings.coordinates_re.match(str(value).strip())
    if match is None:
        raise ValueError(f"Malformed coordinates: '{value}'")

    return (
        float(match.group(1)),
        float(match.group(2)),
        float(match.group(3)) if match.group(3) else None,
    )


def parse_date(value: str) -> Any:
    """'2026-05-02T12:00:00Z' -> '2026-05-02'

    Raises:
        ValueError: Incorrectly formatted date or None
    """
    if pd.isna(value):
        raise ValueError("No date found")

    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(f"Incorrectly formatted date: {value}")


def parse_label(value: str) -> str:
    """'moor - A wetland found in ...' -> 'moor'

    Raises:
        ValueError: None

    """
    if pd.isna(value):
        raise ValueError("No label found")

    return str(value).split(" - ", 1)[0].strip()
