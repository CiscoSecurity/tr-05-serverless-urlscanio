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
        ('url', 'http://gasimanai.ml/zanku/PvqDq929BSx_A_D_M1n_a.php'),
    )
)
def test_positive_indicators(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to check
    indicators of Urlscan module

    ID: CCTRI-1031-06fa7ad3-fbd5-40ff-964e-3369b5c62629

    Steps:
        1. Send request to enrich observe observable endpoint and check
        indicators

    Expectedresults:
        1. Response body contains indicators entity with needed fields from
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

    indicators = response_from_urlscan_module['data']['indicators']

    assert len(indicators['docs']) > 0

    for indicator in indicators['docs']:
        assert indicator['description']
        assert indicator['tags']
        assert indicator['valid_time']['start_time']
        assert indicator['producer'] == MODULE_NAME
        assert indicator['schema_version']
        assert indicator['type'] == 'indicator'
        assert indicator['external_ids']
        assert indicator['short_description']
        assert indicator['title']
        assert indicator['id'].startswith('transient:indicator')
        assert indicator['confidence'] == CONFIDENCE_LEVEL
        for external_reference in indicator['external_references']:
            assert external_reference['source_name'] == MODULE_NAME
            assert 'URL' in external_reference['description']
            assert external_reference[
                'url'].startswith(f'https://{MODULE_NAME}/')

    assert indicators['count'] == len(indicators['docs'])
