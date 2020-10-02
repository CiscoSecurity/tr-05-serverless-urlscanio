import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import MODULE_NAME


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '88.83.00.00'),
        ('domain', 'some.ml'),
        ('ipv6', '2000:4720:3136::68e8:6abd')
    )
)
def test_positive_smoke_empty_observables(
        module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to check that
     observable, on which Urlscan doesn't have information, will return empty
     data

    ID: CCTRI-1695-aaaa685a-b321-4d3a-88fe-a03280a529f0

    Steps:
        1. Send request to enrich observe observable endpoint

    Expectedresults:
        1. Check that data in response body contains empty dict from Urlscan
        module

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )

    urlscan_data = response_from_all_modules['data']

    response_from_urlscan_module = get_observables(urlscan_data, MODULE_NAME)

    assert response_from_urlscan_module['module'] == MODULE_NAME
    assert response_from_urlscan_module['module_instance_id']
    assert response_from_urlscan_module['module_type_id']

    assert response_from_urlscan_module['data'] == {}
