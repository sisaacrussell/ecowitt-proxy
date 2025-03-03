#!/bin/sh

# Set defaults if not provided
HA_WEBHOOK_ID=${HA_WEBHOOK_ID:-"your_actual_webhook_id"}
HA_BASE_URL=${HA_BASE_URL:-"http://homeassistant.local:8123/api/webhook/"}
HA_AUTH_TOKEN=${HA_AUTH_TOKEN:-"your_long_lived_access_token"}
ECOWITT_PROXY_PORT=${ECOWITT_PROXY_PORT:-"8082"}

echo "Using Home Assistant Webhook: $HA_BASE_URL$HA_WEBHOOK_ID"
echo "Using port: $ECOWITT_PROXY_PORT"

# Export variables so receiver.py can use them
export HA_WEBHOOK_ID
export HA_BASE_URL
export HA_AUTH_TOKEN
export ECOWITT_PROXY_PORT

# Run the Python script
exec python3 /app/receiver.py
