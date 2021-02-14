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
import libs.date_util as date_util
import libs.entity_types as entity_types
from libs.builder.entity_builder import EntityBuilder


class PatientsListAggregatedBuilder(EntityBuilder):

    AGGREGATE_TYPE = 'PatientsList'
    ENTITY_TYPE = 'Covid19PatientsListAggregated'

    def build_entity(self, municipality_code):
        """
        """
        aggregated = self.build_entity_mockup(municipality_code)

        raw_entities = self.broker.get_entities(
            entity_types.COVID19_PATIENTS, municipality_code)

        entities = sorted(raw_entities, key=lambda x: x['patientNo'])

        for entity in reversed(entities):
            dt = date_util.iso_to_datetime(entity['publishedAt'])
            aggregated['data']['value'].append({
                '全国地方公共団体コード': entity['municipalityCode'],
                '公表_年月日': entity['publishedAt'],
                '都道府県名':  entity['prefectureName'],
                '患者_年代':  entity['patientAge'],
                '患者_性別':  entity['patientGender'],
            })

        return aggregated
