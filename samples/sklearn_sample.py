from __future__ import print_function

"""
Calls API operations on the hard-coded Python scikit-learn run in experiment 0 executed in the docker container.
"""

import sys
from mlflow_api_client import MLflowApiClient

def process(client):
    experiment_id = "0"
    metric_key = 'auc'
    param_key = 'max_depth'

    print("====== get_experiment")
    exp = client.get_experiment(experiment_id)
    print("get_experiment rsp:",exp)

    run = exp['runs'][0]
    print(">> run",run)
    run_uuid = run['run_uuid']
    print("run_uuid:",run_uuid)

    print("====== get_run")
    run = client.get_run(run_uuid)
    print("get_run rsp:",run)

    print("====== get_metric")
    rsp = client.get_metric(run_uuid, metric_key)
    print("get_metric rsp:",rsp)

    print("====== get_metric_history")
    rsp = client.get_metric_history(run_uuid, metric_key)
    print("get_metric_history rsp:",rsp)

    print("====== list_artifacts")
    path = ''
    rsp = client.list_artifacts(run_uuid, path)
    print("list_artifacts rsp:",rsp)

    print("====== get_artifact - txt")
    path = 'confusion_matrix.txt'
    rsp = client.get_artifact(run_uuid, path)
    print("get_artifacts: path={} rsp={}".format(path,rsp))

    print("====== get_artifact - pkl")
    path = 'model/model.pkl'
    rsp = client.get_artifact(run_uuid, path)
    print("get_artifacts: path={} #rsp.bytes={}".format(path,len(rsp)))

    print("====== Search")
    expIds = [ experiment_id]
    clauses = [
        { 'type': 'parameter', 'comparator': '=', 'key': param_key, 'value': '3'},
        { 'type': 'metric', 'comparator': '>=', 'key': metric_key, 'value': .99} ]
    rsp = client.search2(expIds,clauses)
    print("search2 rsp:",rsp)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Expecting BASE_URL")
        sys.exit(1)
    client = MLflowApiClient(sys.argv[1])
    process(client)
