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
import os
import json
import yaml


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


def load_config(file):
    global BROKER_VERSION
    global BROKER_URL
    global BROKER_SERVICE
    global BROKER_PATH
    global BROKER_TOKEN
    global BROKER_CONTEXT
    global CODE
    global AGGREGATE
    global CONFIG_TYPE

    if not file:
        config_path = './config.json'
    else:
        config_path = file

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            ext = os.path.splitext(config_path)[1]

            if ext == '.yml':
                CONFIG_TYPE = 'yml'
                config = yaml.load(f, Loader=yaml.SafeLoader)

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
                    BROKER_CONTEXT = config['broker']['context']

                CODE = config['code']
                AGGREGATE = config['aggregate']

            elif ext == '.json':
                CONFIG_TYPE = 'json'
                config = json.load(f)

                if 'BROKER_VERSION' in config and len(config['BROKER_VERSION']):
                    BROKER_VERSION = config['BROKER_VERSION']

                if 'BROKER_URL' in config and len(config['BROKER_URL']):
                    BROKER_URL = config['BROKER_URL']

                if 'BROKER_SERVICE' in config and len(config['BROKER_SERVICE']):
                    BROKER_SERVICE = config['BROKER_SERVICE']

                if 'BROKER_PATH' in config and len(config['BROKER_PATH']):
                    BROKER_PATH = config['BROKER_PATH']

                if 'BROKER_TOKEN' in config and len(config['BROKER_TOKEN']):
                    BROKER_TOKEN = config['BROKER_TOKEN']

                if 'BROKER_CONTEXT' in config and len(config['BROKER_CONTEXT']):
                    BROKER_CONTEXT = config['BROKER_CONTEXT']
