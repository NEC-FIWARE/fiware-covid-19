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
# import json
import math
import functools
from datetime import datetime
import libs.date_util as date_util
import libs.entity_types as entity_types
from libs.builder.entity_builder import EntityBuilder
from libs.builder.test_people_daily_aggregated_builder import TestPeopleDailyAggregatedBuilder
from libs.builder.test_count_daily_aggregated_builder import TestCountDailyAggregatedBuilder
from libs.builder.callcenter_daily_aggregated_builder import CallCenterDailyAggregatedBuilder
from libs.builder.confirm_negative_daily_aggregated_builder import ConfirmNegativeDailyAggregatedBuilder


class PatientsDailyAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'PatientsDaily'
    ENTITY_TYPE = 'Covid19PatientsDailyAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            entity_types.COVID19_PATIENTS, municipality_code)

        if not len(raw_entities):
            return aggregated

        entities = sorted(raw_entities, key=lambda x: (x['patientNo']))

        entities_max = max(map(lambda x: x['publishedAt'], entities))

        dates = [date_util.iso_to_datetime(entities_max).strftime('%Y-%m-%d')]

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
        for dt in date_util.date_range(datetime(2020, 1, 1), max_date):
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
            d = date_util.iso_to_datetime(
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
            days = data_keys_rev[i:i+7]
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
