#!/bin/bash

# Inputs
read -p "Enter domain name (e.g., lovida.tagrit.com): " DOMAIN

# Step 2: Show ports in use
echo ""
echo "Checking ports already in use..."
echo ""
ports_in_use

# Optional: Capture suggested port from ports_in_use output
SUGGESTED_PORT=$(ports_in_use | grep -oP 'Suggested next available port: \K\d+')

# Step 3: Prompt for port, suggesting a default
read -p "Enter port number [default: $SUGGESTED_PORT]: " PORT
PORT=${PORT:-$SUGGESTED_PORT}

# Show only names with indexes from /root/apps.json
if [ -f /root/apps.json ]; then

  # Read the app names and rename 'navari_csf_ke' to 'csf_ke' and  'kenya-compliance-via-slade' to 'kenya_compliance_via_slade'
  available_apps=$(jq -r '.[].name 
    | gsub("navari_csf_ke"; "csf_ke") 
    | gsub("kenya-compliance-via-slade"; "kenya_compliance_via_slade")' /root/apps.json)


  if [ -z "$available_apps" ]; then
    echo "⚠️  No apps found in /root/apps.json"
    exit 1
  fi

  echo "📦 Available apps:"
  echo "$available_apps" | nl
  echo ""

  # Ask user to input a comma-separated list of apps or 'all' to install all
  read -p "Enter the list of apps you want to select (comma-separated) or type 'all' to install all apps: " user_input

  # If the user typed 'all', install all available apps
  # If the user typed 'all', install all available apps
if [ "$user_input" == "all" ]; then
  
  echo "🚀 Installing all available apps..."
  # Join all available apps into a comma-separated string
  APPS=$(echo "$available_apps" | tr '\n' ',')
  # Remove the trailing comma
  APPS=$(echo "$APPS" | sed 's/,$//')
else
  # Convert user input to an array and replace the app names
  APPS=$(echo "$user_input" | tr ',' '\n' | sed 's/navari_csf_ke/csf_ke/g' | tr '\n' ',')
  
  # Remove the trailing comma if any
  APPS=$(echo "$APPS" | sed 's/,$//')
fi


  # Show the selected apps (after renaming or if 'all' was selected)
  echo "🔍 Selected apps (after renaming or 'all' selected):"
  echo "$APPS"
  echo ""

else
  echo "⚠️ /root/apps.json not found!"
  exit 1
fi


echo ""
echo "✅ Domain: $DOMAIN"
echo "✅ Port: $PORT"
echo "✅ Selected Apps: $APPS"

# Site name (for Docker service)
SITE_NAME=$(echo "$DOMAIN" | cut -d. -f1)

# Go to project directory
cd /root/frappe_docker || exit 1
YML_PATH="pwd.yml"


# 1. Create site inside the container and install apps
docker exec -it frappe_prod-backend-1 bash -c "
bench new-site $DOMAIN \
  --mariadb-user-host-login-scope='%' \
  --admin-password=admin \
  --db-root-username=root \
  --db-root-password=admin && \
IFS=',' read -ra APPLIST <<< \"$APPS\" && \
for app in \"\${APPLIST[@]}\"; do
    echo \"🚀 Installing \$app...\"
    bench --site $DOMAIN install-app \$app
done"

YML_TEMP="/tmp/tmp_pwd.yml"
SERVICE_BLOCK=$(cat <<EOF
  frontend-${SITE_NAME}:
    image: kevinamayi20/tagrit-erp:\${TAG:-v2.0.0}
    platform: linux/arm64
    depends_on:
      - websocket
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - nginx-entrypoint.sh
    environment:
      BACKEND: backend:8000
      FRAPPE_SITE_NAME_HEADER: $DOMAIN
      SOCKETIO: websocket:9000
      UPSTREAM_REAL_IP_ADDRESS: 127.0.0.1
      UPSTREAM_REAL_IP_HEADER: X-Forwarded-For
      UPSTREAM_REAL_IP_RECURSIVE: "off"
      PROXY_READ_TIMEOUT: 120
      CLIENT_MAX_BODY_SIZE: 50m
    volumes:
      - \${APPS_MOUNT:-apps}:/home/frappe/frappe-bench/apps
      - \${SITES_MOUNT:-sites}:/home/frappe/frappe-bench/sites
      - logs:/home/frappe/frappe-bench/logs
    ports:
      - "$PORT:8080"
    networks:
      - frappe_network
EOF
)

awk -v block="$SERVICE_BLOCK" '
  BEGIN { added = 0 }
  /^volumes:/ && !added {
    print block "\n"
    added = 1
  }
  { print }
' "$YML_PATH" > "$YML_TEMP" && mv "$YML_TEMP" "$YML_PATH"


# Step 3: Create temporary nginx config (HTTP only)
NGINX_PATH="/etc/nginx/sites-available/$DOMAIN"
NGINX_LINK="/etc/nginx/sites-enabled/$DOMAIN"

# Step 1: Create temporary nginx config (HTTP only)
cat <<EOF > "$NGINX_PATH"
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Step 2: Enable the site and reload nginx
ln -sf "$NGINX_PATH" "$NGINX_LINK"
nginx -t && systemctl reload nginx

# Step 3: Obtain SSL certificate using Certbot (HTTP challenge)
certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m kevin@tagrit.com

# Step 4: Replace config with SSL-enabled server block
cat <<EOF > "$NGINX_PATH"
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Step 5: Reload nginx with new SSL config
nginx -t && systemctl reload nginx

# Step 6: Start new container
echo "Starting new frontend container..."
./start.sh prod


echo ""
echo "✅✅✅ Site Provisioned Successfully!"
echo "------------------------------------------"
echo "🌐 Domain: $DOMAIN"
echo "🚪 Port: $PORT"
echo "📦 Installed Apps: $APPS"
echo ""
echo "🔗 You can now access your site at:"
echo "   👉 $DOMAIN"
echo "------------------------------------------"

# Copy new site  from Docker container to local system
docker cp frappe_prod-backend-1:/home/frappe/frappe-bench/sites/$DOMAIN /root/frappe_docker/sites/$DOMAIN

# Go to the frappe_docker directory
cd /root/frappe_docker

# Add all uncommited changes
git add -A

# Commit the changes
git commit -m "Added new site ($DOMAIN) and app ($DOMAIN) from Production"

# Push to GitHub (main branch or staging)
git push tagrit main

echo "✅ New site and app synced to GitHub!"
