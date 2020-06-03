import requests
from flask import Blueprint, current_app

from api.utils import get_jwt, jsonify_data, url_for, get_response_data

health_api = Blueprint('health', __name__)


def check_health_url_scan():
    url = url_for('search')

    headers = {
        'Accept': 'application/json',
        'API-Key': get_jwt().get('key', '')
    }

    params = {
        'q': current_app.config.get('URL_SCAN_HEALTH_CHECK_PARAM')
    }

    response = requests.get(url, headers=headers, params=params)

    return get_response_data(response)


@health_api.route('/health', methods=['POST'])
def health():
    check_health_url_scan()
    return jsonify_data({'status': 'ok'})
