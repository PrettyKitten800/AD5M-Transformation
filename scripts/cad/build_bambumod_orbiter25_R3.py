"""Build BambuMod x Orbiter v2.5 AD5M Offset-Hotend Adapter — Revision 3 (R3).

Addresses user feedback after R2:
  1. Keeps ONLY the 4 actual AD5M steel carriage mounting holes:
       - low_R (-19.0, 3.5), low_L (+19.0, 3.5),
       - up_R  (-24.0, 61.0), up_L (+24.0, 61.0),
     all kept as rear-entry (-Y) blind pockets completely hidden from the front (+Y).
  2. Completely plugs the 3 obsolete stock-extruder holes from bm_body that are
     no longer used:
       - old_mid_R   (-21.5, 51.0)
       - old_up_L_hi (+23.7, 66.5)
       - old_top_R   (-14.0, 71.5)
     eliminating the unneeded left/top protective boss bumps inside the motor pocket
     and cleaning up both front and rear walls while preserving Kirill's belt slots.
  3. Retains all R2 offset-hotend + cooling upgrades cleanly:
       - Primary datum: X_mot = 0.000, Z_mot = 51.900, X_fil = -6.335, Z_mount = 32.600
       - Restored +X 3010 fan shroud arch + 5-section Part.makeLoft cooling duct +
         all 4 unobstructed 3010 corner M3 mounting bores + front X1C wrench bay.

Credits & License (preserved):
  - BambuMod adapter base: Kirill_Wawe (Printables #1574762), CC BY-NC-SA 4.0
  - Orbiter v2.5 extruder mockup: dr. Lorincz Robert
  - Derived R3 adapter files share CC BY-NC-SA 4.0.
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
from build_bambumod_orbiter25_R2 import (  # noqa: E402
    MOT_HOLE_R,
    X_FIL,
    X_MOT,
    Z_MOT,
    Z_MOUNT,
    build_duct_void,
    detect_front_shroud_y,
)

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R3"

# Only the 4 true AD5M steel carriage mounting bores (rear-entry blind pockets)
CARRIAGE_HOLES_R3 = [
    ("low_R", -19.0, 3.5, -5.58, None),
    ("low_L", 19.0, 3.5, -5.58, None),
    ("up_R", -24.0, 61.0, -5.58, -4.45),  # Stops 0.17 mm behind Orbiter corner (-4.276) -> 1.13 mm blind skin
    ("up_L", 24.0, 61.0, -5.58, None),
]

# 3 obsolete stock-extruder holes in Kirill's BambuMod body -> plugged solid
OBSOLETE_EXTRUDER_HOLES = [
    ("old_mid_R", -21.5, 51.0),
    ("old_up_L_hi", 23.7, 66.5),
    ("old_top_R", -14.0, 71.5),
]


def build_primary_r3(refs: dict) -> tuple[Part.Shape, dict]:
    """Build R3 Primary adapter with 4 blind carriage bores, 3 obsolete bores plugged, and R2 cooling duct."""
    bm_body = refs["bm_body"]
    rear_y, front_y = detect_backplate_y_planes(bm_body)
    shroud_front_y = detect_front_shroud_y(bm_body)

    plate_top = Z_MOUNT - 0.02
    plate_bot = Z_MOUNT - 5.80  # 26.800 mm

    work = bm_body.copy()
    # 0. Heal BambuMod upstream 0.0002 mm micro-slit on -X front corner flush to exact front shroud plane
    work = work.fuse(box(-28.10, -27.15, 27.05, shroud_front_y, 30.80, 31.05))

    # 1. Remove upper interior features above Orbiter plate level ONLY (preserving Z < plate_top duct shell!)
    pre_cuts = [
        box(-27.8, 14.3, front_y - 0.1, 27.8, plate_top, 59.8),
        box(-14.0, 14.3, front_y - 0.1, 27.8, 59.5, 69.5),
        box(-31.5, -26.70, front_y + 0.05, 32.5, plate_top, 59.00),
        box(-31.5, -26.70, -2.0, 32.5, 58.90, 64.00),
        box(14.0, 18.42, 2.0, 22.0, plate_top, 45.0).cut(
            cyl_x(3.10, 23.37, 34.25, 13.5, 20.0)
        ),
        box(14.0, 18.42, front_y - 0.1, 22.0, 37.35, 45.0),
        box(18.35, 18.58, 2.0, 18.5, 36.35, 38.0),
        box(19.42, 30.5, -3.72, 26.46, 7.16, 37.35),
        box(-6.5, 8.6, front_y + 0.1, 13.5, 23.80, 32.55),
    ]
    for c in pre_cuts:
        work = work.cut(c)

    # 2. Rebuild lower duct envelope, sealed front shroud, Orbiter shelf, blind caps, & old-hole plugs
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

    # Solid backplate infill starting at Y=-8.50 (preserving Kirill's 2.6 mm rear belt/weight channels)
    back_fill_lo = box(-27.8, 27.8, -8.50, front_y, 20.6, 48.0)
    back_fill_hi = box(-18.5, 27.8, -8.50, front_y, 47.8, 58.6)
    back_fill_top = box(-12.5, 19.5, -8.50, front_y, 58.4, 64.2)

    # 2g. Blind-hole front caps for the 4 retained rear-entry carriage bores (zero front visibility)
    blind_caps = []
    for name, cx, cz, cap_y0, cap_y1_ov in CARRIAGE_HOLES_R3:
        cy1 = front_y if cap_y1_ov is None else cap_y1_ov
        cap_r = 2.18 if name == "up_R" else 2.40
        blind_caps.append(cyl_y(cap_r, cx, cz, cap_y0, cy1))

    # 2h. Plug the 3 obsolete stock-extruder holes solid while keeping upper belt slot clear
    belt_high_zone = box(-40.0, 40.0, rear_y - 0.1, -9.12, 64.8, 75.2)
    old_hole_plugs = [
        cyl_y(2.40, -21.5, 51.0, rear_y, front_y),
        cyl_y(2.40, 23.7, 66.5, rear_y, front_y).cut(belt_high_zone),
        cyl_y(2.40, -14.0, 71.5, -9.12, front_y),
    ]

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
        *old_hole_plugs,
    ]:
        work = work.fuse(solid_add)

    work = work.removeSplitter()
    assert work.isValid(), "Primary_R3 pre-cut BRep invalid!"

    # 3. Carve exact aerodynamic duct loft + shifted X1C heatsink & screw window + motor/Orbiter cutouts
    duct_void = build_duct_void()

    # Only protect the 2 upper kept carriage bosses (up_L always, up_R behind Y=-4.45)
    protect_up_l = cyl_y(2.50, 24.0, 61.0, -9.00, front_y + 2.0)
    protect_up_r_back = cyl_y(2.18, -24.0, 61.0, -9.00, -4.45)
    above_plate_mask = box(-32.0, 32.0, -10.0, front_y + 2.0, plate_top, 80.0)

    final_cuts = [
        duct_void,
        box(X_FIL - 8.30, X_FIL + 8.30, -2.50, 23.25, 5.20, 7.65),
        box(X_FIL - 6.60, X_FIL + 6.60, 8.28, 30.50, 24.80, 31.10),
        box(X_FIL - 6.60, X_FIL + 6.60, 24.50, 30.50, 24.80, plate_top),
        cyl_y(1.65, X_FIL - 3.425, 27.220, -1.60, 9.00),
        cyl_y(1.65, X_FIL + 3.425, 27.220, -1.60, 9.00),
        cyl_z(2.00, X_FIL, 12.08, plate_bot - 0.50, plate_top + 1.00),
        Part.makeCone(2.60, 1.90, 0.80, Vector(X_FIL, 12.08, 30.50), Vector(0, 0, 1)),
        cyl_z(2.20, -23.85, 12.08, plate_top - 4.30, plate_top + 0.50),
        cyl_z(2.20, 13.15, 12.08, plate_top - 4.30, plate_top + 0.50),
        cyl_y(MOT_HOLE_R, X_MOT, Z_MOT, rear_y - 1.0, front_y + 1.0),
        cyl_y(25.40, X_MOT, Z_MOT, -6.85, -4.45).common(above_plate_mask).cut(protect_up_l.fuse(protect_up_r_back)),
        cyl_y(25.60, X_MOT, Z_MOT, -4.45, front_y + 1.0).common(above_plate_mask).cut(protect_up_l),
        stadium_xz_y(
            X_MOT + 17.5 * math.cos(math.radians(-30)),
            Z_MOT + 17.5 * math.sin(math.radians(-30)),
            X_MOT + 22.0 * math.cos(math.radians(-30)),
            Z_MOT + 22.0 * math.sin(math.radians(-30)),
            3.20,
            -8.20,
            front_y + 1.0,
        ),
        stadium_xz_y(
            X_MOT - 17.5 * math.cos(math.radians(-30)),
            Z_MOT - 17.5 * math.sin(math.radians(-30)),
            X_MOT - 22.0 * math.cos(math.radians(-30)),
            Z_MOT - 22.0 * math.sin(math.radians(-30)),
            3.20,
            -8.20,
            front_y + 1.0,
        ).cut(protect_up_r_back),
        stadium_xz_y(-11.2, 34.0, -8.8, 37.5, 3.80, rear_y - 1.0, front_y + 1.0),
    ]

    for c in final_cuts:
        work = work.cut(c)

    work = work.removeSplitter()
    assert work.isValid(), "Primary_R3 BRep invalid!"
    assert len(work.Solids) == 1, f"Expected 1 solid, got {len(work.Solids)}"
    solid = work.Solids[0]

    # === Verify Collisions, 4 Blind Carriage Holes, 3 Plugged Holes, and 4 Fan Bores ===
    orb_placed = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_body_solids"]]
    orb_bolts = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_bolts"]]
    he_placed = refs["he_raw"].copy()
    he_placed.translate(Vector(X_FIL, 0, 0))
    fan_3010 = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)
    ebb_bkt = refs["ebb_bkt"]
    steel_carriage = box(-40.0, 40.0, -30.0, rear_y - 0.005, -10.0, 90.0)
    belt_low = box(-40.0, 40.0, rear_y - 0.1, -9.12, 9.8, 20.2)

    bm_solid = bm_body.Solids[0]
    ov_orb = sum(solid.common(o).Volume for o in orb_placed)
    ov_bolts = sum(solid.common(b).Volume for b in orb_bolts)
    ov_he = solid.common(he_placed).Volume
    ov_fan = solid.common(fan_3010).Volume
    ov_fan_orb = sum(fan_3010.common(o).Volume for o in orb_placed)
    ov_ebb = solid.common(ebb_bkt).Volume
    ov_carriage = solid.common(steel_carriage).Volume
    ov_belt_lo = solid.common(belt_low.cut(bm_solid)).Volume
    ov_belt_hi = solid.common(belt_high_zone.cut(bm_solid)).Volume

    fan_holes_obs = {
        f"fan_yz_{y}_{z}": round(solid.common(cyl_x(1.30, y, z, 15.0, 19.6)).Volume, 4)
        for y, z in [(-0.63, 10.25), (23.37, 10.25), (-0.63, 34.25), (23.37, 34.25)]
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

    # Verify the 3 obsolete extruder bores are solidly plugged in their full rear structural span
    plugged_report = {}
    plug_spans = {
        "old_mid_R": (-11.05, -7.00),    # 4.05 mm rear plate behind R=25.4 motor recess
        "old_up_L_hi": (-9.05, -4.00),   # 5.05 mm full backing clear of upper belt slot
        "old_top_R": (-9.05, -7.00),     # 2.05 mm rear backing behind R=25.4 motor recess & clear of belt slot
    }
    for name, ox, oz in OBSOLETE_EXTRUDER_HOLES:
        y0, y1 = plug_spans[name]
        check_cyl = cyl_y(2.05, ox, oz, y0, y1)
        frac = solid.common(check_cyl).Volume / check_cyl.Volume
        plugged_report[name] = {
            "xz_mm": [ox, oz],
            "checked_y_span_mm": [y0, y1],
            "solid_fraction": round(frac, 4),
            "completely_plugged": bool(frac > 0.99),
        }

    duct_clearance_x = {}
    for x0 in [18.5, 14.0, 8.0, 2.5, -18.0, -25.0]:
        probe = box(x0, x0 + 0.5, 5.0, 17.0, 10.0, 22.0)
        duct_clearance_x[f"X_{x0:.1f}"] = round(solid.common(probe).Volume / probe.Volume, 4)

    bb = solid.BoundBox
    report = {
        "variant": "Primary_R3",
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
        "carriage_holes_4_blind_verification": hole_report,
        "obsolete_extruder_holes_3_plugged": plugged_report,
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
    """Export STEP, verify re-read, export Z=0 flat-back STL, verify manifoldness, write preview JSONs."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    step_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R3.step"
    stl_p = OUT_DIR / "BambuMod_Orbiter25_Primary_R3.stl"
    fcstd_p = OUT_DIR / "BambuMod_Orbiter25_Assembly_R3.FCStd"

    solid.exportStep(str(step_p))
    re_read = Part.read(str(step_p))
    assert re_read.isValid() and len(re_read.Solids) == 1, "Re-read STEP invalid!"

    stl_shape = solid.copy()
    stl_shape.rotate(Vector(0, 0, 0), Vector(1, 0, 0), -90)
    stl_shape.translate(Vector(0, 0, -stl_shape.BoundBox.ZMin))

    mesh = MeshPart.meshFromShape(Shape=stl_shape, LinearDeflection=0.05, AngularDeflection=0.25, Relative=False)
    mesh.write(str(stl_p))
    mchk = Mesh.Mesh(str(stl_p))
    assert mchk.isSolid(), "STL is not solid!"
    assert not mchk.hasNonManifolds(), "STL has non-manifold edges!"

    oh_area = 0.0
    oh_deep = 0.0
    for f in mchk.Facets:
        nz = f.Normal.z
        zc = sum(p[2] for p in f.Points) / 3.0
        if zc > 0.25 and nz < -0.7071:
            oh_area += f.Area
            if nz < -0.94:
                oh_deep += f.Area

    doc = App.newDocument("BambuMod_Orbiter25_R3")
    for obj_name, shp in [
        ("Primary_Adapter_R3", solid),
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

    def _tess_list(shp: Part.Shape, tol: float = 0.08):
        v, f = shp.tessellate(tol)
        return [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v], [[int(i) for i in tri] for tri in f]

    parts_json = []
    for pname, shp, col in [
        ("adapter", solid, [65, 130, 195]),
        ("x1c", ctx["he_placed"], [215, 95, 70]),
        ("orbiter", ctx["orb_placed"], [72, 76, 84]),
        ("ebb42", ctx["ebb_bkt"], [65, 165, 105]),
        ("fan3010", ctx["fan_3010"], [225, 165, 55]),
    ]:
        verts, faces = _tess_list(shp)
        parts_json.append({"name": pname, "color": col, "v": verts, "f": faces})

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

    (OUT_DIR / "preview_primary_r3.json").write_text(json.dumps(parts_json), encoding="utf-8")
    (OUT_DIR / "preview_cutaways_r3.json").write_text(json.dumps(cuts_payload), encoding="utf-8")

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
    print("Building Primary_R3 (4 blind carriage holes, 3 obsolete bores plugged, R2 ducting)...", flush=True)
    solid, ctx = build_primary_r3(refs)
    rep = export_verified(solid, ctx)
    cols = rep["collisions_mm3"]
    assert all(v < 1e-3 for v in cols.values()), f"Collision detected: {cols}"
    fan_obs = rep["fan_3010_mounting_holes_obstruction_mm3"]
    assert all(v < 1e-3 for v in fan_obs.values()), f"3010 fan hole blocked: {fan_obs}"
    holes = rep["carriage_holes_4_blind_verification"]
    assert all(h["hidden_from_front"] for h in holes.values()), f"Blind carriage hole failed: {holes}"
    plugs = rep["obsolete_extruder_holes_3_plugged"]
    assert all(p["completely_plugged"] for p in plugs.values()), f"Obsolete hole plug failed: {plugs}"
    print("R3 BUILD & CAD VALIDATION PASSED CLEANLY.")


if __name__ == "__main__":
    main()
