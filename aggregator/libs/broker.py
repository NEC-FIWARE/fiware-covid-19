#
# MIT License
#
# Copyright (c) 2021 NEC Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
"""
import json
import math
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlencode

BROKER = {
    'v2': {
        'get-entity': '/v2/entities/{}',
        'get-entities': '/v2/entities',
        'code-query': 'municipalityCode==\'{}\'',
        'count-header': 'Fiware-Total-Count',
        'update': '/v2/op/update',
        'decode': 'utf-8',
        'link': '',
    },
    'ld': {
        'get-entity': '/ngsi-ld/v1/entities/{}',
        'get-entities': '/ngsi-ld/v1/entities',
        'code-query': 'municipalityCode=="{}"',
        'count-header': 'NGSILD-Results-Count',
        'update': '/ngsi-ld/v1/entityOperations/upsert',
        'link': '<{}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'decode': 'utf-8',
    }
}

QUERY_LIMIT = 1000


class Broker():
    def __init__(self,
                 broker_url: str,
                 broker_version: str,
                 broker_service: str,
                 broker_path: str,
                 broker_token: str,
                 broker_context: str):
        """
        """
        if broker_version != 'v2' and broker_version != 'ld':
            raise ValueError('invalid ngsi version.')

        self.broker_url: str = broker_url
        self.broker_version: str = broker_version
        self.broker_service: str = broker_service
        self.broker_path: str = broker_path
        self.broker_token: str = broker_token
        self.broker_context: str = broker_context

    def get_entity(self, entity_type: str, entity_id: str) -> dict:
        api = urljoin(self.broker_url,
                      BROKER[self.broker_version]['get-entity'].format(entity_id))

        headers = {
            'Accept': 'application/json',
        }
        if self.broker_service:
            headers['Fiware-Service'] = self.broker_service
        if self.broker_path:
            headers['Fiware-ServicePath'] = self.broker_path
        if self.broker_token:
            headers['Authorization'] = 'Bearer: {}'.format(self.broker_token)
        if self.broker_version == 'ld':
            headers['Link'] = BROKER[self.broker_version]['link'].format(
                self.broker_context)

        params = {
            'options': 'keyValues',
        }
        if self.broker_version == 'v2':
            params['type'] = entity_type

        url = '{}?{}'.format(api, urlencode(params))

        try:
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request) as response:
                print(response.status, response.reason)

                result = json.loads(response.read().decode(
                    BROKER[self.broker_version]['decode']), strict=False)

                return result

        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            print(e.read())
            exit()

    def get_entities(self, entity_type: str, municipality_code: str) -> list:
        """
        """
        entities = []

        api = urljoin(self.broker_url,
                      BROKER[self.broker_version]['get-entities'])

        headers = {
            'Accept': 'application/json',
        }
        if self.broker_service:
            headers['Fiware-Service'] = self.broker_service
        if self.broker_path:
            headers['Fiware-ServicePath'] = self.broker_path
        if self.broker_token:
            headers['Authorization'] = 'Bearer: {}'.format(self.broker_token)
        if self.broker_version == 'ld':
            headers['Link'] = BROKER[self.broker_version]['link'].format(
                self.broker_context)

        params = {
            'type': entity_type,
            'q': BROKER[self.broker_version]['code-query'].format(municipality_code),
            'options': 'keyValues,count',
            'limit': QUERY_LIMIT,
            'offset': 0
        }

        url = '{}?{}'.format(api, urlencode(params))

        try:
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request) as response:
                print(response.status, response.reason)

                entities.extend(json.loads(response.read().decode(
                    BROKER[self.broker_version]['decode']), strict=False))
                total_count = int(
                    response.headers[BROKER[self.broker_version]['count-header']])

            if QUERY_LIMIT < total_count:
                max_get = math.ceil(total_count / QUERY_LIMIT)

                for i in range(1, max_get):
                    params['offset'] = i * QUERY_LIMIT
                    url = '{}?{}'.format(api, urlencode(params))

                    request = urllib.request.Request(url, headers=headers)

                    with urllib.request.urlopen(request) as response:
                        print(response.status, response.reason)

                        entities.extend(json.loads(
                            response.read().decode(BROKER[self.broker_version]['decode']), strict=False))

        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            print(e.read())
            exit()

        print('entities:', len(entities))

        return entities

    def broker_update(self, entities: list) -> None:
        """
        """
        api = urljoin(self.broker_url, BROKER[self.broker_version]['update'])

        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }
        if self.broker_service:
            headers['Fiware-Service'] = self.broker_service
        if self.broker_path:
            headers['Fiware-ServicePath'] = self.broker_path
        if self.broker_token:
            headers['Authorization'] = 'Bearer: {}'.format(self.broker_token)
        if self.broker_version == 'ld':
            headers['Link'] = BROKER[self.broker_version]['link'].format(
                self.broker_context)

        if self.broker_version == 'v2':
            payload = {
                'actionType': 'append',
                'entities': entities
            }
        elif self.broker_version == 'ld':
            payload = entities
        else:
            raise ValueError('invalid ngsi version.')

        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        try:
            request = urllib.request.Request(
                api, data=data, headers=headers, method='POST')

            with urllib.request.urlopen(request) as response:
                print(response.status, response.reason)

        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            print(e.read())
            exit()
