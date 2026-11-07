from flask import Flask, request
import requests
import os
import sys
import logging

app = Flask("Ecowitt Proxy")

# Vars from environment variables
# Not all of these are settable from the add-on configuration; however, I wanted to give extra
# flexibility in case someone wanted to run this outside of a Home Assistant add-on.
log_level = os.environ.get('ECOWITT_PROXY_LOG_LEVEL', 'INFO')  # TODO
service_port = os.environ.get('ECOWITT_PROXY_PORT', '8082')
ha_webhook_id = os.environ.get('HA_WEBHOOK_ID', 'no-webhook-id')
base_url = os.environ.get('HA_BASE_URL', 'http://supervisor/core/api/webhook/')
forward_url = base_url + ha_webhook_id

# Set logging level
logger_level = logging.INFO  # Default
if log_level == 'DEBUG':
    logger_level = logging.DEBUG
if log_level == 'WARNING':
    logger_level = logging.WARNING

# Set logging format
logger_format = logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Init logger
logging.basicConfig(stream=sys.stdout, level=logger_level,
                    format=logger_format)


@app.route('/')
def version():
    return "Home Assistant Ecowitt Proxy\n"

# Show a friendly error if someone tries to access the webhook URL directly


@app.route('/log/ha', methods=['GET'])
def logHomeAssistantGet():
    return "Requires POST operation\n"


@app.route('/log/ha', methods=['POST'])
def logHomeAssistant():
    # Get form data
    payload = request.form

    # Log payload to console
    logging.debug("Received Payload: " + str(payload))

    try:
        with requests.post(
            forward_url, data=payload, timeout=5, allow_redirects=False, stream=True
        ) as response:
            status = response.status_code
    except requests.Timeout:
        logging.error("Home Assistant webhook request timed out")
        return "Home Assistant webhook request timed out\n", 504
    except requests.RequestException:
        logging.error("Home Assistant webhook request failed")
        return "Home Assistant webhook request failed\n", 502

    if status != 200:
        logging.error("Home Assistant webhook returned HTTP %s", status)
        return "Home Assistant webhook rejected the request\n", 502
    return "OK"


if __name__ == "__main__":
    # Verify webhook ID is set
    if ha_webhook_id == 'no-webhook-id':
        logger.error("HA_WEBHOOK_ID environment variable not set.")
        exit(1)

    logging.info("Starting Home Assistant Ecowitt Proxy")

    # Suppress Flask development server startup message (not working?)
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    app.run(host="0.0.0.0", port=service_port, debug=log_level == 'DEBUG')
