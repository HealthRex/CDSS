#!/bin/bash

# Check if host, IP, and identity file were provided
if [ $# -ne 3 ]; then
  echo "Usage: ./update_ssh_ip.sh <host_name> <new_ip> <identity_file>"
  exit 1
fi

HOST_NAME="$1"
NEW_IP="$2"
IDENTITY_FILE="$3"
CONFIG_FILE="$HOME/.ssh/config"
BACKUP_FILE="$CONFIG_FILE.bak"

echo "Updating SSH config for host: $HOST_NAME with IP: $NEW_IP"
echo "Using identity file: $IDENTITY_FILE"
echo "Backing up config file to: $BACKUP_FILE"

# Backup existing config
cp "$CONFIG_FILE" "$BACKUP_FILE"

# Get the User from the existing block, if present
USER=$(awk -v host="^Host $HOST_NAME\$" '
    BEGIN {in_block=0}
    $0 ~ host {in_block=1; next}
    in_block && /^Host / {in_block=0}
    in_block && /^ *User / {print $2; exit}
' "$BACKUP_FILE")

if [ -z "$USER" ]; then
  USER="$USER_NAME" # fallback to default environment variable or leave blank
fi

# Remove the existing block for the host
awk -v host="^Host $HOST_NAME\$" '
  BEGIN {in_block=0}
  $0 ~ host {in_block=1; next}
  in_block && /^Host / {in_block=0}
  !in_block {print}
' "$BACKUP_FILE" > "$CONFIG_FILE.tmp"

mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

# Append the new block
cat <<EOF >> "$CONFIG_FILE"

Host $HOST_NAME
  HostName $NEW_IP
  User $USER
  IdentityFile ~/.ssh/$IDENTITY_FILE
EOF

echo "Done. Updated SSH block for $HOST_NAME:"
grep -A4 "^Host $HOST_NAME" "$CONFIG_FILE"
