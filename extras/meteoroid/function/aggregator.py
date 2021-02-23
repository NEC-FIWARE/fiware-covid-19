#!/usr/bin/env python
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

import os
from datetime import datetime, timedelta
import functools
import json
import math
import urllib.error
import urllib.request
import urllib.parse


def main(params):
    data = config_over_write(params['data'][0])

    load_config(data)

    municipality_code = CODE
    aggregate_types = AGGREGATE

    if not BROKER_URL:
        return {'status': 'BROKER_URL is none.'}

    if not municipality_code:
        return {'status': 'no municipality code enterd.'}

    entities = []
    broker = Broker(BROKER_URL,
                    broker_version=BROKER_VERSION,
                    broker_service=BROKER_SERVICE,
                    broker_path=BROKER_PATH,
                    broker_token=BROKER_TOKEN,
                    broker_context=BROKER_CONTEXT)

    for aggregate_type in aggregate_types:

        builder = select_builder(broker, aggregate_type)

        aggregated = builder.build_entity(municipality_code)

        broker.broker_update([aggregated])

        entities.append(aggregated['id'])

    r = update_status(data, entities)
    if not r:
        return {'status': 'status update error', 'entities': entities}

    return {'status': 'ok', 'entities': entities}


def config_over_write(data):
    if 'broker' not in data:
        data['broker'] = {}

    if 'params' in data:
        for key in data['params']:
            data['broker'][key] = data['params'][key]

    return data


def update_status(params, entities):
    url = urllib.parse.urljoin(params['broker']['url'], '/v2/entities')
    url = url + '?' + urllib.parse.urlencode({'options': 'keyValues,upsert'})

    req = urllib.request.Request(url)
    req.add_header('Fiware-Service', params['broker']['service'])
    req.add_header('Fiware-ServicePath', params['broker']['path'])
    req.add_header('Content-Type', 'application/json')

    body = {}
    body['id'] = 'urn:ngsi-ld:Covid19Status:' + params['code']
    body['type'] = 'Covid19Status'
    body['modifiedAt'] = datetime.now().isoformat()
    body['entities'] = entities

    body = json.dumps(body, ensure_ascii=False).encode()

    try:
        res = urllib.request.urlopen(req, body)

    except urllib.error.HTTPError as err:
        print(err.code)
        print(err.reason)
        return False
    except urllib.error.URLError as err:
        print(err.reason)
        return False
    else:
        if res.status != 204:
            print(res.status)
            print(res.read().decode('utf-8'))
            res.close()
            return False
        res.close()

    return True


def arg_parse():
    aggregate_types = []
    for builder in BUILDERS:
        aggregate_types.append(builder.AGGREGATE_TYPE)

    parser = argparse.ArgumentParser(
        description='Entity aggregation tool.',
        epilog="Aggregate types:\n" + "\n".join(aggregate_types),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-m', '--mcode', help='Municipality code.')
    parser.add_argument(
        '-t', '--type', help="Aggregate type.")
    parser.add_argument(
        '-c', '--config', help='Config file.')

    return parser.parse_args()


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

        self.broker_url = broker_url
        self.broker_version = broker_version
        self.broker_service = broker_service
        self.broker_path = broker_path
        self.broker_token = broker_token
        self.broker_context = broker_context

    def get_entity(self, entity_type: str, entity_id: str) -> dict:
        api = urllib.parse.urljoin(self.broker_url,
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

        url = '{}?{}'.format(api, urllib.parse.urlencode(params))

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

        api = urllib.parse.urljoin(self.broker_url,
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

        url = '{}?{}'.format(api, urllib.parse.urlencode(params))

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
                    url = '{}?{}'.format(api, urllib.parse.urlencode(params))

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
        api = urllib.parse.urljoin(self.broker_url, BROKER[self.broker_version]['update'])

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


class EntityBuilder():

    AGGREGATE_TYPE = ""
    ENTITY_TYPE = ""

    def __init__(self, broker: Broker):
        """
        """
        self.broker = broker

    def build_entity(self, municipality_code: str) -> list:
        """
        """
        pass

    def build_entity_mockup(self, municipality_code: str):
        """
        """
        iso_datetime = datetime.now().isoformat()
        if self.broker.broker_version == 'v2':
            return {
                'type': self.ENTITY_TYPE,
                'id': 'urn:ngsi-ld:{}:{}'.format(self.ENTITY_TYPE, municipality_code),
                'date': {'type': 'DateTime', 'value': iso_datetime},
                'data': {'type': 'StructuredValue', 'value': []}
            }
        elif self.broker.broker_version == 'ld':
            return {
                'type': self.ENTITY_TYPE,
                'id': 'urn:ngsi-ld:{}:{}'.format(self.ENTITY_TYPE, municipality_code),
                'date': {'type': 'Property', 'value': iso_datetime},
                'data': {'type': 'Property', 'value': []}
            }
        else:
            raise ValueError('invalid ngsi version.')


def select_builder(broker, aggregate_type) -> EntityBuilder:
    results = list(
        filter(lambda builder: builder.AGGREGATE_TYPE == aggregate_type, BUILDERS))

    if len(results) == 0:
        print('Aggregate type is not found. ({})'.format(aggregate_type))
        exit()

    if len(results) != 1:
        print('Aggregate: duplicated entity type. ({})'.format(aggregate_type))
        exit()

    return results[0](broker)


def date_range_to_today(start_dt: datetime) -> list:
    return date_range(start_dt, datetime.now())


def date_range(start_dt: datetime, end_dt: datetime) -> list:
    return list(start_dt + timedelta(days=i)
                for i in range((end_dt - start_dt).days + 1))


def iso_to_datetime(iso_string: str) -> datetime:
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        pass
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        pass
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        pass

    raise ValueError('invalid format. {}'.format(iso_string))


def weekday_name(dt: datetime) -> str:
    return ['月', '火', '水', '木', '金', '土', '日'][dt.weekday()]


COVID19_PATIENTS = 'Covid19Patients'
COVID19_TEST_PEOPLE = 'Covid19TestPeople'
COVID19_TEST_COUNT = 'Covid19TestCount'
COVID19_CONFIRM_NEGATIVE = 'Covid19ConfirmNegative'
COVID19_CALL_CENTER = 'Covid19CallCenter'

BROKER_VERSION = os.getenv('BROKER_VERSION', 'v2')
BROKER_URL = os.getenv('BROKER_URL')
BROKER_SERVICE = os.getenv('BROKER_SERVICE')
BROKER_PATH = os.getenv('BROKER_PATH', '/')
BROKER_TOKEN = os.getenv('BROKER_TOKEN')
BROKER_CONTEXT = os.getenv(
    'BROKER_CONTEXT', 'https://cio-context.fiware-testbed.jp/cio-context-en.jsonld')
CODE = ''
AGGREGATE = []
CONFIG_TYPE = ''


def load_config(config):
    global BROKER_VERSION
    global BROKER_URL
    global BROKER_SERVICE
    global BROKER_PATH
    global BROKER_TOKEN
    global BROKER_CONTEXT
    global CODE
    global AGGREGATE
    global CONFIG_TYPE

    CONFIG_TYPE = 'yml'

    if 'type' in config['broker']:
        BROKER_VERSION = config['broker']['type']

    if 'url' in config['broker']:
        BROKER_URL = config['broker']['url']

    if 'service' in config['broker']:
        BROKER_SERVICE = config['broker']['service']

    if 'path' in config['broker']:
        BROKER_PATH = config['broker']['path']

    if 'token' in config['broker']:
        BROKER_TOKEN = config['broker']['token']

    if 'context' in config['broker']:
        BROKER_TOKEN = config['broker']['context']

    CODE = config['code']
    AGGREGATE = config['aggregate']


class CallCenterDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'CallCenterDaily'
    ENTITY_TYPE = 'Covid19CallCenterDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_CALL_CENTER, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['acceptedAt'])

        # daily
        for entity in entities:
            dt = iso_to_datetime(entity['acceptedAt'])
            aggregated['data']['value'].append({
                '日付': dt.isoformat(),
                '曜日': weekday_name(dt),
                '9-13時': -1,
                '13-17時': -1,
                '17-21時': -1,
                'date': dt.strftime('%Y-%m-%d'),
                'w': dt.isocalendar()[1],
                '小計': int(entity['numberOfCalls']),
                'weekly_average_count': 0,
            })

        # weekly average
        data_value_rev = list(reversed(aggregated['data']['value']))
        for i, entity in enumerate(data_value_rev):
            lst = data_value_rev[i:i + 7]
            sub = functools.reduce(
                lambda acc, val: acc + val['小計'], lst, 0)
            ave = math.floor((sub / len(lst)) * 10) / 10
            entity['weekly_average_count'] = ave

        return aggregated


class ConfirmNegativeDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'ConfirmNegativeDaily'
    ENTITY_TYPE = 'Covid19ConfirmNegativeDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_CONFIRM_NEGATIVE, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['confirmedNegativeAt'])

        # daily
        for entity in entities:
            dt = iso_to_datetime(entity['confirmedNegativeAt'])
            aggregated['data']['value'].append({
                '日付': dt.isoformat(),
                '曜日': weekday_name(dt),
                'date': dt.strftime('%Y-%m-%d'),
                'w': dt.isocalendar()[1],
                '小計': int(entity['numberOfNegatives']),
                'weekly_average_count': 0,
            })

        # weekly average
        data_value_rev = list(reversed(aggregated['data']['value']))
        for i, entity in enumerate(data_value_rev):
            lst = data_value_rev[i:i + 7]
            sub = functools.reduce(
                lambda acc, val: acc + val['小計'], lst, 0)
            ave = math.floor((sub / len(lst)) * 10) / 10
            entity['weekly_average_count'] = ave

        return aggregated


class PatientsDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'PatientsDaily'
    ENTITY_TYPE = 'Covid19PatientsDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_PATIENTS, municipality_code)

        if not len(raw_entities):
            return aggregated

        entities = sorted(raw_entities, key=lambda x: (x['patientNo']))

        entities_max = max(map(lambda x: x['publishedAt'], entities))

        dates = [iso_to_datetime(entities_max).strftime('%Y-%m-%d')]

        test_people_count_entity = self.broker.get_entity(
            self.create_type(TestPeopleDailyAggregatedBuilder),
            self.create_id(TestPeopleDailyAggregatedBuilder, municipality_code))

        test_count_entity = self.broker.get_entity(
            self.create_type(TestCountDailyAggregatedBuilder),
            self.create_id(TestCountDailyAggregatedBuilder, municipality_code))

        confirm_negative_entity = self.broker.get_entity(
            self.create_type(ConfirmNegativeDailyAggregatedBuilder),
            self.create_id(ConfirmNegativeDailyAggregatedBuilder, municipality_code))

        call_center_entity = self.broker.get_entity(
            self.create_type(CallCenterDailyAggregatedBuilder),
            self.create_id(CallCenterDailyAggregatedBuilder, municipality_code))

        if test_people_count_entity and len(test_people_count_entity['data']):
            dates.append(test_people_count_entity['data'][-1]['date'])

        if test_count_entity and len(test_count_entity['data']):
            dates.append(test_count_entity['data'][-1]['date'])

        if confirm_negative_entity and len(confirm_negative_entity['data']):
            dates.append(confirm_negative_entity['data'][-1]['date'])

        if call_center_entity and len(call_center_entity['data']):
            dates.append(call_center_entity['data'][-1]['date'])

        max_date = datetime.strptime(max(dates), '%Y-%m-%d')

        data_hash = {}

        # template
        for dt in date_range(datetime(2020, 1, 1), max_date):
            data_hash[dt.strftime('%Y-%m-%d')] = {
                'd': dt.strftime('%Y-%m-%d'),
                '日付': dt.isoformat(),
                '小計': 0,
                'diagnosed_date': dt.strftime('%Y-%m-%d'),
                'count': 0,
                'missing_count': -1,
                'reported_count': -1,
                'weekly_gain_ratio': -1,
                'untracked_percent': -1,
                'weekly_average_count': 0,
                'weekly_average_untracked_count': -1,
                'weekly_average_untracked_increse_percent': -1,
                '退院済': 0,
                '入院中': 0,
                '入院不明': 0,
            }

        # daily
        for entity in entities:
            d = iso_to_datetime(
                entity['publishedAt']).strftime('%Y-%m-%d')

            data_hash[d]['小計'] = data_hash[d]['小計'] + 1
            data_hash[d]['count'] = data_hash[d]['count'] + 1

            if entity['patientDischarged'] == 1:
                data_hash[d]['退院済'] = data_hash[d]['退院済'] + 1
            if entity['patientDischarged'] == 0:
                data_hash[d]['入院中'] = data_hash[d]['入院中'] + 1
            else:
                data_hash[d]['入院不明'] = data_hash[d]['入院不明'] + 1

        # weekly average
        data_keys_rev = list(reversed(list(data_hash.keys())))
        for i, d in enumerate(data_keys_rev):
            days = data_keys_rev[i:i + 7]
            sub = functools.reduce(
                lambda acc, val: acc + data_hash[val]['count'], days, 0)
            ave = math.floor((sub / len(days)) * 10) / 10
            data_hash[d]['weekly_average_count'] = ave
            # print(i, d, days, data_hash[d]['count'], sub, ave)

        aggregated['data']['value'] = list(data_hash.values())

        return aggregated

    def create_type(self, builder: EntityBuilder) -> str:
        return builder.ENTITY_TYPE

    def create_id(self, builder: EntityBuilder, municipality_code: str) -> str:
        id_pattern = 'urn:ngsi-ld:{}:{}'
        return id_pattern.format(builder.ENTITY_TYPE, municipality_code)


class PatientsListAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'PatientsList'
    ENTITY_TYPE = 'Covid19PatientsListAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_PATIENTS, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['patientNo'])

        for entity in reversed(entities):
            aggregated['data']['value'].append({
                '全国地方公共団体コード': entity['municipalityCode'],
                '公表_年月日': entity['publishedAt'],
                '都道府県名': entity['prefectureName'],
                '患者_年代': entity['patientAge'],
                '患者_性別': entity['patientGender'],
            })

        return aggregated


class PatientsSummaryBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'PatientsSummary'
    ENTITY_TYPE = 'Covid19PatientsSummary'

    def build_entity(self, municipality_code):
        """
        """
        # entity
        patients_entity = self.broker.get_entity(
            self.create_type(PatientsDailyAggregatedBuilder),
            self.create_id(PatientsDailyAggregatedBuilder, municipality_code))

        test_people_count_entity = self.broker.get_entity(
            self.create_type(TestPeopleDailyAggregatedBuilder),
            self.create_id(TestPeopleDailyAggregatedBuilder, municipality_code))

        test_count_entity = self.broker.get_entity(
            self.create_type(TestCountDailyAggregatedBuilder),
            self.create_id(TestCountDailyAggregatedBuilder, municipality_code))

        confirm_negative_entity = self.broker.get_entity(
            self.create_type(ConfirmNegativeDailyAggregatedBuilder),
            self.create_id(ConfirmNegativeDailyAggregatedBuilder, municipality_code))

        # last count
        if len(patients_entity['data']):
            patients_ave = patients_entity['data'][-1]['weekly_average_count']
        else:
            patients_ave = 0

        if len(test_people_count_entity['data']):
            test_people_count_ave = test_people_count_entity['data'][-1]['weekly_average_count']
        else:
            test_people_count_ave = 0

        # total count
        patients_total = functools.reduce(
            lambda acc, val: acc + val['小計'], patients_entity['data'], 0)

        discharged_total = functools.reduce(
            lambda acc, val: acc + val['退院済'], patients_entity['data'], 0)

        hospital_total = functools.reduce(
            lambda acc, val: acc + val['入院中'], patients_entity['data'], 0)

        test_people_count_total = functools.reduce(
            lambda acc, val: acc + val['小計'], test_people_count_entity['data'], 0)

        test_count_total = functools.reduce(
            lambda acc, val: acc + val['小計'], test_count_entity['data'], 0)

        confirm_negative_total = functools.reduce(
            lambda acc, val: acc + val['小計'], confirm_negative_entity['data'], 0)

        call_center_total = functools.reduce(
            lambda acc, val: acc + val['小計'], test_people_count_entity['data'], 0)

        # print(patients_total, test_people_count_total, test_count_total,
        #      confirm_negative_total, call_center_total)

        aggregated = self.build_entity_mockup(municipality_code)

        if test_people_count_ave == 0:
            positive_percentage_ave = 0
        else:
            positive_percentage_ave = math.floor(
                (patients_ave / test_people_count_ave) * 10) / 10 * 100

        data = {
            'summary': {
                'date': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                '陽性者数': patients_total,
                '入院中': hospital_total,
                '軽症中等症': -1,
                '重症': -1,
                '宿泊療養': -1,
                '自宅療養': -1,
                '調査中': -1,
                '死亡': -1,
                '退院': discharged_total,
                '検査実施人数': test_people_count_total,
                '検査実施件数': test_count_total,
                '陰性確認数': confirm_negative_total,
                'コールセンター相談件数': call_center_total,
            },
            '(1)新規陽性者数': patients_ave,
            '(2)#7119（東京消防庁救急相談センター）における発熱等相談件数 ': -1,
            '(3)新規陽性者における接触歴等不明者（人数）': -1,
            '(3)新規陽性者における接触歴等不明者（増加比）': -1,
            '(4)PCR・抗原検査（陽性率）': positive_percentage_ave,
            '(4)PCR・抗原検査（検査人数）': test_people_count_ave,
            '(5)救急医療の東京ルールの適用件数': -1,
            '(6)入院患者数': -1,
            '(6)入院患者確保病床数': '-1床',
            '(7)重症患者数': -1,
            '(7)重症患者確保病床数': '-1床',
            '総括コメント-感染状況': {
                'level': -1,
                'display': {
                    '@ja': '-1',
                    '@en': '-1',
                }
            },
            '総括コメント-医療提供体制': {
                'level': -1,
                'display': {
                    '@ja': '-1',
                    '@en': '-1',
                }
            },
            'children': [
                {
                    'attr': '陽性患者数',
                    'date': iso_to_datetime(patients_entity['date']).strftime('%Y/%m/%d %H:%M:%S'),
                    'value': patients_total,
                    'children': [
                        {
                            'attr': '入院中',
                            'value': hospital_total,
                            'children': [
                                {
                                    'attr': '軽症・中等症',
                                    'value': -1,
                                },
                                {
                                    'attr': '重症',
                                    'value': -1,
                                }
                            ]
                        },
                        {
                            'attr': '退院',
                            'value': discharged_total,
                        },
                        {
                            'attr': '死亡',
                            'value': -1,
                        },
                        {
                            'attr': '宿泊療養',
                            'value': -1,
                        },
                        {
                            'attr': '自宅療養',
                            'value': -1,
                        },
                        {
                            'attr': '調査中',
                            'value': -1,
                        }
                    ]
                }
            ]
        }

        aggregated['data']['value'] = data

        return aggregated

    def create_type(self, builder: EntityBuilder) -> str:
        return builder.ENTITY_TYPE

    def create_id(self, builder: EntityBuilder, municipality_code: str) -> str:
        id_pattern = 'urn:ngsi-ld:{}:{}'
        return id_pattern.format(builder.ENTITY_TYPE, municipality_code)


class TestCountDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'TestCountDaily'
    ENTITY_TYPE = 'Covid19TestCountDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_TEST_COUNT, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['testedAt'])

        # dayly
        for entity in entities:
            dt = iso_to_datetime(entity['testedAt'])
            aggregated['data']['value'].append({
                '日付': dt.isoformat(),
                '曜日': weekday_name(dt),
                'date': dt.strftime('%Y-%m-%d'),
                'w': dt.isocalendar()[1],
                '小計': int(entity['numberOfTests']),
                'weekly_average_count': 0,
            })

        # weekly average
        data_value_rev = list(reversed(aggregated['data']['value']))
        for i, entity in enumerate(data_value_rev):
            lst = data_value_rev[i:i + 7]
            sub = functools.reduce(
                lambda acc, val: acc + val['小計'], lst, 0)
            ave = math.floor((sub / len(lst)) * 10) / 10
            entity['weekly_average_count'] = ave

        return aggregated


class TestPeopleDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'TestPeopleDaily'
    ENTITY_TYPE = 'Covid19TestPeopleDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            COVID19_TEST_PEOPLE, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['testedAt'])

        # daily
        for entity in entities:
            dt = iso_to_datetime(entity['testedAt'])
            aggregated['data']['value'].append({
                '日付': dt.isoformat(),
                '曜日': weekday_name(dt),
                'date': dt.strftime('%Y-%m-%d'),
                'w': dt.isocalendar()[1],
                '小計': int(entity['numberOfTestedPeople']),
                'weekly_average_count': 0,
            })

        # weekly average
        data_value_rev = list(reversed(aggregated['data']['value']))
        for i, entity in enumerate(data_value_rev):
            lst = data_value_rev[i:i + 7]
            sub = functools.reduce(
                lambda acc, val: acc + val['小計'], lst, 0)
            ave = math.floor((sub / len(lst)) * 10) / 10
            entity['weekly_average_count'] = ave

        return aggregated


BUILDERS = [
    PatientsSummaryBuilder,
    PatientsDailyAggregatedBuilder,
    PatientsListAggregatedBuilder,
    TestPeopleDailyAggregatedBuilder,
    TestCountDailyAggregatedBuilder,
    ConfirmNegativeDailyAggregatedBuilder,
    CallCenterDailyAggregatedBuilder,
]
