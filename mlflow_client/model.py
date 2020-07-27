from enum import Enum

from .tag import Tag
from .time import timestamp_2_time

class ModelVersionStage(Enum):
    unknown = 'None'
    test = 'Staging'
    prod = 'Production'
    archived = 'Archived'

    def __hash__(self):
        return hash(self.value)


class ModelVersionState(Enum):
    pending = 'PENDING_REGISTRATION'
    failed = 'FAILED_REGISTRATION'
    ready = 'READY'

    def __hash__(self):
        return hash(self.value)


class ModelVersionStatus(object):

    def __init__(self, status, message=""):
        self.status = ModelVersionState(status)
        self.message = message


    def __repr__(self):
        return "<{self.__class__.__name__} status={self.status} message={self.message}>"\
                .format(self=self)


    def __str__(self):
        return str(self.status.name) + (" because of '{}'".format(self.message) if self.message else "")


    def __hash__(self):
        return hash(self.status.value)


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, str):
                return other == self.__str__()
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(status=other[0], message=other[1])
        return repr(self) == repr(other)


class ModelVersionTag(Tag):
    pass


class ModelTag(Tag):
    pass


class ModelVersion(object):

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
        :param dct: REST API response item
        :type dct: dict
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
        :param lst: REST API response list
        :type lst: list[dict]
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
        :param dct: REST API response item
        :type dct: dict
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
        :param lst: REST API response list
        :type lst: list[dict]
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
