from .internal import Listable, MakeableFromTupleStr, ComparableByStr, HashableByStr


class Tag(Listable, MakeableFromTupleStr, ComparableByStr, HashableByStr):
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
        self.value = str(value) if value else ''


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    key=inp.get('key'),
                    value=inp.get('value')
                )


    @classmethod
    def from_list(cls, inp, **kwargs):
        if isinstance(inp, dict):
            return cls.list_class(cls.make(item, **kwargs) for item in inp.items())
        return super(Tag, cls).from_list(inp, **kwargs)


    def __repr__(self):
        return "<{self.__class__.__name__} key={self.key} value={self.value}>"\
                .format(self=self)


    def __str__(self):
        return self.key
