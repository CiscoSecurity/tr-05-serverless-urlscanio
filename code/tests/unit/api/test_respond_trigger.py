from http import HTTPStatus

from pytest import fixture
from unittest import mock

from .utils import headers
from tests.unit.mock_for_tests import (
    EXPECTED_RESPONSE_404_ERROR,
    EXPECTED_RESPONSE_500_ERROR,
    EXPECTED_RESPONSE_AUTH_ERROR,
    EXPECTED_RESPONSE_429_ERROR,
    EXPECTED_RESPONSE_503_ERROR,
    SCAN_RESPONSE_MOCK
)

from ..conftest import url_scan_api_response
from ..mock_for_tests import EXPECTED_RESPONSE_OF_JWKS_ENDPOINT


def routes():
    yield '/respond/trigger'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


def test_enrich_call_with_invalid_json_failure(route, client, valid_jwt,
                                               invalid_json):
    response = client.post(
        route, headers=headers(valid_jwt()), json=invalid_json)

    expected_payload = {
        'errors': [
            {
                'code': 'invalid argument',
                'message': mock.ANY,
                'type': 'fatal',
            }
        ]
    }

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == expected_payload


@fixture(scope='module')
def valid_json():
    return {
        'action-id': 'test-action-id',
        'observable_type': 'url',
        'observable_value': 'https://test.com'
    }


def test_respond_trigger_call_success(route, client, valid_jwt, valid_json,
                                      url_scan_api_request):
    url_scan_api_request.return_value = \
        url_scan_api_response(payload=SCAN_RESPONSE_MOCK)

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()

    assert data


def test_respond_trigger_call_auth_error(route, client, valid_jwt, valid_json,
                                         url_scan_api_request,
                                         mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT)

    url_scan_api_request.return_value = (
        url_scan_api_response(status_code=HTTPStatus.UNAUTHORIZED))

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_AUTH_ERROR


def test_respond_trigger_call_404(route, client, valid_jwt, valid_json,
                                  url_scan_api_request,
                                  mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT)

    url_scan_api_request.return_value = (
        url_scan_api_response(status_code=HTTPStatus.NOT_FOUND))

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_404_ERROR


def test_respond_trigger_call_500(route, client, valid_jwt, valid_json,
                                  url_scan_api_request,
                                  mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT)

    url_scan_api_request.return_value = (
        url_scan_api_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR))

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_500_ERROR


def test_respond_trigger_call_429(route, client, valid_jwt, valid_json,
                                  url_scan_api_request,
                                  mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT)

    url_scan_api_request.return_value = (
        url_scan_api_response(status_code=HTTPStatus.TOO_MANY_REQUESTS))

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_429_ERROR


def test_respond_trigger_call_503(route, client, valid_jwt, valid_json,
                                  url_scan_api_request,
                                  mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT)
    url_scan_api_request.return_value = (
        url_scan_api_response(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
    )

    response = client.post(route, headers=headers(valid_jwt()),
                           json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_503_ERROR
