from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables


def test_positive_judgement(module_headers):
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
    observables = [{'type': 'ip', 'value': '185.143.172.209'}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )['data']
    judgements = get_observables(
        response_from_all_modules, 'urlscan.io')['data']['judgements']
    impact = ['Low', 'Medium', 'High']

    assert len(judgements['docs']) > 0

    for judgement in judgements['docs']:
        assert judgement['valid_time']['start_time']
        assert judgement['valid_time']['end_time']
        assert judgement['schema_version']
        assert judgement['observable'] == observables[0]
        assert judgement['type'] == 'judgement'
        assert judgement['source'] == 'urlscan.io'
        assert judgement['disposition'] == 2
        assert judgement['external_references']
        assert judgement['reason']
        assert judgement['source_uri'].startswith('https://urlscan.io/')
        assert judgement['disposition_name'] == 'Malicious'
        assert judgement['priority']
        assert judgement['id'].startswith('transient:judgement')
        assert judgement['severity'] in impact
        assert judgement['confidence'] in impact

    assert judgements['count'] == len(judgements['docs'])
