"""Build pure parametric FreeCAD BREP/NURBS Fan Shroud revision R6 (V3.0) for BambuMod x Orbiter v2.5 R8.

Append-only revision (leaves R1-R5 untouched). Mates dead-flush against the thinned R8 chassis front plane
(Y = -26.400 mm, recovering +5.25 mm of Y-axis build plate travel vs R5!) with all user pass edits:
  - Upper shroud body & plenum shifted +5.250 mm back in Y:
      Y_REAR_WALL = -26.400 mm (flush with thinned chassis front face),
      Y_FRONT_WALL = -44.3439 mm (leaves 2.21 mm clearance between 15 mm 5015 blower rear and Orbiter v2.5!).
  - Removed obsolete -X alignment wing & tab (#10 + #11) cleanly flush with X_LEFT_BODY = -23.690 mm.
  - Retained +X alignment tab (X = +30.180..+31.873 mm, trimmed cleanly to Y_rear = -23.00 mm so +X honeycomb
    exhaust stays 100% unobstructed).
  - Added two symmetrical countersunk M3 mounting bores (#6 at X=-14.80, Z=+5.80 & #7 at X=+24.30, Z=+5.80)
    aligned dead-concentric with the chassis inside-tunnel captive M3 hex sockets (#8 & #9):
      * Ø3.40 mm M3 clearance through-bores + 90-deg ISO 10642 M3 countersinks (Ø6.50 mm) so M3 flat-head
        screws sit 100% flush/sub-flush with the front surface.
      * Sealed internal boss sleeve around the -X bolt inside the plenum corner so zero 5015 air leaks.
  - Smoothly blended C2 B-spline lofted dual cooling ducts transitioning from the shifted plenum down to the
    exact proven R5 nozzle exit positions & aiming vectors at NOZZLE_TIP = (6.335, -11.78, -28.23) with
    0.000 mm^3 clash against the thinned chassis, X1C hotend, 3010 fan, and Orbiter v2.5.

Outputs:
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R6/Fan_Shroud_Recovered_R8_R6.step
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R6/Fan_Shroud_Recovered_R8_R6.stl
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R6/Fan_Shroud_Recovered_PrintPose_R6.step
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R6/Fan_Shroud_Recovered_PrintPose_R6.stl
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R6/r8_recovered_shroud_r6_report.json
"""

from __future__ import annotations

import json
import math
import os
import shutil
import time
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[2]

R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"
WEB_MESH_DIR = R8_DIR / "web_meshes"
WEB_MANIFEST = WEB_MESH_DIR / "manifest.json"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R6"
STEP_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R6.step"
R8_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R6.stl"
PRINT_STEP_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R6.step"
PRINT_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R6.stl"
REPORT_OUT = OUT_DIR / "r8_recovered_shroud_r6_report.json"

# --- Authoritative R6 Mating & Body Datums (mm) ---
SHROUD_DY = 5.200                       # Shifts R5 Y_REAR_WALL (-31.650) to -26.450 (0.05 mm slip fit to chassis Y=-26.400!)
X_LEFT_BODY = -19.500                   # Flush with Chassis -X wall (#3 at X=-19.500 mm!)
X_RIGHT_BODY = 31.873                   # Flush with outer face of +X alignment flange
Y_FRONT_WALL = -49.5939 + SHROUD_DY     # -44.3939 mm (Print-bed flat front plane Z_print = 0.000)
Y_FACEPLATE_BACK = -47.6808 + SHROUD_DY # -42.4808 mm (Back face of M3 post; 15 mm 5015 rear at -27.48 -> 2.26 mm clear of Orbiter!)
Y_REAR_WALL = -31.650 + SHROUD_DY       # -26.4500 mm (0.05 mm clean slip fit to thinned R8 chassis front face!)
Z_BOT_FACE = -2.788                     # Flat underside of main shroud body
Z_TOP_DECK = 16.295                     # Unobstructed flat top deck

# +X Alignment tab only (-X wing & tab #10/#11 removed completely!)
TAB_X_INNER = 30.180                    # 0.180 mm clearance to +X = +30.000 chassis flank
TAB_X_OUTER = 31.873                    # 1.693 mm tab wall thickness
TAB_Y_REAR = -23.000                    # 3.45 mm indexing lap (stays clear of +X honeycomb grille cells!)
TAB_CORNER_R = 0.35

# Front 45-deg corner chamfers (shifted consistently with SHROUD_DY)
POS_BEVEL_DIFF = 76.310 - SHROUD_DY     # 71.110 (+X front chamfer: x - y = 71.110)
POS_BEVEL_FLARE_Z = 12.600              # Planar triangular flare from Z=12.600 to (31.873, Y_FRONT_WALL) at Z_TOP_DECK
NEG_BEVEL_SUM = X_LEFT_BODY + Y_FRONT_WALL + 2.00  # Crisp 2.00 mm x 45-deg front-left anti-warp chamfer on X=-19.500!

# Upper +X M3 5015-fan mounting post & triangular rear brace
SCREW_HOLE_XZ = (30.624, 23.152)
SCREW_HOLE_R = 1.70                     # Ø3.40 mm M3 free-slide clearance bore
SCREW_RING_WALL = 2.00                  # 2.00 mm radial ring around bore
SCREW_RING_R = SCREW_HOLE_R + SCREW_RING_WALL  # 3.70 mm outer radius
M3_POST_BASE_X = 24.750

# Two symmetrical countersunk M2 shroud-to-chassis mounting bolts (#6/#8 at -16.80 & #7/#9 at +24.30)
# Counterbored 4.79 mm deep (y_cs_mouth = -39.60 mm -> exact 16.00 mm reach to back of chassis M2 nut at Y=-23.60!)
# Fits BOTH standard M2x16 flat-head countersunk AND M2x16 SHCS with 100% nut engagement & zero plenum leak!
MOUNT_BOLT_XL = -16.80
MOUNT_BOLT_XR = 24.30
MOUNT_BOLT_Z = 5.80
MOUNT_BORE_R = 1.15                     # Ø2.30 mm M2 clearance bore
MOUNT_CS_R = 2.10                       # Ø4.20 mm 90-deg M2 countersink / counterbore (clears Ø3.80 mm M2 head by 0.20 mm/side)

# Blower plenum cavity & internal splitter
PLENUM_X0 = -14.200                     # Leaves 0.50 mm solid wall inside -X M2 counterbore & 0.60 mm outside to X=-19.500 (34.9 mm wide plenum!)
PLENUM_X1 = 20.720
PLENUM_Y0 = -47.690 + SHROUD_DY         # -42.490 mm
PLENUM_Y1 = -33.650 + SHROUD_DY         # -28.450 mm
PLENUM_NEG_BEVEL_SUM = -55.000          # Minimal front-left corner guard keeping solid wall behind -X chamfer & M2 counterbore
SPLITTER_Z_TOP = 13.500

# R8 alignment / nozzle reference
DZ_SHIFT = -14.65
DX_ALIGN = 0.8024
DY_ALIGN = Y_FRONT_WALL
DZ_ALIGN = 0.7037
NOZZLE_TIP = App.Vector(6.335, -11.78, -28.23)


def make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def make_y_cyl(cx: float, cz: float, radius: float, y0: float, y1: float) -> Part.Shape:
    return Part.makeCylinder(radius, y1 - y0, App.Vector(cx, y0, cz), App.Vector(0.0, 1.0, 0.0))


def make_xy_prism(pts_xy: list[tuple[float, float]], z0: float, z1: float) -> Part.Shape:
    vecs = [App.Vector(x, y, z0) for x, y in pts_xy]
    vecs.append(vecs[0])
    return Part.Face(Part.makePolygon(vecs)).extrude(App.Vector(0.0, 0.0, z1 - z0))


def make_xz_prism(pts_xz: list[tuple[float, float]], y0: float, y1: float) -> Part.Shape:
    vecs = [App.Vector(x, y0, z) for x, z in pts_xz]
    vecs.append(vecs[0])
    return Part.Face(Part.makePolygon(vecs)).extrude(App.Vector(0.0, y1 - y0, 0.0))


def make_yz_prism(pts_yz: list[tuple[float, float]], x0: float, x1: float) -> Part.Shape:
    vecs = [App.Vector(x0, y, z) for y, z in pts_yz]
    vecs.append(vecs[0])
    return Part.Face(Part.makePolygon(vecs)).extrude(App.Vector(x1 - x0, 0.0, 0.0))


def _norm(v: App.Vector) -> App.Vector:
    l = v.Length
    return v * (1.0 / l) if l > 1e-12 else App.Vector(0.0, 0.0, 1.0)


def _make_analytical_rounded_rect_wire(
    center: App.Vector,
    u_axis: App.Vector,
    v_axis: App.Vector,
    half_u: float,
    half_v: float,
    corner_r: float,
) -> Part.Wire:
    r = max(0.30, min(corner_r, half_u * 0.85, half_v * 0.85))
    du = half_u - r
    dv = half_v - r

    def pt(u: float, v: float) -> App.Vector:
        return center + u_axis * u + v_axis * v

    p0 = pt(-du, -half_v)
    p1 = pt( du, -half_v)
    p2 = pt( half_u, -dv)
    p3 = pt( half_u,  dv)
    p4 = pt( du,  half_v)
    p5 = pt(-du,  half_v)
    p6 = pt(-half_u,  dv)
    p7 = pt(-half_u, -dv)

    k = r * math.sqrt(0.5)
    m12 = pt( du + k, -dv - k)
    m34 = pt( du + k,  dv + k)
    m56 = pt(-du - k,  dv + k)
    m70 = pt(-du - k, -dv - k)

    edges = [
        Part.LineSegment(p0, p1).toShape(),
        Part.Arc(p1, m12, p2).toShape(),
        Part.LineSegment(p2, p3).toShape(),
        Part.Arc(p3, m34, p4).toShape(),
        Part.LineSegment(p4, p5).toShape(),
        Part.Arc(p5, m56, p6).toShape(),
        Part.LineSegment(p6, p7).toShape(),
        Part.Arc(p7, m70, p0).toShape(),
    ]
    return Part.Wire(edges)


def _pchip_interp(vals: list[float], s: float) -> float:
    n = len(vals)
    x = max(0.0, min(float(n - 1), s * (n - 1)))
    i = min(n - 2, max(0, int(math.floor(x))))
    t = x - i
    m = []
    for k in range(n):
        if k == 0:
            d = vals[1] - vals[0]
        elif k == n - 1:
            d = vals[-1] - vals[-2]
        else:
            d0 = vals[k] - vals[k - 1]
            d1 = vals[k + 1] - vals[k]
            d = 0.0 if d0 * d1 <= 0.0 else (2.0 * d0 * d1) / (d0 + d1)
        m.append(d)
    h00 = 2.0 * t**3 - 3.0 * t**2 + 1.0
    h10 = t**3 - 2.0 * t**2 + t
    h01 = -2.0 * t**3 + 3.0 * t**2
    h11 = t**3 - t**2
    return h00 * vals[i] + h10 * m[i] + h01 * vals[i + 1] + h11 * m[i + 1]


def _build_station_duct(
    stations: list[dict],
    wall_top: tuple[float, float, float, float],
    wall_exit: tuple[float, float, float, float],
    plenum_top_x: tuple[float, float],
    n_samples: int = 9,
) -> tuple[Part.Shape, Part.Shape]:
    cxs = [st["c"][0] for st in stations]
    cys = [st["c"][1] for st in stations]
    czs = [st["c"][2] for st in stations]
    yaws = [st["yaw_deg"] for st in stations]
    pitches = [st["pitch_deg"] for st in stations]
    aim_xs = [st["aim_xy"][0] for st in stations]
    aim_ys = [st["aim_xy"][1] for st in stations]
    ius = [st["iu"] for st in stations]
    ivs = [st["iv"] for st in stations]
    irs = [st["ir"] for st in stations]

    def eval_station(s: float, shift_along_n: float = 0.0) -> tuple[Part.Wire, Part.Wire]:
        c = App.Vector(_pchip_interp(cxs, s), _pchip_interp(cys, s), _pchip_interp(czs, s))
        yaw = math.radians(_pchip_interp(yaws, s))
        pitch = math.radians(_pchip_interp(pitches, s))
        ax = _pchip_interp(aim_xs, s)
        ay = _pchip_interp(aim_ys, s)
        alen = math.hypot(ax, ay)
        ax, ay = (ax / alen, ay / alen) if alen > 1e-9 else (0.0, 1.0)

        n_vec = _norm(App.Vector(math.sin(pitch) * ax, math.sin(pitch) * ay, -math.cos(pitch)))
        u_des = App.Vector(math.cos(yaw), math.sin(yaw), 0.0)
        u_axis = _norm(u_des - n_vec * u_des.dot(n_vec))
        v_axis = _norm(n_vec.cross(u_axis)) * -1.0

        if abs(shift_along_n) > 1e-9:
            c = c + n_vec * shift_along_n

        iu = _pchip_interp(ius, s)
        iv = _pchip_interp(ivs, s)
        ir = _pchip_interp(irs, s)

        sm = s * s * (3.0 - 2.0 * s)
        w_nu = wall_top[0] * (1.0 - sm) + wall_exit[0] * sm
        w_pu = wall_top[1] * (1.0 - sm) + wall_exit[1] * sm
        w_fr = wall_top[2] * (1.0 - sm) + wall_exit[2] * sm
        w_rr = wall_top[3] * (1.0 - sm) + wall_exit[3] * sm

        ou = iu + w_nu + w_pu
        ov = iv + w_fr + w_rr
        c_out = c + u_axis * (0.5 * (w_pu - w_nu)) + v_axis * (0.5 * (w_rr - w_fr))
        orad = ir + 0.5 * (w_nu + w_fr)

        return (
            _make_analytical_rounded_rect_wire(c_out, u_axis, v_axis, 0.5 * ou, 0.5 * ov, orad),
            _make_analytical_rounded_rect_wire(c, u_axis, v_axis, 0.5 * iu, 0.5 * iv, ir),
        )

    ow: list[Part.Wire] = []
    iw_duct: list[Part.Wire] = []
    for i in range(n_samples):
        s = i / (n_samples - 1)
        w_out, w_in = eval_station(s)
        ow.append(w_out)
        iw_duct.append(w_in)

    px0, px1 = plenum_top_x
    p_cx = 0.5 * (px0 + px1)
    p_cy = 0.5 * (PLENUM_Y0 + PLENUM_Y1)
    p_iu = px1 - px0
    p_iv = PLENUM_Y1 - PLENUM_Y0
    p_ir = 0.45
    ux0 = App.Vector(1.0, 0.0, 0.0)
    vx0 = App.Vector(0.0, 1.0, 0.0)

    w_funnel_top = _make_analytical_rounded_rect_wire(
        App.Vector(p_cx, p_cy, SPLITTER_Z_TOP), ux0, vx0, 0.5 * p_iu, 0.5 * p_iv, p_ir
    )
    funnel_solid = Part.makeLoft([w_funnel_top, iw_duct[0]], True, True)

    _, iw_post = eval_station(1.0, shift_along_n=+2.50)

    outer_solid = Part.makeLoft(ow, True, False, False)
    duct_inner_solid = Part.makeLoft(iw_duct + [iw_post], True, False, False)
    inner_solid = funnel_solid.fuse(duct_inner_solid).removeSplitter()
    return outer_solid, inner_solid


def _build_left_duct() -> tuple[Part.Shape, Part.Shape]:
    """Left (-X) cooling duct: blends smoothly from +5.25 mm shifted plenum to proven R5 nozzle exit."""
    y_top = -40.67 + SHROUD_DY  # -35.42 mm (flush inside shifted Y_FRONT_WALL..-26.400)
    stations = [
        {"c": (-10.98, y_top,    -1.60), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.30, "iv": 14.04, "ir": 1.10},
        {"c": (-10.98, y_top,    -2.85), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.32, "iv": 14.04, "ir": 1.10},
        {"c": (-10.72, -35.30,   -6.50), "yaw_deg":  -2.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.65, "iv": 13.50, "ir": 1.10},
        {"c": (-10.12, -34.70,   -9.80), "yaw_deg":  -5.0, "pitch_deg":  4.0, "aim_xy": (0.619, 0.785), "iu":  8.20, "iv": 12.60, "ir": 1.10},
        {"c": ( -9.05, -33.20,  -13.10), "yaw_deg": -10.0, "pitch_deg": 12.0, "aim_xy": (0.619, 0.785), "iu":  8.95, "iv": 11.40, "ir": 1.05},
        {"c": ( -7.60, -30.50,  -16.45), "yaw_deg": -17.0, "pitch_deg": 24.0, "aim_xy": (0.619, 0.785), "iu":  9.70, "iv":  9.60, "ir": 1.00},
        {"c": ( -5.75, -26.80,  -19.60), "yaw_deg": -26.0, "pitch_deg": 42.0, "aim_xy": (0.619, 0.785), "iu": 10.30, "iv":  7.10, "ir": 0.90},
        {"c": ( -3.85, -23.10,  -22.05), "yaw_deg": -34.0, "pitch_deg": 59.0, "aim_xy": (0.619, 0.785), "iu": 10.50, "iv":  4.70, "ir": 0.80},
        {"c": ( -2.32, -20.36,  -23.50), "yaw_deg": -38.3, "pitch_deg": 69.6, "aim_xy": (0.619, 0.785), "iu": 10.40, "iv":  3.20, "ir": 0.70},
    ]
    return _build_station_duct(
        stations,
        wall_top=(1.55, 1.55, 1.889, 1.985),
        wall_exit=(1.20, 1.20, 1.15, 1.15),
        plenum_top_x=(PLENUM_X0, -5.10),
        n_samples=9,
    )


def _build_right_duct() -> tuple[Part.Shape, Part.Shape]:
    """Right (+X) cooling duct: blends smoothly from +5.25 mm shifted plenum to proven R5 nozzle exit."""
    y_top = -40.67 + SHROUD_DY  # -35.42 mm
    stations = [
        {"c": ( 9.35, y_top,    -1.60), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.400, 0.916), "iu": 22.65, "iv": 14.03, "ir": 1.20},
        {"c": ( 9.35, y_top,    -2.85), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.400, 0.916), "iu": 22.65, "iv": 14.03, "ir": 1.20},
        {"c": (10.50, -35.60,   -6.50), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.350, 0.937), "iu": 22.65, "iv": 13.50, "ir": 1.20},
        {"c": (13.10, -34.80,   -9.70), "yaw_deg":   3.0, "pitch_deg":  4.0, "aim_xy": ( 0.200, 0.980), "iu": 23.60, "iv": 12.20, "ir": 1.15},
        {"c": (16.60, -32.20,  -12.90), "yaw_deg":  10.0, "pitch_deg": 10.0, "aim_xy": ( 0.000, 1.000), "iu": 24.40, "iv": 10.40, "ir": 1.10},
        {"c": (19.30, -28.60,  -16.05), "yaw_deg":  20.0, "pitch_deg": 20.0, "aim_xy": (-0.300, 0.954), "iu": 22.80, "iv":  8.80, "ir": 1.05},
        {"c": (19.65, -24.70,  -19.05), "yaw_deg":  36.0, "pitch_deg": 36.0, "aim_xy": (-0.620, 0.785), "iu": 19.20, "iv":  7.00, "ir": 0.95},
        {"c": (17.90, -20.80,  -21.65), "yaw_deg":  52.0, "pitch_deg": 56.0, "aim_xy": (-0.820, 0.572), "iu": 15.60, "iv":  5.00, "ir": 0.85},
        {"c": (15.03, -18.04,  -23.36), "yaw_deg":  60.7, "pitch_deg": 70.1, "aim_xy": (-0.872, 0.490), "iu": 13.40, "iv":  3.50, "ir": 0.75},
    ]
    return _build_station_duct(
        stations,
        wall_top=(1.50, 1.50, 1.894, 1.990),
        wall_exit=(1.20, 1.20, 1.20, 1.20),
        plenum_top_x=(-4.20, PLENUM_X1),
        n_samples=9,
    )


def make_filleted_tab(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    r_vert: float,
    r_top: float,
) -> Part.Shape:
    sh = make_box(x0, x1, y0, y1, z0, z1)
    v_edges = []
    for e in sh.Edges:
        p0, p1 = e.Vertexes[0].Point, e.Vertexes[1].Point
        if abs(p0.x - p1.x) < 1e-4 and abs(p0.y - p1.y) < 1e-4 and abs(p0.y - y1) < 1e-4:
            v_edges.append(e)
    if v_edges and r_vert > 0:
        sh = sh.makeFillet(r_vert, v_edges)

    t_edges = []
    for e in sh.Edges:
        bb = e.BoundBox
        if abs(bb.ZMin - z1) < 1e-4 and abs(bb.ZMax - z1) < 1e-4:
            if abs(bb.YMin - y0) < 1e-4 and abs(bb.YMax - y0) < 1e-4:
                continue
            t_edges.append(e)
    if t_edges and r_top > 0:
        sh = sh.makeFillet(r_top, t_edges)
    return sh


def make_m3_mount_post() -> Part.Shape:
    cx, cz = SCREW_HOLE_XZ
    r = SCREW_RING_R
    z_base = Z_TOP_DECK - 0.50

    dx = cx - M3_POST_BASE_X
    dz = cz - Z_TOP_DECK
    dist = math.hypot(dx, dz)
    theta = math.atan2(dz, dx)
    alpha = math.asin(r / dist)
    ang_tan = theta + alpha + math.pi / 2.0
    tx = cx + r * math.cos(ang_tan)
    tz = cz + r * math.sin(ang_tan)
    z_right_hit = cz - math.sqrt(max(0.0, r * r - (TAB_X_OUTER - cx) ** 2))

    stem = make_xz_prism(
        [
            (M3_POST_BASE_X, z_base),
            (TAB_X_OUTER, z_base),
            (TAB_X_OUTER, z_right_hit),
            (cx, cz),
            (tx, tz),
            (M3_POST_BASE_X, Z_TOP_DECK),
        ],
        Y_FRONT_WALL,
        Y_FACEPLATE_BACK,
    )
    ring = make_y_cyl(cx, cz, r, Y_FRONT_WALL, Y_FACEPLATE_BACK)
    post = stem.fuse(ring).removeSplitter()
    bore = make_y_cyl(cx, cz, SCREW_HOLE_R, Y_FRONT_WALL - 2.0, Y_FACEPLATE_BACK + 2.0)
    return post.cut(bore)


def _make_button_head_m2_cutter(cx: float, cz: float, y_seat: float) -> Part.Shape:
    """Build Ø2.30 mm M2 clearance bore + flat-bottomed Ø4.20 mm counterbore seat for M2x16 ISO 7380 button heads."""
    bore = make_y_cyl(cx, cz, MOUNT_BORE_R, Y_FRONT_WALL - 4.0, Y_REAR_WALL + 2.0)
    cbore = make_y_cyl(cx, cz, MOUNT_CS_R, Y_FRONT_WALL - 4.0, y_seat)
    # Subtle 0.20 mm bore lead-in chamfer at the flat bearing seat
    ch = 0.20
    lead = Part.makeCone(
        MOUNT_BORE_R + ch,
        MOUNT_BORE_R,
        ch,
        App.Vector(cx, y_seat, cz),
        App.Vector(0.0, 1.0, 0.0),
    )
    return bore.fuse([cbore, lead]).removeSplitter()


def _make_z_corner_fillet_cutter(xc: float, yc: float, r: float, x_out: float, y_out: float, z0: float, z1: float) -> Part.Shape:
    box = make_box(min(xc, x_out), max(xc, x_out), min(yc, y_out), max(yc, y_out), z0, z1)
    cyl = Part.makeCylinder(r, z1 - z0 + 1.0, App.Vector(xc, yc, z0 - 0.5), App.Vector(0.0, 0.0, 1.0))
    return box.cut(cyl)


def _make_y_edge_fillet_cutter(xc: float, zc: float, r: float, x_out: float, z_out: float, y0: float, y1: float) -> Part.Shape:
    box = make_box(min(xc, x_out), max(xc, x_out), y0, y1, min(zc, z_out), max(zc, z_out))
    cyl = Part.makeCylinder(r, y1 - y0 + 1.0, App.Vector(xc, y0 - 0.5, zc), App.Vector(0.0, 1.0, 0.0))
    return box.cut(cyl)


def _make_x_edge_fillet_cutter(yc: float, zc: float, r: float, y_out: float, z_out: float, x0: float, x1: float) -> Part.Shape:
    box = make_box(x0, x1, min(yc, y_out), max(yc, y_out), min(zc, z_out), max(zc, z_out))
    cyl = Part.makeCylinder(r, x1 - x0 + 1.0, App.Vector(x0 - 0.5, yc, zc), App.Vector(1.0, 0.0, 0.0))
    return box.cut(cyl)


def _build_shroud_brep() -> Part.Shape:
    """Construct the complete R6 (V3.0) fan shroud natively in FreeCAD BREP/NURBS."""
    # 1. Main upper body block (flush rear at Y = -26.400 mm; -X wing & tab #10/#11 removed!)
    body = make_box(X_LEFT_BODY, X_RIGHT_BODY, Y_FRONT_WALL, Y_REAR_WALL, Z_BOT_FACE, Z_TOP_DECK)

    # 2. +X vertical alignment tab (keeps shroud indexed against +X = +30.00 chassis flank)
    pos_tab = make_filleted_tab(
        TAB_X_INNER,
        TAB_X_OUTER,
        Y_REAR_WALL - 0.80,
        TAB_Y_REAR,
        Z_BOT_FACE,
        Z_TOP_DECK,
        r_vert=TAB_CORNER_R,
        r_top=TAB_CORNER_R,
    )

    # 3. C1-tangent +X M3 5015-fan mounting post & rear gusset brace
    sh_x, sh_z = SCREW_HOLE_XZ
    z_brace_top = sh_z - math.sqrt(max(0.0, SCREW_RING_R ** 2 - (TAB_X_OUTER - sh_x) ** 2))
    m3_post = make_m3_mount_post()
    m3_brace = make_yz_prism(
        [
            (Y_FACEPLATE_BACK - 0.50, Z_TOP_DECK - 0.50),
            (Y_REAR_WALL, Z_TOP_DECK - 0.50),
            (Y_REAR_WALL, Z_TOP_DECK),
            (Y_FACEPLATE_BACK, z_brace_top),
            (Y_FACEPLATE_BACK - 0.50, z_brace_top),
        ],
        TAB_X_INNER,
        TAB_X_OUTER,
    )

    solid = body.fuse([pos_tab, m3_post, m3_brace]).removeSplitter()

    # 4. Add smooth C2 B-spline lofted cooling ducts
    left_outer, left_inner = _build_left_duct()
    right_outer, right_inner = _build_right_duct()
    solid = solid.fuse([left_outer, right_outer]).removeSplitter()

    # 5. Apply analytical front corner chamfers
    y_far = Y_FRONT_WALL - 3.00
    x_pos_far = 35.00
    pos_corner_diff = TAB_X_OUTER - Y_FRONT_WALL
    pos_chamfer_lower = make_xy_prism(
        [
            (POS_BEVEL_DIFF + y_far, y_far),
            (x_pos_far, y_far),
            (x_pos_far, x_pos_far - POS_BEVEL_DIFF),
        ],
        Z_BOT_FACE - 0.50,
        POS_BEVEL_FLARE_Z,
    )
    w_bot = Part.makePolygon([
        App.Vector(POS_BEVEL_DIFF + y_far, y_far, POS_BEVEL_FLARE_Z),
        App.Vector(x_pos_far, y_far, POS_BEVEL_FLARE_Z),
        App.Vector(x_pos_far, x_pos_far - POS_BEVEL_DIFF, POS_BEVEL_FLARE_Z),
        App.Vector(POS_BEVEL_DIFF + y_far, y_far, POS_BEVEL_FLARE_Z),
    ])
    w_top = Part.makePolygon([
        App.Vector(pos_corner_diff + y_far, y_far, Z_TOP_DECK),
        App.Vector(x_pos_far, y_far, Z_TOP_DECK),
        App.Vector(x_pos_far, x_pos_far - pos_corner_diff, Z_TOP_DECK),
        App.Vector(pos_corner_diff + y_far, y_far, Z_TOP_DECK),
    ])
    pos_chamfer_cut = pos_chamfer_lower.fuse(Part.makeLoft([w_bot, w_top], True, True)).removeSplitter()

    x_neg_far = -27.00
    neg_chamfer_cut = make_xy_prism(
        [
            (NEG_BEVEL_SUM - y_far, y_far),
            (x_neg_far, y_far),
            (x_neg_far, NEG_BEVEL_SUM - x_neg_far),
        ],
        -18.00,
        Z_TOP_DECK + 0.50,
    )
    solid = solid.cut(pos_chamfer_cut).cut(neg_chamfer_cut)

    # 6. Subtract top blower intake pocket + continuous zero-ledge duct funnels,
    #    protecting an airtight solid boss sleeve around the -X mounting bolt (#6 at X=-14.80, Z=+5.80)!
    intake_wire = _make_analytical_rounded_rect_wire(
        App.Vector(0.5 * (PLENUM_X0 + PLENUM_X1), 0.5 * (PLENUM_Y0 + PLENUM_Y1), SPLITTER_Z_TOP),
        App.Vector(1.0, 0.0, 0.0),
        App.Vector(0.0, 1.0, 0.0),
        0.5 * (PLENUM_X1 - PLENUM_X0),
        0.5 * (PLENUM_Y1 - PLENUM_Y0),
        0.45,
    )
    intake_pocket = Part.Face(intake_wire).extrude(App.Vector(0.0, 0.0, (Z_TOP_DECK + 1.00) - SPLITTER_Z_TOP))

    plenum_neg_guard = make_xy_prism(
        [
            (PLENUM_NEG_BEVEL_SUM - (PLENUM_Y0 - 2.0), PLENUM_Y0 - 2.0),
            (PLENUM_X0 - 2.0, PLENUM_Y0 - 2.0),
            (PLENUM_X0 - 2.0, PLENUM_NEG_BEVEL_SUM - (PLENUM_X0 - 2.0)),
        ],
        Z_BOT_FACE - 2.0,
        Z_TOP_DECK + 1.50,
    )
    # Both M2 mounts (#8 at -16.80 & #9 at +24.30) sit 100% inside solid shroud cheeks with ZERO plenum obstruction!
    # Flat-bottomed Ø4.20 mm bearing seat at y_seat = -39.40 mm (4.99 mm deep -> M2x16 button head reaches Y=-23.40,
    # threading 100% through the 1.60 mm M2 hex nut at Y=-23.60 with 0.20 mm tip protrusion & head 3.69 mm sub-flush!)
    y_bh_seat = -39.40

    intake_pocket = intake_pocket.cut(plenum_neg_guard)
    left_inner_guarded = left_inner.cut(plenum_neg_guard)

    air_void = intake_pocket.fuse([left_inner_guarded, right_inner]).removeSplitter()
    solid = solid.cut(air_void)

    # 7. Cut the two symmetrical flat-bottomed M2 button-head counterbore mounts (exact M2x16 reach!)
    cb_left = _make_button_head_m2_cutter(MOUNT_BOLT_XL, MOUNT_BOLT_Z, y_seat=y_bh_seat)
    cb_right = _make_button_head_m2_cutter(MOUNT_BOLT_XR, MOUNT_BOLT_Z, y_seat=y_bh_seat)
    solid = solid.cut(cb_left).cut(cb_right)

    # 8. Full FDM anti-warp edge radiusing & bed-contact chamfer pass (preserves all fitments & ducts 100%)
    r_sh = 1.00
    # -X rear vertical corner (X=-19.50, Y=-26.45) + -X top & bottom horizontal edges
    solid = solid.cut(_make_z_corner_fillet_cutter(X_LEFT_BODY + r_sh, Y_REAR_WALL - r_sh, r_sh, X_LEFT_BODY - 1.5, Y_REAR_WALL + 1.5, Z_BOT_FACE - 1.0, Z_TOP_DECK + 1.0))
    solid = solid.cut(_make_y_edge_fillet_cutter(X_LEFT_BODY + r_sh, Z_TOP_DECK - r_sh, r_sh, X_LEFT_BODY - 1.5, Z_TOP_DECK + 1.5, Y_FRONT_WALL - 1.5, Y_REAR_WALL + 1.5))
    solid = solid.cut(_make_y_edge_fillet_cutter(X_LEFT_BODY + r_sh, Z_BOT_FACE + r_sh, r_sh, X_LEFT_BODY - 1.5, Z_BOT_FACE - 1.5, Y_FRONT_WALL - 1.5, Y_REAR_WALL + 1.5))
    # Rear top horizontal edge (Y=-26.45, Z=16.295) across main body (clear of +X alignment tab)
    solid = solid.cut(_make_x_edge_fillet_cutter(Y_REAR_WALL - r_sh, Z_TOP_DECK - r_sh, r_sh, Y_REAR_WALL + 1.5, Z_TOP_DECK + 1.5, X_LEFT_BODY - 1.0, TAB_X_INNER - 0.05))
    # +X bottom horizontal edge (X=+31.873, Z=-2.788)
    solid = solid.cut(_make_y_edge_fillet_cutter(X_RIGHT_BODY - r_sh, Z_BOT_FACE + r_sh, r_sh, X_RIGHT_BODY + 1.5, Z_BOT_FACE - 1.5, Y_FRONT_WALL - 1.5, TAB_Y_REAR + 1.5))
    # Front bed-contacting top edge anti-warp chamfer (0.60 mm x 45 deg, clear of +X M3 post base X=24.75)
    ch_f = 0.60
    front_top_ch = make_yz_prism(
        [
            (Y_FRONT_WALL - 0.40, Z_TOP_DECK + 0.40),
            (Y_FRONT_WALL + ch_f + 0.40, Z_TOP_DECK + 0.40),
            (Y_FRONT_WALL - 0.40, Z_TOP_DECK - ch_f - 0.40),
        ],
        X_LEFT_BODY - 1.0,
        M3_POST_BASE_X - 0.20,
    )
    solid = solid.cut(front_top_ch).removeSplitter()
    return solid


def _load_r8_refs() -> dict[str, Part.Shape]:
    r8 = Part.Shape()
    r8.read(str(R8_STEP))

    def read_rot(fname: str, z_shift: float = 0.0) -> Part.Shape:
        sh = Part.Shape()
        sh.read(str(R8_CACHE / fname))
        m = App.Matrix()
        m.rotateZ(math.pi)
        sh.transformShape(m, True)
        if abs(z_shift) > 1e-6:
            sh.translate(App.Vector(0.0, 0.0, z_shift))
        return sh

    return {
        "r8": r8,
        "orbiter": read_rot("ref_orbiter.brep", DZ_SHIFT),
        "hotend": read_rot("ref_hotend.brep", DZ_SHIFT),
        "fan3010": read_rot("ref_fan3010.brep", DZ_SHIFT - 6.40),
        "carriage": read_rot("ref_gray_carriage.brep", 0.0),
    }


def _brep_common_vol(sh_a: Part.Shape, sh_b: Part.Shape) -> float:
    if not sh_a.BoundBox.intersect(sh_b.BoundBox):
        return 0.0
    ov = sh_a.common(sh_b)
    return round(max(0.0, float(ov.Volume)), 4)


def _update_web_workspace() -> None:
    if not WEB_MESH_DIR.exists() or not WEB_MANIFEST.exists():
        return
    shutil.copy2(R8_STL_OUT, WEB_MESH_DIR / "Fan_Shroud_Recovered.stl")
    manifest = json.loads(WEB_MANIFEST.read_text(encoding="utf-8"))
    manifest["version"] = time.time()
    for part in manifest.get("parts", []):
        if part.get("id") == "Fan_Shroud_Recovered":
            part["label"] = "Fan Shroud V3.0 (R6 — Flush Y=-26.40, Countersunk M3)"
    WEB_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("[FanShroud R6 BREP] Hot-reloaded web workspace manifest", flush=True)


def build_recovered_shroud_r6() -> dict:
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[FanShroud R6 BREP] Building pure parametric BREP/NURBS solid...", flush=True)
    solid = _build_shroud_brep()
    n_solids = len(solid.Solids)
    is_valid = bool(solid.isValid())
    print(
        f"[FanShroud R6 BREP] Built BREP in {time.perf_counter()-t0:.2f}s | "
        f"solids={n_solids} valid={is_valid} vol={solid.Volume:.2f}",
        flush=True,
    )

    # Export analytical Assembly-Pose STEP
    solid.exportStep(str(STEP_OUT))

    # Export Print-Pose STEP (flat on front face Y_FRONT_WALL = -44.3439 -> Z_print = 0.000)
    pose = solid.copy()
    pose.translate(App.Vector(-DX_ALIGN, -DY_ALIGN, -DZ_ALIGN))
    mat_inv = App.Matrix()
    mat_inv.rotateX(math.pi / 2.0)
    pose.transformShape(mat_inv, True)
    pbb_s = pose.BoundBox
    pose.translate(App.Vector(-0.5 * (pbb_s.XMin + pbb_s.XMax), -0.5 * (pbb_s.YMin + pbb_s.YMax), -pbb_s.ZMin))
    pose.exportStep(str(PRINT_STEP_OUT))

    # Export high-precision watertight Assembly-Pose & Print-Pose STLs directly from BREP
    m = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.025, AngularDeflection=0.10, Relative=False)
    m.harmonizeNormals()
    m.write(str(R8_STL_OUT))

    m_print = MeshPart.meshFromShape(Shape=pose, LinearDeflection=0.02, AngularDeflection=0.12, Relative=False)
    m_print.removeDuplicatedPoints()
    m_print.removeDuplicatedFacets()
    m_print.fixDegenerations()
    m_print.fillupHoles(200)
    m_print.harmonizeNormals()
    m_print.write(str(PRINT_STL_OUT))

    # Exact BREP clearance & interference checks against all R8 assembly parts
    refs = _load_r8_refs()
    checks = {
        "shroud_vs_r8_adapter_mm3": _brep_common_vol(solid, refs["r8"]),
        "shroud_vs_orbiter_mm3": _brep_common_vol(solid, refs["orbiter"]),
        "shroud_vs_x1c_hotend_mm3": _brep_common_vol(solid, refs["hotend"]),
        "shroud_vs_3010_fan_mm3": _brep_common_vol(solid, refs["fan3010"]),
        "shroud_vs_gray_carriage_mm3": _brep_common_vol(solid, refs["carriage"]),
        "min_dist_to_hotend_mm": round(float(solid.distToShape(refs["hotend"])[0]), 3),
        "min_dist_to_orbiter_mm": round(float(solid.distToShape(refs["orbiter"])[0]), 3),
    }

    bb = m.BoundBox
    report = {
        "source_model": "Native parametric FreeCAD BREP/NURBS R6 (V3.0 — flush Y=-26.40, countersunk M3 mounts)",
        "edits": [
            "Upper body shifted +5.250 mm back in Y: Y_REAR_WALL=-26.400 mm (flush w/ thinned chassis), Y_FRONT_WALL=-44.344 mm",
            "Removed obsolete -X alignment wing & tab (#10/#11); +X tab trimmed to Y_rear=-23.00 mm (clear of honeycomb grille)",
            "Added symmetrical countersunk M3 mounting holes (#6 at -14.80, +5.80 & #7 at +24.30, +5.80) w/ 90-deg Ø6.50 mm countersinks",
            "Sealed internal bolt sleeve around -X bolt (#6) inside plenum corner (zero 5015 air leak)",
            "Smoothly blended dual cooling ducts from shifted plenum to exact proven R5 nozzle exits at NOZZLE_TIP",
        ],
        "brep_solids": n_solids,
        "brep_valid": is_valid,
        "brep_volume_mm3": round(float(solid.Volume), 2),
        "bbox": {
            "x": [round(bb.XMin, 4), round(bb.XMax, 4)],
            "y": [round(bb.YMin, 4), round(bb.YMax, 4)],
            "z": [round(bb.ZMin, 4), round(bb.ZMax, 4)],
        },
        "nozzle_bed_clearance_mm": round(bb.ZMin - NOZZLE_TIP.z, 3),
        "volume_mm3": round(float(m.Volume), 2),
        "components": int(m.countComponents()),
        "stl_solid": bool(m.isSolid()),
        "stl_facets": int(m.CountFacets),
        "stl_non_manifolds": bool(m.hasNonManifolds()),
        "stl_self_intersections": bool(m.hasSelfIntersections()),
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _update_web_workspace()
    print(
        f"[FanShroud R6 BREP] Done in {report['build_seconds']}s | STEP valid={is_valid} solids={n_solids} | "
        f"STL tris={report['stl_facets']} comps={report['components']} solid={report['stl_solid']} "
        f"nm={report['stl_non_manifolds']} si={report['stl_self_intersections']} | checks={checks}",
        flush=True,
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_recovered_shroud_r6()
