"""Render verification views + internal duct cutaways for BambuMod x Orbiter v2.5 Primary_R2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_bambumod_orbiter25_R1 import render_panel, rot_x, rot_z, save_grid  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R2"


def save_cutaway_grid(cuts: dict, out_png: Path, header: str) -> None:
    """Render 2x2 internal duct cutaway inspection sheet using shared R1 triangle rasterizer."""
    pw, ph = 720, 620
    specs = [
        (
            cuts["cut_y11"],
            "SECTION Y <= 11.37 (Front -> Fan Centerline): Upper Arch + Sloped Roof + X1C + Exhaust",
            np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float),
        ),
        (
            cuts["cut_z16"],
            "SECTION Z <= 16.50 (Top Look Down): Fan Funnel -> X1C Fins -> -X Hex Exhaust",
            np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float),
        ),
        (
            cuts["cut_y23"],
            "SECTION Y <= 23.00 (Front Cut): Closed Floor + Shifted X1C Slot + Side Walls",
            np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float),
        ),
        (
            cuts["cut_y11"],
            "ISO CUTAWAY (+X Fan Arch -> Shifted Fins -> -X Vents)",
            rot_x(66) @ rot_z(138),
        ),
    ]
    panels = [render_panel(parts, rot, size=(pw, ph), title=title) for parts, title, rot in specs]
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
    data = json.loads((OUT_DIR / "preview_primary_r2.json").read_text(encoding="utf-8"))
    adapter_only = [p for p in data if p["name"] == "adapter"]

    part_views = [
        ("FRONT (+Y -> viewer: Blind Carriage Holes & Sealed Duct)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR (-Y carriage face -> viewer: 7 Rear-Entry M3 Bores)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("ISO FRONT-RIGHT (-X Exhaust Grille & Orbiter Shelf)", rot_x(66) @ rot_z(138)),
        ("ISO REAR-LEFT (+X 3010 Fan Arch & Slanted Motor Cutout)", rot_x(66) @ rot_z(-42)),
    ]
    assy_views = [
        ("FRONT ASSEMBLY (+X Fan Left / -X Exhaust Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR ASSEMBLY (Stepper / EBB42 / Blind Carriage Face)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("RIGHT SIDE (-X -> viewer: Hex Vents & Fins)", np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], dtype=float)),
        ("LEFT SIDE (+X -> viewer: Full 3010 Fan Pocket & Orbiter)", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
    ]

    label = "PRIMARY R2 (X_mot=0 | X_fil=-6.335 | Sealed Convergent 3010 Duct | Blind Rear Holes)"
    save_grid(
        adapter_only,
        OUT_DIR / "Primary_R2_part_views.png",
        f"{label} -- PRINTED ADAPTER ONLY",
        part_views,
    )
    save_grid(
        data,
        OUT_DIR / "Primary_R2_assembly_views.png",
        f"{label} -- FULL TOOLHEAD ASSEMBLY CHECK",
        assy_views,
    )

    cuts = json.loads((OUT_DIR / "preview_cutaways_r2.json").read_text(encoding="utf-8"))
    save_cutaway_grid(
        cuts,
        OUT_DIR / "Primary_R2_duct_cutaways.png",
        f"{label} -- INTERNAL COOLING DUCT SECTIONS",
    )


if __name__ == "__main__":
    main()
