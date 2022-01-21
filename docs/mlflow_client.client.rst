MLflow API client
=================================================================

Summary
--------
.. currentmodule:: mlflow_client.mlflow_client.MLflowClient

Main class
^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    mlflow_client.mlflow_client.MLflowClient

Experiment
^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    list_experiments
    list_experiments_iterator

    get_experiment
    get_experiment_id
    get_experiment_by_name

    get_or_create_experiment
    create_experiment
    rename_experiment
    delete_experiment
    restore_experiment

    set_experiment_tag

Run
^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    list_experiment_runs
    list_experiment_runs_iterator

    search_runs
    search_runs_iterator

    get_run

    create_run
    set_run_status
    start_run
    schedule_run
    finish_run
    fail_run
    kill_run
    delete_run
    restore_run

    log_run_parameter
    log_run_parameters

    log_run_metric
    log_run_metrics

    log_run_batch
    log_run_model

    set_run_tag
    set_run_tags
    delete_run_tag
    delete_run_tags

Run metrics
^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    list_run_metric_history
    list_run_metric_history_iterator


Run artifacts
^^^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    list_run_artifacts
    list_run_artifacts_iterator

Model
^^^^^
.. autosummary::
    :nosignatures:

    list_models
    list_models_iterator

    search_models
    search_models_iterator

    get_model

    get_or_create_model
    create_model
    rename_model
    set_model_description
    delete_model

    set_model_tag
    delete_model_tag

Model version
^^^^^^^^^^^^^
.. autosummary::
    :nosignatures:

    list_model_versions
    list_model_versions_iterator

    list_model_all_versions
    list_model_all_versions_iterator

    search_model_versions
    search_model_versions_iterator

    get_model_version
    get_model_version_download_url

    create_model_version
    set_model_version_description
    delete_model_version

    set_model_version_tag
    delete_model_version_tag

    transition_model_version_stage
    test_model_version
    promote_model_version
    archive_model_version

Documentation
--------------
.. autoclass:: mlflow_client.mlflow_client.MLflowClient
    :members:
