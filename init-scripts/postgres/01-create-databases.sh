#!/bin/sh
set -e

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  echo "Criando múltiplos bancos: $POSTGRES_MULTIPLE_DATABASES"

  OLD_IFS="$IFS"
  IFS=','
  for db in $POSTGRES_MULTIPLE_DATABASES; do
    db="$(echo "$db" | tr -d '\r' | xargs)"

    if [ -n "$db" ]; then
      echo "Verificando banco: $db"
      DB_EXISTS=$(psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db'")

      if [ "$DB_EXISTS" != "1" ]; then
        echo "Criando banco: $db"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -c "CREATE DATABASE \"$db\";"
      else
        echo "Banco $db já existe, pulando."
      fi
    fi
  done
  IFS="$OLD_IFS"

  echo "Processo finalizado."
fi