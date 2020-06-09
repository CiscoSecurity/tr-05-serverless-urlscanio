import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    URL_SCAN_SOURCE_NAME = 'urlscan.io'

    URL_SCAN_API_URL = 'https://urlscan.io/api/v1/{endpoint}'

    URL_SCAN_HEALTH_CHECK_OBSERVABLE = {
        'type': 'ip',
        'value': '1.1.1.1'
    }

    URL_SCAN_OBSERVABLE_TYPES = {
        'ip': 'ip:{observable}',
        'ipv6': 'ip:{observable}',
        'domain': 'domain:{observable}',
        'url': 'page.url:{observable}'
    }

    USER_AGENT = ('Cisco Threat Response Integrations '
                  '<tr-integrations-support@cisco.com>')

    CTR_DEFAULT_ENTITIES_LIMIT = 100
    CTR_ENTITIES_LIMIT = CTR_DEFAULT_ENTITIES_LIMIT

    try:
        limit = int(os.environ.get('CTR_ENTITIES_LIMIT'))
        if limit > 0:
            CTR_ENTITIES_LIMIT = limit
    except (ValueError, TypeError):
        pass

    CTIM_SCHEMA_VERSION = '1.0.16'

    CTIM_SIGHTING_DEFAULT = {
        'type': 'sighting',
        'schema_version': CTIM_SCHEMA_VERSION,
        'source': URL_SCAN_SOURCE_NAME,
        'confidence': 'High',
        'internal': False,
        'description': 'Scan Result'
    }
