#!/bin/bash

echo -e "🔍 Ports currently used by Frappe frontend containers:\n"
printf "%-10s %-20s\n" "PORT" "SITE"
echo "------------------------------"

# Declare an array to store used ports
declare -a used_ports=()

# Process containers without subshells
while read -r name ports; do
    site=$(echo "$name" | sed -E 's/^frappe_prod-frontend-//;s/-[0-9]+$//')

    # Break comma-separated port mappings
    IFS=',' read -ra port_mappings <<< "$ports"
    for mapping in "${port_mappings[@]}"; do
        host_port=$(echo "$mapping" | grep -oP '(?<=0.0.0.0:)[0-9]+')
        if [[ -n "$host_port" ]]; then
            printf "%-10s %-20s\n" "$host_port" "$site"
            used_ports+=("$host_port")
        fi
    done
done < <(docker ps --format '{{.Names}} {{.Ports}}' | grep 'frontend')

# Get sorted, unique list of used ports
if [[ ${#used_ports[@]} -gt 0 ]]; then
    sorted_ports=($(printf "%s\n" "${used_ports[@]}" | sort -n | uniq))
    last_port="${sorted_ports[-1]}"
    suggested_port=$((last_port + 1))
    echo -e "\n✅ Suggested next available port: $suggested_port"
else
    echo -e "\n✅ No ports in use. Suggested starting port: 8081"
fi
