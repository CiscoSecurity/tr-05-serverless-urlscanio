import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import (
    MODULE_NAME,
    CONFIDENCE_LEVEL,
    SEVERITY_LEVEL
)


@pytest.mark.parametrize(
    'observable_type, observable',
    (
        ('ip', '185.143.172.209'),
        ('domain', 'gasimanai.ml'),
        ('ipv6', '2606:4700:3036::6818:62bd'),
        ('url', 'http://gasimanai.ml/zanku/PvqDq929BSx_A_D_M1n_a.php'),
    )
)
def test_positive_judgement(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to check
    judgements of Urlscan module

    ID: CCTRI-1032-edddfab6-e48f-4121-af52-23f25044b72f

    Steps:
        1. Send request to enrich observe observable endpoint and check
        judgement

    Expectedresults:
        1. Response body contains judgements entity with needed fields from
        Urlscan module

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )['data']
    judgements = get_observables(
        response_from_all_modules, MODULE_NAME)['data']['judgements']

    assert len(judgements['docs']) > 0

    for judgement in judgements['docs']:
        assert judgement['valid_time']['start_time']
        assert judgement['valid_time']['end_time']
        assert judgement['schema_version']
        assert judgement['observable'] == observables[0]
        assert judgement['type'] == 'judgement'
        assert judgement['source'] == MODULE_NAME
        assert judgement['disposition'] == 2
        assert judgement['external_references']
        assert judgement['reason']
        assert judgement['source_uri'].startswith(f'https://{MODULE_NAME}/')
        assert judgement['disposition_name'] == 'Malicious'
        assert judgement['priority']
        assert judgement['id'].startswith('transient:judgement')
        assert judgement['severity'] == SEVERITY_LEVEL
        assert judgement['confidence'] == CONFIDENCE_LEVEL

    assert judgements['count'] == len(judgements['docs'])
