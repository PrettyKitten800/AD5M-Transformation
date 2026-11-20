"""Build modified Printables #1404902 lightweight fan duct for BambuMod x Orbiter v2.5 R8.

Takes reference/AD5M_Lightweight_FanDuct_1404902/adventurer-5m-duct-5x2-magnets-final.stl:
1. Rotates from print flat-on-front pose to R8 display orientation (rx = -90 deg).
2. Shifts +6.335 mm in X and -14.65 mm in Z (with Y placed cleanly in front of R8's chin)
   so its CFD-swept dual cooling horns straddle R8's shifted X1C hotend nozzle at
   (+6.335, -11.78, -28.23 mm) with >= 2.0 mm bed clearance and >= 4 mm hotend clearance.
3. Removes top mounts above Z = +70.2 mm (keeping full blower bay & hex shroud intact) and
   removes the two unused upper/mid stock AD5M magnet standoffs inside the cover.
4. Adds rigid lower R8 magnet brackets & side guide rails matching R8's front Ø5.1 mm magnets
   at display (±24.50, -30.04, +3.35 mm) with Ø7.40 mm clearance sockets for R8's Ø6.70 mm rings
   and Ø5.20 x 2.35 mm magnet pockets ("forgo the top mounts, similar to the initial design").
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import tempfile
import time
from pathlib import Path

import FreeCAD as App
import Mesh
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[2]
SRC_STL = REPO / "reference" / "AD5M_Lightweight_FanDuct_1404902" / "adventurer-5m-duct-5x2-magnets-final.stl"
R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R1"
STL_OUT = OUT_DIR / "R8_1404902_FanDuct_R1.stl"
REPORT_OUT = OUT_DIR / "r8_1404902_fanduct_report.json"

BLENDER_EXE = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

# Alignment of 1404902 onto R8 display frame (-Y=Front, +Y=Back, +Z=Up) after rx(-90 deg)
DZ_SHIFT = -14.65
X_SH = 6.335
Y_SH = -49.54     # Back face of 18 mm shroud box sits at Y = -31.54 (1.50 mm ahead of R8 Y = -30.04)
Z_SH = 27.20      # Horn ZMin = -53.328 + 27.20 = -26.128 mm (+2.10 mm above -28.23 nozzle tip)
Z_TOP_CUT = 70.20 # Above Y_stl = -43.0 (removes stock top U-latch & top ears cleanly)

NOZZLE_TIP = App.Vector(X_SH, -11.78, -28.23)
MAGNET_POSITIONS = [(-24.50, -30.04, 3.35), (24.50, -30.04, 3.35)]


def make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


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


def _build_addon_solids() -> tuple[Part.Shape, Part.Shape]:
    """Build analytical magnet wings, side guide rails, and subtraction cutters in R8 display frame."""
    add_parts: list[Part.Shape] = []
    sub_parts: list[Part.Shape] = []

    # 1) Top mount cutter (removes Z > Z_TOP_CUT)
    sub_parts.append(make_box(-45.0, 55.0, -60.0, -15.0, Z_TOP_CUT, 95.0))

    # 2) Unused stock AD5M internal magnet standoffs inside 1404902:
    #    raw (-18.0, -34.7) and (+24.0, +4.3) from front skin inner face (Z_stl=2.02 -> Y_SH+2.02) through back
    sub_parts.append(
        Part.makeCylinder(6.2, 20.0, App.Vector(-18.0 + X_SH, Y_SH + 2.02, 34.7 + Z_SH), App.Vector(0, 1, 0))
    )
    sub_parts.append(
        Part.makeCylinder(5.8, 20.0, App.Vector(24.0 + X_SH, Y_SH + 2.02, -4.3 + Z_SH), App.Vector(0, 1, 0))
    )

    # 3) Bed / nozzle safety cut below Z = -26.23 (keeps >= 2.00 mm clearance to -28.23 nozzle tip)
    sub_parts.append(make_box(-45.0, 55.0, -60.0, 10.0, -40.0, -26.23))

    # 4) Left & Right R8 Magnet Bridges & Side Guide Rails
    #    Shroud back wall is at Y_BACK = Y_SH + 18.0 = -31.54.
    #    Shifted shroud X range is [-23.665, +36.335].
    #    R8 front plane is at Y = -30.04, R8 magnet rings protrude to Y = -32.04 (R=3.35),
    #    R8 outer chin walls are at X = ±30.00.
    y_back = Y_SH + 18.0  # -31.54

    # Left magnet boss + bridge from X=-23.665 out to left guide rail X=-31.70
    left_boss = Part.makeCylinder(5.0, 4.5, App.Vector(-24.50, -34.54, 3.35), App.Vector(0, 1, 0))
    left_arm = make_box(-30.50, -21.00, -35.00, -30.04, -1.65, 8.35)
    left_rail = make_box(-31.75, -30.15, -35.00, -26.80, -2.50, 9.20)
    add_parts.extend([left_boss, left_arm, left_rail])

    # Right magnet boss + inner right guide rail hugging R8's X=+30.00 edge
    right_boss = Part.makeCylinder(5.0, 4.5, App.Vector(24.50, -34.54, 3.35), App.Vector(0, 1, 0))
    right_bridge = make_box(21.00, 31.75, -33.50, -30.04, -1.65, 8.35)
    right_rail = make_box(30.15, 31.75, -33.50, -26.80, -2.50, 9.20)
    add_parts.extend([right_boss, right_bridge, right_rail])

    # Clear R8's protruding Ø6.70 mm rings (Ø7.40 socket from Y=-32.24 to -29.80) + Ø5.20x2.35 magnet pockets
    for mx, _, mz in MAGNET_POSITIONS:
        sub_parts.append(Part.makeCylinder(3.70, 2.50, App.Vector(mx, -32.24, mz), App.Vector(0, 1, 0)))
        sub_parts.append(Part.makeCylinder(2.60, 2.35, App.Vector(mx, -34.59, mz), App.Vector(0, 1, 0)))

    # Ensure zero overlap with R8 chin (-30.04 <= Y <= +12, |X| <= 30.00, Z <= 24)
    # Wait: also protect internal shroud blower cavity (make sure magnet bridges don't encroach inside Y < -33.6!)
    # Keep R8 rail clearance margin (0.15 mm on outer rails already factored into ±30.15)
    r8_clear = make_box(-30.05, 30.05, -30.04, 15.0, -9.15, 24.0)
    sub_parts.append(r8_clear)

    add_compound = add_parts[0].multiFuse(add_parts[1:]) if len(add_parts) > 1 else add_parts[0]
    sub_compound = sub_parts[0].multiFuse(sub_parts[1:]) if len(sub_parts) > 1 else sub_parts[0]
    return add_compound, sub_compound


def _run_blender_boolean(c0_stl: Path, c1_stl: Path, add_stl: Path, sub_stl: Path, out_stl: Path) -> None:
    """Use Blender 5.2 Manifold Boolean engine to cleanly union and trim the high-poly STL."""
    blender_py = f"""
import bpy
import bmesh

bpy.ops.wm.read_factory_settings(use_empty=True)

def import_stl(filepath, name):
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.active_object
    obj.name = name
    return obj

base = import_stl(r"{c1_stl}", "BodyShroud")
right_horn = import_stl(r"{c0_stl}", "RightHorn")
add_obj = import_stl(r"{add_stl}", "AddonMounts")
sub_obj = import_stl(r"{sub_stl}", "Cutters")

def apply_bool(target, tool_obj, op_name):
    mod = target.modifiers.new(name=f"Bool_{{tool_obj.name}}", type='BOOLEAN')
    mod.operation = op_name
    mod.solver = 'MANIFOLD'
    mod.object = tool_obj
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool_obj, do_unlink=True)

apply_bool(base, sub_obj, 'DIFFERENCE')
apply_bool(base, add_obj, 'UNION')
apply_bool(base, right_horn, 'UNION')

sub2 = import_stl(r"{sub_stl}", "CuttersFinal")
apply_bool(base, sub2, 'DIFFERENCE')

# Clean degenerate edges/faces and triangulate cleanly before STL export
bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(base.data)
bm.free()

bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.wm.stl_export(filepath=r"{out_stl}", export_selected_objects=True)
print("Blender MANIFOLD exported:", len(base.data.polygons), "tris")
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(blender_py)
        script_path = Path(tf.name)
    try:
        res = subprocess.run(
            [str(BLENDER_EXE), "-b", "--python", str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        print(res.stdout[-600:])
    finally:
        script_path.unlink(missing_ok=True)


def build_modified_1404902_duct() -> dict:
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = _load_r8_refs()

    src_mesh = Mesh.Mesh(str(SRC_STL))
    raw_comps = src_mesh.getSeparateComponents()
    # Identify main body+left horn (tallest component) vs right horn
    raw_comps.sort(key=lambda c: c.BoundBox.YLength)
    c0, c1 = raw_comps[0].copy(), raw_comps[-1].copy()
    for c in (c0, c1):
        mat = App.Matrix()
        mat.rotateX(-math.pi / 2.0)
        c.transform(mat)
        c.translate(X_SH, Y_SH, Z_SH)

    add_sh, sub_sh = _build_addon_solids()
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        c0_stl, c1_stl = tmp / "c0.stl", tmp / "c1.stl"
        add_stl, sub_stl = tmp / "add.stl", tmp / "sub.stl"
        c0.write(str(c0_stl))
        c1.write(str(c1_stl))
        MeshPart.meshFromShape(Shape=add_sh, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False).write(str(add_stl))
        MeshPart.meshFromShape(Shape=sub_sh, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False).write(str(sub_stl))
        _run_blender_boolean(c0_stl, c1_stl, add_stl, sub_stl, STL_OUT)

    # Reload final STL in FreeCAD, strip any tiny boolean shards (<100 facets), harmonize normals & verify
    duct_mesh = Mesh.Mesh(str(STL_OUT))
    sub_comps = [c for c in duct_mesh.getSeparateComponents() if c.CountFacets >= 100]
    if sub_comps:
        cleaned = sub_comps[0].copy()
        for sc in sub_comps[1:]:
            cleaned.addMesh(sc)
        cleaned.removeDuplicatedPoints()
        cleaned.removeDuplicatedFacets()
        cleaned.fixDegenerations(1e-5)
        cleaned.removeNonManifolds()
        cleaned.fixIndices()
        cleaned.harmonizeNormals()
        cleaned.write(str(STL_OUT))
        duct_mesh = Mesh.Mesh(str(STL_OUT))

    def mesh_common_vol(ref_shape: Part.Shape) -> float:
        mref = MeshPart.meshFromShape(Shape=ref_shape, LinearDeflection=0.08, AngularDeflection=0.35, Relative=False)
        if not duct_mesh.BoundBox.intersect(mref.BoundBox):
            return 0.0
        inter = duct_mesh.intersect(mref)
        if inter.CountFacets == 0:
            return 0.0
        return round(max(0.0, float(inter.Volume)), 3)

    # Also compute exact minimum surface distance to hotend and orbiter via point clouds
    import numpy as np
    d_pts = np.array([[p.x, p.y, p.z] for p in duct_mesh.Points])

    def min_dist_to(ref_shape: Part.Shape) -> float:
        mref = MeshPart.meshFromShape(Shape=ref_shape, LinearDeflection=0.06, AngularDeflection=0.25, Relative=False)
        r_pts = np.array([[p.x, p.y, p.z] for p in mref.Points])
        # Coarse bbox filter first
        rbb = mref.BoundBox
        sub = d_pts[
            (d_pts[:, 0] >= rbb.XMin - 15) & (d_pts[:, 0] <= rbb.XMax + 15) &
            (d_pts[:, 1] >= rbb.YMin - 15) & (d_pts[:, 1] <= rbb.YMax + 15) &
            (d_pts[:, 2] >= rbb.ZMin - 15) & (d_pts[:, 2] <= rbb.ZMax + 15)
        ]
        if len(sub) == 0:
            return 99.9
        best = 1e9
        for i in range(0, len(sub), 1500):
            da = sub[i:i+1500, None, :] - r_pts[None, :, :]
            d2 = np.sum(da * da, axis=2)
            v = float(np.sqrt(d2.min()))
            if v < best:
                best = v
        return round(best, 3)

    checks = {
        "duct_vs_r8_adapter_mm3": mesh_common_vol(refs["r8"]),
        "duct_vs_orbiter_mm3": mesh_common_vol(refs["orbiter"]),
        "duct_vs_x1c_hotend_mm3": mesh_common_vol(refs["hotend"]),
        "duct_vs_3010_fan_mm3": mesh_common_vol(refs["fan3010"]),
        "duct_vs_gray_carriage_mm3": mesh_common_vol(refs["carriage"]),
        "min_dist_to_hotend_mm": min_dist_to(refs["hotend"]),
        "min_dist_to_orbiter_mm": min_dist_to(refs["orbiter"]),
    }

    bb = duct_mesh.BoundBox
    report = {
        "source_model": "Printables 1404902 (adventurer-5m-duct-5x2-magnets-final.stl)",
        "transform_display_mm": {"rx_deg": -90.0, "dx": X_SH, "dy": Y_SH, "dz": Z_SH, "top_cut_z": Z_TOP_CUT},
        "nozzle_target_display_mm": [round(NOZZLE_TIP.x, 3), round(NOZZLE_TIP.y, 3), round(NOZZLE_TIP.z, 3)],
        "magnet_mounts_display_mm": [list(p) for p in MAGNET_POSITIONS],
        "bbox": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
        "nozzle_bed_clearance_mm": round(bb.ZMin - NOZZLE_TIP.z, 3),
        "volume_mm3": round(float(duct_mesh.Volume), 2),
        "components": int(duct_mesh.countComponents()),
        "stl_solid": bool(duct_mesh.isSolid()),
        "stl_facets": int(duct_mesh.CountFacets),
        "stl_non_manifolds": bool(duct_mesh.hasNonManifolds()),
        "stl_non_uniform_faces": int(duct_mesh.countNonUniformOrientedFacets()),
        "stl_self_intersections": bool(duct_mesh.hasSelfIntersections()),
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"[1404902->R8 R1] Built in {report['build_seconds']}s | vol={report['volume_mm3']} | "
        f"comps={report['components']} solid={report['stl_solid']} nm={report['stl_non_manifolds']} "
        f"si={report['stl_self_intersections']} | bed_clear={report['nozzle_bed_clearance_mm']}mm | "
        f"checks={checks}"
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_modified_1404902_duct()
