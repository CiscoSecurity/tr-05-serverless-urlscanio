import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import MODULE_NAME, CONFIDENCE_LEVEL


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'gasimanai.ml'),
        ('ipv6', '2606:4700:3036::6818:62bd'),
        # uncomment it when you find url with data
        # ('url', 'http://gasimanai.ml/zanku/PvqDq929BSx_A_D_M1n_a.php'),
    )
)
def test_positive_sighting(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to check
    sightings of Urlscan module

    ID: CCTRI-818-acd56463-e158-4c67-9b26-57f08bbe775c

    Steps:
        1. Send request to enrich observe observable endpoint and check
        sighting

    Expectedresults:
        1. Response body contains sightings entity with needed fields from
        Urlscan module

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )['data']
    response_from_urlscan_module = get_observables(
        response_from_all_modules, MODULE_NAME)

    assert response_from_urlscan_module['module'] == MODULE_NAME
    assert response_from_urlscan_module['module_instance_id']
    assert response_from_urlscan_module['module_type_id']

    sightings = response_from_urlscan_module['data']['sightings']

    assert len(sightings['docs']) > 0

    for sighting in sightings['docs']:
        assert sighting['description'] == 'Scan Result'
        assert sighting['schema_version']
        assert sighting['relations']
        assert sighting['observables'][0] == observables[0]
        assert sighting['type'] == 'sighting'
        assert sighting['source'] == MODULE_NAME
        assert sighting['external_ids']
        assert sighting['internal'] is False
        assert sighting['source_uri'].startswith(f'https://{MODULE_NAME}/')
        assert sighting['id'].startswith('transient:sighting')
        assert sighting['count'] == 1
        assert sighting['confidence'] == CONFIDENCE_LEVEL
        assert sighting['observed_time']['start_time']
        assert sighting['data']['columns']
        assert sighting['data']['rows']
    assert sightings['count'] == len(sightings['docs'])
