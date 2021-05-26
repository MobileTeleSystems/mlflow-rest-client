import logging
import os
import random
import string
from datetime import datetime

import pytest

from mlflow_client import MLflowApiClient

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


def rand_str(length=8):
    letters = string.ascii_lowercase
    return "".join(random.sample(letters, length))


def rand_int(a=0, b=100):
    return random.randint(a, b)


def rand_float(a=0, b=100):
    return random.uniform(a, b)


def create_exp_name():
    return "pyTestExp-" + rand_str()


def create_model_name():
    return "pyTestModel-" + rand_str()


def now():
    return datetime.now().replace(microsecond=0)


@pytest.yield_fixture(scope="session")
def client():
    host = os.environ["MLFLOW_HOST"] or "localhost"
    port = os.environ["MLFLOW_PORT"] or "5000"
    api_url = "http://{host}:{port}".format(host=host, port=port)
    with MLflowApiClient(api_url) as client:
        yield client


@pytest.fixture(scope="function")
def create_experiment(request, client):
    exp_name = create_exp_name()
    exp = client.create_experiment(exp_name)

    def finalizer():
        client.delete_experiment(exp.id)

    request.addfinalizer(finalizer)

    return exp


@pytest.fixture(scope="function")
def create_run(request, client, create_experiment):
    exp = create_experiment
    run = client.create_run(experiment_id=exp.id)

    def finalizer():
        client.delete_run(run.id)

    request.addfinalizer(finalizer)

    return run


@pytest.fixture(scope="function")
def create_model(request, client):
    model_name = create_model_name()
    model = client.create_model(model_name)

    def finalizer():
        client.delete_model(model.name)

    request.addfinalizer(finalizer)

    return model


@pytest.fixture(scope="function")
def create_model_version(request, client, create_model):
    model = create_model

    version = client.create_model_version(model.name)

    def finalizer():
        client.delete_model_version(version.name, version.version)

    request.addfinalizer(finalizer)

    return version


@pytest.fixture(scope="function")
def create_test_model_version(client, create_model_version):
    version = create_model_version

    new_version = client.test_model_version(version.name, version.version)

    return new_version


@pytest.fixture(scope="function")
def create_prod_model_version(client, create_model_version):
    version = create_model_version

    new_version = client.promote_model_version(version.name, version.version)

    return new_version


@pytest.fixture(scope="function")
def create_archived_model_version(client, create_model_version):
    version = create_model_version

    new_version = client.archive_model_version(version.name, version.version)

    return new_version
