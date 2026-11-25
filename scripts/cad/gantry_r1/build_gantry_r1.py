"""Parametric FreeCAD builder for AD5M 3x MGN12H 300mm Linear-Rail CoreXY Gantry (R1).

Miniature Voron Trident architecture anchored strictly to AD5M_Frame.STEP & AD5M_Enclosure.STEP:
  1. Y_Rail_Spine_L / Y_Rail_Spine_R (300mm MGN12H inward vertical rails on 3x M5 frame bolts)
  2. Rear_Motor_Mount_L / R + Motor_DS_Cap_L / R (48mm NEMA17 double-shear, staggered Z)
  3. Front_BFI_Housing_L / R + Front_BFI_Carrier_L / R (compression idlers, door-accessible bolts)
  4. Support-free Voron Trident split XY Joints + 300mm self-supporting X-rail C-clamps:
       - XY_Joint_R_Upper + XY_Joint_R_Lower + XY_Joint_R_Bottom_Cap (3-piece support-free split)
       - XY_Joint_L_Upper + XY_Joint_L_Lower (2-piece support-free split)
  5. X_Carriage_MGN12_Base_R1 (monolithic MGN12H carriage base w/ integrated 6mm GT2 clamps)

Exports 16 individual validated STEPs + watertight STLs, reference hardware STLs (incl. dowel pins),
full assembly STEP, and validation.json into outputs/AD5M_MGN12_Gantry_R1/.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import FreeCAD as App
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[3]
FRAME_STEP = REPO / "reference" / "AD5M_gantry_research" / "official_frame_model" / "AD5M_Frame.STEP"
ENC_STEP = REPO / "reference" / "AD5M_gantry_research" / "official_frame_model" / "AD5M_Enclosure.STEP"
OUT_DIR = REPO / "outputs" / "AD5M_MGN12_Gantry_R1"
PARTS_DIR = OUT_DIR / "parts"
PRINT_POSE_DIR = OUT_DIR / "parts_print_pose"

PRINT_POSE_ROTS: Dict[str, Tuple[Tuple[float, float, float], float]] = {
    "Y_Rail_Spine_R":          ((0.0, 1.0, 0.0), -90.0),
    "Y_Rail_Spine_L":          ((0.0, 1.0, 0.0), +90.0),
    "Rear_Motor_Mount_R":      ((1.0, 0.0, 0.0), -90.0),
    "Rear_Motor_Mount_L":      ((1.0, 0.0, 0.0), -90.0),
    "Motor_DS_Cap_R":          ((1.0, 0.0, 0.0),   0.0),
    "Motor_DS_Cap_L":          ((1.0, 0.0, 0.0),   0.0),
    "Front_BFI_Housing_R":     ((1.0, 0.0, 0.0), 180.0),
    "Front_BFI_Housing_L":     ((1.0, 0.0, 0.0), 180.0),
    "Front_BFI_Carrier_R":     ((1.0, 0.0, 0.0), -90.0),
    "Front_BFI_Carrier_L":     ((1.0, 0.0, 0.0), -90.0),
    "XY_Joint_R_Upper":        ((1.0, 0.0, 0.0), 180.0),
    "XY_Joint_R_Lower":        ((1.0, 0.0, 0.0), 180.0),
    "XY_Joint_R_Bottom_Cap":   ((1.0, 0.0, 0.0),   0.0),
    "XY_Joint_L_Upper":        ((1.0, 0.0, 0.0), 180.0),
    "XY_Joint_L_Lower":        ((1.0, 0.0, 0.0),   0.0),
    "X_Carriage_MGN12_Base_R1":((1.0, 0.0, 0.0),   0.0),
}

# ==============================================================================
# MASTER DATUM TABLE (Native AD5M_Frame.STEP coordinates, mm)
#   +X = Right, -X = Left, +Y = Rear, -Y = Front, +Z = Up
# ==============================================================================
Z_STEEL_BOT = 405.63
Z_STEEL_TOP = 406.83

# Vertical MGN12H Y-Rails facing inward toward X=0
X_YRAIL_BASE = 171.500             # +/-171.500; rail spans |X|=[163.5..171.5]
X_YCAR_FACE  = 158.500             # +/-158.500 (13.0mm assembly height)
Z_YRAIL_MID  = 391.500             # MGN12 rail Z=[385.5..397.5], block Z=[378.0..405.0]
Y_YRAIL_MIN  = -142.000
Y_YRAIL_MAX  = 158.000
Y_RAIL_LEN   = 300.000

# X_RAIL-above-belts CoreXY Z-stack (both belts below self-supporting 300mm X-rail!)
Z_MOT_FACE_L   = 356.500           # Left Motor B 48mm body Z=[308.50..356.50], shaft [356.50..380.50] (-0.5mm for 16mm tall pulleys)
Z_MOT_FACE_R   = 367.500           # Right Motor A 48mm body Z=[319.50..367.50], shaft [367.50..391.50] (-0.5mm for 16mm tall pulleys)
MOT_BODY_H     = 48.000
MOT_SHAFT_L    = 24.000
Z_MOT_PLATE_THK_L = 4.000          # Left plate Z=[356.50..360.50] (1.00mm below XY_Joint_L_Lower Z>=361.50!)
Z_MOT_PLATE_THK_R = 4.000          # Right plate Z=[367.50..371.50] (0.90mm below XY_Joint_R_Lower Z>=372.40!)
Z_BELT_B       = 370.000           # Lower belt (Left Motor B; bay Z=[364.9..375.1])
Z_BELT_A       = 381.000           # Upper belt (Right Motor A; bay Z=[375.9..386.1])
Z_DS_CAP_BOT_L = 376.000           # Left double-shear F695 cap Z=[376.00..381.50] (bearing [376.5..380.5])
Z_DS_CAP_BOT_R = 386.500           # Right double-shear F695 cap Z=[386.50..392.00] (bearing [387.0..391.0])
DS_CAP_H       = 5.500
DS_CAP_BOLTS   = [(160.5, 166.5), (136.0, 168.0), (107.0, 154.0)]  # +X local coords
Z_XRAIL_MIN    = 388.500           # Self-supporting 300mm X-rail Z=[388.50..400.50]
Z_XRAIL_MAX    = 400.500
Z_XRAIL_MID    = 394.500           # X-MGN12H block Z=[381.00..408.00] inside top opening

# Voron Trident 2-piece horizontal split XY-Joint datums
Z_XY_UPPER_TOP  = 404.000
Z_XY_UPPER_BOT  = 375.520          # 0.04mm clean print seam around Z_SPLIT = 375.500
Z_XY_LOWER_TOP  = 375.480
Z_XY_LOWER_BOT  = 361.500
Z_XY_RCAP_TOP   = 364.980          # Right Bottom Cap [361.500..364.980] <-> R_Lower [365.020..375.480]
Z_XY_RCAP_BOT   = 361.500
Z_XY_RLOW_BOT   = 365.020

X_MOT        = 136.000             # +/-136.000
Y_MOT        = 154.000
R_20T        = 6.366
R_F695       = 7.130

X_Y_MID      = X_MOT + R_20T       # 142.366 (Motor outer == BFI inner)
X_Y_INNER    = X_MOT - R_20T       # 129.634 (Motor inner == XY_2_SM outer)
X_BFI        = X_Y_MID + R_F695    # 149.496 (BFI F695 center == XY_1 center)
X_Y_OUTER    = X_BFI + R_F695      # 156.626 (BFI outer == XY_1 outer)
X_XY2_SM     = X_Y_INNER - R_F695  # 122.504 (XY_2 F695 pass-through center)
X_XY2_20T    = 146.800             # Opposite-belt 20T return idler center (clears Ø18mm FULARR + Ø16mm Gates idlers)

Y_BFI_NOM    = -154.000            # Slider travel [-158.0 .. -150.0]

# Nominal parked gantry pose (Y_yc=+13.0 -> Nozzle Y=-18.5, X=0)
Y_YC_NOM     = 13.000
X_C_NOM      = 0.000

# Print & hardware tolerances
PIN_D_PRESS  = 5.00
PIN_D_CLEAR  = 5.15
F695_BAY_H   = 10.20               # 2x 4.0mm F695 + 2x 1.0mm shim + 0.2mm play
IDLER20T_BAY = 9.60                # 8.5mm 20T toothed idler + 2x 0.5mm shim + play
HS_M3_D      = 4.00               # M3 x 4.6mm OD x 5.7mm heat-set insert bore
SHCS_M3_CLR  = 3.40
SHCS_M4_CLR  = 4.40
SHCS_M5_CLR  = 5.40
SLIDER_CLR   = 0.25


# ==============================================================================
# GEOMETRY HELPERS
# ==============================================================================
def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def chamfered_box_z(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    ch_fl: float = 0.0,
    ch_fr: float = 0.0,
    ch_rr: float = 0.0,
    ch_rl: float = 0.0,
) -> Part.Shape:
    """Extruded Z-prism with clean 45-deg Voron corner chamfers (no OCCT fillet instability)."""
    pts: List[App.Vector] = []
    # Front-Left (x0, y0)
    if ch_fl > 0.0:
        pts.extend([App.Vector(x0 + ch_fl, y0, z0)])
    else:
        pts.append(App.Vector(x0, y0, z0))
    # Front-Right (x1, y0)
    if ch_fr > 0.0:
        pts.extend([App.Vector(x1 - ch_fr, y0, z0), App.Vector(x1, y0 + ch_fr, z0)])
    else:
        pts.append(App.Vector(x1, y0, z0))
    # Rear-Right (x1, y1)
    if ch_rr > 0.0:
        pts.extend([App.Vector(x1, y1 - ch_rr, z0), App.Vector(x1 - ch_rr, y1, z0)])
    else:
        pts.append(App.Vector(x1, y1, z0))
    # Rear-Left (x0, y1)
    if ch_rl > 0.0:
        pts.extend([App.Vector(x0 + ch_rl, y1, z0), App.Vector(x0, y1 - ch_rl, z0)])
    else:
        pts.append(App.Vector(x0, y1, z0))
    if ch_fl > 0.0:
        pts.append(App.Vector(x0, y0 + ch_fl, z0))
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(App.Vector(0, 0, z1 - z0))


def cyl_z(x: float, y: float, r: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeCylinder(r, z1 - z0, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def cyl_x(x0: float, x1: float, y: float, z: float, r: float) -> Part.Shape:
    return Part.makeCylinder(r, x1 - x0, App.Vector(x0, y, z), App.Vector(1, 0, 0))


def cyl_y(x: float, y0: float, y1: float, z: float, r: float) -> Part.Shape:
    return Part.makeCylinder(r, y1 - y0, App.Vector(x, y0, z), App.Vector(0, 1, 0))


def hex_prism_y(cx: float, cz: float, af: float, y0: float, y1: float) -> Part.Shape:
    r = af / math.sqrt(3.0)
    pts = [
        App.Vector(cx + r * math.cos(math.radians(60 * k + 30)), y0, cz + r * math.sin(math.radians(60 * k + 30)))
        for k in range(6)
    ]
    wire = Part.makePolygon(pts + [pts[0]])
    return Part.Face(wire).extrude(App.Vector(0, y1 - y0, 0))


def clean(shape: Part.Shape) -> Part.Shape:
    try:
        return shape.removeSplitter()
    except Exception:
        return shape


def make_nema17_ref(cx: float, cy: float, z_top: float, body_h: float = 48.0) -> Part.Shape:
    hw, ch = 21.15, 4.5
    z0 = z_top - body_h
    pts = [
        App.Vector(cx - hw + ch, cy - hw, z0),
        App.Vector(cx + hw - ch, cy - hw, z0),
        App.Vector(cx + hw, cy - hw + ch, z0),
        App.Vector(cx + hw, cy + hw - ch, z0),
        App.Vector(cx + hw - ch, cy + hw, z0),
        App.Vector(cx - hw + ch, cy + hw, z0),
        App.Vector(cx - hw, cy + hw - ch, z0),
        App.Vector(cx - hw, cy - hw + ch, z0),
    ]
    body = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(App.Vector(0, 0, body_h))
    boss = cyl_z(cx, cy, 11.0, z_top, z_top + 2.0)
    shaft = cyl_z(cx, cy, 2.5, z_top + 2.0, z_top + MOT_SHAFT_L)
    return clean(body.fuse(boss).fuse(shaft))


def make_pulley_20t_ref(cx: float, cy: float, z_belt_mid: float) -> Part.Shape:
    """20T motor drive pulley reference (16mm OD flange x 16mm tall hub-down FULARR profile)."""
    return cyl_z(cx, cy, 8.0, z_belt_mid - 11.0, z_belt_mid + 5.0)


def make_idler_20t_ref(cx: float, cy: float, z_belt_mid: float) -> Part.Shape:
    """20T toothed idler reference (18mm OD flange x 8mm tall FULARR / Voron envelope)."""
    return cyl_z(cx, cy, 9.0, z_belt_mid - 4.0, z_belt_mid + 4.0)


def make_f695_pair_ref(cx: float, cy: float, z_belt_mid: float) -> Part.Shape:
    bot_fl = cyl_z(cx, cy, 7.5, z_belt_mid - 4.0, z_belt_mid - 3.2)
    mid_br = cyl_z(cx, cy, 6.5, z_belt_mid - 3.2, z_belt_mid + 3.2)
    top_fl = cyl_z(cx, cy, 7.5, z_belt_mid + 3.2, z_belt_mid + 4.0)
    return clean(bot_fl.fuse(mid_br).fuse(top_fl))


def make_f695_single_ref(cx: float, cy: float, z_bot: float, flange_top: bool = True) -> Part.Shape:
    """Single F695-2RS bearing (4.0mm tall, Ø13mm body, Ø15x0.8mm flange)."""
    if flange_top:
        body = cyl_z(cx, cy, 6.5, z_bot, z_bot + 3.2)
        fl = cyl_z(cx, cy, 7.5, z_bot + 3.2, z_bot + 4.0)
    else:
        fl = cyl_z(cx, cy, 7.5, z_bot, z_bot + 0.8)
        body = cyl_z(cx, cy, 6.5, z_bot + 0.8, z_bot + 4.0)
    return clean(body.fuse(fl))


# ==============================================================================
# 1. Y-RAIL SPINES (L & R)
# ==============================================================================
def build_y_rail_spine(side: int) -> Part.Shape:
    x_in = 171.50
    x_out = 178.50
    y0, y1 = -137.5, 159.0
    z0, z1 = 381.0, 405.40

    body = box(x_in, x_out, y0, y1, z0, z1)
    # Notch rear PEM boss clearance (frame PEMs at |X|>=176.8, Y=[142.0..152.5], Z=[374..404])
    body = body.cut(box(175.6, x_out + 0.5, 141.5, 152.5, z0 - 0.5, z1 + 0.5))
    # Clear front BFI corner top-flange pocket (Y < -132.0, Z >= 398.5)
    body = body.cut(box(x_in - 0.5, x_out + 0.5, y0 - 0.5, -132.0, 398.5, z1 + 0.5))

    # Side-skirt M5 mount holes at Y = -120.96, +2.04, +125.04, Z = 388.83
    for yh in (-120.96, 2.04, 125.04):
        body = body.cut(cyl_x(x_in - 0.5, x_out + 0.5, yh, 388.83, SHCS_M5_CLR / 2.0))
        body = body.cut(cyl_x(x_in - 0.5, x_in + 3.2, yh, 388.83, 4.80))

    # 11x M3x4.6x5.7 heat-set insert holes for MGN12 rail (skipping k=11 at Y=+145.5 inside frame PEM notch)
    for k in range(11):
        yr = Y_YRAIL_MIN + 12.5 + k * 25.0
        body = body.cut(cyl_x(x_in - 0.5, x_in + 6.2, yr, Z_YRAIL_MID, HS_M3_D / 2.0))

    if side < 0:
        body = body.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
    return clean(body)


# ==============================================================================
# 2. FIXED RIGID REAR 48mm DOUBLE-SHEAR MOTOR MOUNTS & CAPS (L & R)
# ==============================================================================
def build_rear_motor_mount(side: int) -> Part.Shape:
    """Rigid 48mm-ready rear motor bracket with double-shear upper bearing cap seat:
    - Left (side=-1): Z_face=357.0, plate=[357.0..361.0], DS cap seat=[376.0..381.5]
    - Right (side=+1): Z_face=368.0, plate=[368.0..372.0], DS cap seat=[386.5..392.0]
    """
    z_face = Z_MOT_FACE_R if side > 0 else Z_MOT_FACE_L
    plate_thk = Z_MOT_PLATE_THK_R if side > 0 else Z_MOT_PLATE_THK_L
    z_plate_top = z_face + plate_thk
    z_cap_bot = Z_DS_CAP_BOT_R if side > 0 else Z_DS_CAP_BOT_L
    z_cap_top = z_cap_bot + DS_CAP_H

    # 1. Top mounting flange under rear steel deck (Z = 400.5 .. 405.4)
    top_plate = box(101.0, 175.0, 151.0, 175.0, 400.5, 405.4)
    top_inboard_ear = chamfered_box_z(101.0, 113.5, 136.0, 152.0, 400.5, 405.4, ch_fl=2.0, ch_fr=1.5)
    top_plate = top_plate.cut(box(158.0, 178.8, 135.0, 159.5, 377.5, 406.0))
    top_plate = top_plate.cut(box(166.5, 178.0, 166.0, 178.0, 355.0, 406.0))

    # 2. Rear vertical bridge wall behind pulley (Y = [162.8 .. 175.0], X = [101.0 .. 166.5])
    rear_wall = box(101.0, 166.5, 162.8, 175.0, z_face, 401.0)
    rear_wall = rear_wall.cut(box(158.0, 168.0, 162.0, 165.0, 377.5, 406.0))
    rear_wall = rear_wall.cut(box(166.5, 178.0, 166.0, 178.0, 355.0, 406.0))

    # 3. Inboard vertical side gusset (X = [101.0 .. 113.0], Y = [136.0 .. 175.0])
    side_gusset = chamfered_box_z(101.0, 113.0, 136.0, 175.0, z_face, 401.0, ch_fl=2.0)

    # 4. Horizontal NEMA 17 Motor Plate (chamfered front corners matching 48mm motor chamfer)
    motor_plate = chamfered_box_z(
        101.0, 158.0, 132.5, 175.0, z_face, z_plate_top,
        ch_fl=2.5, ch_fr=5.7,
    )

    mount = clean(top_plate.fuse(top_inboard_ear).fuse(rear_wall).fuse(side_gusset).fuse(motor_plate))

    # Carve double-shear cap seating shelf into front of rear_wall & inboard side_gusset (0.20mm fit clearance)
    seat_rear = box(100.5, 166.6, 162.5, 172.2, z_cap_bot - 0.10, z_cap_top + 0.15)
    seat_side = box(100.5, 113.2, 146.0, 172.2, z_cap_bot - 0.10, z_cap_top + 0.15)
    mount = mount.cut(clean(seat_rear.fuse(seat_side)))

    # 3x M3x4.6x5.7 heat-set pockets below cap seat + vertical hex-driver access bores up through top_plate
    for bx, by in DS_CAP_BOLTS:
        mount = mount.cut(cyl_z(bx, by, HS_M3_D / 2.0, z_cap_bot - 6.5, z_cap_bot + 0.2))
        mount = mount.cut(cyl_z(bx, by, 3.0, z_cap_top - 0.2, 406.0))

    # NEMA17 pilot bore (D=22.4mm) + 4x M3 clearance bores + vertical wrench access tunnels
    mount = mount.cut(cyl_z(X_MOT, Y_MOT, 11.2, z_face - 0.5, z_plate_top + 0.5))
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            mx, my = X_MOT + dx, Y_MOT + dy
            mount = mount.cut(cyl_z(mx, my, SHCS_M3_CLR / 2.0, z_face - 0.5, z_plate_top + 0.5))
            mount = mount.cut(cyl_z(mx, my, 3.25, z_plate_top - 0.1, 406.0))

    # Upper top-deck M4 / M5 heat-set pockets for factory rear deck holes
    for hx, hy, hd in [(161.25, 163.64, 5.2), (138.50, 169.64, 6.2), (126.00, 157.54, 5.2), (108.15, 142.64, 6.2)]:
        mount = mount.cut(cyl_z(hx, hy, hd / 2.0, 400.0, 406.0))

    if side < 0:
        mount = mount.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
    return clean(mount)


def build_motor_ds_cap(side: int) -> Part.Shape:
    """Removable 3-bolt double-shear F695-2RS bearing cap with Voron corner chamfers."""
    z0 = Z_DS_CAP_BOT_R if side > 0 else Z_DS_CAP_BOT_L
    z1 = z0 + DS_CAP_H
    z_brg_bot = z0 + 0.50

    boss = cyl_z(X_MOT, Y_MOT, 8.40, z0, z1)
    arm_rear = box(127.6, 144.4, 154.0, 171.9, z0, z1)
    seat_rear = chamfered_box_z(101.2, 166.2, 163.0, 171.9, z0, z1, ch_fr=2.0, ch_rr=2.0)
    seat_side = chamfered_box_z(101.2, 112.8, 146.5, 171.9, z0, z1, ch_fl=2.0, ch_fr=2.0)

    cap = clean(boss.fuse(arm_rear).fuse(seat_rear).fuse(seat_side))
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            cap = cap.cut(cyl_z(X_MOT + dx, Y_MOT + dy, 3.25, z0 - 0.5, z1 + 0.5))

    cap = cap.cut(cyl_z(X_MOT, Y_MOT, 3.75, z0 - 0.5, z_brg_bot + 0.1))
    cap = cap.cut(cyl_z(X_MOT, Y_MOT, 6.525, z_brg_bot - 0.1, z_brg_bot + 3.3))
    cap = cap.cut(cyl_z(X_MOT, Y_MOT, 7.60, z_brg_bot + 3.15, z1 + 0.5))

    for bx, by in DS_CAP_BOLTS:
        cap = cap.cut(cyl_z(bx, by, SHCS_M3_CLR / 2.0, z0 - 0.5, z1 + 0.5))
        cap = cap.cut(cyl_z(bx, by, 2.90, z1 - 1.5, z1 + 0.5))

    if side < 0:
        cap = cap.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
    return clean(cap)


# ==============================================================================
# 3. FRONT BFI COMPRESSION TENSIONERS (Housing + Slider Carrier, L & R)
# ==============================================================================
def build_front_bfi(side: int) -> Tuple[Part.Shape, Part.Shape]:
    z_bmid = Z_BELT_B if side < 0 else Z_BELT_A  # Left=-1 -> 370.0, Right=+1 -> 381.0
    z_h0 = 359.0
    z_h1 = 405.40
    bay_z0 = z_bmid - F695_BAY_H / 2.0
    bay_z1 = z_bmid + F695_BAY_H / 2.0

    # --- A. BFI HOUSING ---
    top_flange = chamfered_box_z(136.0, 174.0, -173.0, -132.2, 399.0, z_h1, ch_rl=2.0)
    top_flange = top_flange.fuse(chamfered_box_z(136.0, 170.8, -173.0, -132.2, 396.5, 399.2, ch_rl=2.0))

    h_main = chamfered_box_z(135.5, 167.5, -173.5, -139.0, z_h0, 397.0, ch_fl=2.0, ch_rl=2.0)
    hsg = clean(top_flange.fuse(h_main))
    hsg = hsg.cut(box(163.0, 178.5, -142.5, -131.0, 384.8, 398.2))
    hsg = hsg.cut(box(166.5, 180.0, -175.0, -166.0, z_h0 - 1.0, z_h1 + 1.0))

    ch_x0 = X_BFI - 9.05
    ch_x1 = X_BFI + 9.05
    ch_z0 = z_bmid - 11.25
    ch_z1 = z_bmid + 11.25
    hsg = hsg.cut(box(ch_x0, ch_x1, -167.0, -138.0, ch_z0, ch_z1))

    for z_t in (z_bmid - 8.0, z_bmid + 8.0):
        hsg = hsg.cut(cyl_y(X_BFI, -174.5, -166.0, z_t, SHCS_M3_CLR / 2.0))
        hsg = hsg.cut(hex_prism_y(X_BFI, z_t, 5.65, -174.0, -170.0))

    for hx, hy in [(147.49, -166.41), (147.49, -134.91), (169.49, -166.41), (169.49, -134.91)]:
        z_bot_hs = 398.6 if (hx > 165.0 and hy > -140.0) else 396.0
        hsg = hsg.cut(cyl_z(hx, hy, 2.60, z_bot_hs, 406.0))

    # --- B. BFI SLIDER CARRIER ---
    cx0 = ch_x0 + SLIDER_CLR
    cx1 = ch_x1 - SLIDER_CLR
    cz0 = ch_z0 + SLIDER_CLR
    cz1 = ch_z1 - SLIDER_CLR
    car = chamfered_box_z(cx0, cx1, -162.5, -143.5, cz0, cz1, ch_fl=1.2, ch_fr=1.2, ch_rr=1.2, ch_rl=1.2)

    car = car.cut(box(cx0 - 0.5, cx1 + 0.5, -161.6, -145.4, bay_z0, bay_z1))
    car = car.cut(box(cx0 - 0.5, X_BFI - 4.8, -145.5, -143.0, bay_z0, bay_z1))
    car = car.cut(box(X_BFI + 4.8, cx1 + 0.5, -145.5, -143.0, bay_z0, bay_z1))

    car = car.cut(cyl_z(X_BFI, Y_BFI_NOM, PIN_D_PRESS / 2.0, cz0 - 0.5, cz1 + 0.5))

    for z_t in (z_bmid - 8.0, z_bmid + 8.0):
        car = car.cut(cyl_y(X_BFI, -163.0, -143.0, z_t, SHCS_M3_CLR / 2.0))
        car = car.cut(cyl_y(X_BFI, -145.5, -143.0, z_t, 3.10))

    if side < 0:
        hsg = hsg.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
        car = car.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
    return clean(hsg), clean(car)


# ==============================================================================
# 4. VORON TRIDENT 2-PIECE SUPPORT-FREE SPLIT XY JOINTS + X-RAIL CLAMPS
# ==============================================================================
def build_xy_joint_split(side: int, y_yc: float = Y_YC_NOM) -> Dict[str, Part.Shape]:
    """Build Voron Trident style 100% support-free split XY Joints in +X coords, then mirror for Left.

    CRITICAL CoreXY asymmetry handled explicitly (not by blind X-mirroring):
      - Right (side=+1, own_is_upper=True): XY_1 & XY_2_SM in Upper Belt A (Z_A=381.0),
        XY_2_20T in Lower Belt B (Z_B=370.0). Exports Upper, Lower, and Bottom_Cap (3 flat parts).
      - Left  (side=-1, own_is_upper=False): XY_1 & XY_2_SM in Lower Belt B (Z_B=370.0),
        XY_2_20T in Upper Belt A (Z_A=381.0). Exports Upper and Lower (2 flat parts).
    """
    own_is_upper = side > 0

    y_x_back  = y_yc - 2.000
    y_x_front = y_x_back - 8.000
    y_clamp   = y_x_back - 6.500        # y_yc - 8.500
    y_pass    = y_clamp + 2.0 * R_20T   # y_yc + 4.232

    y_xy1     = y_clamp - R_F695        # y_yc - 15.630 (X=149.496)
    y_xy2_sm  = y_pass + R_F695         # y_yc + 11.362 (X=122.504)
    y_xy2_20t = y_clamp + R_20T         # y_yc - 2.134  (X=148.000)

    # 3-Bolt vertical Upper <-> Lower split clamp pattern (+X local coords)
    b1 = (149.5, y_yc - 27.0)           # front of XY_1, between X_Y_MID (142.4) & X_Y_OUTER (156.6)
    b2 = (155.2, y_yc + 16.5)           # rear-outboard spine, clear of Y-carriage bolt (y_yc+10) & motor
    b3 = (137.5, y_yc + 14.5)           # rear-inboard, 1.0mm+ wall clear of XY_2_SM (134.5), DS cap & X_Y_MID
    upper_lower_bolts = [b1, b2, b3]

    if own_is_upper:
        # ----------------------------------------------------------------------
        # RIGHT SIDE (+X): XY_1 & XY_2_SM at Z_A=381.0; XY_2_20T at Z_B=370.0
        # ----------------------------------------------------------------------
        # 1) XY_Joint_R_Upper [375.52 .. 404.00] - ALL upper roofs flush at Z=404.00 (0% supports upside-down!)
        u_car = box(153.5, 158.5, y_yc - 22.5, y_yc + 22.5, 377.5, Z_XY_UPPER_TOP)
        u_x_rear = chamfered_box_z(133.5, 155.5, y_x_back, y_x_back + 6.8, 386.10, Z_XY_UPPER_TOP, ch_fl=1.5)
        u_x_end  = chamfered_box_z(150.2, 158.5, y_x_front - 1.0, y_x_back + 6.8, 386.10, Z_XY_UPPER_TOP, ch_fl=1.5)
        u_x_cap  = chamfered_box_z(138.0, 155.5, y_x_front - 0.5, y_x_back + 0.5, Z_XRAIL_MAX + 0.15, Z_XY_UPPER_TOP, ch_fl=1.5)

        # Flush Z=404.00 upper roofs above Belt A bays (Z=[386.10..404.00]) + XY_1 & XY_2_SM
        u_xy1_top = chamfered_box_z(140.0, 158.5, b1[1] - 4.0, y_xy1 + 8.5, 386.10, Z_XY_UPPER_TOP, ch_fl=2.0)
        u_xy2_top = chamfered_box_z(114.8, 155.5, y_xy2_sm - 8.2, y_yc + 17.5, 386.10, Z_XY_UPPER_TOP, ch_fl=2.0, ch_rl=2.0)

        # Split-bolt vertical pillars descending straight down to split plane Z=375.52 (0 overhangs upside-down!)
        # Note: Keep Y_max<=y_yc+17.5 inboard of X=151 so DS_Cap (Y>=145.6 at Y_yc=126) stays completely clear!
        u_b1_col = chamfered_box_z(144.2, 155.8, b1[1] - 4.0, y_xy1 - 8.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP, ch_fl=2.0, ch_fr=2.0)
        u_b1_bos = cyl_z(b1[0], b1[1], 4.0, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_b2_col = box(151.8, 158.5, b2[1] - 4.2, y_yc + 22.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_b3_col = chamfered_box_z(132.5, 140.5, y_yc + 10.0, b3[1] + 4.2, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP, ch_fl=2.0, ch_rl=2.0)
        u_b3_arm = box(132.5, 155.5, y_yc + 12.5, y_yc + 17.5, 386.10, Z_XY_UPPER_TOP)

        # XY_2_20T upper Ø10.0mm pin column extending down to split plane (fits cleanly between Y_clamp & Y_pass!)
        u_20t_col = cyl_z(X_XY2_20T, y_xy2_20t, 5.0, Z_XY_UPPER_BOT, 388.50)

        upper = clean(
            u_car.fuse(u_x_rear).fuse(u_x_end).fuse(u_x_cap)
            .fuse(u_xy1_top).fuse(u_xy2_top)
            .fuse(u_b1_col).fuse(u_b1_bos).fuse(u_b2_col).fuse(u_b3_col).fuse(u_b3_arm)
            .fuse(u_20t_col)
        )
        upper = upper.cut(box(158.50, 165.0, y_yc - 30.0, y_yc + 30.0, 360.0, 406.0))
        # Surgical X-rail C-channel pocket (open front -Y & open down to Belt A bay; top Z=[400.65..404.00] sits flat on bed!)
        upper = upper.cut(box(133.0, 150.2, y_x_front - 0.5, y_x_back + 0.15, 386.00, Z_XRAIL_MAX + 0.15))
        upper = upper.cut(box(110.0, 138.5, y_x_front - 12.0, y_x_back, 360.0, 405.0))
        # Clean tangential Belt A channels (X_Y_MID straight pass-through + XY_1 + XY_2_SM)
        upper = upper.cut(box(X_Y_MID - 1.5, X_Y_MID + 1.5, y_yc - 35.0, y_yc + 25.0, Z_XY_UPPER_BOT - 0.5, 385.50))
        upper = upper.cut(cyl_z(X_BFI, y_xy1, 8.20, Z_XY_UPPER_BOT - 0.5, 386.10))
        upper = upper.cut(box(X_Y_OUTER - 1.6, X_Y_OUTER + 1.6, y_yc - 35.0, y_xy1 + 1.0, Z_XY_UPPER_BOT - 0.5, 385.50))
        upper = upper.cut(box(110.0, X_BFI + 1.0, y_clamp - 2.0, y_clamp + 2.0, Z_XY_UPPER_BOT - 0.5, 385.50))
        upper = upper.cut(box(110.0, 134.5, y_xy2_sm - 8.5, y_yc + 25.0, Z_XY_UPPER_BOT - 0.5, 386.10))
        upper = upper.cut(box(110.0, X_XY2_SM + 8.5, y_pass - 2.0, y_pass + 2.0, Z_XY_UPPER_BOT - 0.5, 385.50))
        # Keep car_plate lower face above split plane; notch around XY_1 outer tangent belt at X=[153.5..158.5]
        upper = upper.cut(box(153.0, 159.0, y_yc - 23.0, y_xy1 + 0.5, 375.50, 386.10))

        # Fasteners in R_Upper: X-rail M3 heat-set, 4x Y-carriage M3 bores, Ø5 pin sockets, 3x M3 heat-sets
        upper = upper.cut(cyl_y(137.5, y_x_back - 0.5, y_x_back + 6.3, Z_XRAIL_MID, HS_M3_D / 2.0))
        for dy in (-10.0, 10.0):
            for dz in (-10.0, 10.0):
                upper = upper.cut(cyl_x(150.0, 159.0, y_yc + dy, Z_YRAIL_MID + dz, SHCS_M3_CLR / 2.0))
                upper = upper.cut(cyl_x(142.0, 155.0, y_yc + dy, Z_YRAIL_MID + dz, 3.15))
        upper = upper.cut(cyl_z(X_BFI, y_xy1, PIN_D_PRESS / 2.0, 385.5, 393.5))
        upper = upper.cut(cyl_z(X_XY2_SM, y_xy2_sm, PIN_D_PRESS / 2.0, 385.5, 393.5))
        upper = upper.cut(cyl_z(X_XY2_20T, y_xy2_20t, PIN_D_PRESS / 2.0, Z_XY_UPPER_BOT - 0.5, 384.0))
        for bx, by in upper_lower_bolts:
            upper = upper.cut(cyl_z(bx, by, HS_M3_D / 2.0, Z_XY_UPPER_BOT - 0.5, Z_XY_UPPER_BOT + 6.5))

        # 2) XY_Joint_R_Lower [365.02 .. 375.48] - prints upside-down flat on Z=375.48!
        #    Split-seam horizontal floor Z=[372.40..375.48] (strictly > Right motor_plate 372.00!)
        l_xy1_flr = chamfered_box_z(139.0, 158.5, b1[1] - 4.0, y_xy1 + 8.5, 372.40, Z_XY_LOWER_TOP, ch_fl=2.0)
        l_b1_bos  = cyl_z(b1[0], b1[1], 4.0, 372.40, Z_XY_LOWER_TOP)
        l_xy2_flr = chamfered_box_z(114.8, 158.5, y_yc + 10.0, y_xy2_sm + 8.2, 372.40, Z_XY_LOWER_TOP, ch_fl=2.0, ch_rl=2.0)
        l_b2_ear  = chamfered_box_z(151.0, 158.5, y_yc + 4.5, y_yc + 20.5, 372.40, Z_XY_LOWER_TOP, ch_rr=1.5)
        l_tie_rib = box(141.0, 158.5, b1[1] - 4.0, y_yc + 20.5, 372.40, Z_XY_LOWER_TOP)

        # Lower Belt B perimeter columns rising straight up in printer Z (375.48 -> 365.02) around XY_2_20T
        c1 = (142.5, y_yc - 13.5)
        c2 = (155.5, y_yc - 13.5)
        c3 = (155.8, y_yc + 5.2)        # clears Right motor_plate (ch_fr=5.7) & 20T bay cleanly!
        l_front_blk = chamfered_box_z(139.0, 158.5, y_yc - 17.0, y_yc - 10.2, Z_XY_RLOW_BOT, Z_XY_LOWER_TOP, ch_fl=2.0)
        l_out_spine = chamfered_box_z(154.6, 158.5, y_yc - 13.5, y_yc + 7.2, Z_XY_RLOW_BOT, Z_XY_LOWER_TOP, ch_rr=2.5)
        l_c3_bos    = cyl_z(c3[0], c3[1], 2.55, Z_XY_RLOW_BOT, Z_XY_LOWER_TOP)

        lower = clean(
            l_xy1_flr.fuse(l_b1_bos).fuse(l_xy2_flr).fuse(l_b2_ear).fuse(l_tie_rib)
            .fuse(l_front_blk).fuse(l_out_spine).fuse(l_c3_bos)
        )
        lower = lower.cut(box(158.50, 165.0, y_yc - 30.0, y_yc + 30.0, 360.0, 380.0))
        lower = lower.cut(cyl_z(X_XY2_20T, y_xy2_20t, 9.30, Z_XY_RLOW_BOT - 0.5, 374.80))
        lower = lower.cut(box(110.0, X_XY2_20T + 1.0, y_clamp - 2.0, y_clamp + 2.0, Z_XY_RLOW_BOT - 0.5, 374.60))
        lower = lower.cut(box(110.0, X_XY2_20T + 1.0, y_pass - 2.0, y_pass + 2.0, Z_XY_RLOW_BOT - 0.5, 374.60))
        lower = lower.cut(box(110.0, 138.5, y_x_front - 12.0, y_x_back, 360.0, 376.0))
        lower = lower.cut(cyl_z(X_BFI, y_xy1, PIN_D_PRESS / 2.0, 372.3, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(cyl_z(X_XY2_SM, y_xy2_sm, PIN_D_PRESS / 2.0, 372.3, Z_XY_LOWER_TOP + 0.5))
        for bx, by in upper_lower_bolts:
            lower = lower.cut(cyl_z(bx, by, SHCS_M3_CLR / 2.0, 372.3, Z_XY_LOWER_TOP + 0.5))
            lower = lower.cut(cyl_z(bx, by, 2.85, 372.3, 373.4))
        for cx_b, cy_b in (c1, c2, c3):
            lower = lower.cut(cyl_z(cx_b, cy_b, HS_M3_D / 2.0, Z_XY_RLOW_BOT - 0.5, Z_XY_RLOW_BOT + 6.5))

        # 3) XY_Joint_R_Bottom_Cap [361.50 .. 364.98] - prints flat on Z=361.50
        rcap_front = chamfered_box_z(139.0, 158.5, y_yc - 17.0, y_yc - 10.2, Z_XY_RCAP_BOT, Z_XY_RCAP_TOP, ch_fl=2.0)
        rcap_mid   = box(142.5, 158.5, y_yc - 13.5, y_yc + 3.0, Z_XY_RCAP_BOT, Z_XY_RCAP_TOP)
        rcap_pin   = cyl_z(X_XY2_20T, y_xy2_20t, 6.2, Z_XY_RCAP_BOT, Z_XY_RCAP_TOP)
        rcap_rear  = chamfered_box_z(154.0, 158.5, y_yc - 13.5, y_yc + 7.2, Z_XY_RCAP_BOT, Z_XY_RCAP_TOP, ch_rr=2.5)
        rcap_c3    = cyl_z(c3[0], c3[1], 2.55, Z_XY_RCAP_BOT, Z_XY_RCAP_TOP)
        rcap = clean(rcap_front.fuse(rcap_mid).fuse(rcap_pin).fuse(rcap_rear).fuse(rcap_c3))
        rcap = rcap.cut(box(158.50, 165.0, y_yc - 30.0, y_yc + 30.0, 360.0, 370.0))
        rcap = rcap.cut(cyl_z(X_XY2_20T, y_xy2_20t, PIN_D_PRESS / 2.0, Z_XY_RCAP_BOT - 0.5, Z_XY_RCAP_TOP + 0.5))
        for cx_b, cy_b in (c1, c2, c3):
            rcap = rcap.cut(cyl_z(cx_b, cy_b, SHCS_M3_CLR / 2.0, Z_XY_RCAP_BOT - 0.5, Z_XY_RCAP_TOP + 0.5))
            rcap = rcap.cut(cyl_z(cx_b, cy_b, 2.85, Z_XY_RCAP_BOT - 0.5, Z_XY_RCAP_BOT + 1.2))

        return {"Upper": upper, "Lower": lower, "Bottom_Cap": rcap}

    else:
        # ----------------------------------------------------------------------
        # LEFT SIDE (-X): Built in +X local coords and mirrored in X at the end!
        # XY_1 & XY_2_SM at Z_B=370.0 (Lower); XY_2_20T at Z_A=381.0 (Upper)
        # ----------------------------------------------------------------------
        # 1) XY_Joint_L_Upper [375.52 .. 404.00] - ALL upper roofs flush at Z=404.00 (0% supports upside-down!)
        u_car = box(153.5, 158.5, y_yc - 22.5, y_yc + 22.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_x_rear = chamfered_box_z(133.5, 155.5, y_x_back, y_x_back + 6.8, 385.80, Z_XY_UPPER_TOP, ch_fl=1.5)
        u_x_end  = chamfered_box_z(150.2, 158.5, y_x_front - 1.0, y_x_back + 6.8, 385.80, Z_XY_UPPER_TOP, ch_fl=1.5)
        u_x_cap  = chamfered_box_z(138.0, 155.5, y_x_front - 0.5, y_x_back + 0.5, Z_XRAIL_MAX + 0.15, Z_XY_UPPER_TOP, ch_fl=1.5)
        u_20t_top = chamfered_box_z(140.0, 155.5, y_xy2_20t - 8.5, y_x_back + 6.8, 385.80, Z_XY_UPPER_TOP, ch_fl=1.5)

        u_xy1_col = cyl_z(X_BFI, y_xy1, 5.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_xy2_col = cyl_z(X_XY2_SM, y_xy2_sm, 5.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_xy1_top = chamfered_box_z(142.0, 158.5, b1[1] - 4.0, y_xy1 + 5.5, 385.80, Z_XY_UPPER_TOP, ch_fl=2.0)
        u_b1_bos  = cyl_z(b1[0], b1[1], 4.0, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_b1_web  = box(144.2, 155.8, b1[1] - 4.0, y_xy1 + 2.0, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_b2_col  = box(151.8, 158.5, b2[1] - 4.2, y_yc + 22.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_xy2_top = chamfered_box_z(116.5, 155.5, y_xy2_sm - 5.5, y_yc + 17.5, 385.80, Z_XY_UPPER_TOP, ch_fl=2.0, ch_rl=2.0)
        u_b3_col  = cyl_z(b3[0], b3[1], 4.2, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)
        u_b3_arm  = box(132.5, 155.5, y_yc + 10.5, y_yc + 17.5, Z_XY_UPPER_BOT, Z_XY_UPPER_TOP)

        upper = clean(
            u_car.fuse(u_x_rear).fuse(u_x_end).fuse(u_x_cap).fuse(u_20t_top)
            .fuse(u_xy1_col).fuse(u_xy2_col).fuse(u_xy1_top)
            .fuse(u_b1_bos).fuse(u_b1_web).fuse(u_b2_col).fuse(u_xy2_top).fuse(u_b3_col).fuse(u_b3_arm)
        )
        upper = upper.cut(box(158.50, 165.0, y_yc - 30.0, y_yc + 30.0, 360.0, 406.0))
        upper = upper.cut(box(133.0, 150.2, y_x_front - 0.5, y_x_back + 0.15, 385.75, Z_XRAIL_MAX + 0.15))
        upper = upper.cut(box(110.0, 138.5, y_x_front - 12.0, y_x_back, 360.0, 405.0))
        upper = upper.cut(cyl_z(X_XY2_20T, y_xy2_20t, 9.30, Z_XY_UPPER_BOT - 0.5, 385.80))
        upper = upper.cut(box(110.0, X_XY2_20T + 1.0, y_clamp - 2.0, y_clamp + 2.0, Z_XY_UPPER_BOT - 0.5, 385.60))
        upper = upper.cut(box(110.0, X_XY2_20T + 1.0, y_pass - 2.0, y_pass + 2.0, Z_XY_UPPER_BOT - 0.5, 385.60))

        upper = upper.cut(cyl_y(137.5, y_x_back - 0.5, y_x_back + 6.3, Z_XRAIL_MID, HS_M3_D / 2.0))
        for dy in (-10.0, 10.0):
            for dz in (-10.0, 10.0):
                upper = upper.cut(cyl_x(150.0, 159.0, y_yc + dy, Z_YRAIL_MID + dz, SHCS_M3_CLR / 2.0))
                upper = upper.cut(cyl_x(142.0, 155.0, y_yc + dy, Z_YRAIL_MID + dz, 3.15))
        upper = upper.cut(cyl_z(X_BFI, y_xy1, PIN_D_PRESS / 2.0, Z_XY_UPPER_BOT - 0.5, 383.5))
        upper = upper.cut(cyl_z(X_XY2_SM, y_xy2_sm, PIN_D_PRESS / 2.0, Z_XY_UPPER_BOT - 0.5, 383.5))
        upper = upper.cut(cyl_z(X_XY2_20T, y_xy2_20t, PIN_D_PRESS / 2.0, 385.2, 393.5))
        for bx, by in upper_lower_bolts:
            upper = upper.cut(cyl_z(bx, by, HS_M3_D / 2.0, Z_XY_UPPER_BOT - 0.5, Z_XY_UPPER_BOT + 6.5))

        # 2) XY_Joint_L_Lower [361.50 .. 375.48] - prints RIGHT-SIDE-UP flat on Z=361.50!
        #    Continuous 3.40mm floor Z=[361.50..364.90] (strictly > Left motor_plate 361.00!)
        l_bot_xy1 = chamfered_box_z(138.8, 158.5, b1[1] - 4.0, y_xy1 + 8.5, Z_XY_LOWER_BOT, 364.90, ch_fl=2.0)
        l_bot_mid = box(142.0, 158.5, y_yc - 15.0, y_yc + 17.5, Z_XY_LOWER_BOT, 364.90)
        l_bot_rear_out = box(151.8, 158.5, y_yc + 15.0, y_yc + 22.5, Z_XY_LOWER_BOT, 364.90)
        l_bot_xy2 = chamfered_box_z(114.8, 155.5, y_yc - 1.0, y_xy2_sm + 8.2, Z_XY_LOWER_BOT, 364.90, ch_fl=2.0, ch_rl=2.0)

        l_spine   = box(154.0, 158.5, y_yc - 15.0, y_yc + 22.5, 364.90, Z_XY_LOWER_TOP)
        l_20t_col = cyl_z(X_XY2_20T, y_xy2_20t, 5.0, 364.90, Z_XY_LOWER_TOP)
        l_b1_bos  = cyl_z(b1[0], b1[1], 4.0, Z_XY_LOWER_BOT, Z_XY_LOWER_TOP)
        l_b1_web  = box(144.2, 155.8, b1[1] - 4.0, y_xy1 - 8.8, Z_XY_LOWER_BOT, Z_XY_LOWER_TOP)
        l_b2_col  = box(151.8, 158.5, b2[1] - 4.2, y_yc + 22.5, Z_XY_LOWER_BOT, Z_XY_LOWER_TOP)
        l_b3_col  = cyl_z(b3[0], b3[1], 4.2, Z_XY_LOWER_BOT, Z_XY_LOWER_TOP)
        l_b3_arm  = box(132.5, 155.5, y_yc + 10.5, y_yc + 17.5, Z_XY_LOWER_BOT, Z_XY_LOWER_TOP)

        lower = clean(
            l_bot_xy1.fuse(l_bot_mid).fuse(l_bot_rear_out).fuse(l_bot_xy2)
            .fuse(l_spine).fuse(l_20t_col)
            .fuse(l_b1_bos).fuse(l_b1_web).fuse(l_b2_col).fuse(l_b3_col).fuse(l_b3_arm)
        )
        lower = lower.cut(box(158.50, 165.0, y_yc - 30.0, y_yc + 30.0, 360.0, 380.0))
        # Clear Belt B straight pass-through at X_Y_MID + XY_1 + XY_2_SM bays & corridors open upward!
        lower = lower.cut(box(X_Y_MID - 1.5, X_Y_MID + 1.5, y_yc - 35.0, y_yc + 25.0, 365.50, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(cyl_z(X_BFI, y_xy1, 8.20, 364.90, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(X_Y_OUTER - 1.6, X_Y_OUTER + 1.6, y_yc - 35.0, y_xy1 + 1.0, 365.50, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(110.0, X_BFI + 1.0, y_clamp - 2.0, y_clamp + 2.0, 365.50, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(110.0, 134.5, y_xy2_sm - 8.5, y_yc + 25.0, 364.90, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(110.0, X_XY2_SM + 8.5, y_pass - 2.0, y_pass + 2.0, 365.50, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(153.5, 159.0, y_yc - 23.0, y_xy1 + 0.5, 364.90, Z_XY_LOWER_TOP + 0.5))
        lower = lower.cut(box(110.0, 138.5, y_x_front - 12.0, y_x_back, 360.0, 376.0))

        lower = lower.cut(cyl_z(X_BFI, y_xy1, PIN_D_PRESS / 2.0, Z_XY_LOWER_BOT - 0.5, 365.5))
        lower = lower.cut(cyl_z(X_XY2_SM, y_xy2_sm, PIN_D_PRESS / 2.0, Z_XY_LOWER_BOT - 0.5, 365.5))
        lower = lower.cut(cyl_z(X_XY2_20T, y_xy2_20t, PIN_D_PRESS / 2.0, Z_XY_LOWER_BOT - 0.5, Z_XY_LOWER_TOP + 0.5))
        for bx, by in upper_lower_bolts:
            lower = lower.cut(cyl_z(bx, by, SHCS_M3_CLR / 2.0, Z_XY_LOWER_BOT - 0.5, Z_XY_LOWER_TOP + 0.5))
            lower = lower.cut(cyl_z(bx, by, 2.85, Z_XY_LOWER_BOT - 0.5, Z_XY_LOWER_BOT + 1.5))

        return {
            "Upper": clean(upper.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))),
            "Lower": clean(lower.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))),
        }


# ==============================================================================
# 5. MONOLITHIC MGN12H X-CARRIAGE BELT-CLAMP BASE (R1)
# ==============================================================================
def build_x_carriage_base(x_c: float = X_C_NOM, y_yc: float = Y_YC_NOM) -> Part.Shape:
    """Monolithic MGN12H carriage base with Voron corner chamfers & integrated 6mm GT2 clamps."""
    y_x_back    = y_yc - 2.000
    y_x_front   = y_x_back - 8.000      # y_yc - 10.0
    y_blk_front = y_x_front - 5.000     # y_yc - 15.0 (MGN12H front face)
    y_clamp     = y_x_back - 6.500      # y_yc - 8.500

    front_plate = box(x_c - 22.0, x_c + 22.0, y_blk_front - 4.0, y_blk_front, 365.5, 408.0)
    lower_neck = box(x_c - 22.0, x_c + 22.0, y_blk_front - 0.5, y_x_front + 1.0, 365.5, 380.4)
    clamp_tower = chamfered_box_z(
        x_c - 22.0, x_c + 22.0, y_x_front + 0.5, y_x_back - 1.5, 365.5, 386.5,
        ch_rl=1.5, ch_rr=1.5,
    )

    car = clean(front_plate.fuse(lower_neck).fuse(clamp_tower))

    for dx in (-10.0, 10.0):
        for dz in (-10.0, 10.0):
            car = car.cut(cyl_y(x_c + dx, y_blk_front - 4.5, y_blk_front + 0.5, Z_XRAIL_MID + dz, SHCS_M3_CLR / 2.0))

    for z_belt in (Z_BELT_A, Z_BELT_B):
        car = car.cut(box(x_c - 22.5, x_c - 5.5, y_clamp - 0.85, y_clamp + 0.85, z_belt - 3.3, z_belt + 3.3))
        car = car.cut(box(x_c + 5.5, x_c + 22.5, y_clamp - 0.85, y_clamp + 0.85, z_belt - 3.3, z_belt + 3.3))
        car = car.cut(cyl_z(x_c - 14.0, y_clamp + 2.0, 1.35, z_belt - 4.3, z_belt + 4.3))
        car = car.cut(cyl_z(x_c + 14.0, y_clamp + 2.0, 1.35, z_belt - 4.3, z_belt + 4.3))

    return clean(car)


# ==============================================================================
# REFERENCE HARDWARE SOLIDS
# ==============================================================================
def make_mgn12_rail(x0, x1, y0, y1, z0, z1) -> Part.Shape:
    return box(x0, x1, y0, y1, z0, z1)


def make_mgn12h_block(cx, cy, cz, orient: str) -> Part.Shape:
    if orient == "Y_INWARD_R":
        return box(158.5, 171.5, cy - 22.7, cy + 22.7, cz - 13.5, cz + 13.5)
    elif orient == "Y_INWARD_L":
        return box(-171.5, -158.5, cy - 22.7, cy + 22.7, cz - 13.5, cz + 13.5)
    elif orient == "X_FRONT":
        return box(cx - 22.7, cx + 22.7, cy - 15.0, cy - 10.0, cz - 13.5, cz + 13.5)
    raise ValueError(orient)


def make_dowel_pins_ref(y_yc: float) -> Part.Shape:
    """8x Ø5.0mm hardened steel dowel pins (2x BFI + 6x XY-joints)."""
    yc = y_yc - 8.500
    yp = yc + 2.0 * R_20T
    pins = [
        cyl_z(+X_BFI, Y_BFI_NOM, 2.5, Z_BELT_A - 10.0, Z_BELT_A + 10.0),
        cyl_z(-X_BFI, Y_BFI_NOM, 2.5, Z_BELT_B - 10.0, Z_BELT_B + 10.0),
        # Right XY-joint pins
        cyl_z(+X_BFI, yc - R_F695, 2.5, 372.5, 390.5),
        cyl_z(+X_XY2_SM, yp + R_F695, 2.5, 372.5, 390.5),
        cyl_z(+X_XY2_20T, yc + R_20T, 2.5, 362.0, 383.5),
        # Left XY-joint pins
        cyl_z(-X_BFI, yc - R_F695, 2.5, 362.0, 383.0),
        cyl_z(-X_XY2_SM, yp + R_F695, 2.5, 362.0, 383.0),
        cyl_z(-X_XY2_20T, yc + R_20T, 2.5, 362.0, 390.5),
    ]
    return Part.makeCompound(pins)


def make_belt_ribbon(pts: List[Tuple[float, float]], z_mid: float, width: float = 1.38, height: float = 6.0) -> Part.Shape:
    segs = []
    hw = width / 2.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 0.01:
            continue
        nx, ny = -dy / L * hw, dx / L * hw
        poly = [
            App.Vector(x0 + nx, y0 + ny, z_mid - height / 2.0),
            App.Vector(x1 + nx, y1 + ny, z_mid - height / 2.0),
            App.Vector(x1 - nx, y1 - ny, z_mid - height / 2.0),
            App.Vector(x0 - nx, y0 - ny, z_mid - height / 2.0),
        ]
        segs.append(Part.Face(Part.makePolygon(poly + [poly[0]])).extrude(App.Vector(0, 0, height)))
    return Part.makeCompound(segs)


def make_belts_ref(y_yc: float) -> Tuple[Part.Shape, Part.Shape]:
    y_clamp_n = y_yc - 8.500
    y_pass_n  = y_clamp_n + 2.0 * R_20T
    belt_a = make_belt_ribbon([
        (X_C_NOM + 6.0, y_clamp_n),
        (+X_BFI, y_clamp_n),
        (+X_Y_OUTER, y_clamp_n - R_F695),
        (+X_Y_OUTER, Y_BFI_NOM),
        (+X_Y_MID, Y_BFI_NOM),
        (+X_Y_MID, Y_MOT),
        (+X_Y_INNER, Y_MOT),
        (+X_Y_INNER, y_pass_n + R_F695),
        (+X_XY2_SM, y_pass_n),
        (-X_XY2_20T, y_pass_n),
        (-X_XY2_20T - 6.366, y_clamp_n + R_20T),
        (-X_XY2_20T, y_clamp_n),
        (X_C_NOM - 6.0, y_clamp_n),
    ], Z_BELT_A)
    belt_b = make_belt_ribbon([
        (X_C_NOM - 6.0, y_clamp_n),
        (-X_BFI, y_clamp_n),
        (-X_Y_OUTER, y_clamp_n - R_F695),
        (-X_Y_OUTER, Y_BFI_NOM),
        (-X_Y_MID, Y_BFI_NOM),
        (-X_Y_MID, Y_MOT),
        (-X_Y_INNER, Y_MOT),
        (-X_Y_INNER, y_pass_n + R_F695),
        (-X_XY2_SM, y_pass_n),
        (+X_XY2_20T, y_pass_n),
        (+X_XY2_20T + 6.366, y_clamp_n + R_20T),
        (+X_XY2_20T, y_clamp_n),
        (X_C_NOM + 6.0, y_clamp_n),
    ], Z_BELT_B)
    return belt_a, belt_b


# ==============================================================================
# BUILD, CHECK & EXPORT
# ==============================================================================
def validate_and_export(name: str, shape: Part.Shape) -> Dict:
    step_p = PARTS_DIR / f"{name}.step"
    stl_p  = PARTS_DIR / f"{name}.stl"
    pp_stl_p = PRINT_POSE_DIR / f"{name}_PrintPose.stl"
    shape.exportStep(str(step_p))

    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.15, Relative=False)
    mesh.write(str(stl_p))

    # Pre-oriented flat-bed Z=0 Print-Pose STL centered at X=0, Y=0, Z_min=0
    axis, ang = PRINT_POSE_ROTS[name]
    pp = shape.copy()
    if abs(ang) > 1e-6:
        bb0 = pp.BoundBox
        c0 = App.Vector((bb0.XMin + bb0.XMax) * 0.5, (bb0.YMin + bb0.YMax) * 0.5, (bb0.ZMin + bb0.ZMax) * 0.5)
        pp.rotate(c0, App.Vector(*axis), ang)
    bb_p = pp.BoundBox
    pp.translate(App.Vector(-(bb_p.XMin + bb_p.XMax) * 0.5, -(bb_p.YMin + bb_p.YMax) * 0.5, -bb_p.ZMin))
    pp_mesh = MeshPart.meshFromShape(Shape=pp, LinearDeflection=0.05, AngularDeflection=0.15, Relative=False)
    pp_mesh.write(str(pp_stl_p))

    solids = len(shape.Solids)
    valid = shape.isValid()
    vol = round(shape.Volume, 2)
    bb = shape.BoundBox
    return {
        "name": name,
        "solids": solids,
        "valid": bool(valid),
        "volume_mm3": vol,
        "facets": int(mesh.CountFacets),
        "bbox": {
            "x": [round(bb.XMin, 2), round(bb.XMax, 2)],
            "y": [round(bb.YMin, 2), round(bb.YMax, 2)],
            "z": [round(bb.ZMin, 2), round(bb.ZMax, 2)],
        },
        "step": str(step_p.relative_to(REPO)),
        "stl": str(stl_p.relative_to(REPO)),
        "print_pose_stl": str(pp_stl_p.relative_to(REPO)),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    PRINT_POSE_DIR.mkdir(parents=True, exist_ok=True)

    # Remove superseded monolithic XY_Joint_L/R files if present
    for stale in ("XY_Joint_R.stl", "XY_Joint_R.step", "XY_Joint_L.stl", "XY_Joint_L.step"):
        sp = PARTS_DIR / stale
        if sp.exists():
            sp.unlink()

    print("Loading AD5M_Frame.STEP and AD5M_Enclosure.STEP...")
    frame = Part.read(str(FRAME_STEP))
    enc = Part.read(str(ENC_STEP))

    print("Building parametric printed parts (Voron Trident split XY joints)...")
    spine_r = build_y_rail_spine(+1)
    spine_l = build_y_rail_spine(-1)
    mot_r   = build_rear_motor_mount(+1)
    mot_l   = build_rear_motor_mount(-1)
    cap_r   = build_motor_ds_cap(+1)
    cap_l   = build_motor_ds_cap(-1)
    bfi_h_r, bfi_c_r = build_front_bfi(+1)
    bfi_h_l, bfi_c_l = build_front_bfi(-1)
    xy_r_parts = build_xy_joint_split(+1, Y_YC_NOM)
    xy_l_parts = build_xy_joint_split(-1, Y_YC_NOM)
    x_car   = build_x_carriage_base(X_C_NOM, Y_YC_NOM)

    printed_parts = {
        "Y_Rail_Spine_R": spine_r,
        "Y_Rail_Spine_L": spine_l,
        "Rear_Motor_Mount_R": mot_r,
        "Rear_Motor_Mount_L": mot_l,
        "Motor_DS_Cap_R": cap_r,
        "Motor_DS_Cap_L": cap_l,
        "Front_BFI_Housing_R": bfi_h_r,
        "Front_BFI_Carrier_R": bfi_c_r,
        "Front_BFI_Housing_L": bfi_h_l,
        "Front_BFI_Carrier_L": bfi_c_l,
        "XY_Joint_R_Upper": xy_r_parts["Upper"],
        "XY_Joint_R_Lower": xy_r_parts["Lower"],
        "XY_Joint_R_Bottom_Cap": xy_r_parts["Bottom_Cap"],
        "XY_Joint_L_Upper": xy_l_parts["Upper"],
        "XY_Joint_L_Lower": xy_l_parts["Lower"],
        "X_Carriage_MGN12_Base_R1": x_car,
    }

    part_reports = []
    for name, shp in printed_parts.items():
        rep = validate_and_export(name, shp)
        part_reports.append(rep)
        print(f"  {name:26s}: solids={rep['solids']} valid={rep['valid']} vol={rep['volume_mm3']:8.1f}mm3 tris={rep['facets']}")
        if rep["solids"] != 1 or not rep["valid"]:
            raise RuntimeError(f"Invalid BREP for {name}: {rep}")

    # Nominal hardware references
    y_rail_r = make_mgn12_rail(163.5, 171.5, Y_YRAIL_MIN, Y_YRAIL_MAX, Z_YRAIL_MID - 6.0, Z_YRAIL_MID + 6.0)
    y_rail_l = make_mgn12_rail(-171.5, -163.5, Y_YRAIL_MIN, Y_YRAIL_MAX, Z_YRAIL_MID - 6.0, Z_YRAIL_MID + 6.0)
    y_blk_r  = make_mgn12h_block(0, Y_YC_NOM, Z_YRAIL_MID, "Y_INWARD_R")
    y_blk_l  = make_mgn12h_block(0, Y_YC_NOM, Z_YRAIL_MID, "Y_INWARD_L")
    x_rail   = make_mgn12_rail(-150.0, 150.0, Y_YC_NOM - 10.0, Y_YC_NOM - 2.0, Z_XRAIL_MIN, Z_XRAIL_MAX)
    x_blk    = make_mgn12h_block(X_C_NOM, Y_YC_NOM, Z_XRAIL_MID, "X_FRONT")

    mot_body_r = make_nema17_ref(+X_MOT, Y_MOT, Z_MOT_FACE_R)
    mot_body_l = make_nema17_ref(-X_MOT, Y_MOT, Z_MOT_FACE_L)
    pulley_r   = make_pulley_20t_ref(+X_MOT, Y_MOT, Z_BELT_A)
    pulley_l   = make_pulley_20t_ref(-X_MOT, Y_MOT, Z_BELT_B)
    ds_brg_r   = make_f695_single_ref(+X_MOT, Y_MOT, Z_DS_CAP_BOT_R + 0.50, flange_top=True)
    ds_brg_l   = make_f695_single_ref(-X_MOT, Y_MOT, Z_DS_CAP_BOT_L + 0.50, flange_top=True)

    bfi_brg_r  = make_f695_pair_ref(+X_BFI, Y_BFI_NOM, Z_BELT_A)
    bfi_brg_l  = make_f695_pair_ref(-X_BFI, Y_BFI_NOM, Z_BELT_B)

    y_clamp_n = Y_YC_NOM - 8.500
    y_pass_n  = y_clamp_n + 2.0 * R_20T
    xy1_brg_r = make_f695_pair_ref(+X_BFI, y_clamp_n - R_F695, Z_BELT_A)
    xy2_brg_r = make_f695_pair_ref(+X_XY2_SM, y_pass_n + R_F695, Z_BELT_A)
    xy2_20t_r = make_idler_20t_ref(+X_XY2_20T, y_clamp_n + R_20T, Z_BELT_B)

    xy1_brg_l = make_f695_pair_ref(-X_BFI, y_clamp_n - R_F695, Z_BELT_B)
    xy2_brg_l = make_f695_pair_ref(-X_XY2_SM, y_pass_n + R_F695, Z_BELT_B)
    xy2_20t_l = make_idler_20t_ref(-X_XY2_20T, y_clamp_n + R_20T, Z_BELT_A)

    dowel_pins = make_dowel_pins_ref(Y_YC_NOM)
    belt_a, belt_b = make_belts_ref(Y_YC_NOM)

    ref_groups = {
        "Ref_Rails_Blocks": Part.makeCompound([y_rail_r, y_rail_l, y_blk_r, y_blk_l, x_rail, x_blk]),
        "Ref_Motors_48mm": Part.makeCompound([mot_body_r, mot_body_l]),
        "Ref_Pulleys_Bearings": Part.makeCompound([
            pulley_r, pulley_l, ds_brg_r, ds_brg_l, bfi_brg_r, bfi_brg_l,
            xy1_brg_r, xy2_brg_r, xy2_20t_r, xy1_brg_l, xy2_brg_l, xy2_20t_l,
        ]),
        "Ref_Dowel_Pins": dowel_pins,
        "Ref_Belt_A": belt_a,
        "Ref_Belt_B": belt_b,
        "Ref_AD5M_Frame": Part.makeCompound(frame.Solids),
    }
    for rname, rshp in ref_groups.items():
        MeshPart.meshFromShape(Shape=rshp, LinearDeflection=0.15, AngularDeflection=0.25, Relative=False).write(
            str(PARTS_DIR / f"{rname}.stl")
        )

    hw_refs = Part.makeCompound([
        ref_groups["Ref_Rails_Blocks"],
        ref_groups["Ref_Motors_48mm"],
        ref_groups["Ref_Pulleys_Bearings"],
        dowel_pins,
        belt_a,
        belt_b,
    ])
    hw_refs.exportStep(str(OUT_DIR / "Gantry_Hardware_Refs.step"))
    asm = Part.makeCompound(list(printed_parts.values()) + [hw_refs])
    asm.exportStep(str(OUT_DIR / "AD5M_MGN12_Gantry_R1_Assembly.step"))

    # ==========================================================================
    # COMPREHENSIVE INTERFERENCE MATRIX (STATIC, SELF-BELT/BEARING, SPLIT-MATE, 4-CORNER SWEEP)
    # ==========================================================================
    print("\nRunning comprehensive static, belt/bearing self-clearance & 4-corner dynamic sweep checks...")
    static_grp = {
        "Y_Rail_Spine_R": spine_r,
        "Y_Rail_Spine_L": spine_l,
        "Rear_Motor_Mount_R": mot_r,
        "Rear_Motor_Mount_L": mot_l,
        "Motor_DS_Cap_R": cap_r,
        "Motor_DS_Cap_L": cap_l,
        "Front_BFI_Housing_R": bfi_h_r,
        "Front_BFI_Housing_L": bfi_h_l,
        "Front_BFI_Carrier_R": bfi_c_r,
        "Front_BFI_Carrier_L": bfi_c_l,
    }
    interferences: Dict[str, float] = {}

    def ov(a: Part.Shape, b: Part.Shape) -> float:
        if not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return round(a.common(b).Volume, 4)

    frame_compound = ref_groups["Ref_AD5M_Frame"]
    enc_compound = Part.makeCompound(enc.Solids)
    static_hw = Part.makeCompound([y_rail_r, y_rail_l, mot_body_r, mot_body_l, pulley_r, pulley_l, ds_brg_r, ds_brg_l, bfi_brg_r, bfi_brg_l])
    belts_all = Part.makeCompound([belt_a, belt_b])

    for name, shp in static_grp.items():
        interferences[f"{name}_vs_frame"] = ov(shp, frame_compound)
        interferences[f"{name}_vs_enc"]   = ov(shp, enc_compound)
        interferences[f"{name}_vs_static_hw"] = ov(shp, static_hw)
        interferences[f"{name}_vs_belts"] = ov(shp, belts_all)
    interferences["Motor_DS_Cap_R_vs_Mount_R"] = ov(cap_r, mot_r)
    interferences["Motor_DS_Cap_L_vs_Mount_L"] = ov(cap_l, mot_l)

    # Split-half mating interference checks (0.0000 mm3)
    interferences["XY_Joint_R_Upper_vs_Lower"] = ov(xy_r_parts["Upper"], xy_r_parts["Lower"])
    interferences["XY_Joint_R_Lower_vs_BottomCap"] = ov(xy_r_parts["Lower"], xy_r_parts["Bottom_Cap"])
    interferences["XY_Joint_R_Upper_vs_BottomCap"] = ov(xy_r_parts["Upper"], xy_r_parts["Bottom_Cap"])
    interferences["XY_Joint_L_Upper_vs_Lower"] = ov(xy_l_parts["Upper"], xy_l_parts["Lower"])

    xy_r_all = Part.makeCompound(list(xy_r_parts.values()))
    xy_l_all = Part.makeCompound(list(xy_l_parts.values()))
    xy_brgs_r = Part.makeCompound([xy1_brg_r, xy2_brg_r, xy2_20t_r])
    xy_brgs_l = Part.makeCompound([xy1_brg_l, xy2_brg_l, xy2_20t_l])

    # Self-checks vs bearings, belts, rails & blocks at nominal pose
    interferences["XY_Joint_R_vs_brgs_R"] = ov(xy_r_all, xy_brgs_r)
    interferences["XY_Joint_L_vs_brgs_L"] = ov(xy_l_all, xy_brgs_l)
    interferences["XY_Joint_R_vs_belt_A"] = ov(xy_r_all, belt_a)
    interferences["XY_Joint_R_vs_belt_B"] = ov(xy_r_all, belt_b)
    interferences["XY_Joint_L_vs_belt_A"] = ov(xy_l_all, belt_a)
    interferences["XY_Joint_L_vs_belt_B"] = ov(xy_l_all, belt_b)
    interferences["X_Carriage_vs_x_blk"] = ov(x_car, x_blk)
    interferences["X_Carriage_vs_x_rail"] = ov(x_car, x_rail)
    interferences["X_Carriage_vs_xy_joints_nom"] = ov(x_car, Part.makeCompound([xy_r_all, xy_l_all]))
    interferences["XY_Joints_nom_vs_y_blocks"] = ov(Part.makeCompound([xy_r_all, xy_l_all]), Part.makeCompound([y_blk_r, y_blk_l]))
    interferences["XY_Joints_nom_vs_x_rail"] = ov(Part.makeCompound([xy_r_all, xy_l_all]), x_rail)

    # 4-Corner Dynamic Sweep (X=+-115mm, Y_yc in [-100, +125] -> 225mm Y travel w/ Ø18mm idlers)
    static_all = Part.makeCompound(list(static_grp.values()) + [frame_compound, static_hw])
    for pose_name, xc_test, yyc_test in [
        ("FrontLeft_min",  -115.0, -100.0),
        ("FrontRight_min", +115.0, -100.0),
        ("RearLeft_max",   -115.0, +125.0),
        ("RearRight_max",  +115.0, +125.0),
    ]:
        xy_rt = list(build_xy_joint_split(+1, yyc_test).values())
        xy_lt = list(build_xy_joint_split(-1, yyc_test).values())
        xc_t   = build_x_carriage_base(xc_test, yyc_test)
        xr_t   = make_mgn12_rail(-150.0, 150.0, yyc_test - 10.0, yyc_test - 2.0, Z_XRAIL_MIN, Z_XRAIL_MAX)
        xb_t   = make_mgn12h_block(xc_test, yyc_test, Z_XRAIL_MID, "X_FRONT")
        yb_rt  = make_mgn12h_block(0, yyc_test, Z_YRAIL_MID, "Y_INWARD_R")
        yb_lt  = make_mgn12h_block(0, yyc_test, Z_YRAIL_MID, "Y_INWARD_L")
        yc_t   = yyc_test - 8.500
        yp_t   = yc_t + 2.0 * R_20T
        p_rt = Part.makeCompound([
            make_f695_pair_ref(+X_BFI, yc_t - R_F695, Z_BELT_A),
            make_f695_pair_ref(+X_XY2_SM, yp_t + R_F695, Z_BELT_A),
            make_idler_20t_ref(+X_XY2_20T, yc_t + R_20T, Z_BELT_B),
        ])
        p_lt = Part.makeCompound([
            make_f695_pair_ref(-X_BFI, yc_t - R_F695, Z_BELT_B),
            make_f695_pair_ref(-X_XY2_SM, yp_t + R_F695, Z_BELT_B),
            make_idler_20t_ref(-X_XY2_20T, yc_t + R_20T, Z_BELT_A),
        ])
        ba_t, bb_t = make_belts_ref(yyc_test)
        xy_rt_cmp = Part.makeCompound(xy_rt)
        xy_lt_cmp = Part.makeCompound(xy_lt)
        moving_all = Part.makeCompound([xy_rt_cmp, xy_lt_cmp, xc_t, xr_t, xb_t, yb_rt, yb_lt, p_rt, p_lt])
        interferences[f"sweep_{pose_name}_vs_static_all"] = ov(moving_all, static_all)
        interferences[f"sweep_{pose_name}_xcar_vs_joints"] = ov(xc_t, Part.makeCompound([xy_rt_cmp, xy_lt_cmp]))
        interferences[f"sweep_{pose_name}_xyR_vs_brgs_belts"] = ov(xy_rt_cmp, Part.makeCompound([p_rt, ba_t, bb_t]))
        interferences[f"sweep_{pose_name}_xyL_vs_brgs_belts"] = ov(xy_lt_cmp, Part.makeCompound([p_lt, ba_t, bb_t]))

    # BFI slider stroke check (+-4.0 mm)
    for delta in (-4.0, +4.0):
        c_shift = bfi_c_r.copy()
        c_shift.translate(App.Vector(0, delta, 0))
        interferences[f"bfi_slider_dy_{delta:+.1f}_vs_housing_r"] = ov(c_shift, bfi_h_r)

    max_ov = max(interferences.values()) if interferences else 0.0
    for k, v in interferences.items():
        if v > 0.0:
            print(f"  NON-ZERO INTERFERENCE: {k} = {v:.4f} mm3")
    print(f"Max interference across {len(interferences)} checks: {max_ov:.4f} mm3")

    val = {
        "parts": part_reports,
        "interferences_mm3": interferences,
        "max_interference_mm3": max_ov,
        "all_clear": max_ov == 0.0,
    }
    with open(OUT_DIR / "validation.json", "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2)
    print(f"Saved validation report to {OUT_DIR / 'validation.json'}")


if __name__ == "__main__":
    main()
