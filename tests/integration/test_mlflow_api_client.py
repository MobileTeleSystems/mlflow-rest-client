import logging
import os
import pytest
import random
import uuid
import unittest

from requests import HTTPError
from datetime import datetime, timedelta

from mlflow_client import MLflowApiClient
from mlflow_client.experiment import ExperimentStage
from mlflow_client.run import RunStatus, RunStage, Metric
from mlflow_client.model import ModelVersionStage

log = logging.getLogger(__name__)

host = os.environ['MLFLOW_HOST'] or 'localhost'
port = os.environ['MLFLOW_PORT'] or '5000'
api_url = "http://{host}:{port}".format(host=host, port=port)
client = MLflowApiClient(api_url)

DEFAULT_TIMEOUT = 60

def rand_str():
    return uuid.uuid4().hex

def create_exp_name():
    return "pyTestExp_"+ rand_str()

def create_model_name():
    return "pyTestModel_"+ rand_str()

def now():
    return datetime.now().replace(microsecond=0)

class ApiTest(unittest.TestCase):
    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_experiments(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        exps = client.list_experiments()
        assert exp_name in exps

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_experiments_iterator(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        created = False
        for item in client.list_experiments_iterator():
            if item.name == exp_name:
                created = True
        assert created

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_experiment(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        exp2 = client.get_experiment(exp.id)
        assert exp == exp2

        with pytest.raises(HTTPError) as ex:
            client.get_experiment(rand_str())

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_experiment_by_name(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        exp2 = client.get_experiment_by_name(exp_name)
        assert exp == exp2

        non_existing = client.get_experiment_by_name(rand_str())
        assert non_existing is None

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_rename_experiment(self):
        exp_name = create_exp_name()
        exp_name2 = create_exp_name()
        exp = client.create_experiment(exp_name)

        client.rename_experiment(exp.id, exp_name2)

        exp2 = client.get_experiment(exp.id)
        assert exp.id == exp2.id

        old_exp = client.get_experiment_by_name(exp_name)
        assert old_exp is None

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_create_experiment(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)
        assert exp.name == exp_name

        with pytest.raises(HTTPError) as ex:
            client.create_experiment(exp_name)

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_experiment(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        client.delete_experiment(exp.id)

        old_exp = client.get_experiment(exp.id)
        assert old_exp.stage == ExperimentStage.deleted

        by_name = client.get_experiment_by_name(exp_name)
        assert by_name is None

        with pytest.raises(HTTPError) as ex:
            client.create_experiment(exp_name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_restore_experiment(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        client.delete_experiment(exp.id)
        client.restore_experiment(exp.id)

        old_exp = client.get_experiment(exp.id)
        assert old_exp.stage == ExperimentStage.active
        assert old_exp.name == exp_name

        by_name = client.get_experiment_by_name(exp_name)
        assert by_name == old_exp

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_experiment_tag(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        key = rand_str()
        value = rand_str()

        client.set_experiment_tag(exp.id, key, value)

        old_exp = client.get_experiment(exp.id)
        assert old_exp.stage == ExperimentStage.active
        assert key in old_exp.tags

        exist = False
        assert key in old_exp.tags
        assert old_exp.tags[key].value == value
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_experiment_id(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        exp_id = client.get_experiment_id(exp_name)
        assert exp_id == exp.id

        non_existing_id = client.get_experiment_id(rand_str())
        assert non_existing_id is None

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_or_create_experiment(self):
        exp_name = create_exp_name()
        exp = client.get_or_create_experiment(exp_name)
        exp2 = client.get_or_create_experiment(exp_name)
        assert exp == exp2

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_experiment_runs(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        empty_runs = client.list_experiment_runs(exp.id)
        assert len(empty_runs) == 0

        run = client.create_run(experiment_id=exp.id)
        runs = client.list_experiment_runs(exp.id)
        assert run in runs

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_experiment_runs_iterator(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        is_empty = True
        for run in client.list_experiment_runs_iterator(exp.id):
            is_empty = False

        assert is_empty

        run = client.create_run(experiment_id=exp.id)

        exist = False
        for item in client.list_experiment_runs_iterator(exp.id):
            if item.id == run.id:
                exist = True

        assert exist

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)

        run2 = client.get_run(run.id)
        assert run == run2

        with pytest.raises(HTTPError) as ex:
            client.get_run(rand_str())

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_create_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run1 = client.create_run(experiment_id=exp.id)
        assert run1.experiment_id == exp.id

        key = rand_str()
        value = rand_str()

        start_time = now()
        run2 = client.create_run(experiment_id=exp.id, start_time=start_time, tags={key: value})
        assert run2.experiment_id == exp.id
        assert run1.start_time == start_time
        assert key in run2.tags
        assert run2.tags[key].value == value

        client.delete_run(run1.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_start_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.status == RunStatus.started

        run_info = client.start_run(run.id)
        assert run_info.status == RunStatus.started
        assert run_info.end_time is None

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_schedule_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.status == RunStatus.started

        run_info = client.schedule_run(run.id)
        assert run_info.status == RunStatus.scheduled
        assert run_info.end_time is None

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_finish_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.status == RunStatus.started

        end_time = now()
        run_info = client.finish_run(run.id, end_time=end_time)
        assert run_info.status == RunStatus.finished
        assert run_info.end_time == end_time

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_fail_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.status == RunStatus.started

        end_time = now()
        run_info = client.fail_run(run.id, end_time=end_time)
        assert run_info.status == RunStatus.failed
        assert run_info.end_time == end_time

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_kill_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.status == RunStatus.started

        end_time = now()
        run_info = client.kill_run(run.id, end_time=end_time)
        assert run_info.status == RunStatus.killed
        assert run_info.end_time == end_time

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.stage == RunStage.active

        client.delete_run(run.id)

        run = client.get_run(run.id)
        assert run.stage == RunStage.deleted

        with pytest.raises(HTTPError) as ex:
            client.delete_run(run.id)

        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_restore_run(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        run = client.create_run(experiment_id=exp.id)
        assert run.stage == RunStage.active

        client.delete_run(run.id)
        client.restore_run(run.id)

        run = client.get_run(run.id)
        assert run.stage == RunStage.active

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_log_run_parameter(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        key = rand_str()
        value = rand_str()

        run = client.create_run(experiment_id=exp.id)
        assert key not in run.params

        client.log_run_parameter(run.id, key, value)

        run = client.get_run(run.id)
        assert key in run.params
        assert run.params[key].value == value

        new_value = rand_str()
        with pytest.raises(HTTPError) as ex:
            client.log_run_parameter(run.id, key, new_value)

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_log_run_parameters(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        params = {
            rand_str(): rand_str()
        }

        run = client.create_run(experiment_id=exp.id)
        for key in params:
            assert key not in run.params

        client.log_run_parameters(run.id, params)

        run = client.get_run(run.id)
        for key, value in params.items():
            assert key in run.params
            assert run.params[key].value == value

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_log_run_metric(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        key = rand_str()
        value = random.random()

        run = client.create_run(experiment_id=exp.id)
        assert key not in run.params

        timestamp = now()
        client.log_run_metric(run.id, key, value, timestamp=timestamp)

        run = client.get_run(run.id)
        assert key in run.metrics
        assert run.metrics[key].value == pytest.approx(value)
        assert run.metrics[key].step == 0
        assert run.metrics[key].timestamp == timestamp

        new_value = random.random()
        client.log_run_metric(run.id, key, new_value, step=1)

        run = client.get_run(run.id)
        assert key in run.metrics
        assert run.metrics[key].value != pytest.approx(value)
        assert run.metrics[key].value == pytest.approx(new_value)

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_log_run_metrics(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        metrics = {
            rand_str(): random.random()
        }

        run = client.create_run(experiment_id=exp.id)
        for key in metrics:
            assert key not in run.metrics

        timestamp = now()
        client.log_run_metrics(run.id, metrics)

        run = client.get_run(run.id)
        for key, value in metrics.items():
            assert key in run.metrics
            assert run.metrics[key].value == pytest.approx(value)
            assert run.metrics[key].step == 0
            assert run.metrics[key].timestamp == timestamp

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_run_tag(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        key = rand_str()
        value = rand_str()

        run = client.create_run(experiment_id=exp.id)
        assert key not in run.tags

        client.set_run_tag(run.id, key, value)

        client.set_run_tag(run.id, key, value)

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_run_tags(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        tags = {
            rand_str(): rand_str()
        }

        run = client.create_run(experiment_id=exp.id)
        for key in tags:
            assert key not in run.tags

        client.set_run_tags(run.id, tags)

        run = client.get_run(run.id)
        for key, value in tags.items():
            assert key in run.tags
            assert run.tags[key].value == value

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_run_tag(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        key = rand_str()
        value = rand_str()

        run = client.create_run(experiment_id=exp.id, tags={key: value})
        assert key in run.tags
        assert run.tags[key].value == value

        client.delete_run_tag(run.id, key)

        run = client.get_run(run.id)
        assert key not in run.tags

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_run_tags(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        tags = {
            rand_str(): rand_str()
        }

        run = client.create_run(experiment_id=exp.id, tags=tags)
        for key, value in tags.items():
            assert key in run.tags
            assert run.tags[key].value == value

        client.delete_run_tags(run.id, tags)

        run = client.get_run(run.id)
        for key in tags:
            assert key not in run.tags

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_run_metric_history(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        timestamp = now()
        key = rand_str()
        values = [{'key': key, 'value': random.random(), 'step': i, 'timestamp': timestamp+timedelta(seconds=i*10)} \
                    for i in range(1, 6)]

        run = client.create_run(experiment_id=exp.id)
        client.log_run_metrics(run.id, values)

        for metric in client.list_run_metric_history(run.id, key):
            found = None
            for _metric in values:
                if _metric['key'] == metric.key and _metric['step'] == metric.step:
                    found = Metric.from_dict(_metric)
                    break

            assert found
            assert found.value == pytest.approx(metric.value)
            assert found.timestamp == metric.timestamp

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_run_metric_history_iterator(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        timestamp = now()
        key = rand_str()
        values = [{'key': key, 'value': random.random(), 'step': i, 'timestamp': timestamp+timedelta(seconds=i*10)} \
                    for i in range(1, 6)]

        run = client.create_run(experiment_id=exp.id)
        client.log_run_metrics(run.id, values)

        for metric in client.list_run_metric_history_iterator(run.id, key):
            found = None
            for _metric in values:
                if _metric['key'] == metric.key and _metric['step'] == metric.step:
                    found = Metric.from_dict(_metric)
                    break

            assert found
            assert found.value == pytest.approx(metric.value)
            assert found.timestamp == metric.timestamp

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_run_artifacts(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)
        run = client.create_run(experiment_id=exp.id)

        artifacts = client.list_run_artifacts(run.id)
        assert len(artifacts) == 0

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_runs(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        timestamp = now()
        key = rand_str()
        values = [{'key': key, 'value': random.random(), 'step': i, 'timestamp': timestamp+timedelta(seconds=i*10)} \
                    for i in range(1, 6)]

        run = client.create_run(experiment_id=exp.id)
        client.log_run_metrics(run.id, values)

        query = 'metrics."{}" < 1'.format(key)
        runs = client.search_runs(experiment_ids=[exp.id], query=query)
        assert run.id in runs

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_runs_iterator(self):
        exp_name = create_exp_name()
        exp = client.create_experiment(exp_name)

        timestamp = now()
        key = rand_str()
        values = [{'key': key, 'value': random.random(), 'step': i, 'timestamp': timestamp+timedelta(seconds=i*10)} \
                    for i in range(1, 6)]

        run = client.create_run(experiment_id=exp.id)
        client.log_run_metrics(run.id, values)

        query = 'metrics."{}" < 1'.format(key)
        exist = False
        for _run in client.search_runs_iterator(experiment_ids=[exp.id], query=query):
            if _run.id == run.id:
                exist = True
        assert exist

        client.delete_run(run.id)
        client.delete_experiment(exp.id)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_create_model(self):
        model_name = create_model_name()

        key = rand_str()
        value = rand_str()

        model = client.create_model(model_name, tags={key: value})

        assert model.name == model_name
        assert key in model.tags
        assert model.tags[key].value == value

        with pytest.raises(HTTPError) as ex:
            client.create_model(model_name)

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_model(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        model2 = client.get_model(model_name)
        assert model == model2

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_or_create_model(self):
        model_name = create_model_name()

        model = client.get_or_create_model(model_name)
        model2 = client.get_or_create_model(model_name)
        assert model == model2

        client.delete_model(model_name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_rename_model(self):
        model_name = create_model_name()
        client.create_model(model_name)

        new_name = create_model_name()
        model2 = client.rename_model(model_name, new_name)

        assert model2.name != model_name
        assert model2.name == new_name

        with pytest.raises(HTTPError) as ex:
            client.get_model(model_name)

        client.delete_model(model2.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_model_description(self):
        model_name = create_model_name()

        model = client.create_model(model_name)
        assert not model.description

        description = rand_str()
        model2 = client.set_model_description(model_name, description)

        assert model2.description == description

        client.delete_model(model2.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_model(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        client.delete_model(model_name)

        with pytest.raises(HTTPError) as ex:
            client.get_model(model_name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_models(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        models = client.list_models()
        assert model in models

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_models_iterator(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        exist = False
        for _model in client.list_models_iterator():
            if _model == model_name:
                exist = True
        assert exist

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_models(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        query = "name LIKE '{}%'".format(model_name)
        models = client.search_models(query=query)
        assert model in models

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_models_iterator(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        query = "name LIKE '{}%'".format(model_name)
        exist = False
        for _model in client.search_models(query=query):
            if model.name == _model.name:
                exist = True
        assert exist

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_model_tag(self):
        model_name = create_model_name()

        key = rand_str()
        value = rand_str()

        model = client.create_model(model_name)
        assert key not in model.tags

        client.set_model_tag(model_name, key, value)

        model = client.get_model(model_name)
        assert key in model.tags
        assert model.tags[key].value == value

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_model_tag(self):
        model_name = create_model_name()

        key = rand_str()
        value = rand_str()

        client.create_model(model_name)
        client.set_model_tag(model_name, key, value)

        client.delete_model_tag(model_name, key)

        model = client.get_model(model_name)
        assert key not in model.tags

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_model_versions(self):
        model_name = create_model_name()

        model = client.create_model(model_name)

        versions = client.list_model_versions(model_name)
        assert len(versions) == 0

        version = client.create_model_version(model_name)
        client.test_model_version(model_name, version.version)

        versions = client.list_model_versions(model_name)
        assert version in versions

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_list_model_versions_iterator(self):
        model_name = create_model_name()

        model = client.create_model(model_name)

        exist = False
        for version in client.list_model_versions_iterator(model_name):
            exist = True
        assert not exist

        version = client.create_model_version(model_name)
        client.test_model_version(model_name, version.version)

        for _version in client.list_model_versions_iterator(model_name):
            assert version == _version

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_create_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        key = rand_str()
        value = rand_str()
        source = rand_str()

        version1 = client.create_model_version(model_name, source=source, tags={key: value})
        assert version1.source == source
        assert key in version1.tags
        assert version1.tags[key].value == value

        experiment_name = create_exp_name()
        exp = client.create_experiment(experiment_name)
        run = client.create_run(experiment_id=exp.id)

        version2 = client.create_model_version(model_name, run_id=run.id)
        assert version2.run_id == run.id

        client.delete_model_version(version1.name, version1.version)
        client.delete_run(run.id)
        client.delete_experiment(exp.id)
        client.delete_model_version(version2.name, version2.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)
        version1 = client.get_model_version(model_name, version.version)
        assert version == version1

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_model_version_description(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)
        assert not version.description

        description = rand_str()
        new_version = client.set_model_version_description(model_name, version.version, description)
        assert new_version.description == description

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_set_model_version_tag(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        key = rand_str()
        value = rand_str()

        version = client.create_model_version(model_name)
        assert key not in version.tags

        client.set_model_version_tag(model_name, version.version, key, value)

        new_version = client.get_model_version(model_name, version.version)
        assert key in new_version.tags
        assert new_version.tags[key].value == value

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_model_version_tag(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        key = rand_str()
        value = rand_str()

        version = client.create_model_version(model_name, tags={key: value})
        client.delete_model_version_tag(model_name, version.version, key)

        new_version = client.get_model_version(model_name, version.version)
        assert key not in new_version.tags

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_delete_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)

        client.delete_model_version(model_name, version.version)

        with pytest.raises(HTTPError) as ex:
            client.get_model_version(model_name, version.version)

        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_model_versions(self):
        model_name = create_model_name()
        model = client.create_model(model_name)
        version = client.create_model_version(model_name)

        query = "name='{}'".format(model_name)
        versions = client.search_model_versions(query=query)
        assert version in versions

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_search_model_versions_iterator(self):
        model_name = create_model_name()
        model = client.create_model(model_name)
        version = client.create_model_version(model_name)

        query = "name='{}'".format(model_name)
        exist = False
        for _version in client.search_model_versions_iterator(query=query):
            if _version == version:
                exist = True
        assert exist

        client.delete_model_version(version.name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_get_model_version_download_url(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name, source=rand_str())

        url = client.get_model_version_download_url(model_name, version.version)
        assert url

        client.get_model_version(model_name, version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_test_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)
        assert version.stage == ModelVersionStage.unknown

        new_version = client.test_model_version(model_name, version.version)
        assert new_version.stage == ModelVersionStage.test

        prod_version = client.create_model_version(model_name)
        new_prod_version = client.promote_model_version(model_name, prod_version.version)
        assert new_prod_version.stage == ModelVersionStage.prod

        another_version = client.create_model_version(model_name)
        new_version = client.test_model_version(model_name, another_version.version, archive_existing=True)
        assert new_version.stage == ModelVersionStage.test

        old_version = client.get_model_version(model_name, version.version)
        assert old_version.stage == ModelVersionStage.archived

        prod_version = client.get_model_version(model_name, prod_version.version)
        assert prod_version.stage == ModelVersionStage.prod

        client.get_model_version(model_name, new_version.version)
        client.get_model_version(model_name, old_version.version)
        client.get_model_version(model_name, prod_version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_promote_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)
        assert version.stage == ModelVersionStage.unknown

        new_version = client.promote_model_version(model_name, version.version)
        assert new_version.stage == ModelVersionStage.prod

        test_version = client.create_model_version(model_name)
        new_test_version = client.test_model_version(model_name, test_version.version)
        assert new_test_version.stage == ModelVersionStage.test

        another_version = client.create_model_version(model_name)
        new_version = client.promote_model_version(model_name, another_version.version, archive_existing=True)
        assert new_version.stage == ModelVersionStage.prod

        old_version = client.get_model_version(model_name, version.version)
        assert old_version.stage == ModelVersionStage.archived

        test_version = client.get_model_version(model_name, test_version.version)
        assert test_version.stage == ModelVersionStage.test

        client.get_model_version(model_name, new_version.version)
        client.get_model_version(model_name, old_version.version)
        client.get_model_version(model_name, test_version.version)
        client.delete_model(model.name)


    @pytest.mark.timeout(DEFAULT_TIMEOUT)
    def test_archive_model_version(self):
        model_name = create_model_name()
        model = client.create_model(model_name)

        version = client.create_model_version(model_name)
        assert version.stage == ModelVersionStage.unknown

        new_version = client.archive_model_version(model_name, version.version)
        assert new_version.stage == ModelVersionStage.archived

        client.get_model_version(model_name, version.version)
        client.delete_model(model.name)
