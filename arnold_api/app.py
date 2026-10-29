"""Tiny HTTP runtime for the ArnoldAPI DSL."""
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlsplit

Handler = Callable[[dict[str, Any]], Any]


class ArnoldAPI:
    def __init__(self) -> None:
        self.routes: list[tuple[str, re.Pattern[str], Handler, str]] = []

    def route(self, method: str, path: str, handler: Handler) -> None:
        names: list[str] = []
        pattern = re.sub(r"<([A-Za-z_][A-Za-z0-9_]*)>", lambda m: names.append(m.group(1)) or rf"(?P<{names[-1]}>[^/]+)", path)
        self.routes.append((method.upper(), re.compile(rf"^{pattern}$"), handler, path))

    def load(self, source: str | Path) -> None:
        """Load the small ArnoldAPI extension syntax used by .arnoldc files."""
        text = Path(source).read_text(encoding="utf-8") if isinstance(source, Path) else source
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("//")]
        i = 0
        while i < len(lines):
            match = re.fullmatch(r'ROUTE\s+"(GET|POST|PUT|PATCH|DELETE)"\s+"([^"]+)"', lines[i])
            if not match:
                i += 1
                continue
            method, path = match.groups(); i += 1
            if i >= len(lines): raise ValueError(f"Missing response after {method} {path}")
            response = re.fullmatch(r'TALK TO THE HAND\s+"(.*)"', lines[i])
            payload = re.fullmatch(r'RETURN JSON\s+"(.*)"', lines[i])
            if response:
                value = response.group(1).replace('\\"', '"')
                handler = lambda request, value=value: value
            elif payload:
                raw = payload.group(1).replace('\\"', '"')
                value = json.loads(raw)
                handler = lambda request, value=value: value
            else:
                raise ValueError(f"Unsupported response syntax: {lines[i]}")
            self.route(method, path, handler); i += 1
            if i < len(lines) and lines[i] == "ENOUGH TALK": i += 1

    def _match(self, method: str, path: str):
        for route_method, pattern, handler, template in self.routes:
            match = pattern.match(path)
            if route_method == method and match:
                return handler, match.groupdict(), template
        return None

    def serve(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        app = self
        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                print(f"{self.command} {self.path} - {format % args}")
            def do_GET(self): self._dispatch()
            def do_POST(self): self._dispatch()
            def do_PUT(self): self._dispatch()
            def do_PATCH(self): self._dispatch()
            def do_DELETE(self): self._dispatch()
            def _dispatch(self):
                parsed = urlsplit(self.path); found = app._match(self.command, parsed.path)
                if not found:
                    self._send(404, {"error": "not found"}); return
                handler, params, template = found
                request = {"method": self.command, "path": parsed.path, "params": params,
                           "query": {k: v[-1] for k, v in parse_qs(parsed.query).items()}}
                try: result = handler(request); self._send(200, result)
                except Exception as exc: self._send(500, {"error": str(exc)})
            def _send(self, status, value):
                body = value.encode() if isinstance(value, str) else json.dumps(value).encode()
                content_type = "text/plain; charset=utf-8" if isinstance(value, str) else "application/json"
                self.send_response(status); self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        print(f"ArnoldAPI listening on http://{host}:{port}")
        ThreadingHTTPServer((host, port), RequestHandler).serve_forever()
