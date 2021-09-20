#!/usr/bin/env bash

root_path=$(dirname $(realpath $0))
$root_path/pytest_runner.sh $root_path/tests/unit --reruns 5 $*
