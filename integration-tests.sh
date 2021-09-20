#!/usr/bin/env bash

root_path=$(dirname $(realpath $0))
$root_path/wait-for-it.sh -h $MLFLOW_HOST -p $MLFLOW_PORT -t 0
$root_path/pytest_runner.sh $root_path/tests/integration --reruns 5 $*
