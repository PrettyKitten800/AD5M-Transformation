#!/usr/bin/env python3
"""Render multi-view previews for AD5M_custom_toolhead_inline_eddy_R1:
- Assembly_preview.png (custom housing + EBB42 R7 mount + Bambu X1C hotend + inline Eddy bracket + Eddy Duo)
- Housing_preview.png (AD5M_Custom_Housing_R1 4-view)
- Bracket_preview.png (Eddy_Duo_Inline_Mount_R1 4-view showing front contact face & rear recessed nut channels)
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "AD5M_custom_toolhead_inline_eddy_R1"


def rot_x(deg):
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, s], [0, -s, c]], dtype=float)


def rot_z(deg):
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def render_panel(parts, R, size=(720, 620), title=""):
    all_v = np.vstack([p[0] @ R.T for p in parts])
    mn, mx = all_v.min(0), all_v.max(0)
    span = max(mx[0] - mn[0], mx[1] - mn[1], 1.0)
    scale = min(size[0] - 80, size[1] - 100) / span
    cx, cy = (mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0

    light = np.array([0.32, 0.45, 0.83], dtype=float)
    light /= np.linalg.norm(light)

    tris = []
    for v, f, col in parts:
        vr = v @ R.T
        tri = vr[f]
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
            tris.append(
                (
                    float(z[i]),
                    [(float(px[i, 0]), float(py[i, 0])), (float(px[i, 1]), float(py[i, 1])), (float(px[i, 2]), float(py[i, 2]))],
                    tuple(map(int, c[i])),
                )
            )
    tris.sort(key=lambda t: t[0])
    im = Image.new("RGB", size, (242, 246, 249))
    dr = ImageDraw.Draw(im)
    for _, pts, col in tris:
        dr.polygon(pts, fill=col)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    dr.text((22, 16), title, fill=(32, 42, 52), font=font)
    return im


def make_grid(panels, size=(720, 620)):
    im = Image.new("RGB", (size[0] * 2, size[1] * 2), (242, 246, 249))
    im.paste(panels[0], (0, 0))
    im.paste(panels[1], (size[0], 0))
    im.paste(panels[2], (0, size[1]))
    im.paste(panels[3], (size[0], size[1]))
    return im


def main():
    prev = json.loads((OUT / "preview_parts.json").read_text())
    vh = np.array(prev["housing"]["v"], dtype=float)
    fh = np.array(prev["housing"]["f"], dtype=int)
    vb = np.array(prev["bracket"]["v"], dtype=float)
    fb = np.array(prev["bracket"]["f"], dtype=int)

    # Load EBB42 R7 top bracket
    r7 = json.loads((ROOT / "outputs" / "EBB42_uniform_posts_R7" / "preview_parts.json").read_text())
    v_r7 = np.array(r7[1]["v"], dtype=float)
    f_r7 = np.array(r7[1]["f"], dtype=int)

    # Load Bambu X1C hotend and Eddy Duo from Custom_toolhead_reference_R1
    cref = json.loads((ROOT / "outputs" / "Custom_toolhead_reference_R1" / "preview_mesh.json").read_text())
    hotend_parts = []
    for i in range(3):
        pv = np.array(cref[i]["v"], dtype=float)
        pf = np.array(cref[i]["f"], dtype=int)
        nv = np.zeros_like(pv)
        nv[:, 0] = -pv[:, 1]
        nv[:, 1] = pv[:, 0] + 12.08
        nv[:, 2] = pv[:, 2] - 13.58
        hotend_parts.append((nv, pf, np.array(cref[i]["color"], dtype=float)))

    # Place Eddy Duo against front of bracket (Y_bracket_front = 34.12 mm)
    # In cref[3], X_ref in [16.95, 35.25], Y_ref in [-9.05, 9.05], Z_ref in [2.5, 36.29]
    ev_ref = np.array(cref[3]["v"], dtype=float)
    ef_ref = np.array(cref[3]["f"], dtype=int)
    ev = np.zeros_like(ev_ref)
    ev[:, 0] = -ev_ref[:, 1]
    ev[:, 1] = (ev_ref[:, 0] - 16.95) + 34.12
    ev[:, 2] = ev_ref[:, 2] - 13.58
    eddy_part = (ev, ef_ref, np.array([52, 62, 70], dtype=float))

    R_front = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)
    R_side = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)
    R_top = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    R_iso = rot_x(64) @ rot_z(142)
    R_rear_iso = rot_x(64) @ rot_z(-38)

    assy_parts = [
        (vh, fh, np.array([152, 168, 182], dtype=float)),
        (v_r7, f_r7, np.array([98, 152, 162], dtype=float)),
        *hotend_parts,
        (vb, fb, np.array([239, 148, 46], dtype=float)),
        eddy_part,
    ]
    im_assy = make_grid(
        [
            render_panel(assy_parts, R_iso, title="ISOMETRIC | Inline Eddy (x_offset = 0) + Custom Housing"),
            render_panel(assy_parts, R_side, title="SIDE | Eddy +2.5 mm above nozzle, 4 mm bracket on bulkhead"),
            render_panel(assy_parts, R_front, title="FRONT | Eddy centered on nozzle X=0, 10 mm vertical slots"),
            render_panel(assy_parts, R_top, title="TOP | EBB42 R7 mount + inline front Eddy alignment"),
        ]
    )
    im_assy.save(OUT / "Assembly_preview.png")

    h_parts = [(vh, fh, np.array([145, 165, 182], dtype=float)), *hotend_parts]
    im_housing = make_grid(
        [
            render_panel(h_parts, R_iso, title="FRONT ISO | Reinforced M3 bosses + skeletonized side windows"),
            render_panel(h_parts, R_side, title="SIDE | Self-supporting hex windows + 3010 fan & heatsink fit"),
            render_panel(h_parts, R_front, title="FRONT | Four 2.5 mm M3 pilot holes (24 x 8.0 mm) + hotend fit"),
            render_panel(h_parts, R_rear_iso, title="REAR ISO | Stock AD5M carriage datums & hotend top-fin relief"),
        ]
    )
    im_housing.save(OUT / "Housing_preview.png")

    b_parts = [(vb, fb, np.array([239, 148, 46], dtype=float))]
    im_bracket = make_grid(
        [
            render_panel(b_parts, R_iso, title="FRONT ISO | Sensor contact face & 10 mm vertical adjustment slots"),
            render_panel(b_parts, R_rear_iso, title="REAR ISO | Recessed 5.8 mm M3 nut channels (4.7 mm center wall)"),
            render_panel(b_parts, R_front, title="FRONT | 24 x 8.0 mm housing anchors outside 10.5 mm Eddy slots"),
            render_panel(b_parts, R_side, title="SIDE | Flat 4.0 mm plate (prints front-face down, supports OFF)"),
        ]
    )
    im_bracket.save(OUT / "Bracket_preview.png")
    print("Saved Assembly_preview.png, Housing_preview.png, Bracket_preview.png")


if __name__ == "__main__":
    main()
