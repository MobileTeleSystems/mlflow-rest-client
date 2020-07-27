from enum import Enum

from .tag import Tag
from .time import timestamp_2_time

class ModelVersionStage(Enum):
    """ Model version stage """
    unknown = 'None'
    test = 'Staging'
    prod = 'Production'
    archived = 'Archived'

    def __hash__(self):
        return hash(self.value)


class ModelVersionState(Enum):
    """ Model version stage """
    pending = 'PENDING_REGISTRATION'
    failed = 'FAILED_REGISTRATION'
    ready = 'READY'

    def __hash__(self):
        return hash(self.value)


class ModelVersionStatus(object):
    """ Model version state with message

        :param state: Model version state
        :type state: str

        :ivar state: Model version state
        :vartype state: ModelVersionState

        :param message: Model version state message
        :type message: str, optional

        :ivar message: Model version state message
        :vartype message: str
    """

    def __init__(self, state, message=""):
        self.state = ModelVersionState(state)
        self.message = message


    def __repr__(self):
        return "<{self.__class__.__name__} state={self.state} message={self.message}>"\
                .format(self=self)


    def __str__(self):
        return str(self.state.name) + (" because of '{}'".format(self.message) if self.message else "")


    def __hash__(self):
        return hash(self.state.value)


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, str):
                return other == self.__str__()
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(state=other[0], message=other[1])
        return repr(self) == repr(other)


class ModelVersionTag(Tag):
    """ Model version tag """
    pass


class ModelTag(Tag):
    """ Model tag """
    pass


class ModelVersion(object):
    """ Model version

        :param name: Model name
        :type name: str

        :ivar name: Model name
        :vartype name: str

        :param version: Version number
        :type version: int

        :ivar version: Version number
        :vartype version: int

        :param creation_timestamp: Version creation timestamp
        :type creation_timestamp: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar creation_timestamp: Version creation timestamp
        :vartype creation_timestamp: :obj:`datetime.datetime`

        :param last_updated_timestamp: Version last update timestamp
        :type last_updated_timestamp: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar last_updated_timestamp: Version last update timestamp
        :vartype last_updated_timestamp: :obj:`datetime.datetime`

        :param stage: Version stage
        :type stage: str, optional

        :ivar stage:  Version stage
        :vartype stage: :obj:`ModelVersionStage`

        :param description: Version description
        :type description: str, optional

        :ivar description:  Version description
        :vartype description: str

        :param source: Version source path
        :type source: str, optional

        :ivar source: Version source path
        :vartype source: str

        :param run_id: Run ID used for generating version
        :type run_id: str, optional

        :ivar run_id: Run ID used for generating version
        :vartype run_id: str

        :param state: Version state
        :type state: str, optional

        :param state_message: Version stage message
        :type state_message: str, optional

        :ivar status: Version status
        :vartype status: :obj:`ModelVersionStatus`

        :param tags: Tags list
        :type tags: :obj:`list` of :obj:`dict`, optional

        :ivar tags: Tags list
        :vartype tags: :obj:`dict` of :obj:`str`::obj:`ModelVersionTag`, optional
    """

    def __init__(
        self,
        name,
        version,
        creation_timestamp=None,
        last_updated_timestamp=None,
        stage=ModelVersionStage.unknown,
        description=None,
        source=None,
        run_id=None,
        state=ModelVersionState.pending,
        state_message=None,
        tags=None
    ):
        self.name = str(name)
        self.version = int(version)
        self.created_time = timestamp_2_time(creation_timestamp)
        self.updated_time = timestamp_2_time(last_updated_timestamp)
        self.stage = ModelVersionStage(stage)
        self.description = str(description) if description else ''
        self.source = str(source) if source else ''
        self.run_id = str(run_id) if run_id else None
        self.status = ModelVersionStatus(state, state_message)

        _tags = ModelVersionTag.from_list(tags or [])
        self.tags = {tag.key: tag for tag in _tags}


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: ModelVersion
        :rtype: ModelVersion
        """
        return cls(
                    name=dct.get('name'),
                    version=dct.get('version'),
                    creation_timestamp=dct.get('creation_timestamp'),
                    last_updated_timestamp=dct.get('last_updated_timestamp'),
                    stage=dct.get('current_stage') or dct.get('stage'),
                    description=dct.get('description'),
                    source=dct.get('source'),
                    run_id=dct.get('run_id'),
                    state=dct.get('status', dct.get('state')).upper(),
                    state_message=dct.get('status_message') or dct.get('state_message'),
                    tags=dct.get('tags')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: ModelVersion
        :rtype: :obj:`list` of :obj:`ModelVersion`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]


    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name} version={self.version}>" \
                .format(self=self)


    def __str__(self):
        return str("{self.name} v{self.version}".format(self=self))


    def __hash__(self):
        return hash(self.__str__())


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(name=other[0], version=other[1])
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)

class Model(object):
    """ Model

        :param name: Model name
        :type name: str

        :ivar name: Model name
        :vartype name: str

        :param creation_timestamp: Model creation timestamp
        :type creation_timestamp: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar creation_timestamp: Model creation timestamp
        :vartype creation_timestamp: :obj:`datetime.datetime`

        :param last_updated_timestamp: Model last update timestamp
        :type last_updated_timestamp: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar last_updated_timestamp: Model last update timestamp
        :vartype last_updated_timestamp: :obj:`datetime.datetime`

        :param description: Model description
        :type description: str, optional

        :ivar description: Model description
        :vartype description: str

        :param versions: Model latest versions
        :type versions: :obj:`list` of :obj:`ModelVersion`, optional

        :ivar versions: Model latest versions
        :vartype versions: :obj:`dict` of :obj:`ModelVersionStage`::obj:`ModelVersion`, optional

        :param tags: Tags list
        :type tags: :obj:`list` of :obj:`ModelTag`, optional

        :ivar tags: Tags list
        :vartype tags: :obj:`dict` of :obj:`str`::obj:`ModelTag`, optional
    """

    def __init__(self, name, creation_timestamp=None, last_updated_timestamp=None, description=None, versions=None, tags=None):
        self.name = name
        self.created_time = timestamp_2_time(creation_timestamp)
        self.updated_time = timestamp_2_time(last_updated_timestamp)
        self.description = str(description) if description else ''

        _versions = ModelVersion.from_list(versions or [])
        self.versions = {version.stage: version for version in _versions}

        _tags = ModelTag.from_list(tags or [])
        self.tags = {tag.key: tag for tag in _tags}


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Model
        :rtype: Model
        """
        return cls(
                    name=dct.get('name'),
                    creation_timestamp=dct.get('creation_timestamp'),
                    last_updated_timestamp=dct.get('last_updated_timestamp'),
                    description=dct.get('description'),
                    versions=dct.get('latest_versions') or dct.get('versions'),
                    tags=dct.get('tags')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Model
        :rtype: :obj:`list` of :obj:`Model`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]


    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name}>" \
                .format(self=self)


    def __str__(self):
        return str(self.name)


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
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
