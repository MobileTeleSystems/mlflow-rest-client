from enum import Enum

from .tag import Tag
from .timestamp import timestamp_2_time
from .internal import \
    SearchableList, \
    Listable, \
    MakeableFromStr, \
    MakeableFromTupleStr, \
    Comparable, \
    ComparableByStr, \
    HashableByStr

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


class ModelVersionStatus(Listable, MakeableFromTupleStr, ComparableByStr):
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

    def __init__(self, state=None, message=None, *args, **kwargs):
        super(ModelVersionStatus, self).__init__(*args, **kwargs)

        self.state = ModelVersionState(state) if state else ModelVersionState.pending
        self.message = message or ""


    @classmethod
    def _from_dict(cls, inp):
        return cls(
            state=inp.get('state'),
            message=inp.get('message'),
        )


    def __repr__(self):
        return "<{self.__class__.__name__} state={self.state} message={self.message}>"\
                .format(self=self)


    def __str__(self):
        return str(self.state.name) + (" because of '{}'".format(self.message) if self.message else "")


    def __hash__(self):
        return hash(self.state.value)


class ModelVersionTag(Tag):
    """ Model version tag """
    pass


class ModelVersionList(SearchableList):
    def __contains__(self, item):
        for it in self:
            try:
                if isinstance(it, ModelVersion):
                    if isinstance(item, ModelVersionStage) and it.stage == item:
                        return True
                    if it.stage == ModelVersionStage(item):
                        return True
            except Exception:
                pass

        return super(ModelVersionList, self).__contains__(item)


    def __getitem__(self, item):
        for it in self:
            try:
                if isinstance(it, ModelVersion):
                    if isinstance(item, ModelVersionStage) and it.stage == item:
                        return it
                    if it.stage == ModelVersionStage(item):
                        return it
            except Exception:
                pass

        return super(ModelVersionList, self).__getitem__(item)


class ModelTag(Tag):
    """ Model tag """
    pass


class ModelVersion(Listable, MakeableFromTupleStr, Comparable):
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

    list_class = ModelVersionList

    def __init__(
        self,
        name,
        version,
        creation_timestamp=None,
        last_updated_timestamp=None,
        stage=None,
        description=None,
        source=None,
        run_id=None,
        state=None,
        state_message=None,
        tags=None
    ):
        self.name = str(name)
        self.version = int(version)
        self.created_time = timestamp_2_time(creation_timestamp)
        self.updated_time = timestamp_2_time(last_updated_timestamp)

        if stage is None:
            stage = ModelVersionStage.unknown
        self.stage = ModelVersionStage(stage)

        self.description = str(description) if description else ''
        self.source = str(source) if source else ''
        self.run_id = str(run_id) if run_id else None
        self.status = ModelVersionStatus(state, state_message)
        self.tags = ModelVersionTag.from_list(tags or [])


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    name=inp.get('name'),
                    version=inp.get('version'),
                    creation_timestamp=inp.get('creation_timestamp'),
                    last_updated_timestamp=inp.get('last_updated_timestamp'),
                    stage=inp.get('current_stage') or inp.get('stage'),
                    description=inp.get('description'),
                    source=inp.get('source'),
                    run_id=inp.get('run_id'),
                    state=inp.get('status') or inp.get('state'),
                    state_message=inp.get('status_message') or inp.get('state_message'),
                    tags=inp.get('tags')
                )


    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name} version={self.version}>" \
                .format(self=self)


    def __str__(self):
        return str("{self.name} v{self.version}".format(self=self))


class Model(Listable, MakeableFromStr, ComparableByStr, HashableByStr):
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
        self.versions = ModelVersion.from_list(versions or [], name=name)
        self.tags = ModelTag.from_list(tags or [])


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    name=inp.get('name'),
                    creation_timestamp=inp.get('creation_timestamp'),
                    last_updated_timestamp=inp.get('last_updated_timestamp'),
                    description=inp.get('description'),
                    versions=inp.get('latest_versions') or inp.get('versions'),
                    tags=inp.get('tags')
                )


    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name}>" \
                .format(self=self)


    def __str__(self):
        return str(self.name)
