# pylint: disable=too-many-lines

import json
from datetime import datetime
from typing import List

import requests
import urllib3
from pydantic import parse_obj_as

from .artifact import Artifact
from .experiment import Experiment
from .log import get_logger
from .model import ListableModelVersion, Model, ModelVersion, ModelVersionStage
from .page import Page
from .run import Metric, Run, RunInfo, RunStatus, RunViewType
from .timestamp import current_timestamp, format_to_timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# pylint: disable=too-many-public-methods
class MLflowApiClient:
    """HTTP Client for MLflow API

    Parameters
    ----------
    api_url : str
        MLflow URL

        Example:
            "http://some.domain:5000"

    user : str, optional
        MLflow user name (if exist)

    password : str, optional
        MLflow user password (if exist)

    logger : logging.Logger, optional
        Logger to use

    ignore_ssl_check : bool
        If `True`, skip SSL verify step

    Attributes
    ----------
    base_url : str
        MLflow URL

    user : str
        MLflow user name

    logger : logging.Logger
        Logger to use

    Examples
    --------
    .. code:: python

        client = MLflowApiClient("http://some.domain:5000")
    """

    MAX_RESULTS = 100

    # pylint: disable=too-many-arguments
    def __init__(self, api_url, user=None, password=None, logger=None, ignore_ssl_check=False):
        self.base_url = api_url
        self.logger = logger if logger else get_logger()

        self._session = requests.Session()
        self._session.verify = not ignore_ssl_check
        if user and password:
            self._session.auth = (user, password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()

    def list_experiments(self, view_type=RunViewType.ACTIVE):
        """
        List all existing experiments in MLflow database

        Parameters
        ----------
        view_type : :obj:`mlflow_client.run.RunViewType`, optional
            View type

        Returns
        ----------
        experiments_list: :obj:`mlflow_client.experiment.ExperimentList`
            Experiments list

        Examples
        --------
        .. code:: python

            experiments_list = client.list_experiments()

        """
        data = parse_obj_as(
            List[Experiment], self._get("experiments/list", view_type=view_type.value).get("experiments", [])
        )
        return data

    def list_experiments_iterator(self, view_type=RunViewType.ACTIVE):
        """
        Iterate by all existing experiments in MLflow database

        Parameters
        ----------
        view_type : :obj:`mlflow_client.run.RunViewType`, optional
            View type

        Returns
        ----------
        experiments_iterator: :obj:`Iterator` of :obj:`mlflow_client.experiment.Experiment`
            Experiments iterator

        Examples
        --------
        .. code:: python

            for experiment in client.list_experiments_iterator():
                print(experiment)
        """
        experiments = self.list_experiments(view_type=view_type)
        for experiment in experiments:
            yield experiment

    def get_experiment(self, id):
        """
        Get experiment by its id

        Parameters
        ----------
        id : int
            Experiment ID

        Returns
        ----------
        experiment: :obj:`mlflow_client.experiment.Experiment`
            Experiment

        Examples
        --------
        .. code:: python

            experiment = client.get_experiment(123)
        """
        data = self._get("experiments/get", experiment_id=id)["experiment"]
        return Experiment.parse_obj(data)

    def get_experiment_by_name(self, name):
        """
        Get experiment by its name

        Parameters
        ----------
        name : str
            Experiment name

        Returns
        ----------
        experiment: :obj:`mlflow_client.experiment.Experiment` or None
            Experiment, if exists

        Examples
        --------
        .. code:: python

            experiment = client.get_experiment_by_name("some_experiment")
        """
        experiment_id = self.get_experiment_id(name)
        if experiment_id:
            return self.get_experiment(experiment_id)
        return None

    def create_experiment(self, name, artifact_location=None):
        """
        Create experiment

        Parameters
        ----------
        name : str
            Experiment name

        artifact_location : str, optional
            Path for artifacts

        Returns
        ----------
        experiment: :obj:`mlflow_client.experiment.Experiment`
            New experiment

        Examples
        --------
        .. code:: python

            experiment = client.create_experiment("some_experiment")

            experiment = client.create_experiment("some_experiment", artifact_location="some/path")
        """
        params = {}
        if artifact_location:
            params["artifact_location"] = artifact_location

        experiment_id = self._post("experiments/create", name=name, **params)["experiment_id"]
        return self.get_experiment(experiment_id)

    def rename_experiment(self, id, new_name):
        """
        Rename experiment

        Parameters
        ----------
        id : int
            Experiment id

        new_name : str
            New experiment name

        Examples
        --------
        .. code:: python

            client.rename_experiment(123, "new_experiment")
        """
        self._post("experiments/update", experiment_id=id, new_name=new_name)

    def delete_experiment(self, id):
        """
        Delete experiment

        Parameters
        ----------
        id : int
            Experiment ID

        Examples
        --------
        .. code:: python

            client.delete_experiment(123)
        """
        self._post("experiments/delete", experiment_id=id)

    def restore_experiment(self, id):
        """
        Restore experiment

        Parameters
        ----------
        id : int
            Experiment ID

        Examples
        --------
        .. code:: python

            client.restore_experiment(123)
        """
        self._post("experiments/restore", experiment_id=id)

    def set_experiment_tag(self, id, key, value):
        """
        Set experiment tag

        Parameters
        ----------
        id : int
            Experiment ID

        key : str
            Tag name

        value : str
            Tag value

        Examples
        --------
        .. code:: python

            client.set_experiment_tag(123, "some.tag", "some.value")
        """
        self._post("experiments/set-experiment-tag", experiment_id=id, key=key, value=value)

    def get_experiment_id(self, name):
        """
        Get experiment id by name

        Parameters
        ----------
        name : str
            Experiment name

        Returns
        ----------
        id : str or None
            Experiment ID, if exists

        Examples
        --------
        .. code:: python

            experiment_id = client.get_experiment_id("some_experiment")
        """
        exps = self.list_experiments()
        for exp in exps:
            if exp.name == name:
                return exp.id
        return None

    def get_or_create_experiment(self, name, artifact_location=None):
        """
        Get existing experiment by name or create new one

        Parameters
        ----------
        name : str
            Experiment name

        artifact_location : str, optional
            Path for artifacts

        Returns
        ----------
        experiment : :obj:`mlflow_client.experiment.Experiment`
            New or existing experiment

        Examples
        --------
        .. code:: python

            experiment = client.get_or_create_experiment("some_experiment")
        """
        experiment_id = self.get_experiment_id(name)
        if experiment_id is None:
            experiment = self.create_experiment(name, artifact_location)
        else:
            experiment = self.get_experiment(experiment_id)
        return experiment

    def list_experiment_runs(self, id):
        """
        List experiments runs

        Parameters
        ----------
        id : int
            Experiment ID

        Returns
        ----------
        runs : :obj:`mlflow_client.run.RunList`
            Runs list

        Examples
        --------
        .. code:: python

            runs = client.list_experiment_runs(123)
        """
        data = [run for run in self.list_experiment_runs_iterator(id)]
        return parse_obj_as(List[Run], data)

    def list_experiment_runs_iterator(self, id):
        """
        Iterate by experiment runs

        Parameters
        ----------
        id : int
            Experiment ID

        Returns
        ----------
        runs : :obj:`Iterator` of :obj:`mlflow_client.run.Run`
            Runs iterator

        Examples
        --------
        .. code:: python

            for run in client.list_experiment_runs_iterator(123):
                print(run)
        """
        for run in self.search_runs_iterator(experiment_ids=[id]):
            yield run

    def get_run(self, id):
        """
        Get run by ID

        Parameters
        ----------
        id : str
            Run ID

        Returns
        ----------
        run : :obj:`mlflow_client.run.Run`
            Run

        Examples
        --------
        .. code:: python

            run = client.get_run("some_run_id")
        """
        return Run.parse_obj(self._get("runs/get", run_id=id)["run"])

    def create_run(self, experiment_id, start_time=None, tags=None):
        """
        Create run

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        start_time : :obj:`int` or :obj:`datetime.datetime`, optional
            Start time

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        ----------
        run : :obj:`mlflow_client.run.Run`
            Run

        Examples
        --------
        .. code:: python

            experiment_id = 123
            run = client.create_run(experiment_id)
            run = client.create_run(experiment_id, start_time=datetime.datetime.now())

            tags = {"some": "tag"}
            # or
            tags = [{"key": "some", "value": "tag"}]
            run = client.create_run(experiment_id, tags=tags)
        """
        if not start_time:
            start_time = current_timestamp()

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)

        data = self._post(
            "runs/create", experiment_id=experiment_id, start_time=format_to_timestamp(start_time), tags=tags
        )["run"]
        return Run.parse_obj(data)

    def set_run_status(self, id, status, end_time=None):
        """
        Set run status

        Parameters
        ----------
        id : str
            Run ID

        status : :obj:`str` or :obj:`mlflow_client.run.RunStatus`
            Run status

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.set_run_status("some_run_id", "FAILED")
            run_info = client.set_run_status("some_run_id", RunStatus.FAILED)
            run_info = client.set_run_status(
                "some_run_id", RunStatus.FINISHED, end_time=datetime.datetime.now()
            )
        """
        params = {"status": status.value}
        if end_time:
            params["end_time"] = format_to_timestamp(end_time)

        return RunInfo.parse_obj(self._post("runs/update", run_id=id, **params)["run_info"])

    def start_run(self, id):
        """
        Change run status to STARTED

        Parameters
        ----------
        id : str
            Run ID

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.start_run("some_run_id")
        """
        return self.set_run_status(id, RunStatus.STARTED)

    def schedule_run(self, id):
        """
        Change run status to SCHEDULED

        Parameters
        ----------
        id : str
            Run ID

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.schedule_run("some_run_id")
        """
        return self.set_run_status(id, RunStatus.SCHEDULED)

    def finish_run(self, id, end_time=None):
        """
        Change run status to FINISHED

        Parameters
        ----------
        id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.finish_run("some_run_id")
            run_info = client.finish_run("some_run_id", end_time=datetime.datetime.now())
        """
        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(id, RunStatus.FINISHED, end_time=format_to_timestamp(end_time))

    def fail_run(self, id, end_time=None):
        """
        Change run status to FAILED

        Parameters
        ----------
        id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.fail_run("some_run_id")
            run_info = client.fail_run("some_run_id", end_time=datetime.datetime.now())
        """
        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(id, RunStatus.FAILED, end_time=end_time)

    def kill_run(self, id, end_time: datetime = None):
        """
        Change run status to KILLED

        Parameters
        ----------
        id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        ----------
        run_info : :obj:`mlflow_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.kill_run("some_run_id")
            run_info = client.kill_run("some_run_id", end_time=datetime.datetime.now())
        """
        data = self.set_run_status(id, RunStatus.KILLED, end_time=format_to_timestamp(end_time))

        return data

    def delete_run(self, id):
        """
        Delete run

        Parameters
        ----------
        id : str
            Run ID

        Examples
        --------
        .. code:: python

            client.delete_run("some_run_id")
        """
        self._post("runs/delete", run_id=id)

    def restore_run(self, id):
        """
        Restore run

        Parameters
        ----------
        id : str
            Run ID

        Examples
        --------
        .. code:: python

            client.restore_run("some_run_id")
        """
        self._post("runs/restore", run_id=id)

    def log_run_parameter(self, id, key, value):
        """
        Add or update run parameter value

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Parameter name

        value : str
            Parameter value

        Examples
        --------
        .. code:: python

            client.log_run_parameter("some_run_id", "some.param", "some_value")
        """
        self._post("runs/log-parameter", run_id=id, key=key, value=value)

    def log_run_parameters(self, id, params):
        """
        Add or update run parameters

        Parameters
        ----------
        id : str
            Run ID

        params : :obj:`dict` or :obj:`list` of :obj:`dict`
            Parameters

        Examples
        --------
        .. code:: python

            params = {"some": "param"}
            # or
            params = [{"key": "some", "value": "param"}]
            client.log_run_parameters("some_run_id", params)
        """

        if isinstance(params, dict):
            params = self._handle_tags(params)

        self.log_run_batch(id=id, params=params)

    def log_run_metric(self, id, key, value, step=0, timestamp=None):
        """
        Add or update run metric value

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Metric name

        value : float
            Metric value

        step : int, optional
            Metric step (default: 0)

        timestamp : :obj:`int` or :obj:`datetime.datetime`, optional
            Metric timestamp

        Examples
        --------
        .. code:: python

            client.log_run_metric("some_run_id", "some.metric", 123)
            client.log_run_metric("some_run_id", "some.metric", 123, step=2)
            client.log_run_metric(
                "some_run_id", "some.metric", 123, timestamp=datetime.datetime.now()
            )
        """
        if not timestamp:
            timestamp = current_timestamp()
        dct = self._add_timestamp({"run_id": id, "key": key, "value": value, "step": int(step)}, int(timestamp))
        self._post("runs/log-metric", **dct)

    def log_run_metrics(self, id, metrics):
        """
        Add or update run parameters

        Parameters
        ----------
        id : str
            Run ID

        metrics : :obj:`dict` or :obj:`list` of :obj:`dict`
            Metrics

        Examples
        --------
        .. code:: python

            metrics = {"some": 0.1}
            # or
            metrics = [
                {"key": "some", "value": 0.1, "step": 0, "timestamp": datetime.datetime.now()}
            ]
            client.log_run_metrics("some_run_id", metrics)
        """
        timestamp = current_timestamp()

        if isinstance(metrics, dict):
            metrics = self._handle_tags(metrics)

        metrics = [self._add_timestamp(metric, timestamp) for metric in metrics]

        self.log_run_batch(id=id, metrics=metrics)

    def log_run_batch(self, id, params=None, metrics=None, timestamp=None, tags=None):
        """
        Add or update run parameters, mertics or tags withit one request

        Parameters
        ----------
        id : str
            Run ID

        params : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
            Params list

        metrics : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
            Metrics list

        timestamp : :obj:`int` or :obj:`datetime.datetime`, optional
            Run tags Default timestamp for metric

        tags : :obj:`dict` or :obj:`list` of :obj:`dict`, optional
            Run tags list

        Examples
        --------
        .. code:: python

            params = {"some": "param"}
            # or
            params = [{"key": "some", "value": "param"}]
            client.log_run_batch("some_run_id", params=params)

            metrics = {"some": 0.1}
            # or
            metrics = [
                {"key": "some", "value": 0.1, "step": 0, "timestamp": datetime.datetime.now()}
            ]
            client.log_run_batch("some_run_id", metrics=metrics)

            metrics = {"some": 0.1}
            # or
            metrics = [{"key": "some", "value": 0.1, "step": 0}]
            client.log_run_batch("some_run_id", metrics=metrics, timestamp=datetime.datetime.now())

            run_tags = {"some": "tag"}
            # or
            run_tags = [{"key": "some", "value": "param"}]

            client.log_run_batch("some_run_id", tags=run_tags)
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
        metrics = [self._add_timestamp(metric, int(timestamp)) for metric in metrics]

        if not tags:
            tags = []
        if isinstance(metrics, dict):
            tags = self._handle_tags(tags)

        self._post("runs/log-batch", run_id=id, params=params, metrics=metrics, tags=tags)

    def log_run_model(self, id, model):
        """
        Add or update run model description

        Parameters
        ----------
        id : str
            Run ID

        model : dict
            MLmodel JSON description

        Examples
        --------
        .. code:: python

            model = {
                "flavors": {
                    "sklearn": {"sklearn_version": "0.19.1", "pickled_model": "model.pkl"},
                    "python_function": {"loader_module": "mlflow.sklearn"},
                }
            }

            client.log_run_model("some_run_id", model)
        """
        self._post("runs/log-model", run_id=id, model_json=model)

    def set_run_tag(self, id, key, value):
        """
        Set run tag

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Tag name

        value : str
            Tag value

        Examples
        --------
        .. code:: python

            client.set_run_tag("some_run_id", "some.tag", "some.value")
        """
        self._post("runs/set-tag", run_id=id, key=key, value=value)

    def set_run_tags(self, id, tags):
        """
        Set run tags

        Parameters
        ----------
        id : str
            Run ID

        tags: :obj:`dict`, :obj:`list` of :obj:`dict`
            Run tags list

        Examples
        --------
        .. code:: python

            run_tags = {"some": "tag"}
            # or
            run_tags = [{"key": "some", "value": "param"}]

            client.set_run_tags("some_run_id", run_tags)
        """

        if isinstance(tags, dict):
            tags = self._handle_tags(tags)

        self.log_run_batch(id=id, tags=tags)

    def delete_run_tag(self, id, key):
        """
        Delete run tag

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Tag name

        Examples
        --------
        .. code:: python

            client.delete_run_tag("some_run_id", "some.tag")
        """
        self._post("runs/delete-tag", run_id=id, key=key)

    def delete_run_tags(self, id, keys):
        """
        Delete run tags

        Parameters
        ----------
        id : str
            Run ID

        tags: :obj:`dict`, :obj:`list` of :obj:`dict`
            Run tags list

        Examples
        --------
        .. code:: python

            run_tags = {"some": "tag"}
            # or
            run_tags = [{"key": "some", "value": "param"}]

            client.delete_run_tags("some_run_id", run_tags)
        """
        if isinstance(keys, dict):
            for tag in keys:
                self.delete_run_tag(id, tag)
        elif isinstance(keys, list):
            for tag in keys:
                if isinstance(tag, str):
                    self.delete_run_tag(id, tag)
                elif isinstance(tag, dict) and "key" in tag:
                    self.delete_run_tag(id, tag["key"])

    @staticmethod
    def _add_timestamp(item, timestamp):
        if "timestamp" in item and isinstance(item["timestamp"], int):
            return item

        item["timestamp"] = timestamp
        return item

    def list_run_metric_history(self, id, key):
        """
        List metric history

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Metric name

        Returns
        ----------
        metrics: :obj:`mlflow_client.run.MetricList`
            Metrics list

        Examples
        --------
        .. code:: python

            metrics_list = client.list_run_metric_history("some_run_id", "some.metric")
        """
        return parse_obj_as(List[Metric], self._get("metrics/get-history", run_id=id, metric_key=key)["metrics"])

    def list_run_metric_history_iterator(self, id, key):
        """
        Iterate by metric history

        Parameters
        ----------
        id : str
            Run ID

        key : str
            Metric name

        Returns
        ----------
        metrics: :obj:`Iterator` of :obj:`mlflow_client.run.Metric`
            Metrics iterator

        Examples
        --------
        .. code:: python

            for metric in client.list_run_metric_history_iterator("some_run_id", "some.metric"):
                print(metric)
        """
        for metric in self.list_run_metric_history(id, key):
            yield metric

    def list_run_artifacts(self, id, path=None, page_token=None):
        """
        List run artifacts

        Parameters
        ----------
        id : str
            Run ID

        path : str, optional
            Artifacts path to search (can contain `*`)

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        artifacts_page: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.artifact.Artifact`
            Artifacts page

        Examples
        --------
        .. code:: python

            artifacts_page = client.list_run_artifacts("some_run_id")
            artifacts_page = client.list_run_artifacts("some_run_id", path="some/path/*")
            artifacts_page = client.list_run_artifacts("some_run_id", page_token="next_page_id")
        """
        params = {}
        if path:
            params["path"] = path
        if page_token:
            params["page_token"] = page_token
        response = self._get("artifacts/list", run_id=id, **params)

        return Page.make(response, items_key="files", item_class=Artifact, root=response["root_uri"])

    def list_run_artifacts_iterator(self, id, path=None, page_token=None):
        """
        Iterate by run artifacts

        Like `list_run_artifacts`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------
        id : str
            Run ID

        path : str, optional
            Artifacts path to search (can contain `*`)

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        artifacts: :obj:`Iterator` of :obj:`mlflow_client.artifact.Artifact`
            Artifacts iterator

        Examples
        --------
        .. code:: python

            for artifact in client.list_run_artifacts_iterator("some_run_id"):
                print(artifact)

            for artifact in client.list_run_artifacts_iterator("some_run_id", path="some/path/*"):
                print(artifact)


            for artifact in client.list_run_artifacts_iterator(
                "some_run_id", page_token="next_page_id"
            ):
                print(artifact)
        """
        page = self.list_run_artifacts(id=id, path=path, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.list_run_artifacts(id=id, path=path, page_token=page.next_page_token)
            else:
                break

    def search_runs(
        self,
        experiment_ids,
        query="",
        run_view_type=RunViewType.ACTIVE,
        max_results=MAX_RESULTS,
        order_by=None,
        page_token=None,
    ):
        """
        Search for runs

        Parameters
        ----------
        experiment_ids : :obj:`list` of int
            Experiment IDS

        query : str, optional
            Query to search

        run_view_type : :obj:`mlflow_client.run.RunViewType`, optional
            View type

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        runs_page: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.run.Run`
            Runs page

        Examples
        --------
        .. code:: python

            experiment_ids = [123]

            runs_page = client.search_runs(experiment_ids)

            query = "metrics.rmse < 1 and params.model_class = 'LogisticRegression'"
            runs_page = client.search_runs(experiment_ids, query=query)

            order_by = ["name", "version ASC"]
            runs_page = client.search_runs(experiment_ids, order_by=order_by)

            runs_page = client.search_runs(experiment_ids, run_view_type=RunViewType.ALL)
            runs_page = client.search_runs(experiment_ids, max_results=100)
            runs_page = client.search_runs(experiment_ids, page_token="next_page_id")
        """

        if not isinstance(experiment_ids, list):
            experiment_ids = [experiment_ids]
        if not order_by:
            order_by = []

        params = {
            "experiment_ids": experiment_ids,
            "filter": query,
            "max_results": max_results,
            "run_view_type": run_view_type.value,
            "order_by": order_by,
        }
        if page_token:
            params["page_token"] = page_token
        response = self._post("runs/search", **params)
        return Page.make(response, items_key="runs", item_class=Run)

    def search_runs_iterator(
        self,
        experiment_ids,
        query="",
        run_view_type=RunViewType.ACTIVE,
        max_results=MAX_RESULTS,
        order_by=None,
        page_token=None,
    ):
        """
        Iterate by runs

        Like `search_runs`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------
        experiment_ids : :obj:`list` of int
            Experiment IDS

        query : str, optional
            Query to search

        run_view_type : :obj:`mlflow_client.run.RunViewType`, optional
            View type

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        runs: :obj:`Iterator` of :obj:`mlflow_client.run.Run`
            Runs iterator

        Examples
        --------
        .. code:: python

            experiment_ids = [123]

            for run in client.search_runs_iterator(experiment_ids):
                print(run)

            query = "metrics.rmse < 1 and params.model_class = 'LogisticRegression'"
            for run in client.search_runs_iterator(experiment_ids, query=query):
                print(run)

            order_by = ["name", "version ASC"]
            for run in client.search_runs_iterator(experiment_ids, order_by=order_by):
                print(run)

            for run in client.search_runs_iterator(experiment_ids, run_view_type=RunViewType.ALL):
                print(run)

            for run in client.search_runs_iterator(experiment_ids, max_results=100):
                print(run)

            for run in client.search_runs_iterator(experiment_ids, page_token="next_page_id"):
                print(run)
        """

        page = self.search_runs(
            experiment_ids=experiment_ids,
            query=query,
            run_view_type=run_view_type,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
        )
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_runs(
                    experiment_ids=experiment_ids,
                    query=query,
                    run_view_type=run_view_type,
                    max_results=max_results,
                    order_by=order_by,
                    page_token=page.next_page_token,
                )
            else:
                break

    def create_model(self, name, tags=None):
        """
        Create model

        Parameters
        ----------
        name : str
            Model name

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        ----------
        model: :obj:`mlflow_client.modelModel`
            New model

        Examples
        --------
        .. code:: python

            model = client.create_model("some_model")

            tags = {"some": "tag"}
            # or
            tags = [{"key": "some", "value": "tag"}]
            model = client.create_model("some_model", tags=tags)
        """

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)
        data = self._post("registered-models/create", name=name, tags=tags)["registered_model"]

        return Model.parse_obj(data)

    def get_model(self, name):
        """
        Get model by name

        Parameters
        ----------
        name: str
            Model name

        Returns
        ----------
        model : :obj:`mlflow_client.run.Model`
            Model

        Examples
        --------
        .. code:: python

            model = client.get_model("some_model")
        """
        return Model.parse_obj(self._get("registered-models/get", name=name)["registered_model"])

    def get_or_create_model(self, name, tags=None):
        """
        Get existing model by name or create new one

        Parameters
        ----------
        name : str
            Model name

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        ----------
        model: :obj:`mlflow_client.modelModel`
            New or existing model

        Examples
        --------
        .. code:: python

            model = client.get_or_create_model("some_model")

            tags = {"some": "tag"}
            # or
            tags = [{"key": "some", "value": "tag"}]
            model = client.get_or_create_model("some_model", tags=tags)
        """

        for model in self.search_models_iterator("name = '{name}'".format(name=name), max_results=1):
            return model
        return self.create_model(name, tags=tags)

    def rename_model(self, name, new_name):
        """
        Rename model

        Parameters
        ----------
        name : str
            Old model name

        new_name : str
            New model name

        Returns
        ----------
        model: :obj:`mlflow_client.model.Model`
            Updated model

        Examples
        --------
        .. code:: python

            model = client.rename_model("old_model", "new_model")
        """
        return Model.parse_obj(self._post("registered-models/rename", name=name, new_name=new_name)["registered_model"])

    def set_model_description(self, name, description):
        """
        Set model description

        Parameters
        ----------
        name : str
            Old model name

        description : str
            New model description

        Returns
        ----------
        model: :obj:`mlflow_client.model.Model`
            Updated model

        Examples
        --------
        .. code:: python

            model = client.set_model_description("some_model", "new description")
        """
        return Model.parse_obj(
            self._patch("registered-models/update", name=name, description=description)["registered_model"]
        )

    def delete_model(self, name):
        """
        Delete model

        Parameters
        ----------
        name : str
            Model name

        Examples
        --------
        .. code:: python

            client.delete_model("some_model")
        """
        self._delete("registered-models/delete", name=name)

    def list_models(self, max_results=MAX_RESULTS, page_token=None):
        """
        List models

        Parameters
        ----------
        max_results : int, optional
            Max results to return

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        models_page : :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.model.Model`
            Models page

        Examples
        --------
        .. code:: python

            models_page = client.list_models()
            models_page = client.list_models(max_results=1000)
            models_page = client.list_models(page_token="next_page_id")
        """
        params = {}
        if page_token:
            params["max_results"] = max_results
        if page_token:
            params["page_token"] = page_token
        response = self._get("registered-models/list", **params)
        return Page.make(response, items_key="registered_models", item_class=Model)

    def list_models_iterator(self, max_results=MAX_RESULTS, page_token=None):
        """
        Iterate by models

        Like `list_models`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------
        max_results : int, optional
            Max results to return

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        models : :obj:`Iterator` of :obj:`mlflow_client.model.Model`
            Models iterator

        Examples
        --------
        .. code:: python

            for model in client.list_models():
                print(model)

            for model in client.list_models(max_results=1000):
                print(model)

            for model in client.list_models(page_token="next_page_id"):
                print(model)
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

        Parameters
        ----------

        query : str
            Query to search

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        models_page: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.model.Model`
            Models page

        Examples
        --------
        .. code:: python

            query = "name = 'some_model%'"  # or "name LIKE "some-model%"'

            models_page = client.search_models(query)

            order_by = ["name", "version ASC"]
            models_page = client.search_models(query, order_by=order_by)

            models_page = client.search_models(query, max_results=100)
            models_page = client.search_models(query, page_token="next_page_id")
        """
        params = {"filter": query}
        if max_results:
            params["max_results"] = max_results
        if order_by:
            params["order_by"] = order_by
        if page_token:
            params["page_token"] = page_token

        response = self._get("registered-models/search", **params)
        return Page.make(response, items_key="registered_models", item_class=Model)

    def search_models_iterator(self, query="", max_results=MAX_RESULTS, order_by=None, page_token=None):
        """
        Iterate models found by search query

        Like `search_models`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------

        query : str
            Query to search

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        models: :obj:`Iterator` of :obj:`mlflow_client.model.Model`
            Models iterator

        Examples
        --------
        .. code:: python

            query = "name = 'some_model%'"  # or "name LIKE "some-model%"'

            for model in client.search_models_iterator(query):
                print(model)

            order_by = ["name", "version ASC"]
            for model in client.search_models_iterator(query, order_by=order_by):
                print(model)

            for model in client.search_models_iterator(query, max_results=100):
                print(model)

            for model in client.search_models_iterator(query, page_token="next_page_id"):
                print(model)
        """

        page = self.search_models(query=query, max_results=max_results, order_by=order_by, page_token=page_token)
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_models(
                    query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token
                )
            else:
                break

    def set_model_tag(self, name, key, value):
        """
        Set model tag

        Parameters
        ----------
        name : str
            Model name

        key : str
            Tag name

        value : str
            Tag value

        Examples
        --------
        .. code:: python

            client.set_model_tag("some_model", "some.tag", "some.value")
        """
        self._post("registered-models/set-tag", name=name, key=key, value=value)

    def delete_model_tag(self, name, key):
        """
        Delete model tag

        Parameters
        ----------
        name : str
            Model name

        key : str
            Tag name

        Examples
        --------
        .. code:: python

            client.delete_model_tag("some_model", "some.tag")
        """
        self._delete("registered-models/delete-tag", name=name, key=key)

    def list_model_versions(self, name, stages=None):
        """
        List model versions (only latest version of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        ----------
        model_versions_list : :obj:`mlflow_client.model.ModelVersionList`
            Model versions list

        Examples
        --------
        .. code:: python

            model_versions_list = client.list_model_versions("some_model")
            model_versions_list = client.list_model_versions(
                "some_model", stages=[ModelVersionStage.PROD]
            )
        """
        params = {}
        if stages:
            if isinstance(stages, list):
                params["stages"] = [stage.value if isinstance(stage, ModelVersionStage) else stage for stage in stages]
            elif isinstance(stages, ModelVersionStage):
                params["stages"] = [stages.value]
            else:
                params["stages"] = [stages]

        response = self._get("registered-models/get-latest-versions", name=name, **params)

        return ListableModelVersion.parse_obj(response.get("model_versions", []))

    def list_model_versions_iterator(self, name, stages=None):
        """
        Iterate by models versions (only latest version of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        ----------
        model_versions_iterator : :obj:`Iterator` or :obj:`mlflow_client.model.ModelVersion`
            Model versions iterator

        Examples
        --------
        .. code:: python

            for model_version in client.list_model_versions_iterator("some_model"):
                print(model_version)

            for model_version in client.list_model_versions_iterator(
                "some_model", stages=[ModelVersionStage.PROD]
            ):
                print(model_version)
        """
        versions = self.list_model_versions(name=name, stages=stages)
        for version in versions:
            yield version

    def list_model_all_versions(self, name, stages=None):
        """
        List model versions (all versions of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        ----------
        model_versions_list : :obj:`mlflow_client.model.ModelVersionList`
            Model versions list

        Examples
        --------
        .. code:: python

            model_versions_list = client.list_model_all_versions("some_model")
            model_versions_list = client.list_model_all_versions(
                "some_model", stages=[ModelVersionStage.PROD]
            )
        """
        return parse_obj_as(ListableModelVersion, self.list_model_all_versions_iterator(name=name, stages=stages))

    # pylint: disable=broad-except
    def list_model_all_versions_iterator(self, name, stages=None):
        """
        Iterate by models versions (all versions of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        ----------
        model_versions_iterator : :obj:`Iterator` or :obj:`mlflow_client.model.ModelVersion`
            Model versions iterator

        Examples
        --------
        .. code:: python

            for model_version in client.list_model_all_versions_iterator("some_model"):
                print(model_version)

            for model_version in client.list_model_all_versions_iterator(
                "some_model", stages=[ModelVersionStage.PROD]
            ):
                print(model_version)
        """

        _stages = None
        if stages:
            if isinstance(stages, list):
                _stages = [
                    ModelVersionStage(stage) if not isinstance(stage, ModelVersionStage) else stage for stage in stages
                ]
            else:
                _stages = [stages]

        max_version = -1
        for version in self.list_model_versions_iterator(name, stages):
            if version.version > max_version:
                max_version = version.version

        for i in range(0, max_version + 1):
            try:
                version = self.get_model_version(name, i)
                if _stages:
                    if version.stage in _stages:
                        yield version
                else:
                    yield version

            except Exception:  # nosec
                pass

    def create_model_version(self, name, source=None, run_id=None, tags=None):
        """
        Create model version

        Parameters
        ----------
        name : str
            Model name

        source : str
            Model version source path

        run_id : str
            Run ID used for generating model

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of model tags

        Returns
        ----------
        model_version : :obj:`mlflow_client.model.ModelVersion`
            ModelVersion

        Examples
        --------
        .. code:: python

            name = "some_model"
            model_version = client.create_model_version(name)

            source = "my_script.py"
            model_version = client.create_model_version(name, source=source)

            run_id = "some_run_id"
            model_version = client.create_model_version(name, run_id=run_id)

            tags = {"some": "tag"}
            # or
            tags = [{"key": "some", "value": "tag"}]
            model_version = client.create_model_version(name, tags=tags)
        """
        params = {}
        if source:
            params["source"] = source
        if run_id:
            params["run_id"] = run_id

        if not tags:
            tags = []
        if isinstance(tags, dict):
            tags = self._handle_tags(tags)

        return ModelVersion.parse_obj(
            self._post("model-versions/create", name=name, tags=tags, **params)["model_version"]
        )

    def get_model_version(self, name, version):
        """
        Get model version

        Parameters
        ----------
        name: str
            Model name

        version: int
            Version number

        Returns
        ----------
        model_version : :obj:`mlflow_client.run.ModelVersion`
            ModelVersion

        Examples
        --------
        .. code:: python

            model_version = client.get_model_version("some_model", 1)
        """
        return ModelVersion.parse_obj(self._get("model-versions/get", name=name, version=str(version))["model_version"])

    def set_model_version_description(self, name, version, description):
        """
        Set model version description

        Parameters
        ----------
        name : str
            Old model name

        version: int
            Version number

        description : str
            New model version description

        Returns
        ----------
        model_version: :obj:`mlflow_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.set_model_version_description("some_model", 1, "new description")
        """
        return ModelVersion.parse_obj(
            self._patch("model-versions/update", name=name, version=str(version), description=description)[
                "model_version"
            ]
        )

    def set_model_version_tag(self, name, version, key, value):
        """
        Set model version tag

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        key : str
            Tag name

        value : str
            Tag value

        Examples
        --------
        .. code:: python

            client.set_model_version_tag("some_model", 1, "some.tag", "some.value")
        """
        self._post("model-versions/set-tag", name=name, version=str(version), key=key, value=value)

    def delete_model_version_tag(self, name, version, key):
        """
        Delete model version tag

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        key : str
            Tag name

        Examples
        --------
        .. code:: python

            client.delete_model_version_tag("some_model", 1, "some.tag")
        """
        self._delete("model-versions/delete-tag", name=name, version=str(version), key=key)

    def delete_model_version(self, name, version):
        """
        Delete model version

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        Examples
        --------
        .. code:: python

            client.delete_model_version("some_model", 1)
        """
        self._delete("model-versions/delete", name=name, version=str(version))

    def search_model_versions(self, query, max_results=None, order_by=None, page_token=None):
        """
        Search for model versions

        Parameters
        ----------

        query : str
            Query to search

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        model_versions_page: :obj:`mlflow_client.page.Page` of :obj:`mlflow_client.model.ModelVersion`
            Model versions page

        Examples
        --------
        .. code:: python

            query = "name='some_model'"

            model_versions_page = client.search_model_versions(query)

            order_by = ["name", "version ASC"]
            model_versions_page = client.search_model_versions(query, order_by=order_by)

            model_versions_page = client.search_model_versions(query, max_results=100)
            model_versions_page = client.search_model_versions(query, page_token="next_page_id")
        """
        params = {"filter": query}
        if max_results:
            params["max_results"] = max_results
        if order_by:
            params["order_by"] = order_by
        if page_token:
            params["page_token"] = page_token

        response = self._get("model-versions/search", **params)
        return Page.make(response, items_key="model_versions", item_class=ModelVersion)

    def search_model_versions_iterator(self, query="", max_results=MAX_RESULTS, order_by=None, page_token=None):
        """
        Iterate by model versions

        Like `search_model_versions`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------

        query : str
            Query to search

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        ----------
        model_versions_iterator: :obj:`Iterator` of :obj:`mlflow_client.model.ModelVersion`
            Model versions iterator

        Examples
        --------
        .. code:: python

            query = "name='some_model'"

            for model_versions in client.search_model_versions(query):
                print(page)

            order_by = ["name", "version ASC"]
            for model_versions in client.search_model_versions_iterator(query, order_by=order_by):
                print(page)

            for model_versions in client.search_model_versions_iterator(query, max_results=100):
                print(page)
            for model_versions in client.search_model_versions_iterator(
                query, page_token="next_page_id"
            ):
                print(page)
        """
        page = self.search_model_versions(
            query=query, max_results=max_results, order_by=order_by, page_token=page_token
        )
        while True:
            for item in page:
                yield item
            if page.has_next_page:
                page = self.search_model_versions(
                    query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token
                )
            else:
                break

    def get_model_version_download_url(self, name, version):
        """
        Get download URL for model artifact by version

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        ----------
        download_url: str
            Artifact URL

        Examples
        --------
        .. code:: python

            download_url = client.get_model_version_download_url("some_model", 1)
        """
        return self._get("model-versions/get-download-uri", name=name, version=str(version)).get("artifact_uri")

    def transition_model_version_stage(self, name, version, stage, archive_existing=False):
        """
        Transition model version between stages

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        stage : :obj:`str` or :obj:`mlflow_client.model.ModelVersionStage`
            Model version state

        archive_existing : bool, optional
            If `True`, previous model versions should be archived

        Returns
        ----------
        model_version : :obj:`mlflow_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.transition_model_version_stage("some_run_id", 1, "Production")
            model_version = client.transition_model_version_stage(
                "some_run_id", 1, ModelVersionStage.PROD
            )
            model_version = client.transition_model_version_stage(
                "some_run_id", 1, ModelVersionStage.PROD, archive_existing=True
            )
        """
        return ModelVersion.parse_obj(
            self._post(
                "model-versions/transition-stage",
                name=name,
                version=str(version),
                stage=stage.value,
                archive_existing_versions=archive_existing,
            )["model_version"]
        )

    def test_model_version(self, name, version, **params):
        """
        Change model version stage to Staging

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        archive_existing : bool, optional
            If `True`, previous model versions should be archived

        Returns
        ----------
        model_version : :obj:`mlflow_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.test_model_version("some_run_id", 1)
            model_version = client.test_model_version("some_run_id", 1, archive_existing=True)
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.TEST, **params)

    def promote_model_version(self, name, version, **params):
        """
        Change model version stage to Production

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        archive_existing : bool, optional
            If `True`, previous model versions should be archived

        Returns
        ----------
        model_version : :obj:`mlflow_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.promote_model_version("some_run_id", 1)
            model_version = client.promote_model_version("some_run_id", 1, archive_existing=True)
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.PROD, **params)

    def archive_model_version(self, name, version, **params):
        """
        Change model version stage to Archived

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        Returns
        ----------
        model_version : :obj:`mlflow_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.archive_model_version("some_run_id", 1)
        """
        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.ARCHIVED, **params)

    @staticmethod
    def _handle_tags(tags):
        result = []
        for key, value in tags.items():
            dct = {"key": key, "value": value}
            if hasattr(value, "step"):
                dct["step"] = value.step
            result.append(dct)

        return result

    def _url(self, path):
        return "{base}/api/2.0/preview/mlflow/{path}".format(base=self.base_url, path=path)

    def _get(self, url, **query):
        resp = self._request("get", url, params=query)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        return None

    def _post(self, url, **data):
        resp = self._request("post", url, json=data)
        rsp = str(resp.text)

        if rsp:
            return json.loads(rsp)
        return None

    def _patch(self, url, **data):
        resp = self._request("patch", url, json=data)
        rsp = str(resp.text)
        if rsp:
            return json.loads(rsp)
        return None

    def _delete(self, url, **data):
        self._request("delete", url, json=data)

    # pylint: disable=logging-format-interpolation
    def _request(self, method, url, log_response=True, **params):
        url = self._url(url)

        self.logger.debug("api_client.{}: req: {}".format(method.upper(), params))
        self.logger.debug("api_client.{}: url: {}".format(method.upper(), url))
        resp = getattr(self._session, method)(url, **params)
        resp.raise_for_status()

        if log_response:
            self.logger.debug("api_client.{}: rsp: {}".format(method.upper(), resp.text))

        return resp
