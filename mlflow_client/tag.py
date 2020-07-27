class Tag(object):
    """ Generic tag class

        :param key: Tag name
        :type key: str

        :ivar name: Tag name
        :vartype name: str

        :param value: Tag value
        :type value: str

        :ivar value: Tag value
        :vartype value: str
    """

    def __init__(self, key, value=None):
        self.key = str(key)
        self.value = str(value)


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Tag
        :rtype: Tag
        """
        return cls(
                    key=dct.get('key'),
                    value=dct.get('value')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Tag
        :rtype: :obj:`list` of :obj:`Tag`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<{self.__class__.__name__} key={self.key} value={self.value}>"\
                .format(self=self)


    def __str__(self):
        return self.key


    def __hash__(self):
        return hash(self.__str__())


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, str):
                return other == self.__str__()
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(key=other[0], value=other[1])
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
