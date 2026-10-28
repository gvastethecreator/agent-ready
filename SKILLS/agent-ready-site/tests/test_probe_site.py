"""Response-size regression through the HTTP fetch interface; no external traffic."""

import gzip
import importlib.util
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import threading
import unittest
import zlib


spec = importlib.util.spec_from_file_location(
    "probe_site", Path(__file__).resolve().parents[1] / "scripts" / "probe_site.py"
)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ResponseLimitTest(unittest.TestCase):
    def test_compressed_responses_respect_decoded_limit(self):
        payload = b"x" * (probe.MAX_BODY + 1)
        compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        bodies = {
            "gzip": gzip.compress(payload),
            "deflate": compressor.compress(payload) + compressor.flush(),
        }

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                encoding = self.path.lstrip("/")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Encoding", encoding)
                self.end_headers()
                self.wfile.write(bodies[encoding])

            def log_message(self, *args):
                pass

        with HTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                fetch = probe.Fetcher(probe.TOOL_UA, limit=2, delay=0, timeout=5)
                for encoding in bodies:
                    with self.subTest(encoding=encoding):
                        result = fetch.get(f"http://127.0.0.1:{server.server_port}/{encoding}")
                        self.assertEqual(result["status"], 200)
                        self.assertEqual(result["bytes"], probe.MAX_BODY)
                        self.assertEqual(result["_body"], "x" * probe.MAX_BODY)
                        self.assertTrue(result["truncated"])
                        self.assertNotIn("note", result)
            finally:
                server.shutdown()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
