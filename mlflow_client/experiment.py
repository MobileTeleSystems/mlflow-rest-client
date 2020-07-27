from enum import Enum

from .tag import Tag

class ExperimentStage(Enum):
    active = 'ACTIVE'
    deleted = 'DELETED'

class ExperimentTag(Tag):
    pass


class Experiment(object):

    def __init__(self, name=None, id=None, artifact_location=None, stage=ExperimentStage.active, tags=None):
        self.name = name
        self.id = id
        self.artifact_location = artifact_location
        self.stage = ExperimentStage(stage)
        self.tags = ExperimentTag.from_list(tags or [])


    @classmethod
    def from_dict(cls, dct):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    id=dct.get('experiment_id') or dct.get('id'),
                    name=dct.get('name'),
                    artifact_location=dct.get('artifact_location'),
                    stage=(dct.get('lifecycle_stage') or dct.get('stage')).upper(),
                    tags=dct.get('tags')
                )


    @classmethod
    def from_list(cls, lst):
        """
        :param lst: REST API response list
        :type lst: list[dict]
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]


    def __repr__(self):
        return "<{self.__class__.__name__} id={self.id} name={self.name}>"\
                .format(self=self)


    def __str__(self):
        return self.name


    def __hash__(self):
        return hash(self.__str__())


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, str):
                other = self.__class__(name=other)
            elif isinstance(other, int):
                other = self.__class__(id=id)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
