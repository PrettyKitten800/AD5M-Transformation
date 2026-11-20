"""
Build the -20.0 mm Full-Slim AD5M Dragon Burner (#1406257) Adapter + Reverse-Orbiter
Mount Pack (R1) for Sensorless Homing Builds, WITH #1406257's original bottom/upper
fan-shroud screwhole ear tabs (Y = -44.16 .. -33.30) completely preserved.

Generates verified single-solid manifold STLs & STEPs in
outputs/Dragon_Burner_AD5M_Slim_20mm_R1/:
  1. AD5M_Dragon_Burner_Slim_20mm_Adapter_R1.{stl,step}
     - Removes the full 20.0 mm unused prismatic spacer Z=[3.45, 23.45] from #1406257
       (Z_mount: 33.40 -> 13.40 mm; Nozzle Z: 44.697 -> 24.697 mm, just +1.500 mm
       ahead of stock/AD5M_Custom_Housing_R1's 23.197 mm).
     - Preserves BOTH #1406257 fan-shroud screwhole tabs (Y=-44.16..-33.30, Z=3.45..8.90).
       (Requires Reverse-Orbiter front-motor orientation; a regular rear-motor Orbiter
       collides into the restored shroud tabs by ~459 mm3.)
     - Fuses compact R=4.0 mm backing bosses (Z=2.95..7.00, Y<=-44.16) behind the
       upper carriage bolt holes UL/UR so rear M3 screws retain solid 4.0 mm backing
       without intruding into the open central bay.
     - Bakes in anti-warp 45-deg corner chamfers on all 4 bed-contact corners:
       5.0x5.0 mm vertical XY chamfers on bottom-left/bottom-right, and 4.5 mm
       45-deg lofted tapered chamfers on top-left/top-right (preserving Z>=3.45 tabs).
  2. Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1.{stl,step}
  3. Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1.{stl,step}
"""

from __future__ import annotations

import json
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
OUT_DIR = ROOT / "outputs/Dragon_Burner_AD5M_Slim_20mm_R1"

TRIM_MM = 20.000
ORIG_NOZZLE = (34.924, -138.401, 44.697)
SLIM_NOZZLE = (34.924, -138.401, 44.697 - TRIM_MM)   # Z = 24.697 mm
SLIM_MOUNT_Z = 33.400 - TRIM_MM                       # Z = 13.400 mm
CARRIAGE_BOTTOM_Y = SLIM_NOZZLE[1] + 13.600           # -124.801 mm


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def load_1406257_solid() -> Part.Shape:
    m = Mesh.Mesh(str(REF_1406))
    sh = Part.Shape()
    sh.makeShapeFromMesh(m.Topology, 0.05)
    s = Part.makeSolid(sh).removeSplitter()
    assert s.isValid() and len(s.Solids) == 1, "Base #1406257 STL failed solid conversion"
    return s


def _xy_corner_chamfer_cutter(cx: float, cy: float, sx: float, sy: float, c: float) -> Part.Shape:
    """Create a vertical 45-deg XY corner cutter passing through (cx+sx*c, cy) and (cx, cy+sy*c)."""
    p0 = App.Vector(cx - sx * 2.0, cy - sy * 2.0, -2.0)
    p1 = App.Vector(cx + sx * (c + 2.0), cy - sy * 2.0, -2.0)
    p2 = App.Vector(cx - sx * 2.0, cy + sy * (c + 2.0), -2.0)
    return Part.Face(Part.makePolygon([p0, p1, p2, p0])).extrude(App.Vector(0.0, 0.0, 30.0))


def _tapered_corner_chamfer_cutter(cx: float, cy: float, sx: float, sy: float,
                                    c_bed: float = 4.5, c_top: float = 0.05,
                                    z_bed: float = 0.0, z_top: float = 4.45) -> Part.Shape:
    """
    Create a 45-deg self-supporting tapered triangle loft cutter that trims a c_bed x c_bed
    triangle at Z=0 and tapers inward at 45 deg up to Z=z_top, leaving upper tabs untouched.
    """
    z0 = z_bed - 0.5
    c0 = c_bed + (z_bed - z0) * ((c_bed - c_top) / (z_top - z_bed))

    def _tri(z: float, c: float) -> Part.Wire:
        p0 = App.Vector(cx - sx * 2.0, cy - sy * 2.0, z)
        p1 = App.Vector(cx + sx * (c + 2.0), cy - sy * 2.0, z)
        p2 = App.Vector(cx - sx * 2.0, cy + sy * (c + 2.0), z)
        return Part.makePolygon([p0, p1, p2, p0])

    return Part.makeLoft([_tri(z0, c0), _tri(z_top, c_top)], True, False)


def build_slim_20mm_adapter(base: Part.Shape) -> Part.Shape:
    """
    Cut full 20.0 mm from Z=[3.45, 23.45] spacer while keeping both original #1406257
    fan-shroud screwhole tabs (Y=-44.16..-33.30), reinforce UL/UR carriage screw pockets
    with R=4.0 mm backing bosses (Z=2.95..7.00), and bevel all 4 bed-contact corners.
    """
    split_z_rear = 3.450
    split_z_front = split_z_rear + TRIM_MM  # 23.450

    rear_part = base.common(box(-50.0, 150.0, -200.0, 50.0, -5.0, split_z_rear))
    front_part = base.common(box(-50.0, 150.0, -200.0, 50.0, split_z_front, 60.0))
    front_part.translate(App.Vector(0.0, 0.0, -TRIM_MM))

    # Fuse UL/UR R=4.0 mm backing bosses (Z=2.95..7.00, Y<=-44.16) so Z=0..2.95 rear screw
    # pockets keep >= 4.0 mm solid plastic backing instead of punching through at Z=3.45.
    boss_ul = Part.makeCylinder(4.0, 4.05, App.Vector(15.302, -47.700, 2.95)).common(
        box(9.0, 21.0, -53.0, -44.16, 2.95, 7.00)
    )
    boss_ur = Part.makeCylinder(4.0, 4.05, App.Vector(54.503, -47.700, 2.95)).common(
        box(49.0, 61.0, -53.0, -44.16, 2.95, 7.00)
    )

    slim = rear_part.fuse(front_part).fuse(boss_ul).fuse(boss_ur).removeSplitter()

    # Anti-warp chamfers at Z=0 on all 4 outer corners:
    # - BL / BR: vertical 5.0 x 5.0 mm XY chamfers (clear of M3 bolts & shroud feet)
    # - TL / TR: 3.45 mm 45-deg tapered chamfers ending at Z=3.40 (zero impact on Z>=3.45 shroud tabs)
    corner_cuts = (
        _xy_corner_chamfer_cutter(4.902, -124.300, +1.0, +1.0, 5.0)
        .fuse(_xy_corner_chamfer_cutter(64.899, -124.300, -1.0, +1.0, 5.0))
        .fuse(_tapered_corner_chamfer_cutter(4.902, -44.150, +1.0, -1.0, c_bed=3.45, c_top=0.05, z_bed=0.0, z_top=3.40))
        .fuse(_tapered_corner_chamfer_cutter(64.899, -44.150, -1.0, -1.0, c_bed=3.45, c_top=0.05, z_bed=0.0, z_top=3.40))
    )
    slim = slim.cut(corner_cuts).removeSplitter()

    assert slim.isValid() and len(slim.Solids) == 1, "Slim 20mm adapter is not a single valid solid!"
    return slim.Solids[0]


def build_reverse_orbiter_mounts():
    """
    Build Bambu_Mount_ReverseOrbiter and Orbiter2_Mount_ReverseOrbiter from
    Dragon_Burner_v0.2_v8_reference.step positioned in the -20.0 mm Slim frame.
    """
    doc = App.newDocument("DBRefTmp20")
    Import.insert(str(REF_DB_STEP), doc.Name)
    db_main_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "MainBody"][0]
    bm_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Bambu_Mount (2)"][0]
    om_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Orbiter2_Mount (4)"][0]
    duct_r_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Standard (1)"][0]
    App.closeDocument(doc.Name)

    FIL_X = 330.100
    FIL_Y = -155.235
    TOP_Z = 109.500

    orig_L_x = FIL_X - 19.51
    orig_R_x = FIL_X + 17.49
    mirr_L_x = FIL_X - 17.49
    mirr_R_x = FIL_X + 19.51

    plug_L = Part.makeCylinder(2.45, 5.80, App.Vector(orig_L_x, FIL_Y, 103.75))
    plug_R = Part.makeCylinder(2.45, 5.80, App.Vector(orig_R_x, FIL_Y, 103.75))
    boss_L = Part.makeCylinder(3.85, 5.00, App.Vector(mirr_L_x, FIL_Y, 104.50))

    hole_L = Part.makeCylinder(2.35, 5.20, App.Vector(mirr_L_x, FIL_Y, 104.40))
    hole_R = Part.makeCylinder(2.35, 5.20, App.Vector(mirr_R_x, FIL_Y, 104.40))
    top_trim_flat = box(295.0, 365.0, -172.0, -138.0, TOP_Z, TOP_Z + 2.0)

    bm_rev_raw = (
        bm_raw.fuse(plug_L)
        .fuse(plug_R)
        .fuse(boss_L)
        .cut(hole_L.fuse(hole_R).fuse(top_trim_flat))
        .removeSplitter()
    )
    assert bm_rev_raw.isValid() and len(bm_rev_raw.Solids) == 1, "Bambu_Mount_Reverse invalid"

    wall_metrics = {}
    for lbl, hx in (("mirr_L", mirr_L_x), ("mirr_R", mirr_R_x)):
        ring = Part.makeCylinder(3.85, 4.80, App.Vector(hx, FIL_Y, 104.60)).cut(
               Part.makeCylinder(2.35, 4.80, App.Vector(hx, FIL_Y, 104.60)))
        wall_metrics[lbl] = round(bm_rev_raw.common(ring).Volume / ring.Volume, 4)

    om_rev_raw = om_raw.copy()
    om_rev_raw.rotate(App.Vector(FIL_X, FIL_Y, 0.0), App.Vector(0, 0, 1), 180.0)
    assert om_rev_raw.isValid() and len(om_rev_raw.Solids) == 1, "Orbiter2_Mount_Reverse invalid"

    def main_step_to_slim(sh: Part.Shape) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
        out.translate(App.Vector(34.9065 - 147.877, -86.681 - 102.550, 33.400 - 119.462 - TRIM_MM))
        return out

    def bm2_to_slim(sh: Part.Shape) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
        out.translate(App.Vector(SLIM_NOZZLE[0] - FIL_X, -79.717 - TOP_Z, SLIM_NOZZLE[2] + 0.010 - (-FIL_Y)))
        return out

    hot_raw = Part.read(str(REF_HOTEND_STEP))
    hot = Part.makeCompound(hot_raw.Solids)
    hot.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
    hot.translate(App.Vector(147.895, -130.759, 95.130 - 40.300))
    hot_slim = main_step_to_slim(hot)

    bm_rev_print = bm_rev_raw.copy()
    bm_rev_print.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    bb_p = bm_rev_print.BoundBox
    bm_rev_print.translate(App.Vector(-FIL_X, -((bb_p.YMin + bb_p.YMax) / 2.0), -143.929))

    om_rev_print = om_rev_raw.copy()
    bb_o = om_rev_print.BoundBox
    om_rev_print.translate(App.Vector(-FIL_X, -FIL_Y, -bb_o.ZMin))

    return {
        "bm_orig_slim": bm2_to_slim(bm_raw),
        "om_orig_slim": bm2_to_slim(om_raw),
        "bm_rev_slim": bm2_to_slim(bm_rev_raw),
        "om_rev_slim": bm2_to_slim(om_rev_raw),
        "bm_rev_print": bm_rev_print.Solids[0],
        "om_rev_print": om_rev_print.Solids[0],
        "db_main_slim": main_step_to_slim(db_main_raw),
        "duct_r_slim": main_step_to_slim(duct_r_raw),
        "hotend_slim": hot_slim,
        "wall_metrics": wall_metrics,
    }


def make_orbiter_25_envelope(reverse: bool) -> dict[str, Part.Shape]:
    """
    Approximate Orbiter v2.0/v2.5 physical envelope aligned to filament center
    (SLIM_NOZZLE[0], Y_base=-72.817, SLIM_NOZZLE[2] + 0.010) from published
    51x49.5x46.9 mm body + Ø36x20 mm LDO-36STH20-1004AHG motor geometry.
    """
    fx, fy_base, fz = SLIM_NOZZLE[0], -72.817, SLIM_NOZZLE[2] + 0.010
    motor_z0 = fz + (0.0 if reverse else -20.0)
    motor_cyl = Part.makeCylinder(18.0, 20.0, App.Vector(fx, fy_base + 25.0, motor_z0), App.Vector(0, 0, 1))

    z_a = fz - 12.0 if reverse else fz - 8.0
    z_b = fz + 8.0 if reverse else fz + 12.0
    gearbox = box(fx - 24.75, fx + 24.75, fy_base, fy_base + 47.0, min(z_a, z_b), max(z_a, z_b))
    return {"motor": motor_cyl, "gearbox": gearbox, "all": motor_cyl.fuse(gearbox)}


def export_stl_and_step(solid: Part.Shape, stem: str, repair_step_seam: bool = False) -> dict:
    step_p = OUT_DIR / f"{stem}.step"
    stl_p = OUT_DIR / f"{stem}.stl"
    solid.exportStep(str(step_p))
    mesh = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.035, AngularDeflection=0.14, Relative=False)
    if repair_step_seam:
        mesh.removeDuplicatedPoints()
        mesh.fillupHoles(200)
        mesh.harmonizeNormals()
        mbb = mesh.BoundBox
        mesh.translate(0.0, 0.0, -mbb.ZMin)
    mesh.write(str(stl_p))
    assert mesh.isSolid() and not mesh.hasNonManifolds(), f"{stl_p.name} failed manifold solidity!"
    bb = mesh.BoundBox
    return {
        "stl": stl_p.name,
        "step": step_p.name,
        "valid_brep": bool(solid.isValid()),
        "solids": len(solid.Solids),
        "mesh_is_solid": bool(mesh.isSolid()),
        "has_non_manifolds": bool(mesh.hasNonManifolds()),
        "repaired_upstream_step_seam": repair_step_seam,
        "facets": int(mesh.CountFacets),
        "volume_mm3": round(float(mesh.Volume if repair_step_seam else solid.Volume), 2),
        "stl_bbox_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading #1406257 & building -20.0 mm Slim Adapter (restored tabs) + Reverse Orbiter Mounts...", flush=True)
    base = load_1406257_solid()
    slim_adapter = build_slim_20mm_adapter(base)
    parts = build_reverse_orbiter_mounts()

    orb_reg = make_orbiter_25_envelope(reverse=False)
    orb_rev = make_orbiter_25_envelope(reverse=True)

    # Verify restored #1406257 shroud screwhole tabs (Y=-44.14..-30.0, Z=3.45..9.50) match shifted original exactly
    tab_region = box(-50.0, 150.0, -44.14, -30.0, 3.45, 9.50)
    orig_tabs_shifted = base.common(box(-50.0, 150.0, -44.14, -30.0, 23.45, 29.50))
    orig_tabs_shifted.translate(App.Vector(0.0, 0.0, -TRIM_MM))
    slim_tabs = slim_adapter.common(tab_region)
    tab_restore_metrics = {
        "orig_shifted_tabs_volume_mm3": round(orig_tabs_shifted.Volume, 2),
        "slim_restored_tabs_volume_mm3": round(slim_tabs.Volume, 2),
        "diff_mm3": round(abs(orig_tabs_shifted.Volume - slim_tabs.Volume), 4),
    }

    steel_carriage = box(-20.0, 90.0, CARRIAGE_BOTTOM_Y, -20.0, -15.0, 0.0)
    carriage_holes = [
        ("upper_left", 15.302, -47.700),
        ("upper_right", 54.503, -47.700),
        ("lower_left", 11.302, -105.899),
        ("lower_right", 58.702, -106.000),
        ("fifth_plus14", SLIM_NOZZLE[0] + 14.00, -116.45),
        ("fifth_minus14", SLIM_NOZZLE[0] - 14.00, -116.45),
    ]
    bolt_checks = {}
    for lbl, bx, by in carriage_holes:
        if "upper" in lbl:
            rear_pocket = Part.makeCylinder(1.60, 4.80, App.Vector(bx, by, -2.0), App.Vector(0, 0, 1))
            solid_backing = Part.makeCylinder(1.60, 3.80, App.Vector(bx, by, 3.10), App.Vector(0, 0, 1))
            bolt_checks[lbl] = {
                "boss_thickness_mm": 7.00,
                "rear_pocket_Z0_to_2p8_overlap_mm3": round(slim_adapter.common(rear_pocket).Volume, 4),
                "solid_backing_Z3p1_to_6p9_mm3": round(slim_adapter.common(solid_backing).Volume, 3),
                "solid_backing_expected_mm3": round(solid_backing.Volume, 3),
            }
        else:
            corridor = Part.makeCylinder(2.75, 16.0, App.Vector(bx, by, 3.45), App.Vector(0, 0, 1))
            bolt_checks[lbl] = {"front_tool_corridor_overlap_mm3": round(slim_adapter.common(corridor).Volume, 4)}

    slot_corr = box(13.64, 55.64, -117.30, -108.30, 3.45, 14.0)
    bolt_checks["slot_42x9_front_corridor_overlap_mm3"] = round(slim_adapter.common(slot_corr).Volume, 4)

    checks = {
        "trim_depth_mm": TRIM_MM,
        "mount_z_mm": SLIM_MOUNT_Z,
        "nozzle_tip_slim_mm": list(SLIM_NOZZLE),
        "nozzle_shift_vs_stock_1406257_mm": -TRIM_MM,
        "nozzle_vs_custom_housing_r1_mm": round(SLIM_NOZZLE[2] - 23.197, 3),
        "restored_shroud_screw_tabs": tab_restore_metrics,
        "anti_warp_corner_chamfers": {
            "bottom_BL_BR_vertical_leg_mm": 5.0,
            "top_TL_TR_45deg_tapered_leg_mm": 3.45,
        },
        "carriage_bolts": bolt_checks,
        "bambu_mount_rev_mirrored_heatset_wall_fraction": parts["wall_metrics"],
        "steel_carriage_overlap_mm3": round(slim_adapter.common(steel_carriage).Volume, 6),
        "slim_vs_db_main_overlap_mm3": round(slim_adapter.common(parts["db_main_slim"]).Volume, 6),
        "slim_vs_bm_rev_overlap_mm3": round(slim_adapter.common(parts["bm_rev_slim"]).Volume, 6),
        "slim_vs_hotend_overlap_mm3": round(slim_adapter.common(parts["hotend_slim"]).Volume, 6),
        "om_rev_vs_db_main_overlap_mm3": round(parts["om_rev_slim"].common(parts["db_main_slim"]).Volume, 6),
        "om_rev_vs_slim_overlap_mm3": round(parts["om_rev_slim"].common(slim_adapter).Volume, 6),
        "duct_right_rear_clearance_to_carriage_mm": round(parts["duct_r_slim"].BoundBox.ZMin, 3),
        "regular_orbiter_motor_envelope": {
            "motor_z_span_mm": [round(orb_reg["motor"].BoundBox.ZMin, 2), round(orb_reg["motor"].BoundBox.ZMax, 2)],
            "motor_overlap_slim_adapter_mm3": round(orb_reg["motor"].common(slim_adapter).Volume, 4),
            "motor_overlap_restored_tabs_mm3": round(orb_reg["motor"].common(slim_tabs).Volume, 4),
            "motor_rear_gap_to_steel_carriage_mm": round(orb_reg["motor"].BoundBox.ZMin, 3),
        },
        "reverse_orbiter_motor_envelope": {
            "motor_z_span_mm": [round(orb_rev["motor"].BoundBox.ZMin, 2), round(orb_rev["motor"].BoundBox.ZMax, 2)],
            "gearbox_rear_z_min_mm": round(orb_rev["gearbox"].BoundBox.ZMin, 2),
            "motor_overlap_db_main_mm3": round(orb_rev["motor"].common(parts["db_main_slim"]).Volume, 4),
            "motor_overlap_slim_adapter_mm3": round(orb_rev["motor"].common(slim_adapter).Volume, 4),
            "gearbox_overlap_slim_adapter_mm3": round(orb_rev["gearbox"].common(slim_adapter).Volume, 4),
            "motor_gap_to_adapter_mm": round(orb_rev["motor"].distToShape(slim_adapter)[0], 3),
            "gearbox_rear_gap_to_adapter_wall_mm": round(orb_rev["gearbox"].distToShape(slim_adapter)[0], 3),
            "motor_front_vs_db_main_nose_mm": round(orb_rev["motor"].BoundBox.ZMax - parts["db_main_slim"].BoundBox.ZMax, 2),
            "total_toolhead_front_z_mm": round(max(orb_rev["motor"].BoundBox.ZMax, parts["duct_r_slim"].BoundBox.ZMax), 2),
        },
    }

    exports = {
        "slim_adapter": export_stl_and_step(slim_adapter, "AD5M_Dragon_Burner_Slim_20mm_Adapter_R1"),
        "bambu_mount_reverse": export_stl_and_step(
            parts["bm_rev_print"], "Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1", repair_step_seam=True
        ),
        "orbiter2_mount_reverse": export_stl_and_step(parts["om_rev_print"], "Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1"),
    }

    report = {"exports": exports, "checks": checks}
    (OUT_DIR / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)

    doc = App.newDocument("Slim20DragonBurnerCompare")
    objs = [
        ("PRINT_Slim20mmAdapter_R1", slim_adapter),
        ("REF_OrigBase1406257", base),
        ("REF_DB_MainBody_Slim", parts["db_main_slim"]),
        ("REF_DB_DuctRight_Slim", parts["duct_r_slim"]),
        ("REF_BambuHotend_Slim", parts["hotend_slim"]),
        ("REF_BambuMount_Orig_Slim", parts["bm_orig_slim"]),
        ("REF_OrbiterMount_Orig_Slim", parts["om_orig_slim"]),
        ("PRINT_BambuMount_RevOrb_Slim", parts["bm_rev_slim"]),
        ("PRINT_OrbiterMount_RevOrb_Slim", parts["om_rev_slim"]),
        ("ENV_Orbiter25_Regular_RearMotor", orb_reg["all"]),
        ("ENV_Orbiter25_Reverse_FrontMotor", orb_rev["all"]),
    ]
    for name, sh in objs:
        o = doc.addObject("Part::Feature", name)
        o.Shape = sh
    doc.recompute()
    doc.saveAs(str(OUT_DIR / "AD5M_Dragon_Burner_Slim_20mm_Comparison_R1.FCStd"))
    App.closeDocument(doc.Name)

    preview = []
    for name, sh, col in [
        ("slim_adapter", slim_adapter, [66, 133, 244]),
        ("db_main", parts["db_main_slim"], [255, 167, 38]),
        ("duct_r", parts["duct_r_slim"], [251, 140, 0]),
        ("hotend", parts["hotend_slim"], [211, 47, 47]),
        ("bm_orig", parts["bm_orig_slim"], [76, 175, 80]),
        ("om_orig", parts["om_orig_slim"], [129, 199, 132]),
        ("bm_rev", parts["bm_rev_slim"], [0, 150, 136]),
        ("om_rev", parts["om_rev_slim"], [77, 182, 172]),
        ("orb_reg", orb_reg["all"], [156, 39, 176]),
        ("orb_rev", orb_rev["all"], [233, 30, 99]),
    ]:
        v, f = sh.tessellate(0.16)
        preview.append({"name": name, "v": [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v], "f": f, "color": col})
    (OUT_DIR / "preview_parts.json").write_text(json.dumps(preview), encoding="utf-8")
    print("Saved outputs to", OUT_DIR, flush=True)


if __name__ == "__main__":
    main()
