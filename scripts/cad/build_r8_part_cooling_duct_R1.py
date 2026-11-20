"""Build shifted dual-horn part-cooling blower shroud & nozzle duct for BambuMod x Orbiter v2.5 R8.

Attaches below Orbiter v2.5 onto R8's front face using Kirill's two Ø5.1 mm magnets at display
(±24.50, -30.04, +3.35 mm), preserves Kirill's tested front radial blower cavity for the stock
AD5M blower assembly, and routes airflow symmetrically around the +6.335 mm X-shifted X1C
hotend (nozzle tip at display (+6.335, -11.78, -28.23 mm)).
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[2]
R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP_PATH = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE_DIR = R8_DIR / "cache"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_R1"
STEP_PATH = OUT_DIR / "R8_PartCooling_Duct_R1.step"
STL_PATH = OUT_DIR / "R8_PartCooling_Duct_R1.stl"
REPORT_PATH = OUT_DIR / "r8_fanduct_report.json"

# R8 shifted hotend & mounting datums in display coords (-Y = Front, +Y = Back, +Z = Up)
DZ_SHIFT = -14.65
X_FIL_DISP = 6.335
Y_FIL_DISP = -12.08
Z_NOZZLE_DISP = -28.23
NOZZLE_TIP = App.Vector(X_FIL_DISP, -11.78, Z_NOZZLE_DISP)

WALL_T = 1.40
MAGNET_POSITIONS = [(-24.50, -32.14, 3.35), (24.50, -32.14, 3.35)]
MAGNET_R = 2.60       # Ø5.20 mm bore for press/glue fit of 5x2 / 5x3 mm magnets
MAGNET_DEPTH = 2.35


def make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    """Create an axis-aligned solid box."""
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def make_rounded_rect_y(cx: float, cz: float, width: float, height: float, corner_r: float, y0: float, y1: float) -> Part.Shape:
    """Extrude a rounded-corner XZ rectangle along +Y."""
    hw, hh = width * 0.5, height * 0.5
    r = max(0.2, min(corner_r, hw - 0.05, hh - 0.05))
    d = r * (1.0 - math.sqrt(0.5))
    p1 = App.Vector(cx - hw + r, y0, cz + hh)
    p2 = App.Vector(cx + hw - r, y0, cz + hh)
    p3 = App.Vector(cx + hw, y0, cz + hh - r)
    p4 = App.Vector(cx + hw, y0, cz - hh + r)
    p5 = App.Vector(cx + hw - r, y0, cz - hh)
    p6 = App.Vector(cx - hw + r, y0, cz - hh)
    p7 = App.Vector(cx - hw, y0, cz - hh + r)
    p8 = App.Vector(cx - hw, y0, cz + hh - r)
    wire = Part.Wire([
        Part.LineSegment(p1, p2).toShape(),
        Part.Arc(p2, App.Vector(cx + hw - d, y0, cz + hh - d), p3).toShape(),
        Part.LineSegment(p3, p4).toShape(),
        Part.Arc(p4, App.Vector(cx + hw - d, y0, cz - hh + d), p5).toShape(),
        Part.LineSegment(p5, p6).toShape(),
        Part.Arc(p6, App.Vector(cx - hw + d, y0, cz - hh + d), p7).toShape(),
        Part.LineSegment(p7, p8).toShape(),
        Part.Arc(p8, App.Vector(cx - hw + d, y0, cz + hh - d), p1).toShape(),
    ])
    return Part.Face(wire).extrude(App.Vector(0.0, y1 - y0, 0.0))


def _load_r8_refs() -> dict[str, Part.Shape]:
    """Load R8_Adapter and display-oriented reference solids."""
    r8 = Part.Shape()
    r8.read(str(R8_STEP_PATH))

    def read_rot(fname: str, z_shift: float = 0.0) -> Part.Shape:
        sh = Part.Shape()
        sh.read(str(R8_CACHE_DIR / fname))
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


def _make_xy_capsule(x0: float, y0: float, x1: float, y1: float, radius: float, z0: float, z1: float) -> Part.Shape:
    """Extrude a rounded stadium/capsule between (x0, y0) and (x1, y1) vertically along +Z."""
    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist < 1e-5:
        return Part.makeCylinder(radius, z1 - z0, App.Vector(x0, y0, z0), App.Vector(0.0, 0.0, 1.0))
    ux, uy = dx / dist, dy / dist
    nx, ny = -uy, ux
    p1 = App.Vector(x0 + nx * radius, y0 + ny * radius, z0)
    p2 = App.Vector(x1 + nx * radius, y1 + ny * radius, z0)
    p3 = App.Vector(x1 - nx * radius, y1 - ny * radius, z0)
    p4 = App.Vector(x0 - nx * radius, y0 - ny * radius, z0)
    mid1 = App.Vector(x1 + ux * radius, y1 + uy * radius, z0)
    mid2 = App.Vector(x0 - ux * radius, y0 - uy * radius, z0)
    wire = Part.Wire([
        Part.LineSegment(p1, p2).toShape(),
        Part.Arc(p2, mid1, p3).toShape(),
        Part.LineSegment(p3, p4).toShape(),
        Part.Arc(p4, mid2, p1).toShape(),
    ])
    return Part.Face(wire).extrude(App.Vector(0.0, 0.0, z1 - z0))


def _make_xy_duct_polygon(pts_2d: list[tuple[float, float]], corner_r: float, offset_r: float, z0: float, z1: float) -> Part.Shape:
    """Create a smooth rounded planar polygon extruded along +Z cleanly with makeOffset2D."""
    vecs = [App.Vector(x, y, z0) for x, y in pts_2d] + [App.Vector(pts_2d[0][0], pts_2d[0][1], z0)]
    wire = Part.makePolygon(vecs)
    face = Part.Face(wire)
    if corner_r > 0.05:
        face = face.makeOffset2D(corner_r, 0, False, False, False)
        face = face.makeOffset2D(-corner_r, 0, False, False, False)
    if abs(offset_r) > 1e-4:
        face = face.makeOffset2D(offset_r, 0, False, False, False)
    return face.extrude(App.Vector(0.0, 0.0, z1 - z0))


def _build_analytical_blower_shroud() -> tuple[Part.Shape, Part.Shape]:
    """Build clean analytical lower AD5M radial blower shroud matching R8's front face.

    Returns (shroud_solid, exhaust_throat_void).
    Flat front outer face at Y=-44.24 prints directly on the build plate without supports while
    providing 14.20 mm internal blower depth (Y=-42.74..-30.04), Ø5.20 mm magnet pockets at
    (±24.50, -32.14, +3.35), outer flank guide rails, chin locator, and 21.5 x 6.5 mm exhaust.
    """
    outer = make_rounded_rect_y(0.0, -0.975, 60.0, 36.35, 2.5, -44.24, -30.04)

    # Outer flank guide rails anchored solidly into outer (Y=-34..-30.04) and hugging R8 outside |X|>=30.15
    rail_l = make_box(29.00, 31.75, -34.00, -30.04, -8.80, 9.50).fuse(
        make_box(30.15, 31.75, -30.50, -26.80, -8.80, 9.50)
    )
    rail_r = make_box(-31.75, -29.00, -34.00, -30.04, -8.80, 9.50).fuse(
        make_box(-31.75, -30.15, -30.50, -26.80, -8.80, 9.50)
    )
    # Lower chin lip anchored into shroud bottom (-35..-30.04) and catching under R8 chin (Z=-11.30..-9.30)
    chin_lip = make_box(-27.0, 27.0, -35.00, -26.50, -11.30, -9.30)
    outer = outer.fuse(rail_l).fuse(rail_r).fuse(chin_lip)

    # 12.70 mm internal blower cavity behind 1.50 mm flat front skin (Y=-42.74..-30.04)
    pocket_main = make_rounded_rect_y(0.0, -0.70, 52.0, 33.4, 2.0, -42.74, -29.50)
    intake = make_rounded_rect_y(0.0, -3.50, 28.0, 11.5, 5.7, -45.00, -42.00)
    top_arch = make_rounded_rect_y(0.0, 15.0, 32.0, 7.0, 3.5, -44.80, -29.50)

    # Magnet pads stop cleanly at Y = -32.15 (0.11 mm clear of R8's protruding Ø6.7 mm magnet boss rings)
    # Use circular R=3.60 bosses bridged to outer wall (±24.5..±30.0) so blower cavity stays maximally open
    mag_boss_l = (
        Part.makeCylinder(3.60, 3.10, App.Vector(24.50, -35.25, 3.35), App.Vector(0.0, 1.0, 0.0))
        .fuse(make_box(24.50, 30.00, -35.25, -32.15, -0.25, 6.95))
    )
    mag_boss_r = (
        Part.makeCylinder(3.60, 3.10, App.Vector(-24.50, -35.25, 3.35), App.Vector(0.0, 1.0, 0.0))
        .fuse(make_box(-30.00, -24.50, -35.25, -32.15, -0.25, 6.95))
    )

    shroud = outer.cut(pocket_main).cut(intake).cut(top_arch)
    # Trim Y = -32.15..-30.04 around R8's protruding magnet boss rings (R=3.60) + +X wire slot relief
    for mx, _my, mz in MAGNET_POSITIONS:
        boss_clear = Part.makeCylinder(3.65, 2.50, App.Vector(mx, -32.15, mz), App.Vector(0.0, 1.0, 0.0))
        shroud = shroud.cut(boss_clear)
    wire_relief = make_box(12.50, 21.50, -33.00, -29.50, 10.50, 17.50)
    shroud = shroud.cut(wire_relief)

    shroud = shroud.fuse(mag_boss_l).fuse(mag_boss_r)

    for mx, my, mz in MAGNET_POSITIONS:
        mp = Part.makeCylinder(MAGNET_R, MAGNET_DEPTH + 0.4, App.Vector(mx, my + 0.2, mz), App.Vector(0.0, -1.0, 0.0))
        shroud = shroud.cut(mp)

    throat_void = make_box(-22.50, -1.00, -40.54, -34.04, -20.50, -16.00)
    shroud = shroud.cut(throat_void)
    return shroud, throat_void


def _build_shifted_dual_horn_duct() -> tuple[Part.Shape, Part.Shape]:
    """Build twist-free planar plenum, Y-splitter, and symmetric tilted cooling horns around shifted nozzle."""
    # 1. Drop collar directly beneath blower exhaust (-22.50..-1.00, -40.54..-34.04) down to plenum floor
    z_plenum_bot = -25.40
    z_plenum_top = -19.00
    z_void_bot = z_plenum_bot + WALL_T   # -24.00
    z_void_top = z_plenum_top - WALL_T   # -20.40 -> 3.60 mm tall channel

    drop_outer = make_box(-22.50 - WALL_T, -1.00 + WALL_T, -40.54 - WALL_T, -34.04 + WALL_T, z_plenum_bot, -18.50)
    drop_void = make_box(-22.50, -1.00, -40.54, -34.04, z_void_bot, -16.50)

    # 2. Smooth sweeping plenum from blower drop (-22.5..-1.0, -40.54..-34.04) to centered Y-splitter
    #    at (X_FIL_DISP = +6.335, Y = -21.50) built from two smooth overlapping planar capsules:
    #    Radius = 5.0 mm inner / 6.4 mm outer keeps gentle sweep and generous cross-section.
    r_arm_in = 3.20
    r_arm_out = r_arm_in + WALL_T
    # Sweeping transfer manifold from left/right ends of blower chute toward centered splitter bar
    # Build two smooth wide channels across the plenum path so airflow shifts cleanly without choke:
    plenum_in = (
        _make_xy_capsule(-18.50, -37.29, X_FIL_DISP - 5.50, -23.00, r_arm_in, z_void_bot, z_void_top)
        .fuse(_make_xy_capsule(-5.00, -37.29, X_FIL_DISP + 5.50, -23.00, r_arm_in, z_void_bot, z_void_top))
        .fuse(make_box(-22.50, -1.00, -40.54, -34.04, z_void_bot, z_void_top))
        .fuse(_make_xy_capsule(X_FIL_DISP - 5.50, -23.00, X_FIL_DISP + 5.50, -23.00, r_arm_in, z_void_bot, z_void_top))
    )
    plenum_out = (
        _make_xy_capsule(-18.50, -37.29, X_FIL_DISP - 5.50, -23.00, r_arm_out, z_plenum_bot, z_plenum_top)
        .fuse(_make_xy_capsule(-5.00, -37.29, X_FIL_DISP + 5.50, -23.00, r_arm_out, z_plenum_bot, z_plenum_top))
        .fuse(make_box(-22.50 - WALL_T, -1.00 + WALL_T, -40.54 - WALL_T, -34.04 + WALL_T, z_plenum_bot, z_plenum_top))
        .fuse(_make_xy_capsule(X_FIL_DISP - 5.50, -23.00, X_FIL_DISP + 5.50, -23.00, r_arm_out, z_plenum_bot, z_plenum_top))
    )

    # 3. Mirror-symmetric Left (+X) and Right (-X) cooling horns around hotend sock keepout (X=2.3..10.5)
    # Inner flank & tip keep >= 2.8 mm bare heater-block clearance (>= 1.3 mm past silicone sock)
    def build_horn(side: float) -> tuple[Part.Shape, Part.Shape]:
        x_split = X_FIL_DISP + side * 5.80
        y_split = -23.00
        x_elbow = X_FIL_DISP + side * 13.40
        y_elbow = -17.50
        x_side = X_FIL_DISP + side * 13.40
        y_side = -11.78
        x_tip = X_FIL_DISP + side * 10.60
        y_tip = -11.78

        # Horizontal arms connecting splitter -> elbow -> nozzle flank (keeping outer Z=-25.40..-19.00)
        arm1_out = _make_xy_capsule(x_split, y_split, x_elbow, y_elbow, r_arm_out, z_plenum_bot, z_plenum_top)
        arm2_out = _make_xy_capsule(x_elbow, y_elbow, x_side, y_side, r_arm_out, z_plenum_bot, z_plenum_top)
        arm1_in = _make_xy_capsule(x_split, y_split, x_elbow, y_elbow, r_arm_in, z_void_bot, z_void_top)
        arm2_in = _make_xy_capsule(x_elbow, y_elbow, x_side, y_side, r_arm_in, z_void_bot, z_void_top)

        # Short inward-sloped nozzle tip lofted linearly between two planar YZ-aligned sections (zero twist!)
        def make_yz_rect(xc: float, zc: float, y_len: float, z_h: float, rc: float) -> Part.Wire:
            hy, hz = y_len * 0.5, z_h * 0.5
            r = max(0.25, min(rc, hy - 0.1, hz - 0.1))
            d = r * (1.0 - math.sqrt(0.5))
            yc = y_side
            p1 = App.Vector(xc, yc - hy + r, zc + hz)
            p2 = App.Vector(xc, yc + hy - r, zc + hz)
            p3 = App.Vector(xc, yc + hy, zc + hz - r)
            p4 = App.Vector(xc, yc + hy, zc - hz + r)
            p5 = App.Vector(xc, yc + hy - r, zc - hz)
            p6 = App.Vector(xc, yc - hy + r, zc - hz)
            p7 = App.Vector(xc, yc - hy, zc - hz + r)
            p8 = App.Vector(xc, yc - hy, zc + hz - r)
            return Part.Wire([
                Part.LineSegment(p1, p2).toShape(),
                Part.Arc(p2, App.Vector(xc, yc + hy - d, zc + hz - d), p3).toShape(),
                Part.LineSegment(p3, p4).toShape(),
                Part.Arc(p4, App.Vector(xc, yc + hy - d, zc - hz + d), p5).toShape(),
                Part.LineSegment(p5, p6).toShape(),
                Part.Arc(p6, App.Vector(xc, yc - hy + d, zc - hz + d), p7).toShape(),
                Part.LineSegment(p7, p8).toShape(),
                Part.Arc(p8, App.Vector(xc, yc - hy + d, zc + hz - d), p1).toShape(),
            ])

        tip_out = Part.makeLoft([
            make_yz_rect(x_side, 0.5 * (z_plenum_bot + z_plenum_top), 2.0 * r_arm_out, z_plenum_top - z_plenum_bot, 1.2),
            make_yz_rect(x_tip, -23.90, 7.6 + 2.0 * WALL_T, 3.0 + 2.0 * WALL_T, 1.0),
        ], True, True)
        # Void extends 3.2 mm past tip toward nozzle so outlet is guaranteed cut open cleanly
        tip_in = Part.makeLoft([
            make_yz_rect(x_side + side * 0.5, 0.5 * (z_void_bot + z_void_top), 2.0 * r_arm_in, z_void_top - z_void_bot, 0.8),
            make_yz_rect(x_tip - side * 2.8, -25.15, 7.6, 2.8, 0.6),
        ], True, True)

        return arm1_out.fuse(arm2_out).fuse(tip_out), arm1_in.fuse(arm2_in).fuse(tip_in)

    left_outer, left_void = build_horn(+1.0)
    right_outer, right_void = build_horn(-1.0)

    outer_all = drop_outer.fuse(plenum_out).fuse(left_outer).fuse(right_outer)
    void_all = drop_void.fuse(plenum_in).fuse(left_void).fuse(right_void)
    return outer_all, void_all


def build_part_cooling_duct() -> dict:
    """Build R8_PartCooling_Duct_R1, export STEP/STL, and run full interference checks."""
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = _load_r8_refs()

    shroud, throat_void = _build_analytical_blower_shroud()
    duct_outer, duct_void = _build_shifted_dual_horn_duct()

    full_void = throat_void.fuse(duct_void)
    part = shroud.fuse(duct_outer).cut(full_void)

    bed_safety = make_box(-50.0, 50.0, -60.0, 10.0, -38.00, Z_NOZZLE_DISP + 2.00)
    part = part.cut(bed_safety)

    solids = [s for s in part.Solids if s.Volume >= 10.0]
    if len(solids) == 1:
        part = solids[0]
    elif solids:
        part = solids[0].multiFuse(solids[1:])

    part.exportStep(str(STEP_PATH))

    mesh = MeshPart.meshFromShape(Shape=part, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False)
    mesh.write(str(STL_PATH))
    mesh_reload = Mesh.Mesh(str(STL_PATH))

    def common_vol(other: Part.Shape) -> float:
        if not part.BoundBox.intersect(other.BoundBox):
            return 0.0
        try:
            cm = part.common(other)
            return round(cm.Volume, 3) if not cm.isNull() else 0.0
        except Part.OCCError:
            return -1.0

    def min_dist(other: Part.Shape) -> float:
        try:
            return round(part.distToShape(other)[0], 3)
        except Exception:
            return -1.0

    checks = {
        "duct_vs_r8_adapter_mm3": common_vol(refs["r8"]),
        "duct_vs_orbiter_mm3": common_vol(refs["orbiter"]),
        "duct_vs_x1c_hotend_mm3": common_vol(refs["hotend"]),
        "duct_vs_3010_fan_mm3": common_vol(refs["fan3010"]),
        "duct_vs_gray_carriage_mm3": common_vol(refs["carriage"]),
        "min_dist_to_hotend_mm": min_dist(refs["hotend"]),
        "min_dist_to_orbiter_mm": min_dist(refs["orbiter"]),
    }

    report = {
        "nozzle_target_display_mm": [round(NOZZLE_TIP.x, 3), round(NOZZLE_TIP.y, 3), round(NOZZLE_TIP.z, 3)],
        "magnet_mounts_display_mm": [list(p) for p in MAGNET_POSITIONS],
        "bbox": {
            "x": [round(part.BoundBox.XMin, 3), round(part.BoundBox.XMax, 3)],
            "y": [round(part.BoundBox.YMin, 3), round(part.BoundBox.YMax, 3)],
            "z": [round(part.BoundBox.ZMin, 3), round(part.BoundBox.ZMax, 3)],
        },
        "nozzle_bed_clearance_mm": round(part.BoundBox.ZMin - Z_NOZZLE_DISP, 3),
        "volume_mm3": round(part.Volume, 2),
        "brep_valid": bool(part.isValid()),
        "solid_count": len(part.Solids),
        "stl_facets": int(mesh_reload.CountFacets),
        "stl_non_manifolds": bool(mesh_reload.hasNonManifolds()),
        "stl_non_uniform_faces": int(mesh_reload.countNonUniformOrientedFacets()),
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"[FanDuct R1] Built in {report['build_seconds']}s | vol={report['volume_mm3']} | "
        f"solids={report['solid_count']} valid={report['brep_valid']} | "
        f"bed_clear={report['nozzle_bed_clearance_mm']}mm | stl_nm={report['stl_non_manifolds']} | "
        f"checks={checks}"
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_part_cooling_duct()
