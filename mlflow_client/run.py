import time

from enum import Enum

from .tag import Tag
from .time import timestamp_2_time

class RunStage(Enum):
    """ Run stage """

    active = 'ACTIVE'
    deleted = 'DELETED'


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


class RunInfo(object):
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

    def __init__(self, id, experiment_id=None, status=RunStatus.started, stage=RunStage.active, start_time=None, end_time=None, artifact_uri=None):
        self.id = str(id)
        self.experiment_id = int(experiment_id)
        self.status = RunStatus(status)
        self.stage = RunStage(stage)
        self.start_time = timestamp_2_time(start_time)
        self.end_time = timestamp_2_time(end_time)
        self.artifact_uri = str(artifact_uri) if artifact_uri else ''


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Run info
        :rtype: RunInfo
        """
        return cls(
                    id=dct.get('run_id') or dct.get('run_uuid') or dct.get('id'),
                    experiment_id=dct.get('experiment_id'),
                    status=dct.get('status'),
                    stage=(dct.get('lifecycle_stage') or dct.get('stage')).upper(),
                    start_time=dct.get('start_time'),
                    end_time=dct.get('end_time'),
                    artifact_uri=dct.get('artifact_uri')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Runs info
        :rtype: :obj:`list` of :obj:`RunInfo`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<RunInfo id={self.id} experiment_id={self.experiment_id} status={self.status}>"\
                .format(self=self)

    def __str__(self):
        return self.id


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


class Metric(object):
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

    def __init__(self, key, value=None, timestamp=None, step=None):
        self.key = str(key)
        self.value = float(value) if value is not None else None
        self.timestamp = timestamp_2_time(timestamp)
        self.step = int(step) if step else 0


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Metric
        :rtype: Metric
        """
        return cls(
                    key=dct.get('key'),
                    value=dct.get('value'),
                    timestamp=dct.get('timestamp'),
                    step=dct.get('step')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Metrics
        :rtype: :obj:`list` of :obj:`Metric`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<Metric key={self.key} value={self.value} step={self.step} timestamp={self.timestamp}>"\
                .format(self=self)


    def __str__(self):
        return str("{self.key}: {self.value} for {self.step} at {self.timestamp}".format(self=self))


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
            elif isinstance(other, tuple) and len(other) == 4:
                other = self.__class__(key=other[0], value=other[1], step=other[2], timestamp=other[3])
            elif isinstance(other, tuple) and len(other) == 3:
                other = self.__class__(key=other[0], value=other[1], step=other[2])
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(key=other[0], value=other[1])
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)


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


class RunData(object):
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
        _params = Param.from_list(params or [])
        self.params = {param.key: param for param in _params}

        _metrics = Metric.from_list(metrics or [])
        self.metrics = {metric.key: metric for metric in _metrics}

        _tags = RunTag.from_list(tags or [])
        self.tags = {tag.key: tag for tag in _tags}

    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Run data
        :rtype: RunData
        """
        return cls(
                    params=dct.get('params'),
                    metrics=dct.get('metrics'),
                    tags=dct.get('tags')
                )

    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Runs data
        :rtype: :obj:`list` of :obj:`RunData`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<RunData params={self.params} metrics={self.metrics} tags={self.tags}>"\
                .format(self=self)


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)

class Run(object):
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
        self.info = RunInfo.from_dict(info or {})
        self.data = RunData.from_dict(data or {})


    @classmethod
    def from_dict(cls, dct):
        """
        Generate object from REST API response

        :param dct: Response item
        :type dct: dict`

        :returns: Run
        :rtype: Run
        """
        return cls(
                    info=dct.get('info'),
                    data=dct.get('data')
                )


    @classmethod
    def from_list(cls, lst):
        """
        Generate objects list from REST API response

        :param lst: Response items
        :type lst: :obj:`list` of :obj:`dict`

        :returns: Runs
        :rtype: :obj:`list` of :obj:`Run`
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<Run info={info} data={data}>"\
                .format(info=repr(self.info), data=repr(self.data))


    def __str__(self):
        return str(self.info.id)


    def __hash__(self):
        return hash(self.__str__())


    def __getattr__(self, attr):
        if hasattr(self.info, attr):
            return getattr(self.info, attr)
        if hasattr(self.data, attr):
            return getattr(self.data, attr)
        getattr(self, attr)


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, str):
                return other == str(self.info)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
