import datetime
import time

from enum import Enum


class Unit(Enum):
    nanosec = 1000
    msec = 1


def current_timestamp():
    return int(time.time() - time.timezone)


def normalize_timestamp(timestamp):
    timestamp = int(timestamp)
    if timestamp >= 1000000000000:
        unit = Unit.nanosec
    else:
        unit = Unit.msec
    return timestamp / unit.value


def mlflow_timestamp(timestamp):
    return timestamp * 1000


def timestamp_2_time(timestamp):
    if timestamp:
        if isinstance(timestamp, datetime.datetime):
            return timestamp
        return datetime.datetime.utcfromtimestamp(normalize_timestamp(timestamp))
    return None


def _remove_tz(inp):
    if inp.utcoffset() is not None:
        inp -= inp.utcoffset()
    if inp.tzinfo is not None:
        if hasattr(datetime, "timezone"):
            inp = inp.replace(tzinfo=datetime.timezone.utc)
        else:
            inp = inp.replace(tzinfo=None)
    return inp


def time_2_timestamp(inp):
    if inp:
        if isinstance(inp, (float, int)):
            timestamp = normalize_timestamp(inp)
        if isinstance(inp, datetime.datetime):
            inp = _remove_tz(inp)
            utc = _remove_tz(datetime.datetime(1970, 1, 1))
            timestamp = (inp - utc).total_seconds()
        return mlflow_timestamp(timestamp)
    return None
