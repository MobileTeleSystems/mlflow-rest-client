# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os

VERSION_FILE = os.path.join(os.path.dirname(__file__), "VERSION")


def get_version() -> str:
    with open(VERSION_FILE) as f:
        return f.read().strip()
