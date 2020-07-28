#!/usr/bin/env bash

python_version=$(python -c 'import sys; print("{0}.{1}".format(*sys.version_info))')
coverage run -m pytest tests --junitxml=./reports/junit/unit-${python_version}.xml --reruns 5 $@
