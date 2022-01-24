#!/usr/bin/env bash
set -e

export PGHOST=$POSTGRES_HOST
export PGDATABASE=$POSTGRES_DB
export PGPORT=$POSTGRES_PORT
export PGUSER=$POSTGRES_USER
export PGPASSWORD=$POSTGRES_PASSWORD

until psql -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

>&2 echo "Postgres is up"
