"""Build BambuMod x Orbiter v2.5 AD5M Offset-Hotend Adapter — Revision 2 (R2).

Addresses user feedback after R1:
  1. Offset-hotend design ONLY (Primary: centered stepper X_mot = 0.000,
     Z_mot = 51.900; shifted X1C hotend X_fil = -6.335 mm; horizontal Orbiter
     v2.5 mounting plate Z_mount = 32.600 mm).
  2. Proper BambuMod-derived 3010 hotend fan shroud and enclosed convergent
     cooling ducting:
       - Restores the full +X 3010 fan shroud arch up to Z = 37.35 mm with a
         1.10-1.45 mm wall clearing Orbiter's +X hub (0.000 mm^3 overlap) and
         an internal upper baffle deflecting upper blade airflow cleanly down.
       - Replaces R1's coarse Z=23.6..59.8 cavity cut with a smooth 5-section
         Part.makeLoft cooling tunnel converging from the 3010 aperture
         (X=19.50) onto the shifted X1C heatsink fins (X=[-14.19,+1.51],
         Z=[5.7,24.5]) and expanding into Kirill_Wawe's -X hex exhaust vents.
       - Plugs unused stock X=0 floor opening (+X bypass leak) and X=0 hotend
         bosses, seals front walls smoothly up to Z_plate_bot (26.80 mm) on
         both flanks while preserving a compact front X1C M3 screw & wire
         bay strictly above the fin tunnel roof (Z = 24.80..31.10).
  3. Blind rear-entry carriage holes:
       - Caps the front 1.70 mm (Y = -5.58..front_y; -5.20 for (-14.0, 71.5))
         of all 7 rear carriage mounting bores so no carriage attachment holes
         are visible or open from the front (+Y), while keeping full rear (-Y)
         M3 screw / heatset depth.

Coordinate Frame (upright toolhead):
  X = 0    : AD5M carriage centerline (+X = 3010 fan / left, -X = exhaust / Eddy)
  +Y / -Y  : +Y = Front | -Y = Rear (steel carriage at Y = -11.117 mm)
  Z = 0    : BambuMod carriage chin bottom (X1C nozzle tip at Z = -13.580 mm)

Credits & License (preserved):
  - BambuMod adapter base: Kirill_Wawe (Printables #1574762), CC BY-NC-SA 4.0
  - Orbiter v2.5 extruder mockup: dr. Lorincz Robert
  - Derived R2 adapter files share CC BY-NC-SA 4.0.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import Part
from FreeCAD import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_bambumod_orbiter25_R1 import (  # noqa: E402
    box,
    cyl_x,
    cyl_y,
    cyl_z,
    detect_backplate_y_planes,
    load_references,
    orbiter_xform,
    stadium_xz_y,
)

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R2"

X_FIL = -6.335
X_MOT = 0.000
Z_MOUNT = 32.600
Z_MOT = 51.900
MOT_HOLE_R = 19.100

CARRIAGE_HOLES = [
    ("low_R", -19.0, 3.5, -5.58, None),
    ("low_L", 19.0, 3.5, -5.58, None),
    ("mid_R", -21.5, 51.0, -5.58, None),
    ("up_R", -24.0, 61.0, -5.58, -4.45),  # Stops 0.17 mm behind Orbiter corner (-4.276) -> 1.13 mm blind skin
    ("up_L_lo", 24.0, 61.0, -5.58, None),
    ("up_L_hi", 23.7, 66.5, -5.58, None),
    ("top_R_5th", -14.0, 71.5, -5.20, None),
]


def _duct_section_wire(x: float, y_lo: float, y_hi: float, z_lo: float, z_hi: float, ch: float) -> Part.Wire:
    """Create a 6-vertex closed YZ section wire with 45 deg print-safe front chamfers."""
    pts = [
        Vector(x, y_lo, z_lo),
        Vector(x, y_hi - ch, z_lo),
        Vector(x, y_hi, z_lo + ch),
        Vector(x, y_hi, z_hi - ch),
        Vector(x, y_hi - ch, z_hi),
        Vector(x, y_lo, z_hi),
        Vector(x, y_lo, z_lo),
    ]
    return Part.makePolygon(pts)


def build_duct_void() -> Part.Shape:
    """Build smooth ruled cooling plenum from +X 3010 exit across shifted X1C fins to -X grille."""
    # Section specs: (X, y_lo, y_hi, z_lo, z_hi, ch)
    # 3010 fan exit aperture is centered at Y=11.372, Z=22.246, R=14.50 (Y=[-3.13, 25.87], Z=[7.75, 36.75]).
    # Shifted X1C heatsink fins span X=[-14.185, +1.515], Y=[-2.17, 22.83], Z=[5.72, 24.50].
    sections = [
        (19.65, -2.90, 25.60, 7.80, 34.90, 2.60),   # Meets fan opening bevel cleanly
        (18.75, -2.90, 25.60, 7.65, 32.00, 2.50),   # Inside upper fan lip (stays >=1.2 mm below/right of Orb corner)
        (16.90, -2.75, 25.10, 7.50, 29.90, 2.40),   # Smoothly clears below Orbiter mounting hub
        (1.85, -2.50, 24.60, 5.55, 24.85, 1.65),    # Shifted X1C heatsink right entrance (y_hi-ch=22.95 > 22.83)
        (-14.55, -2.50, 24.60, 5.55, 24.85, 1.65),  # Shifted X1C heatsink left exit
        (-27.30, -3.50, 27.10, 7.55, 26.55, 2.00),  # Diffuses directly into Kirill's -X hex grille
    ]
    wires = [_duct_section_wire(*s) for s in sections]
    loft = Part.makeLoft(wires, True, True)
    assert loft.isValid(), "Duct void loft failed OCCT validity!"
    return loft


def detect_front_shroud_y(bm_body: Part.Shape) -> float:
    """Return exact Y coordinate of BambuMod's main front shroud plane (~30.119 mm)."""
    ys = []
    for f in bm_body.Faces:
        bb = f.BoundBox
        if f.Area > 100.0 and abs(bb.YMax - bb.YMin) < 1e-3 and 29.8 < bb.YMax < 30.5:
            ys.append(0.5 * (bb.YMin + bb.YMax))
    assert ys, "Could not locate BambuMod front shroud plane!"
    return max(ys)


def build_primary_r2(refs: dict) -> tuple[Part.Shape, dict]:
    """Build the R2 Primary (offset-hotend) carriage adapter with restored ducting and blind holes."""
    bm_body = refs["bm_body"]
    rear_y, front_y = detect_backplate_y_planes(bm_body)
    shroud_front_y = detect_front_shroud_y(bm_body)

    plate_top = Z_MOUNT - 0.02
    plate_bot = Z_MOUNT - 5.80  # 26.800 mm

    work = bm_body.copy()
    # 0. Heal BambuMod upstream 0.0002 mm micro-slit on -X front corner flush to exact front shroud plane
    work = work.fuse(box(-28.10, -27.15, 27.05, shroud_front_y, 30.80, 31.05))

    # 1. Remove upper interior features above Orbiter plate level ONLY (preserving Z < plate_top duct shell!)
    #    plus Kirill's obsolete centered X=0 hotend mounting pillar and stock upper X=0 motor pockets.
    pre_cuts = [
        # Upper motor bay above Z_mount - 0.02 (do NOT chop Z = 23.6..32.58 like R1 did!)
        box(-27.8, 14.3, front_y - 0.1, 27.8, plate_top, 59.8),
        box(-14.0, 14.3, front_y - 0.1, 27.8, 59.5, 69.5),
        # Open -X wall ONLY above plate top up to Z=59.0 (preserving -X hex grille Z=7.5..26.8 and Z>=59 rail bevel)
        box(-31.5, -26.70, front_y + 0.05, 32.5, plate_top, 59.00),
        box(-31.5, -26.70, -2.0, 32.5, 58.90, 64.00),
        # Trim inner +X fan flange strip interfered with by Orbiter's +X hub (XMax=17.67..18.04),
        # preserving outer fan ring X=[18.42..19.50] up to Z=37.35 and both upper 3010 corner bosses,
        # plus clear Orbiter side protrusion in X=[14.0..18.42], Y=[front_y..2.0], Z>=37.35!
        box(14.0, 18.42, 2.0, 22.0, plate_top, 45.0).cut(
            cyl_x(3.10, 23.37, 34.25, 13.5, 20.0)
        ),
        box(14.0, 18.42, front_y - 0.1, 22.0, 37.35, 45.0),
        # Extra 0.40 mm radial clearance around Orbiter's top motor ear edge above Z=36.3 up to X=18.55
        box(18.35, 18.58, 2.0, 18.5, 36.35, 38.0),
        # Crisp up outer 3010 fan seating pocket (X=[19.42..30.5])
        box(19.42, 30.5, -3.72, 26.46, 7.16, 37.35),
        # Remove Kirill's centered X=0 mounting boss (X=[-6, +7.8]) inside the airflow path
        box(-6.5, 8.6, front_y + 0.1, 13.5, 23.80, 32.55),
    ]
    for c in pre_cuts:
        work = work.cut(c)

    # 2. Rebuild solid lower duct envelope, sealed front shroud & Orbiter mounting plate BEFORE carving duct_void
    # 2a. Seal obsolete X=0 floor cutout & build dense solid floor deck (Z=5.50..7.50) across fan-to-heatsink
    floor_seal = box(-15.5, 19.50, front_y, 24.5, 5.50, 7.50)

    # 2b. Seal upper crescent inside +X 3010 fan aperture (Y=[0.80, 21.94], Z=[32.20, 37.35], X=[18.42, 19.50])
    #     so upper blade edge air is deflected cleanly downward rather than escaping above Orbiter.
    fan_top_plug = box(18.42, 19.50, 0.80, 21.94, 32.20, 37.35).common(
        cyl_x(14.60, 11.372, 22.246, 18.35, 19.55)
    )
    # 2c. Fan transition upper baffle hood bridging smoothly from X=19.50 down under plate_bot (Z=26.80)
    #     without encroaching into Orbiter (kept at X <= 18.08 above Z_plate_bot and X <= 19.50 below it)
    fan_hood_fill = box(1.5, 19.50, front_y, 27.12, 24.50, plate_top)
    fan_hood_wing = box(18.05, 19.50, 0.80, 27.12, 24.50, 37.35).cut(
        box(18.00, 18.45, 0.5, 22.0, plate_top, 38.0)
    ).cut(
        box(18.30, 18.60, 0.5, 18.5, 36.35, 38.0)
    ).common(
        # Trim outer hood silhouette neatly inside Kirill's Y/Z shroud rectangle + 3010 circle
        box(17.90, 19.50, -3.88, 27.12, 24.50, 37.05)
    ).cut(
        # Keep Kirill's upper-front 3010 fan M3 bore (YZ=23.37, 34.25) unobstructed
        cyl_x(1.78, 23.37, 34.25, 17.80, 20.00)
    )

    # 2d. Seal front shroud walls solidly (Y = 24.0..shroud_front_y, Z = 21.8..plate_top) right up into plate bottom
    #     from X=-27.20 to X=+19.50 (strictly leaving X <= -27.20 hex vents clear; X1C window cut cleanly later)
    front_seal = box(-27.20, 19.50, 24.00, shroud_front_y, 21.80, plate_top)
    # Interior fill above fins/exhaust between fins roof Z=24.75 and plate_bot Z=26.80 so exhaust & entry are flush
    ceiling_seal = box(-27.20, 19.50, front_y, 24.50, 24.75, plate_top)

    # 2e. Horizontal Orbiter v2.5 Mounting Plate (Z = [plate_bot, plate_top] = [26.80, 32.58])
    px_min = -28.80
    px_max = 18.10
    plate = box(px_min, px_max, front_y, 27.80, plate_bot, plate_top)
    # Blend front shroud top step smoothly into front edge of mounting plate (Y=27.80 -> shroud_front_y over Z=26.8..29.1)
    plate_front_lip = Part.makePolygon([
        Vector(-27.20, 27.80, plate_bot),
        Vector(-27.20, shroud_front_y, plate_bot),
        Vector(-27.20, 27.80, plate_bot + 2.32),
        Vector(-27.20, 27.80, plate_bot),
    ])
    plate_front_chamfer = Part.Face(plate_front_lip).extrude(Vector(19.50 - (-27.20), 0, 0))
    # Clear left corner fan pocket / front face >= 18.10 at Z > plate_bot cleanly
    plate_front_chamfer = plate_front_chamfer.common(box(-27.20, 18.10, 27.5, 30.2, plate_bot, plate_top))

    # 2f. Solid backplate infill starting at Y=-8.50 (preserving Kirill's 2.6 mm rear belt/weight channels)
    back_fill_lo = box(-27.8, 27.8, -8.50, front_y, 20.6, 48.0)
    back_fill_hi = box(-18.5, 27.8, -8.50, front_y, 47.8, 58.6)
    back_fill_top = box(-12.5, 19.5, -8.50, front_y, 58.4, 64.2)

    # 2g. Blind-hole front caps (Y = cap_y0 .. cap_y1) on ALL 7 rear-entry carriage bores (zero front visibility!)
    blind_caps = []
    for name, cx, cz, cap_y0, cap_y1_ov in CARRIAGE_HOLES:
        cy1 = front_y if cap_y1_ov is None else cap_y1_ov
        cap_r = 2.18 if name == "up_R" else 2.40  # up_R bm_body bore is r=2.150; Orbiter starts at r=2.195 behind -4.45
        blind_caps.append(cyl_y(cap_r, cx, cz, cap_y0, cy1))

    for solid_add in [
        floor_seal,
        fan_top_plug,
        fan_hood_fill,
        fan_hood_wing,
        front_seal,
        ceiling_seal,
        plate,
        plate_front_chamfer,
        back_fill_lo,
        back_fill_hi,
        back_fill_top,
        *blind_caps,
    ]:
        work = work.fuse(solid_add)

    work = work.removeSplitter()
    assert work.isValid(), "Primary_R2 pre-cut BRep invalid!"

    # 3. Carve exact aerodynamic duct loft + shifted X1C heatsink & screw window + motor/Orbiter cutouts
    duct_void = build_duct_void()

    Z_mot_val = Z_MOT
    protect_mid_hi = (
        cyl_y(3.00, -21.5, 51.0, -9.00, front_y + 2.0)
        .fuse(cyl_y(2.50, -14.0, 71.5, -9.00, front_y + 2.0))
        .fuse(cyl_y(2.50, 24.0, 61.0, -9.00, front_y + 2.0))
    )
    protect_up_r_back = cyl_y(2.18, -24.0, 61.0, -9.00, -4.45)
    above_plate_mask = box(-32.0, 32.0, -10.0, front_y + 2.0, plate_top, 80.0)

    final_cuts = [
        duct_void,
        # Shifted Bambu X1C heatsink drop-in opening through Z=5.5..7.5 floor (+0.4 mm slip around fins)
        box(X_FIL - 8.30, X_FIL + 8.30, -2.50, 23.25, 5.20, 7.65),
        # Shifted X1C top aluminum mounting block / heatbreak neck & front M3 wrench bay (Z=24.8..31.10)
        box(X_FIL - 6.60, X_FIL + 6.60, 8.28, 30.50, 24.80, 31.10),
        # Cut open the top chamfers around X1C neck bay on Y=27.8..shroud_front_y so bolts stay unobstructed
        box(X_FIL - 6.60, X_FIL + 6.60, 24.50, 30.50, 24.80, plate_top),
        # Two shifted X1C M3 screw bores at Z = 27.220 (X_fil +- 3.425 = -9.760 and -2.910)
        cyl_y(1.65, X_FIL - 3.425, 27.220, -1.60, 9.00),
        cyl_y(1.65, X_FIL + 3.425, 27.220, -1.60, 9.00),
        # Orbiter v2.5 horizontal filament bore (X_fil = -6.335, Y = 12.08) + bevel chamfer
        cyl_z(2.00, X_FIL, 12.08, plate_bot - 0.50, plate_top + 1.00),
        Part.makeCone(2.60, 1.90, 0.80, Vector(X_FIL, 12.08, 30.50), Vector(0, 0, 1)),
        # Orbiter v2.5 two M3 heatset insert bores (centered (-23.85, 12.08) and (+13.15, 12.08))
        cyl_z(2.20, -23.85, 12.08, plate_top - 4.30, plate_top + 0.50),
        cyl_z(2.20, 13.15, 12.08, plate_top - 4.30, plate_top + 0.50),
        # Central slanted-mounted LDO-36STH20 stepper cutout (X_mot=0, Z_mot=51.90)
        cyl_y(MOT_HOLE_R, X_MOT, Z_mot_val, rear_y - 1.0, front_y + 1.0),
        # Stepped motor flange recesses strictly above plate_top, sparing neighboring blind carriage bosses
        cyl_y(25.40, X_MOT, Z_mot_val, -6.85, -4.45).common(above_plate_mask).cut(protect_mid_hi.fuse(protect_up_r_back)),
        cyl_y(25.60, X_MOT, Z_mot_val, -4.45, front_y + 1.0).common(above_plate_mask).cut(protect_mid_hi),
        # -30 deg / +150 deg slanted stepper mounting ear pockets (Orbiter ears at (+18.97, 40.94) & (-18.97, 62.85))
        stadium_xz_y(
            X_MOT + 17.5 * math.cos(math.radians(-30)),
            Z_mot_val + 17.5 * math.sin(math.radians(-30)),
            X_MOT + 22.0 * math.cos(math.radians(-30)),
            Z_mot_val + 22.0 * math.sin(math.radians(-30)),
            3.20,
            -8.20,
            front_y + 1.0,
        ),
        stadium_xz_y(
            X_MOT - 17.5 * math.cos(math.radians(-30)),
            Z_mot_val - 17.5 * math.sin(math.radians(-30)),
            X_MOT - 22.0 * math.cos(math.radians(-30)),
            Z_mot_val - 22.0 * math.sin(math.radians(-30)),
            3.20,
            -8.20,
            front_y + 1.0,
        ).cut(protect_mid_hi.fuse(protect_up_r_back)),
        # Bottom-right stepper JST connector harness relief (clear of Z_mount plate)
        stadium_xz_y(-11.2, 34.0, -8.8, 37.5, 3.80, rear_y - 1.0, front_y + 1.0),
    ]

    for c in final_cuts:
        work = work.cut(c)

    work = work.removeSplitter()
    assert work.isValid(), "Primary_R2 BRep invalid!"
    assert len(work.Solids) == 1, f"Expected 1 solid, got {len(work.Solids)}"
    solid = work.Solids[0]

    # === Verify Collisions & Blind Carriage Holes ===
    orb_placed = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_body_solids"]]
    orb_bolts = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_bolts"]]
    he_placed = refs["he_raw"].copy()
    he_placed.translate(Vector(X_FIL, 0, 0))
    fan_3010 = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)
    ebb_bkt = refs["ebb_bkt"]
    steel_carriage = box(-40.0, 40.0, -30.0, rear_y - 0.005, -10.0, 90.0)
    belt_low = box(-40.0, 40.0, rear_y - 0.1, -9.12, 9.8, 20.2)
    belt_high = box(-40.0, 40.0, rear_y - 0.1, -9.12, 64.8, 75.2)

    ov_orb = sum(solid.common(o).Volume for o in orb_placed)
    ov_bolts = sum(solid.common(b).Volume for b in orb_bolts)
    ov_he = solid.common(he_placed).Volume
    ov_fan = solid.common(fan_3010).Volume
    ov_fan_orb = sum(fan_3010.common(o).Volume for o in orb_placed)
    ov_ebb = solid.common(ebb_bkt).Volume
    ov_carriage = solid.common(steel_carriage).Volume
    # Belt clearance: verify R2 adds ZERO solid inside empty belt-slot pockets vs upstream bm_body
    bm_solid = bm_body.Solids[0]
    ov_belt_lo = solid.common(belt_low.cut(bm_solid)).Volume
    ov_belt_hi = solid.common(belt_high.cut(bm_solid)).Volume

    # Verify all four 3010 fan mounting holes remain open through X=[15.0..19.5]
    fan_holes_obs = {
        f"fan_yz_{y}_{z}": round(solid.common(cyl_x(1.30, y, z, 15.0, 19.6)).Volume, 4)
        for y, z in [(-0.63, 10.25), (23.37, 10.25), (-0.63, 34.25), (23.37, 34.25)]
    }

    # Verify all 7 carriage holes: blind in Y=[rear_y..cap_y0] AND solid front cap in Y=[cap_y0+0.10..cy1-0.02]
    hole_report = {}
    for name, hx, hz, cap_y0, cap_y1_ov in CARRIAGE_HOLES:
        cy1 = front_y if cap_y1_ov is None else cap_y1_ov
        y_start = -9.90 if name == "top_R_5th" else rear_y + 0.05
        rear_open_cyl = cyl_y(1.80, hx, hz, y_start, cap_y0 - 0.10)
        front_skin_cyl = cyl_y(2.10, hx, hz, cap_y0 + 0.10, cy1 - 0.02)
        rear_solid = solid.common(rear_open_cyl).Volume
        front_solid_frac = solid.common(front_skin_cyl).Volume / front_skin_cyl.Volume
        hole_report[name] = {
            "xz_mm": [hx, hz],
            "blind_depth_from_rear_mm": round(cap_y0 - rear_y, 2),
            "front_skin_thickness_mm": round(cy1 - cap_y0, 2),
            "rear_bore_obstruction_mm3": round(rear_solid, 4),
            "front_skin_solid_fraction": round(front_solid_frac, 4),
            "hidden_from_front": bool(front_solid_frac > 0.99 and rear_solid < 0.01),
        }

    # Check airflow duct cross-section continuity (sample internal void fraction at key X planes)
    duct_clearance_x = {}
    for x0 in [18.5, 14.0, 8.0, 2.5, -18.0, -25.0]:
        probe = box(x0, x0 + 0.5, 5.0, 17.0, 10.0, 22.0)
        duct_clearance_x[f"X_{x0:.1f}"] = round(solid.common(probe).Volume / probe.Volume, 4)

    bb = solid.BoundBox
    report = {
        "variant": "Primary_R2",
        "step_valid": bool(solid.isValid()),
        "step_solids": len(work.Solids),
        "volume_mm3": round(solid.Volume, 2),
        "bbox_upright_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
        "datums_mm": {
            "x_fil": X_FIL,
            "x_mot": X_MOT,
            "z_mount_plate": Z_MOUNT,
            "z_mot_center": Z_MOT,
            "rear_y": round(rear_y, 3),
            "front_y": round(front_y, 3),
        },
        "collisions_mm3": {
            "adapter_vs_orbiter_and_motor": round(ov_orb, 4),
            "adapter_vs_orbiter_m3_bolts": round(ov_bolts, 4),
            "adapter_vs_x1c_hotend": round(ov_he, 4),
            "adapter_vs_3010_fan": round(ov_fan, 4),
            "3010_fan_vs_orbiter": round(ov_fan_orb, 4),
            "adapter_vs_ebb42_bracket": round(ov_ebb, 4),
            "adapter_vs_steel_carriage_plane": round(ov_carriage, 4),
            "adapter_vs_belt_low": round(ov_belt_lo, 4),
            "adapter_vs_belt_high": round(ov_belt_hi, 4),
        },
        "fan_3010_mounting_holes_obstruction_mm3": fan_holes_obs,
        "carriage_holes_blind_verification": hole_report,
        "duct_core_solid_fraction_should_be_zero": duct_clearance_x,
    }

    return solid, {
        "report": report,
        "he_placed": he_placed,
        "orb_placed": Part.makeCompound(orb_placed),
        "fan_3010": fan_3010,
        "ebb_bkt": ebb_bkt,
    }


def export_verified(solid: Part.Shape, ctx: dict) -> dict:
    """Export STEP, verify re-read, export Z=0 flat-back STL, verify FreeCAD + Trimesh manifoldness."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    step_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R2.step"
    stl_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R2.stl"
    fcstd_p = OUT_DIR / "BambuMod_Orbiter25_Assembly_R2.FCStd"

    # Mandatory solid.exportStep + Part.read verify
    solid.exportStep(str(step_p))
    re_read = Part.read(str(step_p))
    assert re_read.isValid() and len(re_read.Solids) == 1, "Re-read STEP invalid!"

    # Rotate -90 deg about +X so rear carriage face (Y=-11.117) rests flat on Z_stl = 0
    stl_shape = solid.copy()
    stl_shape.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    z0 = stl_shape.BoundBox.ZMin
    stl_shape.translate(Vector(0, 0, -z0))

    mesh = MeshPart.meshFromShape(Shape=stl_shape, LinearDeflection=0.05, AngularDeflection=0.25, Relative=False)
    mesh.write(str(stl_p))
    mchk = Mesh.Mesh(str(stl_p))
    assert mchk.isSolid(), "STL is not solid!"
    assert not mchk.hasNonManifolds(), "STL has non-manifold edges!"

    # Overhang check in print orientation (flat back down -> normal.z < -cos(45 deg) and Z > 0.25 mm)
    oh_area = 0.0
    oh_deep = 0.0
    for f in mchk.Facets:
        nz = f.Normal.z
        zc = sum(p[2] for p in f.Points) / 3.0
        if zc > 0.25 and nz < -0.7071:
            oh_area += f.Area
            if nz < -0.94:
                oh_deep += f.Area

    # Save FreeCAD assembly document
    doc = App.newDocument("BambuMod_Orbiter25_R2")
    for obj_name, shp in [
        ("Primary_Adapter_R2", solid),
        ("X1C_Hotend_Ref", ctx["he_placed"]),
        ("Orbiter25_Motor_Ref", ctx["orb_placed"]),
        ("Fan_3010_Envelope", ctx["fan_3010"]),
        ("EBB42_Short_Bridge_R7", ctx["ebb_bkt"]),
    ]:
        o = doc.addObject("Part::Feature", obj_name)
        o.Shape = shp
    doc.recompute()
    doc.saveAs(str(fcstd_p))
    App.closeDocument(doc.Name)

    # Save tessellated preview JSON for render_bambumod_orbiter25_R2.py (including cutaway meshes!)
    def _tess_list(shp: Part.Shape, tol: float = 0.08):
        v, f = shp.tessellate(tol)
        return [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v], [[int(i) for i in tri] for tri in f]

    parts_json = []
    specs = [
        ("adapter", solid, [65, 130, 195]),
        ("x1c", ctx["he_placed"], [215, 95, 70]),
        ("orbiter", ctx["orb_placed"], [72, 76, 84]),
        ("ebb42", ctx["ebb_bkt"], [65, 165, 105]),
        ("fan3010", ctx["fan_3010"], [225, 165, 55]),
    ]
    for pname, shp, col in specs:
        verts, faces = _tess_list(shp)
        parts_json.append({"name": pname, "color": col, "v": verts, "f": faces})

    # Precompute 3 real BRep cutaway views of adapter + shifted heatsink for inspection PNGs
    cut_y11 = solid.common(box(-32.0, 32.0, -12.0, 11.37, -1.0, 82.0))
    cut_he_y11 = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 11.37, -15.0, 82.0))
    cut_z16 = solid.common(box(-32.0, 32.0, -12.0, 32.0, -1.0, 16.50))
    cut_he_z16 = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 32.0, -15.0, 16.50))
    cut_front = solid.common(box(-32.0, 32.0, -12.0, 23.00, -1.0, 38.0))
    cut_he_front = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 23.00, -15.0, 38.0))

    cuts_payload = {}
    for cname, ad_s, he_s in [
        ("cut_y11", cut_y11, cut_he_y11),
        ("cut_z16", cut_z16, cut_he_z16),
        ("cut_y23", cut_front, cut_he_front),
    ]:
        va, fa = _tess_list(ad_s)
        vh, fh = _tess_list(he_s)
        cuts_payload[cname] = [
            {"name": "adapter", "color": [65, 130, 195], "v": va, "f": fa},
            {"name": "x1c", "color": [215, 95, 70], "v": vh, "f": fh},
        ]

    (OUT_DIR / "preview_primary_r2.json").write_text(json.dumps(parts_json), encoding="utf-8")
    (OUT_DIR / "preview_cutaways_r2.json").write_text(json.dumps(cuts_payload), encoding="utf-8")

    rep = ctx["report"]
    mbb = mchk.BoundBox
    rep["stl"] = {
        "file": stl_p.name,
        "facets": int(mchk.CountFacets),
        "is_solid": bool(mchk.isSolid()),
        "has_non_manifolds": bool(mchk.hasNonManifolds()),
        "volume_mm3": round(float(mchk.Volume), 2),
        "bbox_print_bed_mm": {
            "x": [round(mbb.XMin, 3), round(mbb.XMax, 3)],
            "y": [round(mbb.YMin, 3), round(mbb.YMax, 3)],
            "z": [round(mbb.ZMin, 3), round(mbb.ZMax, 3)],
        },
        "overhang_gt45deg_mm2": round(oh_area, 2),
        "flat_bridge_gt70deg_mm2": round(oh_deep, 2),
    }

    (OUT_DIR / "validation.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))
    return rep


def main() -> None:
    print("Loading reference CAD models...", flush=True)
    refs = load_references()
    print("Building Primary_R2 offset-hotend adapter with BambuMod cooling duct & blind carriage holes...", flush=True)
    solid, ctx = build_primary_r2(refs)
    rep = export_verified(solid, ctx)
    cols = rep["collisions_mm3"]
    assert all(v < 1e-3 for v in cols.values()), f"Collision detected: {cols}"
    fan_obs = rep["fan_3010_mounting_holes_obstruction_mm3"]
    assert all(v < 1e-3 for v in fan_obs.values()), f"3010 fan hole blocked: {fan_obs}"
    holes = rep["carriage_holes_blind_verification"]
    assert all(h["hidden_from_front"] for h in holes.values()), f"Hole visibility check failed: {holes}"
    print("R2 BUILD & CAD VALIDATION PASSED CLEANLY.")


if __name__ == "__main__":
    main()
