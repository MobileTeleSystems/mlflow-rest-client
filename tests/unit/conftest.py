import random
import string
import logging

from datetime import datetime

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


def rand_str(length=8):
    letters = string.ascii_lowercase
    return "".join(random.sample(letters, length))


def rand_int(a=0, b=100):
    return random.randint(a, b)


def rand_float(a=0, b=100):
    return random.uniform(a, b)


def now():
    return datetime.now().replace(microsecond=0)
