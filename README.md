# MLflow Python Client
[![Build Status](https://jenkins.bd.msk.mts.ru/job/Platform/job/DSX/job/mlflow-client/badge/icon)](https://jenkins.bd.msk.mts.ru/job/Platform/job/DSX/job/mlflow-client)
[![Quality Gate Status](https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=alert_status)](https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client)
[![Maintainability Rating](https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=sqale_rating)](https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client)
[![Coverage](https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=coverage)](https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client)
[![Documentation](https://img.shields.io/badge/docs-latest-success)](https://mlflow-client.msk.bd-cloud.mts.ru)
[![PyPI](https://img.shields.io/badge/pypi-download-orange)](http://docker.rep.msk.mts.ru/ui/packages/pypi:%2F%2Fmlflow-client?name=%2Amlflow%2A&type=packages)

A slightly opinionated Python client for [MLflow](https://mlflow.org) REST API that implements all REST operations.

See [mlflow_api_client.py](mlflow_client/mlflow_api_client.py) for client implementation.


## Documentation
See https://mlflow-client.msk.bd-cloud.mts.ru/


## Installation
Basic
```bash
pip install mlflow-client
```

## Run
Make sure you have an [MLflow Tracking Server](https://mlflow.org/docs/latest/tracking.html#running-a-tracking-server) running.

Run [sample.py](sample/sample.py).
