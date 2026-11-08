"""Exercise the Flask route and Requests against a local webhook fixture."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest import TestCase, main
from urllib.parse import parse_qs
import sys
import os
import ssl
from unittest.mock import patch
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import receiver


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.received = (
            self.path,
            self.headers.get("Authorization"),
            parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode()),
        )
        self.send_response(self.server.status)
        if self.server.status == 307:
            self.send_header("Location", "/redirect-target")
        self.end_headers()
        self.wfile.write(b"upstream response containing test-webhook-secret")

    def log_message(self, *_):
        pass


class ForwardingTest(TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), WebhookHandler)
        self.server.status = 200
        thread = Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(self.server.shutdown)
        old_url = receiver.forward_url
        self.addCleanup(setattr, receiver, "forward_url", old_url)
        receiver.forward_url = (
            f"http://127.0.0.1:{self.server.server_port}/api/webhook/test-webhook-secret"
        )
        self.client = receiver.app.test_client()

    def test_forwards_readings_without_authorization(self):
        response = self.client.post("/log/ha", data={"tempf": "71.8", "PASSKEY": "station"})
        self.assertEqual((response.status_code, response.data), (200, b"OK"))
        self.assertEqual(
            self.server.received,
            ("/api/webhook/test-webhook-secret", None, {"tempf": ["71.8"], "PASSKEY": ["station"]}),
        )

    def test_upstream_error_does_not_expose_response_body(self):
        self.server.status = 403
        with self.assertLogs(level="ERROR") as logs:
            response = self.client.post("/log/ha", data={"tempf": "71.8"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn(b"test-webhook-secret", response.data)
        self.assertNotIn("test-webhook-secret", "\n".join(logs.output))

    def test_does_not_follow_upstream_redirect(self):
        self.server.status = 307
        response = self.client.post("/log/ha", data={"tempf": "71.8"})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(self.server.received[0], "/api/webhook/test-webhook-secret")


    def test_request_failures_hide_webhook_url(self):
        secret = "https://example.invalid/api/webhook/test-webhook-secret"
        failures = (
            (requests.Timeout(secret), 504),
            (requests.exceptions.SSLError(secret), 502),
            (requests.ConnectionError(secret), 502),
        )
        for failure, expected_status in failures:
            with self.subTest(failure=type(failure).__name__):
                with patch.object(receiver.requests, "post", side_effect=failure):
                    with self.assertLogs(level="ERROR") as logs:
                        response = self.client.post("/log/ha", data={"tempf": "71.8"})
                self.assertEqual(response.status_code, expected_status)
                self.assertNotIn(b"test-webhook-secret", response.data)
                self.assertNotIn("test-webhook-secret", "\n".join(logs.output))

    def test_https_requires_trusted_certificate(self):
        tls_dir = Path(os.environ["TEST_TLS_DIR"])
        cert = tls_dir / "cert.pem"
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, tls_dir / "key.pem")
        server = ThreadingHTTPServer(("127.0.0.1", 0), WebhookHandler)
        server.status = 200
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        receiver.forward_url = (
            f"https://127.0.0.1:{server.server_port}/api/webhook/test-webhook-secret"
        )

        with patch.dict(os.environ, {"REQUESTS_CA_BUNDLE": str(cert)}):
            response = self.client.post("/log/ha", data={"tempf": "71.8", "PASSKEY": "station"})
        self.assertEqual((response.status_code, response.data), (200, b"OK"))
        self.assertEqual(
            server.received,
            ("/api/webhook/test-webhook-secret", None, {"tempf": ["71.8"], "PASSKEY": ["station"]}),
        )

        server.received = None
        with patch.dict(os.environ, {"REQUESTS_CA_BUNDLE": requests.certs.where()}):
            with self.assertLogs(level="ERROR") as logs:
                response = self.client.post("/log/ha", data={"tempf": "71.8"})
        self.assertEqual(response.status_code, 502)
        self.assertIsNone(server.received)
        self.assertNotIn(b"test-webhook-secret", response.data)
        self.assertNotIn("test-webhook-secret", "\n".join(logs.output))


if __name__ == "__main__":
    main()
