# Should return the dict to the caller, should not know about the query per se
def nanopub_query(query: str) -> dict:
    """Perform a SPARQL query against the nanopub network"""
