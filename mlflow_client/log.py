import logging
import logging.handlers
import sys

def init(level):
    # Setup logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_logger(level))
    return logger


def get_logger(level=logging.INFO):
    return init(level)


def stdout_logger(level):
    console = logging.StreamHandler(sys.stdout)
    if isinstance(level, str):
        level = level.upper()
    console.setLevel(level)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    return console
