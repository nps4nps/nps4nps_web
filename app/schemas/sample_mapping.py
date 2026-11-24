from pydantic import BaseModel


class SampleMapping(BaseModel):
    """Parses input parameters and generates SPARQL query"""

    @property
    def query(self) -> str:
        return """
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix dct: <http://purl.org/dc/terms/>
prefix np: <http://www.nanopub.org/nschema#>
prefix npa: <http://purl.org/nanopub/admin/>
prefix npx: <http://purl.org/nanopub/x/>


SELECT DISTINCT
    ?np
    ?timepoint

WHERE {

    graph npa:graph {
        ?np npa:hasValidSignatureForPublicKey ?pubkey .
        filter not exists { ?npx npx:invalidates ?np ; npa:hasValidSignatureForPublicKey ?pubkey . }
        ?np dct:created ?date .
        ?np np:hasAssertion ?assertion .
        ?np npx:introduces ?sample .
        optional { ?np rdfs:label ?label }
    }

    FILTER NOT EXISTS {
        ?np a <http://purl.org/nanopub/x/DraftNanopub> .
    }
      
  GRAPH ?assertion {

    ?sample a
      <https://w3id.org/spaces/biodiversity/r/ontology/Sample> .
    
    OPTIONAL {
      ?timeNode
        <https://w3id.org/spaces/biodiversity/r/ontology/hasSamplingPurpose>
        ?timepoint .
    }
  }
  
}   
"""
