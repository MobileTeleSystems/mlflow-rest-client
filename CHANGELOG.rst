Changelog
=================================================================

2.0
--------------------
.. changelog::
    :version: 2.0.0

    .. change::
        :tags: general
        :tickets: DSX:288

        Change package author to `<dsx-team@mts.ru>`__

    .. change::
        :tags: general
        :tickets: DSX:419

        Add ``CONTRIBUTING.rst`` file

    .. change::
        :tags: general, breaking
        :tickets: DSX:384

        Drop Python 2.7 and 3.6 support

    .. change::
        :tags: dependency, breaking
        :tickets: DSX:384

        Use ``pydantic`` to parse responses

    .. change::
        :tags: client, feature
        :tickets: DSX:442

        Add ``Bearer`` token auth

    .. change::
        :tags: general
        :tickets: DSX:409

        Add ``LICENSE.txt`` file

    .. change::
        :tags: client, breaking
        :tickets: DSX:545, DSX:632

        Rename library:

            * ``mlflow-client`` -> ``mlflow-rest-client``
            * ``MLflowApiClient`` -> ``MLflowRESTClient``

    .. change::
        :tags: general, feature
        :tickets: DSX:449

        Add ``SECURITY.rst`` file

    .. change::
        :tags: general, feature
        :tickets: DSX:411

        Move repo to github.com

    .. change::
        :tags: docs, feature
        :tickets: DSX:421

        Move documentation to readthedocs.org

    .. change::
        :tags: dev, feature
        :tickets: DSX:599

        Upgrade source code to Python 3.7+

    .. change::
        :tags: ci, feature
        :tickets: DSX:412, 1

        Move from Gitlab CI to Github Actions

    .. change::
        :tags: dev, feature
        :tickets: DSX:549

        Check type hints with ``mypy``

1.1
--------------------
.. changelog::
    :version: 1.1.7
    :released: 26.05.2021 17:47

    .. change::
        :tags: tests, bug
        :tickets: DSX:166

        Do not use relative paths to run tests

    .. change::
        :tags: client, bug
        :tickets: DSX:262

        Do not use `LIKE` operator while searching model by name in `get_or_create_model` function

    .. change::
        :tags: dev, feature
        :tickets: DSX:358

        Build and push dev versions for feature and bug branches too

.. changelog::
    :version: 1.1.6
    :released: 03.04.2021 14:21

    .. change::
        :tags: ci, feature
        :tickets: DSX:166

        Use Jenkins declarative pipeline

    .. change::
        :tags: client, feature
        :tickets: DSX:166

        Disable SSL ignore warnings

    .. change::
        :tags: client, feature
        :tickets: DSX:166

        Create one session for all requests

.. changelog::
    :version: 1.1.5
    :released: 25.12.2020 15:55

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Pass project urls into setup.py

    .. change::
        :tags: general, feature
        :tickets: DSX:34

        Test python 3.8 and 3.9 compatibility

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Improve Jenkinsfile

    .. change::
        :tags: ci, feature
        :tickets: DSX:111

        Move CI/CD from bdbuilder04 to adm-ci

    .. change::
        :tags: dev, feature
        :tickets: DSX:34

        Add requirements-dev.txt as ``dev`` extras into ``setup.py``

    .. change::
        :tags: ci, feature
        :tickets: DSX:128

        Download base python images before build

    .. change::
        :tags: ci, feature
        :tickets: DSX:130

        Fix requirements caching in Docker image

    .. change::
        :tags: docs, feature
        :tickets: DSX:130

        Add summary to documentation pages

.. changelog::
    :version: 1.1.4
    :released: 05.12.2020 13:06

    .. change::
        :tags: ci, feature
        :tickets: DSX:66

        Allow to build and deploy versions from non-master branch

    .. change::
        :tags: ci, feature
        :tickets: DSX:72

        Remove old dev versions from Artifactory

    .. change::
        :tags: ci, feature
        :tickets: DSX:80

        Move documentation deployment step to separated Jenkins job

    .. change::
        :tags: general, bug
        :tickets: DSX:80

        Include README.rst into PyPi package

    .. change::
        :tags: ci
        :tickets: DSX:89

        Make test scripts a docker image entrypoints

    .. change::
        :tags: ci, bug
        :tickets: DSX:89

        Publish package and documentation to Artifactory in one build info

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Pass real project version to SonarQube

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Pass project links to SonarQube

    .. change::
        :tags: ci, bug
        :tickets: DSX:34

        Remove redundant proxying from Jenkinsfile

    .. change::
        :tags: ci, feature
        :tickets: DSX:111

        Move CI/CD from bdbuilder04 to adm-ci

    .. change::
        :tags: ci, bug
        :tickets: DSX:34

        Remove volumes after stopping test container

    .. change::
        :tags: ci, bug
        :tickets: DSX:34

        Fix PyLint report upload to SonarQube

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Format source code with Black

    .. change::
        :tags: ci, feature
        :tickets: DSX:34

        Check source code vulnerabilities with Bandit

    .. change::
        :tags: dev, feature
        :tickets: DSX:34

        Add pre-commit hooks

.. changelog::
    :version: 1.1.3
    :released: 17.10.2020 03:40

    .. change::
        :tags: ci
        :tickets: DSX:53

        Improve Jenkinsfile

    .. change::
        :tags: client, feature
        :tickets: DSX:25

        Add ``list_model_all_versions`` and ``list_model_all_versions_iterator`` methods

.. changelog::
    :version: 1.1.2
    :released: 02.10.2020 19:06

    .. change::
        :tags: dependency
        :tickets: DSX:45

        Don't hard code dependency versions

    .. change::
        :tags: model
        :tickets: DSX:45

        Fix error with accessing model list by stage

.. changelog::
    :version: 1.1.1
    :released: 29.09.2020 18:08

    .. change::
        :tags: docs
        :tickets: DSX:46

        Improve documentation

.. changelog::
    :version: 1.1.0
    :released: 29.09.2020 16:29

    .. change::
        :tags: refactor
        :tickets: DSX:46

        Refactor code

    .. change::
        :tags: tests
        :tickets: DSX:46

        Increase tests coverage

    .. change::
        :tags: model, feature
        :tickets: DSX:46

        Allow to get version by stage from ``Model`` object

    .. change::
        :tags: tag, feature
        :tickets: DSX:46

        Allow to get tag by name from any object

    .. change::
        :tags: run, feature
        :tickets: DSX:46

        Allow to get param by key from ``RunData`` object

    .. change::
        :tags: run, feature
        :tickets: DSX:46

        Allow to get metric by key from ``RunData`` object

    .. change::
        :tags: docs
        :tickets: DSX:46

        Improve documentation

1.0
--------------------

.. changelog::
    :version: 1.0.8
    :released: 24.09.2020 16:42

    .. change::
        :tags: general
        :tickets: DSX:16
        :changeset: d5e57951

        Added ``mlflow_client.__version__`` attribute

    .. change::
        :tags: docs
        :tickets: DSX:16
        :changeset: 33121a8e

        Added CHANGELOG.rst file

    .. change::
        :tags: general, bug
        :tickets: DSX:16
        :changeset: 67b641f6

        Fixed VERSION file include into package

.. changelog::
    :version: 1.0.7
    :released: 16.09.2020 12:14

    .. change::
        :tags: general
        :tickets: DSX:24
        :changeset: e3d715da

        Add VERSION file

    .. change::
        :tags: docs
        :tickets: SCRR:133
        :changeset: 0b32c40d

        Deploy dev version documentation

    .. change::
        :tags: general, bug
        :tickets: SCRR:142
        :changeset: 0b32c40d

        Removed ``tests`` dir from release package

.. changelog::
    :version: 1.0.6
    :released: 14.08.2020 12:12

    .. change::
        :tags: ci
        :tickets: SCRR:133
        :changeset: f7824f2a

        Update ansible from v2.2 to v2.9

.. changelog::
    :version: 1.0.5
    :released: 14.08.2020 12:12

    .. change::
        :tags: ci
        :tickets: SCRR:111
        :changeset: 0aa457f9

        Development version is released on every push to ``dev`` branch

    .. change::
        :tags: general, bug
        :tickets: SCRR:111
        :changeset: 0aa457f9

        Removed ``tests`` dir from release package

.. changelog::
    :version: 1.0.4
    :released: 07.08.2020 17:20

    .. change::
        :tags: client, bug
        :tickets: SCRR:111
        :changeset: ca138fa5

        Logs are now passed to STDOUT instead of STDERR

.. changelog::
    :version: 1.0.3
    :released: 05.08.2020 18:01

    .. change::
        :tags: client, bug
        :tickets: SCRR:111
        :changeset: e9d7759d

        Fixed ``MLflowApiClient.get_or_create_model`` method

.. changelog::
    :version: 1.0.2
    :released: 05.08.2020 18:01

    .. change::
        :tags: tests, bug
        :tickets: SCRR:111
        :changeset: 5d345837

        Add timeout to integration tests

    .. change::
        :tags: client, bug
        :tickets: SCRR:111
        :changeset: 3b7c1930

        Fixed ``ignore_ssl_check`` flag handling in ``MLflowApiClient`` methods

.. changelog::
    :version: 1.0.1
    :released: 31.07.2020 14:15

    .. change::
        :tags: client, feature
        :tickets: SCRR:111
        :changeset: 22d95875

        Add ``MLflowApiClient.get_or_create_model`` method

.. changelog::
    :version: 1.0.0
    :released: 30.07.2020 19:01

    .. change::
        :tags: general
        :tickets: SCRR:111
        :changeset: 77e7f798

        ``mlflow-rest-client`` package was created based on ``mlflow-python-client <https://github.com/amesar/mlflow-python-client>``__

    .. change::
        :tags: artifact, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``artifact`` module was added with certain classes:
            * ``FileInfo``

    .. change::
        :tags: experiment, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``experiment`` module was added with certain classes:
            * ``Experiment``
            * ``ExperimentTag``
            * ``ExperimentStage``

    .. change::
        :tags: model, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``model`` module was added with certain classes:
            * ``Model``
            * ``ModelVersion``
            * ``ModelTag``
            * ``ModelVersionTag``
            * ``ModelVersionStage``
            * ``ModelVersionState``
            * ``ModelVersionStatus``

    .. change::
        :tags: page, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``page`` module was added with certain classes:
            * ``Page``

    .. change::
        :tags: run, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``run`` module was added with certain classes:
            * ``Run``
            * ``RunInfo``
            * ``RunData``
            * ``Param``
            * ``Metric``
            * ``RunTag``
            * ``RunStage``
            * ``RunStatus``
            * ``RunViewType``

    .. change::
        :tags: tag, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``tag`` module was added with certain classes:
            * ``Tag``

    .. change::
        :tags: client, feature
        :tickets: SCRR:111
        :changeset: 81484376

        ``client.MLflowApiClient`` class methods were created:
            * ``get*``
                * ``get_experiment_by_name``
                * ``get_or_create_experiment``

                * ``get_model``

                * ``get_model_version``
                * ``get_model_version_download_url``

            * ``list*``
                * ``list_experiment_runs``
                * ``list_models``
                * ``list_model_versions``

            * ``search*``
                * ``search_models``
                * ``search_model_versions``

            * ``create*``
                * ``create_model``
                * ``create_model_version``

            * ``update*``
                * ``rename_experiment``

                * ``start_run``
                * ``schedule_run``
                * ``finish_run``
                * ``fail_run``
                * ``kill_run``

                * ``log_run_batch``
                * ``log_run_model``

                * ``rename_model``
                * ``set_model_description``

                * ``set_model_version_description``

                * ``transition_model_version_stage``
                * ``test_model_version``
                * ``promote_model_version``
                * ``promote_model_version``

            * ``tag*``
                * ``set_experiment_tag``

                * ``set_run_tag``
                * ``delete_run_tag``

                * ``set_model_tag``
                * ``delete_model_tag``

                * ``set_model_version_tag``
                * ``delete_model_version_tag``

            * ``delete*``
                * ``delete_experiment``
                * ``delete_run``
                * ``delete_model``
                * ``delete_model_version``

            * ``restore*``
                * ``restore_experiment``
                * ``restore_run``

        Renamed:
            * ``update_run`` -> ``set_run_status``
            * ``log_parameter`` -> ``log_run_parameter``
            * ``log_metric`` -> ``log_run_metric``
            * ``get_metric_history`` -> ``get_run_metric_history``
            * ``list_artifacts`` -> ``list_run_artifacts``
            * ``get_artifact`` -> ``get_run_artifact``
            * ``search2`` -> ``search_runs``

        Updated:
            * ``list_experiments``
            * ``get_experiment``
            * ``create_experiment``
            * ``get_experiment_id``
            * ``get_run``
            * ``create_run``

        Deleted:
            * ``get_or_create_experiment_id``
            * ``search``

    .. change::
        :tags: page, feature
        :tickets: SCRR:111
        :changeset: 432be0ef

        * ``page.Page``:
            * Class can be constructed from list
            * Presence of an item can be checked with ``in`` operator
            * Item can be appended using ``+`` operator
            * Item can be removed using ``del`` operator
            * Items count can be determined using ``len`` function
            * Is comparable now with another Page, list or dict
            * Is iterable now

    .. change::
        :tags: run, feature
        :tickets: SCRR:111
        :changeset: 432be0ef

        * ``run.RunInfo``
            * experiment_id is not mandatory constructor argument anymore
            * Is comparable now with another Run, list, dict or str (=id)
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``tag.Param``
            * Is comparable now with another Param, list, dict or tuple (=(key, value))
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``run.Metric``
            * Is comparable now with another Metric, list, dict or tuple (=(key, value, timestamp) or (key, value))
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``tag.RunTag``
            * Is comparable now with another RunTag, list, dict or tuple (=(key, value))
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``run.RunData``
            * Is comparable now with another RunData, list or dict
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``run.Run``
            * Is comparable now with another Run, list or dict
            * Presence of an item in a dict can be checked using ``in`` operator

    .. change::
        :tags: tag, feature
        :tickets: SCRR:111
        :changeset: 432be0ef

        * ``tag.Tag``
            * Is comparable now with another RunTag, list, dict or tuple (=(key, value))
            * Presence of an item in a dict can be checked using ``in`` operator

    .. change::
        :tags: sample, bug
        :tickets: SCRR:111
        :changeset: 432be0ef

        Fixed sample scripts

    .. change::
        :tags: client, bug
        :tickets: SCRR:111
        :changeset: a01fe488

        Fixed ``MLflowApiClient`` methods:
            * ``list_experiments``
            * ``log_run_model``
            * ``delete_run_tag``
            * ``get_run_metric_history``
            * ``list_run_artifacts``
            * ``search_runs``
            * ``set_model_description``
            * ``list_models``
            * ``search_models``
            * ``get_model_version``
            * ``set_model_version_description``
            * ``set_model_version_tag``
            * ``delete_model_version_tag``
            * ``delete_model_version``
            * ``search_model_versions``
            * ``get_model_version_download_url``
            * ``transition_model_version_stage``

    .. change::
        :tags: tag, bug
        :tickets: SCRR:111
        :changeset: a01fe488

        Fixed ``MLflowApiClient`` methods tag handling:
            * ``list_experiments``
            * ``get_run``
            * ``create_model_version``

    .. change::
        :tags: client, feature
        :tickets: SCRR:111
        :changeset: a01fe488

        Added new ``MLflowApiClient`` methods:
            * ``list_experiment_runs_iterator``
            * ``list_run_artifacts_iterator``
            * ``search_runs_iterator``
            * ``search_models_iterator``
            * ``search_model_versions_iterator``
            * ``archive_model_version``

    .. change::
        :tags: client, feature
        :tickets: SCRR:111
        :changeset: a01fe488

        Now it's possible to pass stages to ``MLflowApiClient.list_model_versions`` as list of strings

    .. change::
        :tags: model, feature
        :tickets: SCRR:111
        :changeset: a01fe488

        * ``model.ModelVersionState``
            * Is comparable now with another ModelVersionState or tuple (=(status, message))
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``model.ModelVersion``
            * Is comparable now with another ModelVersion, list, dict or tuple (=(name, version))
            * Presence of an item in a dict can be checked using ``in`` operator

        * ``model.Model``
            * Is comparable now with another Model, list, dict or str (=name)
            * Presence of an item in a dict can be checked using ``in`` operator

    .. change::
        :tags: model, bug
        :tickets: SCRR:111
        :changeset: a01fe488

        Fixed parsing stage in ``model.ModelVersion`` constructor
