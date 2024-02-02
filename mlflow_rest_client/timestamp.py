# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
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
