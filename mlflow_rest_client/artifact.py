#  Copyright 2022 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import AnyUrl, BaseModel  # pylint: disable=no-name-in-module


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
