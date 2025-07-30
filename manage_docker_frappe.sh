#!/bin/bash

# File: manage_docker_frappe
# Description: Manage Frappe stack in Docker with simple commands

FRAPPE_DIR="/root/frappe_docker"
START_SCRIPT="$FRAPPE_DIR/start.sh"
STOP_SCRIPT="$FRAPPE_DIR/stop.sh"

function usage() {
  echo ""
  echo "🛠️  Manage Frappe Docker Containers"
  echo ""
  echo "Usage:"
  echo "  manage_docker_frappe start            Start or restart the Frappe stack"
  echo "  manage_docker_frappe stop             Stop the stack (volumes are preserved)"
  echo "  manage_docker_frappe stop --clean     ⚠️ Stop and REMOVE volumes (irreversible)"
  echo "  manage_docker_frappe status           Show running Frappe containers"
  echo "  manage_docker_frappe help             Show this help message"
  echo ""
}

case "$1" in
  start)
    echo "🚀 Starting Frappe stack..."
    cd "$FRAPPE_DIR" && "$START_SCRIPT" prod
    ;;
  stop)
    if [[ "$2" == "--clean" ]]; then
      echo "⚠️ WARNING: This will remove Docker volumes (all data not persisted in DB is lost)."
      read -p "Are you sure? Type 'yes' to continue: " confirm
      if [[ "$confirm" == "yes" ]]; then
        echo "🧼 Stopping Frappe and cleaning volumes..."
        cd "$FRAPPE_DIR" && "$STOP_SCRIPT" prod --clean
      else
        echo "❌ Operation cancelled."
        exit 1
      fi
    else
      echo "🛑 Stopping Frappe stack (volumes preserved)..."
      cd "$FRAPPE_DIR" && "$STOP_SCRIPT" prod
    fi
    ;;
  status)
    echo "📦 Current Frappe Docker containers:"
    docker ps --filter "name=frappe_prod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ;;
  help|"")
    usage
    ;;
  *)
    echo "❌ Unknown command: $1"
    usage
    exit 1
    ;;
esac
