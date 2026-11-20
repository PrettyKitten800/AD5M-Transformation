"""Render verification views + internal duct cutaways for BambuMod x Orbiter v2.5 Primary_R4."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_bambumod_orbiter25_R1 import rot_x, rot_z, save_grid  # noqa: E402
from render_bambumod_orbiter25_R2 import save_cutaway_grid  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R4"


def main() -> None:
    data = json.loads((OUT_DIR / "preview_primary_r4.json").read_text(encoding="utf-8"))
    adapter_only = [p for p in data if p["name"] == "adapter"]

    part_views = [
        ("FRONT (+Y -> viewer: Clean Portal & Dia-44mm Circle)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR (-Y carriage face -> viewer: 4 Bores & Dia-44mm Circle)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("ISO FRONT-RIGHT (-X Exhaust Grille & Orbiter Shelf)", rot_x(66) @ rot_z(138)),
        ("ISO REAR-LEFT (+X 3010 Fan Arch & EBB42 Portal)", rot_x(66) @ rot_z(-42)),
    ]
    assy_views = [
        ("FRONT ASSEMBLY (+X Fan Left / -X Exhaust Right)", np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=float)),
        ("REAR ASSEMBLY (Stepper / EBB42 / Dia-44mm Circle)", np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)),
        ("RIGHT SIDE (-X -> viewer: Hex Vents & Fins)", np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], dtype=float)),
        ("LEFT SIDE (+X -> viewer: Full 3010 Fan Pocket & Orbiter)", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
    ]

    label = "PRIMARY R4 (X_mot=0 | X_fil=-6.335 | Dia-44mm Smooth Motor Circle | Clean EBB42 Top Bridge)"
    save_grid(
        adapter_only,
        OUT_DIR / "Primary_R4_part_views.png",
        f"{label} -- PRINTED ADAPTER ONLY",
        part_views,
    )
    save_grid(
        data,
        OUT_DIR / "Primary_R4_assembly_views.png",
        f"{label} -- FULL TOOLHEAD ASSEMBLY CHECK",
        assy_views,
    )

    cuts = json.loads((OUT_DIR / "preview_cutaways_r4.json").read_text(encoding="utf-8"))
    save_cutaway_grid(
        cuts,
        OUT_DIR / "Primary_R4_duct_cutaways.png",
        f"{label} -- INTERNAL COOLING DUCT SECTIONS",
    )


if __name__ == "__main__":
    main()
