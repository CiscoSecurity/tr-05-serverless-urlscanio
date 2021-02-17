from flask import Blueprint, current_app

from api.utils import get_jwt, jsonify_data
from api.client import URLScanClient

health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    api_key = get_jwt()
    client = URLScanClient(
        base_url=current_app.config['URL_SCAN_API_URL'],
        api_key=api_key,
        user_agent=current_app.config['USER_AGENT'],
        observable_types=current_app.config['URL_SCAN_OBSERVABLE_TYPES']
    )
    client.get_search_data(
        current_app.config['URL_SCAN_HEALTH_CHECK_OBSERVABLE'])
    return jsonify_data({'status': 'ok'})
