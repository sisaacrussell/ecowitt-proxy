#!/bin/sh

# Use environment variables instead of bashio
HA_WEBHOOK_ID=${HA_WEBHOOK_ID:-"your_default_webhook_id"}
ECOWITT_PROXY_PORT=${ECOWITT_PROXY_PORT:-"8080"}

echo "Using webhook ID: $HA_WEBHOOK_ID"
echo "Using port: $ECOWITT_PROXY_PORT"

# Export variables so receiver.py can use them
export HA_WEBHOOK_ID
export ECOWITT_PROXY_PORT

# Run the Python script
exec python3 /app/receiver.py
