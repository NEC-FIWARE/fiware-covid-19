#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import io
import sys
import re
import argparse
import json
import csv
import yaml
import urllib.request
import urllib.parse
from datetime import datetime

entity_types = None
nubmer_items = None
flag_items = None
date_itimes = None

add_text = None
add_text_default = None
add_number = None
add_number_default = None
add_number_serial = None
add_flag = None
add_date = None

municipality_code = None
required_items = None

dryrun = False
debug = False


def create_ngsi_entities(config, entities):
    broker = config['broker']
    v2 = broker['type'] == 'v2'

    url = urllib.parse.urljoin(
        broker['url'], '/v2/op/update' if v2 else '/ngsi-ld/v1/entityOperations/upsert')
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    if 'service' in broker:
        req.add_header(
            'Fiware-Service' if v2 else 'NGSILD-Tenant', broker['service'])
    if v2 and 'path' in broker:
        req.add_header('Fiware-ServicePath', broker['path'])
    if 'token' in broker:
        req.add_header('Authorization', 'Bearer ' + broker['token'])

    if v2:
        payload = {
            'actionType': 'append',
            'entities': entities
        }
    else:
        payload = entities
        req.add_header('link', '<' + broker['context'] + '>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"')

    if debug:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    body = json.dumps(payload, ensure_ascii=False).encode()

    if dryrun:
        return True

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
        if res.status != 200 and res.status != 204:
            print(res.status)
            print(res.read().decode('utf-8'))
            res.close()
            return False
        res.close()

    return True


trans_table = str.maketrans({'<': '＜', '>': '＞', '"': '”', '\'': '’', '=': '＝', ';': '；', '(': '（', ')': '）'})
trans_num_table = str.maketrans({'０': '0', '１': '1', '２': '2', '３': '3', '４': '4', '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'})


def conv_forbidden_chars(s):
    return s.translate(trans_table)


def get_default_number(value, attr):
    i = attr['serial']
    attr['serial'] = i + 1
    return i


def get_number(value):
    if type(value) is int:
        return value
    elif value is None:
        return 0
    elif re.match(r'^\d+$', str(value).strip()):
        return int(str(value).strip())
    else:
        return 0


def get_flag(value, attr):
    if value == '1':
        flag = 1
    elif value == '0':
        flag = 0
    else:
        flag = -1
    return flag


def init_v2():
    global entity_types, nubmer_items, flag_items, date_itimes
    global add_text, add_text_default, add_number, add_number_default, add_number_serial, add_flag, add_date
    global municipality_code, required_items

    required_items = {
        'Covid19Patients': ['municipalityCode', 'prefectureName', 'cityName', 'publishedAt'],
        'Covid19TestPeople': ['municipalityCode', 'testedAt', 'prefectureName', 'cityName', 'numberOfTestedPeople'],
        'Covid19TestCount': ['municipalityCode', 'testedAt', 'prefectureName', 'cityName', 'numberOfTests'],
        'Covid19ConfirmNegative': ['municipalityCode', 'confirmedNegativeAt', 'prefectureName', 'cityName', 'numberOfNegatives'],
        'Covid19CallCenter': ['municipalityCode', 'acceptedAt', 'prefectureName', 'cityName', 'numberOfCalls']
    }
    entity_types = {'publishedAt': 'Covid19Patients', 'numberOfTestedPeople': 'Covid19TestPeople',
                    'numberOfTests': 'Covid19TestCount', 'numberOfNegatives': 'Covid19ConfirmNegative', 'numberOfCalls': 'Covid19CallCenter'}
    nubmer_items = ('numberOfTestedPeople', 'numberOfTests',
                    'numberOfNegatives', 'numberOfCalls')
    flag_items = ('patientTravelHistory', 'patientDischarged')
    date_itimes = ('publishedAt', 'symptomOnsetAt', 'testedAt',
                   'confirmedNegativeAt', 'acceptedAt')

    def add_text(value, attr): return {'type': 'Text', 'value': conv_forbidden_chars(value)}
    def add_text_default(value, attr): return {'type': 'Text', 'value': conv_forbidden_chars(attr['default'])}
    def add_number(value, attr): return {'type': 'Number', 'value': get_number(value)}
    def add_number_default(value, attr): return {'type': 'Number', 'value': attr['default']}
    def add_number_serial(value, attr): return {'type': 'Number', 'value': get_default_number(value, attr)}
    def add_flag(value, attr): return {'type': 'Number', 'value': get_flag(value, attr)}
    def add_date(value, attr): return None if value == '' else {'type': 'DateTime', 'value': datetime.strptime(value.translate(trans_num_table), attr['format']).isoformat()}

    municipality_code = 'municipalityCode'


def init_ld():
    global entity_types, nubmer_items, flag_items, date_itimes
    global add_text, add_text_default, add_number, add_number_default, add_number_serial, add_flag, add_date
    global municipality_code, required_items

    required_items = {
        '陽性患者属性': ['全国地方公共団体コード', '都道府県名', '市区町村名', '公表_年月日'],
        '検査実施人数': ['全国地方公共団体コード', '実施_年月日', '都道府県名', '市区町村名', '検査実施_人数'],
        '検査実施件数': ['全国地方公共団体コード', '実施_年月日', '都道府県名', '市区町村名', '検査実施_件数'],
        '陰性確認数': ['全国地方公共団体コード', '完了_年月日', '都道府県名', '市区町村名', '陰性確認_件数'],
        'コールセンター相談件数': ['全国地方公共団体コード', '受付_年月日', '都道府県名', '市区町村名', '相談件数']
    }
    entity_types = {'公表_年月日': '陽性患者属性', '検査実施_人数': '検査実施人数',
                    '検査実施_件数': '検査実施件数', '陰性確認_件数': '陰性確認数', '相談件数': 'コールセンター相談件数'}
    nubmer_items = ('検査実施_人数', '検査実施_件数', '陰性確認_件数', '相談件数')
    flag_items = ('患者_渡航歴の有無フラグ', '患者_退院済フラグ')
    date_itimes = ('公表_年月日', '発症_年月日', '実施_年月日', '完了_年月日', '受付_年月日')

    def add_text(value, attr): return {'type': 'Property', 'value': conv_forbidden_chars(value)}
    def add_text_default(value, attr): return {'type': 'Property', 'value': conv_forbidden_chars(attr['default'])}
    def add_number(value, attr): return {'type': 'Property', 'value': get_number(value)}
    def add_number_default(value, attr): return {'type': 'Property', 'value': attr['default']}
    def add_number_serial(value, attr): return {'type': 'Property', 'value': get_default_number(value, attr)}
    def add_flag(value, attr): return {'type': 'Property', 'value': get_flag(value, attr)}
    def add_date(value, attr): return None if value == '' else {'type': 'Property', 'value': datetime.strptime(value.translate(trans_num_table), attr['format']).isoformat()}

    municipality_code = '全国地方公共団体コード'


def get_translate_func(attr):
    if 'serial' in attr:
        return add_number_serial
    if 'default' in attr:
        if type(attr['default']) is int:
            return add_number_default
        else:
            return add_text_default
    if 'type' in attr:
        t = attr['type']
        if t == "Number":
            return add_number
        elif t == "DateTime":
            return add_date
        else:
            return add_text
    elif attr['name'] in nubmer_items:
        return add_number
    elif attr['name'] in flag_items:
        return add_flag
    elif attr['name'] in date_itimes:
        return add_date
    else:
        return add_text


def get_attribute(item, key, attributes):
    for e in attributes:
        if item in e:
            if e[item] == key:
                return e
    return None


def make_mapping_table_csv(attributes, header):
    table = []
    add_attrs = []

    for k in header:
        e = get_attribute('key', k, attributes)
        if e is None:
            table.append([lambda a, b: None, "", None])
            continue
        f = get_translate_func(e)
        table.append([f, e['name'], e])

    for e in attributes:
        f = get_translate_func(e)
        if 'key' not in e:
            add_attrs.append([f, e['name'], e])

    return table, add_attrs


def make_mapping_table_json(attributes):
    table = {}
    add_attrs = []

    for e in attributes:
        f = get_translate_func(e)
        if 'key' in e:
            table[e['key']] = [f, e['name'], e]
        else:
            add_attrs.append([f, e['name'], e])
    return table, add_attrs


def get_uri(config):
    uri = config['source']['file']
    if isURL(uri):
        if 'apikey' in config['source']:
            apikey = config['source']['apikey']
            apikey = os.getenv(apikey, apikey)
            if apikey != '':
                uri = uri + '?' + urllib.parse.urlencode({'apikey': apikey})
    return uri


def request(url, encoding):
    req = urllib.request.Request(url)
    try:
        res = urllib.request.urlopen(req)

    except urllib.error.HTTPError as err:
        print(err.code)
        print(err.reason)
        return ""
    except urllib.error.URLError as err:
        print(err.reason)
        return ""
    else:
        body = res.read().decode(encoding)
        if res.status != 200:
            print(url)
            print(res.status)
            print(body)
            body = ""
        res.close()
        return body


def conv_json(config):
    uri = get_uri(config)
    encoding = config['source']['encoding']

    if uri == '':
        json_data = json.load(sys.stdin)
    elif isURL(uri):
        res = request(uri, encoding)
        if res == "":
            return False
        json_data = json.loads(res)
    else:
        with open(uri, 'r', encoding=encoding) as f:
            json_data = json.load(f)

    table, add_attrs = make_mapping_table_json(config['mapping']['attributes'])
    entity_type = get_type(config['mapping']['attributes'])

    id = config['mapping']['id'] if 'id' in config['mapping'] else 1
    limit = config['broker']['limit']
    entities = []
    code = ""
    for key in add_attrs:
        if key[1] == municipality_code:
            code = key[2]['default']
    for data in json_data:
        entity = {}
        entity['type'] = entity_type
        for j in data:
            if j in table:
                value = table[j][0](data[j], table[j][2])
                if value is not None:
                    entity[table[j][1]] = value
        if code == "":
            code = entity[municipality_code]['value']
        entity['id'] = 'urn:ngsi-ld:' + entity_type + ':' + code + ':' + str(id) if type(id) is int else entity[id]['value']
        for key in add_attrs:
            value = key[0](None, key[2])
            if value is not None:
                entity[key[1]] = value

        entities.append(entity)
        if len(entities) >= limit:
            if not create_ngsi_entities(config, entities):
                return False
            entities = []
        if type(id) is int:
            id += 1

    if len(entities) > 0:
        return create_ngsi_entities(config, entities)

    return True


def conv_csv(config):
    uri = get_uri(config)
    encoding = config['source']['encoding']

    if uri == '':
        reader = csv.reader(sys.stdin)
        lines = [row for row in reader]
    elif isURL(uri):
        res = request(uri, encoding)
        if res == "":
            return False
        f = io.StringIO(res)
        reader = csv.reader(f)
        lines = [row for row in reader]
    else:
        with open(uri, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

    table, add_attrs = make_mapping_table_csv(config['mapping']['attributes'], lines[0])
    entity_type = get_type(config['mapping']['attributes'])

    id = config['mapping']['id'] if 'id' in config['mapping'] else 1
    limit = config['broker']['limit']
    entities = []
    code = ""
    for key in add_attrs:
        if key[1] == municipality_code:
            code = key[2]['default']
    for line in lines[1:]:
        entity = {}
        entity['type'] = entity_type
        for j in range(len(line)):
            value = table[j][0](line[j], table[j][2])
            if value is not None:
                entity[table[j][1]] = value
        if code == "":
            code = entity[municipality_code]['value']
        entity['id'] = 'urn:ngsi-ld:' + entity_type + ':' + code + ':' + str(id) if type(id) is int else entity[id]['value']
        for key in add_attrs:
            value = key[0](None, key[2])
            if value is not None:
                entity[key[1]] = value
        entities.append(entity)
        if len(entities) >= limit:
            if not create_ngsi_entities(config, entities):
                return False
            entities = []
        if type(id) is int:
            id += 1

    if len(entities) > 0:
        return create_ngsi_entities(config, entities)

    return True


def get_type(attributes):
    for k in entity_types:
        for kk in attributes:
            if 'name' in kk and kk['name'] == k:
                return entity_types[k]
    return None


def get_options():
    global dryrun, debug

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', help='mapping file', type=str)
    parser.add_argument('-f', '--file', help='covid-19 file', type=str)
    parser.add_argument('-j', '--json', help='file type json', action='store_true')
    parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
    parser.add_argument('--dryrun', help='dryrun', action='store_true')
    parser.add_argument('--debug', help='debug', action='store_true')
    args = parser.parse_args()
    dryrun = args.dryrun
    debug = args.debug
    if debug:
        print(args.map)
        print(args.file)
    return args


def isURL(url): return url.startswith('http://') or url.startswith('https://')


def yaml_load(args):
    if args.map is None or not os.path.exists(args.map):
        print('mapping file not found')
        return None

    with open(args.map, 'r') as yml:
        config = yaml.load(yml, Loader=yaml.SafeLoader)

    if 'broker' not in config:
        if os.path.exists('./config.yml'):
            with open('./config.yml', 'r') as yml:
                conv = yaml.load(yml)
                if 'broker' in conv:
                    config['broker'] = {}
                    for k in conv['broker']:
                        config['broker'][k] = conv['broker'][k]

    if 'source' not in config:
        config['source'] = {}
        config['source']['file'] = ''

    if sys.stdin.isatty():
        if args.file is not None:
            config['source']['file'] = args.file

    if args.json:
        config['source']['type'] = 'json'

    if args.sjis:
        config['source']['encoding'] = 'shift_jis'

    return check_config(config)


def check_config(config):
    err = False

    if 'version' in config:
        if not config['version'] == '1':
            print('version is not "1"')
            return None
    else:
        print('version: not found')
        return None

    if 'metadata' in config and not config['metadata'] is None:
        for k in config['metadata']:
            if k not in ('title', 'description', 'source', 'author', 'license', 'remarks'):
                print(k + ': unknown key in metadata:')
                err = True
        if 'source' in config['metadata']:
            source = config['metadata']['source']
            if source != "" and not isURL(source):
                print('source not url in metadata')
                err = True

    if 'source' in config and not config['source'] is None:
        for k in config['source']:
            if k not in ('file', 'encoding', 'type', 'apikey'):
                print(k + ': unknown key in source:')
                err = True
        if 'file' not in config['source']:
            print('file not found in mapping.yml or -f option')
            err = True
            return None
        if 'encoding' not in config['source']:
            config['source']['encoding'] = 'utf_8_sig'
        if 'type' not in config['source']:
            file = config['source']['file']
            if file == '':
                config['source']['type'] = 'csv'
            else:
                ext = str.lower(os.path.splitext(file)[1])[1:]
                if ext in ('json', 'csv'):
                    config['source']['type'] = ext
                else:
                    config['source']['type'] = 'csv'

    if 'broker' in config and not config['broker'] is None:
        for k in config['broker']:
            if k not in ('url', 'type', 'service', 'path', 'context', 'token', 'limit'):
                print(k + ': unknown key in broker:')
                err = True
            if k == 'url':
                if not isURL(config['broker']['url']):
                    print('url: not URL in broker')
                    err = True
            elif k == 'type':
                config['broker']['type'] = str.lower(config['broker']['type'])
                if not config['broker']['type'] in ('v2', 'ld'):
                    print('broker type: v2 or ld')
                    err = True
                if config['broker']['type'] == 'ld':
                    if 'context' not in config['broker']:
                        print('cotext not found in broker')
                        err = True
                    else:
                        if not isURL(config['broker']['context']):
                            print('cotext not url in broker')
                            err = True
            elif k == 'path':
                if not config['broker'][k].startswith('/'):
                    print('path should start with /')
                    err = True

            elif k == 'token':
                if type(config['broker'][k]) is str:
                    token = config['broker'][k]
                    token = os.getenv(token, token)
                    if token == '':
                        print('token is empty')
                        err = True
                else:
                    print('token should be string')
                    err = True
            elif k == 'limit':
                limit = config['broker'][k]
                if type(limit) is int:
                    if limit > 3000 or limit < 1:
                        print('limit out of range (1 <= limit <= 3000')
                        err = True
                else:
                    print('limit not int')
                    err = True

        if 'type' not in config['broker']:
            config['broker']['type'] = 'v2'
        if 'limit' not in config['broker']:
            config['broker']['limit'] = 1000
    else:
        print('broker: not found')
        return None

    if config['broker']['type'] == 'v2':
        init_v2()
    else:
        init_ld()

    if 'mapping' in config and not config['mapping'] is None:
        for k in config['mapping']:
            if k not in ('attributes', 'id'):
                print(k + ': unknown key in mapping')
                err = True
        if 'attributes' in config['mapping']:
            entity_type = get_type(config['mapping']['attributes'])
            if entity_type is None:
                print('unknown covid-19 data modle')
                return None
            for k in required_items[entity_type]:
                found = False
                for attrs in config['mapping']['attributes']:
                    if 'name' in attrs and attrs['name'] == k:
                        found = True
                        break
                if not found:
                    print('missing "' + k + '" in attributes (' + entity_type + ')')
                    err = True

            for attrs in config['mapping']['attributes']:
                for k in attrs:
                    if k not in ('name', 'key', 'type', 'format', 'default', 'serial'):
                        print(k + ': unknown key in attributes')
                        err = True
                if 'name' not in attrs:
                    print('name key not found in attributes')
                    err = True
                if 'key' not in attrs:
                    if 'serial' not in attrs and 'default' not in attrs and 'type' not in attrs:
                        print('serial or default needed when no key in mapping')
                        err = True
                if 'serial' in attrs and 'default' in attrs:
                    print('either serial or default in mapping')
                    err = True
                if 'serial' in attrs and not type(attrs['serial']) is int:
                    print('serial value is not integer in mapping')
                    err = True
                if 'format' in attrs and not type(attrs['format']) is str:
                    print('format value is not string in mapping')
                    err = True
                if 'type' in attrs:
                    if attrs['type'] in ('Number', 'Text', 'DateTime'):
                        t = attrs['type']
                        if t == 'Number':
                            if 'default' in attrs and not type(attrs['default']) is int:
                                print('default type error in ' + attrs['name'] + ' in attributes')
                                err = True
                        elif t == 'Text':
                            if 'default' in attrs and not type(attrs['default']) is str:
                                print('default type error in ' + attrs['name'] + ' in attributes')
                                err = True
                            if 'serial' in attrs:
                                print('cannot specify serial in ' + attrs['name'] + ' in attributes')
                                err = True
                        elif t == 'DateTime':
                            if 'default' in attrs:
                                print('cannot specify default in' + attrs['name'] + ' in attributes')
                                err = True
                            if 'serial' in attrs:
                                print('cannot specify serial in ' + attrs['name'] + ' in attributes')
                                err = True
                            if 'format' not in attrs:
                                print('format not found in ' + attrs['name'] + ' in attributes')
                                err = True
                    else:
                        print(attrs['type'] + ': unknown type in attributes')
                        err = True
            if 'id' in config['mapping']:
                id = config['mapping']['id']
                if not type(id) is str and not type(id) is int:
                    print('id type error in mapping')
                    err = True
                if type(id) is str:
                    found = False
                    for attrs in config['mapping']['attributes']:
                        if 'name' in attrs:
                            if attrs['name'] == id:
                                found = True
                                break
                    if not found:
                        print(id + ' not found in attribute')
                        err = True
        else:
            print('attributes: not found')
            err = True
    else:
        print('mapping: not found')
        err = True
    if err:
        return None
    else:
        return config


def main():
    config = yaml_load(get_options())
    if config is None:
        sys.exit(1)

    if config['source']['type'] == 'json':
        r = conv_json(config)
    else:
        r = conv_csv(config)

    if not r:
        sys.exit(1)


if __name__ == '__main__':
    main()
