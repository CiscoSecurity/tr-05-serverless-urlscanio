import json

from authlib.jose import jwt
from authlib.jose.errors import JoseError
from flask import request, current_app, jsonify, g
from api.errors import (
    BadRequestError
)


def url_for(endpoint):
    return current_app.config['URL_SCAN_API_URL'].format(
        endpoint=endpoint,
    )


def get_jwt():
    """
    Parse the incoming request's Authorization Bearer JWT for some credentials.
    Validate its signature against the application's secret key.

    Note. This function is just an example of how one can read and check
    anything before passing to an API endpoint, and thus it may be modified in
    any way, replaced by another function, or even removed from the module.
    """

    try:
        scheme, token = request.headers['Authorization'].split()
        assert scheme.lower() == 'bearer'
        return jwt.decode(token, current_app.config['SECRET_KEY'])
    except (KeyError, ValueError, AssertionError, JoseError):
        return {}


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

    if not data['data']:
        data.pop('data')

    return jsonify(data)
