import logging

import pytest
from requests import HTTPError

from mlflow_client.experiment import EXPERIMENTSTAGE
from mlflow_client.model import ModelVersionStage
from mlflow_client.run import Metric, RunStage, RunStatus

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60

import logging
from datetime import timedelta

import pytest
from requests import HTTPError

from .conftest import (
    DEFAULT_TIMEOUT,
    create_exp_name,
    create_model_name,
    now,
    rand_float,
    rand_str,
)

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_experiments(client, create_experiment):
    exp = create_experiment

    exps = client.list_experiments()
    assert exp in exps


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_experiments_iterator(client, create_experiment):
    exp = create_experiment

    created = False
    for item in client.list_experiments_iterator():
        if item.name == exp.name:
            created = True
    assert created


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment(client, create_experiment):
    exp = create_experiment

    exp2 = client.get_experiment(exp.id)
    assert exp == exp2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment_fail(client):
    with pytest.raises(HTTPError):
        client.get_experiment(rand_str())


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment_by_name(client, create_experiment):
    exp = create_experiment

    exp2 = client.get_experiment_by_name(exp.name)
    assert exp == exp2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment_by_name_non_existing(client):
    non_existing = client.get_experiment_by_name(rand_str())

    assert non_existing is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_rename_experiment(client, create_experiment):
    exp = create_experiment
    exp_name2 = create_exp_name()

    client.rename_experiment(exp.id, exp_name2)

    exp2 = client.get_experiment(exp.id)
    assert exp.id == exp2.id

    old_exp = client.get_experiment_by_name(exp.name)
    assert old_exp is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_experiment(client, request):
    exp_name = create_exp_name()
    exp = client.create_experiment(exp_name)

    def finalizer():
        client.delete_experiment(exp.id)

    request.addfinalizer(finalizer)

    assert exp.name == exp_name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_experiment_existing(client, create_experiment):
    exp = create_experiment

    with pytest.raises(HTTPError):
        client.create_experiment(exp.name)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_experiment(client):
    exp_name = create_exp_name()
    exp = client.create_experiment(exp_name)

    client.delete_experiment(exp.id)

    old_exp = client.get_experiment(exp.id)
    assert old_exp.stage == EXPERIMENTSTAGE.deleted

    by_name = client.get_experiment_by_name(exp.name)
    assert by_name is None

    with pytest.raises(HTTPError) as ex:
        client.create_experiment(exp.name)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_restore_experiment(client, create_experiment):
    exp = create_experiment

    client.delete_experiment(exp.id)
    client.restore_experiment(exp.id)

    old_exp = client.get_experiment(exp.id)
    assert old_exp.stage == EXPERIMENTSTAGE.active
    assert old_exp.name == exp.name

    by_name = client.get_experiment_by_name(exp.name)
    assert by_name == old_exp


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_experiment_tag(client, create_experiment):
    exp = create_experiment

    key = rand_str()
    value = rand_str()

    client.set_experiment_tag(exp.id, key, value)

    old_exp = client.get_experiment(exp.id)
    assert old_exp.stage == EXPERIMENTSTAGE.active

    assert key in [item.key for item in old_exp.tags]
    assert old_exp.tags[0].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment_id(client, create_experiment):
    exp = create_experiment

    exp_id = client.get_experiment_id(exp.name)
    assert exp_id == exp.id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_experiment_id_non_existing(client):
    non_existing_id = client.get_experiment_id(rand_str())
    assert non_existing_id is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_or_create_experiment(client, create_experiment):
    exp = create_experiment
    exp2 = client.get_or_create_experiment(exp.name)

    assert exp == exp2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_experiment_runs(client, request, create_experiment):
    exp = create_experiment

    empty_runs = client.list_experiment_runs(exp.id)
    assert len(empty_runs) == 0

    run = client.create_run(experiment_id=exp.id)

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    runs = client.list_experiment_runs(exp.id)
    assert run in runs


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_experiment_runs_iterator(client, request, create_experiment):
    exp = create_experiment

    is_empty = True
    for run in client.list_experiment_runs_iterator(exp.id):
        is_empty = False

    assert is_empty

    run = client.create_run(experiment_id=exp.id)

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    exist = False
    for item in client.list_experiment_runs_iterator(exp.id):
        if item.id == run.id:
            exist = True

    assert exist


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_run(client, create_run):
    run = create_run

    run2 = client.get_run(run.id)

    assert run == run2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_run_fail(client):
    with pytest.raises(HTTPError):
        client.get_run(rand_str())


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_run(request, client, create_experiment):
    exp = create_experiment
    run = client.create_run(experiment_id=exp.id)

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    assert run.experiment_id == exp.id
    assert run.status == RunStatus.STARTED
    assert run.stage == RunStage.ACTIVE


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_run_without_start_time(request, client, create_experiment):
    exp = create_experiment
    start_time = now()

    run = client.create_run(experiment_id=exp.id)

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    assert run.start_time

    assert start_time.date() <= run.start_time.date()
    assert run.end_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_run_with_start_time(request, client, create_experiment):
    exp = create_experiment
    start_time = now()

    run = client.create_run(experiment_id=exp.id, start_time=start_time)

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    assert int(run.start_time.timestamp()) == int(start_time.timestamp())
    assert run.end_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_run_with_tags(request, client, create_experiment):
    exp = create_experiment
    key = rand_str()
    value = rand_str()

    run = client.create_run(experiment_id=exp.id, tags={key: value})

    def finalizer_run():
        client.delete_run(run.id)

    request.addfinalizer(finalizer_run)

    assert key in run.tags
    assert run.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_start_run(create_run, client):
    run = create_run

    run_info = client.start_run(run.id)
    assert run_info.status == RunStatus.STARTED
    assert run_info.end_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_schedule_run(create_run, client):
    run = create_run

    run_info = client.schedule_run(run.id)
    assert run_info.status == RunStatus.SCHEDULED
    assert run_info.end_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_finish_run(create_run, client):
    run = create_run

    end_time = now()
    run_info = client.finish_run(run.id, end_time=end_time)
    assert run_info.status == RunStatus.FINISHED
    assert run_info.end_time.date() == end_time.date()


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_fail_run(create_run, client):
    run = create_run

    end_time = now()
    run_info = client.fail_run(run.id, end_time=end_time)
    assert run_info.status == RunStatus.FAILED
    assert run_info.end_time
    assert run_info.end_time.date() == end_time.date()


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_kill_run(create_run, client):

    run = create_run

    end_time = now()
    run_info = client.kill_run(run.id, end_time=end_time)

    assert run_info.status == RunStatus.KILLED
    assert run_info.end_time
    assert int(run_info.end_time.timestamp()) == int(end_time.timestamp())


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_run(create_experiment, client):
    exp = create_experiment

    run = client.create_run(experiment_id=exp.id)
    client.delete_run(run.id)

    run = client.get_run(run.id)
    assert run.stage == RunStage.DELETED


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_run_fail(create_experiment, client):
    exp = create_experiment

    run = client.create_run(experiment_id=exp.id)
    client.delete_run(run.id)

    with pytest.raises(HTTPError):
        client.delete_run(run.id)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_restore_run(create_run, client):
    run = create_run

    client.delete_run(run.id)
    client.restore_run(run.id)

    run = client.get_run(run.id)
    assert run.stage == RunStage.ACTIVE


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_log_run_parameter(create_run, client):
    key = rand_str()
    value = rand_str()

    run = create_run
    assert key not in run.params

    client.log_run_parameter(run.id, key, value)

    run = client.get_run(run.id)
    assert key in run.params
    assert run.params[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_log_run_parameter_fail(create_run, client):
    key = rand_str()
    value = rand_str()

    run = create_run
    client.log_run_parameter(run.id, key, value)

    new_value = rand_str()
    with pytest.raises(HTTPError):
        client.log_run_parameter(run.id, key, new_value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_log_run_parameters(create_run, client):
    params = {rand_str(): rand_str()}

    run = create_run
    for key in params:
        assert key not in run.params

    client.log_run_parameters(run.id, params)

    run = client.get_run(run.id)
    for key, value in params.items():
        assert key in run.params
        assert run.params[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_log_run_metric(create_run, client):
    key = rand_str()
    value = rand_float()

    run = create_run
    assert key not in run.params

    timestamp = now().timestamp()
    client.log_run_metric(run.id, key, value, timestamp=int(timestamp))

    run = client.get_run(run.id)
    assert key in run.metrics
    assert run.metrics[key].value == pytest.approx(value)
    assert run.metrics[key].step == 0
    assert int(run.metrics[key].timestamp.timestamp()) == int(timestamp)

    new_value = rand_float()
    client.log_run_metric(run.id, key, new_value, step=1)

    run = client.get_run(run.id)
    assert key in run.metrics
    assert run.metrics[key].value != pytest.approx(value)
    assert run.metrics[key].value == pytest.approx(new_value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_log_run_metrics(create_run, client):
    metrics = {rand_str(): rand_float()}

    run = create_run
    for key in metrics:
        assert key not in run.metrics

    timestamp = now()
    client.log_run_metrics(run.id, metrics)

    run = client.get_run(run.id)
    for key, value in metrics.items():
        assert key in run.metrics
        assert run.metrics[key].value == pytest.approx(value)
        assert run.metrics[key].step == 0
        assert int(run.metrics[key].timestamp.timestamp()) == int(timestamp.timestamp())


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_run_tag(create_run, client):
    key = rand_str()
    value = rand_str()

    run = create_run
    assert key not in run.tags

    client.set_run_tag(run.id, key, value)

    run = client.get_run(run.id)
    assert key in run.tags
    assert run.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_run_tags(create_run, client):
    tags = {rand_str(): rand_str()}

    run = create_run
    for key in tags:
        assert key not in run.tags

    client.set_run_tags(run.id, tags)

    run = client.get_run(run.id)
    for key, value in tags.items():
        assert key in run.tags
        assert run.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_run_tag(create_run, client):
    key = rand_str()
    value = rand_str()

    run = create_run
    client.set_run_tag(run.id, key, value)

    client.delete_run_tag(run.id, key)

    run = client.get_run(run.id)
    assert key not in run.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_run_tags(create_run, client):
    tags = {rand_str(): rand_str()}

    run = create_run
    client.set_run_tags(run.id, tags)

    client.delete_run_tags(run.id, tags)

    run = client.get_run(run.id)
    for key in tags:
        assert key not in run.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_run_metric_history(create_run, client):
    timestamp = now()
    key = rand_str()
    values = [
        {"key": key, "value": rand_float(), "step": i, "timestamp": timestamp + timedelta(seconds=i * 10)}
        for i in range(1, 6)
    ]

    run = create_run
    client.log_run_metrics(run.id, values)

    for metric in client.list_run_metric_history(run.id, key):
        found = None
        for _metric in values:
            if _metric["key"] == metric.key and _metric["step"] == metric.step:
                found = Metric.parse_obj(_metric)
                break

        assert found
        assert found.value == pytest.approx(metric.value)
        assert found.timestamp.date() == metric.timestamp.date()


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_run_metric_history_iterator(create_run, client):
    timestamp = now()
    key = rand_str()
    values = [
        {"key": key, "value": rand_float(), "step": i, "timestamp": timestamp + timedelta(seconds=i * 10)}
        for i in range(1, 6)
    ]

    run = create_run
    client.log_run_metrics(run.id, values)

    for metric in client.list_run_metric_history_iterator(run.id, key):
        found = None
        for _metric in values:
            if _metric["key"] == metric.key and _metric["step"] == metric.step:
                found = Metric.parse_obj(_metric)
                break

        assert found
        assert found.value == pytest.approx(metric.value)
        assert found.timestamp.date() == metric.timestamp.date()


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_run_artifacts(create_run, client):
    run = create_run

    artifacts = client.list_run_artifacts(run.id)
    assert len(artifacts) == 0


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_runs(create_run, client):
    timestamp = now()
    key = rand_str()
    values = [
        {"key": key, "value": rand_float(0, 1), "step": i, "timestamp": timestamp + timedelta(seconds=i * 10)}
        for i in range(1, 6)
    ]

    run = create_run
    client.log_run_metrics(run.id, values)

    query = 'metrics."{}" < 1'.format(key)
    runs = client.search_runs(experiment_ids=[run.experiment_id], query=query)
    assert run.id in runs


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_runs_iterator(create_run, client):
    timestamp = now()
    key = rand_str()
    values = [
        {"key": key, "value": rand_float(0, 1), "step": i, "timestamp": timestamp + timedelta(seconds=i * 10)}
        for i in range(1, 6)
    ]

    run = create_run
    client.log_run_metrics(run.id, values)

    query = 'metrics."{}" < 1'.format(key)
    exist = False
    for _run in client.search_runs_iterator(experiment_ids=[run.experiment_id], query=query):
        if _run.id == run.id:
            exist = True
    assert exist


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model(request, client):
    model_name = create_model_name()

    model = client.create_model(model_name)

    def finalizer():
        client.delete_model(model.name)

    request.addfinalizer(finalizer)

    assert model.name == model_name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_with_tags(request, client):
    model_name = create_model_name()

    key = rand_str()
    value = rand_str()

    model = client.create_model(model_name, tags={key: value})

    def finalizer():
        client.delete_model(model.name)

    request.addfinalizer(finalizer)

    assert key in model.tags
    assert model.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_already_exist(request, client):
    model_name = create_model_name()

    model = client.create_model(model_name)

    def finalizer():
        client.delete_model(model.name)

    request.addfinalizer(finalizer)

    with pytest.raises(HTTPError) as ex:
        client.create_model(model_name)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_model(create_model, client):
    model = create_model

    model2 = client.get_model(model.name)
    assert model == model2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_or_create_model(request, create_model, client):
    model = create_model
    _models = []

    def finalizer():
        for _model in _models:
            client.delete_model(_model.name)

    request.addfinalizer(finalizer)

    for name in [model.name, model.name.replace("-", "_")]:
        _model = client.get_or_create_model(name)

        if model.name == _model.name:
            assert model == _model
        else:
            _models.append(_model)
            assert model != _model

        assert _model.name == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_rename_model(request, client, create_model):
    model = create_model

    new_name = create_model_name()
    model2 = client.rename_model(model.name, new_name)

    def finalizer():
        client.rename_model(new_name, model.name)

    request.addfinalizer(finalizer)

    assert model2.name != model.name
    assert model2.name == new_name

    with pytest.raises(HTTPError):
        client.get_model(model.name)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_model_description(create_model, client):
    model = create_model
    assert not model.description

    description = rand_str()
    model = client.set_model_description(model.name, description)

    assert model.description == description


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_model(client):
    model_name = create_model_name()
    model = client.create_model(model_name)

    client.delete_model(model.name)

    with pytest.raises(HTTPError):
        client.get_model(model.name)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_models(client, create_model):
    model = create_model

    models = client.list_models()
    assert model in models


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_models_iterator(client, create_model):
    model = create_model

    exist = False
    for _model in client.list_models_iterator():
        if _model.name == model.name:
            exist = True

    assert exist


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_models(client, create_model):
    model = create_model

    for name in [model.name, model.name.replace("-", "_")]:
        query = "name LIKE '{}%'".format(name)
        models = client.search_models(query=query)
        assert model in models


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_models_iterator(client, create_model):
    model = create_model

    for name in [model.name, model.name.replace("-", "_")]:
        query = "name LIKE '{}%'".format(name)
        exist = False
        for _model in client.search_models(query=query):
            if model.name == _model.name:
                exist = True
        assert exist


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_model_tag(client, create_model):
    key = rand_str()
    value = rand_str()

    model = create_model
    assert key not in model.tags

    client.set_model_tag(model.name, key, value)

    model = client.get_model(model.name)
    assert key in model.tags
    assert model.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_model_tag(client, create_model):
    key = rand_str()
    value = rand_str()

    model = create_model
    client.set_model_tag(model.name, key, value)

    client.delete_model_tag(model.name, key)

    model = client.get_model(model.name)
    assert key not in model.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_model_versions(client, create_model):
    model = create_model

    versions = client.list_model_versions(model.name)
    assert len(versions) == 0

    version1 = client.create_model_version(model.name)
    client.test_model_version(model.name, version1.version)

    versions = client.list_model_versions(model.name)

    assert version1 in versions

    version2 = client.create_model_version(model.name)
    client.test_model_version(model.name, version2.version)

    versions = client.list_model_versions(model.name)
    assert version1 not in versions
    assert version2 in versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [stage for stage in ModelVersionStage])
def test_list_model_versions_with_stage(client, create_model, stage):
    model = create_model

    versions = client.list_model_versions(model.name, stages=stage)
    assert len(versions) == 0

    version1 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version1.version, stage)

    for _stage in ModelVersionStage:
        versions = client.list_model_versions(model.name, stages=_stage)
        if _stage == stage:
            assert version1 in versions
        else:
            assert version1 not in versions

    version2 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version2.version, stage)

    for _stage in ModelVersionStage:
        versions = client.list_model_versions(model.name, stages=_stage)
        if _stage == stage:
            assert version1 not in versions
            assert version2 in versions
        else:
            assert version1 not in versions
            assert version2 not in versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_model_versions_iterator(client, create_model):
    model = create_model

    is_empty = True
    for _version in client.list_model_versions_iterator(model.name):
        is_empty = False
    assert is_empty

    version1 = client.create_model_version(model.name)
    client.test_model_version(model.name, version1.version)

    present1 = False
    for _version in client.list_model_versions_iterator(model.name):
        if _version.version == version1.version:
            present1 = True
    assert present1

    version2 = client.create_model_version(model.name)
    client.test_model_version(model.name, version2.version)

    present1 = False
    present2 = False

    for _version in client.list_model_versions_iterator(model.name):
        if _version.version == version1.version:
            present1 = True
        if _version.version == version2.version:
            present2 = True

    assert not present1
    assert present2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [stage for stage in ModelVersionStage])
def test_list_model_versions_iterator_with_stage(client, create_model, stage):
    model = create_model

    is_empty = True
    for _version in client.list_model_versions_iterator(model.name, stages=stage):
        is_empty = False
    assert is_empty

    version1 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version1.version, stage)

    for _stage in ModelVersionStage:
        present1 = False
        for _version in client.list_model_versions_iterator(model.name, stages=_stage):
            if _version.version == version1.version:
                present1 = True

        if _stage == stage:
            assert present1
        else:
            assert not present1

    version2 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version2.version, stage)

    for _stage in ModelVersionStage:
        present1 = False
        present2 = False

        for _version in client.list_model_versions_iterator(model.name, stages=_stage):
            if _version.version == version1.version:
                present1 = True
            if _version.version == version2.version:
                present2 = True

        if _stage == stage:
            assert not present1
            assert present2
        else:
            assert not present1
            assert not present2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_model_all_versions(client, create_model):
    model = create_model

    versions = client.list_model_all_versions(model.name)
    assert len(versions) == 0

    version1 = client.create_model_version(model.name)
    client.test_model_version(model.name, version1.version)

    versions = client.list_model_all_versions(model.name)
    assert version1 in versions

    version2 = client.create_model_version(model.name)
    client.test_model_version(model.name, version2.version)

    versions = client.list_model_all_versions(model.name)
    assert version1 in versions
    assert version2 in versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_list_model_all_versions_iterator(client, create_model):
    model = create_model

    is_empty = True
    for _version in client.list_model_all_versions_iterator(model.name):
        is_empty = False
    assert is_empty

    version1 = client.create_model_version(model.name)
    client.test_model_version(model.name, version1.version)

    present1 = False
    for _version in client.list_model_all_versions_iterator(model.name):
        if _version.version == version1.version:
            present1 = True
    assert present1

    version2 = client.create_model_version(model.name)
    client.test_model_version(model.name, version2.version)

    present1 = False
    present2 = False

    for _version in client.list_model_all_versions_iterator(model.name):
        if _version.version == version1.version:
            present1 = True
        if _version.version == version2.version:
            present2 = True

    assert present1
    assert present2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [stage for stage in ModelVersionStage])
def test_list_model_all_versions_with_stage(client, create_model, stage):
    model = create_model

    versions = client.list_model_all_versions(model.name, stages=stage)
    assert len(versions) == 0

    version1 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version1.version, stage)

    for _stage in ModelVersionStage:
        versions = client.list_model_all_versions(model.name, stages=_stage)
        if _stage == stage:
            assert version1 in versions
        else:
            assert version1 not in versions

    version2 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version2.version, stage)

    for _stage in ModelVersionStage:
        versions = client.list_model_all_versions(model.name, stages=_stage)
        if _stage == stage:
            assert version1 in versions
            assert version2 in versions
        else:
            assert version1 not in versions
            assert version2 not in versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("stage", [stage for stage in ModelVersionStage])
def test_list_model_all_versions_iterator_with_stage(client, create_model, stage):
    model = create_model
    data = client.list_model_all_versions_iterator(model.name, stages=stage)

    is_empty = True
    for _version in data:
        is_empty = False

    assert is_empty

    version1 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version1.version, stage)

    for _stage in ModelVersionStage:
        present1 = False
        for _version in client.list_model_all_versions_iterator(model.name, stages=_stage):
            if _version.version == version1.version:
                present1 = True

        if _stage == stage:
            assert present1
        else:
            assert not present1

    version2 = client.create_model_version(model.name)
    client.transition_model_version_stage(model.name, version2.version, stage)

    for _stage in ModelVersionStage:
        present1 = False
        present2 = False

        for _version in client.list_model_all_versions_iterator(model.name, stages=_stage):
            if _version.version == version1.version:
                present1 = True
            if _version.version == version2.version:
                present2 = True

        if _stage == stage:
            assert present1
            assert present2
        else:
            assert not present1
            assert not present2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_version(request, client, create_model_version):
    version1 = create_model_version

    version2 = client.create_model_version(version1.name)

    def finalizer():
        client.delete_model_version(version2.name, version2.version)

    request.addfinalizer(finalizer)

    assert version1.name == version2.name
    assert version2.version > version1.version


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_version_above_existing(request, client, create_model):
    model = create_model

    version = client.create_model_version(model.name)

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    assert version.name == model.name
    assert version.version == 1


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_version_with_source(request, client, create_model):
    model = create_model

    source = rand_str()

    version = client.create_model_version(model.name, source=source)

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    assert version.source == source


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_version_with_tags(request, client, create_model):
    model = create_model

    key = rand_str()
    value = rand_str()

    version = client.create_model_version(model.name, tags={key: value})

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    assert key in version.tags
    assert version.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_create_model_version_with_run_id(request, client, create_run, create_model):
    model = create_model
    run = create_run

    version = client.create_model_version(model.name, run_id=run.id)

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    assert version.run_id == run.id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_model_version(client, create_model_version):
    version = create_model_version

    version1 = client.get_model_version(version.name, version.version)
    assert version == version1


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_model_version_description(client, create_model_version):
    version = create_model_version
    assert not version.description

    description = rand_str()
    new_version = client.set_model_version_description(version.name, version.version, description)
    assert new_version.description == description


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_set_model_version_tag(client, create_model_version):
    key = rand_str()
    value = rand_str()

    version = create_model_version
    assert key not in version.tags

    client.set_model_version_tag(version.name, version.version, key, value)

    new_version = client.get_model_version(version.name, version.version)
    assert key in new_version.tags
    assert new_version.tags[key].value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_model_version_tag(client, create_model_version):
    key = rand_str()
    value = rand_str()

    version = create_model_version
    client.set_model_version_tag(version.name, version.version, key, value)

    client.delete_model_version_tag(version.name, version.version, key)

    new_version = client.get_model_version(version.name, version.version)
    assert key not in new_version.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_delete_model_version(client, create_model):
    model = create_model

    version = client.create_model_version(model.name)

    client.delete_model_version(version.name, version.version)

    with pytest.raises(HTTPError):
        client.get_model_version(version.name, version.version)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_model_versions(client, create_model_version):
    version = create_model_version

    query = "name='{}'".format(version.name)
    versions = client.search_model_versions(query=query)
    assert version in versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_search_model_versions_iterator(client, create_model_version):
    version = create_model_version

    query = "name='{}'".format(version.name)
    exist = False
    for _version in client.search_model_versions_iterator(query=query):
        if _version == version:
            exist = True
    assert exist


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_get_model_version_download_url(request, client, create_model):
    model = create_model

    version = client.create_model_version(model.name, source=rand_str())

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    url = client.get_model_version_download_url(version.name, version.version)
    assert url


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "old_stage, changed",
    [(None, True), (ModelVersionStage.TEST, False), (ModelVersionStage.PROD, True), (ModelVersionStage.ARCHIVED, True)],
)
def test_test_model_version(client, create_model_version, old_stage, changed):
    old_version = create_model_version
    if old_stage is not None:
        old_version = client.transition_model_version_stage(old_version.name, old_version.version, old_stage)

    new_version = client.test_model_version(old_version.name, old_version.version)

    if changed:
        assert new_version.stage != old_version.stage
        assert new_version.stage == ModelVersionStage.TEST
    else:
        assert new_version.stage == old_version.stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "old_stage, changed",
    [
        (None, False),
        (ModelVersionStage.TEST, True),
        (ModelVersionStage.PROD, False),
        (ModelVersionStage.ARCHIVED, False),
    ],
)
@pytest.mark.parametrize(
    "new_stage", [(None), (ModelVersionStage.TEST), (ModelVersionStage.PROD), (ModelVersionStage.ARCHIVED)]
)
@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_test_model_version_archive_existing(request, client, create_model_version, old_stage, new_stage, changed):
    old_version = create_model_version
    if old_stage is not None:
        old_version = client.transition_model_version_stage(old_version.name, old_version.version, old_stage)

    changed_version = client.create_model_version(old_version.name)

    def finalizer():
        client.delete_model_version(changed_version.name, changed_version.version)

    request.addfinalizer(finalizer)

    if new_stage is not None:
        new_stage = client.transition_model_version_stage(changed_version.name, changed_version.version, new_stage)

    client.test_model_version(changed_version.name, changed_version.version, archive_existing=True)
    new_version = client.get_model_version(old_version.name, old_version.version)

    if changed:
        assert new_version.stage != old_version.stage
        assert new_version.stage == ModelVersionStage.ARCHIVED
    else:
        assert new_version.stage == old_version.stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "old_stage, changed",
    [(None, True), (ModelVersionStage.TEST, True), (ModelVersionStage.PROD, False), (ModelVersionStage.ARCHIVED, True)],
)
def test_promote_model_version(client, create_model_version, old_stage, changed):
    old_version = create_model_version
    if old_stage is not None:
        old_version = client.transition_model_version_stage(old_version.name, old_version.version, old_stage)

    new_version = client.promote_model_version(old_version.name, old_version.version)

    if changed:
        assert new_version.stage != old_version.stage
        assert new_version.stage == ModelVersionStage.PROD
    else:
        assert new_version.stage == old_version.stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "old_stage, changed",
    [
        (None, False),
        (ModelVersionStage.TEST, False),
        (ModelVersionStage.PROD, True),
        (ModelVersionStage.ARCHIVED, False),
    ],
)
@pytest.mark.parametrize(
    "new_stage", [(None), (ModelVersionStage.TEST), (ModelVersionStage.PROD), (ModelVersionStage.ARCHIVED)]
)
@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_promote_model_version_archive_existing(request, client, create_model_version, old_stage, new_stage, changed):
    old_version = create_model_version
    if old_stage is not None:
        old_version = client.transition_model_version_stage(old_version.name, old_version.version, old_stage)

    changed_version = client.create_model_version(old_version.name)

    def finalizer():
        client.delete_model_version(changed_version.name, changed_version.version)

    request.addfinalizer(finalizer)

    if new_stage is not None:
        new_stage = client.transition_model_version_stage(changed_version.name, changed_version.version, new_stage)

    client.promote_model_version(changed_version.name, changed_version.version, archive_existing=True)
    new_version = client.get_model_version(old_version.name, old_version.version)

    if changed:
        assert new_version.stage != old_version.stage
        assert new_version.stage == ModelVersionStage.ARCHIVED
    else:
        assert new_version.stage == old_version.stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "old_stage, changed",
    [
        (None, True),
        (ModelVersionStage.TEST, True),
        (ModelVersionStage.PROD, True),
        (ModelVersionStage.ARCHIVED, False),
        ("Staging", True),
        ("Production", True),
        ("Archived", False),
    ],
)
def test_archive_model_version(client, create_model_version, old_stage, changed):
    old_version = create_model_version
    if old_stage is not None:
        old_version = client.transition_model_version_stage(old_version.name, old_version.version, old_stage)

    new_version = client.archive_model_version(old_version.name, old_version.version)

    if changed:
        assert new_version.stage != old_version.stage
        assert new_version.stage == ModelVersionStage.ARCHIVED
    else:
        assert new_version.stage == old_version.stage
