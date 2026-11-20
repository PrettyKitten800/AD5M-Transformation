"""Render Primary_R7 views, assembly views, duct cutaways, and R7 verification checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CAD_DIR = Path(__file__).resolve().parent
if str(CAD_DIR) not in sys.path:
    sys.path.insert(0, str(CAD_DIR))

import render_bambumod_orbiter25_R1 as r1  # noqa: E402
import render_bambumod_orbiter25_R2 as r2  # noqa: E402

ROOT = CAD_DIR.parents[1]
OUT_DIR = ROOT / "outputs" / "BambuMod_Orbiter25_Remix_R7"


def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def save_checks_grid(checks: dict[str, list[dict]], out_png: Path, header: str) -> None:
    """Render each R7 verification slice from two complementary viewpoints into a 4x2 grid."""
    specs = [
        (
            "cut_up_holes",
            "UP HOLES: Front-Top Inner Wall (-X Boss)",
            r1.rot_x(60) @ r1.rot_z(155),
        ),
        (
            "cut_up_holes",
            "UP HOLES: Rear-Right Bore View (up_R & up_L)",
            r1.rot_x(60) @ r1.rot_z(25),
        ),
        (
            "cut_ext_holes",
            "EXTRUDER HOLES: Top Plan (2x Dia 3.60 mm)",
            np.eye(3, dtype=float),
        ),
        (
            "cut_ext_holes",
            "EXTRUDER HOLES: Front-Top Tilt (-23.85 Blind / +13.15 Thru)",
            r1.rot_x(30) @ r1.rot_z(180),
        ),
        (
            "cut_top_bed",
            "TOP CORNERS: Rear Bed Face (R3.50 Anti-Warp)",
            np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]], dtype=float),
        ),
        (
            "cut_top_bed",
            "TOP CORNERS: Rear-Top Iso (R3.50->R0.85 Taper + EBB42 Bores)",
            r1.rot_x(52) @ r1.rot_z(32),
        ),
        (
            "cut_rear_hex",
            "REAR HOTEND HEX: Direct Rear View",
            np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]], dtype=float),
        ),
        (
            "cut_rear_hex",
            "REAR HOTEND HEX: Rear-Top Iso",
            r1.rot_x(52) @ r1.rot_z(-28),
        ),
    ]

    panels: list[Image.Image] = []
    for key, title, rot in specs:
        parts = checks[key]
        panels.append(r1.render_panel(parts, rot, title=title))

    pw, ph = panels[0].size
    cols, rows = 2, 4
    header_h = 48
    pad = 8
    canvas = Image.new(
        "RGB",
        (cols * pw + (cols + 1) * pad, header_h + rows * ph + (rows + 1) * pad),
        (244, 246, 248),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), header, fill=(24, 28, 34), font=_load_font(20))

    for idx, panel in enumerate(panels):
        row, col = divmod(idx, cols)
        x = pad + col * (pw + pad)
        y = header_h + pad + row * (ph + pad)
        canvas.paste(panel, (x, y))

    canvas.save(out_png)


def main() -> None:
    primary_data = json.loads((OUT_DIR / "preview_primary_r7.json").read_text(encoding="utf-8"))
    cutaway_data = json.loads((OUT_DIR / "preview_cutaways_r7.json").read_text(encoding="utf-8"))
    checks_data = json.loads((OUT_DIR / "preview_r7_checks.json").read_text(encoding="utf-8"))

    part_views = [
        ("FRONT (+Y -> viewer, +X Fan Left / -X Eddy Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR (-Y carriage face -> viewer, +X Fan Right)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("ISO FRONT-RIGHT (-X Eddy / Orbiter Shelf)", r1.rot_x(66) @ r1.rot_z(138)),
        ("ISO REAR-LEFT (+X 3010 Fan / Motor Cutout)", r1.rot_x(66) @ r1.rot_z(-42)),
    ]
    assy_views = [
        ("FRONT ASSEMBLY (+X Fan Left / -X Eddy Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR ASSEMBLY (Carriage & Hotend Hex Pockets)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("RIGHT SIDE (-X -> viewer: Latch / EBB42 / Fins)", np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], dtype=float)),
        ("LEFT SIDE (+X -> viewer: 3010 Fan & Orbiter Plate)", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
    ]

    r1.save_grid(
        [primary_data[0]],
        OUT_DIR / "Primary_R7_part_views.png",
        "Primary_R7 — Rounded Corners, Reinforced -X Boss, Matched Dia 3.60 mm Extruder Holes",
        part_views,
    )
    r1.save_grid(
        primary_data,
        OUT_DIR / "Primary_R7_assembly_views.png",
        "Primary_R7 Toolhead Assembly Check (Zero Collisions / Short EBB42 Bridge / Orbiter v2.5 / Bambu Hotend)",
        assy_views,
    )
    r2.save_cutaway_grid(
        cutaway_data,
        OUT_DIR / "Primary_R7_duct_cutaways.png",
        "Primary_R7 Internal Air Duct, Fan Scoop & Heatsink Cooling Cutaways",
    )
    save_checks_grid(
        checks_data,
        OUT_DIR / "Primary_R7_r7_checks.png",
        "Primary_R7 Targeted Checks: Reinforced Upper Bosses, Matched Extruder Holes, R3.50 Top Bed Corners, Rear Hex Pockets",
    )
    print("Rendered 4 PNGs in", OUT_DIR)


if __name__ == "__main__":
    main()
