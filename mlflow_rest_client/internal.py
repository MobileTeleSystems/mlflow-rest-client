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

from typing import List

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .tag import Tag


class ListableBase(BaseModel):
    __root__: list

    class Config:
        frozen = True

    @property
    def as_dict(self):
        return {item.key: item for item in self.__root__}

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        if isinstance(item, str) and self.as_dict:
            return self.as_dict[item]

        return self.__root__[item]

    def __contains__(self, item):
        if isinstance(item, str):
            return any(i.key == item for i in self.__root__)

        return item in self.__root__

    def __len__(self):
        return len(self.__root__)


class ListableTag(ListableBase):

    __root__: List[Tag]

    def __getitem__(self, item):
        if isinstance(item, str):
            res = {i.key: i for i in self.__root__}
            return res[item]

        return super().__getitem__(item)
