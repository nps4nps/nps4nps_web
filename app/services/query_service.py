from typing import Any

from SPARQLWrapper import JSON, SPARQLWrapper

from app.core.config import settings


def nanopub_query(query: str) -> Any:
    """Perform a SPARQL query against the nanopub network"""

    sparql = SPARQLWrapper(settings.nanopublication_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    return sparql.query().convert()
