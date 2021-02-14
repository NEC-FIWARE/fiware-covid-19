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
import math
import functools
import libs.date_util as date_util
import libs.entity_types as entity_types
from libs.builder.entity_builder import EntityBuilder


class ConfirmNegativeDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'ConfirmNegativeDaily'
    ENTITY_TYPE = 'Covid19ConfirmNegativeDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            entity_types.COVID19_CONFIRM_NEGATIVE, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['confirmedNegativeAt'])

        # daily
        for entity in entities:
            dt = date_util.iso_to_datetime(entity['confirmedNegativeAt'])
            aggregated['data']['value'].append({
                '日付': dt.isoformat(),
                '曜日': date_util.weekday_name(dt),
                'date': dt.strftime('%Y-%m-%d'),
                'w': dt.isocalendar()[1],
                '小計': int(entity['numberOfNegatives']),
                'weekly_average_count': 0,
            })

        # weekly average
        data_value_rev = list(reversed(aggregated['data']['value']))
        for i, entity in enumerate(data_value_rev):
            lst = data_value_rev[i:i+7]
            sub = functools.reduce(
                lambda acc, val: acc + val['小計'], lst, 0)
            ave = math.floor((sub / len(lst)) * 10) / 10
            entity['weekly_average_count'] = ave

        return aggregated
