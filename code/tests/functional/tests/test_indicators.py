import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import (
    MODULE_NAME,
    CONFIDENCE_LEVEL,
    CTR_ENTITIES_LIMIT,
    URLSCAN
)


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'gasimanai.ml'),
        ('ipv6', '2606:4700:3035::6812:3f39')
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
    )
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
        assert 'valid_time' in indicator
        assert indicator['producer'] == URLSCAN
        assert indicator['schema_version']
        assert indicator['type'] == 'indicator'
        assert indicator['short_description']
        assert indicator['title']
        assert indicator['id'].startswith('transient:indicator')
        assert indicator['confidence'] == CONFIDENCE_LEVEL

    assert indicators['count'] == len(indicators['docs']) <= CTR_ENTITIES_LIMIT
