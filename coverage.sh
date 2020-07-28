#!/usr/bin/env bash

coverage combine
coverage xml -o ./reports/coverage.xml -i
