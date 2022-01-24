from __future__ import annotations

import logging
from typing import List
from uuid import uuid4

import pytest
from pydantic import parse_obj_as

from mlflow_client.internal import ListableTag
from mlflow_client.run import (
    ListableMetric,
    ListableParam,
    ListableRunInfo,
    Metric,
    Param,
    Run,
    RunData,
    RunInfo,
    RunStage,
    RunStatus,
    RunTag,
)

from .conftest import DEFAULT_TIMEOUT, now, rand_float, rand_int, rand_str

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.id == id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_with_experiment_id():
    id = uuid4()
    experiment_id = rand_int()

    run_info = RunInfo(id=id, experiment_id=experiment_id)

    assert run_info.experiment_id == experiment_id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_experiment_id():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.experiment_id is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "status",
    [
        RunStatus.SCHEDULED,
        RunStatus.STARTED,
        RunStatus.FINISHED,
        RunStatus.FAILED,
        RunStatus.KILLED,
    ],
)
def test_run_info_with_status(status):
    id = uuid4()

    run_info = RunInfo(id=id, status=status)

    assert run_info.status == status


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_status():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.status == RunStatus.STARTED


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [RunStage.ACTIVE, RunStage.DELETED])
def test_run_info_with_stage(stage):
    id = uuid4()

    run_info = RunInfo(id=id, stage=stage)

    assert run_info.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_stage():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.stage == RunStage.ACTIVE


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_with_start_time():
    id = uuid4()
    start_time = now()

    run_info = RunInfo(id=id, start_time=start_time)

    assert run_info.start_time == start_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_start_time():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.start_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_with_end_time():
    id = uuid4()
    end_time = now()

    run_info = RunInfo(id=id, end_time=end_time)

    assert run_info.end_time == end_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_end_time():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.end_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_with_artifact_uri():
    id = uuid4()
    artifact_uri = rand_str()

    run_info = RunInfo(id=id, artifact_uri=artifact_uri)

    assert run_info.artifact_uri == artifact_uri


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_without_artifact_uri():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.artifact_uri == ""


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_str():
    id = uuid4()

    run_info = RunInfo(id=id)

    assert run_info.id == id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_dict():
    dct = {"run_id": uuid4()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.id == dct["run_id"]

    dct = {"run_uuid": uuid4()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.id == dct["run_uuid"]

    dct = {"id": uuid4()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.id == dct["id"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_dict_with_experiment_id():
    dct = {"id": uuid4(), "experiment_id": rand_int()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.experiment_id == dct["experiment_id"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "status",
    [
        RunStatus.SCHEDULED,
        RunStatus.STARTED,
        RunStatus.FINISHED,
        RunStatus.FAILED,
        RunStatus.KILLED,
    ],
)
def test_run_info_make_dict_with_status(status):
    dct = {"id": uuid4(), "status": status.value}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.status == status


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [RunStage.ACTIVE, RunStage.DELETED])
def test_run_info_make_dict_with_stage(stage):
    dct = {"id": uuid4(), "lifecycle_stage": stage.value}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.stage == stage

    dct = {"id": uuid4(), "stage": stage.value}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_dict_with_start_time():
    dct = {"id": uuid4(), "start_time": now()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.start_time == dct["start_time"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_dict_with_end_time():
    dct = {"id": uuid4(), "end_time": now()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.end_time == dct["end_time"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_make_dict_with_artifact_uri():
    dct = {"id": uuid4(), "artifact_uri": rand_str()}

    run_info = parse_obj_as(RunInfo, dct)

    assert run_info.artifact_uri == dct["artifact_uri"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_eq():
    id1 = uuid4()
    id2 = uuid4()

    assert RunInfo(id=id1) == RunInfo(id=id1)
    assert RunInfo(id=id1) != RunInfo(id=id2)

    experiment_id1 = rand_int()
    experiment_id2 = rand_int()

    assert RunInfo(id=id1, experiment_id=experiment_id1) == RunInfo(id=id1, experiment_id=experiment_id1)
    assert RunInfo(id=id1, experiment_id=experiment_id1) != RunInfo(id=id1, experiment_id=experiment_id2)

    assert RunInfo(id=id1, experiment_id=experiment_id1) != RunInfo(id=id2, experiment_id=experiment_id1)
    assert RunInfo(id=id1, experiment_id=experiment_id1) != RunInfo(id=id2, experiment_id=experiment_id2)

    status1 = RunStatus.SCHEDULED
    status2 = RunStatus.KILLED

    assert RunInfo(id=id1, status=status1) == RunInfo(id=id1, status=status1)
    assert RunInfo(id=id1, status=status1) != RunInfo(id=id1, status=status2)

    assert RunInfo(id=id1, status=status1) != RunInfo(id=id2, status=status1)
    assert RunInfo(id=id1, status=status1) != RunInfo(id=id2, status=status2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_in():
    id1 = uuid4()
    id2 = uuid4()

    run1 = RunInfo(id=id1)
    run2 = RunInfo(id=id2)

    lst = parse_obj_as(List[RunInfo], [run1])

    assert run1 in lst
    assert run2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_in_by_id():
    id1 = uuid4()
    id2 = uuid4()

    run1 = RunInfo(id=id1)

    lst = parse_obj_as(ListableRunInfo, [run1])

    assert id1 in lst
    assert str(id1) in lst
    assert id1.hex in lst

    assert id2 not in lst
    assert str(id2) not in lst
    assert id2.hex not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_info_get_item_by_id():
    id1 = uuid4()
    id2 = uuid4()

    run1 = RunInfo(id=id1)

    lst = parse_obj_as(ListableRunInfo, [run1])

    assert lst[id1] == run1
    assert lst[str(id1)] == run1
    assert lst[id1.hex] == run1

    with pytest.raises(KeyError):
        lst[id2]

    with pytest.raises(KeyError):
        lst[str(id2)]

    with pytest.raises(KeyError):
        lst[id2.hex]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric():
    key = rand_str()

    metric = Metric(key=key)

    assert metric.key == key


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_with_value():
    key = rand_str()
    value = rand_float()

    metric = Metric(key=key, value=value)

    assert metric.value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_without_value():
    key = rand_str()

    metric = Metric(key=key)

    assert metric.value is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_with_step():
    key = rand_str()
    step = rand_int()

    metric = Metric(key=key, step=step)

    assert metric.step == step


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_without_step():
    key = rand_str()

    metric = Metric(key=key)

    assert metric.step == 0


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_with_timestamp():
    key = rand_str()
    timestamp = now()

    metric = Metric(key=key, timestamp=timestamp)

    assert metric.timestamp == timestamp


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_without_timestamp():
    key = rand_str()

    metric = Metric(key=key)

    assert metric.timestamp is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_str():
    key = rand_str()

    metric = Metric(key=key)

    assert metric.key == key


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_tuple():
    key = rand_str()
    value = rand_float()
    step = rand_int()
    timestamp = now()

    metric = Metric(key=key, value=value)
    assert metric.value == value

    metric = Metric(key=key, value=value, step=step)
    assert metric.value == value
    assert metric.step == step

    metric = Metric(key=key, value=value, step=step, timestamp=timestamp)
    assert metric.value == value
    assert metric.step == step
    assert metric.timestamp == timestamp


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_dict():
    dct = {"key": rand_str()}

    metric = parse_obj_as(Metric, dct)

    assert metric.key == dct["key"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_dict_with_value():
    dct = {"key": rand_str(), "value": rand_float()}

    metric = parse_obj_as(Metric, dct)

    assert metric.value == dct["value"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_dict_with_step():
    dct = {"key": rand_str(), "step": rand_int()}

    metric = parse_obj_as(Metric, dct)

    assert metric.step == dct["step"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_make_dict_with_timestamp():
    dct = {"key": rand_str(), "timestamp": now()}

    metric = parse_obj_as(Metric, dct)

    assert metric.timestamp == dct["timestamp"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_str():
    key = rand_str()
    value = rand_float()
    step = rand_int()
    timestamp = now()

    metric = Metric(key=key, value=value, step=step, timestamp=timestamp)

    assert str(metric)
    assert str(metric) == f"{key}: {value} for {step} at {timestamp}"


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_eq():
    key1 = rand_str()
    key2 = rand_str()

    assert Metric(key=key1) == Metric(key=key1)
    assert Metric(key=key1) != Metric(key=key2)

    value1 = rand_float()
    value2 = rand_float()

    assert Metric(key=key1, value=value1) == Metric(key=key1, value=value1)
    assert Metric(key=key1, value=value1) != Metric(key=key1, value=value2)

    assert Metric(key=key1, value=value1) != Metric(key=key2, value=value1)
    assert Metric(key=key1, value=value1) != Metric(key=key2, value=value2)

    step1 = rand_int()
    step2 = rand_int()

    assert Metric(key=key1, step=step1) == Metric(key=key1, step=step1)
    assert Metric(key=key1, step=step1) != Metric(key=key1, step=step2)

    assert Metric(key=key1, step=step1) != Metric(key=key2, step=step1)
    assert Metric(key=key1, step=step1) != Metric(key=key2, step=step2)

    timestamp1 = rand_float()
    timestamp2 = rand_float()

    assert Metric(key=key1, timestamp=timestamp1) == Metric(key=key1, timestamp=timestamp1)
    assert Metric(key=key1, timestamp=timestamp1) != Metric(key=key1, timestamp=timestamp2)

    assert Metric(key=key1, timestamp=timestamp1) != Metric(key=key2, timestamp=timestamp1)
    assert Metric(key=key1, timestamp=timestamp1) != Metric(key=key2, timestamp=timestamp2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_in():
    key1 = rand_str()
    key2 = rand_str()

    metric1 = Metric(key=key1)
    metric2 = Metric(key=key2)

    lst = parse_obj_as(ListableMetric, [metric1])

    assert metric1 in lst
    assert metric2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_in_by_key():
    key1 = rand_str()
    key2 = rand_str()

    metric1 = Metric(key=key1)

    lst = parse_obj_as(ListableMetric, [metric1])

    assert key1 in lst
    assert key2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_metric_get_item_by_key():
    key1 = rand_str()
    key2 = rand_str()

    metric1 = Metric(key=key1)

    lst = parse_obj_as(ListableMetric, [metric1])

    assert lst[key1] == metric1

    with pytest.raises(KeyError):
        lst[key2]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_with_params():
    param = Param(key=rand_str())

    run_data = RunData(params=[param])

    assert run_data.params == parse_obj_as(ListableParam, [param])


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_without_params():
    run_data = RunData()

    assert not run_data.params


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_with_metrics():
    metric = Metric(key=rand_str())

    run_data = RunData(metrics=[metric])

    assert run_data.metrics == parse_obj_as(ListableMetric, [metric])


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_without_metrics():
    run_data = RunData()

    assert not run_data.metrics


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_with_tags():
    key = rand_str()
    value = rand_str()
    tags = {key: value}

    run_data = RunData(tags=[tags])

    assert run_data.tags
    assert key in run_data.tags
    assert run_data.tags[key] == RunTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_without_tags():
    run_data = RunData()

    assert not run_data.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_eq():
    param1 = Param(key=rand_str())
    param2 = Param(key=rand_str())

    assert RunData(params=[param1]) == RunData(params=[param1])
    assert RunData(params=[param1]) != RunData(params=[param2])

    metric1 = Metric(key=rand_str())
    metric2 = Metric(key=rand_str())

    assert RunData(metrics=[metric1]) == RunData(metrics=[metric1])
    assert RunData(metrics=[metric1]) != RunData(metrics=[metric2])

    tag1 = RunTag(key=rand_str())
    tag2 = RunTag(key=rand_str())

    assert RunData(tags=[tag1]) == RunData(tags=[tag1])
    assert RunData(tags=[tag1]) != RunData(tags=[tag2])


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_param_in():
    param = Param(key=rand_str())

    run_data = RunData(params=[param])

    assert param in run_data.params


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_param_by_name():
    name = rand_str()
    param = Param(key=name)

    run_data = RunData(params=[param])

    assert name in run_data.params


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_param_get_item_by_name():
    name = rand_str()
    param = Param(key=name)

    run_data = RunData(params=[param])

    assert run_data.params[name] == param


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_metric_in():
    metric = Metric(key=rand_str())

    run_data = RunData(metrics=[metric])

    assert metric in run_data.metrics


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_metric_by_name():
    name = rand_str()
    metric = Metric(key=name)

    run_data = RunData(metrics=[metric])

    assert name in run_data.metrics


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_metric_get_item_by_name():
    name = rand_str()
    metric = Metric(key=name)

    run_data = RunData(metrics=[metric])

    assert run_data.metrics[name] == metric


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_data_tag_by_name():
    name = rand_str()
    tag = RunTag(key=name)

    run_data = RunData(tags=[tag])

    assert name in run_data.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run():
    id = uuid4()
    run_info = RunInfo(id=id)
    run_data = RunData()

    run = Run(info=run_info, data=run_data)

    assert run.info == run_info
    assert run.data == run_data


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_make_dict():
    id = uuid4()
    run_info = RunInfo(id=id)
    run_data = RunData()

    dct = {"info": run_info, "data": run_data}

    run = parse_obj_as(Run, dct)

    assert run.info == run_info
    assert run.data == run_data


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_str():
    id = uuid4()
    run_info = RunInfo(id=id)
    run = Run(info=run_info)

    assert str(run)
    assert str(run) == str(run_info)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_eq():
    id1 = uuid4()
    id2 = uuid4()

    run_info1 = RunInfo(id=id1)
    run_info2 = RunInfo(id=id2)

    param1 = Param(key=rand_str())
    param2 = Param(key=rand_str())

    metric1 = Metric(key=rand_str())
    metric2 = Metric(key=rand_str())

    run_tag1 = RunTag(key=rand_str())
    run_tag2 = RunTag(key=rand_str())

    run_data1 = RunData(params=[param1], metrics=[metric1], tags=[run_tag1])
    run_data2 = RunData(params=[param2], metrics=[metric2], tags=[run_tag2])

    assert Run(info=run_info1, data=run_data1) == Run(info=run_info1, data=run_data1)
    assert Run(info=run_info1, data=run_data1) == Run(info=run_info1, data=run_data2)
    assert Run(info=run_info1, data=run_data1) != Run(info=run_info2, data=run_data1)
    assert Run(info=run_info1, data=run_data1) != Run(info=run_info2, data=run_data2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_get_attr():
    id = uuid4()
    run_info = RunInfo(id=id)

    param = Param(key=rand_str())
    metric = Metric(key=rand_str())
    run_tag = RunTag(key=rand_str())

    run_data = RunData(params=[param], metrics=[metric], tags=[run_tag])

    run = Run(info=run_info, data=run_data)

    assert run.id == id
    assert run.experiment_id is None
    assert run.status == RunStatus.STARTED
    assert run.params == parse_obj_as(ListableParam, [param])
    assert run.metrics == parse_obj_as(ListableMetric, [metric])
    assert run.tags == parse_obj_as(ListableTag, [run_tag])

    with pytest.raises(AttributeError):
        run.unknown


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_run_in():
    id1 = uuid4()
    id2 = uuid4()

    run_info1 = RunInfo(id=id1)
    run_info2 = RunInfo(id=id2)

    run1 = Run(info=run_info1)
    run2 = Run(info=run_info2)

    lst = parse_obj_as(List[Run], [run1])

    assert run1 in lst
    assert run2 not in lst
