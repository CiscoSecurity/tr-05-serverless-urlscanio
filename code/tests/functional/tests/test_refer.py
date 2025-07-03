import pytest
from urllib.parse import quote
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_refer_observables
from tests.functional.tests.constants import (
    MODULE_NAME,
    URL,
    URLSCAN,
    SEARCH_FOR_THIS,
    BROWSE
)


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'gasimanai.ml'),
        ('ipv6', '2606:4700:3036::6818:62bd')
    )
)
def test_positive_smoke_enrich_refer_observables(module_headers, observable,
                                                 observable_type):
    """Perform testing for enrich refer observables endpoint to check response
     from Urlscan module

    ID: CCTRI-1033-3f3a7a0f-cac8-4111-ab5a-2aa783fac9be

    Steps:
        1. Send request to enrich refer observable endpoint

    Expectedresults:
        1. Response body contains refer entity with needed fields from Urlscan
         module

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_refer_observables(
        payload=observables,
        **{'headers': module_headers}
    )
    response_from_urlscan_module = get_observables(
        response_from_all_modules, MODULE_NAME)
    assert len(response_from_urlscan_module) == 2
    observable_category = (
        observable_type if observable_type != 'ipv6' else 'ip'
    )

    for urlscan in response_from_urlscan_module:
        if urlscan['title'].startswith('Browse'):
            search_type = 'browse'
            url = f'{URL}/{observable_category}/{observable}'
        elif urlscan['title'].startswith('Search') and observable_type == (
                'domain'):
            search_type = 'search'
            url = f'{URL}/{search_type}/#{observable_category}:{observable}'
        elif urlscan['title'].startswith('Search') and observable_type != (
                'domain'):
            search_type = 'search'
            url = f'{URL}/{search_type}/#{observable_category}:"{observable}"'
        else:
            raise AssertionError('Unsupported type')

        assert urlscan['module'] == MODULE_NAME
        assert urlscan['module_instance_id']
        assert urlscan['module_type_id']
        assert urlscan['id'] == (
            f'ref-{MODULE_NAME.split(".")[0]}-{search_type}-'
            f'{observable_type}-{quote(observable, safe="")}'
        )

        assert urlscan['title'] in f'{SEARCH_FOR_THIS } {observable_type},' \
                                   f' {BROWSE} {observable_type}'
        assert urlscan['description'] == (
            f'Check this {observable_type} status with {URLSCAN}'
        )
        assert urlscan['categories'] == [URLSCAN, search_type.capitalize()]
        assert urlscan['url'] == url
