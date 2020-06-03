import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    URL_SCAN_API_URL = 'https://urlscan.io/api/v1/{endpoint}'

    URL_SCAN_HEALTH_CHECK_PARAM = 'ip:1.1.1.1'
