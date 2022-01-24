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
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    Field,
    root_validator,
)

from .internal import ListableBase, ListableTag
from .tag import Tag

RunId = Union[str, UUID]


# pylint: disable=invalid-name
class RunStage(Enum):
    """Run stage"""

    ACTIVE = "active"
    """ Run is active """

    DELETED = "deleted"
    """ Run was deleted """


# pylint: disable=invalid-name
class RunStatus(Enum):
    """Run status"""

    STARTED = "RUNNING"
    """ Run is running or created """

    SCHEDULED = "SCHEDULED"
    """ Run is scheduled for run """

    FINISHED = "FINISHED"
    """ Run was finished successfully """

    FAILED = "FAILED"
    """ Run is failed """

    KILLED = "KILLED"
    """ Run was killed """


# pylint: disable=invalid-name
class RunViewType(Enum):
    """Run view type"""

    ACTIVE = "ACTIVE_ONLY"
    """ Show only active runs """

    DELETED = "DELETED_ONLY"
    """ Show only deleted runs """

    ALL = "ALL"
    """ Show all runs """


class RunInfo(BaseModel):
    """Run information representation

    Parameters
    ----------
    id : str
        Run ID

    experiment_id : int, optional
        Experiment ID

    status : :obj:`str` or :obj:`RunStatus`, optional
        Run status

    stage : :obj:`str` or :obj:`RunStage`, optional
        Run stage

    start_time : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Run start time

    end_time : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Run end time

    artifact_uri : str, optional
        Artifact URL

    Attributes
    ----------
    id : :str
        Run ID

    experiment_id : int
        Experiment ID

    status : :obj:`RunStatus`
        Run status

    stage : :obj:`RunStage`
        Run stage

    start_time : :obj:`datetime.datetime`
        Run start time

    end_time : :obj:`datetime.datetime`
        Run end time

    artifact_uri : str
        Artifact URL

    Examples
    --------
    .. code:: python

        run_info = RunInfo("some_id")
    """

    id: UUID
    experiment_id: Optional[int] = None
    status: RunStatus = RunStatus.STARTED
    stage: RunStage = Field(RunStage.ACTIVE, alias="lifecycle_stage")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    artifact_uri: str = ""

    class Config:
        frozen = True
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def validate_date(cls, values):  # pylint: disable=no-self-argument, no-self-use
        if not values.get("id"):
            values["id"] = values.get("run_id") or values.get("run_uuid")
        return values

    def __str__(self):
        return str(self.id)


class ListableRunInfo(ListableBase):

    __root__: List[RunInfo]

    def __getitem__(self, item):
        if isinstance(item, str):
            item = UUID(item)

        if isinstance(item, UUID):
            res = {i.id: i for i in self.__root__}
            return res[item]

        return self.__root__[item]

    def __contains__(self, item):
        res = [i.id for i in self.__root__]

        if isinstance(item, str):
            item = UUID(str(item))

        if isinstance(item, RunInfo):
            res = self.__root__

        return item in res


class Param(Tag):
    """Run parameter

    Parameters
    ----------
    key : str
        Param name

    value : str
        Param value

    Attributes
    ----------
    key : str
        Param name

    value : str
        Param value
    """


class ListableParam(ListableBase):

    __root__: List[Param]


# pylint: disable=too-many-ancestors
class Metric(BaseModel):
    """Run metric representation

    Parameters
    ----------
    name : str
        Metric name

    value : float, optional
        Metric value

    step : int, optional
        Metric step

    timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Metric timestamp

    Attributes
    ----------
    name : str
        Metric name

    value : float
        Metric value

    step : int
        Metric step

    timestamp : :obj:`datetime.datetime`
        Metric timestamp

    Examples
    --------
    .. code:: python

        metric = Metric(name="some.metric")
        metric = Metric(name="some.metric", value=1.23)
        metric = Metric(name="some.metric", value=1.23, step=2)
        metric = Metric(
            name="some.metric", value=1.23, step=2, timestamp=datetime.datetime.now()
        )
    """

    key: str
    value: Optional[float] = None
    step: int = 0
    timestamp: Optional[datetime] = None

    def __str__(self):
        return str(f"{self.key}: {self.value} for {self.step} at {self.timestamp}")

    class Config:
        frozen = True


class ListableMetric(ListableBase):

    __root__: List[Metric]


# pylint: disable=too-many-ancestors
class RunTag(Tag):
    """Run tag

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

        tag = RunTag(key="some.tag", value="some.val")
    """


class RunData(BaseModel):
    """Run data representation

    Parameters
    ----------
    params : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Params list

    metrics : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Metrics list

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Run tags list

    Attributes
    ----------
    params : :obj:`ParamList`
        Params list

    metrics : :obj:`MetricList`
        Metrics list

    tags : :obj:`RunTagList`
        Run tags list

    Examples
    --------
    .. code:: python

        param = Param(key="some.param", value="some_value")
        metric = Metric(name="some.metric", value=1.23)
        tag = RunTag(key="some.tag", value="some.val")

        run_data = RunData(params=[param], metrics=[metric], tags=[tag])
    """

    params: ListableParam = Field(default_factory=list)
    metrics: ListableMetric = Field(default_factory=list)
    tags: ListableTag = Field(default_factory=list)

    class Config:
        frozen = True


class Run(BaseModel):
    """Run representation

    Parameters
    ----------
    info : :obj:`dict` or :obj:`RunInfo`
        Run info

    data : :obj:`dict` or :obj:`RunData`, optional
        Run data

    Attributes
    ----------
    info : :obj:`RunInfo`
        Run info

    data : :obj:`RunData`
        Run data

    Examples
    --------
    .. code:: python

        run_info = RunInfo(id="some_id")
        run_data = RunData(params=..., metrics=..., tags=...)

        run = Run(run_info, run_data)
    """

    info: RunInfo
    data: RunData = Field(default_factory=RunData)

    class Config:
        frozen = True

    def __str__(self) -> str:
        return str(self.info)

    def __getattr__(self, attr):
        if hasattr(self.info, attr):
            return getattr(self.info, attr)
        if hasattr(self.data, attr):
            return getattr(self.data, attr)

        raise AttributeError(f"{self.__class__.__name__} object has no attribute {attr}")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Run):
            return self.info.dict() == other.info.dict()

        return super().__eq__(other)
