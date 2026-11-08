#!/bin/sh

# Set defaults if not provided
HA_WEBHOOK_ID=${HA_WEBHOOK_ID:-"your_actual_webhook_id"}
HA_BASE_URL=${HA_BASE_URL:-"http://homeassistant.local:8123/api/webhook/"}
ECOWITT_PROXY_PORT=${ECOWITT_PROXY_PORT:-"8082"}

echo "Using port: $ECOWITT_PROXY_PORT"

export HA_WEBHOOK_ID HA_BASE_URL ECOWITT_PROXY_PORT
exec python3 /app/receiver.py
