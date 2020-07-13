INVALID_ARGUMENT = 'invalid argument'
PERMISSION_DENIED = 'permission denied'
UNKNOWN = 'unknown'
NOT_FOUND = 'not found'
INTERNAL = 'internal error'
TOO_MANY_REQUESTS = 'too many requests'
SERVER_UNAVAILABLE = 'service unavailable'
BAD_REQUEST = 'bad request'


class TRError(Exception):
    def __init__(self, code, message, type_='fatal'):
        super().__init__()
        self.code = code or UNKNOWN
        self.message = message or 'Something went wrong.'
        self.type_ = type_

    @property
    def json(self):
        return {'type': self.type_,
                'code': self.code,
                'message': self.message}


class URLScanInternalServerError(TRError):
    def __init__(self):
        super().__init__(
            INTERNAL,
            'The URLScan internal error.'
        )


class URLScanNotFoundError(TRError):
    def __init__(self):
        super().__init__(
            NOT_FOUND,
            'The URLScan not found.'
        )


class URLScanInvalidCredentialsError(TRError):
    def __init__(self):
        super().__init__(
            PERMISSION_DENIED,
            'The request is missing a valid API key.'
        )


class URLScanUnexpectedResponseError(TRError):
    def __init__(self, payload):
        error_payload = payload.json()

        super().__init__(
            UNKNOWN,
            str(error_payload)
        )


class URLScanTooManyRequestsError(TRError):
    def __init__(self):

        super().__init__(
            TOO_MANY_REQUESTS,
            'Too many requests have been made to '
            'URLScan. Please, try again later.'
        )


class URLScanUnavailableError(TRError):
    def __init__(self):

        super().__init__(
            SERVER_UNAVAILABLE,
            'The urlscan.io is unavailable. Please, try again later.'
        )


class URLScanBadRequestError(TRError):
    def __init__(self):

        super().__init__(
            BAD_REQUEST,
            'You sent weird url. '
            'Please check the correctness of your url and try again.'
        )


class BadRequestError(TRError):
    def __init__(self, error_message):
        super().__init__(
            INVALID_ARGUMENT,
            error_message
        )
