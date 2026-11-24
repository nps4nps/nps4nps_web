from pydantic import BaseModel


class SampleMapping(BaseModel):
    """Parses input parameters and generates SPARQL query"""

    @property
    def query(self) -> str:
        # TODO: replace with real SPARQL query
        return "This is the sparql query"
