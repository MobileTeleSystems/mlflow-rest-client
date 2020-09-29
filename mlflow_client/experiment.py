from enum import Enum

from .tag import Tag
from .internal import Listable, MakeableFromTupleStr, ComparableByStr

class ExperimentStage(Enum):
    """ Experiment stage """

    active = 'active'
    """ Experiment is active """

    deleted = 'deleted'
    """ Experiment was deleted"""

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

            tag = ExperimentTag('some.tag', 'some.val')
    """
    pass


class Experiment(Listable, MakeableFromTupleStr, ComparableByStr):
    """Experiment representation

        Parameters
        ----------
        id : int
            Experiment ID

        name : str
            Experiment name

        artifact_location : str, optional
            Experiment artifact location

        stage : :obj:`str` or :obj:`ExperimentStage`, optional
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

        stage : :obj:`ExperimentStage`
            Experiment stage

        tags : :obj:`ExperimentTagList`
            Experiment tags list

        Examples
        --------
        .. code:: python

            experiment = Experiment(id=123, name='some_name')
    """

    def __init__(self, id, name, artifact_location=None, stage=None, tags=None):
        self.id = int(id)
        self.name = str(name)
        self.artifact_location = str(artifact_location) if artifact_location else ''

        if not stage:
            stage = ExperimentStage.active
        self.stage = ExperimentStage(stage)

        self.tags = ExperimentTag.from_list(tags or [])


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    id=inp.get('experiment_id') or inp.get('id'),
                    name=inp.get('name'),
                    artifact_location=inp.get('artifact_location'),
                    stage=inp.get('lifecycle_stage') or inp.get('stage'),
                    tags=inp.get('tags')
                )


    def __repr__(self):
        return "<{self.__class__.__name__} id={self.id} name={self.name}>"\
                .format(self=self)


    def __int__(self):
        return self.id


    def __str__(self):
        return self.name
