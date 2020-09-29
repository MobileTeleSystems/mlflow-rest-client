from enum import Enum

from .tag import Tag
from .internal import Listable, MakeableFromTupleStr, ComparableByStr

class ExperimentStage(Enum):
    """ Experiment stage """

    active = 'active'
    deleted = 'deleted'

class ExperimentTag(Tag):
    """ Experiment tag

        :param key: Tag name
        :type key: str

        :ivar name: Tag name
        :vartype name: str

        :param value: Tag value
        :type value: str

        :ivar value: Tag value
        :vartype value: str
    """
    pass


class Experiment(Listable, MakeableFromTupleStr, ComparableByStr):
    """ Experiment

        :param id: Experiment ID
        :type id: int

        :ivar id: Experiment ID
        :vartype id: int

        :param name: Experiment name
        :type name: str

        :ivar name: Experiment name
        :vartype name: str

        :param artifact_location: Experiment artifact location
        :type artifact_location: str, optional

        :ivar artifact_location: Experiment artifact location
        :vartype artifact_location: str

        :param stage: Experiment stage
        :type stage: str, optional

        :ivar stage: Experiment stage
        :vartype stage: :obj:`ExperimentStage`

        :param tags: Tags list
        :type tags: :obj:`list` of :obj:`dict`, optional

        :ivar tags: Tags list
        :vartype tags: :obj:`dict` of :obj:`str`::obj:`ModelVersionTag`, optional
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
