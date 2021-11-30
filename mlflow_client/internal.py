from typing import List

from pydantic import BaseModel
from pydantic.generics import GenericModel

from .tag import Tag


class ListableBase(BaseModel):
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

        return super(ListableTag, self).__getitem__(item)
