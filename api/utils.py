import json

from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, DecodeError
from flask import request, current_app, jsonify, g
from requests.exceptions import SSLError

from api.errors import (
    BadRequestError,
    URLScanSSLError,
    AuthorizationError
)


def url_for(endpoint):
    return current_app.config['URL_SCAN_API_URL'].format(
        endpoint=endpoint,
    )


def get_jwt():
    """
    Get Authorization token and validate its signature
    against the application's secret key, .
    """

    expected_errors = {
        KeyError: 'Wrong JWT payload structure',
        TypeError: '<SECRET_KEY> is missing',
        BadSignatureError: 'Failed to decode JWT with provided key',
        DecodeError: 'Wrong JWT structure'
    }

    token = get_auth_token()
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'])
        return payload['key']
    except tuple(expected_errors) as error:
        message = expected_errors[error.__class__]
        raise AuthorizationError(message)


def get_auth_token():
    """
    Parse the incoming request's Authorization header and Validate it.
    """

    expected_errors = {
        KeyError: 'Authorization header is missing',
        AssertionError: 'Wrong authorization type'
    }

    try:
        scheme, token = request.headers['Authorization'].split()
        assert scheme.lower() == 'bearer'
        return token
    except tuple(expected_errors) as error:
        raise AuthorizationError(expected_errors[error.__class__])


def get_json(schema):
    """
    Parse the incoming request's data as JSON.
    Validate it against the specified schema.

    Note. This function is just an example of how one can read and check
    anything before passing to an API endpoint, and thus it may be modified in
    any way, replaced by another function, or even removed from the module.
    """

    data = request.get_json(force=True, silent=True, cache=False)

    error = schema.validate(data)

    if error:
        raise BadRequestError(
            f'Invalid JSON payload received. {json.dumps(error)}.')

    return data


def jsonify_data(data):
    return jsonify({'data': data})


def format_docs(docs):
    return {'count': len(docs), 'docs': docs}


def jsonify_errors(error):
    data = {
        'errors': [error],
        'data': {}
    }

    if g.get('sightings'):
        data['data'].update({'sightings': format_docs(g.sightings)})

    if g.get('indicators'):
        data['data'].update({'indicators': format_docs(g.indicators)})

    if g.get('judgements'):
        data['data'].update({'judgements': format_docs(g.judgements)})

    if g.get('relationships'):
        data['data'].update({'relationships': format_docs(g.relationships)})

    if not data['data']:
        data.pop('data')

    return jsonify(data)


def catch_ssl_errors(func):
    def wraps(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SSLError as error:
            raise URLScanSSLError(error)
    return wraps
