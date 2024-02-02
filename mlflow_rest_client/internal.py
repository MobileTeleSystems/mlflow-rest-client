# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
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
