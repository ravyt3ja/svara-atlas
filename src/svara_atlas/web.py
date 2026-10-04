"""Local web app for importing and organizing public YouTube playlists."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from svara_atlas.connectors.youtube import YouTubeAPIError, fetch_public_playlist


STATIC_DIR = Path(__file__).parent / "static"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/static/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/static/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


class SvaraAtlasHandler(BaseHTTPRequestHandler):
    """Serve the organizer and its YouTube playlist import endpoint."""

    server_version = "SvaraAtlas/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/playlist":
            self._handle_playlist_request(parse_qs(parsed.query))
            return

        static_file = STATIC_FILES.get(parsed.path)
        if static_file is None:
            self.send_error(404, "Not found")
            return

        filename, content_type = static_file
        content = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self'; img-src 'self' "
            "https://i.ytimg.com; style-src 'self'; script-src 'self'; "
            "frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()
        self.wfile.write(content)

    def _handle_playlist_request(self, query: Dict[str, List[str]]) -> None:
        playlist_url = query.get("url", [""])[0]
        try:
            result = fetch_public_playlist(
                playlist_url, os.environ.get("YOUTUBE_API_KEY", "")
            )
        except ValueError as error:
            self._send_json({"error": str(error)}, status=400)
            return
        except YouTubeAPIError as error:
            status = 503 if not os.environ.get("YOUTUBE_API_KEY", "").strip() else 502
            self._send_json({"error": str(error)}, status=status)
            return
        self._send_json(result)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, _format_string: str, *_args: Any) -> None:
        """Keep local request logs concise and avoid logging query values."""
        del _format_string, _args
        super().log_message("%s %s", self.command, urlparse(self.path).path)


def main() -> None:
    """Run the local organizer web server."""
    host = os.environ.get("SVARA_ATLAS_HOST", "127.0.0.1")
    port = int(os.environ.get("SVARA_ATLAS_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), SvaraAtlasHandler)
    print("SvaraAtlas is running at http://{}:{}/".format(host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SvaraAtlas.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
