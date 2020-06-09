from uuid import uuid4
from functools import partial
from datetime import datetime

from flask import Blueprint, g, current_app

from api.schemas import ObservableSchema
from api.utils import (
    get_json,
    get_jwt,
    jsonify_data,
    format_docs
)
from api.client import URLScanClient

enrich_api = Blueprint('enrich', __name__)


get_observables = partial(get_json, schema=ObservableSchema(many=True))


def group_observables(relay_input):
    # Leave only unique pairs.

    result = []
    for obj in relay_input:

        obj['type'] = obj['type'].lower()

        # Get only supported types.
        if obj['type'] in current_app.config['URL_SCAN_OBSERVABLE_TYPES']:
            if obj in result:
                continue
            result.append(obj)

    return result


def get_observable_object(type_, value):
    return {
        'type': type_,
        'value': value
    }


def get_relations(search_result):
    relations = []

    domain_object = get_observable_object(
        'domain', search_result['page'].get('domain'))
    url_object = get_observable_object(
        'url', search_result['page'].get('url'))
    ip_object = get_observable_object(
        'ip', search_result['page'].get('ip'))

    if domain_object['value'] and url_object['value']:
        relations.append(
            make_relation(url_object, domain_object, 'Contains'))
    if domain_object['value'] and ip_object['value']:
        relations.append(
            make_relation(domain_object, ip_object, 'Resolved_To'))
    if url_object['value'] and ip_object['value']:
        relations.append(
            make_relation(url_object, ip_object, 'Hosted_By'))

    return relations


def make_relation(source, related, relation_type):
    return {
        "origin": "urlscan.io Module",
        "source": source,
        "related": related,
        "relation": relation_type
    }


def get_data(dict_object):
    data = {
        'columns': [],
        'rows': [[]]
    }
    for item in dict_object.items():
        column = {
            'name': item[0],
            'type': 'integer'
        }
        data['columns'].append(column)
        data['rows'][0].append(item[1])

    return data


def extract_sighting(output, search_result):
    start_time = datetime.strptime(
        search_result['task']['time'].split('+')[0],
        '%Y-%m-%dT%H:%M:%S.%fZ'
    )

    observed_time = {
        'start_time': start_time.isoformat(
            timespec='microseconds') + 'Z',
    }

    observable = {
        'value': output['observable']['value'],
        'type': output['observable']['type']
    }

    sighting_id = f'transient:{uuid4()}'

    doc = {
        'id': sighting_id,
        'count': 1,
        'observables': [observable],
        'observed_time': observed_time,
        'external_ids': [search_result['_id']],
        'source_uri': current_app.config['URL_SCAN_UI_URL'].format(
            id=search_result['_id']),
        'relations': get_relations(search_result),
        'data': get_data(search_result['stats']),
        **current_app.config['CTIM_SIGHTING_DEFAULT']
    }

    return doc


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    # Not implemented
    return jsonify_data({})


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    relay_input = get_json(ObservableSchema(many=True))

    observables = group_observables(relay_input)

    if not observables:
        return jsonify_data({})

    api_key = get_jwt().get('key', '')
    client = URLScanClient(
        base_url=current_app.config['URL_SCAN_API_URL'],
        api_key=api_key,
        user_agent=current_app.config['USER_AGENT']
    )

    g.sightings = []

    for observable in observables:

        output = client.get_search_data(observable)

        if output:

            search_results = output['results']
            search_results.sort(key=lambda x: x['task']['time'], reverse=True)

            if len(search_results) >= current_app.config['CTR_ENTITIES_LIMIT']:
                search_results = \
                    search_results[:current_app.config['CTR_ENTITIES_LIMIT']]

            for search_result in search_results:
                g.sightings.append(extract_sighting(output, search_result))

    relay_output = {}

    if g.sightings:
        relay_output['sightings'] = format_docs(g.sightings)

    return jsonify_data(relay_output)


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data([])
