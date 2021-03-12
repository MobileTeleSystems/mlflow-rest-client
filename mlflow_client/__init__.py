# pylint: disable= wrong-import-position

from __future__ import absolute_import

import os

VERSION_FILE = os.path.join(os.path.dirname(__file__), "VERSION")

with open(VERSION_FILE) as f:
    __version__ = f.read().strip()

from .mlflow_api_client import MLflowApiClient
