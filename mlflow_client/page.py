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

    def __init__(self, items=None, next_page_token=None, item_class=None, **kwargs):
        self.items = items or []
        if item_class:
            if hasattr(item_class, 'from_list'):
                self.items = item_class.from_list(self.items, **kwargs)
            else:
                self.items = [item_class(item, **kwargs) for item in self.items]
        self.next_page_token = str(next_page_token) if next_page_token is not None else next_page_token


    @classmethod
    def from_dict(cls, dct, items_key='items', item_class=None, **kwargs):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :param `**kwargs`: Additional params for item constructor

        :returns: Page
        :rtype: :obj:`Page` of `item_class`
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
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :param `**kwargs`: Additional params for item constructor

        :returns: Page
        :rtype: :obj:`Page` of `item_class`
        """
        return cls.from_dict({items_key: lst}, items_key, item_class, **kwargs)


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
