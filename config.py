import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', None)

    URL_SCAN_SOURCE_NAME = 'urlscan.io'

    URL_SCAN_API_URL = 'https://urlscan.io/api/v1/{endpoint}'
    URL_SCAN_UI_URL = 'https://urlscan.io/result/{id}'
    URL_SCAN_UI_BROWSE = 'https://urlscan.io/{type}/{value}'
    URL_SCAN_UI_SEARCH = 'https://urlscan.io/search/{params}'

    URL_SCAN_BROWSE_TYPES = {
        'ip': 'ip',
        'ipv6': 'ip',
        'domain': 'domain'
    }
    URL_SCAN_SEARCH_TYPES = {
        'ip': '#ip:"{value}"',
        'ipv6': '#ip:"{value}"',
        'domain': '#domain:{value}',
        'url': '#"{value}"'
    }

    URL_SCAN_HEALTH_CHECK_OBSERVABLE = {
        'type': 'ip',
        'value': '1.1.1.1'
    }

    URL_SCAN_OBSERVABLE_TYPES = {
        'ip': 'page.ip:"{observable}"',
        'ipv6': 'page.ip:"{observable}"',
        'domain': 'page.domain:"{observable}"',
        'url': 'page.url.keyword:"{observable}"'
    }
    URL_SCAN_SCAN_OBSERVABLES = ['url']

    URL_SCAN_REFERENCES_OBJECTS = ['domURL', 'screenshotURL', 'reportURL']

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

    CTIM_SCHEMA_VERSION = '1.0.17'

    CTIM_SIGHTING_DEFAULT = {
        'type': 'sighting',
        'schema_version': CTIM_SCHEMA_VERSION,
        'source': URL_SCAN_SOURCE_NAME,
        'confidence': 'High',
        'internal': False,
        'description': 'Scan Result'
    }

    CTIM_JUDGEMENT_DEFAULT = {
        'type': 'judgement',
        'schema_version': CTIM_SCHEMA_VERSION,
        'source': URL_SCAN_SOURCE_NAME,
        'confidence': 'High',
        'severity': 'High',
        'priority': 85,
        'disposition_name': 'Malicious',
        'disposition': 2
    }

    CTIM_INDICATOR_DEFAULT = {
        'type': 'indicator',
        'schema_version': CTIM_SCHEMA_VERSION,
        'producer': URL_SCAN_SOURCE_NAME,
        'confidence': 'High'
    }

    CTIM_RELATIONSHIPS_DEFAULT = {
        'type': 'relationship',
        'relationship_type': 'indicates',
        'schema_version': CTIM_SCHEMA_VERSION
    }

    CTIM_INDICATOR_DESCRIPTION_TEMPLATE = 'Сlassified as {category}'
    CTIM_VALID_DAYS_PERIOD = 7
