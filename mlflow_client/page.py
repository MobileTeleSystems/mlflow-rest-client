class Page(object):

    def __init__(self, items=None, next_page_token=None, item_class=None, **kwargs):
        self.items = items or []
        if item_class:
            if hasattr(item_class, 'from_list'):
                self.items = item_class.from_list(self.items, **kwargs)
            else:
                self.items = [item_class(item, **kwargs) for item in self.items]
        self.next_page_token = next_page_token


    @classmethod
    def from_dict(cls, dct, items_key='items', item_class=None, **kwargs):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    items=dct.get(items_key, []),
                    next_page_token=dct.get('next_page_token'),
                    item_class=item_class,
                    **kwargs
                )


    @classmethod
    def from_list(cls, lst, items_key='items', item_class=None, **kwargs):
        """
        :param lst: REST API response list
        :type lst: list[dict]
        """
        return cls.from_dict({items_key: lst}, items_key, item_class, **kwargs)


    @property
    def has_next_page(self):
        return bool(self.next_page_token)

    def __repr__(self):
        return "<{self.__class__.__name__} items={count} has_next_page={self.has_next_page}>"\
                .format(self=self, count=len(self.items))


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)


    def __getattr__(self, attr):
        return getattr(self.items, attr)


    def __add__(self, item):
        return self.items.append(item)


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
        except IndexError:
            raise StopIteration
        self._index += 1
        return result
