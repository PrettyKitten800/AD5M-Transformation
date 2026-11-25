"""Build pure parametric FreeCAD BREP/NURBS Fan Shroud revision R5 for BambuMod x Orbiter v2.5 R8.

Reconstructed natively from scratch in FreeCAD Part (analytical planes, cylinders, fillets,
and smooth C2 B-spline lofted cooling ducts — zero upstream STL mesh in the output), matching
every proven R4 mating datum, nozzle exit position/aiming vector, and all R5 design edits:
  - Pure flat rear face (Y = -31.650 mm, magnet pockets removed)
  - Both vertical alignment tabs (X = +/-30.180..+/-31.873 mm, Y_rear = -26.843 mm) extending
    full height up to the flat top deck Z = 16.295 mm (+X tab bottom flush at Z = -2.788 mm)
  - Supporting -X connecting bridge flush with the top deck Z = 16.295 mm
  - +X outer shroud wall flush with the +X alignment flange outer face (X = +31.873 mm)
  - Unobstructed flat top deck at Z = 16.295 mm (upper honeycomb skirt removed)
  - C1-tangent +X M3 mounting post at (30.624, 23.152) with Ø3.40 mm M3 free-slide bore,
    2.00 mm radial ring (R = 3.70 mm), and 1.693 mm triangular rear gusset brace
  - Single-face 45-deg front corner chamfers: -X (x + y = -63.569, extending flush past the
    -X duct root) and +X (x - y = 76.310 up to Z = 12.600, flaring via one crisp planar
    triangle to (31.873, -49.5939) at Z = 16.295 to support the M3 post)
  - Smooth C2 B-spline lofted dual cooling ducts starting C1-tangent to the flat front bed face
    (Y = -49.5939 mm, zero step lip) and aiming cleanly at NOZZLE_TIP = (6.335, -11.78, -28.23).

Outputs:
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R5/Fan_Shroud_Recovered_R8_R5.step
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R5/Fan_Shroud_Recovered_R8_R5.stl
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R5/Fan_Shroud_Recovered_PrintPose_R5.stl
  - outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R5/r8_recovered_shroud_r5_report.json
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
import numpy as np
import Part

REPO = Path(__file__).resolve().parents[2]

R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"
WEB_MESH_DIR = R8_DIR / "web_meshes"
WEB_MANIFEST = WEB_MESH_DIR / "manifest.json"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R5"
STEP_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R5.step"
R8_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R5.stl"
PRINT_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R5.stl"
REPORT_OUT = OUT_DIR / "r8_recovered_shroud_r5_report.json"

# --- Authoritative R8/R5 Mating & Body Datums (mm) ---
X_LEFT_BODY = -23.690
X_RIGHT_BODY = 31.873       # Flush with outer face of +X alignment flange
Y_FRONT_WALL = -49.5939     # Print-bed flat front plane (Z_print = 0.000)
Y_FACEPLATE_BACK = -47.6808 # Back face of M3 mounting post (1.913 mm thick)
Y_REAR_WALL = -31.650       # Flat rear plane mating against R8 adapter
Z_BOT_FACE = -2.788         # Flat underside of main shroud body
Z_TOP_DECK = 16.295         # Unobstructed flat top deck

# Alignment tabs & -X connecting bridge
TAB_X_INNER = 30.180        # +/-30.180 mm (0.180 mm clearance per side to 60 mm R8 adapter)
TAB_X_OUTER = 31.873        # 1.693 mm tab wall thickness
TAB_Y_REAR = -26.843
NEG_WING_Y_FRONT = -35.058
NEG_WING_Z_BOT = -1.670
NEG_TAB_Z_BOT = -2.540
TAB_CORNER_R = 0.35

# Front 45-deg corner chamfers
POS_BEVEL_DIFF = 76.310     # +X front chamfer: x - y = 76.310
POS_BEVEL_FLARE_Z = 12.600  # Planar triangular flare from Z=12.600 to (31.873,-49.5939) at Z_TOP_DECK
NEG_BEVEL_SUM = -63.569     # -X front chamfer: x + y = -63.569

# Upper +X M3 mounting post & triangular rear brace
SCREW_HOLE_XZ = (30.624, 23.152)
SCREW_HOLE_R = 1.70         # Ø3.40 mm M3 free-slide clearance bore
SCREW_RING_WALL = 2.00      # 2.00 mm radial ring around bore
SCREW_RING_R = SCREW_HOLE_R + SCREW_RING_WALL  # 3.70 mm outer radius
M3_POST_BASE_X = 24.750

# Blower plenum cavity & internal splitter
PLENUM_X0 = -15.590
PLENUM_X1 = 20.720
PLENUM_Y0 = -47.690
PLENUM_Y1 = -33.650
PLENUM_NEG_BEVEL_SUM = -61.500  # Keeps >= 1.46 mm solid wall behind -X 45-deg chamfer (clean non-grazing cut)
SPLITTER_Z_TOP = 13.500

# R8 alignment / nozzle reference
DZ_SHIFT = -14.65
DX_ALIGN = 0.8024
DY_ALIGN = -49.5939
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
    """Exact 8-edge G1-tangent rounded rectangle (4 straight lines + 4 quarter-circle arcs).

    Produces zero spline overshoot on flat sides (exact Y = -49.5939 front bed face and
    exact Y = -31.650 rear face) and consistent CCW edge ordering for twist-free Part.makeLoft.
    """
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
    """Monotone piecewise cubic Hermite interpolation (PCHIP) on uniform parameter s in [0, 1].

    Guaranteed zero ringing/overshoot between equal control values (keeps duct roots
    strictly tangent to the flat front and rear faces with zero bulge).
    """
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
    """Build smooth overshoot-free outer & inner duct lofts preserving exact R4 internal airways.

    The inner airway runs continuously from the upper plenum intake (Z = SPLITTER_Z_TOP)
    through a smooth converging funnel directly into the curved cooling duct (zero floor
    ledges or corner steps at Z = -2.29 mm). The outer shell starts inside the upper body
    at Z = -1.60 mm and follows the inner airway contour at a uniform sleek wall thickness.
    """
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

        # Station plane normal: straight down (0, 0, -1) at pitch=0, tilting smoothly toward nozzle aim
        n_vec = _norm(App.Vector(math.sin(pitch) * ax, math.sin(pitch) * ay, -math.cos(pitch)))
        u_des = App.Vector(math.cos(yaw), math.sin(yaw), 0.0)
        u_axis = _norm(u_des - n_vec * u_des.dot(n_vec))
        v_axis = _norm(n_vec.cross(u_axis)) * -1.0  # At pitch=0, yaw=0: v=(0, +1, 0), so -v is front (-Y)

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

    # Build crisp 2-wire ruled converging funnel from Z = SPLITTER_Z_TOP down to Z = -1.60 (exact iw_duct[0]!)
    # Ruled loft guarantees 100% flat front/rear plenum walls, dead-straight ramp on -X & splitter walls,
    # smooth corner-radius morph (0.45 -> 1.10/1.20 mm), and ZERO spline bulge or floor ledges!
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

    # Extend curved inner duct +2.5 mm cleanly past the nozzle exit plane
    _, iw_post = eval_station(1.0, shift_along_n=+2.50)

    outer_solid = Part.makeLoft(ow, True, False, False)
    duct_inner_solid = Part.makeLoft(iw_duct + [iw_post], True, False, False)
    inner_solid = funnel_solid.fuse(duct_inner_solid).removeSplitter()
    return outer_solid, inner_solid


def _build_left_duct() -> tuple[Part.Shape, Part.Shape]:
    """Left (-X) cooling duct: exact R4 internal airway + seamless plenum funnel + uniform wall.

    Starts flush with front face Y = -49.5939 and rear face Y = -31.650 inside upper body,
    sweeps smoothly to proven R4 exit (-2.32, -20.36, -23.50) aiming (0.580, 0.736, -0.349).
    """
    stations = [
        {"c": (-10.98, -40.67,  -1.60), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.30, "iv": 14.04, "ir": 1.10},
        {"c": (-10.98, -40.67,  -2.85), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.32, "iv": 14.04, "ir": 1.10},
        {"c": (-10.72, -39.95,  -6.50), "yaw_deg":  -2.0, "pitch_deg":  0.0, "aim_xy": (0.619, 0.785), "iu":  7.65, "iv": 13.50, "ir": 1.10},
        {"c": (-10.12, -38.30,  -9.80), "yaw_deg":  -5.0, "pitch_deg":  4.0, "aim_xy": (0.619, 0.785), "iu":  8.20, "iv": 12.60, "ir": 1.10},
        {"c": ( -9.05, -35.40, -13.10), "yaw_deg": -10.0, "pitch_deg": 12.0, "aim_xy": (0.619, 0.785), "iu":  8.95, "iv": 11.40, "ir": 1.05},
        {"c": ( -7.60, -31.60, -16.45), "yaw_deg": -17.0, "pitch_deg": 24.0, "aim_xy": (0.619, 0.785), "iu":  9.70, "iv":  9.60, "ir": 1.00},
        {"c": ( -5.75, -27.20, -19.60), "yaw_deg": -26.0, "pitch_deg": 42.0, "aim_xy": (0.619, 0.785), "iu": 10.30, "iv":  7.10, "ir": 0.90},
        {"c": ( -3.85, -23.10, -22.05), "yaw_deg": -34.0, "pitch_deg": 59.0, "aim_xy": (0.619, 0.785), "iu": 10.50, "iv":  4.70, "ir": 0.80},
        {"c": ( -2.32, -20.36, -23.50), "yaw_deg": -38.3, "pitch_deg": 69.6, "aim_xy": (0.619, 0.785), "iu": 10.40, "iv":  3.20, "ir": 0.70},
    ]
    # Keep top outer Y strictly inside [-49.5939, -31.650] by 0.015 mm so body front/rear planes stay unbroken
    return _build_station_duct(
        stations,
        wall_top=(1.55, 1.55, 1.889, 1.985),
        wall_exit=(1.20, 1.20, 1.15, 1.15),
        plenum_top_x=(PLENUM_X0, -5.10),
        n_samples=9,
    )


def _build_right_duct() -> tuple[Part.Shape, Part.Shape]:
    """Right (+X) cooling duct: exact R4 internal airway + seamless plenum funnel + uniform wall.

    Starts flush with front face Y = -49.5939 and rear face Y = -31.650 (0.000 mm^3 R8 overlap),
    sweeps out to X=+19.6 around the X1C hotend, and aims at (15.03, -18.04, -23.36).
    """
    stations = [
        {"c": ( 9.35, -40.67,  -1.60), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.400, 0.916), "iu": 22.65, "iv": 14.03, "ir": 1.20},
        {"c": ( 9.35, -40.67,  -2.85), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.400, 0.916), "iu": 22.65, "iv": 14.03, "ir": 1.20},
        {"c": (10.50, -39.95,  -6.50), "yaw_deg":   0.0, "pitch_deg":  0.0, "aim_xy": ( 0.350, 0.937), "iu": 22.65, "iv": 13.50, "ir": 1.20},
        {"c": (13.10, -38.10,  -9.70), "yaw_deg":   3.0, "pitch_deg":  4.0, "aim_xy": ( 0.200, 0.980), "iu": 23.60, "iv": 12.20, "ir": 1.15},
        {"c": (16.60, -34.50, -12.90), "yaw_deg":  10.0, "pitch_deg": 10.0, "aim_xy": ( 0.000, 1.000), "iu": 24.40, "iv": 10.40, "ir": 1.10},
        {"c": (19.30, -29.80, -16.05), "yaw_deg":  20.0, "pitch_deg": 20.0, "aim_xy": (-0.300, 0.954), "iu": 22.80, "iv":  8.80, "ir": 1.05},
        {"c": (19.65, -25.10, -19.05), "yaw_deg":  36.0, "pitch_deg": 36.0, "aim_xy": (-0.620, 0.785), "iu": 19.20, "iv":  7.00, "ir": 0.95},
        {"c": (17.90, -20.80, -21.65), "yaw_deg":  52.0, "pitch_deg": 56.0, "aim_xy": (-0.820, 0.572), "iu": 15.60, "iv":  5.00, "ir": 0.85},
        {"c": (15.03, -18.04, -23.36), "yaw_deg":  60.7, "pitch_deg": 70.1, "aim_xy": (-0.872, 0.490), "iu": 13.40, "iv":  3.50, "ir": 0.75},
    ]
    # Keep top outer Y strictly inside [-49.5939, -31.650] by 0.015 mm so body front/rear planes stay unbroken
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
    fillet_front_outer_x: float | None = None,
) -> Part.Shape:
    """Create a vertical alignment rail with rounded rear corners and top cap."""
    sh = make_box(x0, x1, y0, y1, z0, z1)
    v_edges = []
    for e in sh.Edges:
        p0, p1 = e.Vertexes[0].Point, e.Vertexes[1].Point
        if abs(p0.x - p1.x) < 1e-4 and abs(p0.y - p1.y) < 1e-4:
            if abs(p0.y - y1) < 1e-4:
                v_edges.append(e)
            elif fillet_front_outer_x is not None and abs(p0.y - y0) < 1e-4 and abs(p0.x - fillet_front_outer_x) < 1e-4:
                v_edges.append(e)
    if v_edges and r_vert > 0:
        sh = sh.makeFillet(r_vert, v_edges)

    t_edges = []
    for e in sh.Edges:
        bb = e.BoundBox
        if abs(bb.ZMin - z1) < 1e-4 and abs(bb.ZMax - z1) < 1e-4:
            if fillet_front_outer_x is None and abs(bb.YMin - y0) < 1e-4 and abs(bb.YMax - y0) < 1e-4:
                continue
            t_edges.append(e)
    if t_edges and r_top > 0:
        sh = sh.makeFillet(r_top, t_edges)
    return sh


def make_m3_mount_post() -> Part.Shape:
    """Build C1-tangent M3 mounting post flowing smoothly from top deck into the R=3.70 mm ring."""
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


def _build_shroud_brep() -> Part.Shape:
    """Construct the complete R5 fan shroud natively in FreeCAD BREP/NURBS."""
    # 1. Main upper body block
    body = make_box(X_LEFT_BODY, X_RIGHT_BODY, Y_FRONT_WALL, Y_REAR_WALL, Z_BOT_FACE, Z_TOP_DECK)

    # 2. Vertical alignment tabs (+X and -X) and -X connecting wing
    pos_tab = make_filleted_tab(
        TAB_X_INNER,
        TAB_X_OUTER,
        Y_REAR_WALL - 0.80,
        TAB_Y_REAR,
        Z_BOT_FACE,
        Z_TOP_DECK,
        r_vert=TAB_CORNER_R,
        r_top=TAB_CORNER_R,
        fillet_front_outer_x=None,
    )
    neg_wing = make_box(-TAB_X_INNER - 0.50, X_LEFT_BODY + 0.80, NEG_WING_Y_FRONT, Y_REAR_WALL, NEG_WING_Z_BOT, Z_TOP_DECK)
    neg_tab = make_filleted_tab(
        -TAB_X_OUTER,
        -TAB_X_INNER,
        NEG_WING_Y_FRONT,
        TAB_Y_REAR,
        NEG_TAB_Z_BOT,
        Z_TOP_DECK,
        r_vert=TAB_CORNER_R,
        r_top=TAB_CORNER_R,
        fillet_front_outer_x=-TAB_X_OUTER,
    )

    # 3. C1-tangent +X M3 mounting post & 1.693 mm triangular rear gusset brace
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

    # 4. Fuse upper body exterior components
    solid = body.fuse([pos_tab, neg_wing, neg_tab, m3_post, m3_brace]).removeSplitter()

    # 5. Add smooth 15-station cubic-Bezier C2 B-spline lofted outer cooling ducts
    left_outer, left_inner = _build_left_duct()
    right_outer, right_inner = _build_right_duct()
    solid = solid.fuse([left_outer, right_outer]).removeSplitter()

    # 6. Apply analytical front corner chamfers & front bed plane flush trim
    y_far = -52.50
    x_pos_far = 35.00
    pos_corner_diff = TAB_X_OUTER - Y_FRONT_WALL  # 81.4669 at (31.873, -49.5939)
    pos_chamfer_lower = make_xy_prism(
        [
            (POS_BEVEL_DIFF + y_far, y_far),
            (x_pos_far, y_far),
            (x_pos_far, x_pos_far - POS_BEVEL_DIFF),
        ],
        Z_BOT_FACE - 0.50,
        POS_BEVEL_FLARE_Z,
    )
    w_bot = Part.makePolygon(
        [
            App.Vector(POS_BEVEL_DIFF + y_far, y_far, POS_BEVEL_FLARE_Z),
            App.Vector(x_pos_far, y_far, POS_BEVEL_FLARE_Z),
            App.Vector(x_pos_far, x_pos_far - POS_BEVEL_DIFF, POS_BEVEL_FLARE_Z),
            App.Vector(POS_BEVEL_DIFF + y_far, y_far, POS_BEVEL_FLARE_Z),
        ]
    )
    w_top = Part.makePolygon(
        [
            App.Vector(pos_corner_diff + y_far, y_far, Z_TOP_DECK),
            App.Vector(x_pos_far, y_far, Z_TOP_DECK),
            App.Vector(x_pos_far, x_pos_far - pos_corner_diff, Z_TOP_DECK),
            App.Vector(pos_corner_diff + y_far, y_far, Z_TOP_DECK),
        ]
    )
    pos_chamfer_cut = pos_chamfer_lower.fuse(Part.makeLoft([w_bot, w_top], True, True)).removeSplitter()

    # -X chamfer: extends down past the -X duct corner so it is 100% flush with the -X bevel
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

    # 7. Subtract top blower intake pocket (Z = SPLITTER_Z_TOP..Z_TOP_DECK) + continuous zero-ledge duct funnels
    intake_wire = _make_analytical_rounded_rect_wire(
        App.Vector(0.5 * (PLENUM_X0 + PLENUM_X1), 0.5 * (PLENUM_Y0 + PLENUM_Y1), SPLITTER_Z_TOP),
        App.Vector(1.0, 0.0, 0.0),
        App.Vector(0.0, 1.0, 0.0),
        0.5 * (PLENUM_X1 - PLENUM_X0),
        0.5 * (PLENUM_Y1 - PLENUM_Y0),
        0.45,
    )
    intake_pocket = Part.Face(intake_wire).extrude(App.Vector(0.0, 0.0, (Z_TOP_DECK + 1.00) - SPLITTER_Z_TOP))

    # Chamfer front-left corner of upper plenum void so wall behind -X 45-deg bevel stays >= 1.07 mm thick everywhere
    plenum_neg_guard = make_xy_prism(
        [
            (PLENUM_NEG_BEVEL_SUM - (PLENUM_Y0 - 2.0), PLENUM_Y0 - 2.0),
            (PLENUM_X0 - 2.0, PLENUM_Y0 - 2.0),
            (PLENUM_X0 - 2.0, PLENUM_NEG_BEVEL_SUM - (PLENUM_X0 - 2.0)),
        ],
        Z_BOT_FACE - 2.0,
        Z_TOP_DECK + 1.50,
    )
    intake_pocket = intake_pocket.cut(plenum_neg_guard)
    left_inner_guarded = left_inner.cut(plenum_neg_guard)

    # 8. Fuse all internal air voids first, then subtract cleanly in one boolean (zero coplanar seam artifacts!)
    air_void = intake_pocket.fuse([left_inner_guarded, right_inner]).removeSplitter()
    solid = solid.cut(air_void).removeSplitter()
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
        "fan3010": read_rot("ref_fan3010.brep", DZ_SHIFT),
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
            part["label"] = "Fan Shroud R5 (Native NURBS/BREP CAD)"
    WEB_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("[FanShroud R5 BREP] Hot-reloaded web workspace manifest", flush=True)


def build_recovered_shroud_r5() -> dict:
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[FanShroud R5 BREP] Building pure parametric BREP/NURBS solid...", flush=True)
    solid = _build_shroud_brep()
    n_solids = len(solid.Solids)
    is_valid = bool(solid.isValid())
    print(f"[FanShroud R5 BREP] Built BREP in {time.perf_counter()-t0:.2f}s | solids={n_solids} valid={is_valid} vol={solid.Volume:.2f}", flush=True)

    # Export analytical STEP
    solid.exportStep(str(STEP_OUT))

    # Export high-precision watertight Assembly-Pose STL directly from BREP
    m = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.025, AngularDeflection=0.10, Relative=False)
    m.harmonizeNormals()
    m.write(str(R8_STL_OUT))

    # Export Print-Pose STL (flat on front face Y = -49.5939 -> Z_print = 0.000)
    m_print = m.copy()
    m_print.translate(-DX_ALIGN, -DY_ALIGN, -DZ_ALIGN)
    mat_inv = App.Matrix()
    mat_inv.rotateX(math.pi / 2.0)
    m_print.transform(mat_inv)
    pbb = m_print.BoundBox
    if abs(pbb.ZMin) > 1e-6:
        m_print.translate(0.0, 0.0, -pbb.ZMin)
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
        "source_model": "Native parametric FreeCAD BREP/NURBS (matching R4/1404902 datums & nozzle exits)",
        "edits": [
            "100% pure analytical BREP upper body, chamfers, alignment tabs, M3 post, and gusset brace (zero upstream STL mesh)",
            "Rear magnet pockets removed; rear face dead-flat at Y = -31.650 mm",
            "Vertical alignment tabs (+/-30.180..+/-31.873 mm) and -X bridge extended to Z = 16.295 mm (+X tab bottom flush at Z = -2.788 mm)",
            "+X outer wall brought flush to X = +31.873 mm",
            "Upper honeycomb skirt removed flush with flat top deck Z = 16.295 mm",
            "C1-tangent +X M3 mounting post at (30.624, 23.152) with Ø3.40 mm bore, 2.00 mm radial ring (R = 3.70 mm), and 1.693 mm rear triangular brace",
            "Single-face 45-deg front chamfers (-X x+y=-63.569 flush past duct root; +X x-y=76.310 with 44.1-deg M3 support flare Z=12.600..16.295)",
            "Smooth C2 B-spline lofted dual cooling ducts C1-tangent to Y = -49.5939 mm front bed face (zero lip) aiming at NOZZLE_TIP",
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
        "stl_non_uniform_faces": int(m.countNonUniformOrientedFacets()),
        "stl_self_intersections": bool(m.hasSelfIntersections()),
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _update_web_workspace()
    print(
        f"[FanShroud R5 BREP] Done in {report['build_seconds']}s | STEP valid={is_valid} solids={n_solids} | "
        f"STL tris={report['stl_facets']} comps={report['components']} solid={report['stl_solid']} "
        f"nm={report['stl_non_manifolds']} si={report['stl_self_intersections']} | checks={checks}",
        flush=True,
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_recovered_shroud_r5()
