from enum import Enum

from .internal import (
    Comparable,
    ComparableByStr,
    HashableByStr,
    Listable,
    MakeableFromStr,
    MakeableFromTupleStr,
    SearchableList,
)
from .tag import Tag
from .timestamp import timestamp_2_time


# TODO: change names to UPPERCASE in 2.0
# pylint: disable=invalid-name
class ModelVersionStage(Enum):
    """Model version stage"""

    unknown = "None"

    """ Model version has no stage """

    test = "Staging"
    """ Is a testing model version"""

    prod = "Production"
    """ Is a production model version """

    archived = "Archived"
    """ Model version was archived """

    def __hash__(self):
        return hash(self.value)


# TODO: change names to UPPERCASE in 2.0
# pylint: disable=invalid-name
class ModelVersionState(Enum):
    """Model version stage"""

    pending = "PENDING_REGISTRATION"
    """ Model version registration is pending """

    failed = "FAILED_REGISTRATION"
    """ Model version registration was failed """

    ready = "READY"
    """ Model version registration was successful """

    def __hash__(self):
        return hash(self.value)


class ModelVersionStatus(Listable, MakeableFromTupleStr, ComparableByStr):
    """Model version state with message

    Parameters
    ----------
    state : :obj:`str` or :obj:`ModelVersionState`, optional
        Model version state

    message : str, optional
        Model version state message

    Attributes
    ----------
    state : :obj:`ModelVersionState`
        Model version state

    message : str
        Model version state message

    Examples
    --------
    .. code:: python

        status = ModelVersionStatus(state="READY")

        status = ModelVersionStatus(state=ModelVersionState.ready)

        status = ModelVersionStatus(state=ModelVersionState.failed, message="Reason")
    """

    def __init__(self, state=None, message=None, *args, **kwargs):
        super(ModelVersionStatus, self).__init__(*args, **kwargs)

        self.state = ModelVersionState(state) if state else ModelVersionState.pending
        """Model version state"""

        self.message = message or ""
        """Model version state message"""

    @classmethod
    def _from_dict(cls, inp):
        return cls(
            state=inp.get("state"),
            message=inp.get("message"),
        )

    def __repr__(self):
        return "<{self.__class__.__name__} state={self.state} message={self.message}>".format(self=self)

    def __str__(self):
        return str(self.state.name) + (" because of '{}'".format(self.message) if self.message else "")

    def __hash__(self):
        return hash(self.state.value)


# pylint: disable=too-many-ancestors
class ModelVersionTag(Tag):
    """Model version tag

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

        tag = ModelVersionTag("some.tag", "some.val")
    """


class ModelVersionList(SearchableList):
    """
    List of :obj:`ModelVersion` with extended functions

    Parameters
    ----------
    iterable : Iterable
        Any iterable

    Examples
    --------
    .. code:: python

        name = "some_metric"
        item = ModelVersion(name)

        simple_list = [item]
        this_list = ModelVersion.from_list([item])  # or ModelVersionList([item])

        assert item in simple_list
        assert item in this_list

        assert name not in simple_list
        assert name in this_list
        assert this_list[name] == item

        assert ModelVersionStage.test not in simple_list
        assert ModelVersionStage.prod in this_list
        assert this_list[ModelVersionStage.prod] == item
    """

    # pylint: disable=broad-except
    def __contains__(self, item):
        for it in self:
            try:
                if isinstance(it, ModelVersion):
                    if isinstance(item, ModelVersionStage) and it.stage == item:
                        return True
                    if it.stage == ModelVersionStage(item):
                        return True
            except Exception:  # nosec
                pass

        if isinstance(item, ModelVersionStage):
            return False

        return super(ModelVersionList, self).__contains__(item)

    # pylint: disable=broad-except
    def __getitem__(self, item):
        for it in self:
            try:
                if isinstance(it, ModelVersion):
                    if isinstance(item, ModelVersionStage) and it.stage == item:
                        return it
                    if it.stage == ModelVersionStage(item):
                        return it
            except Exception:  # nosec
                pass

        if isinstance(item, ModelVersionStage):
            raise KeyError("ModelVersion with stage {stage} not found".format(stage=item))

        return super(ModelVersionList, self).__getitem__(item)


# pylint: disable=too-many-ancestors
class ModelTag(Tag):
    """Model tag

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

        tag = ModelTag("some.tag", "some.val")
    """


# pylint: disable=too-many-instance-attributes
class ModelVersion(Listable, MakeableFromTupleStr, Comparable):
    """Model version representation

    Parameters
    ----------
    name : str
        Model name

    version : int
        Version number

    creation_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Version creation timestamp

    last_updated_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Version last update timestamp

    stage : :obj:`str` or :obj:`ModelVersionStage`, optional
        Version stage

    description : str, optional
        Version description

    source : str, optional
        Version source path

    run_id : str, optional
        Run ID used for generating version

    state : :obj:`str` or :obj:`ModelVersionState`, optional
        Version stage

    state_message : str, optional
        Version state message

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Experiment tags list

    Attributes
    ----------
    name : str
        Model name

    version : int
        Version number

    created_time : :obj:`datetime.datetime`
        Version creation timestamp

    updated_time : :obj:`datetime.datetime`
        Version last update timestamp

    stage : :obj:`ModelVersionStage`
        Version stage

    description : str
        Version description

    source : str
        Version source path

    run_id : str
        Run ID used for generating version

    status : :obj:`ModelVersionStatus`
        Version status

    tags : :obj:`ModelVersionTagList`
        Experiment tags list

    Examples
    --------
    .. code:: python

        model_version = ModelVersion(name="some_model", version=1)
    """

    list_class = ModelVersionList

    # pylint: disable=too-many-arguments
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
        tags=None,
    ):
        self.name = str(name)
        """Model name"""

        self.version = int(version)
        """Version number"""

        self.created_time = timestamp_2_time(creation_timestamp)
        """Version creation timestamp"""

        self.updated_time = timestamp_2_time(last_updated_timestamp)
        """Version last update timestamp"""

        if stage is None:
            stage = ModelVersionStage.unknown
        self.stage = ModelVersionStage(stage)
        """Version stage"""

        self.description = str(description) if description else ""
        """Version description"""

        self.source = str(source) if source else ""
        """Version source path"""

        self.run_id = str(run_id) if run_id else None
        """Run ID used for generating version"""

        self.status = ModelVersionStatus(state, state_message)
        """Version status"""

        self.tags = ModelVersionTag.from_list(tags or [])
        """Version tags list"""

    @classmethod
    def _from_dict(cls, inp):
        return cls(
            name=inp.get("name"),
            version=inp.get("version"),
            creation_timestamp=inp.get("creation_timestamp"),
            last_updated_timestamp=inp.get("last_updated_timestamp"),
            stage=inp.get("current_stage") or inp.get("stage"),
            description=inp.get("description"),
            source=inp.get("source"),
            run_id=inp.get("run_id"),
            state=inp.get("status") or inp.get("state"),
            state_message=inp.get("status_message") or inp.get("state_message"),
            tags=inp.get("tags"),
        )

    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name} version={self.version}>".format(self=self)

    def __str__(self):
        return str("{self.name} v{self.version}".format(self=self))


class Model(Listable, MakeableFromStr, ComparableByStr, HashableByStr):
    """Model representation

    Parameters
    ----------
    name : str
        Model name

    creation_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Model creation timestamp

    last_updated_timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Model last update timestamp

    description : str, optional
        Model description

    versions: :obj:`list` of :obj:`ModelVersion` or :obj:`list` of :obj:`dict`, optional
        Model latest versions

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Model tags list

    Attributes
    ----------
    name : str
        Model name

    created_time : :obj:`datetime.datetime`
        Model creation timestamp

    updated_time : :obj:`datetime.datetime`
        Model last update timestamp

    description : str
        Model description

    versions: :obj:`ModelVersionList`
        Model latest versions

    tags : :obj:`ModelTagList`
        Model tags list

    Examples
    --------
    .. code:: python

        model = Model(name="some_model")

        model = Model(name="some_model", versions=[ModelVersion("some_model", 1)])
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, name, creation_timestamp=None, last_updated_timestamp=None, description=None, versions=None, tags=None
    ):
        self.name = name
        self.created_time = timestamp_2_time(creation_timestamp)
        self.updated_time = timestamp_2_time(last_updated_timestamp)
        self.description = str(description) if description else ""
        self.versions = ModelVersion.from_list(versions or [], name=name)
        self.tags = ModelTag.from_list(tags or [])

    @classmethod
    def _from_dict(cls, inp):
        return cls(
            name=inp.get("name"),
            creation_timestamp=inp.get("creation_timestamp"),
            last_updated_timestamp=inp.get("last_updated_timestamp"),
            description=inp.get("description"),
            versions=inp.get("latest_versions") or inp.get("versions"),
            tags=inp.get("tags"),
        )

    def __repr__(self):
        return "<{self.__class__.__name__} name={self.name}>".format(self=self)

    def __str__(self):
        return str(self.name)
