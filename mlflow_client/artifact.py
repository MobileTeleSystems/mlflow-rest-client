import os
from pathlib import Path
from typing import Optional

from pydantic import AnyUrl, BaseModel


class Artifact(BaseModel):
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

    path: Path
    file_size: int
    root: Optional[AnyUrl]

    is_dir: bool = False

    class Config:
        frozen = True

    @property
    def full_path(self):
        if self.root:
            return os.path.join(self.root, self.path)
        return self.path

    def __str__(self):
        return self.full_path
