import pytest

from app.services.uri_service import query_ols


@pytest.mark.network
def test_envo_term():
    term = query_ols(
        url="https://www.ebi.ac.uk/ols4/api/ontologies/envo/terms/",
        uri="http://purl.obolibrary.org/obo/ENVO_00005769",
    )
    assert term == "mountain forest soil"


@pytest.mark.network
def test_mesh_term():
    term = query_ols(
        url="https://www.ebi.ac.uk/ols4/api/ontologies/mesh/terms/",
        uri="http://id.nlm.nih.gov/mesh/D044822",
    )
    assert term == "Biodiversity"
