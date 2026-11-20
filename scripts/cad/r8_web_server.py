"""Shared Browser 3D Workspace HTTP server for BambuMod x Orbiter v2.5 R8.

Serves the interactive Three.js 3D annotation & transform workspace on
http://127.0.0.1:8765 and persists user 3D pin annotations, component transform
offsets, viewport snapshots, and parameter rebuild requests into
outputs/BambuMod_Orbiter25_Remix_R8/ so both the user and AI share live state.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import subprocess
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO = Path(__file__).resolve().parents[2]
WEB_DIR = REPO / "scripts" / "cad" / "r8_web_workspace"
NODE_MODULES_DIR = WEB_DIR / "node_modules"
BUILDER_PY = REPO / "scripts" / "cad" / "r8_live_builder.py"
FREECADCMD_EXE = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
MESH_DIR = OUT_DIR / "web_meshes"
MANIFEST_PATH = MESH_DIR / "manifest.json"
PARAMS_PATH = OUT_DIR / "r8_params.json"
REPORT_PATH = OUT_DIR / "r8_live_report.json"
NOTES_PATH = OUT_DIR / "r8_shared_notes.json"
SNAPSHOT_PATH = OUT_DIR / "r8_user_snapshot.png"

HOST = "127.0.0.1"
PORT = int(os.environ.get("R8_WEB_PORT", "8765"))

_LOCK = threading.Lock()
_REBUILD_STATE: dict[str, object] = {
    "status": "idle",
    "last_error": None,
    "started_at": None,
    "finished_at": None,
}


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _default_notes() -> dict:
    return {
        "updated_at": None,
        "general_note": "",
        "annotations": [],
        "transforms": {},
        "camera": None,
    }


def _run_rebuild_worker() -> None:
    env = os.environ.copy()
    env["R8_SKIP_FCSTD"] = "1"
    try:
        proc = subprocess.run(
            [str(FREECADCMD_EXE), str(BUILDER_PY)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO),
            check=False,
        )
        with _LOCK:
            _REBUILD_STATE["finished_at"] = time.time()
            if proc.returncode == 0:
                _REBUILD_STATE["status"] = "idle"
                _REBUILD_STATE["last_error"] = None
            else:
                _REBUILD_STATE["status"] = "error"
                _REBUILD_STATE["last_error"] = (proc.stderr or proc.stdout or f"Exit {proc.returncode}")[-1000:]
    except Exception as exc:
        with _LOCK:
            _REBUILD_STATE["finished_at"] = time.time()
            _REBUILD_STATE["status"] = "error"
            _REBUILD_STATE["last_error"] = str(exc)


def _safe_child(base: Path, rel: str) -> Path | None:
    clean = rel.lstrip("/").replace("\\", "/")
    candidate = (base / clean).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


class R8WorkspaceHandler(BaseHTTPRequestHandler):
    """Serve static frontend/vendor/meshes and JSON sync APIs."""

    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:
        return

    def _send_bytes(self, code: int, data: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, code: int, payload: object) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self._send_bytes(code, body, "application/json; charset=utf-8")

    def _read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/" or path == "/index.html":
            idx = WEB_DIR / "index.html"
            if not idx.is_file():
                self._send_bytes(HTTPStatus.NOT_FOUND, b"Missing index.html", "text/plain")
                return
            self._send_bytes(HTTPStatus.OK, idx.read_bytes(), "text/html; charset=utf-8")
            return

        if path == "/api/state":
            manifest = _read_json(MANIFEST_PATH, {})
            params = _read_json(PARAMS_PATH, {})
            report = _read_json(REPORT_PATH, {})
            notes = _read_json(NOTES_PATH, _default_notes())
            with _LOCK:
                rebuild = dict(_REBUILD_STATE)
            self._send_json(
                HTTPStatus.OK,
                {
                    "version": manifest.get("version", 0),
                    "manifest": manifest,
                    "params": params,
                    "report": report,
                    "notes": notes,
                    "rebuild": rebuild,
                    "snapshot_exists": SNAPSHOT_PATH.is_file(),
                },
            )
            return

        if path.startswith("/vendor/"):
            target = _safe_child(NODE_MODULES_DIR, path[len("/vendor/"):])
            if target is None:
                self._send_bytes(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
                return
            ctype, _ = mimetypes.guess_type(str(target))
            if target.suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            self._send_bytes(HTTPStatus.OK, target.read_bytes(), ctype or "application/octet-stream")
            return

        if path.startswith("/meshes/"):
            target = _safe_child(MESH_DIR, path[len("/meshes/"):])
            if target is None:
                self._send_bytes(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
                return
            self._send_bytes(HTTPStatus.OK, target.read_bytes(), "application/octet-stream")
            return

        self._send_bytes(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/save_notes":
            try:
                data = self._read_body_json()
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return

            notes = {
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "general_note": str(data.get("general_note", "")),
                "annotations": data.get("annotations", []),
                "transforms": data.get("transforms", {}),
                "clip": data.get("clip", None),
                "camera": data.get("camera", None),
            }
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            NOTES_PATH.write_text(json.dumps(notes, indent=2), encoding="utf-8")

            snap_url = data.get("snapshot_data_url")
            saved_snap = False
            if isinstance(snap_url, str) and snap_url.startswith("data:image/png;base64,"):
                try:
                    png_bytes = base64.b64decode(snap_url.split(",", 1)[1])
                    SNAPSHOT_PATH.write_bytes(png_bytes)
                    saved_snap = True
                except Exception:
                    saved_snap = False

            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "updated_at": notes["updated_at"],
                    "saved_snapshot": saved_snap,
                    "annotation_count": len(notes["annotations"]),
                },
            )
            return

        if path == "/api/rebuild":
            try:
                data = self._read_body_json()
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return

            with _LOCK:
                if _REBUILD_STATE["status"] == "running":
                    self._send_json(HTTPStatus.CONFLICT, {"ok": False, "error": "Rebuild already running"})
                    return
                current = _read_json(PARAMS_PATH, {})
                incoming = data.get("params", {})
                if isinstance(incoming, dict):
                    current.update(incoming)
                PARAMS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
                _REBUILD_STATE["status"] = "running"
                _REBUILD_STATE["last_error"] = None
                _REBUILD_STATE["started_at"] = time.time()
                _REBUILD_STATE["finished_at"] = None

            threading.Thread(target=_run_rebuild_worker, daemon=True).start()
            self._send_json(HTTPStatus.OK, {"ok": True, "status": "running"})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Unknown endpoint"})


def main() -> None:
    if not MANIFEST_PATH.exists():
        env = os.environ.copy()
        env["R8_SKIP_FCSTD"] = "1"
        subprocess.run([str(FREECADCMD_EXE), str(BUILDER_PY)], env=env, cwd=str(REPO), check=True)
    server = ThreadingHTTPServer((HOST, PORT), R8WorkspaceHandler)
    print(f"[R8 Web] Serving Shared 3D Workspace at http://{HOST}:{PORT}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
