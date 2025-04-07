#!/bin/sh

# wait-for-db.sh

echo "⏳ Waiting for Postgres at $DATABASE_HOST:$DATABASE_PORT..."

until nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 1
done

echo "✅ Postgres is up — continuing..."
exec "$@"
