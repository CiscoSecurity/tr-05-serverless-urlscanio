from http import HTTPStatus

import requests

from api.errors import (
    URLScanInvalidCredentialsError,
    URLScanNotFoundError,
    URLScanInternalServerError,
    URLScanTooManyRequestsError,
    URLScanUnexpectedResponseError,
    URLScanUnavailableError
)


class URLScanClient:
    expected_response_errors = {
        HTTPStatus.UNAUTHORIZED: URLScanInvalidCredentialsError,
        HTTPStatus.NOT_FOUND: URLScanNotFoundError,
        HTTPStatus.INTERNAL_SERVER_ERROR: URLScanInternalServerError,
        HTTPStatus.TOO_MANY_REQUESTS: URLScanTooManyRequestsError,
        HTTPStatus.BAD_GATEWAY: URLScanUnavailableError,
        HTTPStatus.SERVICE_UNAVAILABLE: URLScanUnavailableError,
        HTTPStatus.GATEWAY_TIMEOUT: URLScanUnavailableError
    }

    def __init__(self, base_url, api_key, user_agent, observable_types):
        self.base_url = base_url
        self.headers = {
            'Accept': 'application/json',
            'X-API-Key': api_key,
            'User-Agent': user_agent
        }
        self.observable_types = observable_types

    def _get_response_data(self, response):

        if response.ok:
            return response.json()

        else:
            if response.status_code in self.expected_response_errors:
                raise self.expected_response_errors[response.status_code]
            elif response.status_code == HTTPStatus.BAD_REQUEST:
                return {}
            else:
                raise URLScanUnexpectedResponseError(response)

    def _get(self, url, **kwargs):
        response = requests.get(url, headers=self.headers, **kwargs)
        return self._get_response_data(response)

    def _join_url(self, endpoint):
        return self.base_url.format(endpoint=endpoint)

    def get_search_data(self, observable):
        url = self._join_url('search')
        params = {
            'q': self.observable_types[observable['type']].format(
                observable=observable['value'])
        }
        result = self._get(url, params=params)
        result['observable'] = observable
        return result

    def get_result_data(self, id_):
        endpoint = 'result/{}'.format(id_)
        url = self._join_url(endpoint)
        return self._get(url)
