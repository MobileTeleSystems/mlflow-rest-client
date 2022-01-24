from __future__ import annotations

import logging
import random
import string
from datetime import datetime

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


def rand_str(length: int = 8) -> str:
    letters = string.ascii_lowercase
    return "".join(random.sample(letters, length))


def rand_int(a: int = 0, b: int = 100) -> int:
    return random.randint(a, b)


def rand_float(a: float = 0, b: int = 100) -> float:
    return random.uniform(a, b)


def now() -> datetime:
    return datetime.now().replace(microsecond=0)
