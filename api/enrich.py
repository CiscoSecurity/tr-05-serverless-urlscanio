from uuid import uuid4
from functools import partial
from datetime import datetime, timedelta

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


def get_external_references(result_data):
    external_references = []
    for reference_object in current_app.config['URL_SCAN_REFERENCES_OBJECTS']:
        if result_data['task'].get(reference_object):
            external_references.append(
                get_reference_object(
                    reference_object, result_data['task'][reference_object]))
    return external_references


def get_reference_object(description, url):
    return {
      "source_name": current_app.config['URL_SCAN_SOURCE_NAME'],
      "description": description,
      "url": url
    }


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

    sighting_id = f'transient:sighting-{uuid4()}'
    output['relationships'].update({
        search_result['_id']: {
            'indicators_id': [],
            'sighting_id': sighting_id
        }
    })

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


def extract_judgement(output, result_output):
    start_time = datetime.strptime(
        result_output['task']['time'].split('+')[0],
        '%Y-%m-%dT%H:%M:%S.%fZ'
    )
    end_time = start_time + timedelta(
        days=current_app.config['CTIM_VALID_DAYS_PERIOD'])

    valid_time = {
        'start_time': start_time.isoformat(
            timespec='microseconds') + 'Z',
        'end_time': end_time.isoformat(timespec='microseconds') + 'Z'
    }

    observable = {
        'value': output['observable']['value'],
        'type': output['observable']['type']
    }

    judgement_id = f'transient:judgement-{uuid4()}'

    doc = {
        'id': judgement_id,
        'observable': observable,
        'source_uri': result_output['task']['reportURL'],
        'valid_time': valid_time,
        'reason': ', '.join(result_output['verdicts']['overall']['tags']),
        'external_references': get_external_references(result_output),
        **current_app.config['CTIM_JUDGEMENT_DEFAULT']
    }

    return doc


def extract_indicator(output, result_output, category):
    start_time = datetime.strptime(
        result_output['task']['time'].split('+')[0],
        '%Y-%m-%dT%H:%M:%S.%fZ'
    )

    valid_time = {
        'start_time': start_time.isoformat(
            timespec='microseconds') + 'Z'
    }

    indicator_id = f'transient:indicator-{uuid4()}'
    output['relationships'][result_output['task']['uuid']][
        'indicators_id'].append(indicator_id)

    doc = {
        'id': indicator_id,
        'valid_time': valid_time,
        'external_ids': [result_output['task']['uuid']],
        'title': category,
        'tags': result_output['verdicts']['overall']['tags'],
        'external_references': get_external_references(result_output),
        'description':
            current_app.config['CTIM_INDICATOR_DESCRIPTION_TEMPLATE'].format(
                category=category),
        'short_description':
            current_app.config['CTIM_INDICATOR_DESCRIPTION_TEMPLATE'].format(
                category=category),
        **current_app.config['CTIM_INDICATOR_DEFAULT']
    }

    return doc


def extract_relationships(relationships):
    docs = []

    for key in relationships.keys():
        relation = relationships[key]
        sighting_id = relation['sighting_id']

        for indicator_id in relation['indicators_id']:
            relationship_id = f'transient:relationship-{uuid4()}'

            doc = {
                'id': relationship_id,
                'source_ref': indicator_id,
                'target_ref': sighting_id,
                **current_app.config['CTIM_RELATIONSHIPS_DEFAULT']
            }

            docs.append(doc)

    return docs


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
        user_agent=current_app.config['USER_AGENT'],
        observable_types=current_app.config['URL_SCAN_OBSERVABLE_TYPES']
    )

    g.sightings = []
    g.judgements = []
    g.indicators = []
    g.relationships = []

    for observable in observables:

        output = client.get_search_data(observable)

        if output:
            output['relationships'] = {}

            search_results = output['results']
            search_results.sort(key=lambda x: x['task']['time'], reverse=True)

            if len(search_results) > current_app.config['CTR_ENTITIES_LIMIT']:
                search_results = \
                    search_results[:current_app.config['CTR_ENTITIES_LIMIT']]

            for search_result in search_results:
                g.sightings.append(extract_sighting(output, search_result))

                result_output = client.get_result_data(search_result['_id'])
                if result_output['verdicts']['overall']['malicious']:
                    g.judgements.append(
                        extract_judgement(output, result_output))
                    for category in \
                            result_output['verdicts']['overall']['categories']:
                        g.indicators.append(
                            extract_indicator(output, result_output, category))
            g.relationships.extend(
                extract_relationships(output['relationships']))

    relay_output = {}

    if g.sightings:
        relay_output['sightings'] = format_docs(g.sightings)
    if g.judgements:
        relay_output['judgements'] = format_docs(g.judgements)
    if g.indicators:
        relay_output['indicators'] = format_docs(g.indicators)
    if g.relationships:
        relay_output['relationships'] = format_docs(g.relationships)

    return jsonify_data(relay_output)


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data([])
