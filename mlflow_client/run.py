import time

from enum import Enum

from .tag import Tag
from .time import timestamp_2_time

class RunStage(Enum):
    active = 'ACTIVE'
    deleted = 'DELETED'


class RunStatus(Enum):
    started = 'RUNNING'
    scheduled = 'SCHEDULED'
    finished = 'FINISHED'
    failed = 'FAILED'
    killed = 'KILLED'


class RunViewType(Enum):
    active = 'ACTIVE_ONLY'
    deleted = 'DELETED_ONLY'
    all = 'ALL'


class RunInfo(object):

    def __init__(self, id, experiment_id=None, status=RunStatus.started, stage=RunStage.active, start_time=None, artifact_uri=''):
        self.id = id
        self.experiment_id = experiment_id
        self.status = RunStatus(status)
        self.stage = RunStage(stage)
        self.start_time = timestamp_2_time(start_time)
        self.artifact_uri = artifact_uri


    @classmethod
    def from_dict(cls, dct):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    id=dct.get('run_id') or dct.get('run_uuid') or  dct.get('id'),
                    experiment_id=dct.get('experiment_id'),
                    status=dct.get('status'),
                    stage=(dct.get('lifecycle_stage') or dct.get('stage')).upper(),
                    start_time=dct.get('start_time'),
                    artifact_uri=dct.get('artifact_uri', '')
                )


    @classmethod
    def from_list(cls, lst):
        """
        :param lst: REST API response list
        :type lst: list[dict]
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<RunInfo id={self.id} experiment_id={self.experiment_id} status={self.status}>"\
                .format(self=self)

    def __str__(self):
        return str(self.id)


    def __hash__(self):
        return hash(self.__str__())


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            elif isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, str):
                other = self.__class__(other)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)


class Param(Tag):
    pass


class Metric(object):

    def __init__(self, key, value, timestamp=None):
        self.key = key
        self.value = value
        self.timestamp = timestamp_2_time(timestamp)


    @classmethod
    def from_dict(cls, dct):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    key=dct.get('key'),
                    value=dct.get('value'),
                    timestamp=dct.get('timestamp')
                )

    @classmethod
    def from_list(cls, lst):
        """
        :param lst: REST API response list
        :type lst: list[dict]
        """
        return [cls.from_dict(item) if isinstance(item, dict) else item for item in lst]

    def __repr__(self):
        return "<Metric key={self.key} value={self.value} timestamp={self.timestamp}>"\
                .format(self=self)

    def __str__(self):
        return str("{self.key}: {self.value} at {self.timestamp}".format(self=self))


    def __hash__(self):
        return hash(self.__str__())


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            if isinstance(other, list):
                other = self.from_list(other)
            elif isinstance(other, tuple) and len(other) == 3:
                other = self.__class__(key=other[0], value=other[1], timestamp=other[2])
            elif isinstance(other, tuple) and len(other) == 2:
                other = self.__class__(key=other[0], value=other[1])
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)


class RunTag(Tag):
    pass


class RunData(object):

    def __init__(self, params=None, metrics=None, tags=None):
        self.params = Param.from_list(params or [])
        self.metrics = Metric.from_list(metrics or [])
        self.tags = RunTag.from_list(tags or [])

    @classmethod
    def from_dict(cls, dct):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    params=dct.get('params'),
                    metrics=dct.get('metrics'),
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
        return "<RunData params={self.params} metrics={self.metrics} tags={self.tags}>"\
                .format(self=self)


    def __eq__(self, other):
        if other is not None and not isinstance(other, self.__class__):
            if isinstance(other, dict):
                other = self.from_dict(other)
            if isinstance(other, list):
                other = self.from_list(other)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)

class Run(object):

    def __init__(self, info=None, data=None):
        self.info = RunInfo.from_dict(info or {})
        self.data = RunData.from_dict(data or {})


    @classmethod
    def from_dict(cls, dct):
        """
        :param dct: REST API response item
        :type dct: dict
        """
        return cls(
                    info=dct.get('info'),
                    data=dct.get('data')
                )


    @classmethod
    def from_list(cls, lst):
        """
        :param lst: REST API response list
        :type lst: list[dict]
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
            if isinstance(other, list):
                other = self.from_list(other)
            else:
                other = self.from_dict(vars(other))
        return repr(self) == repr(other)
