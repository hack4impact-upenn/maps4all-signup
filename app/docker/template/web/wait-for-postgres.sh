#!/bin/bash
# wait-for-postgres.sh

set -e

host="$DATABASE_HOST"

until psql -h "$host" -U "postgres" -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

sh run.sh
