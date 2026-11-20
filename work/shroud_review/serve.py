import hashlib
import json
import math
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL = Path.home() / "Desktop" / "Fan_Shroud_Recovered.stl"
MODEL_BYTES = MODEL.read_bytes()
SOURCE = hashlib.sha256(MODEL_BYTES).hexdigest()
STATE = ROOT / "annotations.json"
LOCK = threading.Lock()
PORT = 28742
HOST = f"127.0.0.1:{PORT}"
FILES = {"/": "index.html", "/app.js": "app.js", "/three.js": "three.js",
         "/orbit.js": "orbit.js", "/stl.js": "stl.js"}


def state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"model": SOURCE, "revision": 0, "marks": []}


def valid_mark(mark):
    if not isinstance(mark, dict) or not isinstance(mark.get("note"), str):
        return False
    points = mark.get("points")
    return (isinstance(points, list) and 1 <= len(points) <= 6000
            and all(isinstance(p, list) and len(p) == 3
                    and all(type(v) in (int, float) and math.isfinite(v) for v in p)
                    for p in points))


class Handler(BaseHTTPRequestHandler):
    def reply(self, data, kind):
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.headers.get("Host") != HOST:
            return self.send_error(403)
        if self.path == "/marks":
            return self.reply(json.dumps(state()).encode(), "application/json")
        if self.path == "/model.stl":
            return self.reply(MODEL_BYTES, "application/octet-stream")
        if self.path in FILES:
            file = ROOT / FILES[self.path]
            return self.reply(file.read_bytes(), "text/javascript" if file.suffix == ".js"
                              else mimetypes.guess_type(file)[0])
        self.send_error(404)

    def do_POST(self):
        if (self.path != "/marks" or self.headers.get("Host") != HOST
                or self.headers.get("Origin") != f"http://{HOST}"):
            return self.send_error(403)
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 4_000_000:
                return self.send_error(413)
            new = json.loads(self.rfile.read(size))
            if not isinstance(new["marks"], list) or not all(map(valid_mark, new["marks"])):
                return self.send_error(400)
            with LOCK:
                old = state()
                if new["revision"] != old["revision"] or old["model"] != SOURCE or new["model"] != SOURCE:
                    return self.send_error(409)
                new = dict(model=SOURCE, revision=old["revision"] + 1, marks=new["marks"])
                temp = STATE.with_suffix(".tmp")
                temp.write_text(json.dumps(new, ensure_ascii=False), encoding="utf-8")
                temp.replace(STATE)
            self.reply(json.dumps({"revision": new["revision"]}).encode(), "application/json")
        except (ValueError, KeyError, TypeError):
            self.send_error(400)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
