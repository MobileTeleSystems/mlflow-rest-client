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

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    Field,
    root_validator,
    validator,
)

from mlflow_rest_client.internal import ListableBase

from .tag import Tag


# pylint: disable=invalid-name
class ModelVersionStage(Enum):
    """Model version stage"""

    UNKNOWN = "None"

    """ Model version has no stage """

    TEST = "Staging"
    """ Is a testing model version"""

    PROD = "Production"
    """ Is a production model version """

    ARCHIVED = "Archived"
    """ Model version was archived """


ModelVersionStageOrList = Union[str, ModelVersionStage, List[ModelVersionStage], List[str]]


# pylint: disable=invalid-name
class ModelVersionState(Enum):
    """Model version state"""

    PENDING = "PENDING_REGISTRATION"
    """ Model version registration is pending """

    FAILED = "FAILED_REGISTRATION"
    """ Model version registration was failed """

    READY = "READY"
    """ Model version registration was successful """


class ModelVersionStatus(BaseModel):
    """Model version state with message

    Parameters
    ----------
    state : :obj:`str` or :obj:`ModelVersionState`, optional
        Model version state

    message : str, optional
        Model version state message

    Attributes
    ----------
    state : :obj:`ModelVersionState`
        Model version state

    message : str
        Model version state message

    Examples
    --------
    .. code:: python

        status = ModelVersionStatus(state="READY")

        status = ModelVersionStatus(state=ModelVersionState.READY)

        status = ModelVersionStatus(state=ModelVersionState.FAILED, message="Reason")
    """

    state: ModelVersionState = ModelVersionState.PENDING
    message: str = ""

    class Config:
        frozen = True

    @validator("state")
    def valid_state(cls, val):  # pylint: disable=no-self-argument, no-self-use
        return ModelVersionState(val) if isinstance(val, str) else ModelVersionState.PENDING

    def __str__(self):
        return str(self.state.name) + (f" because of '{self.message}'" if self.message else "")


# pylint: disable=too-many-ancestors
class ModelVersionTag(Tag):
    """Model version tag

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

        tag = ModelVersionTag(key="some.tag", value="some.val")
    """


class ListableModelVersionTag(ListableBase):

    __root__: List[ModelVersionTag] = []


# pylint: disable=too-many-ancestors
class ModelTag(Tag):
    """Model tag

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

        tag = ModelTag(key="some.tag", value="some.val")
    """


class ListableModelTag(ListableBase):

    __root__: List[ModelTag]


# pylint: disable=too-many-instance-attributes, no-self-argument, no-self-use
class ModelVersion(BaseModel):
    """Model version representation

    Parameters
    ----------
    name : str
        Model name

    version : int
        Version number

    creation_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Version creation timestamp

    last_updated_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Version last update timestamp

    stage : :obj:`str` or :obj:`ModelVersionStage`, optional
        Version stage

    description : str, optional
        Version description

    source : str, optional
        Version source path

    run_id : str, optional
        Run ID used for generating version

    state : :obj:`str` or :obj:`ModelVersionState`, optional
        Version stage

    state_message : str, optional
        Version state message

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Experiment tags list

    Attributes
    ----------
    name : str
        Model name

    version : int
        Version number

    created_time : :obj:`datetime.datetime`
        Version creation timestamp

    updated_time : :obj:`datetime.datetime`
        Version last update timestamp

    stage : :obj:`ModelVersionStage`
        Version stage

    description : str
        Version description

    source : str
        Version source path

    run_id : str
        Run ID used for generating version

    status : :obj:`ModelVersionStatus`
        Version status

    tags : :obj:`ModelVersionTagList`
        Experiment tags list

    Examples
    --------
    .. code:: python

        model_version = ModelVersion(name="some_model", version=1)
    """

    name: str
    version: int
    created_time: datetime = Field(None, alias="creation_timestamp")
    updated_time: datetime = Field(None, alias="last_updated_timestamp")
    stage: ModelVersionStage = Field(ModelVersionStage.UNKNOWN, alias="current_stage")
    description: str = ""
    source: str = ""
    run_id: Optional[UUID] = None
    status: ModelVersionStatus = Field(ModelVersionStatus(), alias="state")
    tags: ListableModelVersionTag = Field(default_factory=list)

    class Config:
        frozen = True
        allow_population_by_field_name = True

    @validator("run_id", pre=True)
    def validation_run_id(cls, val):
        if val == "":
            return None
        return val

    @validator("tags", pre=True)
    def validation_tags(cls, val):
        if isinstance(val, dict):
            return [val]

        return val

    @validator("status", pre=True)
    def validator_status(cls, val):
        if isinstance(val, ModelVersionState):
            return {"status": val}
        if isinstance(val, str):
            return {"status": ModelVersionState(val)}

        return val

    def __str__(self):
        return f"{self.name} v{self.version}"

    @root_validator(pre=True)
    def main_validator(cls, values):

        if "state_message" in values:
            values["state"]["message"] = values["state_message"]

        if "status_message" in values:
            values["status"]["message"] = values["status_message"]

        return values


class ListableModelVersion(ListableBase):

    __root__: List[ModelVersion]

    def __getitem__(self, item):

        if isinstance(item, ModelVersionStage):
            res = {i.stage: i for i in self.__root__}
            return res[item]

        if isinstance(item, str):
            res = {i.name: i for i in self.__root__}
            return res[item]

        return self.__root__[item]

    def __contains__(self, item):
        for itm in self.__root__:

            if isinstance(item, ModelVersionStage) and item == itm.stage:
                return True

            if (itm.name == item.name) and (itm.version == item.version):
                return True
        return False


class Model(BaseModel):
    name: str

    versions: ListableModelVersion = Field(default_factory=list, alias="latest_versions")
    created_time: datetime = Field(None, alias="creation_timestamp")
    updated_time: datetime = Field(None, alias="last_updated_timestamp")
    description: str = ""
    tags: ListableModelTag = Field(default_factory=list)

    def __str__(self):
        return str(self.name)

    class Config:
        frozen = True
        allow_population_by_field_name = True


class ListableModel(ListableBase):

    __root__: List[Model]

    def __getitem__(self, item):

        if isinstance(item, str):
            res = {i.name: i for i in self.__root__}
            return res[item]

        return self.__root__[item]

    def __contains__(self, item):
        if isinstance(item, str):
            res = [i.name for i in self.__root__]

        if isinstance(item, Model):
            res = self.__root__

        return item in res
