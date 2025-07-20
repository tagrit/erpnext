#!/bin/bash

# === Configuration ===
CONTAINER=frappe_prod-backend-1
DEST_APPS=./apps
DEST_SITES=./sites

# === Ensure destination directories exist ===
mkdir -p "$DEST_APPS"
mkdir -p "$DEST_SITES"

# === Copy apps/ content from container to host's /apps ===
echo "🔄 Copying all apps from container to $DEST_APPS ..."
docker cp "$CONTAINER:/home/frappe/frappe-bench/apps/." "$DEST_APPS"

# === Copy sites/ content from container to host's /sites ===
echo "🔄 Copying all sites from container to $DEST_SITES ..."
docker cp "$CONTAINER:/home/frappe/frappe-bench/sites/." "$DEST_SITES"

echo "✅ Done syncing apps and sites from container."
