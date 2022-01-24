ARG MLFLOW_VERSION=1.22.0
FROM adacotechjp/mlflow:${MLFLOW_VERSION}

RUN apt-get update && \
    apt-get install --no-install-recommends -fy postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY ./mlflow-entrypoint.sh ./wait-for-postgres.sh /
RUN chmod +x /mlflow-entrypoint.sh /wait-for-postgres.sh

ENTRYPOINT ["/mlflow-entrypoint.sh"]
CMD []
