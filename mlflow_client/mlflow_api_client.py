
import json
import time
import requests

from .artifact import FileInfo
from .experiment import Experiment
from .log import get_logger
from .model import Model, ModelVersion, ModelVersionStage
from .page import Page
from .run import Run, RunInfo, RunViewType, RunStatus, Metric

class MLflowApiClient(object):
    """ HTTP Client for MLflow API """

    MAX_RESULTS = 100

    def __init__(self, api_url, user=None, password=None, logger=get_logger(), ignore_ssl_check=False):
        self.base_url = api_url
        self.user = user
        self.password = password
        self._ignore_ssl_check = ignore_ssl_check
        self.logger = logger


    def list_experiments(self, view_type=RunViewType.active):
        """
        :param view_type: view type
        :type view_type: RunViewType
        :returns: experiments
        :rtype: list[Experiment]
        """
        return Experiment.from_list(self._get('experiments/list', view_type=view_type.value).get('experiments', []))


    def get_experiment(self, id):
        """
        :param id: experiment ID
        :type id: str
        :returns: experiment
        :rtype: Experiment
        """
        return Experiment.from_dict(self._get('experiments/get', experiment_id=id)['experiment'])


    def get_experiment_by_name(self, name):
        """
        :param name: experiment name
        :type name: str
        :returns: experiment
        :rtype: Experiment
        """
        id = self.get_experiment_id(name)
        if id:
            return self.get_experiment(id)
        return None


    def create_experiment(self, name, artifact_location=None):
        """
        :param name: experiment name
        :type name: str
        :returns: experiment
        :rtype: Experiment
        """
        params = {}
        if artifact_location:
            params['artifact_location'] = artifact_location

        experiment_id = self._post('experiments/create', name=name, **params)['experiment_id']
        return self.get_experiment(experiment_id)


    def rename_experiment(self, id, new_name):
        """
        :param id: experiment ID
        :type id: str
        :param new_name: new experiment name
        :type new_name: str
        """
        return self._post('experiments/update', experiment_id=id, new_name=new_name)


    def delete_experiment(self, id):
        """
        :param id: experiment ID
        :type id: str
        """
        return self._post('experiments/delete', experiment_id=id)


    def restore_experiment(self, id):
        """
        :param id: experiment ID
        :type id: str
        """
        return self._post('experiments/restore', experiment_id=id)


    def set_experiment_tag(self, id, key, value):
        """
        :param id: experiment ID
        :type id: str
        :param key: tag name
        :type key: str
        :param value: tag value
        :type value: str
        """
        return self._post('experiments/set-experiment-tag', experiment_id=id, key=key, value=value)


    def get_experiment_id(self, name):
        """
        :param name: experiment name
        :type name: str
        :returns: experiment ID
        :rtype: str
        """
        exps = self.list_experiments()
        for exp in exps:
            if exp.name == name:
                return exp.id
        return None


    def get_or_create_experiment(self, name, artifact_location=None):
        """
        :param name: experiment name
        :type name: str
        :returns: experiment ID
        :rtype: str
        """
        id = self.get_experiment_id(name)
        if id is None:
            experiment = self.create_experiment(name, artifact_location)
        else:
            experiment = self.get_experiment(id)
        return experiment


    def list_experiment_runs(self, id):
        """
        :param id: experiment ID
        :type id: str
        :returns: runs
        :rtype: list[Run]
        """
        return [run for run in self.list_experiment_runs_iterator(id)]


    def list_experiment_runs_iterator(self, id):
        """
        :param id: experiment ID
        :type id: str
        :returns: runs
        :rtype: list[Run]
        """
        for run in self.search_runs_iterator(experiment_ids=[id]):
            return run


    def get_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run
        :rtype: dict
        """
        return Run.from_dict(self._get('runs/get', run_id=id)['run'])


    def create_run(self, experiment_id, start_time=None, **tags):
        """
        :param experiment_id: experiment ID
        :type experiment_id: str
        :param start_time: start time as Unix timestamp
        :type start_time: int
        :returns: run
        :rtype: dict
        """
        if not start_time:
            start_time = self._now
        return Run.from_dict(self._post('runs/create', experiment_id=experiment_id, start_time=start_time, tags=self._handle_tags(tags))['run'])


    def set_run_status(self, id, status=None, end_time=None):
        """
        :param id: run ID
        :type id: str
        :param status: run status
        :type status: RunStatus
        :param end_time: end time as Unix timestamp
        :type end_time: int
        :returns: run info
        :rtype: dict
        """
        params = {}
        if status:
            params['status'] = status.value
        if end_time:
            params['end_time'] = end_time
        return RunInfo.from_dict(self._post('runs/update', run_id=id, **params)['run_info'])


    def start_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run info
        :rtype: dict
        """
        return self.set_run_status(id, RunStatus.started)


    def schedule_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run info
        :rtype: dict
        """
        return self.set_run_status(id, RunStatus.scheduled)


    def finish_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run info
        :rtype: dict
        """
        return self.set_run_status(id, RunStatus.finished)


    def fail_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run info
        :rtype: dict
        """
        return self.set_run_status(id, RunStatus.failed, end_time=self._now)


    def kill_run(self, id):
        """
        :param id: run ID
        :type id: str
        :returns: run info
        :rtype: dict
        """
        return self.set_run_status(id, RunStatus.killed, end_time=self._now)


    def delete_run(self, id):
        """
        :param id: run ID
        :type id: str
        """
        return self._post('runs/delete', run_id=id)


    def restore_run(self, id):
        """
        :param id: run ID
        :type id: str
        """
        return self._post('runs/restore', run_id=id)


    def log_run_parameter(self, id, key, value):
        """
        :param id: run ID
        :type id: str
        :param key: parameter name
        :type key: str
        :param value: parameter value
        :type value: str
        """
        return self._post('runs/log-parameter', run_id=id, key=key, value=value)


    def log_run_metric(self, id, key, value, timestamp=None):
        """
        :param id: run ID
        :type id: str
        :param key: metric name
        :type key: str
        :param value: metric value
        :type value: str
        :param timestamp: metric timestamp as Unix timestamp
        :type timestamp: int
        """
        if not timestamp:
            timestamp = self._now
        dct = self._add_timestamp({'run_id': id, 'key': key, 'value': value}, timestamp)
        return self._post('runs/log-metric', **dct)


    def log_run_batch(self, id, params=None, metrics=None, timestamp=None, **tags):
        """
        :param id: run ID
        :type id: str
        :param params: list of params dict like {'key':..., 'value':...}
        :type params: list[dict]
        :param metrics: list of metric dict like {'key':..., 'value':...,'timestamp':...}
        :type metrics: list[dict]
        :param timestamp: default metric timestamp as Unix timestamp
        :type timestamp: int
        :param tags: tags
        :type tags: dict
        """
        if not params:
            params = []
        if not metrics:
            metrics = []
        if not timestamp:
            timestamp = self._now

        metrics = [self._add_timestamp(metric, timestamp) for metric in metrics]

        return self._post('runs/log-batch', run_id=id, params=params, metrics=metrics, tags=self._handle_tags(tags))


    def log_run_model(self, id, model):
        """
        :param id: run ID
        :type id: str
        :param model: MLmodel file
        :type model: dict
        """
        return self._post('runs/log-model', run_id=id, model_json=model)


    def set_run_tag(self, id, key, value):
        """
        :param id: experiment ID
        :type id: str
        :param key: tag name
        :type key: str
        :param value: tag value
        :type value: str
        """
        return self._post('runs/set-tag', run_id=id, key=key, value=value)


    def delete_run_tag(self, id, key):
        """
        :param id: experiment ID
        :type id: str
        :param key: tag name
        :type key: str
        """
        return self._post('runs/delete-tag', run_id=id, key=key)


    def _add_timestamp(self, item, timestamp):
        if 'timestamp' in item and isinstance(item['timestamp'], int):
            return item

        item['timestamp'] = timestamp
        return item


    def get_run_metric_history(self, id, key):
        """
        :param id: run ID
        :type id: str
        :param key: metric name
        :type key: str
        :returns: metrics
        :rtype: list
        """
        return Metric.from_list(self._get('metrics/get-history', run_id=id, metric_key=key)['metrics'])


    def list_run_artifacts(self, id, path=None, page_token=None):
        """
        :param id: run ID
        :type id: str
        :param path: artifacts path
        :type path: str
        """
        params = {}
        if path:
            params['path'] = path
        if page_token:
            params['page_token'] = page_token
        response = self._get('artifacts/list', run_id=id, **params)

        return Page.from_dict(response, items_key='files', item_class=FileInfo, root=response['root_uri'])


    def list_run_artifacts_iterator(self, id, path=None, page_token=None):
        page = self.list_run_artifacts(id=id, path=path, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.list_run_artifacts(id=id, path=path, page_token=page.next_page_token)
            else:
                break


    def search_runs(self, experiment_ids, query="", run_view_type=RunViewType.active, max_results=MAX_RESULTS, order_by=None, page_token=None):
        """
        :param query: query to search
            Example:
                `"metrics.rmse < 1 and params.model_class = 'LogisticRegression'"`
        :type query: str
        :param experiment_ids: experiment IDS
        :type experiment_ids: list
        :param run_view_type: view type
        :type run_view_type: RunViewType
        :param max_results: max results to return
        :type max_results: int
        :param order_by: order by expression
            Example:
                ['name', 'version ASC']
        :type order_by: list
        :param version: models
        :type version: list
        """

        if not isinstance(experiment_ids, list):
            experiment_ids = [experiment_ids]
        if not order_by:
            order_by = []

        params = {
            'experiment_ids': experiment_ids,
            'filter': query,
            'max_results': max_results,
            'run_view_type': run_view_type.value,
            'order_by': order_by
        }
        if page_token:
            params['page_token'] = page_token
        response = self._post('runs/search', **params)
        return Page.from_dict(response, items_key='runs', item_class=Run)


    def search_runs_iterator(self, experiment_ids, query="", run_view_type=RunViewType.active, max_results=MAX_RESULTS, order_by=None, page_token=None):
        page = self.search_runs(experiment_ids=experiment_ids, query=query, run_view_type=run_view_type, max_results=max_results, order_by=order_by, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_runs(experiment_ids=experiment_ids, query=query, run_view_type=run_view_type, max_results=max_results, order_by=order_by, page_token=page.next_page_token)
            else:
                break

    def set_model_tag(self, name, tag_name, tag_value):
        """
        :param name: model name
        :type name: str
        :param tag_name: tag name
        :type tag_name: str
        :param tag_value: tag value
        :type tag_value: str
        """
        return self._post('registered-models/set-tag', name=name, key=tag_name, value=tag_value)

    def create_model(self, name, **tags):
        """
        :param name: model name
        :type name: str
        :param tags: tags
        :type tags: dict
        :returns: model
        :rtype: dict
        """
        return Model.from_dict(self._post('registered-models/create', name=name, tags=self._handle_tags(tags))['registered_model'])

    def delete_model_tag(self, name, tag_name):
        """
        :param name: model name
        :type name: str
        :param tag_name: tag name
        :type tag_name: str
        """
        return self._post('registered-models/delete-tag', name=name, key=tag_name)

    def get_model(self, name):
        """
        :param name: model name
        :type name: str
        :returns: model
        :rtype: dict
        """
        return Model.from_dict(self._post('registered-models/get', name=name)['registered_model'])

    def list_model_versions(self, name, stages=None):
        """
        :returns: model versions
        :rtype: list
        """
        params = {}
        if stages:
            params['stages'] = stages
        return ModelVersion.from_list(self._post('registered-models/get-latest-versions', name=name, **params)['model_versions'])

    def rename_model(self, name, new_name):
        """
        :param name: old model name
        :type name: str
        :param new_name: new model name
        :type new_name: str
        :returns: updated model
        :rtype: dict
        """
        return Model.from_dict(self._post('registered-models/rename', name=name, new_name=new_name)['registered_model'])

    def create_model_version(self, name, source=None, run_id=None, **tags):
        """
        :param name: model name
        :type name: str
        :param source: model source path
        :type source: str
        :param run_id: run ID used for generating model
        :type run_id: str
        :returns: model version
        :rtype: dict
        """
        params = {}
        if source:
            params['source'] = source
        if run_id:
            params['run_id'] = run_id
        return ModelVersion.from_dict(self._post('model-versions/create', name=name, tags=tags, **params)['model_version'])

    def set_model_description(self, name, description):
        """
        :param name: model name
        :type name: str
        :param description: description
        :type description: str
        :returns: updated model
        :rtype: dict
        """
        return Model.from_dict(self._patch('registered-models/update', name=name, description=description)['registered_model'])


    def delete_model(self, name):
        """
        :param name: model name
        :type name: str
        :returns: model
        :rtype: dict
        """
        return self._post('registered-models/delete', name=name)


    def list_models(self, max_results=None, page_token=None):
        """
        :returns: models
        :rtype: list
        """
        params = {}
        if page_token:
            params['max_results'] = max_results
        if page_token:
            params['page_token'] = page_token
        return Model.from_list(self._get('registered-models/list', **params).get('registered_models', []))


    def search_models(self, query, max_results=None, order_by=None, page_token=None):
        """
        :param query: query to search
            Example:\
                "name LIKE 'some_model%'"
        :type query: dict
        :param max_results: max results to return
        :type max_results: int
        :param order_by: order by expression
            Example:
                ['name', 'version ASC']
        :type order_by: list
        :param version: models
        :type version: list
        """
        params = {
            'filter': query
        }
        if max_results:
            params['max_results'] = max_results
        if order_by:
            params['order_by'] = order_by
        if page_token:
            params['page_token'] = page_token

        response = self._get('registered-models/search', **params)
        return Page.from_dict(response, items_key='registered_models', item_class=Model)

    def search_models_iterator(self, query="", max_results=MAX_RESULTS, order_by=None, page_token=None):
        page = self.search_models(query=query, max_results=max_results, order_by=order_by, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_models(query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token)
            else:
                break


    def set_model_tag(self, name, key, value):
        """
        :param name: model name
        :type name: str
        :param key: tag name
        :type key: str
        :param value: tag value
        :type value: str
        """
        return self._post('registered-models/set-tag', name=name, key=key, value=value)


    def delete_model_tag(self, name, key):
        """
        :param name: model name
        :type name: str
        :param key: tag name
        :type key: str
        """
        return self._post('registered-models/delete-tag', name=name, key=key)


    def list_model_versions(self, name, stages=None):
        """
        :returns: model versions
        :rtype: list
        """
        params = {}
        if stages:
            if isinstance(stages, list):
                params['stages'] = [stage.value if isinstance(stage, ModelVersionStage) else stage for stage in stages]
            elif isinstance(stages, ModelVersionStage):
                params['stages'] = [stages.value]
            else:
                params['stages'] = [stages]
        return ModelVersion.from_list(self._get('registered-models/get-latest-versions', name=name, **params).get('model_versions', []))


    def create_model_version(self, name, source=None, run_id=None, **tags):
        """
        :param name: model name
        :type name: str
        :param source: model source path
        :type source: str
        :param run_id: run ID used for generating model
        :type run_id: str
        :returns: model version
        :rtype: dict
        """
        params = {}
        if source:
            params['source'] = source
        if run_id:
            params['run_id'] = run_id
        return ModelVersion.from_dict(self._post('model-versions/create', name=name, tags=self._handle_tags(tags), **params)['model_version'])


    def get_model_version(self, name, version):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :returns: model version
        :rtype: dict
        """
        return ModelVersion.from_dict(self._post('model-versions/get', name=name, version=str(version))['model_version'])


    def set_model_version_description(self, name, version, description):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :param description: new description
        :type description: str
        :returns: model version
        :rtype: dict
        """
        return ModelVersion.from_dict(self._patch('model-versions/update', name=name, version=str(version), description=description)['model_version'])


    def set_model_version_tag(self, name, version, key, value):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :param key: tag name
        :type key: str
        :param value: tag value
        :type value: str
        """
        return self._post('model-versions/set-tag', name=name, version=str(version), key=key, value=value)


    def delete_model_version_tag(self, name, version, key, value):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :param key: tag name
        :type key: str
        """
        return self._post('model-versions/delete-tag', name=name, version=str(version), key=key)


    def delete_model_version(self, name, version):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        """
        return self._post('model-versions/delete', name=name, version=str(version))


    def search_model_versions(self, query, max_results=None, order_by=None, page_token=None):
        """
        :param query: query to search
            Example:
                "name='some_model'"
        :type query: dict
        :param max_results: max results to return
        :type max_results: int
        :param order_by: order by expression
            Example:
                ['name', 'version ASC']
        :type order_by: list
        :param version: model versions
        :type version: list
        """
        params = {
            'filter': query
        }
        if max_results:
            params['max_results'] = max_results
        if order_by:
            params['order_by'] = order_by
        if page_token:
            params['page_token'] = page_token

        response = self._get('model-versions/search', **params)
        return Page.from_dict(response, items_key='model_versions', item_class=ModelVersion)


    def search_model_versions_iterator(self, query="", max_results=MAX_RESULTS, order_by=None, page_token=None):
        page = self.search_model_versions(query=query, max_results=max_results, order_by=order_by, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_model_versions(query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token)
            else:
                break


    def get_model_version_download_url(self, name, version):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :returns: artifact URL
        :rtype: str
        """
        return self._post('model-versions/get-download-uri', name=name, version=str(version)).get('artifact_uri')


    def transition_model_version_stage(self, name, version, stage=None, archive_existing=False):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :param stage: model version
        :type stage: ModelVersionStage
        :param archive_existing: pass `True` if previous model versions should be archived, default `False`
        :type archive_existing: bool
        :returns: new model version
        :rtype: dict
        """
        return ModelVersion.from_dict(
            self._post('model-versions/transition-stage', name=name, version=str(version), stage=stage.value,
                                                            archive_existing_versions=archive_existing)['model_version'])


    def test_model_version(self, name, version, **params):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :returns: new model version
        :rtype: dict
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.test, **params)


    def promote_model_version(self, name, version, **params):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :returns: new model version
        :rtype: dict
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.prod, **params)


    def archive_model_version(self, name, version, **params):
        """
        :param name: model name
        :type name: str
        :param version: model version
        :type version: str
        :returns: new model version
        :rtype: dict
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.archived, **params)

    def _handle_tags(self, tags):
        result = []
        for key, value in tags.items():
            result.append({'key': key, 'value': value})

        return result


    def _url(self, path):
        return "{base}/api/2.0/preview/mlflow/{path}".format(base=self.base_url, path=path)


    def _get(self, url, **query):
        """ Executes an HTTP GET call
        :param url: Relative url name such as runs/get.
        :type url: str
        :param query: GET query
        :type query: dict
        """
        resp = self._request('get', url, params=query)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _post(self, url, **data):
        """
        Executes an HTTP POST call
        :param path: Relative url name such as runs/get.
        :param data: JSON request payload.
        """
        resp = self._request('post', url, json=data)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _patch(self, url, **data):
        """
        Executes an HTTP PATCH call
        :param path: Relative url name such as runs/get.
        :param data: JSON request payload.
        """
        resp = self._request('patch', url, json=data)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _request(self, method, url, log_response=True, **params):
        url = self._url(url)

        if self._auth:
            params['auth'] = self._auth

        if self._ignore_ssl_check:
            params['verify'] = self._ignore_ssl_check

        self.logger.debug("api_client.{}: req: {}".format(method.upper(), params))
        self.logger.debug("api_client.{}: url: {}".format(method.upper(), url))
        resp = getattr(requests, method)(url, **params)
        resp.raise_for_status()

        if log_response:
            self.logger.debug("api_client.{}: rsp: {}".format(method.upper(), resp.text))

        return resp


    @property
    def _auth(self):
        if self.user and self.password:
            return (self.user, self.password)
        else:
            return None


    @property
    def _now(self):
        return int(time.time())
