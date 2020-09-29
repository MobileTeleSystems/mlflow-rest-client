class Page(object):
    """ Page representation

        :param items: Page items
        :type items: list

        :ivar items: Page items
        :vartype items: list

        :param next_page_token: Next page token
        :type next_page_token: str, optional

        :ivar next_page_token: Next page token
        :vartype next_page_token: str

        :param item_class: Item class to be called
            Should implement `from_list` method, overwise constructor will be used
        :type item_class: :obj:`class`, optional

        :param `**kwargs`: Additional params for item constructor
    """

    def __init__(self, items=None, next_page_token=None):
        self.items = items or []
        self.next_page_token = str(next_page_token) if next_page_token is not None else next_page_token


    @classmethod
    def make(cls, inp, items_key='items', item_class=None, **kwargs):
        """
        Generate objects list from REST API response

        :param inp: Response items
        :type inp: :obj:`list` or :obj:`dict`

        :param `**kwargs`: Additional params for item constructor
        :type kwargs: `dict`

        :returns: Page
        :rtype: :obj:`Page` of `item_class`
        """

        items = inp.copy()
        next_page_token = None

        if isinstance(inp, dict):
            items = inp.get(items_key, [])
            next_page_token = inp.get('next_page_token', None) or kwargs.pop('next_page_token', None)

        if item_class:
            if hasattr(item_class, 'from_list'):
                items = item_class.from_list(items, **kwargs)
            elif hasattr(item_class, 'make'):
                items = [item_class.make(item, **kwargs) for item in items]
            else:
                items = [item_class(item, **kwargs) for item in items]

            return cls(
                items=items,
                next_page_token=next_page_token
            )

        if isinstance(inp, dict):
            return cls(
                items=items,
                next_page_token=next_page_token
            )

        try:
            return cls(
                items=vars(inp),
                next_page_token=next_page_token
            )
        except TypeError:
            return None


    @property
    def has_next_page(self):
        """
        Checks whether this page is last or not

        :returns: `True` if there is a next page, `False` if page is last one
        :rtype: bool
        """
        return bool(self.next_page_token)


    def __repr__(self):
        return "<{self.__class__.__name__} items={count} has_next_page={self.has_next_page}>"\
                .format(self=self, count=len(self.items))


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


    def next(self):
        # Python2 only
        return self.__next__()


    def __next__(self):
        try:
            result = self.items[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result
