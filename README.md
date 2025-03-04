# Home Assistant Ecowitt Proxy

This repository contains a **standalone Docker container** that acts as an **HTTP proxy** for Ecowitt weather stations, enabling them to send data to Home Assistant via a webhook.

## Features
- Allows **Ecowitt devices to send data to Home Assistant** even if HA is running over HTTPS.
- Forwards data to the **Home Assistant webhook API**.
- Works as a **Docker container** without requiring Home Assistant Supervisor.

---

## Installation (Standalone Docker)
### Option 1: Run with Docker CLI
Run the following command to start the `ecowitt-proxy` container:

```bash
docker run -d \
  --name ecowitt-proxy \
  -p 8082:8082 \
  -e HA_BASE_URL="http://homeassistant.local:8123/api/webhook/" \
  -e HA_WEBHOOK_ID="your_actual_webhook_id" \
  -e HA_AUTH_TOKEN="your_long_lived_access_token" \
  -e ECOWITT_PROXY_PORT=8082 \
  ecowitt-proxy
```

Make sure to replace:

- homeassistant.local:8123 with your actual Home Assistant URL.
- your_actual_webhook_id with your Home Assistant webhook ID.
- your_long_lived_access_token with a valid HA Long-Lived Access Token.

### Option 2: Run with docker-compose
If you prefer docker-compose, create a file named docker-compose.yml:

```yaml
version: '3.7'
services:
  ecowitt-proxy:
    container_name: ecowitt-proxy
    image: ecowitt-proxy
    restart: unless-stopped
    ports:
      - "8082:8082"
    environment:
      HA_BASE_URL: "http://homeassistant.local:8123/api/webhook/"
      HA_WEBHOOK_ID: "your_actual_webhook_id"
      HA_AUTH_TOKEN: "your_long_lived_access_token"
      ECOWITT_PROXY_PORT: 8082
```

Then start it with:

```bash
docker-compose up -d
```

---

## How to Use

In your Ecowitt gateway, configure as you would for the [Home Assistant Ecowitt Integration](https://www.home-assistant.io/integrations/ecowitt/), substituting the `Path` option with `/log/ha` only. Do not include your webhook ID here; it will be added to the path automatically by the add-on.

## Ecowitt Configuration - Customized Service

- Customized: Enable
- Protocol Type: Ecowitt
- Server IP / Hostname: Your Home Assistant base URL
- Path: `/log/ha`
- Port: Set to the same port configured in the add-on, default 8082
- Upload interval: Your choice

---

## Verify It's Working
1. Check the ecowitt-proxy logs:

```bash
docker logs ecowitt-proxy
```

You should see:

```bash
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8082
 * Running on http://10.0.20.95:8082
2025-03-03 16:49:38 INFO     Press CTRL+C to quit
Using Home Assistant Webhook: https://homeassistant.local/api/webhook/<your_actual_webhook_id>
Using port: 8082
2025-03-03 16:49:50 INFO     <ECOWITT_IP> - - [03/Mar/2025 16:49:50] "POST /log/ha HTTP/1.1" 200 -
```

---

## Credits

This project is based on the original [Home Assistant Ecowitt Proxy Add-on](https://github.com/chrisromp/addon-ecowitt-proxy) created by [Chris Rompon](https://github.com/chrisromp). The original add-on provided the foundation for this standalone Docker container.

## Modifications

The following changes were made to convert the Home Assistant Add-on into a standalone Docker container:

1. Removed Home Assistant Add-on specific configuration and dependencies
2. Added environment variables for configuration instead of the Add-on configuration panel
3. Modified the Docker build process to work independently of the Home Assistant Supervisor
4. Added direct webhook URL configuration instead of relying on Home Assistant's internal service discovery
5. Updated documentation to reflect Docker-specific configuration and usage
6. Added support for Long-lived Access Tokens for authentication with Home Assistant
7. Simplified the deployment process for non-Home Assistant Supervisor environments

These modifications allow the proxy to function as a standalone Docker container while maintaining all the functionality of the original Home Assistant Add-on.

