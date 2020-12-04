import sys
from textwrap import dedent

import six


# pylint: disable=isinstance-second-argument-not-valid-type
class SearchableList(list):
    _compare_with_class = None

    def __contains__(self, item):
        for it in self:
            if isinstance(it, self._compare_with_class) and it == item:
                return True

        if not isinstance(item, int):
            return False

        return super(SearchableList, self).__contains__(item)

    # pylint: disable=missing-format-attribute
    def __getitem__(self, item):
        for it in self:
            if isinstance(it, self._compare_with_class) and it == item:
                return it

        if not isinstance(item, int):
            raise KeyError(
                "{klass.__name__} not found in list by {item.__class__.__name__} {item}".format(
                    klass=self._compare_with_class, item=item
                )
            )

        return super(SearchableList, self).__getitem__(item)


class Makeable(object):
    @classmethod
    def make(cls, inp, **kwargs):
        """
        Generate objects list from REST API response

        Parameters
        ----------
        inp : :obj:`dict`
            Response

        **kwargs : dict
            Additional constructor params

        Returns
        ----------
        item : {klass}
            Item with certain class

        Examples
        --------
        .. code:: python

            {var} = {klass}.make({{"some": "input"}})
        """.format(
            klass=cls.__name__, var=cls.__name__.lower()
        )

        if isinstance(inp, cls):
            return inp

        if isinstance(inp, dict):
            return cls.from_dict(inp, **kwargs)

        try:
            return cls.from_dict(vars(inp), **kwargs)
        except TypeError:
            return None

    @classmethod
    def from_dict(cls, inp, **kwargs):
        """
        Generate objects list from REST API response

        Parameters
        ----------
        inp : :obj:`list` of :obj:`dict`
            Response

        **kwargs : dict
            Additional constructor params

        Returns
        ----------
        item : {klass}
            Item with certain class
        """.format(
            klass=cls.__name__
        )

        dct = inp.copy()
        dct.update(kwargs)

        return cls._from_dict(dct)

    @classmethod
    def _from_dict(cls, inp):
        return cls(**inp)


class ListableMeta(type):
    @staticmethod
    def _class_doc(klass):
        return dedent(
            """
            List of :ref:`{klass}` with extended functions

            Parameters
            ----------
            iterable : Iterable
                Any iterable

            Examples
            --------
            .. code:: python

                name = 123  # depends on class itself
                item = {klass}(id)

                simple_list = [item]
                this_list = {klass}.from_list([item])  # or {klass}List([item])

                assert item in simple_list
                assert item in this_list

                assert name not in simple_list
                assert name in this_list

        """.format(
                klass=klass
            )
        )

    def __new__(cls, name, bases, attrs):
        list_class = attrs.get("list_class", None)

        if list_class is None:
            list_class_name = "{}List".format(name)
            list_class = type(list_class_name, (SearchableList,), {})
            try:
                list_class.__doc__ = cls._class_doc(name)
            except AttributeError:
                pass

        attrs["list_class"] = list_class
        result = type.__new__(cls, name, bases, attrs)

        list_class.__module__ = result.__module__
        list_class._compare_with_class = result

        setattr(sys.modules[result.__module__], list_class.__name__, list_class)

        setattr(result, "list_class", list_class)
        return result


@six.add_metaclass(ListableMeta)
class Listable(Makeable):
    # pylint: disable=no-member
    @classmethod
    def from_list(cls, inp, **kwargs):
        """
        Generate objects list from REST API response

        Parameters
        ----------
        inp : :obj:`list` of :obj:`dict`
            Response

        **kwargs : dict
            Additional constructor params

        Returns
        ----------
        list : {klass}
            Items class list
        """.format(
            klass=cls.list_class
        )

        return cls.list_class(cls.make(item, **kwargs) for item in inp)


class Comparable(object):
    # pylint: disable=no-member
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
