from enum import Enum

from .tag import Tag

class ExperimentStage(Enum):
    active = 'ACTIVE'
    deleted = 'DELETED'

class ExperimentTag(Tag):
    pass


class Experiment(object):

    def __init__(self, id, name, artifact_location=None, stage=ExperimentStage.active, tags=None):
        self.id = int(id)
        self.name = str(name)
        self.artifact_location = str(artifact_location) if artifact_location else ''
        self.stage = ExperimentStage(stage)

        _tags = ExperimentTag.from_list(tags or [])
        self.tags = {tag.key: tag for tag in _tags}


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
                return other == self.__str__()
            elif isinstance(other, int):
                return other == self.id
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
