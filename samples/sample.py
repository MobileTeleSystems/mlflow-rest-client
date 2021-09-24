import os, sys, time

from mlflow_client import MLflowApiClient
from mlflow_client.log import get_logger

logger = get_logger()

def now():
    return int(time.time())

def process(client):
    logger.info("====== list_experiments")
    exps = client.list_experiments()
    logger.info("list_experiments: #experiments: {}".format(len(exps)))
    for exp in exps:
        logger.info("  {}".format(exp))

    logger.info("====== create_experiment")
    experiment_name = "py_exp_"+str(time.time()).replace(".","")
    logger.info("CreateExperiment with name {}".format(experiment_name))
    experiment_id = client.create_experiment(experiment_name)
    logger.info("create_experiment: rsp.experiment_id: {}",experiment_id)

    logger.info("====== create_run")
    run_name = 'run_for_exp_' + experiment_name
    current_file = os.path.basename(__file__)
    start_time = now()
    dct = {'experiment_id': experiment_id, 'run_name': run_name, 'source_type': 'LOCAL', 'source_name': current_file, 'start_time': start_time }
    rsp = client.create_run(dct)
    logger.info("create_run rsp:",rsp)
    run_uuid = rsp['run_uuid']

    logger.info("====== Log params and metrics")
    param_key = 'max_depth'
    metric_key = 'auc'
    client.log_parameter(run_uuid, param_key, '2')
    client.log_metric(run_uuid, metric_key, .99)

    logger.info("====== update_run Run")
    dct = {'run_uuid': run_uuid, 'status': 'FINISHED', 'end_time': start_time+1000 }
    logger.info("update_run req:",dct)
    client.update_run(dct)

    logger.info("====== get_run")
    run = client.get_run(run_uuid)
    logger.info("get_run rsp:",run)

    logger.info("====== get_experiment")
    exp = client.get_experiment(experiment_id)
    logger.info("get_experiment rsp:",exp)

    logger.info("====== get_metric")
    rsp = client.get_metric(run_uuid, metric_key)
    logger.info("get_metric rsp:",rsp)

    logger.info("====== get_metric_history")
    rsp = client.get_metric_history(run_uuid, metric_key)
    logger.info("get_metric_history rsp:",rsp)

    logger.info("====== list_artifacts")
    path = ''
    rsp = client.list_artifacts(run_uuid, path)
    logger.info("list_artifacts rsp:",rsp)

    logger.info("====== Search")
    expIds = [ experiment_id]
    clauses = [
        { 'type': 'parameter', 'comparator': '=', 'key': param_key, 'value': '2'},
        { 'type': 'metric', 'comparator': '>=', 'key': metric_key, 'value': .99} ]
    rsp = client.search2(expIds,clauses)
    logger.info("search2 rsp:",rsp)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Expecting BASE_URL")
        sys.exit(1)
    client = MLflowApiClient(sys.argv[1])
    process(client)
