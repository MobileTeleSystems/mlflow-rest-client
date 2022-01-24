.. title

Python Client for MLflow
==========================

|status| |PyPI| |PyPI License| |PyPI Python Version|
|ReadTheDocs| |Build| |Coverage| |pre-commit.ci|

.. |status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://www.repostatus.org/#active
.. |PyPI| image:: https://badge.fury.io/py/mlflow-client.svg
    :target: https://badge.fury.io/py/mlflow-client
.. |PyPI License| image:: https://img.shields.io/pypi/l/mlflow-client.svg
    :target: https://github.com/MobileTeleSystems/mlflow-client/blob/main/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/mlflow-client.svg
    :target: https://badge.fury.io/py/mlflow-client
.. |ReadTheDocs| image:: https://img.shields.io/readthedocs/mlflow-client.svg
    :target: https://mlflow-client.readthedocs.io
.. |Build| image:: https://github.com/MobileTeleSystems/mlflow-client/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/mlflow-client/actions
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/mlflow-client/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MobileTeleSystems/mlflow-client
.. |pre-commit.ci| image:: https://results.pre-commit.ci/badge/github/MobileTeleSystems/mlflow-client/main.svg
    :target: https://results.pre-commit.ci/latest/github/MobileTeleSystems/mlflow-client/main

Python client for `MLflow <https://mlflow.org>`_ REST API.

**Features:**

- Unlike `MLflow Tracking client <https://mlflow.org/docs/latest/python_api/mlflow.tracking.html>`__
  all REST API methods are exposed to user.

- All class fields are validated with `pydantic <https://pydantic-docs.helpmanual.io>`_.

- Basic and Bearer auth is supported.

- All methods and classes are documented.

**Limitations:**

- There is no integration with ML frameworks and libraries.
  You should use official `MLflow client <https://mlflow.org/docs/latest/python_api/mlflow.html>`__ instead.

- There is no integration with S3 or other artifact storage type.
  You should access it directly with `boto3 <https://boto3.amazonaws.com>`_ or other client.

- Only Python 3.7+ is supported. Python 3.6 and lower already reached end of life.

.. documentation

Documentation
-------------

See https://mlflow-client.readthedocs.io/

.. contribution

Contribution guide
-------------------

See `<CONTRIBUTING.rst>`__

Security
-------------------

See `<SECURITY.rst>`__


.. install

Installation
---------------

Stable release
~~~~~~~~~~~~~~~
Stable version is released on every tag to ``master`` branch. Please use stable releases on production environment.
Version example: ``2.0.0``

.. code:: bash

    pip install mlflow-client==2.0.0 # exact version

    pip install mlflow-client # latest release

Development release
~~~~~~~~~~~~~~~~~~~~
Development version is released on every commit to ``dev`` branch. You can use them to test some new features before official release.
Version example: ``2.0.0.dev5``

.. code:: bash

    pip install mlflow-client==2.0.0.dev5 # exact dev version

    pip install --pre mlflow-client # latest dev version

.. develop

Development
---------------
Clone repo:

.. code:: bash

    git clone git@github.com:MobileTeleSystems/mlflow-client.git

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

    from mlflow_client import MLflowClient

    client = MLflowClient("https://mlflow.domain", ignore_ssl_check=True)

    experiment = client.get_or_create_experiment("experiment_name")
    run = client.create_run(experiment.id)

See `sample.py <https://github.com/MobileTeleSystems/mlflow-client/blob/main/samples/sample.py>`_ for more examples.
