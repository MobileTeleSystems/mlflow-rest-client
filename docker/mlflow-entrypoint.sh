#!/bin/bash

/wait-for-postgres.sh

mlflow db upgrade "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"

mlflow server --host 0.0.0.0 --backend-store-uri "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB" --default-artifact-root "$ARTIFACT_ROOT" $*
