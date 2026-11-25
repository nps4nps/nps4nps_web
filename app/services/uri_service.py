import logging
from urllib.parse import quote

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


def query_ols(url: str, uri: str) -> str:
    """Query the EMBL-EBI Ontology Lookup Service for a term"""
    url = url + quote(quote(uri, safe=""), safe="")
    try:
        r = requests.get(url, timeout=settings.request_timeout)
        r.raise_for_status()
        data_envo = r.json()
        return data_envo["label"]
    except Exception as e:
        logger.warning(f"Error during API call: {e!s}")
        return uri
