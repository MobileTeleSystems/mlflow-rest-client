from datetime import datetime
from enum import Enum

class Unit(Enum):
    nanosec = 1000
    msec = 1

def normalize_timestamp(timestamp):
    timestamp = int(timestamp)
    if timestamp >= 1000000000000:
        unit = Unit.nanosec
    else:
        unit = Unit.msec
    return timestamp/unit.value

def mlflow_timestamp(timestamp):
    return timestamp*1000

def timestamp_2_time(timestamp):
    if timestamp:
        return datetime.fromtimestamp(normalize_timestamp(timestamp))
    return None

def time_2_timestamp(time):
    if time:
        if isinstance(time, float) or isinstance(time, int):
            timestamp = normalize_timestamp(time)
        if isinstance(time, datetime):
            utc_naive = datetime.replace(tzinfo=None) - datetime.utcoffset()
            timestamp = (utc_naive - datetime(1970, 1, 1)).total_seconds()
        return mlflow_timestamp(timestamp)
    return None