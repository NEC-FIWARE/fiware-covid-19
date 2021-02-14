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
from datetime import datetime, timedelta


def date_range_to_today(start_dt: datetime) -> list:
    return date_range(start_dt, datetime.now())


def date_range(start_dt: datetime, end_dt: datetime) -> list:
    return list(start_dt + timedelta(days=i)
                for i in range((end_dt - start_dt).days + 1))


def iso_to_datetime(iso_string: str) -> datetime:
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        pass
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S.%f')
    except:
        pass
    try:
        return datetime.strptime(iso_string, '%Y-%m-%dT%H:%M:%S')
    except:
        pass

    raise ValueError('invalid format. {}'.format(iso_string))


def weekday_name(dt: datetime) -> str:
    return ['月', '火', '水', '木', '金', '土', '日'][dt.weekday()]
