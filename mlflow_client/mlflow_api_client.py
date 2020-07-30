
import json
import requests

from .artifact import Artifact
from .experiment import Experiment
from .log import get_logger
from .model import Model, ModelVersion, ModelVersionStage
from .page import Page
from .run import Run, RunInfo, RunViewType, RunStatus, Metric
from .timestamp import current_timestamp, time_2_timestamp

class MLflowApiClient(object):
    """ HTTP Client for MLflow API

        :param api_url: MLflow URL

            Example:
                "http://some.domain:5000
        :type api_url: str

        :ivar base_url: MLflow URL
        :vartype base_url: str

        :param user: MLflow user name (if exist)
        :type user: str, optional

        :ivar user: MLflow user name
        :vatype user: str

        :param password: MLflow user password (if exist)
        :type password: str, optional

        :param logger: Logger to use
        :type logger: logging.Logger, optional

        :ivar logger: Used logger
        :vartype logger: logging.Logger

        :param ignore_ssl_check: If `True`, skip SSL verify step
        :type ignore_ssl_check: bool
    """

    MAX_RESULTS = 100

    def __init__(self, api_url, user=None, password=None, logger=None, ignore_ssl_check=False):
        self.base_url = api_url
        self.user = user
        self._password = password
        self._ignore_ssl_check = ignore_ssl_check
        self.logger = logger if logger else get_logger()


    def list_experiments(self, view_type=RunViewType.active):
        """
        List all existing experiments in MLflow database

        :param view_type: View type
        :type view_type: RunViewType

        :returns: Experiments
        :rtype: :obj:`List` of :obj:`Experiment`
        """
        return Experiment.from_list(self._get('experiments/list', view_type=view_type.value).get('experiments', []))


    def list_experiments_iterator(self, view_type=RunViewType.active):
        """
        List all existing experiments in MLflow database

        :param view_type: View type
        :type view_type: RunViewType

        :returns: Experiments
        :rtype: Iterator[Experiment]
        """
        experiments = self.list_experiments(view_type=view_type)
        for experiment in experiments:
            yield experiment


    def get_experiment(self, id):
        """
        Get experiment by its id

        :param id: Experiment ID
        :type id: str

        :returns: Experiment
        :rtype: Experiment
        """
        return Experiment.from_dict(self._get('experiments/get', experiment_id=id)['experiment'])


    def get_experiment_by_name(self, name):
        """
        Get experiment by its name

        :param name: Experiment name
        :type name: str

        :returns: Experiment
        :rtype: Experiment, optional
        """
        id = self.get_experiment_id(name)
        if id:
            return self.get_experiment(id)
        return None


    def create_experiment(self, name, artifact_location=None):
        """
        Create experiment

        :param name: Experiment name
        :type name: str

        :param artifact_location: Path for artifacts
        :type artifact_location: str, optional

        :returns: New experiment
        :rtype: Experiment
        """
        params = {}
        if artifact_location:
            params['artifact_location'] = artifact_location

        experiment_id = self._post('experiments/create', name=name, **params)['experiment_id']
        return self.get_experiment(experiment_id)


    def rename_experiment(self, id, new_name):
        """
        Rename experiment

        :param id: Experiment ID
        :type id: str

        :param new_name: New experiment name
        :type new_name: str
        """
        self._post('experiments/update', experiment_id=id, new_name=new_name)


    def delete_experiment(self, id):
        """
        Delete experiment

        :param id: Experiment ID
        :type id: str
        """
        self._post('experiments/delete', experiment_id=id)


    def restore_experiment(self, id):
        """
        Restore experiment

        :param id: Experiment ID
        :type id: str
        """
        self._post('experiments/restore', experiment_id=id)


    def set_experiment_tag(self, id, key, value):
        """
        Set experiment tag

        :param id: Experiment ID
        :type id: str

        :param key: Tag name
        :type key: str

        :param value: Tag value
        :type value: str
        """
        self._post('experiments/set-experiment-tag', experiment_id=id, key=key, value=value)


    def get_experiment_id(self, name):
        """
        Get experiment id by name

        :param name: Experiment name
        :type name: str

        :returns: Experiment ID
        :rtype: Union[str]
        """
        exps = self.list_experiments()
        for exp in exps:
            if exp.name == name:
                return exp.id
        return None


    def get_or_create_experiment(self, name, artifact_location=None):
        """
        Get existing experiment by nabe or create new one

        :param name: Experiment name
        :type name: str

        :returns: Experiment
        :rtype: Experiment
        """
        id = self.get_experiment_id(name)
        if id is None:
            experiment = self.create_experiment(name, artifact_location)
        else:
            experiment = self.get_experiment(id)
        return experiment


    def list_experiment_runs(self, id):
        """
        List experiments

        :param id: Experiment ID
        :type id: str

        :returns: Runs
        :rtype: :obj:`List` of :obj:`Run`
        """
        return [run for run in self.list_experiment_runs_iterator(id)]


    def list_experiment_runs_iterator(self, id):
        """
        Iterate by experiments

        :param id: Experiment ID
        :type id: str

        :returns: Runs
        :rtype: Iterator[Run]
        """
        for run in self.search_runs_iterator(experiment_ids=[id]):
            yield run


    def get_run(self, id):
        """
        Get run by ID

        :param id: Run ID
        :type id: str

        :returns: Run
        :rtype: Run
        """
        return Run.from_dict(self._get('runs/get', run_id=id)['run'])


    def create_run(self, experiment_id, start_time=None, tags=None):
        """
        Create run

        :param experiment_id: Experiment ID
        :type experiment_id: str

        :param start_time: Start time
        :type start_time: :obj:`int` or :obj:`datetime.datetime`, optional

        :param tags: List of tags

            Example:
                `{'some': 'tag}` or `[{'key': 'some', 'value': 'tag']`
        :type tags: :obj:`dict`, :obj:`list` of :obj:`dict`, optional

        :returns: Run
        :rtype: Run
        """
        if not start_time:
            start_time = current_timestamp()

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)

        return Run.from_dict(self._post('runs/create', experiment_id=experiment_id, start_time=time_2_timestamp(start_time), tags=tags)['run'])


    def set_run_status(self, id, status, end_time=None):
        """
        Set run status

        :param id: Run ID
        :type id: str

        :param status: Run status
        :type status: RunStatus

        :param end_time: End time
        :type end_time: int or :obj:`datetime.datetime`, optional

        :returns: Run info
        :rtype: RunInfo
        """
        params = {
            'status': status.value
        }
        if end_time:
            params['end_time'] = time_2_timestamp(end_time)
        return RunInfo.from_dict(self._post('runs/update', run_id=id, **params)['run_info'])


    def start_run(self, id):
        """
        Change run status to STARTED

        :param id: Run ID
        :type id: str

        :returns: Run info
        :rtype: RunInfo
        """
        return self.set_run_status(id, RunStatus.started)


    def schedule_run(self, id):
        """
        Change run status to SCHEDULED

        :param id: Run ID
        :type id: str

        :returns: Run info
        :rtype: RunInfo
        """
        return self.set_run_status(id, RunStatus.scheduled)


    def finish_run(self, id, end_time=None):
        """
        Change run status to FINISHED

        :param id: Run ID
        :type id: str

        :param end_time: End time
        :type end_time: int or :obj:`datetime.datetime`, optional

        :returns: Run info
        :rtype: RunInfo
        """
        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(id, RunStatus.finished, end_time=time_2_timestamp(end_time))


    def fail_run(self, id, end_time=None):
        """
        Change run status to FAILED

        :param id: Run ID
        :type id: str

        :param end_time: End time
        :type end_time: int or :obj:`datetime.datetime`, optional

        :returns: Run info
        :rtype: RunInfo
        """
        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(id, RunStatus.failed, end_time=time_2_timestamp(end_time))


    def kill_run(self, id, end_time=None):
        """
        Change run status to KILLED

        :param id: Run ID
        :type id: str

        :param end_time: End time
        :type end_time: int or :obj:`datetime.datetime`, optional

        :returns: Run info
        :rtype: RunInfo
        """
        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(id, RunStatus.killed, end_time=time_2_timestamp(end_time))


    def delete_run(self, id):
        """
        Delete run

        :param id: Run ID
        :type id: str
        """
        self._post('runs/delete', run_id=id)


    def restore_run(self, id):
        """
        Restore run

        :param id: Run ID
        :type id: str
        """
        self._post('runs/restore', run_id=id)


    def log_run_parameter(self, id, key, value):
        """
        Add or update run parameter value

        :param id: Run ID
        :type id: str

        :param key: Parameter name
        :type key: str

        :param value: Parameter value
        :type value: str
        """
        self._post('runs/log-parameter', run_id=id, key=key, value=value)


    def log_run_parameters(self, id, params):
        """
        Add or update run parameters

        :param id: Run ID
        :type id: str

        :param params: Parameters

            Example:
                `{'some': 'param'}` or `[{'key': 'some', 'value': 'param'}]`
        :type params: Union[dict, :obj:`list` of :obj:`dict`]
        """

        if isinstance(params, dict):
            params = self._handle_tags(params)

        self.log_run_batch(id=id, params=params)


    def log_run_metric(self, id, key, value, step=0, timestamp=None):
        """
        Add or update run metric value

        :param id: Run ID
        :type id: str

        :param key: Metric name
        :type key: str

        :param value: Metric value
        :type value: str

        :param step: Step number
        :type step: int

        :param timestamp: Metric timestamp
        :type timestamp: int or :obj:`datetime.datetime`, optional
        """
        if not timestamp:
            timestamp = current_timestamp()
        dct = self._add_timestamp({'run_id': id, 'key': key, 'value': value, 'step': int(step)}, time_2_timestamp(timestamp))
        self._post('runs/log-metric', **dct)


    def log_run_metrics(self, id, metrics):
        """
        Add or update run parameters

        :param id: Run ID
        :type id: str

        :param metrics: Metrics

            Example:
                `{'some': 0.1}` or `[{'key': 'some', 'value': 0.1, 'step': 0, 'timestamp':...}]`
        :type metrics: Union[dict, :obj:`list` of :obj:`dict`]
        """
        timestamp = time_2_timestamp(current_timestamp())

        if isinstance(metrics, dict):
            metrics = self._handle_tags(metrics)

        metrics = [self._add_timestamp(metric, timestamp) for metric in metrics]

        self.log_run_batch(id=id, metrics=metrics)


    def log_run_batch(self, id, params=None, metrics=None, timestamp=None, tags=None):
        """
        Add or update run parameters, mertics or tags withit one request

        :param id: Run ID
        :type id: str

        :param params: List of params

            Example:
                `[{'key':..., 'value':...}]`
        :type params: :obj:`dict`, :obj:`list` of :obj:`dict`, optional

        :param metrics: List of metrics

            Example:
                `[{'key':..., 'value':...,'timestamp':...,'step':...}]`
        :type metrics: :obj:`dict`, :obj:`list` of :obj:`dict`, optional

        :param timestamp: Default timestamp for metric
        :type timestamp: int or :obj:`datetime.datetime`, optional

        :param tags: List of tags

            Example:
                `{'some': 'tag}` or `[{'key': 'some', 'value': 'tag']`
        :type tags: :obj:`dict`, :obj:`list` of :obj:`dict`, optional
        """

        if not timestamp:
            timestamp = current_timestamp()

        if not params:
            params = []
        if isinstance(params, dict):
            params = self._handle_tags(params)

        if not metrics:
            metrics = []
        if isinstance(metrics, dict):
            metrics = self._handle_tags(metrics)
        metrics = [self._add_timestamp(metric, time_2_timestamp(timestamp)) for metric in metrics]

        if not tags:
            tags = []
        if isinstance(metrics, dict):
            tags = self._handle_tags(tags)

        self._post('runs/log-batch', run_id=id, params=params, metrics=metrics, tags=tags)


    def log_run_model(self, id, model):
        """
        Add or update run model description

        :param id: Run ID
        :type id: str

        :param model: MLmodel JSON description
        :type model: dict
        """
        self._post('runs/log-model', run_id=id, model_json=model)


    def set_run_tag(self, id, key, value):
        """
        Set run tag

        :param id: Experiment ID
        :type id: str

        :param key: Tag name
        :type key: str

        :param value: Tag value
        :type value: str
        """
        self._post('runs/set-tag', run_id=id, key=key, value=value)


    def set_run_tags(self, id, tags):
        """
        Set run tags

        :param id: Run ID
        :type id: str

        :param tags: List of tags

            Example:
                `{'some': 'tag}` or `[{'key': 'some', 'value': 'tag']`
        :type tags: :obj:`dict`, :obj:`list` of :obj:`dict`, optional
        """

        if isinstance(tags, dict):
            tags = self._handle_tags(tags)

        self.log_run_batch(id=id, tags=tags)


    def delete_run_tag(self, id, key):
        """
        Delete run tag

        :param id: Experiment ID
        :type id: str

        :param key: Tag name
        :type key: str
        """
        self._post('runs/delete-tag', run_id=id, key=key)


    def delete_run_tags(self, id, keys):
        """
        Delete run tags

        :param id: Experiment ID
        :type id: str

        :param keys: Tag keys or tags

            Example:
                `['some'] or [{'key': 'some', 'value': 'tag']` or `{'some': 'tag}`
        :type keys: :obj:`dict`, :obj:`list` of :obj:`dict` or :obj:`list` of :obj:`str`
        """
        if isinstance(keys, dict):
            for tag in keys:
                self.delete_run_tag(id, tag)
        elif isinstance(keys, list):
            for tag in keys:
                if isinstance(tag, str):
                    self.delete_run_tag(id, tag)
                elif isinstance(tag, dict) and 'key' in tag:
                    self.delete_run_tag(id, tag['key'])


    def _add_timestamp(self, item, timestamp):
        if 'timestamp' in item and isinstance(item['timestamp'], int):
            return item

        item['timestamp'] = timestamp
        return item


    def list_run_metric_history(self, id, key):
        """
        LIst metric history

        :param id: Run ID
        :type id: str

        :param key: Metric name
        :type key: str

        :returns: Metrics
        :rtype: :obj:`List` of :obj:`Metric`
        """
        return Metric.from_list(self._get('metrics/get-history', run_id=id, metric_key=key)['metrics'])


    def list_run_metric_history_iterator(self, id, key):
        """
        Iterate by metric history

        :param id: Run ID
        :type id: str

        :param key: Metric name
        :type key: str

        :returns: Metrics
        :rtype: :obj:`Iterator` of :class:`mlflow_client.run.Metric`
        """
        for metric in self.list_run_metric_history(id, key):
            yield metric


    def list_run_artifacts(self, id, path=None, page_token=None):
        """
        List run artifacts

        :param id: Run ID
        :type id: str

        :param path: Artifacts path to search (can contain `*`)
        :type path: str, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :returns: Artifacts
        :rtype: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.artifact.Artifact`
        """
        params = {}
        if path:
            params['path'] = path
        if page_token:
            params['page_token'] = page_token
        response = self._get('artifacts/list', run_id=id, **params)

        return Page.from_dict(response, items_key='files', item_class=Artifact, root=response['root_uri'])


    def list_run_artifacts_iterator(self, id, path=None, page_token=None):
        """
        Iterate by run artifacts

        :param id: Run ID
        :type id: str

        :param path: Artifacts path to search
        :type path: str

        :param page_token: Previous page token
        :type page_token: str, optional

        :returns: Artifacts
        :rtype: Iterator[Artifact]
        """
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
        Search for runs

        :param query: Query to search

            Example:
                `"metrics.rmse < 1 and params.model_class = 'LogisticRegression'"`
        :type query: str

        :param experiment_ids: Experiment IDS
        :type experiment_ids: :obj:`List` of int

        :param run_view_type: View type
        :type run_view_type: RunViewType

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Runs
        :type version: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.run.Run`
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
        """
        Iterate by runs

        :param query: Query to search

            Example:
                `"metrics.rmse < 1 and params.model_class = 'LogisticRegression'"`
        :type query: str

        :param experiment_ids: Experiment IDS
        :type experiment_ids: :obj:`List` of int

        :param run_view_type: View type
        :type run_view_type: RunViewType

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Runs
        :type version: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.run.Run`
        """

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

    def create_model(self, name, tags=None):
        """
        Create model

        :param name: Model name
        :type name: str

        :param tags: List of tags

            Example:
                `{'some': 'tag}` or `[{'key': 'some', 'value': 'tag']`
        :type tags: :obj:`dict`, :obj:`list` of :obj:`dict`, optional

        :returns: Model
        :rtype: Model
        """

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)
        return Model.from_dict(self._post('registered-models/create', name=name, tags=tags)['registered_model'])

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
        Get model by name

        :param name: Model name
        :type name: str

        :returns: Model
        :rtype: Model
        """
        return Model.from_dict(self._get('registered-models/get', name=name)['registered_model'])

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
        Rename model

        :param name: Old model name
        :type name: str

        :param new_name: New model name
        :type new_name: str

        :returns: Updated model
        :rtype: Model
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
        Set model description

        :param name: Model name
        :type name: str

        :param description: Description
        :type description: str

        :returns: Updated model
        :rtype: Model
        """
        return Model.from_dict(self._patch('registered-models/update', name=name, description=description)['registered_model'])


    def delete_model(self, name):
        """
        Delete model

        :param name: Model name
        :type name: str
        """
        self._delete('registered-models/delete', name=name)


    def list_models(self, max_results=MAX_RESULTS, page_token=None):
        """
        List models

        :param max_results: Max results to return
        :type max_results: int

        :param page_token: Previous page token
        :type page_token: str, optional

        :returns: Models
        :rtype: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.model.Model`
        """
        params = {}
        if page_token:
            params['max_results'] = max_results
        if page_token:
            params['page_token'] = page_token
        response = self._get('registered-models/list', **params)
        return Page.from_dict(response, items_key='registered_models', item_class=Model)


    def list_models_iterator(self, max_results=MAX_RESULTS, page_token=None):
        """
        Iterate by models

        :param max_results: Max results to return
        :type max_results: int

        :param page_token: Previous page token
        :type page_token: str, optional

        :returns: Model
        :rtype: :obj:`Iterator` of :obj:`mlflow_client.model.Model`
        """
        page = self.list_models(max_results=max_results, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.list_models(max_results=max_results, page_token=page.next_page_token)
            else:
                break


    def search_models(self, query, max_results=None, order_by=None, page_token=None):
        """
        Search for models

        :param query: Query to search

            Example:
                "name LIKE 'some_model%'"
        :type query: str

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Models
        :type version: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.model.Model`
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
        """
        Iterate by models

        :param query: Query to search

            Example:
                "name LIKE 'some_model%'"
        :type query: str

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Models
        :type version: :obj:`Iterator` of :obj:`mlflow_client.model.Model`
        """

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
        Set model tag

        :param name: Model name
        :type name: str

        :param key: Tag name
        :type key: str

        :param value: Tag value
        :type value: str
        """
        self._post('registered-models/set-tag', name=name, key=key, value=value)


    def delete_model_tag(self, name, key):
        """
        Delete model tag

        :param name: Model name
        :type name: str

        :param key: Tag name
        :type key: str
        """
        self._delete('registered-models/delete-tag', name=name, key=key)


    def list_model_versions(self, name, stages=None):
        """
        List model versions

        :param name: Model name
        :type name: str

        :param stages: Model stages
        :type stages: :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional

        :returns: Model versions
        :rtype: List[ModelVersion]
        """
        params = {}
        if stages:
            if isinstance(stages, list):
                params['stages'] = [stage.value if isinstance(stage, ModelVersionStage) else stage for stage in stages]
            elif isinstance(stages, ModelVersionStage):
                params['stages'] = [stages.value]
            else:
                params['stages'] = [stages]
        response = self._get('registered-models/get-latest-versions', name=name, **params)
        return ModelVersion.from_list(response.get('model_versions', []))


    def list_model_versions_iterator(self, name, stages=None):
        """
        Iterate by models versions

        :param name: Model name
        :type name: str

        :param stages: Model stages
        :type stages: :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional

        :returns: Model versions
        :rtype: Iterator[ModelVersion]
        """
        versions = self.list_model_versions(name=name, stages=stages)
        for version in versions:
            yield version


    def create_model_version(self, name, source=None, run_id=None, tags=None):
        """
        Create model version

        :param name: Model name
        :type name: str

        :param source: Model source path
        :type source: str

        :param run_id: Run ID used for generating model
        :type run_id: str

        :param tags: List of tags

            Example:
                `{'some': 'tag}` or `[{'key': 'some', 'value': 'tag']`
        :type tags: :obj:`dict`, :obj:`list` of :obj:`dict`, optional

        :returns: Model version
        :rtype: ModelVersion
        """
        params = {}
        if source:
            params['source'] = source
        if run_id:
            params['run_id'] = run_id

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)
        return ModelVersion.from_dict(self._post('model-versions/create', name=name, tags=tags, **params)['model_version'])


    def get_model_version(self, name, version):
        """
        Get model version

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: int

        :returns: Model version
        :rtype: ModelVersion
        """
        return ModelVersion.from_dict(self._get('model-versions/get', name=name, version=str(version))['model_version'])


    def set_model_version_description(self, name, version, description):
        """
        Set model version description

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: int

        :param description: New description
        :type description: str

        :returns: Model version
        :rtype: ModelVersion
        """
        return ModelVersion.from_dict(self._patch('model-versions/update', name=name, version=str(version), description=description)['model_version'])


    def set_model_version_tag(self, name, version, key, value):
        """
        Set model version tag

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: int

        :param key: Tag name
        :type key: str

        :param value: Tag value
        :type value: str
        """
        self._post('model-versions/set-tag', name=name, version=str(version), key=key, value=value)


    def delete_model_version_tag(self, name, version, key):
        """
        Delete model version tag

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: int

        :param key: Tag name
        :type key: str
        """
        self._delete('model-versions/delete-tag', name=name, version=str(version), key=key)


    def delete_model_version(self, name, version):
        """
        Delete model version

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: int
        """
        self._delete('model-versions/delete', name=name, version=str(version))


    def search_model_versions(self, query, max_results=None, order_by=None, page_token=None):
        """
        Search for model versions

        :param query: Query to search

            Example:
                "name='some_model'"
        :type query: str

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Model versions
        :type version: List[ModelVersion]
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
        """
        Iterate by model versions

        :param query: Query to search

            Example:
                "name='some_model'"
        :type query: str

        :param max_results: Max results to return
        :type max_results: int

        :param order_by: Order by expression

            Example:
                ['name', 'version ASC']
        :type order_by: :obj:`list` of :obj:`str`, optional

        :param page_token: Previous page token
        :type page_token: str, optional

        :param version: Model versions
        :type version: Iterator[ModelVersion]
        """
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
        Get download URL for model artifact by version

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: str

        :returns: Artifact URL
        :rtype: str
        """
        return self._get('model-versions/get-download-uri', name=name, version=str(version)).get('artifact_uri')


    def transition_model_version_stage(self, name, version, stage, archive_existing=False):
        """
        Transition model version between stages

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: str

        :param stage: New model version stage
        :type stage: ModelVersionStage

        :param archive_existing: If `True`, previous model versions should be archived
        :type archive_existing: bool

        :returns: New model version
        :rtype: ModelVersion
        """
        return ModelVersion.from_dict(
            self._post('model-versions/transition-stage', name=name, version=str(version), stage=stage.value,
                                                            archive_existing_versions=archive_existing)['model_version'])


    def test_model_version(self, name, version, **params):
        """
        Change model version stage to Staging

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: str

        :param archive_existing: If `True`, previous model versions should be archived
        :type archive_existing: bool

        :returns: New model version
        :rtype: ModelVersion
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.test, **params)


    def promote_model_version(self, name, version, **params):
        """
        Change model version stage to Production

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: str

        :param archive_existing: If `True`, previous model versions should be archived
        :type archive_existing: bool

        :returns: New model version
        :rtype: ModelVersion
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.prod, **params)


    def archive_model_version(self, name, version, **params):
        """
        Change model version stage to Archived

        :param name: Model name
        :type name: str

        :param version: Model version
        :type version: str

        :param archive_existing: If `True`, previous model versions should be archived
        :type archive_existing: bool

        :returns: New model version
        :rtype: ModelVersion
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.archived, **params)


    def _handle_tags(self, tags):
        result = []
        for key, value in tags.items():
            dct = {'key': key, 'value': value}
            if hasattr(value, 'step'):
                dct['step'] = value.step
            result.append(dct)

        return result


    def _url(self, path):
        return "{base}/api/2.0/preview/mlflow/{path}".format(base=self.base_url, path=path)


    def _get(self, url, **query):
        resp = self._request('get', url, params=query)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _post(self, url, **data):
        resp = self._request('post', url, json=data)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _patch(self, url, **data):
        resp = self._request('patch', url, json=data)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        else:
            return None


    def _delete(self, url, **data):
        self._request('delete', url, json=data)


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
        if self.user and self._password:
            return (self.user, self._password)
        else:
            return None
