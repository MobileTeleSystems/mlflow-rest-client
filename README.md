# MLflow Python Client

A slightly opinionated Python client for [MLflow](https://mlflow.org) REST API that implements all REST operations.

See [mlflow_api_client.py](mlflow_client/mlflow_api_client.py) for client implementation.


## Build
Basic
```
pip install -r requirements.txt
```

Or, if you want to build an egg in dist folder  so you can deploy to a Databricks cluster.
```
python setup.py bdist_egg
```

## Run
Make sure you have an [MLflow Tracking Server](https://mlflow.org/docs/latest/tracking.html#running-a-tracking-server) running.

Run [sample.py](mlflow_client/sample/sample.py).
