"""
Calls API operations on the hard-coded Python scikit-learn run in experiment 0 executed in the docker container.
"""

import sys

from mlflow_rest_client import MLflowRESTClient


def process(client):
    experiment_id = "0"
    metric_key = "auc"
    param_key = "max_depth"

    print("====== get_experiment")
    exp = client.get_experiment(experiment_id)
    print("get_experiment rsp:", exp)

    run = exp["runs"][0]
    print(">> run", run)
    print("run.id:", run.id)

    print("====== get_run")
    run = client.get_run(run.id)
    print("get_run rsp:", run)

    print("====== get_metric")
    rsp = client.get_metric(run.id, metric_key)
    print("get_metric rsp:", rsp)

    print("====== get_metric_history")
    rsp = client.get_metric_history(run.id, metric_key)
    print("get_metric_history rsp:", rsp)

    print("====== list_artifacts")
    path = ""
    rsp = client.list_artifacts(run.id, path)
    print("list_artifacts rsp:", rsp)

    print("====== get_artifact - txt")
    path = "confusion_matrix.txt"
    rsp = client.get_artifact(run.id, path)
    print(f"get_artifacts: path={path} rsp={rsp}")

    print("====== get_artifact - pkl")
    path = "model/model.pkl"
    rsp = client.get_artifact(run.id, path)
    print(f"get_artifacts: path={path} #rsp.bytes={len(rsp)}")

    print("====== Search")
    rsp = client.search_runs(
        experiment_id,
        query=f"parameter.{param_key} = 3 and metric.{metric_key} >= 0.99",
    )
    print("search_runs rsp:", rsp)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Expecting BASE_URL")
        sys.exit(1)
    client = MLflowRESTClient(sys.argv[1])
    process(client)
