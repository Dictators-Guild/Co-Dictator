import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

log = logging.getLogger(__name__)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, *_args):
        pass


def start_health_server() -> None:
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _Handler)
    Thread(target=server.serve_forever, daemon=True, name="health").start()
    log.info("Health server listening on :%d", port)
