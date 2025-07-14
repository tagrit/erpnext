#!/bin/bash

ENV="$1"

if [[ "$ENV" != "dev" && "$ENV" != "staging" && "$ENV" != "prod" ]]; then
  echo "Usage: ./start.sh [dev|staging|prod]"
  exit 1
fi

echo "🔧 Starting Frappe in $ENV mode..."
docker compose -f pwd.yml --env-file .env.$ENV up -d
