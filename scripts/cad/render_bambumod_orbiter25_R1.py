"""Render multi-view part & assembly PNG previews for BambuMod x Orbiter v2.5 R1."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R1"


def rot_x(deg: float) -> np.ndarray:
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, s], [0, -s, c]], dtype=float)


def rot_z(deg: float) -> np.ndarray:
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def render_panel(parts: list[dict], R: np.ndarray, size: tuple[int, int] = (720, 620), title: str = "") -> Image.Image:
    all_v = np.vstack([np.array(p["v"], dtype=float) @ R.T for p in parts if p["v"]])
    mn, mx = all_v.min(0), all_v.max(0)
    span = max(mx[0] - mn[0], mx[1] - mn[1], 1.0)
    scale = min(size[0] - 70, size[1] - 90) / span
    cx, cy = (mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0

    light = np.array([0.32, 0.45, 0.83], dtype=float)
    light /= np.linalg.norm(light)

    tris = []
    for p in parts:
        if not p["v"] or not p["f"]:
            continue
        v = np.array(p["v"], dtype=float) @ R.T
        f = np.array(p["f"], dtype=int)
        col = np.array(p["color"], dtype=float)
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nl = np.linalg.norm(n, axis=1)
        valid = nl > 1e-9
        tri, n, nl = tri[valid], n[valid], nl[valid]
        n /= nl[:, None]
        inten = 0.34 + 0.66 * np.abs(n @ light)
        z = tri[:, :, 2].mean(axis=1)
        px = (tri[:, :, 0] - cx) * scale + size[0] / 2.0
        py = (size[1] + 24) / 2.0 - (tri[:, :, 1] - cy) * scale
        c = np.clip(np.outer(inten, col), 0, 255).astype(np.uint8)
        for i in range(len(tri)):
            tris.append((
                float(z[i]),
                [
                    (float(px[i, 0]), float(py[i, 0])),
                    (float(px[i, 1]), float(py[i, 1])),
                    (float(px[i, 2]), float(py[i, 2])),
                ],
                tuple(map(int, c[i])),
            ))

    tris.sort(key=lambda t: t[0])
    im = Image.new("RGB", size, (242, 246, 250))
    dr = ImageDraw.Draw(im)
    for _, pts, c in tris:
        dr.polygon(pts, fill=c)
    dr.rectangle((0, 0, size[0], 30), fill=(230, 236, 242))
    dr.text((16, 9), title, fill=(22, 32, 44))
    return im


def save_grid(parts: list[dict], out_png: Path, header: str, views: list[tuple[str, np.ndarray]]) -> None:
    pw, ph = 720, 620
    panels = [render_panel(parts, R, size=(pw, ph), title=t) for t, R in views]
    im = Image.new("RGB", (pw * 2, ph * 2 + 44), (242, 246, 250))
    im.paste(panels[0], (0, 44))
    im.paste(panels[1], (pw, 44))
    im.paste(panels[2], (0, ph + 44))
    im.paste(panels[3], (pw, ph + 44))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, pw * 2, 44), fill=(28, 38, 52))
    dr.text((18, 15), header, fill=(240, 244, 248))
    im.save(out_png)
    print(f"Saved {out_png}", flush=True)


def main() -> None:
    part_views = [
        ("FRONT (+Y -> viewer, +X Fan Left / -X Eddy Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR (-Y carriage face -> viewer, +X Fan Right)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("ISO FRONT-RIGHT (-X Eddy / Orbiter Shelf)", rot_x(66) @ rot_z(138)),
        ("ISO REAR-LEFT (+X 3010 Fan / Motor Cutout)", rot_x(66) @ rot_z(-42)),
    ]
    assy_views = [
        ("FRONT ASSEMBLY (+X Fan Left / -X Eddy Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR ASSEMBLY (Slanted motor & JST relief)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("RIGHT SIDE (-X -> viewer: Latch / EBB42 / Fins)", np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], dtype=float)),
        ("LEFT SIDE (+X -> viewer: 3010 Fan & Orbiter Plate)", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
    ]

    for tag, label in [
        ("primary", "PRIMARY (Centered Motor X=0 | X1C Shifted -6.335 mm Right | Z_mount=32.6)"),
        ("alternate", "ALTERNATE (Stock Nozzle X=0 | Shifted Motor +6.335 mm | 3010 Fan Pod | Z_mount=32.0)"),
    ]:
        data = json.loads((OUT_DIR / f"preview_{tag}.json").read_text(encoding="utf-8"))
        adapter_only = [p for p in data if p["name"] == "adapter"]
        title_prefix = "Primary" if tag == "primary" else "Alternate"
        save_grid(
            adapter_only,
            OUT_DIR / f"{title_prefix}_part_views.png",
            f"{label} -- PRINTED CARRIAGE ADAPTER ONLY",
            part_views,
        )
        save_grid(
            data,
            OUT_DIR / f"{title_prefix}_assembly_views.png",
            f"{label} -- FULL TOOLHEAD STACK CHECK",
            assy_views,
        )


if __name__ == "__main__":
    main()
