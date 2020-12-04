#!/usr/bin/env bash

wait-for-it.sh -h $MLFLOW_HOST -p $MLFLOW_PORT -t 0

python_version=$(python -c 'import sys; print("{0}.{1}".format(*sys.version_info))')
pytest_runner.sh tests/integration --junitxml=./reports/junit/integration-${python_version}.xml --reruns 5 $*
