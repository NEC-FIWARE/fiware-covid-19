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

import argparse
import libs.settings as settings
from libs.broker import Broker
from libs.builder.entity_builder import EntityBuilder
from libs.builder.patients_summary_builder import PatientsSummaryBuilder
from libs.builder.patients_daily_aggregated_builder import PatientsDailyAggregatedBuilder
from libs.builder.patients_list_aggregated_builder import PatientsListAggregatedBuilder
from libs.builder.test_people_daily_aggregated_builder import TestPeopleDailyAggregatedBuilder
from libs.builder.test_count_daily_aggregated_builder import TestCountDailyAggregatedBuilder
from libs.builder.confirm_negative_daily_aggregated_builder import ConfirmNegativeDailyAggregatedBuilder
from libs.builder.callcenter_daily_aggregated_builder import CallCenterDailyAggregatedBuilder


BUILDERS = [
    PatientsSummaryBuilder,
    PatientsDailyAggregatedBuilder,
    PatientsListAggregatedBuilder,
    TestPeopleDailyAggregatedBuilder,
    TestCountDailyAggregatedBuilder,
    ConfirmNegativeDailyAggregatedBuilder,
    CallCenterDailyAggregatedBuilder,
]


def main():
    args = arg_parse()
    settings.load_config(args.config)

    if settings.CONFIG_TYPE == 'yml':
        municipality_code = settings.CODE
        aggregate_types = settings.AGGREGATE

    elif settings.CONFIG_TYPE == 'json':
        municipality_code = args.mcode
        aggregate_types = [args.type]

    else:
        print('unknown config type.')
        exit()

    if not settings.BROKER_URL:
        print('BROKER_URL is none.')
        exit()

    if not municipality_code:
        print('no municipality code enterd.')
        exit()

    broker = Broker(settings.BROKER_URL,
                    broker_version=settings.BROKER_VERSION,
                    broker_service=settings.BROKER_SERVICE,
                    broker_path=settings.BROKER_PATH,
                    broker_token=settings.BROKER_TOKEN,
                    broker_context=settings.BROKER_CONTEXT)

    for aggregate_type in aggregate_types:

        builder = select_builder(broker, aggregate_type)

        print(':aggregate:', broker.broker_version, aggregate_type)

        aggregated = builder.build_entity(municipality_code)

        print(':update:')

        broker.broker_update([aggregated])

        print(':end:')

        print('id:', aggregated['id'])
        print()


def arg_parse():
    aggregate_types = []
    for builder in BUILDERS:
        aggregate_types.append(builder.AGGREGATE_TYPE)

    parser = argparse.ArgumentParser(
        description='Entity aggregation tool.',
        epilog="Aggregate types:\n"+"\n".join(aggregate_types),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-m', '--mcode', help='Municipality code.')
    parser.add_argument(
        '-t', '--type', help="Aggregate type.")
    parser.add_argument(
        '-c', '--config', help='Config file.')

    return parser.parse_args()


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


if __name__ == "__main__":
    main()
