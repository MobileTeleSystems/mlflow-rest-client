.. title

Python Client for MLflow
==========================

|status| |PyPI| |PyPI License| |PyPI Python Version|
|ReadTheDocs| |Build| |Coverage| |pre-commit.ci|

.. |status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://www.repostatus.org/#active
.. |PyPI| image:: https://badge.fury.io/py/mlflow-rest-client.svg
    :target: https://badge.fury.io/py/mlflow-rest-client
.. |PyPI License| image:: https://img.shields.io/pypi/l/mlflow-rest-client.svg
    :target: https://github.com/MobileTeleSystems/mlflow-rest-client/blob/main/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/mlflow-rest-client.svg
    :target: https://badge.fury.io/py/mlflow-rest-client
.. |ReadTheDocs| image:: https://img.shields.io/readthedocs/mlflow-rest-client.svg
    :target: https://mlflow-rest-client.readthedocs.io
.. |Build| image:: https://github.com/MobileTeleSystems/mlflow-rest-client/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/mlflow-rest-client/actions
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/mlflow-rest-client/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MobileTeleSystems/mlflow-rest-client
.. |pre-commit.ci| image:: https://results.pre-commit.ci/badge/github/MobileTeleSystems/mlflow-rest-client/main.svg
    :target: https://results.pre-commit.ci/latest/github/MobileTeleSystems/mlflow-rest-client/main

Python client for `MLflow <https://mlflow.org>`_ REST API.

**Features:**

- Unlike `MLflow Tracking client <https://mlflow.org/docs/latest/python_api/mlflow.tracking.html>`__
  all REST API methods are exposed to user.

- All class fields are validated with `pydantic <https://pydantic-docs.helpmanual.io>`_.

- Basic and Bearer auth are supported.

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

See https://mlflow-rest-client.readthedocs.io/

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

    pip install mlflow-rest-client==2.0.0 # exact version

    pip install mlflow-rest-client # latest release

Development release
~~~~~~~~~~~~~~~~~~~~
Development version is released on every commit to ``dev`` branch. You can use them to test some new features before official release.
Version example: ``2.0.0.dev5``

.. code:: bash

    pip install mlflow-rest-client==2.0.0.dev5 # exact dev version

    pip install --pre mlflow-rest-client # latest dev version

.. develop

Development
---------------
Clone repo:

.. code:: bash

    git clone git@github.com:MobileTeleSystems/mlflow-rest-client.git

    cd mlflow-rest-client

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

    from mlflow_rest_client import MLflowRESTClient

    client = MLflowRESTClient("https://mlflow.domain", ignore_ssl_check=True)

    experiment = client.get_or_create_experiment("experiment_name")
    run = client.create_run(experiment.id)

See `sample.py <https://github.com/MobileTeleSystems/mlflow-rest-client/blob/main/samples/sample.py>`_ for more examples.
