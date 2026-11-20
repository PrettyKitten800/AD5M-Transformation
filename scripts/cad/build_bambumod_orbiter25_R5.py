"""Build BambuMod x Orbiter v2.5 AD5M Offset-Hotend Adapter — Revision 5 (R5).

Addresses user feedback after R4:
  1. Silky-smooth, corner-free C2 B-spline cooling air tunnel:
       - Backfills Kirill's internal lower chamber cavity (Y = [front_y, +26.50],
         Z = [7.20, plate_top]) while sparing all four 3010 fan M3 screw bosses
         and outer front/rear/bottom skins, wiping residual internal ledges and
         abrupt Kirill ribs cleanly before carving the new tunnel.
       - Replaces R2/R3/R4's sharp 6-vertex ruled polygon loft (`isRuled=True`)
         with `build_smooth_duct_void()`: a 15-station uniform-arc-length G2/C2
         periodic B-spline loft (`Part.makeLoft(..., isRuled=False)`) transitioning
         smoothly from the circular +X 3010 fan inlet (Y=[-3.10, 25.85],
         Z=[7.75, 34.90], R=14.30) through a cosine-eased curved diffuser into
         the rounded heatsink duct around the shifted X1C fins (r=2.00 mm) and
         flaring smoothly out Kirill's -X hex exhaust grille (r=3.20 mm).
       - Exports STL with tighter curvature deflection (`LinearDeflection=0.025`,
         `AngularDeflection=0.12`) so sliced curves match the C2 B-spline surface.
  2. Extended perpendicular extruder mount boss & M3 through-bore by the +X hotend fan:
       - At the right Orbiter mount (+13.15, 12.08), R4's 4.30 mm bore exited across
         the sloped upper fan tunnel wall, leaving a tilted wedge where an M3 nut
         could not seat flush.
       - Adds a solid Dia 9.00 mm (R = 4.50 mm) vertical cylindrical turret down to
         a flat horizontal perpendicular landing face at Z_NUT_FACE = 27.60 mm
         (4.98 mm plate thickness, sized for standard M3x12 / M3x14 screws + M3 nut),
         clears a Dia 12.40 mm (R = 6.20 mm) circumferential wrench/nut pocket
         strictly below Z_NUT_FACE (confined inside X <= 18.20 mm), and extends the
         M3 through-bore (Dia 3.60 mm / R = 1.80 mm) completely through Z_NUT_FACE.
  3. Preserves all R4 features cleanly:
       - Primary offset-hotend datum (X_mot=0.000, Z_mot=51.900, X_fil=-6.335,
         Z_mount=32.600), plain Dia 44.00 mm smooth motor circle, 3.27 mm clean
         portal web, full-thickness vertical side columns & EBB42 top bridge, 4/4
         symmetric blind rear-entry carriage bores, and left (-23.85, 12.08) M3
         heatset insert pocket.

Credits & License (preserved):
  - BambuMod adapter base: Kirill_Wawe (Printables #1574762), CC BY-NC-SA 4.0
  - Orbiter v2.5 extruder mockup: dr. Lorincz Robert
  - Derived R5 adapter files share CC BY-NC-SA 4.0.
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
)
from build_bambumod_orbiter25_R2 import (  # noqa: E402
    X_FIL,
    X_MOT,
    Z_MOT,
    Z_MOUNT,
    detect_front_shroud_y,
)
from build_bambumod_orbiter25_R3 import CARRIAGE_HOLES_R3  # noqa: E402
from build_bambumod_orbiter25_R4 import (  # noqa: E402
    COL_INNER_X,
    MOT_CIRCLE_R_R4,
    Y_WEB_FRONT,
    Z_TOP_BRIDGE,
)

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R5"

Z_NUT_FACE = 27.600  # Perpendicular underside nut seat (4.98 mm grip from plate_top=32.58)
NUT_BOSS_R = 4.500   # Dia 9.00 mm flat perpendicular landing (fits M3 hex/flange nut & washer)
NUT_MOAT_R = 6.200   # Dia 12.40 mm circumferential wrench/nut clearance below Z_NUT_FACE
RIGHT_MOUNT_BORE_R = 1.800  # Dia 3.60 mm M3 through-bolt bore at (+13.15, 12.08)


def _smoothstep(t: float) -> float:
    """Cosine C1 ease-in/ease-out blend over t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def _rounded_rect_bspline_wire_uniform(
    x: float, y_lo: float, y_hi: float, z_lo: float, z_hi: float, r: float, n_total: int = 96
) -> Part.Wire:
    """Build a uniform-arc-length periodic G2 BSpline section loop starting at (+Y, z_c)."""
    yc, zc = 0.5 * (y_lo + y_hi), 0.5 * (z_lo + z_hi)
    hy, hz = 0.5 * (y_hi - y_lo), 0.5 * (z_hi - z_lo)
    re = max(0.2, min(r, hy - 0.05, hz - 0.05))
    wy, wz = hy - re, hz - re
    al = 0.5 * math.pi * re
    segs = [
        ("line", Vector(x, yc + hy, zc), Vector(x, yc + hy, zc + wz), wz),
        ("arc", yc + wy, zc + wz, 0.0, 0.5 * math.pi, al),
        ("line", Vector(x, yc + wy, zc + hz), Vector(x, yc - wy, zc + hz), 2.0 * wy),
        ("arc", yc - wy, zc + wz, 0.5 * math.pi, math.pi, al),
        ("line", Vector(x, yc - hy, zc + wz), Vector(x, yc - hy, zc - wz), 2.0 * wz),
        ("arc", yc - wy, zc - wz, math.pi, 1.5 * math.pi, al),
        ("line", Vector(x, yc - wy, zc - hz), Vector(x, yc + wy, zc - hz), 2.0 * wy),
        ("arc", yc + wy, zc - wz, 1.5 * math.pi, 2.0 * math.pi, al),
        ("line", Vector(x, yc + hy, zc - wz), Vector(x, yc + hy, zc), wz),
    ]
    tl = sum(s[-1] for s in segs)
    cum, acc = [], 0.0
    for s in segs:
        acc += s[-1]
        cum.append(acc)
    pts = []
    for k in range(n_total):
        tg = (k / n_total) * tl
        for idx, s in enumerate(segs):
            pv = 0.0 if idx == 0 else cum[idx - 1]
            if tg <= cum[idx] + 1e-9:
                u = 0.0 if s[-1] < 1e-9 else min(1.0, max(0.0, (tg - pv) / s[-1]))
                if s[0] == "line":
                    pts.append(s[1] + (s[2] - s[1]) * u)
                else:
                    ang = s[3] + (s[4] - s[3]) * u
                    pts.append(Vector(x, s[1] + re * math.cos(ang), s[2] + re * math.sin(ang)))
                break
    bs = Part.BSplineCurve()
    bs.interpolate(pts, PeriodicFlag=True)
    return Part.Wire([bs.toShape()])


def _eval_smooth_duct_params(x: float) -> tuple[float, float, float, float, float]:
    """Return smooth (y_lo, y_hi, z_lo, z_hi, r_corner) section envelope as a function of X."""
    if x >= 16.5:
        t = _smoothstep((19.65 - x) / (19.65 - 16.5))
        return (-3.10 + 0.25 * t, 25.85 - 0.75 * t, 7.75 - 0.50 * t, 34.90 - 6.40 * t, 14.30 - 8.80 * t)
    elif x >= 2.2:
        t = _smoothstep((16.5 - x) / (16.5 - 2.2))
        return (-2.85 - 0.05 * t, 25.10 - 0.30 * t, 7.25 - 0.60 * t, 28.50 - 3.35 * t, 5.50 - 3.50 * t)
    elif x >= -14.6:
        return (-2.90, 24.80, 6.65, 25.15, 2.00)
    else:
        t = _smoothstep((-14.6 - x) / (-14.6 - (-27.60)))
        return (-2.90 - 0.35 * t, 24.80 + 2.05 * t, 6.65 + 0.10 * t, 25.15 + 0.80 * t, 2.00 + 1.20 * t)


def build_smooth_duct_void() -> Part.Shape:
    """Build smooth C2 periodic B-spline cooling tunnel loft (zero sharp corners or ledges)."""
    xs = [
        19.65, 19.00, 18.20, 17.30, 16.50,
        14.00, 10.50, 6.50, 2.20,
        -2.00, -10.00, -14.60,
        -18.50, -23.00, -27.60,
    ]
    wires = [_rounded_rect_bspline_wire_uniform(x, *_eval_smooth_duct_params(x)) for x in xs]
    loft = Part.makeLoft(wires, True, False)
    assert loft.isValid() and loft.Volume > 0, "Smooth duct BSpline loft invalid!"
    loft.check(True)
    return loft


def build_primary_r5(refs: dict) -> tuple[Part.Shape, dict]:
    """Build R5 Primary adapter with smooth C2 air tunnel & perpendicular +X mount nut boss."""
    bm_body = refs["bm_body"]
    rear_y, front_y = detect_backplate_y_planes(bm_body)
    shroud_front_y = detect_front_shroud_y(bm_body)

    plate_top = Z_MOUNT - 0.02
    plate_bot = Z_MOUNT - 5.80  # 26.800 mm

    work = bm_body.copy()
    # 0. Heal BambuMod upstream 0.0002 mm micro-slit on -X front corner flush to exact front shroud plane
    work = work.fuse(box(-28.10, -27.15, 27.05, shroud_front_y, 30.80, 31.05))

    # 1. Remove stock upper interior features + unused front shroud magnet/cover wings cleanly
    pre_cuts = [
        box(-27.8, 18.42, front_y - 0.05, 27.8, plate_top, 65.0).cut(
            cyl_x(3.10, 23.37, 34.25, 13.5, 20.0)
        ),
        box(-14.0, 14.3, front_y - 0.1, 27.8, 59.5, 69.5),
        box(-31.5, -26.70, front_y + 0.02, 32.5, plate_top, 73.50),
        box(-31.5, -26.70, -2.30, 32.5, 73.50, 81.00),
        box(18.0, 31.5, front_y + 0.02, 32.5, 37.35, 73.50),
        box(18.0, 31.5, -2.30, 32.5, 73.50, 81.00),
        box(14.0, 18.42, front_y - 0.1, 22.0, 37.35, 45.0),
        box(18.35, 18.58, 2.0, 18.5, 36.35, 38.0),
        box(19.42, 30.5, -3.72, 26.46, 7.16, 37.35),
        box(-6.5, 8.6, front_y + 0.1, 13.5, 23.80, 32.55),
    ]
    for c in pre_cuts:
        work = work.cut(c)

    # 2. Cleanly backfill lower inner chamber (leaving all 4x 3010 fan screw bosses & outer skins intact),
    #    then fuse shroud deck, Orbiter plate, EBB42 back slab, and lower blind carriage caps.
    fan_hole_clear = (
        cyl_x(2.20, -0.63, 10.25, 12.0, 20.0)
        .fuse(cyl_x(2.00, 23.37, 10.25, 12.0, 20.0))
        .fuse(cyl_x(2.00, -0.63, 34.25, 12.0, 20.0))
        .fuse(cyl_x(2.20, 23.37, 34.25, 12.0, 20.0))
    )
    chamber_core_fill = (
        box(-27.10, 18.42, front_y, 26.50, 7.20, plate_top)
        .fuse(box(18.42, 19.48, 0.80, 25.80, 7.20, plate_top))
        .cut(fan_hole_clear)
    )
    floor_seal = box(-15.5, 19.50, front_y, 24.5, 5.50, 7.50)
    fan_top_plug = box(18.42, 19.50, 0.80, 21.94, 32.20, 37.35).common(
        cyl_x(14.60, 11.372, 22.246, 18.35, 19.55)
    )
    fan_hood_fill = box(1.5, 19.50, front_y, 27.12, 24.50, plate_top)
    fan_hood_wing = (
        box(18.05, 19.50, 0.80, 27.12, 24.50, 37.35)
        .cut(box(18.00, 18.45, 0.5, 22.0, plate_top, 38.0))
        .cut(box(18.30, 18.60, 0.5, 18.5, 36.35, 38.0))
        .common(box(17.90, 19.50, -3.88, 27.12, 24.50, 37.05))
        .cut(cyl_x(1.78, 23.37, 34.25, 17.80, 20.00))
    )
    front_seal = box(-27.20, 19.50, 24.00, shroud_front_y, 21.80, plate_top)
    ceiling_seal = box(-27.20, 19.50, front_y, 24.50, 24.75, plate_top)
    plate = box(-28.80, 18.10, front_y, 27.80, plate_bot, plate_top)
    plate_front_lip = Part.makePolygon([
        Vector(-27.20, 27.80, plate_bot),
        Vector(-27.20, shroud_front_y, plate_bot),
        Vector(-27.20, 27.80, plate_bot + 2.32),
        Vector(-27.20, 27.80, plate_bot),
    ])
    plate_front_chamfer = Part.Face(plate_front_lip).extrude(Vector(19.50 - (-27.20), 0, 0)).common(
        box(-27.20, 18.10, 27.5, 30.2, plate_bot, plate_top)
    )

    belt_high_zone = box(-40.0, 40.0, rear_y - 0.1, -9.12, 64.8, 75.2)
    ebb_bore_xs = [-27.0, -18.0, 18.0, 27.0]
    back_slab_solid = box(-29.2, 29.2, rear_y, front_y, 20.6, 80.002).cut(belt_high_zone)
    for bx in ebb_bore_xs:
        back_slab_solid = back_slab_solid.cut(cyl_z(2.05, bx, -7.498, 72.9, 80.2))

    # Only add front blind skins on lower carriage holes (Z=3.5 < 20.6); upper holes are drilled directly into back_slab_solid
    blind_caps = [
        cyl_y(2.40, cx, cz, cap_y0, front_y)
        for _, cx, cz, cap_y0, _ in CARRIAGE_HOLES_R3
        if cz < 20.6
    ]

    for solid_add in [
        chamber_core_fill,
        floor_seal,
        fan_top_plug,
        fan_hood_fill,
        fan_hood_wing,
        front_seal,
        ceiling_seal,
        plate,
        plate_front_chamfer,
        back_slab_solid,
        *blind_caps,
    ]:
        work = work.fuse(solid_add)

    work = work.removeSplitter()
    assert work.isValid(), "Primary_R5 pre-cut BRep invalid!"

    # 3. Carve smooth C2 BSpline duct loft FIRST, then add perpendicular +X extruder mount nut boss
    duct_void = build_smooth_duct_void()
    work = work.cut(duct_void)
    work = work.fuse(cyl_z(NUT_BOSS_R, 13.15, 12.08, Z_NUT_FACE, plate_top - 0.50))

    # 4. Carve nut clearance moat, X1C/Orbiter bores, recessed portal, plain 44 mm circle, & upper blind carriage bores
    protect_up_l = cyl_y(2.50, 24.0, 61.0, Y_WEB_FRONT - 0.5, front_y + 1.0)
    protect_up_r_back = cyl_y(2.18, -24.0, 61.0, Y_WEB_FRONT - 0.5, -4.45)

    portal_recess = (
        box(-COL_INNER_X, COL_INNER_X, Y_WEB_FRONT, front_y + 0.5, plate_top, Z_TOP_BRIDGE)
        .cut(protect_up_l.fuse(protect_up_r_back))
    )
    motor_circle_cut = cyl_y(MOT_CIRCLE_R_R4, X_MOT, Z_MOT, rear_y - 1.0, front_y + 0.02)
    motor_front_clear_above_plate = cyl_y(MOT_CIRCLE_R_R4, X_MOT, Z_MOT, front_y - 0.1, 3.0).common(
        box(-25.0, 25.0, front_y - 0.2, 4.0, plate_top, Z_TOP_BRIDGE)
    )
    carriage_re_cuts = [
        cyl_y(2.15, cx, cz, rear_y - 0.2, cap_y0)
        for _, cx, cz, cap_y0, _ in CARRIAGE_HOLES_R3
        if cz >= 20.6
    ]

    final_cuts = [
        cyl_z(NUT_MOAT_R, 13.15, 12.08, 25.00, Z_NUT_FACE).common(
            box(5.0, 18.20, 4.0, 20.0, 24.8, Z_NUT_FACE + 0.1)
        ),
        box(X_FIL - 8.30, X_FIL + 8.30, -2.50, 23.25, 5.20, 7.65),
        box(X_FIL - 6.60, X_FIL + 6.60, 8.28, 30.50, 24.80, 31.10),
        box(X_FIL - 6.60, X_FIL + 6.60, 24.50, 30.50, 24.80, plate_top),
        cyl_y(1.65, X_FIL - 3.425, 27.220, -1.60, 9.00),
        cyl_y(1.65, X_FIL + 3.425, 27.220, -1.60, 9.00),
        cyl_z(2.00, X_FIL, 12.08, plate_bot - 0.50, plate_top + 1.00),
        Part.makeCone(2.60, 1.90, 0.80, Vector(X_FIL, 12.08, 30.50), Vector(0, 0, 1)),
        cyl_z(2.20, -23.85, 12.08, plate_top - 4.30, plate_top + 0.50),
        cyl_z(RIGHT_MOUNT_BORE_R, 13.15, 12.08, Z_NUT_FACE - 0.50, plate_top + 0.50),
        portal_recess,
        motor_circle_cut,
        motor_front_clear_above_plate,
        *carriage_re_cuts,
    ]
    for c in final_cuts:
        work = work.cut(c)

    # Note: omit removeSplitter() after cutting C2 BSpline duct_void (ShapeUpgrade_UnifySameDomain flips BSpline shells)
    assert work.isValid(), "Primary_R5 BRep invalid!"
    assert len(work.Solids) == 1, f"Expected 1 solid, got {len(work.Solids)}"
    solid = work.Solids[0]

    # === Comprehensive Verification ===
    orb_placed = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_body_solids"]]
    orb_bolts = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_bolts"]]
    he_placed = refs["he_raw"].copy()
    he_placed.translate(Vector(X_FIL, 0, 0))
    fan_3010 = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)
    ebb_bkt = refs["ebb_bkt"]
    steel_carriage = box(-40.0, 40.0, -30.0, rear_y - 0.005, -10.0, 90.0)
    belt_low = box(-40.0, 40.0, rear_y - 0.1, -9.12, 9.8, 20.2)
    bm_solid = bm_body.Solids[0]

    fan_holes_obs = {
        f"fan_yz_{y}_{z}": round(solid.common(cyl_x(1.30, y, z, 15.0, 19.6)).Volume, 4)
        for y, z in [(-0.63, 10.25), (23.37, 10.25), (-0.63, 34.25), (23.37, 34.25)]
    }
    ebb_bores_obs = {
        f"ebb_x_{bx:+.0f}": round(solid.common(cyl_z(1.80, bx, -7.498, 73.1, 79.9)).Volume, 4)
        for bx in ebb_bore_xs
    }

    hole_report = {}
    for name, hx, hz, cap_y0, cap_y1_ov in CARRIAGE_HOLES_R3:
        cy1 = front_y if cap_y1_ov is None else cap_y1_ov
        rear_open_cyl = cyl_y(1.80, hx, hz, rear_y + 0.05, cap_y0 - 0.10)
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

    circle_probe = cyl_y(MOT_CIRCLE_R_R4 - 0.05, X_MOT, Z_MOT, rear_y + 0.05, front_y - 0.05).common(
        box(-30.0, 30.0, rear_y, front_y, plate_top + 0.10, 80.0)
    )
    bridge_probe = box(-14.0, 14.0, -9.00, front_y - 0.05, Z_MOT + MOT_CIRCLE_R_R4 + 0.10, 79.95)
    col_l_probe = box(COL_INNER_X + 0.2, 29.0, -9.00, front_y - 0.05, plate_top + 1.0, 58.0)
    col_r_probe = box(-29.0, -COL_INNER_X - 0.2, -9.00, front_y - 0.05, plate_top + 1.0, 58.0)

    duct_clearance_x = {}
    for x0 in [18.5, 14.0, 8.0, 2.5, -18.0, -25.0]:
        probe = box(x0, x0 + 0.5, 5.0, 17.0, 10.0, 22.0)
        duct_clearance_x[f"X_{x0:.1f}"] = round(solid.common(probe).Volume / probe.Volume, 4)

    wall_integrity = {}
    for x0 in [-22.0, -17.0, 5.0, 12.0, 17.5]:
        p_bot = box(x0, x0 + 0.5, 5.0, 17.0, 5.55, 6.45)
        wall_integrity[f"bot_X_{x0:.1f}_frac"] = round(solid.common(p_bot).Volume / p_bot.Volume, 4)
    for x0 in [-25.0, -18.0, -6.335, 5.0, 14.0]:
        p_r = box(x0, x0 + 0.5, -3.85, -3.35, 10.0, 22.0)
        p_f = box(x0, x0 + 0.5, 27.15, 30.05, 10.0, 22.0)
        wall_integrity[f"rear_X_{x0:.1f}_frac"] = round(solid.common(p_r).Volume / p_r.Volume, 4)
        wall_integrity[f"front_X_{x0:.1f}_frac"] = round(solid.common(p_f).Volume / p_f.Volume, 4)

    ann_above = cyl_z(NUT_BOSS_R - 0.05, 13.15, 12.08, Z_NUT_FACE + 0.05, plate_top - 0.05).cut(
        cyl_z(RIGHT_MOUNT_BORE_R + 0.05, 13.15, 12.08, Z_NUT_FACE, plate_top)
    )
    clr_below = cyl_z(NUT_MOAT_R - 0.20, 13.15, 12.08, 25.20, Z_NUT_FACE - 0.05).common(
        box(5.0, 18.10, 4.0, 20.0, 24.8, Z_NUT_FACE)
    )
    bore_cyl = cyl_z(RIGHT_MOUNT_BORE_R - 0.05, 13.15, 12.08, Z_NUT_FACE - 0.5, plate_top + 0.5)
    nut_boss_report = {
        "center_xy_mm": [13.15, 12.08],
        "bore_diameter_mm": round(2.0 * RIGHT_MOUNT_BORE_R, 2),
        "boss_outer_diameter_mm": round(2.0 * NUT_BOSS_R, 2),
        "moat_clearance_diameter_mm": round(2.0 * NUT_MOAT_R, 2),
        "z_nut_face_mm": Z_NUT_FACE,
        "grip_thickness_mm": round(plate_top - Z_NUT_FACE, 2),
        "boss_annulus_solid_fraction": round(solid.common(ann_above).Volume / ann_above.Volume, 4),
        "underside_clearance_obstruction_mm3": round(solid.common(clr_below).Volume, 4),
        "through_bore_obstruction_mm3": round(solid.common(bore_cyl).Volume, 4),
    }

    bb = solid.BoundBox
    report = {
        "variant": "Primary_R5",
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
            "motor_circle_diameter_mm": round(2.0 * MOT_CIRCLE_R_R4, 2),
            "portal_web_thickness_mm": round(Y_WEB_FRONT - rear_y, 2),
            "top_bridge_min_height_mm": round(bb.ZMax - (Z_MOT + MOT_CIRCLE_R_R4), 2),
            "rear_y": round(rear_y, 3),
            "front_y": round(front_y, 3),
            "smooth_duct_bspline_stations": 15,
            "right_nut_face_z": Z_NUT_FACE,
        },
        "collisions_mm3": {
            "adapter_vs_orbiter_and_motor": round(sum(solid.common(o).Volume for o in orb_placed), 4),
            "adapter_vs_orbiter_m3_bolts": round(sum(solid.common(b).Volume for b in orb_bolts), 4),
            "adapter_vs_x1c_hotend": round(solid.common(he_placed).Volume, 4),
            "adapter_vs_3010_fan": round(solid.common(fan_3010).Volume, 4),
            "3010_fan_vs_orbiter": round(sum(fan_3010.common(o).Volume for o in orb_placed), 4),
            "adapter_vs_ebb42_bracket": round(solid.common(ebb_bkt).Volume, 4),
            "adapter_vs_steel_carriage_plane": round(solid.common(steel_carriage).Volume, 4),
            "adapter_vs_belt_low": round(solid.common(belt_low.cut(bm_solid)).Volume, 4),
            "adapter_vs_belt_high": round(solid.common(belt_high_zone.cut(bm_solid)).Volume, 4),
        },
        "fan_3010_mounting_holes_obstruction_mm3": fan_holes_obs,
        "ebb42_top_mounting_bores_obstruction_mm3": ebb_bores_obs,
        "carriage_holes_4_blind_verification": hole_report,
        "motor_portal_verification": {
            "circle_dia_mm": round(2.0 * MOT_CIRCLE_R_R4, 2),
            "circle_core_obstruction_mm3": round(solid.common(circle_probe).Volume, 4),
            "top_bridge_solid_fraction": round(solid.common(bridge_probe).Volume / bridge_probe.Volume, 4),
            "left_column_solid_fraction": round(solid.common(col_l_probe).Volume / col_l_probe.Volume, 4),
            "right_column_solid_fraction": round(solid.common(col_r_probe).Volume / col_r_probe.Volume, 4),
        },
        "duct_core_solid_fraction_should_be_zero": duct_clearance_x,
        "duct_wall_integrity_should_be_one": wall_integrity,
        "right_extruder_nut_boss_verification": nut_boss_report,
    }

    return solid, {
        "report": report,
        "he_placed": he_placed,
        "orb_placed": Part.makeCompound(orb_placed),
        "fan_3010": fan_3010,
        "ebb_bkt": ebb_bkt,
    }


def export_verified(solid: Part.Shape, ctx: dict) -> dict:
    """Export STEP, verify re-read, export smooth Z=0 flat-back STL, verify volume & manifoldness."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    step_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R5.step"
    stl_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R5.stl"
    fcstd_p = OUT_DIR / "BambuMod_Orbiter25_Assembly_R5.FCStd"

    solid.exportStep(str(step_p))
    re_read = Part.read(str(step_p))
    assert re_read.isValid() and len(re_read.Solids) == 1, "Re-read STEP invalid!"

    stl_shape = solid.copy()
    stl_shape.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    stl_shape.translate(Vector(0, 0, -stl_shape.BoundBox.ZMin))

    # Fine angular + linear deflection ensures the C2 BSpline duct prints smooth and matches BRep volume
    mesh = MeshPart.meshFromShape(Shape=stl_shape, LinearDeflection=0.025, AngularDeflection=0.12, Relative=False)
    mesh.write(str(stl_p))
    mchk = Mesh.Mesh(str(stl_p))
    assert mchk.isSolid(), "STL is not solid!"
    assert not mchk.hasNonManifolds(), "STL has non-manifold edges!"
    vol_err = abs(float(mchk.Volume) - float(solid.Volume)) / float(solid.Volume)
    assert vol_err < 0.005, f"STL vs STEP volume mismatch ({vol_err:.4%})!"

    oh_area = 0.0
    oh_deep = 0.0
    for f in mchk.Facets:
        nz = f.Normal.z
        zc = sum(p[2] for p in f.Points) / 3.0
        if zc > 0.25 and nz < -0.7071:
            oh_area += f.Area
            if nz < -0.94:
                oh_deep += f.Area

    doc = App.newDocument("BambuMod_Orbiter25_R5")
    for obj_name, shp in [
        ("Primary_Adapter_R5", solid),
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

    def _tess_list(shp: Part.Shape, tol: float = 0.05):
        v, f = shp.tessellate(tol)
        return [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v], [[int(i) for i in tri] for tri in f]

    step_solid = re_read.Solids[0]
    parts_json = []
    for pname, shp, col in [
        ("adapter", step_solid, [65, 130, 195]),
        ("x1c", ctx["he_placed"], [215, 95, 70]),
        ("orbiter", ctx["orb_placed"], [72, 76, 84]),
        ("ebb42", ctx["ebb_bkt"], [65, 165, 105]),
        ("fan3010", ctx["fan_3010"], [225, 165, 55]),
    ]:
        verts, faces = _tess_list(shp)
        parts_json.append({"name": pname, "color": col, "v": verts, "f": faces})

    # Slice at Y = 12.08 to reveal BOTH the smooth C2 air tunnel AND both Orbiter mount holes (-23.85 & +13.15)
    cut_y12 = step_solid.common(box(-32.0, 32.0, -12.0, 12.08, -1.0, 82.0))
    cut_he_y12 = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 12.08, -15.0, 82.0))
    cut_z16 = step_solid.common(box(-32.0, 32.0, -12.0, 32.0, -1.0, 16.50))
    cut_he_z16 = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 32.0, -15.0, 16.50))
    cut_front = step_solid.common(box(-32.0, 32.0, -12.0, 23.00, -1.0, 38.0))
    cut_he_front = ctx["he_placed"].common(box(-32.0, 32.0, -12.0, 23.00, -15.0, 38.0))

    cuts_payload = {}
    for cname, ad_s, he_s in [
        ("cut_y11", cut_y12, cut_he_y12),
        ("cut_z16", cut_z16, cut_he_z16),
        ("cut_y23", cut_front, cut_he_front),
    ]:
        va, fa = _tess_list(ad_s)
        vh, fh = _tess_list(he_s)
        assert len(va) > 0, f"Cutaway {cname} adapter mesh empty!"
        cuts_payload[cname] = [
            {"name": "adapter", "color": [65, 130, 195], "v": va, "f": fa},
            {"name": "x1c", "color": [215, 95, 70], "v": vh, "f": fh},
        ]

    (OUT_DIR / "preview_primary_r5.json").write_text(json.dumps(parts_json), encoding="utf-8")
    (OUT_DIR / "preview_cutaways_r5.json").write_text(json.dumps(cuts_payload), encoding="utf-8")

    rep = ctx["report"]
    mbb = mchk.BoundBox
    rep["stl"] = {
        "file": stl_p.name,
        "facets": int(mchk.CountFacets),
        "is_solid": bool(mchk.isSolid()),
        "has_non_manifolds": bool(mchk.hasNonManifolds()),
        "volume_mm3": round(float(mchk.Volume), 2),
        "stl_vs_step_volume_rel_diff": round(vol_err, 6),
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
    print("Building Primary_R5 (smooth C2 BSpline air tunnel + perpendicular +X nut boss)...", flush=True)
    solid, ctx = build_primary_r5(refs)
    rep = export_verified(solid, ctx)
    cols = rep["collisions_mm3"]
    assert all(v < 1e-3 for v in cols.values()), f"Collision detected: {cols}"
    fan_obs = rep["fan_3010_mounting_holes_obstruction_mm3"]
    assert all(v < 1e-3 for v in fan_obs.values()), f"3010 fan hole blocked: {fan_obs}"
    ebb_obs = rep["ebb42_top_mounting_bores_obstruction_mm3"]
    assert all(v < 1e-3 for v in ebb_obs.values()), f"EBB42 top bore blocked: {ebb_obs}"
    holes = rep["carriage_holes_4_blind_verification"]
    assert all(h["hidden_from_front"] for h in holes.values()), f"Blind carriage hole failed: {holes}"
    mp = rep["motor_portal_verification"]
    assert mp["circle_core_obstruction_mm3"] < 1e-3, f"Motor circle obstructed: {mp}"
    assert mp["top_bridge_solid_fraction"] > 0.99, f"Top bridge gap detected: {mp}"
    assert mp["left_column_solid_fraction"] > 0.99 and mp["right_column_solid_fraction"] > 0.99, f"Column gap: {mp}"
    duct_chk = rep["duct_core_solid_fraction_should_be_zero"]
    assert all(v < 1e-3 for v in duct_chk.values()), f"Duct core blocked: {duct_chk}"
    walls = rep["duct_wall_integrity_should_be_one"]
    assert all(v > 0.99 for v in walls.values()), f"Duct wall thinned/breached: {walls}"
    nb = rep["right_extruder_nut_boss_verification"]
    assert nb["boss_annulus_solid_fraction"] > 0.99, f"Right nut boss incomplete: {nb}"
    assert nb["underside_clearance_obstruction_mm3"] < 1e-3, f"Right nut boss underside obstructed: {nb}"
    assert nb["through_bore_obstruction_mm3"] < 1e-3, f"Right nut boss through-bore obstructed: {nb}"
    print("R5 BUILD & CAD VALIDATION PASSED CLEANLY.")


if __name__ == "__main__":
    main()
