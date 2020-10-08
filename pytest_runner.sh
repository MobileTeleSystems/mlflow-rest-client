#!/usr/bin/env bash

coverage run -m pytest "$@"

ret=$?
if [ "$ret" = 5 ]; then
    echo "No tests collected.  Exiting with 0 (instead of 5)."
    exit 0
fi
exit "$ret"
