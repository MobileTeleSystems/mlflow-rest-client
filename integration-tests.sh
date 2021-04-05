#!/usr/bin/env bash

root_path=$(dirname $(realpath $0))
$root_path/wait-for-it.sh -h $MLFLOW_HOST -p $MLFLOW_PORT -t 0

python_version=$(python -c 'import sys; print("{0}.{1}".format(*sys.version_info))')
$root_path/pytest_runner.sh $root_path/tests/integration --junitxml=$root_path/reports/junit/integration-${python_version}.xml --reruns 5 $*
