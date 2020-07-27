
class Artifact(object):
    """ Artifact

        :param path: Artifact path
        :type path: str

        :ivar path: Artifact path
        :vartype path: str

        :param root: Artifact root
        :type root: str, optional

        :ivar root: Artifact root
        :vartype root: str

        :param is_dir: Is artifact a dir
        :type is_dir: bool, optional

        :ivar is_dir: If `True`, artifact is dir
        :vartype is_dir: bool

        :param file_size: Artifact file size in bytes
        :type file_size: int, optional

        :ivar file_size: Artifact file size in bytes
        :vartype file_size: int
    """

    def __init__(self, path, root=None, is_dir=False, file_size=None):
        self.path = str(path)
        self.root = str(root) if root else None
        self.is_dir = bool(is_dir)
        self.file_size = int(file_size) if file_size else 0


    @classmethod
    def from_dict(cls, dct, **kwargs):
        """
        Generate object from REST API response
        
        :param dct: Response item
        :type dct: dict`

        :param `**kwargs`: Additional constructor params
        :type dct: dict`

        :returns: Artifact
        :rtype: Artifact
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
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :param `**kwargs`: Additional constructor params
        :type dct: dict`

        :returns: Artifacts
        :rtype: :obj:`list` of :obj:`Artifact`
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
