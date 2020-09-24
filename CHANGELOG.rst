Changelog
=================================================================

1.0
--------------------

.. changelog::
   :version: 1.0.8

   .. change::
      :tags: docs
      :tickets: DSX-16

      Added CHANGELOG.rst file

   .. change::
      :tags: general
      :tickets: DSX-16
      :changeset: d5e57951

      Added `mlflow_client.__version__` attribute

.. changelog::
   :version: 1.0.7
   :released: 16.09.2020 0:14

   .. change::
      :tags: general
      :tickets: DSX-24
      :changeset: e3d715da

      Add VERSION file

   .. change::
      :tags: docs
      :tickets: SCRR-133
      :changeset: 0b32c40d

      Deploy dev version documentation

   .. change::
      :tags: general, bug
      :tickets: SCRR-142
      :changeset: 0b32c40d

      Removed `tests` dir from release package

.. changelog::
   :version: 1.0.6
   :released: 14.08.2020 12:12

   .. change::
      :tags: ci
      :tickets: SCRR-133
      :changeset: f7824f2a

      Update ansible from v2.2 to v2.9

.. changelog::
   :version: 1.0.5
   :released: 14.08.2020 12:12

   .. change::
      :tags: ci
      :tickets: SCRR-111
      :changeset: 0aa457f9

      Development version is released on every push to `dev` branch

   .. change::
      :tags: general, bug
      :tickets: SCRR-111
      :changeset: 0aa457f9

      Removed `tests` dir from release package

.. changelog::
   :version: 1.0.4
   :released: 07.08.2020 17:20

   .. change::
      :tags: client, bug
      :tickets: SCRR-111
      :changeset: ca138fa5

      Logs are now passed to STDOUT instead of STDERR

.. changelog::
   :version: 1.0.3
   :released: 05.08.2020 18:01

   .. change::
      :tags: client, bug
      :tickets: SCRR-111
      :changeset: e9d7759d

      Fixed `MLflowApiClient.get_or_create_model` method

.. changelog::
   :version: 1.0.2
   :released: 05.08.2020 18:01

   .. change::
      :tags: tests, bug
      :tickets: SCRR-111
      :changeset: 5d345837

      Add timeout to integration tests

   .. change::
      :tags: client, bug
      :tickets: SCRR-111
      :changeset: 3b7c1930

      Fixed `ignore_ssl_check` flag handling in `MLflowApiClient` methods

.. changelog::
   :version: 1.0.1
   :released: 31.07.2020 14:15

   .. change::
      :tags: client, feature
      :tickets: SCRR-111
      :changeset: 22d95875

      Add `MLflowApiClient.get_or_create_model` method

.. changelog::
   :version: 1.0.0
   :released: 30.07.2020 19:01

   .. change::
      :tags: general
      :tickets: SCRR-111
      :changeset: 77e7f798

      `mlflow-client` package was created based on `mlflow-python-client <https://github.com/amesar/mlflow-python-client>`__

   .. change::
      :tags: artifact, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `artifact` module was added with certain classes:
         * `FileInfo`

   .. change::
      :tags: experiment, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `experiment` module was added with certain classes:
         * `Experiment`
         * `ExperimentTag`
         * `ExperimentStage`

   .. change::
      :tags: model, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `model` module was added with certain classes:
         * `Model`
         * `ModelVersion`
         * `ModelTag`
         * `ModelVersionTag`
         * `ModelVersionStage`
         * `ModelVersionState`
         * `ModelVersionStatus`

   .. change::
      :tags: page, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `page` module was added with certain classes:
         * `Page`

   .. change::
      :tags: run, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `run` module was added with certain classes:
         * `Run`
         * `RunInfo`
         * `RunData`
         * `Param`
         * `Metric`
         * `RunTag`
         * `RunStage`
         * `RunStatus`
         * `RunViewType`

   .. change::
      :tags: tag, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `tag` module was added with certain classes:
         * `Tag`

   .. change::
      :tags: client, feature
      :tickets: SCRR-111
      :changeset: 81484376

      `client.MLflowApiClient` class methods were created:
         * `get*`
            * `get_experiment_by_name`
            * `get_or_create_experiment`

            * `get_model`

            * `get_model_version`
            * `get_model_version_download_url`

         * `list*`
            * `list_experiment_runs`
            * `list_models`
            * `list_model_versions`

         * `search*`
            * `search_models`
            * `search_model_versions`

         * `create*`
            * `create_model`
            * `create_model_version`

         * `update*`
            * `rename_experiment`

            * `start_run`
            * `schedule_run`
            * `finish_run`
            * `fail_run`
            * `kill_run`

            * `log_run_batch`
            * `log_run_model`

            * `rename_model`
            * `set_model_description`

            * `set_model_version_description`

            * `transition_model_version_stage`
            * `test_model_version`
            * `promote_model_version`
            * `promote_model_version`

         * `tag*`
            * `set_experiment_tag`

            * `set_run_tag`
            * `delete_run_tag`

            * `set_model_tag`
            * `delete_model_tag`

            * `set_model_version_tag`
            * `delete_model_version_tag`

         * `delete*`
            * `delete_experiment`
            * `delete_run`
            * `delete_model`
            * `delete_model_version`

         * `restore*`
            * `restore_experiment`
            * `restore_run`

      Renamed:
         * `update_run` -> `set_run_status`
         * `log_parameter` -> `log_run_parameter`
         * `log_metric` -> `log_run_metric`
         * `get_metric_history` -> `get_run_metric_history`
         * `list_artifacts` -> `list_run_artifacts`
         * `get_artifact` -> `get_run_artifact`
         * `search2` -> `search_runs`

      Updated:
         * `list_experiments`
         * `get_experiment`
         * `create_experiment`
         * `get_experiment_id`
         * `get_run`
         * `create_run`

      Deleted:
         * `get_or_create_experiment_id`
         * `search`

   .. change::
      :tags: page, feature
      :tickets: SCRR-111
      :changeset: 432be0ef

      * `page.Page`:
         * Class can be constructed from list
         * Presence of an item can be checked with `in` operator
         * Item can be appended using `+` operator
         * Item can be removed using `del` operator
         * Items count can be determined using `len` function
         * Is comparable now with another Page, list or dict
         * Is iterable now

   .. change::
      :tags: run, feature
      :tickets: SCRR-111
      :changeset: 432be0ef

      * `run.RunInfo`
         * experiment_id is not mandatory constructor argument anymore
         * Is comparable now with another Run, list, dict or str (=id)
         * Presence of an item in a dict can be checked using `in` operator

      * `tag.Param`
         * Is comparable now with another Param, list, dict or tuple (=(key, value))
         * Presence of an item in a dict can be checked using `in` operator

      * `run.Metric`
         * Is comparable now with another Metric, list, dict or tuple (=(key, value, timestamp) or (key, value))
         * Presence of an item in a dict can be checked using `in` operator

      * `tag.RunTag`
         * Is comparable now with another RunTag, list, dict or tuple (=(key, value))
         * Presence of an item in a dict can be checked using `in` operator

      * `run.RunData`
         * Is comparable now with another RunData, list or dict
         * Presence of an item in a dict can be checked using `in` operator

      * `run.Run`
         * Is comparable now with another Run, list or dict
         * Presence of an item in a dict can be checked using `in` operator

   .. change::
      :tags: tag, feature
      :tickets: SCRR-111
      :changeset: 432be0ef

      * `tag.Tag`
         * Is comparable now with another RunTag, list, dict or tuple (=(key, value))
         * Presence of an item in a dict can be checked using `in` operator

   .. change::
      :tags: sample, bug
      :tickets: SCRR-111
      :changeset: 432be0ef

      Fixed sample scripts

   .. change::
      :tags: client, bug
      :tickets: SCRR-111
      :changeset: a01fe488

      Fixed `MLflowApiClient` methods:
         * `list_experiments`
         * `log_run_model`
         * `delete_run_tag`
         * `get_run_metric_history`
         * `list_run_artifacts`
         * `search_runs`
         * `set_model_description`
         * `list_models`
         * `search_models`
         * `get_model_version`
         * `set_model_version_description`
         * `set_model_version_tag`
         * `delete_model_version_tag`
         * `delete_model_version`
         * `search_model_versions`
         * `get_model_version_download_url`
         * `transition_model_version_stage`

   .. change::
      :tags: tag, bug
      :tickets: SCRR-111
      :changeset: a01fe488

      Fixed `MLflowApiClient` methods tag handling:
         * `list_experiments`
         * `get_run`
         * `create_model_version`

   .. change::
      :tags: client, feature
      :tickets: SCRR-111
      :changeset: a01fe488

      Added new `MLflowApiClient` methods:
         * `list_experiment_runs_iterator`
         * `list_run_artifacts_iterator`
         * `search_runs_iterator`
         * `search_models_iterator`
         * `search_model_versions_iterator`
         * `archive_model_version`

   .. change::
      :tags: client, feature
      :tickets: SCRR-111
      :changeset: a01fe488

      Now it's possible to pass stages to `MLflowApiClient.list_model_versions` as list of strings

   .. change::
      :tags: model, feature
      :tickets: SCRR-111
      :changeset: a01fe488

      * `model.ModelVersionState`
         * Is comparable now with another ModelVersionState or tuple (=(status, message))
         * Presence of an item in a dict can be checked using `in` operator

      * `model.ModelVersion`
         * Is comparable now with another ModelVersion, list, dict or tuple (=(name, version))
         * Presence of an item in a dict can be checked using `in` operator

      * `model.Model`
         * Is comparable now with another Model, list, dict or str (=name)
         * Presence of an item in a dict can be checked using `in` operator

   .. change::
      :tags: model, bug
      :tickets: SCRR-111
      :changeset: a01fe488

      Fixed parsing stage in `model.ModelVersion` constructor
