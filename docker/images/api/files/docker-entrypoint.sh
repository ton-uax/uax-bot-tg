#!/bin/bash

# Stop on errors
set -eo pipefail

# shellcheck disable=SC2078
if [ "CORE_DATABASE_WAIT" ]; then
    while true
    do
        if python /src/docker/wait_for_dependencies.py
        then
            break
        fi
        echo 'Database is unavailable - sleeping'
        sleep 1
    done
fi

# shellcheck disable=SC2078
if [ "CORE_DATABASE_WAIT" ]; then
    python /src/api/manage.py makemigrations wallet
    python /src/api/manage.py makemigrations account
    python /src/api/manage.py migrate --noinput
fi

exec "$@"
