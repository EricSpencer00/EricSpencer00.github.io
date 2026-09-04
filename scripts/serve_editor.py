#!/usr/bin/env python3
"""Run the project-copy desk locally, with saves to editor/index.md.

This server binds only to 127.0.0.1.  It deliberately has no public-hosting
path: the review desk is an authoring tool for this checkout.
"""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
EDITOR = ROOT / "editor"
MARKDOWN = EDITOR / "index.md"
MAX_BYTES = 2_000_000


class EditorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(EDITOR), **kwargs)

    def do_PUT(self) -> None:
        if urlparse(self.path).path != "/api/markdown":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_BYTES:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Invalid document size")
            return
        try:
            content = self.rfile.read(length).decode("utf-8")
        except UnicodeDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Markdown must be UTF-8")
            return
        if not content.startswith("# Project copy review"):
            self.send_error(HTTPStatus.BAD_REQUEST, "Unexpected document format")
            return
        temporary = MARKDOWN.with_suffix(".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(MARKDOWN)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        print(f"editor: {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local project copy desk")
    parser.add_argument("--port", type=int, default=4174)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), EditorHandler)
    print(f"Project copy desk: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProject copy desk stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
