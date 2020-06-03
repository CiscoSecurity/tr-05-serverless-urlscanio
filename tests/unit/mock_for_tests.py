
SEARCH_RESPONSE_MOCK = {
  "results": [
      {
          "task": {
              "visibility": "public",
              "method": "api",
              "time": "2020-06-02T21:35:21.586Z",
              "source": "api",
              "url": "https://exclusivehopie.com/onlinevisitor_us_zt_m/"
                     "index_1.php"
          },
          "stats": {
              "uniqIPs": 1,
              "consoleMsgs": 0,
              "dataLength": 553,
              "encodedDataLength": 684,
              "requests": 1
          },
          "page": {
              "country": "AU",
              "server": "cloudflare",
              "city": "",
              "domain": "exclusivehopie.com",
              "ip": "1.1.1.1",
              "asnname": "CLOUDFLARENET, US",
              "asn": "AS13335",
              "url": "https://exclusivehopie.com/onlinevisitor_us_zt_m/"
                     "index_1.php",
              "ptr": "one.one.one.one"
          },
          "uniq_countries": 1,
          "_id": "13cde17f-a7f5-4e27-8a56-5e81bc086a37",
          "result": "https://urlscan.io/api/v1/result/"
                    "13cde17f-a7f5-4e27-8a56-5e81bc086a37"
      },
      {
          "task": {
              "visibility": "public",
              "method": "api",
              "time": "2020-06-02T19:33:14.851Z",
              "source": "api",
              "url": "http://covid19moodtracker.com"
          },
          "stats": {
              "uniqIPs": 1,
              "consoleMsgs": 0,
              "dataLength": 3801,
              "encodedDataLength": 4401,
              "requests": 4
          },
          "page": {
              "country": "AU",
              "server": "cloudflare",
              "city": "",
              "domain": "covid19moodtracker.com",
              "ip": "1.1.1.1",
              "asnname": "CLOUDFLARENET, US",
              "asn": "AS13335",
              "url": "http://covid19moodtracker.com/",
              "ptr": "one.one.one.one"
          },
          "uniq_countries": 1,
          "_id": "14afd7c3-aee5-4906-acde-9a706ce5bb40",
          "result": "https://urlscan.io/api/v1/result/"
                    "14afd7c3-aee5-4906-acde-9a706ce5bb40"
      }
  ]
}


EXPECTED_RESPONSE_404_ERROR = {
    'errors': [
        {
            'code': 'not found',
            'message': 'The URLScan not found.',
            'type': 'fatal'
        }
    ]
}

EXPECTED_RESPONSE_500_ERROR = {
    'errors': [
        {
            'code': 'internal error',
            'message': 'The URLScan internal error.',
            'type': 'fatal'
        }
    ]
}

EXPECTED_RESPONSE_AUTH_ERROR = {
    'errors': [
        {
            'code': 'permission denied',
            'message': 'The request is missing a valid API key.',
            'type': 'fatal'
        }
    ]
}

EXPECTED_RESPONSE_429_ERROR = {
    'errors': [
        {
            'code': 'too many requests',
            'message': 'Too many requests have been made to URLScan. Please, '
                       'try again later.',
            'type': 'fatal'
        }
    ]
}
