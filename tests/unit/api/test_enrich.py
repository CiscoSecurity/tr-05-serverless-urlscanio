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
    EXPECTED_RESPONSE_503_ERROR,
    SEARCH_RESPONSE_MOCK,
    EXPECTED_SUCCESS_RESPONSE,
    RESULT_1_RESPONCE_MOCK,
    RESULT_2_RESPONCE_MOCK,
    EXPECTED_REFER_RESPONSE,
    EXPECTED_RESPONSE_SSL_ERROR,
    EXPECTED_AUTHORIZATION_HEADER_ERROR,
    EXPECTED_AUTHORIZATION_TYPE_ERROR,
    EXPECTED_JWT_STRUCTURE_ERROR,
    EXPECTED_JWT_PAYLOAD_STRUCTURE_ERROR,
    EXPECTED_WRONG_SECRET_KEY_ERROR,
    EXPECTED_MISSED_SECRET_KEY_ERROR
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
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()

    if route == '/observa/observables':

        sightings_data = data['data']['sightings']
        sighting_id_1 = sightings_data['docs'][0].pop('id')
        sighting_id_2 = sightings_data['docs'][1].pop('id')

        judgements_data = data['data']['judgements']
        assert judgements_data['docs'][0].pop('id')
        assert judgements_data['docs'][1].pop('id')

        indicators_data = data['data']['indicators']
        indicator_id_1 = indicators_data['docs'][0].pop('id')
        indicator_id_2 = indicators_data['docs'][1].pop('id')

        relationships_data = data['data']['relationships']
        assert relationships_data['docs'][0].pop('id')
        assert relationships_data['docs'][1].pop('id')
        assert relationships_data['docs'][0].pop(
            'source_ref') == indicator_id_1
        assert relationships_data['docs'][1].pop(
            'source_ref') == indicator_id_2
        assert relationships_data['docs'][0].pop('target_ref') == sighting_id_1
        assert relationships_data['docs'][1].pop('target_ref') == sighting_id_2

        assert data == EXPECTED_SUCCESS_RESPONSE

    if route == '/refer/observables':
        assert data['data'][0].pop('id')
        assert data == EXPECTED_REFER_RESPONSE


def test_enrich_error_with_data(route, client, valid_jwt, valid_json_multiple,
                                url_scan_api_request):

    if route == '/observe/observables':

        url_scan_api_request.side_effect = (
            url_scan_api_response(ok=True),
            url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
            url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK),
            url_scan_api_response(
                ok=False, status_error=HTTPStatus.TOO_MANY_REQUESTS),
        )

        response = client.post(route, headers=headers(valid_jwt),
                               json=valid_json_multiple)

        assert response.status_code == HTTPStatus.OK

        data = response.get_json()

        sightings_data = data['data']['sightings']
        sighting_id_1 = sightings_data['docs'][0].pop('id')
        sighting_id_2 = sightings_data['docs'][1].pop('id')

        judgements_data = data['data']['judgements']
        assert judgements_data['docs'][0].pop('id')
        assert judgements_data['docs'][1].pop('id')

        indicators_data = data['data']['indicators']
        indicator_id_1 = indicators_data['docs'][0].pop('id')
        indicator_id_2 = indicators_data['docs'][1].pop('id')

        relationships_data = data['data']['relationships']
        assert relationships_data['docs'][0].pop('id')
        assert relationships_data['docs'][1].pop('id')
        assert relationships_data['docs'][0].pop(
            'source_ref') == indicator_id_1
        assert relationships_data['docs'][1].pop(
            'source_ref') == indicator_id_2
        assert relationships_data['docs'][0].pop('target_ref') == sighting_id_1
        assert relationships_data['docs'][1].pop('target_ref') == sighting_id_2

        expected_data = {}
        expected_data.update(EXPECTED_SUCCESS_RESPONSE)
        expected_data.update(EXPECTED_RESPONSE_429_ERROR)

        assert data == expected_data


def test_enrich_call_auth_error(route, client, valid_jwt, valid_json,
                                url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.UNAUTHORIZED)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_AUTH_ERROR


def test_enrich_call_404(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.NOT_FOUND)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_404_ERROR


def test_enrich_call_500(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.INTERNAL_SERVER_ERROR)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_500_ERROR


def test_enrich_call_429(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.TOO_MANY_REQUESTS)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_429_ERROR


def test_enrich_call_503(route, client, valid_jwt, valid_json,
                         url_scan_api_request):
    url_scan_api_request.return_value = url_scan_api_response(
        ok=False, status_error=HTTPStatus.SERVICE_UNAVAILABLE)

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_503_ERROR


def test_enrich_call_ssl_error(route, client, valid_jwt, valid_json,
                               url_scan_api_request):
    mock_exception = mock.MagicMock()
    mock_exception.reason.args.__getitem__().verify_message \
        = 'self signed certificate'
    url_scan_api_request.side_effect = SSLError(mock_exception)

    response = client.post(
        route, headers=headers(valid_jwt), json=valid_json
    )

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_RESPONSE_SSL_ERROR


def test_enrich_call_auth_header_error(route, client, valid_jwt, valid_json,
                                       url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )

    response = client.post(route, headers={}, json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_AUTHORIZATION_HEADER_ERROR


def test_enrich_call_auth_type_error(route, client, valid_jwt, valid_json,
                                     url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )
    header = {
        'Authorization': 'Basic test_jwt'
    }

    response = client.post(route, headers=header, json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_AUTHORIZATION_TYPE_ERROR


def test_enrich_call_jwt_structure_error(route, client, valid_jwt, valid_json,
                                         url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )
    header = {
        'Authorization': 'Bearer bad_jwt_token'
    }

    response = client.post(route, headers=header, json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_JWT_STRUCTURE_ERROR


def test_enrich_call_payload_structure_error(route, client,
                                             valid_jwt_with_wrong_payload,
                                             valid_json, url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )

    response = client.post(
        route,
        headers=headers(valid_jwt_with_wrong_payload),
        json=valid_json
    )

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_JWT_PAYLOAD_STRUCTURE_ERROR


def test_enrich_call_wrong_secret_key_error(route, client, valid_jwt,
                                            valid_json, url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )
    right_secret_key = client.application.secret_key
    client.application.secret_key = 'wrong_key'

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    client.application.secret_key = right_secret_key

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_WRONG_SECRET_KEY_ERROR


def test_enrich_call_missed_secret_key_error(route, client, valid_jwt,
                                             valid_json, url_scan_api_request):
    url_scan_api_request.side_effect = (
        url_scan_api_response(ok=True),
        url_scan_api_response(ok=True, payload=RESULT_1_RESPONCE_MOCK),
        url_scan_api_response(ok=True, payload=RESULT_2_RESPONCE_MOCK)
    )
    right_secret_key = client.application.secret_key
    client.application.secret_key = None

    response = client.post(route, headers=headers(valid_jwt), json=valid_json)

    client.application.secret_key = right_secret_key

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()
    assert data == EXPECTED_MISSED_SECRET_KEY_ERROR
