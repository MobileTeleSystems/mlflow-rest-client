.. title

Python Client for MLflow
==========================

|Build Status| |Quality Gate Status| |Maintainability Rating| |Coverage|
|Documentation| |PyPI|

.. |Build Status| image:: https://jenkins.bd.msk.mts.ru/job/Platform/job/DSX/job/mlflow-client/badge/icon
    :target: https://jenkins.bd.msk.mts.ru/job/Platform/job/DSX/job/mlflow-client
.. |Quality Gate Status| image:: https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=alert_status
    :target: https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client
.. |Maintainability Rating| image:: https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=sqale_rating
    :target: https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client
.. |Coverage| image:: https://sonar.bd.msk.mts.ru/api/project_badges/measure?project=mlflow-client&metric=coverage
    :target: https://sonar.bd.msk.mts.ru/dashboard?id=mlflow-client
.. |Documentation| image:: https://img.shields.io/badge/docs-latest-success
    :target: https://mlflow-client.msk.bd-cloud.mts.ru
.. |PyPI| image:: https://img.shields.io/badge/pypi-download-orange
    :target: http://docker.rep.msk.mts.ru/ui/packages/pypi:%2F%2Fmlflow-client

A slightly opinionated Python client for `MLflow <https://mlflow.org>`_ REST API that implements all REST operations.

See `mlflow_api_client.py <https://git.bd.msk.mts.ru/bigdata/platform/dsx/mlflow-client/-/blob/master/mlflow_client/mlflow_api_client.py>`_ for client implementation.

.. documentation

Documentation
-------------

See https://mlflow-client.msk.bd-cloud.mts.ru/

.. contribution

Contribution guide
-------------------

See `<CONTRIBUTING.rst>`__


.. install

Installation
---------------

Stable release
~~~~~~~~~~~~~~~
Stable version is released on every tag to ``master`` branch. Please use stable releases on production environment.
Version example: ``1.1.4``

.. code:: bash

    pip install mlflow-client==1.1.4 # exact version

    pip install mlflow-client # latest release

Development release
~~~~~~~~~~~~~~~~~~~~
Development version is released on every commit to ``dev`` branch. You can use them to test some new features before official release.
Version example: ``1.1.3.dev5``

.. code:: bash

    pip install mlflow-client==1.1.3.dev5 # exact dev version

    pip install --pre mlflow-client # latest dev version

.. develop

Development
---------------
Clone repo:

.. code:: bash

    git clone ssh://git@git.bd.msk.mts.ru:8022/bigdata/platform/dsx/mlflow-client.git -b dev

    cd mlflow-client

Install dependencies for development:

.. code:: bash

    pip install -r requirements-dev.txt

Install pre-commit hooks:

.. code:: bash

    pre-commit install
    pre-commit autoupdate
    pre-commit install-hooks

Test pre-commit hooks run:

.. code:: bash

    pre-commit run --all-files -v

.. usage

Usage
------------
Make sure you have an `MLflow Tracking Server <https://mlflow.org/docs/latest/tracking.html#running-a-tracking-server>`_ running.

.. code:: python

    from mlflow_client import MLflowApiClient

    client = MLflowApiClient("https://mlflow.msk.bd-cloud.mts.ru", ignore_ssl_check=True)

    experiment = client.get_or_create_experiment("experiment_name")
    run = client.create_run(experiment.id)

See `sample.py <https://git.bd.msk.mts.ru/bigdata/platform/dsx/mlflow-client/-/blob/master/samples/sample.py>`_ for more examples.
