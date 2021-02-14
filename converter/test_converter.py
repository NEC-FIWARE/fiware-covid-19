#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import yaml
import sys
import json
import argparse
from io import StringIO
from urllib.error import HTTPError, URLError
from unittest.mock import patch, MagicMock
import converter


class TestConv(unittest.TestCase):

    def test_create_ngsi_entities_dryrun(self):
        converter.dryrun = True
        converter.debug = True

        cases = [
            [
                {'broker': {'type': 'v2', 'url': 'http://orion:1026', 'service': 'covid19', 'path': '/', 'token': 'test'}},
                '{\n  "actionType": "append",\n  "entities": []\n}\n'
            ],
            [
                {'broker': {'type': 'ld', 'url': 'http://orion-ld:1026', 'service': 'covid19', 'context': 'http://context', 'token': 'test'}},
                '[]\n'
            ]
        ]

        for case in cases:
            with patch('sys.stdout', new=StringIO()) as stdout:
                actual = converter.create_ngsi_entities(case[0], [])

            self.assertEqual(True, actual)
            self.assertEqual(stdout.getvalue(), case[1])

    def test_create_ngsi_entities(self):
        converter.dryrun = False
        cases = [
            [
                {'broker': {'type': 'v2', 'url': 'http://orion:1026', 'service': 'covid19', 'path': '/', 'token': 'test'}},
                '',
                True
            ],
            [
                {'broker': {'type': 'ld', 'url': 'http://orion-ld:1026', 'service': 'covid19', 'context': 'http://context', 'token': 'test'}},
                '404\nerror\n',
                False
            ]
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            host = args[0].host

            if host == 'orion:1026':
                status = 200
            elif host == 'orion-ld:1026':
                status = 404

            class Mock_response():
                def __init__(self):
                    self.status = status

                def read(self):
                    return 'error'.encode()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                with patch('sys.stdout', new=StringIO()) as stdout:
                    actual = converter.create_ngsi_entities(case[0], [])
                self.assertEqual(case[2], actual)
                self.assertEqual(stdout.getvalue(), case[1])

    def test_create_ngsi_entities_exception(self):
        converter.dryrun = False
        converter.debug = False
        cases = [
            [
                {'broker': {'type': 'v2', 'url': 'http://orion:1026', 'service': 'covid19', 'path': '/', 'token': 'test'}},
                HTTPError('http://orion:1026', 500, 'Internal Error', {}, None),
                '500\nInternal Error\n'
            ],
            [
                {'broker': {'type': 'ld', 'url': 'http://orion-ld:1026', 'service': 'covid19', 'context': 'http://context', 'token': 'test'}},
                URLError('Unknown host'),
                'Unknown host\n'
            ]
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            host = args[0].host

            if host == 'orion:1026':
                status = 200
            elif host == 'orion-ld:1026':
                status = 404

            class Mock_response():
                def __init__(self):
                    self.status = status

                def read(self):
                    return 'error'.encode()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = case[1]
                with patch('sys.stdout', new=StringIO()) as stdout:
                    actual = converter.create_ngsi_entities(case[0], [])
                self.assertEqual(False, actual)
                self.assertEqual(stdout.getvalue(), case[2])

    def test_conv_forbidden_chars(self):

        cases = [
            ['!"#$%&\'()-=~[]{}+*?/_<>', '!”#$%&’（）-＝~[]{}+*?/_＜＞'],
            ['0123456789', '0123456789'],
            ['abcdefghijklmnopqrstuvwxyz', 'abcdefghijklmnopqrstuvwxyz'],
            ['ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        ]

        for case in cases:
            actual = converter.conv_forbidden_chars(case[0])
            self.assertEqual(case[1], actual)

    def test_get_flag(self):
        cases = [
            ['0', 0],
            ['1', 1],
            ['2', -1],
            ['', -1],
            ['123', -1],
            [0, -1],
            [1, -1],
            [2, -1]
        ]

        for case in cases:
            actual = converter.get_flag(case[0], None)
            self.assertEqual(case[1], actual)

    def test_check_config_encoding_default(self):
        file = '007_config_default.yml'

        with open('testdata/' + file, 'r') as yml:
            config = yaml.load(yml)
        config = converter.check_config(config)

        self.assertEqual('utf_8_sig', config['source']['encoding'])

    def test_check_config_type_default(self):
        file = '008_config_csv.yml'

        with open('testdata/' + file, 'r') as yml:
            config = yaml.load(yml)
        config = converter.check_config(config)

        self.assertEqual('csv', config['source']['type'])

    def test_check_config_type_csv(self):
        file = '009_config_json.yml'

        with open('testdata/' + file, 'r') as yml:
            config = yaml.load(yml)
        config = converter.check_config(config)

        self.assertEqual('json', config['source']['type'])

    def test_check_config_type_unknown(self):
        file = '010_config_type_unknown.yml'

        with open('testdata/' + file, 'r') as yml:
            config = yaml.load(yml)
        config = converter.check_config(config)

        self.assertEqual('csv', config['source']['type'])

    def test_check_config_type_json(self):
        file = '007_config_default.yml'

        with open('testdata/' + file, 'r') as yml:
            config = yaml.load(yml)
        config = converter.check_config(config)

        self.assertEqual('csv', config['source']['type'])

    def test_check_config_ok(self):
        cases = [
            'ld_1_covid19patients.yml',
            'ld_2_covid19test_people.yml',
            'ld_3_covid19test_count.yml',
            'ld_4_covid19confirm_negative.yml',
            'ld_5_covid19call_center.yml',
            'v2_1_covid19patients.yml',
            'v2_2_covid19test_people.yml',
            'v2_3_covid19test_count.yml',
            'v2_4_covid19confirm_negative.yml',
            'v2_5_covid19call_center.yml',
            'id.yml'
        ]
        for case in cases:
            with open('testdata/' + case, 'r') as yml:
                config = yaml.load(yml)
            actual = converter.check_config(config)

            self.assertNotEqual(None, actual)

    def test_check_config_error(self):
        config = []
        cases = [
            ['001_yml_version_not_found.yml', None, 'version: not found\n'],
            ['002_yml_version_err.yml', None, 'version is not "1"\n'],
            ['003_unknown_key_in_metatada.yml', None, 'download: unknown key in metadata:\nbroker: not found\n'],
            ['004_source_not_url_in_metadata.yml', None, 'source not url in metadata\nbroker: not found\n'],
            ['005_unknown_key_in_source.yml', None, 'donwload: unknown key in source:\nfile not found in mapping.yml or -f option\n'],
            ['006_file_not_found_in_mapping.yml', None, 'file not found in mapping.yml or -f option\n'],
            ['011_broker_unknwon_key.yml', None, 'source: unknown key in broker:\nmapping: not found\n'],
            ['012_broker_not_url.yml', None, 'url: not URL in broker\nmapping: not found\n'],
            ['013_broker_type_error.yml', None, 'broker type: v2 or ld\nmapping: not found\n'],
            ['014_broker_context_not_found.yml', None, 'cotext not found in broker\nmapping: not found\n'],
            ['015_broker_context_not_url.yml', None, 'cotext not url in broker\nmapping: not found\n'],
            ['016_broker_path_error.yml', None, 'path should start with /\nmapping: not found\n'],
            ['017_token_is_empty.yml', None, 'token is empty\nmapping: not found\n'],
            ['018_broker_token_should_be_string.yml', None, 'token should be string\nmapping: not found\n'],
            ['019_broker_limit_out_of_range.yml', None, 'limit out of range (1 <= limit <= 3000\nmapping: not found\n'],
            ['020_broker_limit_0.yml', None, 'limit out of range (1 <= limit <= 3000\nmapping: not found\n'],
            ['021_broker_limit_not_int.yml', None, 'limit not int\nmapping: not found\n'],
            ['030_mapping_unknown_key.yml', None, 'entity: unknown key in mapping\nattributes: not found\n'],
            ['031_mapping_unknown_data_model.yml', None, 'unknown covid-19 data modle\n'],
            ['032_mapping_missing_attribute.yml', None, 'missing "municipalityCode" in attributes (Covid19TestPeople)\n'],
            ['033_mapping_unknown_key_in_attr.yml', None, 'value: unknown key in attributes\n'],
            ['034_name_key_not_found.yml', None, 'name key not found in attributes\n'],
            ['035_mapping_serial_or_default_needed.yml', None, 'serial or default needed when no key in mapping\n'],
            ['036_mapping_either_serial_or_default.yml', None, 'either serial or default in mapping\n'],
            ['037_mapping_serial_is_not_int.yml', None, 'serial value is not integer in mapping\n'],
            ['038_mapping_format_not_str.yml', None, 'format value is not string in mapping\n'],
            ['039_mapping_default_type_error.yml', None, 'default type error in test in attributes\n'],
            ['040_mapping_default_type_error.yml', None, 'default type error in test in attributes\n'],
            ['041_mapping_cannot_specify_serial.yml', None, 'cannot specify serial in test in attributes\n'],
            ['042_mapping_cannot_specify_default.yml', None, 'cannot specify default intest in attributes\nformat not found in test in attributes\n'],
            ['043_mapping_cannot_specify_serial.yml', None, 'cannot specify serial in test in attributes\nformat not found in test in attributes\n'],
            ['044_mapping_format_not_found.yml', None, 'format not found in test in attributes\n'],
            ['045_mapping_uunknown_type.yml', None, 'Integer: unknown type in attributes\n'],
            ['046_mapping_id_type_error.yml', None, 'id type error in mapping\n'],
            ['047_mapping_id_not_found.yml', None, 'No not found in attribute\n'],
            ['048_attributes_not_found.yml', None, 'attributes: not found\n'],
            ['049_mapping_not_found.yml', None, 'mapping: not found\n']
        ]

        for case in cases:
            with open('testdata/' + case[0], 'r') as yml:
                config = yaml.load(yml)

            with patch('sys.stdout', new=StringIO()) as stdout:
                actual = converter.check_config(config)

            self.assertEqual(case[1], actual)
            self.assertEqual(stdout.getvalue(), case[2])

    def test_get_default_number(self):
        attr = {}
        attr['serial'] = 1

        actual = converter.get_default_number(0, attr)

        self.assertEqual(1, actual)
        self.assertEqual(2, attr['serial'])

    def test_get_translate_func_v2(self):
        converter.init_v2()

        cases = [
            ['serial', 1, converter.add_number_serial],
            ['default', 2, converter.add_number_default],
            ['default', 'abc', converter.add_text_default],
            ['type', 'Number', converter.add_number],
            ['type', 'DateTime', converter.add_date],
            ['type', 'Text', converter.add_text],
            ['name', 'numberOfTestedPeopl', converter.add_number],
            ['name', 'numberOfTests', converter.add_number],
            ['name', 'numberOfNegatives', converter.add_number],
            ['name', 'numberOfCalls', converter.add_number],
            ['name', 'patientTravelHistory', converter.add_flag],
            ['name', 'patientDischarged', converter.add_flag],
            ['name', 'publishedAt', converter.add_date],
            ['name', 'symptomOnsetAt', converter.add_date],
            ['name', 'testedAt', converter.add_date],
            ['name', 'confirmedNegativeAt', converter.add_date],
            ['name', 'acceptedAt', converter.add_date],
            ['name', 'remarks', converter.add_text]
        ]
        for case in cases:
            attr = {}
            attr[case[0]] = case[1]
            actual = converter.get_translate_func(attr)

            self.assertEqual(case[2], actual)

    def test_get_translate_func_ld(self):
        converter.init_ld()

        cases = [
            ['serial', 1, converter.add_number_serial],
            ['default', 2, converter.add_number_default],
            ['default', 'abc', converter.add_text_default],
            ['type', 'Number', converter.add_number],
            ['type', 'DateTime', converter.add_date],
            ['type', 'Text', converter.add_text],
            ['name', '検査実施_人数', converter.add_number],
            ['name', '検査実施_件数', converter.add_number],
            ['name', '陰性確認_件数', converter.add_number],
            ['name', '相談件数', converter.add_number],
            ['name', '患者_渡航歴の有無フラグ', converter.add_flag],
            ['name', '患者_退院済フラグ', converter.add_flag],
            ['name', '公表_年月日', converter.add_date],
            ['name', '発症_年月日', converter.add_date],
            ['name', '実施_年月日', converter.add_date],
            ['name', '完了_年月日', converter.add_date],
            ['name', '受付_年月日', converter.add_date],
        ]
        for case in cases:
            attr = {}
            attr[case[0]] = case[1]
            actual = converter.get_translate_func(attr)

            self.assertEqual(case[2], actual)

    def test_get_attribute(self):
        attrs = [{'key': '備考', 'name': 'remarks', 'type': 'Text'}]

        cases = [
            ['key', 'remarks', None],
            ['key', '備考', attrs[0]]
        ]

        for case in cases:
            actual = converter.get_attribute(case[0], case[1], attrs)
            self.assertEqual(case[2], actual)

    def test_make_mapping_table_csv(self):
        cases = [
            [[{'key': '備考', 'name': 'remarks', 'type': 'Text'}], ['備考'], 1, 0],
            [[{'name': 'remarks', 'type': 'Text', 'default': "memo"}], ['test'], 1, 1],
            [[], ['test'], 1, 0],
            [[], [], 0, 0]
        ]

        for case in cases:
            table, add_attrs = converter.make_mapping_table_csv(case[0], case[1])

            self.assertEqual(case[2], len(table))
            self.assertEqual(case[3], len(add_attrs))

    def test_make_mapping_table_json(self):
        cases = [
            [[{'key': '備考', 'name': 'remarks', 'type': 'Text'}], 1, 0],
            [[{'name': 'remarks', 'type': 'Text', 'default': "memo"}], 0, 1]
        ]

        for case in cases:
            table, add_attrs = converter.make_mapping_table_json(case[0])

            self.assertEqual(case[1], len(table))
            self.assertEqual(case[2], len(add_attrs))

    def test_get_uri(self):
        cases = [
            ['file', '', 'file'],
            ['file', 'key', 'file'],
            ['http://open-data', '', 'http://open-data'],
            ['https://open-data', '', 'https://open-data'],
            ['http://open-data', 'key', 'http://open-data?apikey=key'],
            ['https://open-data', 'key', 'https://open-data?apikey=key'],
        ]

        for case in cases:
            config = {'source': {}}
            config['source']['file'] = case[0]
            if case[1] != '':
                config['source']['apikey'] = case[1]
            actual = converter.get_uri(config)

            self.assertEqual(case[2], actual)

    def test_request(self):
        cases = [
            [
                'http://orion:1026',
                'fiware',
                ''
            ],
            [
                'http://orion-ld:1026',
                '',
                '404\nfiware\n'
            ]
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            host = args[0].host

            if host == 'orion:1026':
                status = 200
            elif host == 'orion-ld:1026':
                status = 404

            class Mock_response():
                def __init__(self):
                    self.status = status

                def read(self):
                    return 'fiware'.encode()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                with patch('sys.stdout', new=StringIO()) as stdout:
                    actual = converter.request(case[0], 'utf_8_sig')
                self.assertEqual(case[1], actual)
                self.assertEqual(stdout.getvalue(), case[2])

    def test_request_exception(self):
        cases = [
            [
                'http://orion:1026',
                HTTPError('http://orion:1026', 500, 'Internal Error', {}, None),
                '500\nInternal Error\n'
            ],
            [
                'http://orion-ld:1026',
                URLError('Unknown host'),
                'Unknown host\n'
            ]
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            host = args[0].host

            if host == 'orion:1026':
                status = 200
            elif host == 'orion-ld:1026':
                status = 404

            class Mock_response():
                def __init__(self):
                    self.status = status

                def read(self):
                    return 'error'.encode()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = case[1]
                with patch('sys.stdout', new=StringIO()) as stdout:
                    actual = converter.request(case[0], 'utf_8_sig')
                self.assertEqual('', actual)
                self.assertEqual(stdout.getvalue(), case[2])

    def test_conv_json(self):
        converter.dryrun = True
        cases = [
            ['100_test_data.yml', '100_test_data.json', 1, True],
            ['100_test_data.yml', '100_test_data.json', 2, True],
            ['100_test_data.yml', '100_test_data.json', 3, True],
            ['101_test_data.yml', '101_test_data.json', 1, True],
        ]

        for case in cases:
            parser = argparse.ArgumentParser()
            parser.add_argument('-m', '--map', help='mapping file', type=str)
            parser.add_argument('-f', '--file', help='covid-19 file', type=str)
            parser.add_argument('-j', '--json', help='file type json', action='store_true')
            parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
            parser.add_argument('--dryrun', help='dryrun', action='store_true')
            parser.add_argument('--debug', help='debug', action='store_true')
            args = parser.parse_args(['-m', 'testdata/' + case[0], '-f', 'testdata/' + case[1], '-j'])
            config = converter.yaml_load(args)
            config['broker']['limit'] = case[2]

            actual = converter.conv_json(config)

            self.assertEqual(case[3], actual)

    def test_conv_json_http(self):
        converter.dryrun = True
        cases = [
            ['100_test_data.yml', '100_test_data.json', 1, True],
            ['100_test_data.yml', '100_test_data.json', 2, True],
            ['100_test_data.yml', '105_test_data.json', 1, False],
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            file = args[0].full_url[7:]

            class Mock_response():
                def __init__(self):
                    self.status = status
                    self.file = file

                def read(self):
                    with open(self.file, 'r', encoding='utf_8_sig') as f:
                        return f.read().encode()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            parser = argparse.ArgumentParser()
            parser.add_argument('-m', '--map', help='mapping file', type=str)
            parser.add_argument('-f', '--file', help='covid-19 file', type=str)
            parser.add_argument('-j', '--json', help='file type json', action='store_true')
            parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
            parser.add_argument('--dryrun', help='dryrun', action='store_true')
            parser.add_argument('--debug', help='debug', action='store_true')
            args = parser.parse_args(['-m', 'testdata/' + case[0], '-f', 'http://testdata/' + case[1], '-j'])
            config = converter.yaml_load(args)
            config['broker']['limit'] = case[2]

            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                actual = converter.conv_json(config)

                self.assertEqual(case[3], actual)

    def test_conv_json_stdin(self):
        converter.dryrun = True

        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args(['-m', 'testdata/100_test_data.yml', '-j'])
        config = converter.yaml_load(args)

        def mock_json_load(*args, **kwargs):
            return []

        with patch('json.load') as m_json_load:
            m_json_load.side_effect = mock_json_load
            actual = converter.conv_json(config)

        self.assertEqual(True, actual)

    def test_conv_json_error(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args(['-m', 'testdata/100_test_data.yml', '-f', 'testdata/100_test_data.json', '-j'])
        config = converter.yaml_load(args)
        config['broker']['limit'] = 1
        converter.dryrun = False

        def mock_urlopen(*args, **kwargs):
            class Mock_response():
                def __init__(self):
                    self.status = 404

                def read(self):
                    return 'error'.encode()

                def close(self):
                    pass
            return Mock_response()

        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                actual = converter.conv_json(config)

        self.assertEqual(False, actual)
        self.assertEqual(stdout.getvalue(), '404\nerror\n')

    def test_conv_csv(self):
        converter.dryrun = True
        cases = [
            ['102_test_data.yml', '102_test_data.csv', 1, True],
            ['102_test_data.yml', '102_test_data.csv', 2, True],
            ['102_test_data.yml', '102_test_data.csv', 3, True],
            ['103_test_data.yml', '103_test_data.csv', 1, True],
            ['103_test_data.yml', '103_test_data.csv', 2, True],
        ]

        for case in cases:
            parser = argparse.ArgumentParser()
            parser.add_argument('-m', '--map', help='mapping file', type=str)
            parser.add_argument('-f', '--file', help='covid-19 file', type=str)
            parser.add_argument('-j', '--json', help='file type json', action='store_true')
            parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
            parser.add_argument('--dryrun', help='dryrun', action='store_true')
            parser.add_argument('--debug', help='debug', action='store_true')
            args = parser.parse_args(['-m', 'testdata/' + case[0], '-f', 'testdata/' + case[1], '-s'])
            config = converter.yaml_load(args)
            config['broker']['limit'] = case[2]

            actual = converter.conv_csv(config)

            self.assertEqual(case[3], actual)

    def test_conv_csv_http(self):
        converter.dryrun = True
        cases = [
            ['102_test_data.yml', '102_test_data.csv', 1, True],
            ['102_test_data.yml', '102_test_data.csv', 2, True],
            ['102_test_data.yml', '102_test_data.csv', 3, True],
            ['103_test_data.yml', '103_test_data.csv', 1, True],
            ['103_test_data.yml', '103_test_data.csv', 2, True],
            ['103_test_data.yml', '106_test_data.csv', 1, False],
        ]

        def mock_urlopen(*args, **kwargs):
            status = 200
            file = args[0].full_url[7:]

            class Mock_response():
                def __init__(self):
                    self.status = status
                    self.file = file

                def read(self):
                    with open(self.file, 'rb') as f:
                        return f.read()

                def close(self):
                    pass
            return Mock_response()

        for case in cases:
            parser = argparse.ArgumentParser()
            parser.add_argument('-m', '--map', help='mapping file', type=str)
            parser.add_argument('-f', '--file', help='covid-19 file', type=str)
            parser.add_argument('-j', '--json', help='file type json', action='store_true')
            parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
            parser.add_argument('--dryrun', help='dryrun', action='store_true')
            parser.add_argument('--debug', help='debug', action='store_true')
            args = parser.parse_args(['-m', 'testdata/' + case[0], '-f', 'http://testdata/' + case[1], '-s'])
            config = converter.yaml_load(args)
            config['broker']['limit'] = case[2]

            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                actual = converter.conv_csv(config)

                self.assertEqual(case[3], actual)

    def test_conv_csv_stdin(self):
        converter.dry = True

        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args(['-m', 'testdata/102_test_data.yml'])
        config = converter.yaml_load(args)

        def mock_csv_reader(*args, **kwargs):
            return 'No, リリース日, 曜日, 居住地, 年代, 性別, 属性, 備考, 補足, 退院\n,,,,,,,,,\n,,,,,,,,,\n'

        with patch('csv.reader') as m_csv_reader:
            m_csv_reader.side_effect = mock_csv_reader
            actual = converter.conv_csv(config)

        self.assertEqual(True, actual)

    def test_conv_csv_error(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args(['-m', 'testdata/102_test_data.yml', '-f', 'testdata/102_test_data.csv', '--sjis'])
        config = converter.yaml_load(args)
        config['broker']['limit'] = 1
        converter.dryrun = False

        def mock_urlopen(*args, **kwargs):
            class Mock_response():
                def __init__(self):
                    self.status = 404

                def read(self):
                    return 'error'.encode()

                def close(self):
                    pass
            return Mock_response()

        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                actual = converter.conv_csv(config)

        self.assertEqual(False, actual)
        self.assertEqual(stdout.getvalue(), '404\nerror\n')

    def test_yaml_load_no_mapping(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args([])

        with patch('sys.stdout', new=StringIO()) as stdout:
            config = converter.yaml_load(args)

        self.assertEqual(None, config)
        self.assertEqual(stdout.getvalue(), 'mapping file not found\n')

    def test_yaml_load_no_broker(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--map', help='mapping file', type=str)
        parser.add_argument('-f', '--file', help='covid-19 file', type=str)
        parser.add_argument('-j', '--json', help='file type json', action='store_true')
        parser.add_argument('-s', '--sjis', help='shift_jis encording', action='store_true')
        parser.add_argument('--dryrun', help='dryrun', action='store_true')
        parser.add_argument('--debug', help='debug', action='store_true')
        args = parser.parse_args(['-m', 'testdata/104_test_data.yml', '-f', 'testdata/104_test_data.json', '-j'])

        config = converter.yaml_load(args)

        self.assertNotEqual(None, config)

    def test_get_options(self):
        testargs = ['converter.py', '-m', 'data.yml', '-f', 'data.json']
        with patch.object(sys, 'argv', testargs):
            args = converter.get_options()

            self.assertEqual(False, args.debug)
            self.assertEqual(False, args.dryrun)

    def test_get_options_debug(self):
        testargs = ['converter.py', '-m', 'data.yml', '-f', 'data.json', '--debug']
        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch.object(sys, 'argv', testargs):
                args = converter.get_options()

        self.assertEqual(True, args.debug)
        self.assertEqual(False, args.dryrun)
        self.assertEqual(stdout.getvalue(), 'data.yml\ndata.json\n')

    def test_main(self):
        testargs = ['converter.py']
        with patch.object(sys, 'argv', testargs):
            with patch('sys.stdout', new=StringIO()) as stdout:
                with self.assertRaises(SystemExit) as cm:
                    converter.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(stdout.getvalue(), 'mapping file not found\n')

    def test_main_json(self):
        testargs = ['converter.py', '-m', 'testdata/100_test_data.yml', '-f', 'testdata/100_test_data.json', '--dryrun']
        with patch.object(sys, 'argv', testargs):
            converter.main()

    def test_main_csv(self):
        testargs = ['converter.py', '-m', 'testdata/102_test_data.yml', '-f', 'testdata/102_test_data.csv', '--sjis', '--dryrun']
        with patch.object(sys, 'argv', testargs):
            converter.main()

    def test_main_error(self):
        def mock_urlopen(*args, **kwargs):
            status = 200
            file = args[0].full_url[7:]

            class Mock_response():
                def __init__(self):
                    self.status = status
                    self.file = file

                def read(self):
                    with open(self.file, 'r', encoding='utf_8_sig') as f:
                        return f.read().encode()

                def close(self):
                    pass
            return Mock_response()

        testargs = ['converter', '-m', 'testdata/100_test_data.yml', '-f', 'http://testdata/105_test_data.json', '--dryrun']
        with patch.object(sys, 'argv', testargs):
            with patch('urllib.request.urlopen') as m_urlopen:
                m_urlopen.side_effect = mock_urlopen
                with self.assertRaises(SystemExit) as cm:
                    converter.main()
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
