#!/usr/bin/env bash
if [[ "$1" = 'run' ]]; then
    cd /opt/tasker
    exec pipenv run python3 agent/worker.py
else
    exec "$@"
fi
