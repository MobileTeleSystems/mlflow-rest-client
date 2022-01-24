#  Copyright 2022 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import datetime
from enum import Enum
from typing import Union

AnyTimestamp = Union[int, datetime.datetime, None]


class Unit(Enum):
    MSEC = 1000
    SEC = 1


def current_timestamp() -> int:
    return int(datetime.datetime.now().timestamp())


def normalize_timestamp(timestamp: int | float) -> int:
    timestamp = int(timestamp)
    if timestamp >= 1000000000000:
        unit = Unit.MSEC
    else:
        unit = Unit.SEC
    return timestamp // unit.value


def mlflow_timestamp(timestamp: int) -> int:
    return timestamp * 1000


def timestamp_2_time(timestamp: AnyTimestamp) -> datetime.datetime | None:
    if timestamp:
        if isinstance(timestamp, datetime.datetime):
            return timestamp
        return datetime.datetime.utcfromtimestamp(normalize_timestamp(timestamp))
    return None


def format_to_timestamp(data: AnyTimestamp = None) -> int:
    """Any object (str, int, datetime formatting to timestamp."""

    if not data:
        result = datetime.datetime.now().timestamp()
    elif isinstance(data, int):
        result = normalize_timestamp(data)
    elif isinstance(data, datetime.datetime):
        result = data.timestamp()
    else:
        result = data

    return normalize_timestamp(int(result))
