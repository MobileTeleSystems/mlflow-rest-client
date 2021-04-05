#!/usr/bin/env bash

root_path=$(dirname $(realpath $0))
python_version=$(python -c 'import sys; print("{0}.{1}".format(*sys.version_info))')
$root_path/pytest_runner.sh $root_path/tests/unit --junitxml=$root_path/reports/junit/unit-${python_version}.xml --reruns 5 $*
