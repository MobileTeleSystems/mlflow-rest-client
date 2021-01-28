from enum import Enum

from six import string_types

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


class RunStage(Enum):
    """ Run stage """

    active = "active"
    """ Run is active """

    deleted = "deleted"
    """ Run was deleted """


class RunStatus(Enum):
    """ Run status """

    started = "RUNNING"
    """ Run is running or created """

    scheduled = "SCHEDULED"
    """ Run is scheduled for run """

    finished = "FINISHED"
    """ Run was finished successfully """

    failed = "FAILED"
    """ Run is failed """

    killed = "KILLED"
    """ Run was killed """


class RunViewType(Enum):
    """ Run view type """

    active = "ACTIVE_ONLY"
    """ Show only active runs """

    deleted = "DELETED_ONLY"
    """ Show only deleted runs """

    all = "ALL"
    """ Show all runs """


class RunInfo(Listable, MakeableFromStr, ComparableByStr, HashableByStr):
    """Run information representation

    Parameters
    ----------
    id : str
        Run ID

    experiment_id : int, optional
        Experiment ID

    status : :obj:`str` or :obj:`RunStatus`, optional
        Run status

    stage : :obj:`str` or :obj:`RunStage`, optional
        Run stage

    start_time : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Run start time

    end_time : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Run end time

    artifact_uri : str, optional
        Artifact URL

    Attributes
    ----------
    id : :str
        Run ID

    experiment_id : int
        Experiment ID

    status : :obj:`RunStatus`
        Run status

    stage : :obj:`RunStage`
        Run stage

    start_time : :obj:`datetime.datetime`
        Run start time

    end_time : :obj:`datetime.datetime`
        Run end time

    artifact_uri : str
        Artifact URL

    Examples
    --------
    .. code:: python

        run_info = RunInfo("some_id")
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, id, experiment_id=None, status=None, stage=None, start_time=None, end_time=None, artifact_uri=None
    ):
        self.id = str(id)
        self.experiment_id = int(experiment_id) if experiment_id else None

        if status is None:
            status = RunStatus.started
        self.status = RunStatus(status)

        if stage is None:
            stage = RunStage.active
        self.stage = RunStage(stage)

        self.start_time = timestamp_2_time(start_time)
        self.end_time = timestamp_2_time(end_time)
        self.artifact_uri = str(artifact_uri) if artifact_uri else ""

    @classmethod
    def _from_dict(cls, inp):
        return cls(
            id=inp.get("run_id") or inp.get("run_uuid") or inp.get("id"),
            experiment_id=inp.get("experiment_id"),
            status=inp.get("status"),
            stage=inp.get("lifecycle_stage") or inp.get("stage"),
            start_time=inp.get("start_time"),
            end_time=inp.get("end_time"),
            artifact_uri=inp.get("artifact_uri"),
        )

    def __repr__(self):
        return "<RunInfo id={self.id} experiment_id={self.experiment_id} status={self.status}>".format(self=self)

    def __str__(self):
        return self.id


# pylint: disable=too-many-ancestors
class Param(Tag):
    """Run parameter

    Parameters
    ----------
    key : str
        Param name

    value : str
        Param value

    Attributes
    ----------
    key : str
        Param name

    value : str
        Param value
    """


class MetricList(SearchableList):
    """
    List of :obj:`Metric` with extended functions

    Parameters
    ----------
    iterable : Iterable
        Any iterable

    Examples
    --------
    .. code:: python

        name = "some_metric"
        value = 1.23
        item = Metric(name, value)

        simple_list = [item]
        this_list = Metric.from_list([item])  # or MetricList([item])

        assert item in simple_list
        assert item in this_list

        assert name not in simple_list
        assert name in this_list
        assert this_list[name] == item

        assert value not in simple_list
        assert value in this_list
        assert this_list[value] == item
    """

    def __contains__(self, item):
        for it in self:
            if isinstance(it, Metric):
                if isinstance(item, string_types) and it.key == item:
                    return True
                if isinstance(item, float) and it.value == item:
                    return True

        return super(MetricList, self).__contains__(item)

    def __getitem__(self, item):
        for it in self:
            if isinstance(it, Metric):
                if isinstance(item, string_types) and it.key == item:
                    return it
                if isinstance(item, float) and it.value == item:
                    return it

        return super(MetricList, self).__getitem__(item)


# pylint: disable=too-many-ancestors
class Metric(Listable, MakeableFromTupleStr, ComparableByStr, HashableByStr):
    """Run metric representation

    Parameters
    ----------
    name : str
        Metric name

    value : float, optional
        Metric value

    step : int, optional
        Metric step

    timestamp : :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional
        Metric timestamp

    Attributes
    ----------
    name : str
        Metric name

    value : float
        Metric value

    step : int
        Metric step

    timestamp : :obj:`datetime.datetime`
        Metric timestamp

    Examples
    --------
    .. code:: python

        metric = Metric(name="some.metric")
        metric = Metric(name="some.metric", value=1.23)
        metric = Metric(name="some.metric", value=1.23, step=2)
        metric = Metric(
            name="some.metric", value=1.23, step=2, timestamp=datetime.datetime.now()
        )
    """

    list_class = MetricList

    def __init__(self, key, value=None, step=None, timestamp=None):
        self.key = str(key)
        self.value = float(value) if value is not None else None
        self.step = int(step) if step else 0
        self.timestamp = timestamp_2_time(timestamp)

    @classmethod
    def _from_dict(cls, inp):
        return cls(key=inp.get("key"), value=inp.get("value"), step=inp.get("step"), timestamp=inp.get("timestamp"))

    def __repr__(self):
        return "<Metric key={self.key} value={self.value} step={self.step} timestamp={self.timestamp}>".format(
            self=self
        )

    def __str__(self):
        return str("{self.key}: {self.value} for {self.step} at {self.timestamp}".format(self=self))


# pylint: disable=too-many-ancestors
class RunTag(Tag):
    """Run tag

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

        tag = RunTag("some.tag", "some.val")
    """


class RunData(Listable, Comparable):
    """Run data representation

    Parameters
    ----------
    params : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Params list

    metrics : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Metrics list

    tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
        Run tags list

    Attributes
    ----------
    params : :obj:`ParamList`
        Params list

    metrics : :obj:`MetricList`
        Metrics list

    tags : :obj:`RunTagList`
        Run tags list

    Examples
    --------
    .. code:: python

        param = Param("some.param", "some_value")
        metric = Metric("some.metric", value=1.23)
        tag = RunTag("some.tag", "some.val")

        run_data = RunData(params=[param], metrics=[metric], tags=[tag])
    """

    def __init__(self, params=None, metrics=None, tags=None):
        self.params = Param.from_list(params or [])
        self.metrics = Metric.from_list(metrics or [])
        self.tags = RunTag.from_list(tags or [])

    @classmethod
    def make(cls, inp, **kwargs):
        if isinstance(inp, cls):
            return inp

        if isinstance(inp, dict):
            return cls.from_dict(inp, **kwargs)

        try:
            return cls.from_dict(vars(inp), **kwargs)
        except TypeError:
            return None

    @classmethod
    def _from_dict(cls, inp):
        return cls(params=inp.get("params"), metrics=inp.get("metrics"), tags=inp.get("tags"))

    def __repr__(self):
        return "<RunData params={self.params} metrics={self.metrics} tags={self.tags}>".format(self=self)


class Run(Listable, ComparableByStr, HashableByStr):
    """Run representation

    Parameters
    ----------
    info : :obj:`dict` or :obj:`RunInfo`
        Run info

    data : :obj:`dict` or :obj:`RunData`, optional
        Run data

    Attributes
    ----------
    info : :obj:`RunInfo`
        Run info

    data : :obj:`RunData`
        Run data

    Examples
    --------
    .. code:: python

        run_info = RunInfo("some_id")
        run_data = RunData(params=..., metrics=..., tags=...)

        run = Run(run_info, run_data)
    """

    def __init__(self, info=None, data=None):
        self.info = RunInfo.make(info or {})
        self.data = RunData.make(data or {})

    def __repr__(self):
        return "<Run info={info} data={data}>".format(info=repr(self.info), data=repr(self.data))

    def __str__(self):
        return str(self.info)

    def __getattr__(self, attr):
        if hasattr(self.info, attr):
            return getattr(self.info, attr)
        if hasattr(self.data, attr):
            return getattr(self.data, attr)
        raise AttributeError("{} object has no attribute {}".format(self.__class__.__name__, attr))
