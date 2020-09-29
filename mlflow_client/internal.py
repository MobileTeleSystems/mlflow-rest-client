import six


class SearchableList(list):
    _compare_with_class = None

    def __contains__(self, item):
        for it in self:
            if isinstance(it, self._compare_with_class) and it == item:
                return True

        return super(SearchableList, self).__contains__(item)


    def __getitem__(self, item):
        for it in self:
            if isinstance(it, self._compare_with_class) and it == item:
                return it
        return super(SearchableList, self).__getitem__(item)


class Makeable(object):
    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, cls):
            return inp

        if isinstance(inp, dict):
            return cls.from_dict(inp, **kwargs)

        try:
            return cls.from_dict(vars(inp), **kwargs)
        except TypeError as e:
            print(inp)
            print(e)
            return None


    @classmethod
    def from_dict(cls, inp, **kwargs):
        """
        Generate object from REST API response

        :param inp: Response item
        :type inp: `dict`

        :param `**kwargs`: Additional constructor params
        :type kwargs: `dict`

        :returns: Item
        :rtype: :obj:`self.__class__`
        """
        dct = inp.copy()
        dct.update(kwargs)

        return cls._from_dict(dct)


    @classmethod
    def _from_dict(cls, inp):
        return cls(**inp)


class ListableMeta(type):
    def __new__(metacls, name, bases, attrs):
        list_class = attrs.get('list_class', None)

        if list_class is None:
            list_class_name = "{}List".format(name)
            list_class = type(list_class_name, (SearchableList, ), {})

        attrs['list_class'] = list_class
        result = type.__new__(metacls, name, bases, attrs)

        list_class._compare_with_class = result
        setattr(result, 'list_class', list_class)
        return result


@six.add_metaclass(ListableMeta)
class Listable(Makeable):
    @classmethod
    def from_list(cls, inp, **kwargs):
        """
        Generate objects list from REST API response

        :param inp: Response items
        :type inp: :obj:`list` of :obj:`dict`

        :param `**kwargs`: Additional constructor params
        :type kwargs: `dict`

        :returns: Item
        :rtype: :obj:`list` of :obj:`self.__class__`
        """
        return cls.list_class(cls.make(item, **kwargs) for item in inp)


class Comparable(object):
    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            other = self.__class__.make(other)

        return repr(self) == repr(other)


class ComparableByStr(Comparable):
    def __eq__(self, other):
        if isinstance(other, six.string_types):
            return other == str(self)

        return super(ComparableByStr, self).__eq__(other)


class MakeableFromTuple(Makeable):
    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, tuple):
            return cls(*inp, **kwargs)
        return super(MakeableFromTuple, cls).make(inp, **kwargs)


class MakeableFromStr(Makeable):
    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, six.string_types):
            print(inp)
            return cls(inp, **kwargs)
        return super(MakeableFromStr, cls).make(inp, **kwargs)


class MakeableFromTupleStr(MakeableFromTuple):
    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, six.string_types):
            return cls(inp, **kwargs)
        return super(MakeableFromTupleStr, cls).make(inp, **kwargs)


class HashableByStr(object):
    def __hash__(self):
        return hash(str(self))
