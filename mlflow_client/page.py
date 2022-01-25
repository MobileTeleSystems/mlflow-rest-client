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


class Page:
    """Page representation

    Parameters
    ----------
    items : Iterable, optional
        Page items

    next_page_token : str, optional
        Next page token

    Attributes
    ----------
    items : Iterable
        Page items

    next_page_token : str
        Next page token

    Examples
    --------
    .. code:: python

        model = Page(items=[Model(name="some_model")])

        model = Page(items=[Model(name="some_model")], next_page_token="some_token")
    """

    def __init__(self, items=None, next_page_token=None):
        self.items = items or []
        self.next_page_token = str(next_page_token) if next_page_token is not None else next_page_token
        self._index = 0

    @classmethod
    def make(cls, inp, items_key="items", item_class=None, **kwargs):
        """
        Generate objects from REST API response

        Parameters
        ----------
        inp : :obj:`list` or :obj:`dict`
            Page items

        items_key : str, optional
            Key name for fetching items from dict input

        item_class : class, optional
            Item class to be called

            Should implement `from_list` or `make` methods, otherwise constructor will be used

        **kwargs : dict, optional
            Additional params for item constructor

        Returns
        -------
        page : obj:`Page` of `item_class`
            Page of items

        Examples
        --------
        .. code:: python

            model = Page.make([Model(name="some_model")])

            model = Page.make([ModelVersion(name="some_model", version=1)], name="another_model")
        """

        items = inp.copy()
        next_page_token = None

        if isinstance(inp, dict):
            items = inp.get(items_key, [])
            next_page_token = inp.get("next_page_token", None) or kwargs.pop("next_page_token", None)

        if item_class:
            items = [item_class.parse_obj(item, **kwargs) for item in items]

            return cls(items=items, next_page_token=next_page_token)

        if isinstance(inp, dict):
            return cls(items=items, next_page_token=next_page_token)

        try:
            return cls(items=vars(inp), next_page_token=next_page_token)
        except TypeError:
            return None

    @property
    def has_next_page(self):
        """
        Checks whether this page is last or not

        Returns
        -------
        has_next_page: bool
            `True` if there is a next page, `False` if page is last one
        """
        return bool(self.next_page_token)

    def __repr__(self):
        return f"<{self.__class__.__name__} items={len(self.items)} has_next_page={self.has_next_page}>"

    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, list):
                return self.items == other

            other = self.make(other)

        return repr(self) == repr(other)

    def __getitem__(self, i):
        return self.items[i]

    def __getattr__(self, attr):
        return getattr(self.items, attr)

    def __add__(self, item):
        self.items.append(item)
        return self

    def __contains__(self, item):
        return item in self.items

    def __delitem__(self, i):
        del self.items[i]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        try:
            result = self.items[self._index]
        except IndexError as e:
            raise StopIteration from e
        self._index += 1
        return result
