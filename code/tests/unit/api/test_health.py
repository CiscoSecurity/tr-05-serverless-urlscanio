from http import HTTPStatus

from pytest import fixture
from unittest import mock
from requests.exceptions import SSLError

from .utils import headers
from tests.unit.mock_for_tests import (
    EXPECTED_RESPONSE_404_ERROR,
    EXPECTED_RESPONSE_500_ERROR,
    EXPECTED_RESPONSE_AUTH_ERROR,
    EXPECTED_RESPONSE_429_ERROR,
    SEARCH_RESPONSE_MOCK,
    EXPECTED_RESPONSE_SSL_ERROR,
    EXPECTED_AUTHORIZATION_HEADER_ERROR,
    EXPECTED_AUTHORIZATION_TYPE_ERROR,
    EXPECTED_JWT_STRUCTURE_ERROR,
    EXPECTED_JWT_PAYLOAD_STRUCTURE_ERROR
)

from ..conftest import url_scan_api_response
from ..mock_for_tests import EXPECTED_RESPONSE_OF_JWKS_ENDPOINT


def routes():
    yield '/health'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


def test_health_call_success(route, client, valid_jwt, url_scan_api_request):
    url_scan_api_request.return_value = \
        url_scan_api_response(payload=SEARCH_RESPONSE_MOCK)
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK


def test_health_call_auth_error(route, client, valid_jwt,
                                mock_request):
    mock_request.side_effect = (
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT),
        url_scan_api_response(status_code=HTTPStatus.UNAUTHORIZED))
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_AUTH_ERROR


def test_health_call_404(route, client, valid_jwt, mock_request):
    mock_request.side_effect = (
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT),
        url_scan_api_response(status_code=HTTPStatus.NOT_FOUND))
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_404_ERROR


def test_health_call_500(route, client, valid_jwt, mock_request):
    mock_request.side_effect = (
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT),
        url_scan_api_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR))
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_500_ERROR


def test_health_call_429(route, client, valid_jwt, mock_request):
    mock_request.side_effect = (
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT),
        url_scan_api_response(status_code=HTTPStatus.TOO_MANY_REQUESTS))
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_429_ERROR


def test_health_call_ssl_error(route, client, valid_jwt, mock_request):
    mock_exception = mock.MagicMock()
    mock_exception.reason.args.__getitem__().verify_message \
        = 'self signed certificate'
    mock_request.side_effect = (
        url_scan_api_response(payload=EXPECTED_RESPONSE_OF_JWKS_ENDPOINT),
        SSLError(mock_exception)
    )

    response = client.post(route, headers=headers(valid_jwt()))

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_RESPONSE_SSL_ERROR


def test_health_call_auth_header_error(route, client, valid_jwt,
                                       mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=SEARCH_RESPONSE_MOCK)

    response = client.post(route, headers={})

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_AUTHORIZATION_HEADER_ERROR


def test_health_call_auth_type_error(route, client, valid_jwt,
                                     mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=SEARCH_RESPONSE_MOCK)

    header = {
        'Authorization': 'Basic test_jwt'
    }

    response = client.post(route, headers=header)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_AUTHORIZATION_TYPE_ERROR


def test_health_call_jwt_structure_error(route, client, valid_jwt,
                                         mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=SEARCH_RESPONSE_MOCK)

    header = {
        'Authorization': 'Bearer bad_jwt_token'
    }

    response = client.post(route, headers=header)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_JWT_STRUCTURE_ERROR


def test_health_call_payload_structure_error(route, client,
                                             valid_jwt,
                                             mock_request):
    mock_request.return_value = \
        url_scan_api_response(payload=SEARCH_RESPONSE_MOCK)

    response = client.post(
        route,
        headers=headers(valid_jwt(wrong_structure=True))
    )

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_JWT_PAYLOAD_STRUCTURE_ERROR
