
class FileInfo(object):

    def __init__(self, path, root=None, is_dir=False, file_size=None):
        self.path = str(path)
        self.root = str(root) if root else None
        self.is_dir = bool(is_dir)
        self.file_size = int(file_size) if file_size else 0


    @classmethod
    def from_dict(cls, dct, **kwargs):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    path=dct.get('path'),
                    is_dir=dct.get('is_dir', False),
                    file_size=dct.get('file_size'),
                    root=kwargs.get('root')
                )


    @classmethod
    def from_list(cls, lst, **kwargs):
        """
        :param lst: REST API response list
        :type lst: list[dict]
        """
        return [cls.from_dict(item, **kwargs) if isinstance(item, dict) else item for item in lst]


    @property
    def full_path(self):
        return "{self.root}/{self.path}".format(self=self)


    def __repr__(self):
        return ("<{self.__class__.__name__} root={self.root} path={self.path} is_dir={self.is_dir} " +
                "file_size={self.file_size}>")\
                .format(self=self)


    def __str__(self):
        return self.full_path


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
                other = self.__class__(root=other[0], path=other[1])
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
