#!/bin/bash
# cria os bancos mlflow e airflow automaticamente

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE mlflow;
  CREATE DATABASE airflow;
  GRANT ALL PRIVILEGES ON DATABASE mlflow TO admin;
  GRANT ALL PRIVILEGES ON DATABASE airflow TO admin;
  \echo 'Bancos mlflow e airflow criados com sucesso';
EOSQL