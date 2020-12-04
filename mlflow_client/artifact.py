import os

from .internal import ComparableByStr, HashableByStr, Listable, MakeableFromStr


class Artifact(Listable, MakeableFromStr, ComparableByStr, HashableByStr):
    """Artifact representation

    Parameters
    ----------
    path : str
        Artifact path

    root : str
        Artifact root

    is_dir : bool
        Is artifact a dir

    file_size : int
        Artifact file size in bytes

    Examples
    --------
    .. code:: python

        artifact = Artifact(path="some/path")
    """

    def __init__(self, path, root=None, is_dir=False, file_size=None):
        self.path = str(path)
        """Artifact path"""

        self.root = str(root) if root else None
        """Artifact root"""

        self.is_dir = bool(is_dir)
        """If `True`, artifact is dir"""

        self.file_size = int(file_size) if file_size else 0
        """Artifact file size in bytes"""

    @classmethod
    def _from_dict(cls, inp):
        return cls(
            path=inp.get("path"), is_dir=inp.get("is_dir", False), file_size=inp.get("file_size"), root=inp.get("root")
        )

    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, tuple) and len(inp) == 2:
            return cls(root=inp[0], path=inp[1], **kwargs)
        return super(Artifact, cls).make(inp, **kwargs)

    @property
    def full_path(self):
        if self.root:
            return os.path.join(self.root, self.path)
        return self.path

    def __repr__(self):
        return (
            "<{self.__class__.__name__} root={self.root} path={self.path} is_dir={self.is_dir} "
            + "file_size={self.file_size}>"
        ).format(self=self)

    def __str__(self):
        return self.full_path
