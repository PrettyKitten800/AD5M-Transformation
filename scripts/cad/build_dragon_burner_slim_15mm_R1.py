"""
Build the -15.0 mm Slim AD5M Dragon Burner (#1406257) Adapter + Reverse-Orbiter
Mount Pack (R1) for Sensorless Homing Builds.

Generates verified single-solid manifold STLs & STEPs in
outputs/Dragon_Burner_AD5M_Slim_15mm_R1/:
  1. AD5M_Dragon_Burner_Slim_15mm_Adapter_R1.{stl,step}
     - Removes 15.0 mm from #1406257's Z=[3.40, 23.40] core spacer block
       (Z_mount: 33.40 -> 18.40 mm; Nozzle Z: 44.697 -> 29.697 mm, within +6.50 mm
       of stock/AD5M_Custom_Housing_R1's 23.197 mm!).
     - Omits Hall magnet pockets above 18.40 mm (sensorless homing).
     - Clears #1406257's upper arch bridge above Y_up = -45.78 mm (center motor/wire
       relief) while keeping all 5 M3x10 steel carriage bolt holes & 42x9 slot clean.
  2. Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1.{stl,step}
     - Exact OCCT BRep remix of Bambu_Mount(2): plugs the asymmetric (-19.51, +17.49 mm)
       Orbiter heat-sets and cleanly bores mirrored (-17.49, +19.51 mm) M3 heat-sets
       for mounting Orbiter 2.0/2.5 rotated 180 deg (motor facing FRONT).
  3. Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1.{stl,step}
     - Exact 180 deg rotated Orbiter2_Mount(4) around the filament bore, exported flat
       base down for support-free printing.
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
OUT_DIR = ROOT / "outputs/Dragon_Burner_AD5M_Slim_15mm_R1"

TRIM_MM = 15.000
ORIG_NOZZLE = (34.924, -138.401, 44.697)
SLIM_NOZZLE = (34.924, -138.401, 44.697 - TRIM_MM)   # Z = 29.697 mm
SLIM_MOUNT_Z = 33.400 - TRIM_MM                       # Z = 18.400 mm
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
    """Create a 45-deg XY corner cutter passing exactly through (cx+sx*c, cy) and (cx, cy+sy*c)."""
    p0 = App.Vector(cx - sx * 2.0, cy - sy * 2.0, -2.0)
    p1 = App.Vector(cx + sx * (c + 2.0), cy - sy * 2.0, -2.0)
    p2 = App.Vector(cx - sx * 2.0, cy + sy * (c + 2.0), -2.0)
    return Part.Face(Part.makePolygon([p0, p1, p2, p0])).extrude(App.Vector(0.0, 0.0, 30.0))


def build_slim_adapter(base: Part.Shape) -> Part.Shape:
    """Cut 15.0 mm from Z=[3.40, 23.40] spacer, relieve upper arch, and bevel 4 outer corners."""
    # Z=8.35 and Z=23.35 have identical prismatic cross-sections -> split & fuse at Z=8.40
    split_z_rear = 8.400
    split_z_front = split_z_rear + TRIM_MM  # 23.400

    rear_part = base.common(box(-50.0, 150.0, -200.0, 50.0, -5.0, split_z_rear))
    front_part = base.common(box(-50.0, 150.0, -200.0, 50.0, split_z_front, 60.0))
    front_part.translate(App.Vector(0.0, 0.0, -TRIM_MM))

    slim = rear_part.fuse(front_part).removeSplitter()

    # Remove unneeded bunny-ear arch above carriage plate (Y > -44.15) & notch the thin
    # 1.63 mm pocket roof (Y > -45.78) across X=[12.90, 56.90] forward of Z=8.40 so both
    # a regular rear motor and wire harnesses exit upward without rubbing an overhang arch.
    # Start Y at -44.16 (0.01 mm below top wall) to avoid coplanar STL-to-BRep edge splits.
    top_trim = box(-50.0, 150.0, -44.16, 10.0, 8.38, 40.0)
    center_roof_notch = box(12.90, 56.90, -45.82, -40.0, 8.38, 40.0)
    # Bake 5.0 x 5.0 mm 45-deg anti-warp chamfers into the 4 outer carriage-plate corners.
    c_anti_warp = 5.0
    corner_cuts = (
        _xy_corner_chamfer_cutter(4.902, -44.150, +1.0, -1.0, c_anti_warp)
        .fuse(_xy_corner_chamfer_cutter(64.899, -44.150, -1.0, -1.0, c_anti_warp))
        .fuse(_xy_corner_chamfer_cutter(4.902, -124.300, +1.0, +1.0, c_anti_warp))
        .fuse(_xy_corner_chamfer_cutter(64.899, -124.300, -1.0, +1.0, c_anti_warp))
    )
    slim = slim.cut(top_trim.fuse(center_roof_notch).fuse(corner_cuts)).removeSplitter()

    assert slim.isValid() and len(slim.Solids) == 1, "Slim adapter is not a single valid solid!"
    return slim.Solids[0]


def build_reverse_orbiter_mounts():
    """
    Build Bambu_Mount_ReverseOrbiter and Orbiter2_Mount_ReverseOrbiter from
    Dragon_Burner_v0.2_v8_reference.step (matching Bambu_Mount(2) & Orbiter2_Mount(4)).
    """
    doc = App.newDocument("DBRefTmp")
    Import.insert(str(REF_DB_STEP), doc.Name)
    db_main_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "MainBody"][0]
    bm_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Bambu_Mount (2)"][0]
    om_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Orbiter2_Mount (4)"][0]
    duct_r_raw = [o.Shape.copy() for o in doc.Objects if o.Label == "Standard (1)"][0]
    App.closeDocument(doc.Name)

    # Filament center in Bambu_Mount(2) / Orbiter2_Mount(4) native STEP frame:
    FIL_X = 330.100
    FIL_Y = -155.235
    TOP_Z = 109.500

    # Original Orbiter heat-sets on Bambu_Mount(2): X = 310.59 (-19.51) & 347.59 (+17.49)
    # Mirrored around X = FIL_X (for 180 deg Orbiter rotation): X = 312.61 (-17.49) & 349.61 (+19.51)
    orig_L_x = FIL_X - 19.51
    orig_R_x = FIL_X + 17.49
    mirr_L_x = FIL_X - 17.49  # 312.61
    mirr_R_x = FIL_X + 19.51  # 349.61

    # 1. Plug old heat-sets cleanly (cut flat at TOP_Z=109.500 so Orbiter2_Mount mates dead-flat)
    plug_L = Part.makeCylinder(2.45, 5.80, App.Vector(orig_L_x, FIL_Y, 103.75))
    plug_R = Part.makeCylinder(2.45, 5.80, App.Vector(orig_R_x, FIL_Y, 103.75))
    # Add a compact R=3.85 mm annular pad around mirr_L (Z=104.5..TOP_Z) so the shifted left
    # heat-set keeps full >=1.5 mm radial wall away from the adjacent wire passage (X >= 316.5).
    boss_L = Part.makeCylinder(3.85, 5.00, App.Vector(mirr_L_x, FIL_Y, 104.50))

    # 2. Bore crisp Ø4.70 mm (R=2.35) x 5.0 mm deep M3 heat-set holes at mirrored positions
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

    # Measure mirrored heat-set wall solid fraction before exporting
    wall_metrics = {}
    for lbl, hx in (("mirr_L", mirr_L_x), ("mirr_R", mirr_R_x)):
        ring = Part.makeCylinder(3.85, 4.80, App.Vector(hx, FIL_Y, 104.60)).cut(
               Part.makeCylinder(2.35, 4.80, App.Vector(hx, FIL_Y, 104.60)))
        wall_metrics[lbl] = round(bm_rev_raw.common(ring).Volume / ring.Volume, 4)

    # 3. Rotate Orbiter2_Mount(4) by 180 deg around filament bore (FIL_X, FIL_Y)
    om_rev_raw = om_raw.copy()
    om_rev_raw.rotate(App.Vector(FIL_X, FIL_Y, 0.0), App.Vector(0, 0, 1), 180.0)
    assert om_rev_raw.isValid() and len(om_rev_raw.Solids) == 1, "Orbiter2_Mount_Reverse invalid"

    # Transforms from STEP subassemblies into #1406257 SLIM frame (Z_mount = 18.400 mm, Nozzle = 29.697 mm):
    # MainBody / Standard(1) STEP center matches db_to_1406 + (0, 0, -TRIM_MM)
    def main_step_to_slim(sh: Part.Shape) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
        out.translate(App.Vector(34.9065 - 147.877, -86.681 - 102.550, 33.400 - 119.462 - TRIM_MM))
        return out

    # Bambu_Mount(2) rear flat face is Y_step=-143.929 (11.306 mm behind FIL_Y=-155.235 vs #1406257's
    # 11.297 mm; +0.010 mm Z shift seats its rear face flush on SLIM_MOUNT_Z = 18.4005 mm like Bambu_Mount(1)).
    def bm2_to_slim(sh: Part.Shape) -> Part.Shape:
        out = sh.copy()
        out.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
        out.translate(App.Vector(SLIM_NOZZLE[0] - FIL_X, -79.717 - TOP_Z, SLIM_NOZZLE[2] + 0.010 - (-FIL_Y)))
        return out

    # Bambu X1/P1 hotend transformed to SLIM frame
    hot_raw = Part.read(str(REF_HOTEND_STEP))
    hot = Part.makeCompound(hot_raw.Solids)
    hot.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
    hot.translate(App.Vector(147.895, -130.759, 95.130 - 40.300))
    hot_slim = main_step_to_slim(hot)

    # Print orientations matching stock STLs (flat rear mount face / base at Z=0):
    bm_rev_print = bm_rev_raw.copy()
    bm_rev_print.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    bb_p = bm_rev_print.BoundBox
    bm_rev_print.translate(App.Vector(-FIL_X, -((bb_p.YMin + bb_p.YMax) / 2.0), -143.929))

    # - Orbiter2_Mount_ReverseOrbiter print orientation: flat bottom (Z_raw = 109.50) at Z=0
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
    (SLIM_NOZZLE[0], Y_base=-72.817, SLIM_NOZZLE[2]) from published 51x49.5x46.9 mm
    body + Ø36x20 mm LDO-36STH20-1004AHG motor geometry (envelope check only).
    """
    fx, fy_base, fz = SLIM_NOZZLE[0], -72.817, SLIM_NOZZLE[2] + 0.010

    # Round Ø36 x 20 mm LDO motor cylinder extending roughly 4..20 mm behind/ahead of filament path
    # Centered ~25 mm above Orbiter base (radius 18 mm -> spans Y = +7..+43 mm above base, clearing base cleanly)
    motor_z0 = fz + (0.0 if reverse else -20.0)
    motor_cyl = Part.makeCylinder(18.0, 20.0, App.Vector(fx, fy_base + 25.0, motor_z0), App.Vector(0, 0, 1))

    # Main Orbiter gearbox + tensioner housing (roughly -11..+12 mm on opposite side, 49.5 mm wide, 47 mm tall)
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
        # Upstream STEP Bambu_Mount(2) has a small open boundary seam on the inner planar
        # cheek X=319.82; merge duplicate seam vertices & fill that planar hole before export.
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
    print("Loading #1406257 & building -15.0 mm Slim Adapter + Reverse Orbiter Mounts...", flush=True)
    base = load_1406257_solid()
    slim_adapter = build_slim_adapter(base)
    parts = build_reverse_orbiter_mounts()

    orb_reg = make_orbiter_25_envelope(reverse=False)
    orb_rev = make_orbiter_25_envelope(reverse=True)

    # Collisions & clearances
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
        # Upper holes screw from behind carriage into Z=0..3.0 rear pockets with solid 3.4..8.4 backing;
        # lower holes and 42x9 slot tighten from front Z>=3.45.
        if "upper" in lbl:
            rear_pocket = Part.makeCylinder(1.60, 4.80, App.Vector(bx, by, -2.0), App.Vector(0, 0, 1))
            bolt_checks[lbl] = {
                "wall_thickness_at_hole_mm": 8.40,
                "rear_pocket_Z0_to_2p8_overlap_mm3": round(slim_adapter.common(rear_pocket).Volume, 4),
            }
        else:
            corridor = Part.makeCylinder(2.75, 16.0, App.Vector(bx, by, 3.45), App.Vector(0, 0, 1))
            bolt_checks[lbl] = {"front_tool_corridor_overlap_mm3": round(slim_adapter.common(corridor).Volume, 4)}

    slot_corr = box(13.64, 55.64, -117.30, -108.30, 3.45, 19.0)
    bolt_checks["slot_42x9_front_corridor_overlap_mm3"] = round(slim_adapter.common(slot_corr).Volume, 4)

    checks = {
        "nozzle_tip_slim_mm": list(SLIM_NOZZLE),
        "nozzle_shift_vs_stock_1406257_mm": -TRIM_MM,
        "nozzle_vs_custom_housing_r1_mm": round(SLIM_NOZZLE[2] - 23.197, 3),
        "anti_warp_corner_chamfer_leg_mm": 5.0,
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
            "motor_rear_gap_to_adapter_wall_mm": round(orb_reg["motor"].distToShape(slim_adapter)[0], 3),
            "motor_rear_gap_to_steel_carriage_mm": round(orb_reg["motor"].BoundBox.ZMin, 3),
        },
        "reverse_orbiter_motor_envelope": {
            "motor_z_span_mm": [round(orb_rev["motor"].BoundBox.ZMin, 2), round(orb_rev["motor"].BoundBox.ZMax, 2)],
            "gearbox_rear_z_min_mm": round(orb_rev["gearbox"].BoundBox.ZMin, 2),
            "motor_overlap_db_main_mm3": round(orb_rev["motor"].common(parts["db_main_slim"]).Volume, 4),
            "motor_overlap_slim_adapter_mm3": round(orb_rev["motor"].common(slim_adapter).Volume, 4),
            "gearbox_rear_gap_to_adapter_wall_mm": round(orb_rev["gearbox"].distToShape(slim_adapter)[0], 3),
            "motor_front_vs_db_main_nose_mm": round(orb_rev["motor"].BoundBox.ZMax - parts["db_main_slim"].BoundBox.ZMax, 2),
            "total_toolhead_front_z_mm": round(max(orb_rev["motor"].BoundBox.ZMax, parts["duct_r_slim"].BoundBox.ZMax), 2),
        },
    }

    exports = {
        "slim_adapter": export_stl_and_step(slim_adapter, "AD5M_Dragon_Burner_Slim_15mm_Adapter_R1"),
        "bambu_mount_reverse": export_stl_and_step(
            parts["bm_rev_print"], "Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1", repair_step_seam=True
        ),
        "orbiter2_mount_reverse": export_stl_and_step(parts["om_rev_print"], "Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1"),
    }

    report = {"exports": exports, "checks": checks}
    (OUT_DIR / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)

    # Save FreeCAD comparison assembly & lightweight preview_parts.json for renderer
    doc = App.newDocument("SlimDragonBurnerCompare")
    objs = [
        ("PRINT_Slim15mmAdapter_R1", slim_adapter),
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
    doc.saveAs(str(OUT_DIR / "AD5M_Dragon_Burner_Slim_15mm_Comparison_R1.FCStd"))
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
