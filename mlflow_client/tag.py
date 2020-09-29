from .internal import Listable, MakeableFromTupleStr, ComparableByStr, HashableByStr


class Tag(Listable, MakeableFromTupleStr, ComparableByStr, HashableByStr):
    """ Generic tag class

        Parameters
        ----------
        key : str
            Tag name

        value : str
            Tag value

        Attributes
        ----------
        key : str
            Tag name

        value : str
            Tag value

        Examples
        --------
        .. code:: python

            tag = Tag('some.tag', 'some.val')
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
