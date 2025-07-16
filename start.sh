#!/bin/bash

ENV="$1"  # The environment passed as the first argument (dev, staging, prod)

# Ensure the environment argument is provided
if [[ -z "$ENV" || ! "$ENV" =~ ^(dev|staging|prod)$ ]]; then
  echo "Usage: ./start.sh [dev|staging|prod]"
  exit 1
fi

echo "🔧 Starting Frappe in $ENV mode..."

# Check if the corresponding .env file exists for the given environment
if [ ! -f ".env.$ENV" ]; then
  echo "Error: .env.$ENV file does not exist."
  exit 1
fi

# Export environment variables from the selected .env file
export $(cat .env.$ENV | xargs)

# Pull the latest Docker images and ensure they’re using the appropriate environment settings
echo "⬇️ Pulling latest Docker images..."
docker compose -f pwd.yml --env-file .env.$ENV pull

# Start the Docker containers in detached mode using the provided environment variables
echo "🚀 Starting containers..."
docker compose -f pwd.yml --env-file .env.$ENV up -d

# Optionally, show logs for the backend container (or others)
# docker-compose logs -f backend
