# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Dict, List, Union

from pydantic import BaseModel, root_validator  # pylint: disable=no-name-in-module


# pylint: disable=too-many-ancestors
class Tag(BaseModel):
    """Generic tag class

    Parameters
    ----------
    key : str
        Tag name

    value : str
        Tag value

    Examples
    --------
    .. code:: python

        tag = Tag(key="some.tag", value="some.val")
    """

    key: str
    value: str = ""

    class Config:
        frozen = True

    def __str__(self):
        return self.key

    @root_validator(pre=True)
    def to_dict(cls, values: dict) -> dict:  # pylint: disable=no-self-argument
        """Bring to a single format."""
        if isinstance(values, dict) and ("key" not in values and "value" not in values):
            result = {}
            for key, val in values.items():
                result["key"] = key
                result["value"] = val

            return result

        return values


# Custom type for type hints with Tag models
TagsListOrDict = Union[Dict[str, str], List[Dict[str, str]], List[Tag]]
