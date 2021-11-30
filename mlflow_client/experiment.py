from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from .internal import ListableBase
from .tag import Tag


# pylint: disable=invalid-name
class EXPERIMENTSTAGE(Enum):
    """Experiment stage"""

    active = "active"
    """ Experiment is active """

    deleted = "deleted"
    """ Experiment was deleted"""


# pylint: disable=too-many-ancestors
class ExperimentTag(Tag):
    """Experiment tag

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

        tag = ExperimentTag("some.tag", "some.val")
    """


class ListExperimentTags(ListableBase):

    __root__: List[ExperimentTag]


class Experiment(BaseModel):
    """Experiment representation

    Parameters
    ----------
    id : int
        Experiment ID

    name : str
        Experiment name

    artifact_location : str, optional
        Experiment artifact location

    stage : :obj:`str` or :obj:`EXPERIMENTSTAGE`, optional
        Experiment stage

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Experiment tags list

    Attributes
    ----------
    id : int
        Experiment ID

    name : str
        Experiment name

    artifact_location : str
        Experiment artifact location

    stage : :obj:`EXPERIMENTSTAGE`
        Experiment stage

    tags : :obj:`ExperimentTagList`
        Experiment tags list

    Examples
    --------
    .. code:: python

        experiment = Experiment(id=123, name="some_name")
    """

    id: int = Field(alias="experiment_id")
    name: str
    artifact_location: str = ""
    stage: EXPERIMENTSTAGE = Field(EXPERIMENTSTAGE.active, alias="lifecycle_stage")
    tags: ListExperimentTags = Field(default_factory=list)

    class Config:
        frozen = True

    def __str__(self):
        return self.name
