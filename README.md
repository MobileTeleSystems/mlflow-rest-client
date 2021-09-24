# MLflow Python Client

A slightly opinionated Python client for [MLflow](https://mlflow.org) REST API that implements all REST operations.

See [mlflow_api_client.py](mlflow_client/mlflow_api_client.py) for client implementation.


## Build
Basic
```
pip install -r requirements.txt
```

Of if you want to build an egg in dist folder  so you can deploy to a Databricks cluster.
```
python setup.py bdist_egg
```

## Run
Make sure you have an [MLflow Tracking Server](https://mlflow.org/docs/latest/tracking.html#running-a-tracking-server) running.

Run [sample.py](mlflow_client/sample/sample.py).

```
cd mlflow_client
python sample.py http://localhost:5000
```

Output from [samples/out.log](samples/out.log).
```
api_client: base_uri: http://localhost:5011/api/2.0/preview/mlflow
====== get_experiments
api_client.GET: url: http://localhost:5011/api/2.0/preview/mlflow/experiments/list
api_client.GET: rsp: {
  "experiments": [
    {
      "experiment_id": "0",
      "name": "Default",
      "artifact_location": "/home/andre/work/mlflow/test/mlruns/0"
    },

. . .

api_client.POST: req: {"anded_expressions": [{"parameter": {"string": {"value": "2", "comparator": "="}, "key": "max_depth"}}, {"metric": {"float": {"value": 0.99, "comparator": ">="}, "key": "auc"}}], "experiment_ids": ["10"]}

. . .

search2: {u'runs': [{u'info': {u'status': u'FINISHED', u'source_name': u'sample.py', u'name': u'Run 0', u'artifact_uri': u'/home/andre/work/mlflow/test/mlruns/10/1b3aa6904fa042d3854fb77f38fce92f/artifacts', u'start_time': u'1534530257', u'source_type': u'LOCAL', u'run_uuid': u'1b3aa6904fa042d3854fb77f38fce92f', u'end_time': u'1534531257', u'experiment_id': u'10', u'user_id': u''}, u'data': {u'metrics': [{u'timestamp': u'1534530257', u'value': 0.9900000095367432, u'key': u'auc'}], u'params': [{u'value': u'2', u'key': u'max_depth'}]}}]}
```

# Opinions

The opinions that this MLflow Python Client holds are:
* Unroll responses - when there is only one JSON leaf node in the response, move it up to the root
* Simplify the search request payload as in the search2() method

## Unroll responses

### create_experiment 
The create_experiment REST API operation returns:
```
{"name": "py_exp_153456072699"}
```
The client returns:
```
"py_exp_153456072699"
```

### create_run
The create_run REST API operation returns:
```
{
  "run": {
    "info": {
      "run_uuid": "7b3a9f2f4df446709b8015c5cec2e8c0",
      "experiment_id": "2",
      "name": "Run 0",
      "source_type": "LOCAL",
      "source_name": "sample.py",
      "user_id": "",
      "status": "RUNNING",
      "start_time": "1534560726",
      "artifact_uri": "/home/andre/work/mlflow/test/mlruns/2/7b3a9f2f4df446709b8015c5cec2e8c0/artifacts"
    }
  }
}
```
The client returns only what is relevant - the sole leaf node:
```
{
  "run_uuid": "7b3a9f2f4df446709b8015c5cec2e8c0",
  "experiment_id": "2",
  "name": "Run 0",
  "source_type": "LOCAL",
  "source_name": "sample.py",
  "user_id": "",
  "status": "RUNNING",
  "start_time": "1534560726",
  "artifact_uri": "/home/andre/work/mlflow/test/mlruns/2/7b3a9f2f4df446709b8015c5cec2e8c0/artifacts"
}
```

## Simplify the search endpoint
The search endpoint expects the following request:
```
{
  "experiment_ids": [ "0" ]
  "anded_expressions": [
    {
      "parameter": {
        "key": "max_depth",
        "string": { "value": "3", "comparator": "=" }
      }
    },
    {
      "metric": {
        "key": "auc",
        "float": { "value": 2, "comparator": ">=" }
      }
    }
  ]
}
```
The client ``search2(experiment_ids, clauses)`` simplifies it to:

experiment_ids:
```
[ "0" ]
```

clauses:
```
[ { "type": "parameter", "comparator": "=", "key": "max_depth", "value": "3" },
  { "type": "metric", "comparator": ">=", "key": "auc", "value": 2 }  ]
```
