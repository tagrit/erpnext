#!/bin/bash

# Usage: drop_site sandbox.tagrit.com

SITE_NAME=$1
SITE_KEY="frontend-${SITE_NAME%%.*}"  # e.g. frontend-sandbox
PWD_YML="/root/frappe_docker/pwd.yml"
DOCKER_CONTAINER="frappe_prod-backend-1"
FRAPPE_DOCKER_DIR="/root/frappe_docker"

if [ -z "$SITE_NAME" ]; then
    echo "❌ Please provide a site name to delete. Usage: remove_frappe_site sandbox.tagrit.com"
    exit 1
fi

echo "🚨 Starting full removal for site: $SITE_NAME"

# 1. Drop the site inside the backend container
echo "🔧 Dropping site inside Docker container ($DOCKER_CONTAINER)..."
docker exec -it $DOCKER_CONTAINER bash -c "bench drop-site $SITE_NAME --force --no-backup"


# 2. Remove nginx site configs on host
echo "🧹 Removing Nginx config for $SITE_NAME..."
rm -f /etc/nginx/sites-available/$SITE_NAME
rm -f /etc/nginx/sites-enabled/$SITE_NAME

# 3. Stop and remove any related Docker containers (e.g. frontend-<site>)
echo "🔍 Removing Docker containers related to $SITE_NAME..."
docker ps -a --format '{{.ID}} {{.Names}}' | grep "$SITE_KEY" | while read -r id name; do
    echo "🛑 Stopping/removing container: $name"
    docker stop "$id"
    docker rm "$id"
done

# 4. Remove service block from pwd.yml
echo "✂️ Cleaning up pwd.yml service block for $SITE_KEY..."

awk -v key="$SITE_KEY" '
BEGIN { skip=0 }
/^[^[:space:]]/ { skip=0 }
$0 ~ key ":" { skip=1; next }
skip == 1 && /^[^[:space:]]/ { skip=0 }
skip == 0 { print }
' "$PWD_YML" > "${PWD_YML}.tmp" && mv "${PWD_YML}.tmp" "$PWD_YML"

# 5. Stop and restart containers using your existing scripts
echo "♻️ Restarting Docker containers using stop.sh and start.sh..."
cd "$FRAPPE_DOCKER_DIR" || exit 1
./stop.sh prod
./start.sh prod

# 6. Reload Nginx
echo "🔁 Reloading Nginx..."
systemctl reload nginx || service nginx reload

echo "✅ Site $SITE_NAME has been fully removed and system restarted."
