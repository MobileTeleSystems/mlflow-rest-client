#!/usr/bin/env bash

root_path=$(dirname $(realpath $0))
COVERAGE=unit $root_path/pytest_runner.sh $root_path/tests/unit --reruns 5 $*
