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
from datetime import datetime
import math
import functools
import libs.date_util as date_util
from libs.builder.entity_builder import EntityBuilder
from libs.builder.patients_daily_aggregated_builder import PatientsDailyAggregatedBuilder
from libs.builder.test_people_daily_aggregated_builder import TestPeopleDailyAggregatedBuilder
from libs.builder.test_count_daily_aggregated_builder import TestCountDailyAggregatedBuilder
from libs.builder.callcenter_daily_aggregated_builder import CallCenterDailyAggregatedBuilder
from libs.builder.confirm_negative_daily_aggregated_builder import ConfirmNegativeDailyAggregatedBuilder


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

        call_center_entity = self.broker.get_entity(
            self.create_type(CallCenterDailyAggregatedBuilder),
            self.create_id(CallCenterDailyAggregatedBuilder, municipality_code))

        # last count
        if len(patients_entity['data']):
            patients_ave = patients_entity['data'][-1]['weekly_average_count']
        else:
            patients_ave = 0

        if len(test_people_count_entity['data']):
            test_people_count_ave = test_people_count_entity['data'][-1]['weekly_average_count']
        else:
            test_people_count_ave = 0

        if len(test_count_entity['data']):
            test_count_ave = test_count_entity['data'][-1]['weekly_average_count']
        else:
            test_count_ave = 0

        if len(confirm_negative_entity['data']):
            confirm_negative_ave = confirm_negative_entity['data'][-1]['weekly_average_count']
        else:
            confirm_negative_ave = 0

        if len(call_center_entity['data']):
            call_center_ave = call_center_entity['data'][-1]['weekly_average_count']
        else:
            call_center_ave = 0

        # print(patients_ave, test_people_count_ave, test_count_ave,
        #      confirm_negative_ave, call_center_ave)

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
                    'date': date_util.iso_to_datetime(patients_entity['date']).strftime('%Y/%m/%d %H:%M:%S'),
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
