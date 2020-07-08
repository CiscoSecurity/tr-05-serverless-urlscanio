from functools import partial
from urllib.parse import quote

from flask import Blueprint, current_app, g

from api.schemas import ObservableSchema, ActionFormParamsSchema
from api.utils import get_json, get_jwt, jsonify_data
from api.client import URLScanClient

respond_api = Blueprint('respond', __name__)


get_observables = partial(get_json, schema=ObservableSchema(many=True))
get_action_form_params = partial(get_json, schema=ActionFormParamsSchema())


def get_scan_observables(relay_input):
    result = []
    for obj in relay_input:
        obj['type'] = obj['type'].lower()
        if obj['type'] in current_app.config['URL_SCAN_SCAN_OBSERVABLES']:
            if obj in result:
                continue
            result.append(obj)

    return result


def extract_action(observable):
    return {
        'id': f'respond-urlscan-action-{observable["type"]}-'
              f'{quote(observable["value"], safe="")}',
        'title': 'From SecureX threat response',
        'description': 'Performed via SecureX Threat Response',
        'categories': ['urlscan.io', 'Scan'],
        'query-params': {
            'observable_value': observable['value'],
            'observable_type': observable['type']
        }
    }


@respond_api.route('/respond/observables', methods=['POST'])
def respond_observables():
    relay_input = get_json(ObservableSchema(many=True))

    observables = get_scan_observables(relay_input)

    if not observables:
        return jsonify_data([])

    g.actions = []

    for observable in observables:
        g.actions.append(extract_action(observable))

    return jsonify_data(g.actions)


@respond_api.route('/respond/trigger', methods=['POST'])
def respond_trigger():
    relay_input = get_json(ActionFormParamsSchema())

    api_key = get_jwt().get('key', '')

    client = URLScanClient(
        base_url=current_app.config['URL_SCAN_API_URL'],
        api_key=api_key,
        user_agent=current_app.config['USER_AGENT'],
        observable_types=current_app.config['URL_SCAN_OBSERVABLE_TYPES']
    )

    client.make_scan(relay_input['observable_value'])

    return jsonify_data({'status': 'success'})
