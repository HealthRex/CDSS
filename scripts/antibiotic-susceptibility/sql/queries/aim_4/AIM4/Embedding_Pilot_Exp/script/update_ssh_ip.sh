#!/bin/bash

# Check if host and IP were provided
if [ $# -ne 2 ]; then
  echo "Usage: ./update_ssh_ip.sh <host_name> <new_ip>"
  exit 1
fi

HOST_NAME="$1"
NEW_IP="$2"
CONFIG_FILE="$HOME/.ssh/config"
BACKUP_FILE="$CONFIG_FILE.bak"

echo "Updating SSH config for host: $HOST_NAME with IP: $NEW_IP"
echo "Backing up config file to: $BACKUP_FILE"

# Backup existing config
cp "$CONFIG_FILE" "$BACKUP_FILE"

# Function to generate the new block
generate_block() {
  IDENTITY_FILE="~/.ssh/$HOST_NAME"
  USER=$(grep -A2 "^Host $HOST_NAME" "$BACKUP_FILE" | grep "User " | awk '{print $2}')
  if [ -z "$USER" ]; then
    USER="$USER_NAME" # default fallback
  fi
  cat <<EOF
Host $HOST_NAME
  HostName $NEW_IP
  User $USER
  IdentityFile $IDENTITY_FILE
EOF
}

# Remove the existing block for the host
awk -v host="^Host $HOST_NAME\$" '
  BEGIN {in_block=0}
  $0 ~ host {in_block=1; next}
  in_block && /^Host / {in_block=0}
  !in_block {print}
' "$BACKUP_FILE" > "$CONFIG_FILE.tmp"

mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Append the new block
echo "" >> "$CONFIG_FILE"
generate_block >> "$CONFIG_FILE"

echo "Done. Updated SSH block for $HOST_NAME:"
grep -A3 "^Host $HOST_NAME" "$CONFIG_FILE"
