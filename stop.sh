#!/bin/bash

ENV="$1"
FULL_CLEAN="$2"  # Optional: `--clean` to remove volumes

if [[ "$ENV" != "dev" && "$ENV" != "staging" && "$ENV" != "prod" ]]; then
  echo "Usage: ./stop.sh [dev|staging|prod] [--clean]"
  exit 1
fi

echo "🛑 Stopping Frappe in $ENV mode..."

if [[ "$FULL_CLEAN" == "--clean" ]]; then
  echo "🧼 Full cleanup: removing containers, networks, volumes, and orphans..."
  docker compose -f pwd.yml --env-file .env.$ENV down -v --remove-orphans
else
  echo "🔻 Graceful shutdown: keeping volumes..."
  docker compose -f pwd.yml --env-file .env.$ENV down --remove-orphans
fi
