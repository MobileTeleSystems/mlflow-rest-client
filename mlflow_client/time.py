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
        if isinstance(timestamp, datetime):
            return timestamp
        else:
            return datetime.fromtimestamp(normalize_timestamp(timestamp))
    return None

def time_2_timestamp(time):
    if time:
        if isinstance(time, float) or isinstance(time, int):
            timestamp = normalize_timestamp(time)
        if isinstance(time, datetime):
            if time.utcoffset() is not None:
                time -= time.utcoffset()
            if time.tzinfo is not None:
                time = time.replace(tzinfo=datetime.timezone.utc)
            timestamp = int(time.timestamp())
        return mlflow_timestamp(timestamp)
    return None