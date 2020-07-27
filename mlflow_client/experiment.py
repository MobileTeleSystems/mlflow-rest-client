from enum import Enum

from .tag import Tag

class ExperimentStage(Enum):
    """ Experiment stage """
    active = 'ACTIVE'
    deleted = 'DELETED'

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


class Experiment(object):
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
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Experiment
        :rtype: Experiment
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
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Experiment
        :rtype: :obj:`list` of :obj:`Experiment`
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
