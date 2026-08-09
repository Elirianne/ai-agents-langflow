#!/usr/bin/env bash
# Imports the static seed JSON files into the time-series collections created
# by 01-create-collections.js. Runs automatically on first container start.
set -eu

DB_NAME="${MONGO_INITDB_DATABASE:-perf_metrics}"
DATA_DIR="/docker-entrypoint-initdb.d/data"

mongoimport \
  --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --db "$DB_NAME" \
  --collection api_performance_metrics \
  --file "$DATA_DIR/api_performance_metrics.json" \
  --jsonArray

# NOTE: Disabled for now
# mongoimport \
#   --username "$MONGO_INITDB_ROOT_USERNAME" \
#   --password "$MONGO_INITDB_ROOT_PASSWORD" \
#   --authenticationDatabase admin \
#   --db "$DB_NAME" \
#   --collection infra_metrics \
#   --file "$DATA_DIR/infra_metrics.json" \
#   --jsonArray

echo "Seed data import complete."
