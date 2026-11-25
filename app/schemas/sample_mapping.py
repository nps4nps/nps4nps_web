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
prefix nt: <https://w3id.org/np/o/ntemplate/>
prefix bio: <https://w3id.org/spaces/biodiversity/r/ontology/>
prefix biolink: <https://w3id.org/biolink/vocab/>
prefix kpxl: <https://w3id.org/kpxl/biodiv/terms/>

SELECT DISTINCT
    ?np 
    ?label 
    ?timepoint 
    ?coordinates
    ?ecosystem
    ?ecosystem_label
    ?material
    ?material_label
    ?purpose 
    ?purpose_label

WHERE {
    graph npa:graph {
        ?np npa:hasValidSignatureForPublicKey ?pubkey .
        filter not exists { ?npx npx:invalidates ?np ; npa:hasValidSignatureForPublicKey ?pubkey . }
        ?np dct:created ?date .
        ?np np:hasAssertion ?assertion .
        ?np np:hasPublicationInfo ?pubinfo .
        ?np npx:introduces ?sample .
        optional { ?np rdfs:label ?label }
    }

    FILTER NOT EXISTS {
        ?np a <http://purl.org/nanopub/x/DraftNanopub> .
    }
      
    GRAPH ?assertion {
        ?sample a bio:Sample .
    
        OPTIONAL {
            ?sample biolink:timepoint ?timepoint
        }
    
        OPTIONAL {
            ?sample bio:hasSamplingLocation ?loc .
            OPTIONAL { 
                ?loc kpxl:hasLocationCoordinates ?coordinates 
            }
            OPTIONAL { 
                ?loc bio:hasEcosystem ?ecosystem
            }
        }
        
        OPTIONAL {
            ?sample bio:hasSampleMaterial ?mat . ?mat a ?material
        }
        
        OPTIONAL {
            ?sample bio:hasSamplingPurpose ?purpose
        }
    }
    
    OPTIONAL {
        graph ?pubinfo { ?ecosystem nt:hasLabelFromApi ?ecosystem_label }
    }
    OPTIONAL {
        graph ?pubinfo { ?material nt:hasLabelFromApi ?material_label }
    }
    OPTIONAL {
        graph ?pubinfo { ?purpose nt:hasLabelFromApi ?purpose_label }
    }
}   
"""
