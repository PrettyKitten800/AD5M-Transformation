"""Render verification views + internal duct & rear hex-pocket cutaways for Primary_R6."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_bambumod_orbiter25_R1 import rot_x, rot_z, save_grid  # noqa: E402
from render_bambumod_orbiter25_R2 import save_cutaway_grid  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R6"


def main() -> None:
    data = json.loads((OUT_DIR / "preview_primary_r6.json").read_text(encoding="utf-8"))
    adapter_only = [p for p in data if p["name"] == "adapter"]

    part_views = [
        ("FRONT (+Y -> viewer: Clean Portal & Dia-41mm Circle)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR (-Y carriage face -> viewer: Twin M3 Hex Pockets, 4 Bores & Dia-41mm Circle)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("ISO FRONT-RIGHT (-X Exhaust Grille & Orbiter Shelf)", rot_x(66) @ rot_z(138)),
        ("ISO REAR-LEFT (+X 3010 Fan Arch, Smooth Tunnel & M3 Hex Pockets)", rot_x(66) @ rot_z(-42)),
    ]
    assy_views = [
        ("FRONT ASSEMBLY (+X Fan Left / -X Exhaust Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR ASSEMBLY (Stepper / EBB42 / Hex Pockets & Dia-41mm Circle)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("RIGHT SIDE (-X -> viewer: Hex Vents & Fins)", np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], dtype=float)),
        ("LEFT SIDE (+X -> viewer: Full 3010 Fan Pocket & Orbiter)", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
    ]

    label = "PRIMARY R6 (Rear M3 Hex Pockets | Smooth C2 Duct | +X Nut Boss | Dia-41mm Circle)"
    save_grid(
        adapter_only,
        OUT_DIR / "Primary_R6_part_views.png",
        f"{label} -- PRINTED ADAPTER ONLY",
        part_views,
    )
    save_grid(
        data,
        OUT_DIR / "Primary_R6_assembly_views.png",
        f"{label} -- FULL TOOLHEAD ASSEMBLY CHECK",
        assy_views,
    )

    cuts = json.loads((OUT_DIR / "preview_cutaways_r6.json").read_text(encoding="utf-8"))
    save_cutaway_grid(
        cuts,
        OUT_DIR / "Primary_R6_duct_cutaways.png",
        f"{label} -- SMOOTH AIR TUNNEL & NUT BOSS CUTAWAYS (Y=12.08 / Z=16.5 / Y=23.0)",
    )

    hex_cut_views = [
        ("TOP-DOWN SECTION Z <= 27.22 (Hex Pockets Y=-11.12..-1.631 -> M3 Bores -> Duct Wall)", np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)),
        ("BOTTOM-UP SECTION Z <= 27.22 (Rear Hex Mouth -> Stepped Shoulder -> X1C)", np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=float)),
        ("ISO TOP-REAR SECTION Z <= 27.22 (Captive M3 Nut Seats & Smooth Duct Clearance)", rot_x(58) @ rot_z(-32)),
        ("ISO FRONT SECTION Z <= 27.22 (Heatsink M3 Alignment & Duct Separation)", rot_x(62) @ rot_z(142)),
    ]
    save_grid(
        cuts["cut_z27"],
        OUT_DIR / "Primary_R6_hex_cutaways.png",
        f"{label} -- REAR M3 HEX-NUT POCKETS SECTION (Z <= 27.22)",
        hex_cut_views,
    )


if __name__ == "__main__":
    main()
