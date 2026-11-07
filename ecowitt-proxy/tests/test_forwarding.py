"""Exercise the Flask route and Requests against a local webhook fixture."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest import TestCase, main
from urllib.parse import parse_qs
import sys

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


if __name__ == "__main__":
    main()
