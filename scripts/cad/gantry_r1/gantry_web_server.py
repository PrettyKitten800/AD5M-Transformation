"""Shared Browser 3D Workspace HTTP server for AD5M 3x MGN12H Linear-Rail Gantry R1.

Serves the interactive Three.js 3D annotation & inspection workspace on
http://127.0.0.1:8766 (separate from the R8 toolhead server on 8765) and persists
user 3D pin annotations, component offsets, and snapshots into
outputs/AD5M_MGN12_Gantry_R1/.
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

REPO = Path(__file__).resolve().parents[3]
WEB_DIR = REPO / "scripts" / "cad" / "gantry_r1" / "web_workspace"
NODE_MODULES_DIR = REPO / "scripts" / "cad" / "r8_web_workspace" / "node_modules"
BUILDER_PY = REPO / "scripts" / "cad" / "gantry_r1" / "build_gantry_r1.py"
FREECAD_PYTHON = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")

OUT_DIR = REPO / "outputs" / "AD5M_MGN12_Gantry_R1"
MESH_DIR = OUT_DIR / "parts"
MANIFEST_PATH = OUT_DIR / "manifest.json"
REPORT_PATH = OUT_DIR / "validation.json"
NOTES_PATH = OUT_DIR / "gantry_shared_notes.json"
SNAPSHOT_PATH = OUT_DIR / "gantry_user_snapshot.png"

HOST = "127.0.0.1"
PORT = int(os.environ.get("GANTRY_WEB_PORT", "8766"))

_LOCK = threading.Lock()
_REBUILD_STATE: dict[str, object] = {
    "status": "idle",
    "last_error": None,
    "started_at": None,
    "finished_at": None,
}


def build_manifest_payload() -> dict:
    parts = [
        {"id": "Ref_AD5M_Frame", "label": "AD5M Steel Frame (Ref)", "stl": "/meshes/Ref_AD5M_Frame.stl", "color": "#4f5966", "opacity": 0.25, "uses_dz": False, "movable": False},
        {"id": "Ref_Rails_Blocks", "label": "3x MGN12H 300mm Rails & Blocks", "stl": "/meshes/Ref_Rails_Blocks.stl", "color": "#cfd6df", "opacity": 0.95, "uses_dz": False, "movable": False},
        {"id": "Ref_Motors_48mm", "label": "NEMA17 48mm XY Motors", "stl": "/meshes/Ref_Motors_48mm.stl", "color": "#262930", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Ref_Pulleys_Bearings", "label": "20T Pulleys & F695-2RS Stacks", "stl": "/meshes/Ref_Pulleys_Bearings.stl", "color": "#eab308", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Ref_Dowel_Pins", "label": "Hardened Ø5mm Dowel Pins", "stl": "/meshes/Ref_Dowel_Pins.stl", "color": "#e2e8f0", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Ref_Belt_A", "label": "Belt A (Upper Z=381.0)", "stl": "/meshes/Ref_Belt_A.stl", "color": "#ef4444", "opacity": 0.95, "uses_dz": False, "movable": True},
        {"id": "Ref_Belt_B", "label": "Belt B (Lower Z=370.0)", "stl": "/meshes/Ref_Belt_B.stl", "color": "#22c55e", "opacity": 0.95, "uses_dz": False, "movable": True},
        {"id": "Y_Rail_Spine_R", "label": "Y-Rail Spine Right (+X)", "stl": "/meshes/Y_Rail_Spine_R.stl", "color": "#2e6fe0", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Y_Rail_Spine_L", "label": "Y-Rail Spine Left (-X)", "stl": "/meshes/Y_Rail_Spine_L.stl", "color": "#2e6fe0", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Rear_Motor_Mount_R", "label": "Rear 48mm Motor Mount Right", "stl": "/meshes/Rear_Motor_Mount_R.stl", "color": "#3898ff", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Rear_Motor_Mount_L", "label": "Rear 48mm Motor Mount Left", "stl": "/meshes/Rear_Motor_Mount_L.stl", "color": "#3898ff", "opacity": 1.0, "uses_dz": False, "movable": False},
        {"id": "Motor_DS_Cap_R", "label": "Rear Motor Double-Shear Cap Right", "stl": "/meshes/Motor_DS_Cap_R.stl", "color": "#fb923c", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "Motor_DS_Cap_L", "label": "Rear Motor Double-Shear Cap Left", "stl": "/meshes/Motor_DS_Cap_L.stl", "color": "#fb923c", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "Front_BFI_Housing_R", "label": "Front BFI Housing Right", "stl": "/meshes/Front_BFI_Housing_R.stl", "color": "#3898ff", "opacity": 0.95, "uses_dz": False, "movable": False},
        {"id": "Front_BFI_Housing_L", "label": "Front BFI Housing Left", "stl": "/meshes/Front_BFI_Housing_L.stl", "color": "#3898ff", "opacity": 0.95, "uses_dz": False, "movable": False},
        {"id": "Front_BFI_Carrier_R", "label": "Front BFI Slider Right", "stl": "/meshes/Front_BFI_Carrier_R.stl", "color": "#f59e0b", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "Front_BFI_Carrier_L", "label": "Front BFI Slider Left", "stl": "/meshes/Front_BFI_Carrier_L.stl", "color": "#f59e0b", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "XY_Joint_R_Upper", "label": "XY Joint Right Upper (+X)", "stl": "/meshes/XY_Joint_R_Upper.stl", "color": "#8b5cf6", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "XY_Joint_R_Lower", "label": "XY Joint Right Lower (+X)", "stl": "/meshes/XY_Joint_R_Lower.stl", "color": "#38bdf8", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "XY_Joint_R_Bottom_Cap", "label": "XY Joint Right Bottom Cap (+X)", "stl": "/meshes/XY_Joint_R_Bottom_Cap.stl", "color": "#fb923c", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "XY_Joint_L_Upper", "label": "XY Joint Left Upper (-X)", "stl": "/meshes/XY_Joint_L_Upper.stl", "color": "#8b5cf6", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "XY_Joint_L_Lower", "label": "XY Joint Left Lower (-X)", "stl": "/meshes/XY_Joint_L_Lower.stl", "color": "#38bdf8", "opacity": 1.0, "uses_dz": False, "movable": True},
        {"id": "X_Carriage_MGN12_Base_R1", "label": "X-Carriage MGN12H Base R1", "stl": "/meshes/X_Carriage_MGN12_Base_R1.stl", "color": "#14b8a6", "opacity": 1.0, "uses_dz": False, "movable": True},
    ]
    mtime = 0.0
    for p in parts:
        fp = MESH_DIR / Path(p["stl"]).name
        if fp.is_file():
            mtime = max(mtime, fp.stat().st_mtime)
    return {"version": mtime or time.time(), "parts": parts}


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
    try:
        proc = subprocess.run(
            [str(FREECAD_PYTHON), str(BUILDER_PY)],
            capture_output=True,
            text=True,
            cwd=str(REPO),
            check=False,
        )
        with _LOCK:
            _REBUILD_STATE["finished_at"] = time.time()
            if proc.returncode == 0:
                MANIFEST_PATH.write_text(json.dumps(build_manifest_payload(), indent=2), encoding="utf-8")
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


class GantryWorkspaceHandler(BaseHTTPRequestHandler):
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
            manifest = build_manifest_payload()
            report = _read_json(REPORT_PATH, {})
            notes = _read_json(NOTES_PATH, _default_notes())
            with _LOCK:
                rebuild = dict(_REBUILD_STATE)
            self._send_json(
                HTTPStatus.OK,
                {
                    "version": manifest.get("version", 0),
                    "manifest": manifest,
                    "params": {},
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
            with _LOCK:
                if _REBUILD_STATE["status"] == "running":
                    self._send_json(HTTPStatus.CONFLICT, {"ok": False, "error": "Rebuild already running"})
                    return
                _REBUILD_STATE["status"] = "running"
                _REBUILD_STATE["last_error"] = None
                _REBUILD_STATE["started_at"] = time.time()
                _REBUILD_STATE["finished_at"] = None

            threading.Thread(target=_run_rebuild_worker, daemon=True).start()
            self._send_json(HTTPStatus.OK, {"ok": True, "status": "running"})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Unknown endpoint"})


def main() -> None:
    if not (MESH_DIR / "X_Carriage_MGN12_Base_R1.stl").exists():
        subprocess.run([str(FREECAD_PYTHON), str(BUILDER_PY)], cwd=str(REPO), check=True)
    MANIFEST_PATH.write_text(json.dumps(build_manifest_payload(), indent=2), encoding="utf-8")
    server = ThreadingHTTPServer((HOST, PORT), GantryWorkspaceHandler)
    print(f"[Gantry R1 Web] Serving Shared 3D Workspace at http://{HOST}:{PORT}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
