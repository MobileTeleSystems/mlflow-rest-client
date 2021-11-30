import datetime
import time
from enum import Enum
from typing import Optional


class Unit(Enum):
    MSEC = 1000
    SEC = 1


def current_timestamp():
    return datetime.datetime.now().timestamp()


def normalize_timestamp(timestamp):
    timestamp = int(timestamp)
    if timestamp >= 1000000000000:
        unit = Unit.MSEC
    else:
        unit = Unit.SEC
    return timestamp / unit.value


def mlflow_timestamp(timestamp):
    return timestamp * 1000


def timestamp_2_time(timestamp):
    if timestamp:
        if isinstance(timestamp, datetime.datetime):
            return timestamp
        return datetime.datetime.utcfromtimestamp(normalize_timestamp(timestamp))
    return None


def format_to_timestamp(data: Optional[int] = None) -> int:
    """Any object (str, int, datetime formatting to timestamp."""

    if not data:
        data = datetime.datetime.now().timestamp()
    elif isinstance(data, int):
        data = normalize_timestamp(data)
    elif isinstance(data, datetime.datetime):
        data = data.timestamp()

    return normalize_timestamp(int(data))
