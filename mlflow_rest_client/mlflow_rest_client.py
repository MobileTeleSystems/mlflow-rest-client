#  Copyright 2022 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# pylint: disable=too-many-lines

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Iterator, List
from uuid import UUID

import requests
import urllib3
from pydantic import parse_obj_as  # pylint: disable=no-name-in-module

from .artifact import Artifact
from .experiment import Experiment
from .model import (
    ListableModelVersion,
    Model,
    ModelVersion,
    ModelVersionStage,
    ModelVersionStageOrList,
)
from .page import Page
from .run import Metric, Run, RunId, RunInfo, RunStatus, RunViewType
from .tag import Tag, TagsListOrDict
from .timestamp import current_timestamp, format_to_timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class MLflowRESTClient:
    """Client for MLflow REST API

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

    token : str, optional
        MLflow user token (if exist)

    ignore_ssl_check : bool
        If `True`, skip SSL verify step

    Examples
    --------
    .. code:: python

        client = MLflowRESTClient(url="http://some.domain:5000")
        client_with_basic_auth = MLflowRESTClient(
            url="http://some.domain:5000",
            user="abc",
            password="cde",
        )
        client_with_token_auth = MLflowRESTClient(
            url="http://some.domain:5000",
            token="68036ad49a92d53d02cc10ddf5ec2802",
        )
        client_without_ssl_check = MLflowRESTClient(
            url="http://some.domain:5000",
            ignore_ssl_check=True,
        )
    """

    MAX_RESULTS = 100

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_url: str,
        user: str | None = None,
        password: str | None = None,
        token: str | None = None,
        ignore_ssl_check: bool = False,
    ):
        self._base_url = api_url
        self._session = requests.Session()
        self._session.verify = not ignore_ssl_check
        if user and password:
            self._session.auth = (user, password)
        elif token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()

    def list_experiments(self, view_type: RunViewType = RunViewType.ACTIVE) -> list[Experiment]:
        """
        List all existing experiments in MLflow database

        Parameters
        ----------
        view_type : :obj:`mlflow_rest_client.run.RunViewType`, optional
            View type

        Returns
        -------
        experiments_list: :obj:`mlflow_rest_client.experiment.ExperimentList`
            Experiments list

        Examples
        --------
        .. code:: python

            experiments_list = client.list_experiments()

        """

        data = parse_obj_as(
            List[Experiment],
            self._get("experiments/list", view_type=view_type.value).get("experiments", []),
        )
        return data

    def list_experiments_iterator(self, view_type: RunViewType = RunViewType.ACTIVE) -> Iterator[Experiment]:
        """
        Iterate by all existing experiments in MLflow database

        Parameters
        ----------
        view_type : :obj:`mlflow_rest_client.run.RunViewType`, optional
            View type

        Returns
        -------
        experiments_iterator: :obj:`Iterator` of :obj:`mlflow_rest_client.experiment.Experiment`
            Experiments iterator

        Examples
        --------
        .. code:: python

            for experiment in client.list_experiments_iterator():
                print(experiment)
        """

        experiments = self.list_experiments(view_type=view_type)
        yield from experiments

    def get_experiment(self, experiment_id: int) -> Experiment:
        """
        Get experiment by its id

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        Returns
        -------
        experiment: :obj:`mlflow_rest_client.experiment.Experiment`
            Experiment

        Examples
        --------
        .. code:: python

            experiment = client.get_experiment(123)
        """

        data = self._get("experiments/get", experiment_id=experiment_id).get("experiment")
        return Experiment.parse_obj(data)

    def get_experiment_by_name(self, name: str) -> Experiment | None:
        """
        Get experiment by its name

        Parameters
        ----------
        name : str
            Experiment name

        Returns
        -------
        experiment: :obj:`mlflow_rest_client.experiment.Experiment` or None
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

    def create_experiment(self, name: str, artifact_location: str | None = None) -> Experiment:
        """
        Create experiment

        Parameters
        ----------
        name : str
            Experiment name

        artifact_location : str, optional
            Path for artifacts

        Returns
        -------
        experiment: :obj:`mlflow_rest_client.experiment.Experiment`
            New experiment

        Examples
        --------
        .. code:: python

            experiment = client.create_experiment("some_experiment")

            experiment = client.create_experiment("some_experiment", artifact_location="some/path")
        """

        params: dict[str, str] = {}
        if artifact_location:
            params["artifact_location"] = artifact_location

        experiment_id = self._post("experiments/create", name=name, **params).get("experiment_id")
        return self.get_experiment(experiment_id)  # type: ignore[arg-type]

    def rename_experiment(self, experiment_id: int, new_name: str) -> None:
        """
        Rename experiment

        Parameters
        ----------
        experiment_id : int
            Experiment id

        new_name : str
            New experiment name

        Examples
        --------
        .. code:: python

            client.rename_experiment(123, "new_experiment")
        """

        self._post("experiments/update", experiment_id=experiment_id, new_name=new_name)

    def delete_experiment(self, experiment_id: int) -> None:
        """
        Delete experiment

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        Examples
        --------
        .. code:: python

            client.delete_experiment(123)
        """

        self._post("experiments/delete", experiment_id=experiment_id)

    def restore_experiment(self, experiment_id: int) -> None:
        """
        Restore experiment

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        Examples
        --------
        .. code:: python

            client.restore_experiment(123)
        """

        self._post("experiments/restore", experiment_id=experiment_id)

    def set_experiment_tag(self, experiment_id: int, key: str, value: str) -> None:
        """
        Set experiment tag

        Parameters
        ----------
        experiment_id : int
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

        self._post("experiments/set-experiment-tag", experiment_id=experiment_id, key=key, value=value)

    def get_experiment_id(self, name: str) -> int | None:
        """
        Get experiment id by name

        Parameters
        ----------
        name : str
            Experiment name

        Returns
        -------
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

    def get_or_create_experiment(self, name: str, artifact_location: str | None = None) -> Experiment:
        """
        Get existing experiment by name or create new one

        Parameters
        ----------
        name : str
            Experiment name

        artifact_location : str, optional
            Path for artifacts

        Returns
        -------
        experiment : :obj:`mlflow_rest_client.experiment.Experiment`
            New or existing experiment

        Examples
        --------
        .. code:: python

            experiment = client.get_or_create_experiment("some_experiment")
        """

        experiment_id = self.get_experiment_id(name)
        if experiment_id is not None:
            return self.get_experiment(experiment_id)

        return self.create_experiment(name, artifact_location)

    def list_experiment_runs(self, experiment_id: int) -> list[Run]:
        """
        List experiments runs

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        Returns
        -------
        runs : :obj:`list` of :obj:`mlflow_rest_client.run.Run`
            Runs list

        Examples
        --------
        .. code:: python

            runs = client.list_experiment_runs(123)
        """

        data = list(self.list_experiment_runs_iterator(experiment_id))
        return parse_obj_as(List[Run], data)

    def list_experiment_runs_iterator(self, experiment_id: int) -> Iterator:
        """
        Iterate by experiment runs

        Parameters
        ----------
        experiment_id : int
            Experiment ID

        Returns
        -------
        runs : :obj:`Iterator` of :obj:`mlflow_rest_client.run.Run`
            Runs iterator

        Examples
        --------
        .. code:: python

            for run in client.list_experiment_runs_iterator(123):
                print(run)
        """

        yield from self.search_runs_iterator(experiment_ids=[experiment_id])

    def get_run(self, run_id: RunId) -> Run:
        """
        Get run by ID

        Parameters
        ----------
        run_id : str
            Run ID

        Returns
        -------
        run : :obj:`mlflow_rest_client.run.Run`
            Run

        Examples
        --------
        .. code:: python

            run = client.get_run("some_run_id")
        """

        return Run.parse_obj(self._get("runs/get", run_id=UUID(str(run_id)).hex).get("run"))

    def create_run(
        self,
        experiment_id: int,
        start_time: int | datetime | None = None,
        tags: TagsListOrDict | None = None,
    ) -> Run:
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
        -------
        run : :obj:`mlflow_rest_client.run.Run`
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

        tags_list = self._handle_tags(tags)

        data = self._post(
            "runs/create",
            experiment_id=experiment_id,
            start_time=format_to_timestamp(start_time),
            tags=tags_list,
        ).get("run")
        return Run.parse_obj(data)

    def set_run_status(
        self,
        run_id: RunId,
        status: str | RunStatus,
        end_time: int | datetime | None = None,
    ) -> RunInfo:
        """
        Set run status

        Parameters
        ----------
        run_id : str
            Run ID

        status : :obj:`str` or :obj:`mlflow_rest_client.run.RunStatus`
            Run status

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
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

        params: dict[str, Any] = {"status": RunStatus(status).value}
        if end_time:
            params["end_time"] = format_to_timestamp(end_time)

        return RunInfo.parse_obj(self._post("runs/update", run_id=UUID(str(run_id)).hex, **params).get("run_info"))

    def start_run(self, run_id: RunId) -> RunInfo:
        """
        Change run status to STARTED

        Parameters
        ----------
        run_id : str
            Run ID

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.start_run("some_run_id")
        """
        return self.set_run_status(run_id, RunStatus.STARTED)

    def schedule_run(self, run_id: RunId) -> RunInfo:
        """
        Change run status to SCHEDULED

        Parameters
        ----------
        run_id : str
            Run ID

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.schedule_run("some_run_id")
        """

        return self.set_run_status(run_id, RunStatus.SCHEDULED)

    def finish_run(self, run_id: RunId, end_time: int | datetime | None = None) -> RunInfo:
        """
        Change run status to FINISHED

        Parameters
        ----------
        run_id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.finish_run("some_run_id")
            run_info = client.finish_run("some_run_id", end_time=datetime.datetime.now())
        """

        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(run_id, RunStatus.FINISHED, end_time=format_to_timestamp(end_time))

    def fail_run(self, run_id: RunId, end_time: int | datetime | None = None) -> RunInfo:
        """
        Change run status to FAILED

        Parameters
        ----------
        run_id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.fail_run("some_run_id")
            run_info = client.fail_run("some_run_id", end_time=datetime.datetime.now())
        """

        if not end_time:
            end_time = current_timestamp()
        return self.set_run_status(run_id, RunStatus.FAILED, end_time=end_time)

    def kill_run(self, run_id: RunId, end_time: int | datetime | None = None) -> RunInfo:
        """
        Change run status to KILLED

        Parameters
        ----------
        run_id : str
            Run ID

        end_time : :obj:`int` or :obj:`datetime.datetime`, optional
            End time

        Returns
        -------
        run_info : :obj:`mlflow_rest_client.run.Runinfo`
            Run info

        Examples
        --------
        .. code:: python

            run_info = client.kill_run("some_run_id")
            run_info = client.kill_run("some_run_id", end_time=datetime.datetime.now())
        """

        data = self.set_run_status(run_id, RunStatus.KILLED, end_time=format_to_timestamp(end_time))

        return data

    def delete_run(self, run_id: RunId) -> None:
        """
        Delete run

        Parameters
        ----------
        run_id : UUID
            Run ID

        Examples
        --------
        .. code:: python

            client.delete_run("some_run_id")
        """
        self._post("runs/delete", run_id=UUID(str(run_id)).hex)

    def restore_run(self, run_id: RunId) -> None:
        """
        Restore run

        Parameters
        ----------
        run_id : UUID
            Run ID

        Examples
        --------
        .. code:: python

            client.restore_run("some_run_id")
        """

        self._post("runs/restore", run_id=UUID(str(run_id)).hex)

    def log_run_parameter(self, run_id: RunId, key: str, value: str) -> None:
        """
        Add or update run parameter value

        Parameters
        ----------
        run_id : UUID
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

        self._post("runs/log-parameter", run_id=UUID(str(run_id)).hex, key=key, value=value)

    def log_run_parameters(self, run_id: RunId, params: TagsListOrDict) -> None:
        """
        Add or update run parameters

        Parameters
        ----------
        run_id : str
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

        params_list = self._handle_tags(params)
        self.log_run_batch(run_id=run_id, params=params_list)

    def log_run_metric(
        self,
        run_id: RunId,
        key: str,
        value: float,
        step: int = 0,
        timestamp: int | datetime | None = None,
    ) -> None:
        """
        Add or update run metric value

        Parameters
        ----------
        run_id : UUID
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

        dct = self._add_timestamp(
            {"run_id": UUID(str(run_id)).hex, "key": key, "value": value, "step": int(step)},
            format_to_timestamp(timestamp),
        )
        self._post("runs/log-metric", **dct)

    def log_run_metrics(
        self,
        run_id: RunId,
        metrics: TagsListOrDict,
        timestamp: int | datetime | None = None,
    ) -> None:
        """
        Add or update run parameters

        Parameters
        ----------
        run_id : str
            Run ID

        metrics : :obj:`dict` or :obj:`list` of :obj:`dict`
            Metrics

        timestamp : :obj:`int` or :obj:`datetime.datetime`, optional
            Metric timestamp

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

        if not timestamp:
            timestamp = current_timestamp()

        metrics_list = [
            self._add_timestamp(metric, format_to_timestamp(timestamp)) for metric in self._handle_tags(metrics)
        ]
        self.log_run_batch(run_id=run_id, metrics=metrics_list)

    def log_run_batch(
        self,
        run_id: RunId,
        params: TagsListOrDict | None = None,
        metrics: TagsListOrDict | None = None,
        timestamp: int | datetime | None = None,
        tags: TagsListOrDict | None = None,
    ) -> None:
        """
        Add or update run parameters, mertics or tags withit one request

        Parameters
        ----------
        run_id : UUID
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

        metrics_list = [
            self._add_timestamp(metric, format_to_timestamp(timestamp)) for metric in self._handle_tags(metrics)
        ]
        params_list = self._handle_tags(params)
        tags_list = self._handle_tags(tags)

        self._post(
            "runs/log-batch", run_id=UUID(str(run_id)).hex, params=params_list, metrics=metrics_list, tags=tags_list
        )

    def log_run_model(self, run_id: RunId, model: dict) -> None:
        """
        Add or update run model description

        Parameters
        ----------
        run_id : UUID
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

        self._post("runs/log-model", run_id=UUID(str(run_id)).hex, model_json=model)

    def set_run_tag(self, run_id: RunId, key: str, value: str) -> None:
        """
        Set run tag

        Parameters
        ----------
        run_id : UUID
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

        self._post("runs/set-tag", run_id=UUID(str(run_id)).hex, key=key, value=value)

    def set_run_tags(self, run_id: RunId, tags: TagsListOrDict) -> None:
        """
        Set run tags

        Parameters
        ----------
        run_id : str
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

        tags_list = self._handle_tags(tags)
        self.log_run_batch(run_id=run_id, tags=tags_list)

    def delete_run_tag(self, run_id: RunId, key: str) -> None:
        """
        Delete run tag

        Parameters
        ----------
        run_id : UUID
            Run ID

        key : str
            Tag name

        Examples
        --------
        .. code:: python

            client.delete_run_tag("some_run_id", "some.tag")
        """

        self._post("runs/delete-tag", run_id=UUID(str(run_id)).hex, key=key)

    def delete_run_tags(self, run_id: RunId, keys: TagsListOrDict | list[str]) -> None:
        """
        Delete run tags

        Parameters
        ----------
        run_id : str
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
            for key in keys:
                self.delete_run_tag(run_id, key)
        elif isinstance(keys, list):
            for tag in keys:
                if isinstance(tag, str):
                    self.delete_run_tag(run_id, tag)
                elif isinstance(tag, Tag):
                    self.delete_run_tag(run_id, tag.key)
                elif isinstance(tag, dict) and "key" in tag:
                    self.delete_run_tag(run_id, tag["key"])

    @staticmethod
    def _add_timestamp(item: dict, timestamp: int) -> dict:
        if "timestamp" in item and isinstance(item["timestamp"], int):
            return item

        item["timestamp"] = timestamp
        return item

    def list_run_metric_history(self, run_id: RunId, key: str) -> list[Metric]:
        """
        List metric history

        Parameters
        ----------
        run_id : UUID
            Run ID

        key : str
            Metric name

        Returns
        -------
        metrics: :obj:`mlflow_rest_client.run.Metric`
            Metrics list

        Examples
        --------
        .. code:: python

            metrics_list = client.list_run_metric_history("some_run_id", "some.metric")
        """

        return parse_obj_as(
            List[Metric],
            self._get("metrics/get-history", run_id=UUID(str(run_id)).hex, metric_key=key).get("metrics"),
        )

    def list_run_metric_history_iterator(self, run_id: RunId, key: str) -> Iterator[Metric]:
        """
        Iterate by metric history

        Parameters
        ----------
        run_id : str
            Run ID

        key : str
            Metric name

        Returns
        -------
        metrics: :obj:`Iterator` of :obj:`mlflow_rest_client.run.Metric`
            Metrics iterator

        Examples
        --------
        .. code:: python

            for metric in client.list_run_metric_history_iterator("some_run_id", "some.metric"):
                print(metric)
        """

        yield from self.list_run_metric_history(run_id, key)

    def list_run_artifacts(self, run_id: RunId, path: str | None = None, page_token: str | None = None) -> Page:
        """
        List run artifacts

        Parameters
        ----------
        run_id : UUID
            Run ID

        path : str, optional
            Artifacts path to search (can contain `*`)

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        -------
        artifacts_page: :obj:`mlflow_rest_client.page.Page` of :obj:`mlflow_rest_client.artifact.Artifact`
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
        response = self._get("artifacts/list", run_id=UUID(str(run_id)).hex, **params)

        return Page.make(response, items_key="files", item_class=Artifact, root=response["root_uri"])

    def list_run_artifacts_iterator(
        self,
        run_id: RunId,
        path: str | None = None,
        page_token: str | None = None,
    ) -> Iterator[Artifact]:
        """
        Iterate by run artifacts

        Like `list_run_artifacts`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------
        run_id : str
            Run ID

        path : str, optional
            Artifacts path to search (can contain `*`)

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        -------
        artifacts: :obj:`Iterator` of :obj:`mlflow_rest_client.artifact.Artifact`
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

        page = self.list_run_artifacts(run_id=run_id, path=path, page_token=page_token)
        while True:
            yield from page
            if page.has_next_page:
                page = self.list_run_artifacts(run_id=run_id, path=path, page_token=page.next_page_token)
            else:
                break

    def search_runs(
        self,
        experiment_ids: list[int],
        query: str = "",
        run_view_type: RunViewType = RunViewType.ACTIVE,
        max_results: int = MAX_RESULTS,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Page:
        """
        Search for runs

        Parameters
        ----------
        experiment_ids : :obj:`list` of int
            Experiment IDS

        query : str, optional
            Query to search

        run_view_type : :obj:`mlflow_rest_client.run.RunViewType`, optional
            View type

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        -------
        runs_page: :obj:`mlflow_rest_client.page.Page` of :obj:`mlflow_rest_client.run.Run`
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
        experiment_ids: list[int],
        query: str = "",
        run_view_type: RunViewType = RunViewType.ACTIVE,
        max_results: int = MAX_RESULTS,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Iterator[Run]:
        """
        Iterate by runs

        Like `search_runs`, but automatically fetches next page while iteration, until no pages left.

        Parameters
        ----------
        experiment_ids : :obj:`list` of int
            Experiment IDS

        query : str, optional
            Query to search

        run_view_type : :obj:`mlflow_rest_client.run.RunViewType`, optional
            View type

        max_results : int, optional
            Max results to return

        order_by : :obj:`list` of :obj:`str`, optional
            Order by expression

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        -------
        runs: :obj:`Iterator` of :obj:`mlflow_rest_client.run.Run`
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
            yield from page
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

    def create_model(self, name: str, tags: TagsListOrDict | None = None) -> Model:
        """
        Create model

        Parameters
        ----------
        name : str
            Model name

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        -------
        model: :obj:`mlflow_rest_client.modelModel`
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

        tags_list = self._handle_tags(tags)
        data = self._post("registered-models/create", name=name, tags=tags_list).get("registered_model")

        return Model.parse_obj(data)

    def get_model(self, name: str) -> Model:
        """
        Get model by name

        Parameters
        ----------
        name: str
            Model name

        Returns
        -------
        model : :obj:`mlflow_rest_client.run.Model`
            Model

        Examples
        --------
        .. code:: python

            model = client.get_model("some_model")
        """

        return Model.parse_obj(self._get("registered-models/get", name=name).get("registered_model"))

    def get_or_create_model(self, name: str, tags: TagsListOrDict | None = None) -> Model:
        """
        Get existing model by name or create new one

        Parameters
        ----------
        name : str
            Model name

        tags : :obj:`dict`, :obj:`list` of :obj:`dict`, optional
            List of run tags

        Returns
        -------
        model: :obj:`mlflow_rest_client.modelModel`
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

        for model in self.search_models_iterator(f"name = '{name}'", max_results=1):
            return model
        return self.create_model(name, tags=tags)

    def rename_model(self, name: str, new_name: str) -> Model:
        """
        Rename model

        Parameters
        ----------
        name : str
            Old model name

        new_name : str
            New model name

        Returns
        -------
        model: :obj:`mlflow_rest_client.model.Model`
            Updated model

        Examples
        --------
        .. code:: python

            model = client.rename_model("old_model", "new_model")
        """

        return Model.parse_obj(
            self._post("registered-models/rename", name=name, new_name=new_name).get("registered_model")
        )

    def set_model_description(self, name: str, description: str) -> Model:
        """
        Set model description

        Parameters
        ----------
        name : str
            Old model name

        description : str
            New model description

        Returns
        -------
        model: :obj:`mlflow_rest_client.model.Model`
            Updated model

        Examples
        --------
        .. code:: python

            model = client.set_model_description("some_model", "new description")
        """

        return Model.parse_obj(
            self._patch("registered-models/update", name=name, description=description).get("registered_model"),
        )

    def delete_model(self, name: str) -> None:
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

    def list_models(self, max_results: int = MAX_RESULTS, page_token: str | None = None) -> Page:
        """
        List models

        Parameters
        ----------
        max_results : int, optional
            Max results to return

        page_token : str, optional
            Previous page token, to start search from next page

        Returns
        -------
        models_page : :obj:`mlflow_rest_client.page.Page` of :obj:`mlflow_rest_client.model.Model`
            Models page

        Examples
        --------
        .. code:: python

            models_page = client.list_models()
            models_page = client.list_models(max_results=1000)
            models_page = client.list_models(page_token="next_page_id")
        """

        params: dict[str, Any] = {}
        if page_token:
            params["max_results"] = max_results
        if page_token:
            params["page_token"] = page_token

        response = self._get("registered-models/list", **params)
        return Page.make(response, items_key="registered_models", item_class=Model)

    def list_models_iterator(self, max_results: int = MAX_RESULTS, page_token: str | None = None) -> Iterator:
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
        -------
        models : :obj:`Iterator` of :obj:`mlflow_rest_client.model.Model`
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
            yield from page
            if page.has_next_page:
                page = self.list_models(max_results=max_results, page_token=page.next_page_token)
            else:
                break

    def search_models(
        self,
        query: str,
        max_results: int | None = None,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Page:
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
        -------
        models_page: :obj:`mlflow_rest_client.page.Page` of :obj:`mlflow_rest_client.model.Model`
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

        params: dict[str, Any] = {"filter": query}
        if max_results:
            params["max_results"] = max_results
        if order_by:
            params["order_by"] = order_by
        if page_token:
            params["page_token"] = page_token

        response = self._get("registered-models/search", **params)
        return Page.make(response, items_key="registered_models", item_class=Model)

    def search_models_iterator(
        self,
        query: str,
        max_results: int = MAX_RESULTS,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Iterator:
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
        -------
        models: :obj:`Iterator` of :obj:`mlflow_rest_client.model.Model`
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
            yield from page
            if page.has_next_page:
                page = self.search_models(
                    query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token
                )
            else:
                break

    def set_model_tag(self, name: str, key: str, value: str) -> None:
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

    def delete_model_tag(self, name: str, key: str):
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

    def list_model_versions(
        self,
        name: str,
        stages: ModelVersionStageOrList | None = None,
    ) -> ListableModelVersion:
        """
        List model versions (only latest version of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_rest_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        -------
        model_versions_list : :obj:`mlflow_rest_client.model.ModelVersionList`
            Model versions list

        Examples
        --------
        .. code:: python

            model_versions_list = client.list_model_versions("some_model")
            model_versions_list = client.list_model_versions(
                "some_model", stages=[ModelVersionStage.PROD]
            )
        """

        params: dict[str, Any] = {}
        if stages:
            stages_list: list[str]

            if isinstance(stages, list):
                stages_list = [ModelVersionStage(stage).value for stage in stages]
            else:
                stages_list = [ModelVersionStage(stages).value]

            params["stages"] = stages_list

        response = self._get("registered-models/get-latest-versions", name=name, **params)

        return ListableModelVersion.parse_obj(response.get("model_versions", []))

    def list_model_versions_iterator(
        self,
        name: str,
        stages: ModelVersionStageOrList | None = None,
    ) -> Iterator:
        """
        Iterate by models versions (only latest version of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_rest_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        -------
        model_versions_iterator : :obj:`Iterator` or :obj:`mlflow_rest_client.model.ModelVersion`
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
        yield from versions

    def list_model_all_versions(
        self,
        name: str,
        stages: ModelVersionStageOrList | None = None,
    ) -> ListableModelVersion:
        """
        List model versions (all versions of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_rest_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        -------
        model_versions_list : :obj:`mlflow_rest_client.model.ModelVersionList`
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
    def list_model_all_versions_iterator(
        self,
        name: str,
        stages: ModelVersionStageOrList | None = None,
    ) -> Iterator:
        """
        Iterate by models versions (all versions of each stage)

        Parameters
        ----------
        name : str
            Model name

        stages : :obj:`list` of :obj:`mlflow_rest_client.model.ModelVersionStage` or :obj:`list` of :obj:`str`, optional
            Model stages to fetch

        Returns
        -------
        model_versions_iterator : :obj:`Iterator` or :obj:`mlflow_rest_client.model.ModelVersion`
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

        _stages: list[ModelVersionStage] = []
        if stages:
            if isinstance(stages, list):
                _stages = [ModelVersionStage(stage) for stage in stages]
            else:
                _stages = [ModelVersionStage(stages)]

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

    def create_model_version(
        self,
        name: str,
        source: str | None = None,
        run_id: str | None = None,
        tags: TagsListOrDict | None = None,
    ) -> ModelVersion:
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
        -------
        model_version : :obj:`mlflow_rest_client.model.ModelVersion`
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
            params["run_id"] = UUID(str(run_id)).hex

        tags_list = self._handle_tags(tags)

        return ModelVersion.parse_obj(
            self._post("model-versions/create", name=name, tags=tags_list, **params).get("model_version"),
        )

    def get_model_version(self, name: str, version: int) -> ModelVersion:
        """
        Get model version

        Parameters
        ----------
        name: str
            Model name

        version: int
            Version number

        Returns
        -------
        model_version : :obj:`mlflow_rest_client.run.ModelVersion`
            ModelVersion

        Examples
        --------
        .. code:: python

            model_version = client.get_model_version("some_model", 1)
        """

        return ModelVersion.parse_obj(
            self._get("model-versions/get", name=name, version=str(version)).get("model_version")
        )

    def set_model_version_description(self, name: str, version: int, description: str) -> ModelVersion:
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
        -------
        model_version: :obj:`mlflow_rest_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.set_model_version_description("some_model", 1, "new description")
        """

        return ModelVersion.parse_obj(
            self._patch("model-versions/update", name=name, version=str(version), description=description).get(
                "model_version"
            )
        )

    def set_model_version_tag(self, name: str, version: int, key: str, value: str) -> None:
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

    def delete_model_version_tag(self, name: str, version: int, key: str) -> None:
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

    def delete_model_version(self, name: str, version: int) -> None:
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

    def search_model_versions(
        self,
        query: str,
        max_results: int | None = None,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Page:
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
        -------
        model_versions_page: :obj:`mlflow_rest_client.page.Page` of :obj:`mlflow_rest_client.model.ModelVersion`
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

        params: dict[str, Any] = {"filter": query}
        if max_results:
            params["max_results"] = max_results
        if order_by:
            params["order_by"] = order_by
        if page_token:
            params["page_token"] = page_token

        response = self._get("model-versions/search", **params)
        return Page.make(response, items_key="model_versions", item_class=ModelVersion)

    def search_model_versions_iterator(
        self,
        query: str,
        max_results: int = MAX_RESULTS,
        order_by: list[str] | None = None,
        page_token: str | None = None,
    ) -> Iterator:
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
        -------
        model_versions_iterator: :obj:`Iterator` of :obj:`mlflow_rest_client.model.ModelVersion`
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
            yield from page
            if page.has_next_page:
                page = self.search_model_versions(
                    query=query, max_results=max_results, order_by=order_by, page_token=page.next_page_token
                )
            else:
                break

    def get_model_version_download_url(self, name: str, version: int) -> str | None:
        """
        Get download URL for model artifact by version

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        Returns
        -------
        download_url: str
            Artifact URL

        Examples
        --------
        .. code:: python

            download_url = client.get_model_version_download_url("some_model", 1)
        """

        return self._get("model-versions/get-download-uri", name=name, version=str(version)).get("artifact_uri")

    def transition_model_version_stage(
        self,
        name: str,
        version: int,
        stage: str | ModelVersionStage,
        archive_existing: bool = False,
    ) -> ModelVersion:
        """
        Transition model version between stages

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        stage : :obj:`str` or :obj:`mlflow_rest_client.model.ModelVersionStage`
            Model version state

        archive_existing : bool, optional
            If `True`, previous model versions should be archived

        Returns
        -------
        model_version : :obj:`mlflow_rest_client.model.ModelVersion`
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
                stage=ModelVersionStage(stage).value,
                archive_existing_versions=archive_existing,
            )["model_version"]
        )

    def test_model_version(self, name: str, version: int, **params) -> ModelVersion:
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
        -------
        model_version : :obj:`mlflow_rest_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.test_model_version("some_run_id", 1)
            model_version = client.test_model_version("some_run_id", 1, archive_existing=True)
        """

        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.TEST, **params)

    def promote_model_version(self, name: str, version: int, **params) -> ModelVersion:
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
        -------
        model_version : :obj:`mlflow_rest_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.promote_model_version("some_run_id", 1)
            model_version = client.promote_model_version("some_run_id", 1, archive_existing=True)
        """

        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.PROD, **params)

    def archive_model_version(self, name: str, version: int, **params) -> ModelVersion:
        """
        Change model version stage to Archived

        Parameters
        ----------
        name : str
            Model name

        version: int
            Version number

        Returns
        -------
        model_version : :obj:`mlflow_rest_client.model.ModelVersion`
            Updated model version

        Examples
        --------
        .. code:: python

            model_version = client.archive_model_version("some_run_id", 1)
        """

        return self.transition_model_version_stage(name, version, stage=ModelVersionStage.ARCHIVED, **params)

    @staticmethod
    def _handle_tags(tags: TagsListOrDict | None) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []

        if not tags:
            return result

        if isinstance(tags, dict):
            for key, value in tags.items():
                dct = {"key": key, "value": value}

                step = getattr(value, "step", None)
                if step is not None:
                    dct["step"] = step

                result.append(dct)
        else:
            result = tags  # type: ignore[assignment]

        return result

    def _url(self, path: str) -> str:
        return f"{self._base_url}/api/2.0/preview/mlflow/{path}"

    def _get(self, url: str, **query) -> dict:
        resp = self._request("get", url, params=query)
        if not resp.text:
            return {}

        return resp.json()

    def _post(self, url: str, **data) -> dict:
        resp = self._request("post", url, json=data)
        if not resp.text:
            return {}

        return resp.json()

    def _patch(self, url: str, **data) -> dict:
        resp = self._request("patch", url, json=data)
        if not resp.text:
            return {}

        return resp.json()

    def _delete(self, url: str, **data) -> None:
        self._request("delete", url, json=data)

    # pylint: disable=logging-format-interpolation
    def _request(self, method: str, url: str, log_response: bool = True, **params) -> requests.Response:
        url = self._url(url)

        log.debug(f"api_client.{method.upper()}: req: {params}")
        log.debug(f"api_client.{method.upper()}: url: {url}")

        resp = getattr(self._session, method)(url, **params)
        resp.raise_for_status()

        if log_response:
            log.debug(f"api_client.{method.upper()}: rsp: {resp.text}")

        return resp
