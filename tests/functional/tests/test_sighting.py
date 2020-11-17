import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import (
    MODULE_NAME,
    CONFIDENCE_LEVEL,
    URL,
    RELATION_TYPES,
    CTR_ENTITIES_LIMIT
)


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'gasimanai.ml'),
        ('ipv6', '2606:4700:3036::6818:62bd')
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
    )
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
        assert sighting['observables'] == observables
        assert sighting['type'] == 'sighting'
        assert sighting['source'] == MODULE_NAME
        assert sighting['external_ids']
        assert sighting['internal'] is False
        assert sighting['source_uri'] == (
            f'{URL}/result/{sighting["external_ids"][0]}'
        )
        assert sighting['id'].startswith('transient:sighting')
        assert sighting['count'] == 1
        assert sighting['confidence'] == CONFIDENCE_LEVEL
        assert sighting['observed_time']['start_time'] == (
            sighting['observed_time']['end_time']
        )
        assert sighting['data']['columns']
        assert sighting['data']['rows']

        assert [relation['relation']
                for relation in sighting['relations']] == RELATION_TYPES

        for relation in sighting['relations']:
            assert relation['origin'] == f'{MODULE_NAME} Module'
            assert relation['source']['value']
            assert relation['source']['type']
            assert relation['related']['value']
            assert relation['related']['type']

    assert sightings['count'] == len(sightings['docs']) <= CTR_ENTITIES_LIMIT
