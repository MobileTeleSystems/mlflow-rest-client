#  Copyright 2022 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
    def to_dict(cls, values: dict) -> dict:  # pylint: disable=no-self-argument, no-self-use
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
