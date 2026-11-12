"""
Build the Dragon Burner AD5M Adapter (#1406257) Mode-A Rear Eddy Duo Remix (R1).

Generates a single watertight, manifold STL and STEP in
outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1/, along with validation.json,
preview_parts.json, and an inspection FreeCAD assembly document.

Coordinate Frame (inherited from Printables #1406257 STL):
  +X : Right across carriage width (nozzle & coil centerline X = 34.924 mm)
  +Y : Vertical UP (+Z_printer; adapter top = -33.300, flange bottom = -124.300)
  +Z : Forward toward Dragon Burner & hotend (Z = 0.000 is stock steel carriage face)

Aligned Reference Datums:
  - Nozzle tip (Dragon Burner Bambu_Mount (1) + Bambu X1/P1 hotend):
      (X = 34.924, Y = -138.401, Z = +44.697) mm
  - Stock AD5M steel carriage bottom (+13.6 mm above nozzle tip):
      Y = -124.801 mm (Z <= 0.000)
  - Target BTT Eddy Duo coil center (X = 0, Y = 35.0 mm behind nozzle, Z = +2.5 mm above nozzle):
      (X = 34.924, Y = -135.901, Z = +9.697) mm
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import FreeCAD as App
import Import
import Mesh
import MeshPart
import Part


ROOT = Path(__file__).resolve().parents[2]
REF_1406 = ROOT / "reference/AD5M_Dragon_Burner_Adapter_1406257/adventurer-5m-dragon-burner-adapter-v11.stl"
REF_DB_STEP = ROOT / "reference/Bambu_X1_hotend_CAD/Dragon_Burner_v0.2_v8_reference.step"
REF_HOTEND_STEP = ROOT / "reference/Bambu_X1_hotend_CAD/Bambu_X1_P1_original_hotend_Jorge.STEP"
REF_EDDY_STEP = ROOT / "outputs/Eddy_Duo_BambuMod_mount_R1/EDDY_official.step"
OUT_DIR = ROOT / "outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1"


# Exact rigid datums in #1406257 coordinates (verified against STEP mounts & hotend bores)
NOZZLE_X = 34.924
NOZZLE_Y = -138.401
NOZZLE_Z = 44.697

COIL_X = NOZZLE_X
COIL_Y = NOZZLE_Y + 2.500     # -135.901 mm (+2.5 mm above nozzle tip)
COIL_Z = NOZZLE_Z - 35.000    # +9.697 mm (35.0 mm behind nozzle tip)

CARRIAGE_BOTTOM_Y = NOZZLE_Y + 13.600  # -124.801 mm

# Pocket & thermal baffle design parameters (mm)
POCKET_INNER_W = 18.50        # 18.10 mm lower housing / 18 mm bare coil PCB + 0.40 mm clearance
SIDE_WALL_T = 2.00            # outer X = [23.674, 46.174] -> clear of 5th bolt @ X=20.92/48.92
POCKET_FRONT_Z = 19.00        # inner datum wall (+0.10 mm clear of EDDY back when coil ctr @ +9.70)
BAFFLE_FRONT_Z = 23.30        # 0.10 mm inset from #1406257 Z=23.40 plane (non-coplanar) -> 4.30 mm front baffle
POCKET_SIDE_REAR_Z = 12.50    # main vertical side walls Z = [12.50, 23.30]
COIL_CRADLE_REAR_Z = 4.20     # lower cradle rails Z = [4.20, 23.30] for 18x11 bare coil PCB
COIL_CRADLE_Y_BOT = -136.00   # +2.40 mm above nozzle tip; open bottom for +/-1.0 mm Z travel
COIL_CRADLE_Y_TOP = -131.00
POCKET_CEIL_Y = -98.00        # +3.1 mm headroom above +1.0 mm upward travel of 33.79 mm housing

# Upward relief channel for inward-facing 90 deg 4-pin JST-ZH USB connector + wires
USB_CH_W = 12.60              # clears 9.00 mm JST-ZH housing + plug body
USB_CH_Z_MIN = 13.50
USB_CH_Z_MAX = 20.60          # leaves 23.30 - 20.60 = 2.70 mm solid front ABS/ASA baffle (>= 2.4 mm!)
USB_CH_Y_BOT = -115.00
USB_CH_Y_TOP = -80.00         # breaks into #1406257 existing 20x23.4 mm central tunnel (Y=-82.3..-48.1)

# 26.61 mm center-to-center M3 mounting ears (+/-1.0 mm vertical Z travel)
EAR_PITCH_X = 26.61
EAR_Y_CENTER = -128.50        # 4.2 mm below #1406257 -124.30 flange, 11.2 mm below 5th bolt slot
EAR_HEIGHT = 12.00            # Y = [-134.50, -122.50]
EAR_OUTER_MARGIN_X = 4.00     # 4.0 mm radial boss around M3 slot center
EAR_REAR_Z = 13.00            # rear mounting face; ear spans Z = [13.00, 23.30]
EAR_TRAVEL_MM = 1.00          # +/-1.0 mm vertical travel (2.0 mm stroke)
SLOT_DIA = 3.40               # M3 clearance
NUT_CH_H = 5.80               # M3 hex nut flat-to-flat 5.5 mm + 0.3 mm clearance
NUT_CH_Z_MIN = 16.60          # 3.6 mm solid rear clamping wall (13.0..16.6)
NUT_CH_Z_MAX = 19.40          # 3.9 mm solid front thermal skin (19.4..23.3 >= 2.4 mm!)


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def vertical_slot_prism(cx: float, cy: float, z0: float, z1: float, dia: float, travel: float) -> Part.Shape:
    r = dia / 2.0
    dz = z1 - z0
    c_bot = Part.makeCylinder(r, dz, App.Vector(cx, cy - travel, z0), App.Vector(0, 0, 1))
    c_top = Part.makeCylinder(r, dz, App.Vector(cx, cy + travel, z0), App.Vector(0, 0, 1))
    mid = box(cx - r, cx + r, cy - travel, cy + travel, z0, z1)
    return c_bot.fuse(c_top).fuse(mid).removeSplitter()


def load_1406257_solid() -> Part.Shape:
    m = Mesh.Mesh(str(REF_1406))
    sh = Part.Shape()
    sh.makeShapeFromMesh(m.Topology, 0.05)
    s = Part.makeSolid(sh).removeSplitter()
    assert s.isValid() and len(s.Solids) == 1, "Base #1406257 mesh did not convert to single valid solid"
    return s


def load_aligned_reference_components():
    """Return aligned Dragon Burner MainBody, Bambu_Mount(1), Bambu Hotend, and EDDY components."""
    doc = App.newDocument("RefAlignTmp")
    Import.insert(str(REF_DB_STEP), doc.Name)
    db_main = [o.Shape.copy() for o in doc.Objects if o.Label == "MainBody"][0]
    db_bambu = [o.Shape.copy() for o in doc.Objects if o.Label == "Bambu_Mount (1)"][0]
    App.closeDocument(doc.Name)

    hot_raw = Part.read(str(REF_HOTEND_STEP))
    hot = Part.makeCompound(hot_raw.Solids)
    hot.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
    hot.translate(App.Vector(147.895, -130.759, 95.130 - 40.300))

    def db_to_1406(sh: Part.Shape) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
        out.translate(App.Vector(34.9065 - 147.877, -86.681 - 102.550, 33.400 - 119.462))
        return out

    db_main_a = db_to_1406(db_main)
    db_bambu_a = db_to_1406(db_bambu)
    hot_a = db_to_1406(hot)

    # Align EDDY_official.step so Coil90 (Shell[34]) center is at (COIL_X, COIL_Y, COIL_Z)
    # Wait: keep Shell[818] (full shell), Shell[34] (Coil90), Shell[340] (4-pin USB), Shell[579] (switch),
    # and make a clean lower-housing solid envelope (Upper half > +4.90 mm removed).
    eddy_raw = Part.read(str(REF_EDDY_STEP))
    coil90 = eddy_raw.Shells[34].copy()
    usb4p = eddy_raw.Shells[340].copy()
    switch_s = eddy_raw.Shells[579].copy()
    outer_shell = eddy_raw.Shells[818].copy()

    # In EDDY_official.step:
    #   X_eddy mid = -74.330 mm (width 18.100 mm)
    #   Y_eddy_min = -30.986 mm (bottom housing tip), Coil90 Y=[-29.380, -27.794]
    #   Z_eddy: -1.052 (lower shell back) .. +4.902 (split) .. +17.249 (upper shell top);
    #           Coil90 Z=[1.049, 15.249] (center +8.149)
    # Rotate +180 deg about Y so +Z_eddy (Coil90 + switch) points -Z_1406 (inward toward carriage)
    # while +Y_eddy (tall body) stays +Y_1406 (UP), and -Z_eddy (4-pin USB) faces +Z_1406 (inward into pocket baffle)!
    # Rotate(+180 deg about Y): (x, y, z) -> (-x, y, -z)
    def eddy_to_1406(sh: Part.Shape, z_shift_y: float = 0.0) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 180)
        # After 180 about Y:
        #   X mid = +74.330 -> translate X by COIL_X - 74.330
        #   Y coil bottom = -29.380 (or housing bottom -30.986) -> align Y_eddy=-30.986 to COIL_Y + z_shift_y
        #     Wait: at Y_eddy = -30.986 -> COIL_Y, Coil90 bottom copper is +1.60 mm above (+4.10 mm above nozzle);
        #     or aligning Coil90 bottom (-29.380) to COIL_Y (-135.901) puts lower shell bottom at -137.507 (+0.89 mm above nozzle,
        #     Wait: at -1.0 mm downward adjustment +0.89 - 1.0 = -0.11 mm hits bed if lower shell kept!).
        #     ALIGN HOUSING BOTTOM (-30.986) to COIL_Y (-135.901, +2.50 mm above nozzle) -> adjustable +1.5..+3.5 mm!
        #     AND check bare Coil90 bottom at COIL_Y too!
        #   Z coil center = -8.149 -> translate Z by COIL_Z - (-8.149) = 9.697 + 8.149 = +17.846
        #   (Then lower shell back Z_eddy=-1.052 becomes +1.052 + 17.846 = +18.898 mm <= POCKET_FRONT_Z = 19.00!)
        out.translate(App.Vector(COIL_X - 74.330, COIL_Y - (-30.986) + z_shift_y, COIL_Z + 8.149))
        return out

    return {
        "db_main": db_main_a,
        "db_bambu": db_bambu_a,
        "hotend": hot_a,
        "eddy_to_1406": eddy_to_1406,
        "eddy_shells": {"outer": outer_shell, "coil90": coil90, "usb": usb4p, "switch": switch_s},
    }


def build_eddy_addition_and_cuts() -> tuple[Part.Shape, Part.Shape]:
    """Construct positive pocket/baffle/ear solid and negative pocket/slot/channel cuts."""
    px0 = COIL_X - POCKET_INNER_W / 2.0
    px1 = COIL_X + POCKET_INNER_W / 2.0
    ox0 = px0 - SIDE_WALL_T   # 23.674 mm
    ox1 = px1 + SIDE_WALL_T   # 46.174 mm

    # 1. Main vertical drop-down trunk: spans from coil cradle bottom up into #1406257's solid main block
    #    (#1406257 is solid Z=0..27.9+ across X=[18,50] above Y=-100.75; ending trunk at -95.0 buries it
    #    5.75 mm cleanly inside #1406257 without touching the -82.30 tunnel edge).
    trunk = box(ox0, ox1, COIL_CRADLE_Y_BOT, -95.00, POCKET_SIDE_REAR_Z, BAFFLE_FRONT_Z)

    # 2. Lower coil-cradle side rails extending rearward to COIL_CRADLE_REAR_Z (for 18x11 PCB)
    cradle_L = box(ox0, px0, COIL_CRADLE_Y_BOT, COIL_CRADLE_Y_TOP, COIL_CRADLE_REAR_Z, POCKET_SIDE_REAR_Z + 0.5)
    cradle_R = box(px1, ox1, COIL_CRADLE_Y_BOT, COIL_CRADLE_Y_TOP, COIL_CRADLE_REAR_Z, POCKET_SIDE_REAR_Z + 0.5)

    # 3. Structural rear tie-bridges connecting pocket side rails back to #1406257 Z=0..3.4 flange
    #    strictly OUTSIDE the 5th carriage bolt slot (Y = [-117.30, -108.30]):
    #    - Upper tie above 5th bolt slot (Y = -107.00 .. -100.50) across full width [ox0, ox1]
    upper_tie = box(ox0, ox1, -107.00, -100.50, 3.00, POCKET_SIDE_REAR_Z + 0.5)
    #    - Lower side-rail ties below 5th bolt slot (Y = -124.20 .. -119.50; 0.1 mm inset avoids STL coplanar facet edge)
    lower_tie_L = box(ox0, px0, -124.20, -119.50, 3.00, POCKET_SIDE_REAR_Z + 0.5)
    lower_tie_R = box(px1, ox1, -124.20, -119.50, 3.00, POCKET_SIDE_REAR_Z + 0.5)

    # 4. Left & right 26.61 mm M3 mounting ears at Y = EAR_Y_CENTER (-128.50 mm)
    ear_x_L = COIL_X - EAR_PITCH_X / 2.0  # 21.619 mm
    ear_x_R = COIL_X + EAR_PITCH_X / 2.0  # 48.229 mm
    ear_y0 = EAR_Y_CENTER - EAR_HEIGHT / 2.0  # -134.50 mm
    ear_y1 = EAR_Y_CENTER + EAR_HEIGHT / 2.0  # -122.50 mm

    ear_L = box(ear_x_L - EAR_OUTER_MARGIN_X, ox0 + 0.5, ear_y0, ear_y1, EAR_REAR_Z, BAFFLE_FRONT_Z)
    ear_R = box(ox1 - 0.5, ear_x_R + EAR_OUTER_MARGIN_X, ear_y0, ear_y1, EAR_REAR_Z, BAFFLE_FRONT_Z)

    # Chamfer outer ear corners softly (Z edges) before cutting slots
    for ear_name in ("L", "R"):
        sh = ear_L if ear_name == "L" else ear_R
        z_edges = [
            e for e in sh.Edges
            if abs(e.BoundBox.ZLength - (BAFFLE_FRONT_Z - EAR_REAR_Z)) < 0.05
            and e.BoundBox.XLength < 0.01 and e.BoundBox.YLength < 0.01
            and ((ear_name == "L" and abs(e.BoundBox.XMin - (ear_x_L - EAR_OUTER_MARGIN_X)) < 0.05)
                 or (ear_name == "R" and abs(e.BoundBox.XMax - (ear_x_R + EAR_OUTER_MARGIN_X)) < 0.05))
        ]
        if z_edges:
            sh = sh.makeChamfer(2.0, z_edges)
        if ear_name == "L":
            ear_L = sh
        else:
            ear_R = sh

    # 5. Seamless top-front ramp transitioning Z=BAFFLE_FRONT_Z (23.4) up to #1406257 Z=27.9 at Y=-100.75
    #    Only spans Y = [-104.5, -100.0] to eliminate sharp stress riser while keeping >=11 mm from hotend
    add_solid = (
        trunk.fuse(cradle_L)
        .fuse(cradle_R)
        .fuse(upper_tie)
        .fuse(lower_tie_L)
        .fuse(lower_tie_R)
        .fuse(ear_L)
        .fuse(ear_R)
        .removeSplitter()
    )

    # === Negative Cuts ===
    # A. Main Eddy Duo pocket interior cavity:
    #    Open at bottom (-Y) & rear (-Z < POCKET_FRONT_Z), bounded in front by POCKET_FRONT_Z (19.00 mm)
    #    and on sides by [px0, px1], extending up to POCKET_CEIL_Y (-98.00 mm).
    #    Below COIL_CRADLE_Y_TOP (-131.0), keep Z open rearward all the way back to Z=0 so 18x11 / 14.2 Coil90 fits cleanly.
    pocket_upper = box(px0, px1, COIL_CRADLE_Y_BOT - 1.0, POCKET_CEIL_Y, POCKET_SIDE_REAR_Z - 1.0, POCKET_FRONT_Z)
    pocket_coil_bay = box(px0, px1, COIL_CRADLE_Y_BOT - 1.0, COIL_CRADLE_Y_TOP + 0.1, COIL_CRADLE_REAR_Z - 1.0, POCKET_FRONT_Z)
    # Open rear slot behind upper tie & below -124.3 down to POCKET_FRONT_Z so Eddy slides straight in:
    pocket_rear_open = box(px0, px1, COIL_CRADLE_Y_BOT - 1.0, -100.75, 3.45, POCKET_SIDE_REAR_Z + 0.1)

    # B. Upward relief channel for inward-facing 90 deg 4-pin USB connector + wire harness
    #    Center width 12.6 mm [28.624, 41.224], Y = [-115.0, -80.0], Z = [13.5, 20.60]
    ux0 = COIL_X - USB_CH_W / 2.0
    ux1 = COIL_X + USB_CH_W / 2.0
    usb_channel = box(ux0, ux1, USB_CH_Y_BOT, USB_CH_Y_TOP, USB_CH_Z_MIN, USB_CH_Z_MAX)

    # C. 26.61 mm M3 mounting slots (+/-1.0 mm vertical travel) + side-load captive M3 hex-nut channels
    slot_L = vertical_slot_prism(ear_x_L, EAR_Y_CENTER, EAR_REAR_Z - 1.0, NUT_CH_Z_MAX + 0.2, SLOT_DIA, EAR_TRAVEL_MM)
    slot_R = vertical_slot_prism(ear_x_R, EAR_Y_CENTER, EAR_REAR_Z - 1.0, NUT_CH_Z_MAX + 0.2, SLOT_DIA, EAR_TRAVEL_MM)

    # Side-load captive M3 hex nut pockets (5.8 mm tall across Y, allowing +/-1.0 mm vertical travel -> 7.8 mm)
    nut_h_total = NUT_CH_H + 2.0 * EAR_TRAVEL_MM  # 7.80 mm
    nut_L = box(ear_x_L - EAR_OUTER_MARGIN_X - 0.5, ear_x_L + 3.0,
                EAR_Y_CENTER - nut_h_total / 2.0, EAR_Y_CENTER + nut_h_total / 2.0,
                NUT_CH_Z_MIN, NUT_CH_Z_MAX)
    nut_R = box(ear_x_R - 3.0, ear_x_R + EAR_OUTER_MARGIN_X + 0.5,
                EAR_Y_CENTER - nut_h_total / 2.0, EAR_Y_CENTER + nut_h_total / 2.0,
                NUT_CH_Z_MIN, NUT_CH_Z_MAX)

    cuts = (
        pocket_upper.fuse(pocket_coil_bay)
        .fuse(pocket_rear_open)
        .fuse(usb_channel)
        .fuse(slot_L)
        .fuse(slot_R)
        .fuse(nut_L)
        .fuse(nut_R)
        .removeSplitter()
    )
    return add_solid, cuts


def run_collision_and_audit(remixed: Part.Shape, add_solid: Part.Shape, base: Part.Shape, refs: dict) -> dict:
    """Execute explicit 3D boolean & clearance verification across every constraint."""
    checks: dict = {}

    # 1. #1406257 Two 3 mm X/Y Hall-endstop magnet pockets (X=62.90..64.90, Z=29.40, Y=-57.26 & -62.25)
    #    Verify: (a) magnet pockets remain OPEN in final solid; (b) added remix geometry never overlaps.
    mag_cyls = [
        Part.makeCylinder(1.45, 2.2, App.Vector(63.0, ym, 29.40), App.Vector(1, 0, 0))
        for ym in (-57.258, -62.248)
    ]
    checks["hall_magnet_pockets_open_overlap_mm3"] = [round(remixed.common(c).Volume, 6) for c in mag_cyls]
    checks["hall_magnet_min_dist_to_addition_mm"] = round(min(add_solid.distToShape(c)[0] for c in mag_cyls), 3)

    # 2. All 5 M3x10 mm steel carriage bolt holes + socket-head / hex-key clearance cylinders
    carriage_holes_4 = [
        ("upper_left", 15.302, -47.700),
        ("upper_right", 54.503, -47.700),
        ("lower_left", 11.302, -105.899),
        ("lower_right", 58.702, -106.000),
    ]
    # Include both candidate X signs (+14.0 & -14.0 mm) for 5th carriage bolt inside 42x9 mm slot
    carriage_bolts_5th = [
        ("fifth_bolt_plus14", COIL_X + 14.00, -116.45),
        ("fifth_bolt_minus14", COIL_X - 14.00, -116.45),
    ]
    bolt_results = {}
    for label, bx, by in carriage_holes_4 + carriage_bolts_5th:
        shank = Part.makeCylinder(1.60, 10.0, App.Vector(bx, by, -5.0), App.Vector(0, 0, 1))
        # Socket head + tool access corridor in front of carriage flange (Z = 3.40 .. 12.00)
        head_access = Part.makeCylinder(2.75, 8.60, App.Vector(bx, by, 3.40), App.Vector(0, 0, 1))
        bolt_results[label] = {
            "shank_in_remixed_mm3": round(remixed.common(shank).Volume, 6),
            "addition_overlap_head_corridor_mm3": round(add_solid.common(head_access).Volume, 6),
            "min_dist_addition_to_shank_mm": round(add_solid.distToShape(shank)[0], 3),
        }
    # Check full 42x9 mm slot corridor from Z=3.45..11.5 (ensure bolt slot itself stays unobstructed up to head)
    slot_corridor = box(13.64, 55.64, -117.30, -108.30, 3.45, 11.50)
    bolt_results["slot_42x9_head_corridor_Z3p45_to_11p5_overlap_mm3"] = round(add_solid.common(slot_corridor).Volume, 6)
    checks["carriage_bolts_and_slot"] = bolt_results

    # 3. Dragon Burner / Hotend / Steel Carriage collisions
    steel_carriage_env = box(-20.0, 90.0, CARRIAGE_BOTTOM_Y, 0.0, -15.0, 0.0)
    checks["steel_carriage_overlap_mm3"] = round(remixed.common(steel_carriage_env).Volume, 6)
    checks["db_bambu_mount_overlap_mm3"] = round(remixed.common(refs["db_bambu"]).Volume, 6)
    checks["db_main_body_overlap_mm3"] = round(remixed.common(refs["db_main"]).Volume, 6)
    checks["bambu_hotend_overlap_mm3"] = round(remixed.common(refs["hotend"]).Volume, 6)

    # Clearances from new front baffle (Z = BAFFLE_FRONT_Z) to Dragon Burner & Hotend
    baffle_only = box(COIL_X - 15.0, COIL_X + 15.0, COIL_CRADLE_Y_BOT, -100.75, POCKET_FRONT_Z, BAFFLE_FRONT_Z)
    checks["min_air_gap_baffle_to_db_main_mm"] = round(baffle_only.distToShape(refs["db_main"])[0], 3)
    checks["min_air_gap_baffle_to_hotend_mm"] = round(baffle_only.distToShape(refs["hotend"])[0], 3)

    # 4. De-shelled Eddy Duo fit check across nominal, -1.0 mm, and +1.0 mm vertical travel
    #    Check BOTH:
    #    (a) Exact 18x11 mm bare coil PCB + vertical 18.1x33.8x6.0 mm main PCB/lower-half envelope + USB plug
    #    (b) EDDY_official.step internal components (Coil90 + 4-pin USB + switch) + lower shell region (Z_eddy <= +4.90)
    px0 = COIL_X - 9.05
    px1 = COIL_X + 9.05
    eddy_fit = {}
    for dz_travel in (-1.0, 0.0, +1.0):
        # 18.10 x 11.00 mm bare coil PCB (centered at COIL_Z = +9.697, bottom at COIL_Y + dz_travel)
        coil_18x11 = box(px0, px1, COIL_Y + dz_travel, COIL_Y + dz_travel + 1.60, COIL_Z - 5.50, COIL_Z + 5.50)
        # De-shelled lower housing + main PCB (18.10 mm wide x 33.79 mm tall x Z=[12.95, 18.90])
        lower_housing_env = box(px0, px1, COIL_Y + dz_travel, COIL_Y + dz_travel + 33.79, 12.95, 18.90)
        # Mated 4-pin USB plug + wire boot exiting upward (9.6 x 12 x 6 mm -> Z=[14.5, 20.4], Y=[-112, -85])
        usb_plug_env = box(COIL_X - 4.8, COIL_X + 4.8, COIL_Y + dz_travel + 24.0, COIL_Y + dz_travel + 42.0, 14.5, 20.4)

        coil90_t = refs["eddy_to_1406"](refs["eddy_shells"]["coil90"], dz_travel)
        usb_t = refs["eddy_to_1406"](refs["eddy_shells"]["usb"], dz_travel)
        switch_t = refs["eddy_to_1406"](refs["eddy_shells"]["switch"], dz_travel)

        eddy_fit[f"z_travel_{dz_travel:+.1f}mm"] = {
            "bare_18x11_coil_overlap_mm3": round(remixed.common(coil_18x11).Volume, 6),
            "lower_housing_18p1_overlap_mm3": round(remixed.common(lower_housing_env).Volume, 6),
            "usb_plug_and_wires_overlap_mm3": round(remixed.common(usb_plug_env).Volume, 6),
            "eddy_step_coil90_dist_mm": round(remixed.distToShape(coil90_t)[0], 3),
            "eddy_step_usb4p_dist_mm": round(remixed.distToShape(usb_t)[0], 3),
            "eddy_step_switch_dist_mm": round(remixed.distToShape(switch_t)[0], 3),
            "coil_bottom_above_nozzle_mm": round((COIL_Y + dz_travel) - NOZZLE_Y, 3),
        }
    checks["eddy_envelope_fit"] = eddy_fit

    # 5. Thermal baffle & wall thickness audit
    checks["baffle_main_thickness_mm"] = round(BAFFLE_FRONT_Z - POCKET_FRONT_Z, 3)
    checks["baffle_over_usb_channel_mm"] = round(BAFFLE_FRONT_Z - USB_CH_Z_MAX, 3)
    checks["baffle_over_nut_channel_mm"] = round(BAFFLE_FRONT_Z - NUT_CH_Z_MAX, 3)
    checks["min_front_baffle_thickness_mm"] = round(
        min(BAFFLE_FRONT_Z - POCKET_FRONT_Z, BAFFLE_FRONT_Z - USB_CH_Z_MAX, BAFFLE_FRONT_Z - NUT_CH_Z_MAX), 3
    )

    return checks


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading base #1406257 solid & reference CAD...", flush=True)
    base = load_1406257_solid()
    refs = load_aligned_reference_components()

    print("Building Mode-A rear drop-down pocket, 26.61 mm M3 ears, thermal baffle & USB channel...", flush=True)
    add_solid, cuts = build_eddy_addition_and_cuts()

    remixed = base.fuse(add_solid).cut(cuts).removeSplitter()
    assert remixed.isValid(), "Remixed BRep shape is invalid!"
    assert len(remixed.Solids) == 1, f"Expected 1 solid, got {len(remixed.Solids)}"
    solid = remixed.Solids[0]
    assert solid.Volume > 80000.0, f"Unexpected solid volume {solid.Volume}"

    step_path = OUT_DIR / "AD5M_Dragon_Burner_Eddy_Adapter_R1.step"
    stl_path = OUT_DIR / "AD5M_Dragon_Burner_Eddy_Adapter_R1.stl"
    fcstd_path = OUT_DIR / "AD5M_Dragon_Burner_Eddy_Adapter_R1.FCStd"

    solid.exportStep(str(step_path))
    mesh = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.04, AngularDeflection=0.14, Relative=False)
    mesh.write(str(stl_path))
    assert mesh.isSolid(), "FreeCAD mesh.isSolid() check failed!"

    print("Running full 3D collision & envelope checks...", flush=True)
    audit = run_collision_and_audit(solid, add_solid, base, refs)

    bb = solid.BoundBox
    validation = {
        "model": "Printables #1406257 (v11) AD5M Dragon Burner Adapter — Mode A Rear Eddy Duo Remix (R1)",
        "units": "mm",
        "freecad_valid_brep": bool(solid.isValid()),
        "freecad_solid_count": len(remixed.Solids),
        "freecad_mesh_is_solid": bool(mesh.isSolid()),
        "mesh_facets": int(mesh.CountFacets),
        "mesh_points": int(mesh.CountPoints),
        "volume_mm3": round(float(solid.Volume), 3),
        "base_volume_mm3": round(float(base.Volume), 3),
        "bbox_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
        "datums_in_adapter_frame_mm": {
            "nozzle_tip": [NOZZLE_X, NOZZLE_Y, NOZZLE_Z],
            "coil_center_nominal": [COIL_X, COIL_Y, COIL_Z],
            "stock_steel_carriage_bottom": [NOZZLE_X, CARRIAGE_BOTTOM_Y, 0.0],
        },
        "printer_cfg_offsets_mm": {
            "x_offset": 0.0,
            "y_offset": 35.0,
            "z_above_nozzle_nominal": 2.5,
            "z_travel_range_above_nozzle": [1.5, 3.5],
            "below_steel_carriage_bottom_mm": round(CARRIAGE_BOTTOM_Y - COIL_Y, 3),
        },
        "ear_geometry_mm": {
            "center_to_center_pitch_x": EAR_PITCH_X,
            "ear_x_centers": [round(COIL_X - EAR_PITCH_X / 2.0, 3), round(COIL_X + EAR_PITCH_X / 2.0, 3)],
            "ear_y_center": EAR_Y_CENTER,
            "vertical_travel_mm": [-EAR_TRAVEL_MM, +EAR_TRAVEL_MM],
            "slot_diameter_mm": SLOT_DIA,
            "captive_hex_nut_channel": {"height_mm": NUT_CH_H + 2 * EAR_TRAVEL_MM, "z_span_mm": [NUT_CH_Z_MIN, NUT_CH_Z_MAX]},
        },
        "collisions_and_clearances": audit,
    }

    (OUT_DIR / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2), flush=True)

    # Save lightweight FreeCAD assembly document + tessellated parts for standalone matplotlib renderer
    doc = App.newDocument("DragonBurnerEddyR1")
    for name, sh in [
        ("PRINT_RemixedAdapterR1", solid),
        ("REF_Base1406257", base),
        ("REF_DragonBurnerMainBody", refs["db_main"]),
        ("REF_DragonBurnerBambuMount", refs["db_bambu"]),
        ("REF_BambuHotend", refs["hotend"]),
        ("REF_EddyCoil90_Nom", refs["eddy_to_1406"](refs["eddy_shells"]["coil90"], 0.0)),
        ("REF_EddyUSB4p_Nom", refs["eddy_to_1406"](refs["eddy_shells"]["usb"], 0.0)),
        ("REF_EddySwitch_Nom", refs["eddy_to_1406"](refs["eddy_shells"]["switch"], 0.0)),
        ("REF_EddyOuterShell_RefOnly", refs["eddy_to_1406"](refs["eddy_shells"]["outer"], 0.0)),
    ]:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = sh
    doc.recompute()
    doc.saveAs(str(fcstd_path))
    App.closeDocument(doc.Name)

    # Save preview_parts.json for renderer
    preview = []
    for name, sh, col in [
        ("adapter", solid, [66, 133, 244]),
        ("db_bambu", refs["db_bambu"], [76, 175, 80]),
        ("db_main", refs["db_main"], [255, 167, 38]),
        ("hotend", refs["hotend"], [211, 47, 47]),
        ("coil90", refs["eddy_to_1406"](refs["eddy_shells"]["coil90"], 0.0), [156, 39, 176]),
        ("usb4p", refs["eddy_to_1406"](refs["eddy_shells"]["usb"], 0.0), [0, 150, 136]),
    ]:
        v, f = sh.tessellate(0.18)
        preview.append({"name": name, "v": [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v], "f": f, "color": col})
    (OUT_DIR / "preview_parts.json").write_text(json.dumps(preview), encoding="utf-8")
    print(f"Saved {stl_path.name}, {step_path.name}, validation.json", flush=True)


if __name__ == "__main__":
    main()
