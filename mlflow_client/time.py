from datetime import datetime
from enum import Enum

class Unit(Enum):
    nanosec = 1000
    msec = 1

def timestamp_2_time(timestamp):
    if timestamp:
        timestamp = int(timestamp)
        if timestamp >= 1000000000000:
            unit = Unit.nanosec
        else:
            unit = Unit.msec
        return datetime.fromtimestamp(timestamp/unit.value)
    return None