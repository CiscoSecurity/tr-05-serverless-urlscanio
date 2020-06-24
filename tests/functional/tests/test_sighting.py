from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
import pytest


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'doodle.com'),
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
        response_from_all_modules, 'urlscan.io')

    assert response_from_urlscan_module['module'] == 'urlscan.io'
    assert response_from_urlscan_module['module_instance_id']
    assert response_from_urlscan_module['module_type_id']

    sightings = response_from_urlscan_module['data']['sightings']
    confidence_levels = ['High', 'Info', 'Low', 'Medium', 'None', 'Unknown']

    assert len(sightings['docs']) > 0

    for sighting in sightings['docs']:
        assert sighting['description'] == 'Scan Result'
        assert sighting['schema_version']
        assert sighting['relations']
        assert sighting['observables'][0] == observables[0]
        assert sighting['type'] == 'sighting'
        assert sighting['source'] == 'urlscan.io'
        assert sighting['external_ids']
        assert sighting['internal'] is False
        assert sighting['source_uri'].startswith('https://urlscan.io/')
        assert sighting['id'].startswith('transient:')
        assert sighting['count'] == 1
        assert sighting['confidence'] in confidence_levels
        assert sighting['observed_time']['start_time']
        assert sighting['data']['columns']
        assert sighting['data']['rows']
    assert sightings['count'] == len(sightings['docs'])
