from enum import Enum

import six

from .tag import Tag
from .timestamp import timestamp_2_time
from .internal import \
    SearchableList, \
    Listable, \
    Comparable, \
    ComparableByStr, \
    MakeableFromTuple, \
    MakeableFromStr, \
    HashableByStr

class RunStage(Enum):
    """ Run stage """

    active = 'active'
    deleted = 'deleted'


class RunStatus(Enum):
    """ Run status """

    started = 'RUNNING'
    scheduled = 'SCHEDULED'
    finished = 'FINISHED'
    failed = 'FAILED'
    killed = 'KILLED'


class RunViewType(Enum):
    """ Run view type """

    active = 'ACTIVE_ONLY'
    deleted = 'DELETED_ONLY'
    all = 'ALL'


class RunInfo(Listable, MakeableFromStr, ComparableByStr, HashableByStr):
    """ Run information

        :param id: Run ID
        :type id: str

        :ivar id: Run ID
        :vartype id: str

        :param experiment_id: Experiment ID
        :type experiment_id: int

        :ivar experiment_id: Experiment ID
        :vartype experiment_id: int

        :param status: Run status
        :type status: str, optional

        :ivar status: Run status
        :vartype status: :obj:`RunStatus`

        :param stage: Run stage
        :type stage: str, optional

        :ivar stage: Run stage
        :vartype stage: :obj:`RunStage`

        :param start_time: Run start time
        :type start_time: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar start_time: Run start time
        :vartype start_time: :obj:`datetime.datetime`

        :param end_time: Run end time
        :type end_time: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar end_time: Run end time
        :vartype end_time: :obj:`datetime.datetime`

        :param artifact_uri: Artifact URL
        :type artifact_uri: str, optional

        :ivar artifact_uri: Artifact URL
        :vartype artifact_uri: str
    """

    def __init__(
        self,
        id,
        experiment_id=None,
        status=None,
        stage=None,
        start_time=None,
        end_time=None,
        artifact_uri=None
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
        self.artifact_uri = str(artifact_uri) if artifact_uri else ''


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    id=inp.get('run_id') or inp.get('run_uuid') or inp.get('id'),
                    experiment_id=inp.get('experiment_id'),
                    status=inp.get('status'),
                    stage=inp.get('lifecycle_stage') or inp.get('stage'),
                    start_time=inp.get('start_time'),
                    end_time=inp.get('end_time'),
                    artifact_uri=inp.get('artifact_uri')
                )


    def __repr__(self):
        return "<RunInfo id={self.id} experiment_id={self.experiment_id} status={self.status}>"\
                .format(self=self)


    def __str__(self):
        return self.id


class Param(Tag):
    """ Run param

        :param key: Param name
        :type key: str

        :ivar name: Param name
        :vartype name: str

        :param value: Param value
        :type value: str

        :ivar value: Param value
        :vartype value: str
    """
    pass


class MetricList(SearchableList):
    def __contains__(self, item):
        for it in self:
            try:
                if isinstance(it, Metric):
                    if isinstance(item, Metric) and it == item:
                        return True
                    if isinstance(item, six.string_types) and it.key == item:
                        return True
            except Exception:
                pass

        return super(MetricList, self).__contains__(item)


    def __getitem__(self, item):
        for it in self:
            try:
                if isinstance(it, Metric):
                    if isinstance(item, Metric) and it == item:
                        return it
                    if isinstance(item, six.string_types) and it.key == item:
                        return it
            except Exception:
                pass

        return super(MetricList, self).__getitem__(item)


class Metric(Listable, MakeableFromTuple, MakeableFromStr, ComparableByStr, HashableByStr):
    """ Run metric

        :param key: Metric name
        :type key: str

        :ivar key: Metric name
        :vartype key: str

        :param value: Metric value
        :type value: float

        :ivar value: Metric value
        :vartype value: float

        :param timestamp: Metric timestamp
        :type timestamp: :obj:`int` (UNIX timestamp) or :obj:`datetime.datetime`, optional

        :ivar timestamp: Metric timestamp
        :vartype timestamp: :obj:`datetime.datetime`

        :param step: Metric step
        :type step: int, optional

        :ivar step: Metric step
        :vartype step: int
    """

    list_class = MetricList

    def __init__(self, key, value=None, step=None, timestamp=None):
        self.key = str(key)
        self.value = float(value) if value is not None else None
        self.step = int(step) if step else 0
        self.timestamp = timestamp_2_time(timestamp)


    @classmethod
    def _from_dict(cls, inp):
        return cls(
                    key=inp.get('key'),
                    value=inp.get('value'),
                    step=inp.get('step'),
                    timestamp=inp.get('timestamp')
                )


    def __repr__(self):
        return "<Metric key={self.key} value={self.value} step={self.step} timestamp={self.timestamp}>"\
                .format(self=self)


    def __str__(self):
        return str("{self.key}: {self.value} for {self.step} at {self.timestamp}".format(self=self))


class RunTag(Tag):
    """ Run tag

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


class RunData(Listable, Comparable):
    """ Run params, metrics and tags

        :param params: Params list
        :type params: :obj:`list` of :obj:`dict`, optional

        :ivar params: Params list
        :vartype params: :obj:`dict` of :obj:`str`::obj:`Param`, optional

        :param metrics: Metrics list
        :type metrics: :obj:`list` of :obj:`dict`, optional

        :ivar metrics: Metrics list
        :vartype metrics: :obj:`dict` of :obj:`str`::obj:`Metric`, optional

        :param tags: Tags list
        :type tags: :obj:`list` of :obj:`dict`, optional

        :ivar tags: Tags list
        :vartype tags: :obj:`dict` of :obj:`str`::obj:`RunTag`, optional
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
        return cls(
                    params=inp.get('params'),
                    metrics=inp.get('metrics'),
                    tags=inp.get('tags')
                )


    def __repr__(self):
        return "<RunData params={self.params} metrics={self.metrics} tags={self.tags}>"\
                .format(self=self)


class Run(Listable, ComparableByStr, HashableByStr):
    """ Run

        :param info: Run info
        :type info: dict, optional

        :ivar info: Run info
        :vartype info: RunInfo

        :param data: Run data
        :type data: dict, optional

        :ivar data: Run data
        :vartype data: RunData
    """

    def __init__(self, info=None, data=None):
        self.info = RunInfo.make(info or {})
        self.data = RunData.make(data or {})


    def __repr__(self):
        return "<Run info={info} data={data}>"\
                .format(info=repr(self.info), data=repr(self.data))


    def __str__(self):
        return str(self.info)


    def __getattr__(self, attr):
        if hasattr(self.info, attr):
            return getattr(self.info, attr)
        if hasattr(self.data, attr):
            return getattr(self.data, attr)
        raise AttributeError("{} object has no attribute {}"\
                                .format(self.__class__.__name__, attr))
