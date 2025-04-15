#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for PostgreSQL at $host..."

until PGPASSWORD=$DATABASE_PASSWORD psql -h "$host" -U "$DATABASE_USER" -c '\q' 2>/dev/null; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - running command"
exec $cmd
