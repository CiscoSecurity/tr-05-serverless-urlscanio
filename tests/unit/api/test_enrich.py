from http import HTTPStatus

from pytest import fixture
from unittest import mock

from .utils import headers
from tests.unit.mock_for_tests import (
    EXPECTED_RESPONSE_404_ERROR,
    EXPECTED_RESPONSE_500_ERROR,
    EXPECTED_RESPONSE_AUTH_ERROR,
    EXPECTED_RESPONSE_429_ERROR,
    SEARCH_RESPONSE_MOCK,
    EXPECTED_SUCCESS_RESPONSE,
    RESULT_RESPONCE_MOCK,
    EXPECTED_REFER_RESPONSE
)


def routes():
    yield '/observe/observables'
    yield '/refer/observables'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='function')
def url_scan_api_request():
    with mock.patch('requests.get') as mock_request:
        yield mock_request


def url_scan_api_response(*, ok, payload=None, status_error=None):
    mock_response = mock.MagicMock()

    mock_response.ok = ok

    if ok and not payload:
        payload = SEARCH_RESPONSE_MOCK

    else:
        mock_response.status_code = status_error

    mock_response.json = lambda: payload

    return mock_response


@fixture(scope='module')
def invalid_json():
    return [{'type': 'unknown', 'value': ''}]


def test_enrich_call_with_invalid_json_failure(route, client, valid_jwt,
                                               invalid_json):
    response = client.post(
        route, headers=headers(valid_jwt), json=invalid_json)

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
    return [{'type': 'ip', 'value': '1.1.1.1'}]


@fixture(scope='module')
def valid_json_multiple():
    return [
        {'type': 'ip', 'value': '1.1.1.1'},
        {'type': 'ip', 'value': '2.2.2.2'},
    ]


def test_enrich_call_success(route, client, valid_jwt, valid_json,
                             url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_RESPONCE_MOCK)
    )

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()

    if route == 'observe/observables':

        assert data['data']['sightings']['docs'][0].pop('id')
        assert data['data']['sightings']['docs'][1].pop('id')
        assert data['data']['judgements']['docs'][0].pop('id')
        assert data['data']['judgements']['docs'][1].pop('id')

        assert data == EXPECTED_SUCCESS_RESPONSE

    if route == '/refer/observables':
        assert data['data'][0].pop('id')
        assert data == EXPECTED_REFER_RESPONSE


def test_enrich_error_with_data(route, client, valid_jwt, valid_json_multiple,
                                url_scan_api_request):

    if route == 'observe/observables':

        url_scan_api_request.side_effect = (
            url_scan_api_response(ok=True),
            url_scan_api_response(ok=True, payload=RESULT_RESPONCE_MOCK),
            url_scan_api_response(ok=True, payload=RESULT_RESPONCE_MOCK),
            url_scan_api_response(
                ok=False, status_error=HTTPStatus.TOO_MANY_REQUESTS),
        )

        response = client.post(route, headers=headers(valid_jwt),
                               json=valid_json_multiple)

        assert response.status_code == HTTPStatus.OK

        data = response.get_json()

        assert data['data']['sightings']['docs'][0].pop('id')
        assert data['data']['sightings']['docs'][1].pop('id')
        assert data['data']['judgements']['docs'][0].pop('id')
        assert data['data']['judgements']['docs'][1].pop('id')

        expected_data = {}
        expected_data.update(EXPECTED_SUCCESS_RESPONSE)
        expected_data.update(EXPECTED_RESPONSE_429_ERROR)

        assert data == expected_data


def test_health_call_auth_error(route, client, valid_jwt, valid_json,
                                url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.UNAUTHORIZED)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_AUTH_ERROR


def test_health_call_404(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.NOT_FOUND)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_404_ERROR


def test_health_call_500(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.INTERNAL_SERVER_ERROR)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_500_ERROR


def test_health_call_429(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.TOO_MANY_REQUESTS)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_429_ERROR
