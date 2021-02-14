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
import datetime
from libs.broker import Broker


class EntityBuilder():

    AGGREGATE_TYPE: str = None
    ENTITY_TYPE: str = None

    def __init__(self, broker: Broker):
        """
        """
        self.broker: Broker = broker

    def build_entity(self, municipality_code: str) -> list:
        """
        """
        pass

    def build_entity_mockup(self, municipality_code: str):
        """
        """
        iso_datetime = datetime.datetime.now().isoformat()
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
