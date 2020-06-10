
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

EXPECTED_SUCCESS_RESPONSE = {
    'data': {
        'sightings': {
            'count': 2,
            'docs': [
                {
                    'confidence': 'High',
                    'count': 1,
                    'data': {
                        'columns': [
                            {
                                'name': 'uniqIPs',
                                'type': 'integer'
                            },
                            {
                                'name': 'consoleMsgs',
                                'type': 'integer'
                            },
                            {
                                'name': 'dataLength',
                                'type': 'integer'
                            },
                            {
                                'name': 'encodedDataLength',
                                'type': 'integer'
                            },
                            {
                                'name': 'requests',
                                'type': 'integer'
                            }
                        ],
                        'rows': [
                            [1, 0, 553, 684, 1]
                        ]
                    },
                    'description': 'Scan Result',
                    'external_ids': ['13cde17f-a7f5-4e27-8a56-5e81bc086a37'],
                    'internal': False,
                    'observables': [
                        {
                            'type': 'ip',
                            'value': '1.1.1.1'
                        }
                    ],
                    'observed_time': {
                        'start_time': '2020-06-02T21:35:21.586000Z'
                    },
                    'relations': [
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'domain',
                                'value': 'exclusivehopie.com'
                            },
                            'relation': 'Contains',
                            'source': {
                                'type': 'url',
                                'value': 'https://exclusivehopie.com/'
                                         'onlinevisitor_us_zt_m/index_1.php'
                            }
                        },
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'ip',
                                'value': '1.1.1.1'
                            },
                            'relation': 'Resolved_To',
                            'source': {
                                'type': 'domain',
                                'value': 'exclusivehopie.com'
                            }
                        },
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'ip',
                                'value': '1.1.1.1'
                            },
                            'relation': 'Hosted_By',
                            'source': {
                                'type': 'url',
                                'value': 'https://exclusivehopie.com/'
                                         'onlinevisitor_us_zt_m/index_1.php'
                            }
                        }
                    ],
                    'schema_version': '1.0.16',
                    'source': 'urlscan.io',
                    'source_uri': 'https://urlscan.io/result/'
                                  '13cde17f-a7f5-4e27-8a56-5e81bc086a37',
                    'type': 'sighting'
                },
                {
                    'confidence': 'High',
                    'count': 1,
                    'data': {
                        'columns': [
                            {
                                'name': 'uniqIPs',
                                'type': 'integer'
                            },
                            {
                                'name': 'consoleMsgs',
                                'type': 'integer'
                            },
                            {
                                'name': 'dataLength',
                                'type': 'integer'
                            },
                            {
                                'name': 'encodedDataLength',
                                'type': 'integer'
                            },
                            {
                                'name': 'requests',
                                'type': 'integer'
                            }
                        ],
                        'rows': [
                            [1, 0, 3801, 4401, 4]
                        ]
                    },
                    'description': 'Scan Result',
                    'external_ids': ['14afd7c3-aee5-4906-acde-9a706ce5bb40'],
                    'internal': False,
                    'observables': [
                        {
                            'type': 'ip',
                            'value': '1.1.1.1'
                        }
                    ],
                    'observed_time': {
                        'start_time': '2020-06-02T19:33:14.851000Z'
                    },
                    'relations': [
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'domain',
                                'value': 'covid19moodtracker.com'
                            },
                            'relation': 'Contains',
                            'source': {
                                'type': 'url',
                                'value': 'http://covid19moodtracker.com/'
                            }
                        },
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'ip',
                                'value': '1.1.1.1'
                            },
                            'relation': 'Resolved_To',
                            'source': {
                                'type': 'domain',
                                'value': 'covid19moodtracker.com'
                            }
                        },
                        {
                            'origin': 'urlscan.io Module',
                            'related': {
                                'type': 'ip',
                                'value': '1.1.1.1'
                            },
                            'relation': 'Hosted_By',
                            'source': {
                                'type': 'url',
                                'value': 'http://covid19moodtracker.com/'
                            }
                        }
                    ],
                    'schema_version': '1.0.16',
                    'source': 'urlscan.io',
                    'source_uri': 'https://urlscan.io/result/'
                                  '14afd7c3-aee5-4906-acde-9a706ce5bb40',
                    'type': 'sighting'
                }
            ]
        }
    }
}
