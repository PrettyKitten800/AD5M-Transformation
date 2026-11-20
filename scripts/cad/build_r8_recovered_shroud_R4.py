"""Build R8-mounted Fan_Shroud_Recovered revision R4 (simplify pinned bevel, side-wall, and underside steps).

Takes outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R3/Fan_Shroud_Recovered_R8_R3.stl and makes
the four pinned step/groove regions flush with their dominant planes using sequential Blender 5.2
MANIFOLD Booleans (guaranteeing a single watertight manifold solid):
  - Region A (Pins #3, #4, #5): Left-front 45 deg bevel flushed to x + y = -63.569 (d = 44.95 mm)
    across Z = [-2.788, +7.10], bounded cleanly by X >= -23.69 and Y >= -49.59.
  - Region B (Pins #9, #10): Left underside notch filled flush to Z = -2.788, Y = -31.650, X = -23.69.
  - Region C (Pins #1, #2, #7): Right outer side wall & upper-rear groove flushed to X = +33.390,
    Y = -31.650, Z = [-2.788, +16.360] (staying outside the internal blower cavity and magnet pocket).
  - Region D (Pins #6, #8): Right underside notch filled flush to Z = -2.788, Y = -31.650, X = +33.390.
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
import numpy as np
import Part

REPO = Path(__file__).resolve().parents[2]
R3_STL = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R3" / "Fan_Shroud_Recovered_R8_R3.stl"

R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R4"
R8_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R4.stl"
PRINT_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R4.stl"
REPORT_OUT = OUT_DIR / "r8_recovered_shroud_r4_report.json"

BLENDER_EXE = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

# Dominant planes measured from R3
X_LEFT_WALL = -23.690
X_RIGHT_WALL = 33.390
Y_FRONT_WALL = -49.593
Y_REAR_WALL = -31.650
Z_BOT_FACE = -2.788
Z_RIGHT_TOP = 16.360

# Left-front 45 deg bevel: x + y = BEVEL_SUM (d = (-x - y)/sqrt(2) = 44.95 mm)
BEVEL_SUM = -63.569
Z_BEVEL_TOP = 7.100

DZ_SHIFT = -14.65
DX_ALIGN = 0.8024
DY_ALIGN = -49.5939
DZ_ALIGN = 0.7037
NOZZLE_TIP = App.Vector(6.335, -11.78, -28.23)


def make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def _make_xy_prism(pts_xy: list[tuple[float, float]], z0: float, z1: float) -> Part.Shape:
    vecs = [App.Vector(x, y, z0) for x, y in pts_xy]
    vecs.append(vecs[0])
    wire = Part.makePolygon(vecs)
    return Part.Face(wire).extrude(App.Vector(0.0, 0.0, z1 - z0))


def _build_ops() -> list[tuple[str, str, Part.Shape]]:
    """Build ordered list of (name, op, solid) for clean sequential MANIFOLD booleans."""
    y_left_hit = BEVEL_SUM - X_LEFT_WALL
    x_front_hit = BEVEL_SUM - Y_FRONT_WALL

    # Region A: 45-deg bevel groove filler + protruding rib trimmer
    bevel_in_sum = BEVEL_SUM + 1.80
    bevel_fill = _make_xy_prism(
        [
            (X_LEFT_WALL, y_left_hit),
            (x_front_hit, Y_FRONT_WALL),
            (bevel_in_sum - Y_FRONT_WALL, Y_FRONT_WALL),
            (X_LEFT_WALL, bevel_in_sum - X_LEFT_WALL),
        ],
        Z_BOT_FACE,
        Z_BEVEL_TOP,
    )
    bevel_out_sum = BEVEL_SUM - 4.00
    bevel_trim = _make_xy_prism(
        [
            (X_LEFT_WALL - 1.5, BEVEL_SUM - (X_LEFT_WALL - 1.5)),
            (BEVEL_SUM - (Y_FRONT_WALL - 1.5), Y_FRONT_WALL - 1.5),
            (bevel_out_sum - (Y_FRONT_WALL - 1.5), Y_FRONT_WALL - 1.5),
            (X_LEFT_WALL - 1.5, bevel_out_sum - (X_LEFT_WALL - 1.5)),
        ],
        Z_BOT_FACE - 0.15,
        Z_BEVEL_TOP,
    )

    # Region B: Left underside notch filler (Pins #9, #10)
    left_bottom_fill = make_box(X_LEFT_WALL, -15.00, -37.50, Y_REAR_WALL, Z_BOT_FACE, -0.90)

    # Region C: Right outer side wall + Pin #7 rear-upper groove fillers + shave > X_RIGHT_WALL
    right_wall_fill = make_box(30.80, X_RIGHT_WALL, -37.80, Y_REAR_WALL, Z_BOT_FACE, Z_RIGHT_TOP)
    pin7_rear_fill = make_box(28.20, X_RIGHT_WALL, -32.65, Y_REAR_WALL, 8.50, Z_RIGHT_TOP)
    right_wall_trim = make_box(X_RIGHT_WALL, 36.00, -45.50, Y_REAR_WALL + 0.50, Z_BOT_FACE - 0.50, Z_RIGHT_TOP + 0.50)

    # Region D: Right underside notch filler (Pins #6, #8)
    right_bottom_fill = make_box(22.50, X_RIGHT_WALL, -37.80, Y_REAR_WALL, Z_BOT_FACE, -0.90)

    return [
        ("BevelFill", "UNION", bevel_fill),
        ("BevelTrim", "DIFFERENCE", bevel_trim),
        ("LeftBottomFill", "UNION", left_bottom_fill),
        ("RightWallFill", "UNION", right_wall_fill),
        ("Pin7RearFill", "UNION", pin7_rear_fill),
        ("RightBottomFill", "UNION", right_bottom_fill),
        ("RightWallTrim", "DIFFERENCE", right_wall_trim),
    ]


def _run_blender_ops(src_stl: Path, op_files: list[tuple[str, str, Path]], out_stl: Path) -> None:
    ops_lit = repr([(name, op, str(fp)) for name, op, fp in op_files])
    blender_py = f"""
import bpy
import bmesh

bpy.ops.wm.read_factory_settings(use_empty=True)

def import_stl(filepath, name):
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.active_object
    obj.name = name
    return obj

base = import_stl(r"{src_stl}", "Shroud")
for name, op, fp in {ops_lit}:
    tool = import_stl(fp, name)
    mod = base.modifiers.new(name=f"Bool_{{name}}", type='BOOLEAN')
    mod.operation = op
    mod.solver = 'MANIFOLD'
    mod.object = tool
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)

bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(base.data)
bm.free()

bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.wm.stl_export(filepath=r"{out_stl}", export_selected_objects=True)
print("Blender MANIFOLD R4 exported:", len(base.data.polygons), "tris")
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
        print(res.stdout[-500:])
    finally:
        script_path.unlink(missing_ok=True)


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


def _mesh_common_vol(mesh_a: Mesh.Mesh, ref_shape: Part.Shape) -> float:
    mref = MeshPart.meshFromShape(Shape=ref_shape, LinearDeflection=0.06, AngularDeflection=0.25, Relative=False)
    if not mesh_a.BoundBox.intersect(mref.BoundBox):
        return 0.0
    inter = mesh_a.intersect(mref)
    if inter.CountFacets == 0:
        return 0.0
    return round(max(0.0, float(inter.Volume)), 4)


def _min_dist_to(d_pts: np.ndarray, ref_shape: Part.Shape) -> float:
    mref = MeshPart.meshFromShape(Shape=ref_shape, LinearDeflection=0.06, AngularDeflection=0.25, Relative=False)
    r_pts = np.array([[p.x, p.y, p.z] for p in mref.Points])
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
        da = sub[i:i + 1500, None, :] - r_pts[None, :, :]
        d2 = np.sum(da * da, axis=2)
        v = float(np.sqrt(d2.min()))
        if v < best:
            best = v
    return round(best, 3)


def build_recovered_shroud_r4() -> dict:
    t0 = time.perf_counter()
    if not R3_STL.exists():
        raise FileNotFoundError(f"Missing R3 STL: {R3_STL}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ops = _build_ops()
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        op_files: list[tuple[str, str, Path]] = []
        for name, op, sh in ops:
            fp = tmp / f"{name}.stl"
            MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.02, AngularDeflection=0.20, Relative=False).write(str(fp))
            op_files.append((name, op, fp))
        _run_blender_ops(R3_STL, op_files, R8_STL_OUT)

    m = Mesh.Mesh(str(R8_STL_OUT))
    comps = [c for c in m.getSeparateComponents() if c.CountFacets >= 50]
    if comps:
        cleaned = comps[0].copy()
        for sc in comps[1:]:
            cleaned.addMesh(sc)
        cleaned.removeDuplicatedPoints()
        cleaned.removeDuplicatedFacets()
        cleaned.fixDegenerations(1e-5)
        cleaned.removeNonManifolds()
        cleaned.fillupHoles(20)
        cleaned.fixIndices()
        cleaned.harmonizeNormals()
        cleaned.write(str(R8_STL_OUT))
        m = Mesh.Mesh(str(R8_STL_OUT))

    # Print-ready flat-on-front pose (ZMin = 0.000)
    m_print = m.copy()
    m_print.translate(-DX_ALIGN, -DY_ALIGN, -DZ_ALIGN)
    mat_inv = App.Matrix()
    mat_inv.rotateX(math.pi / 2.0)
    m_print.transform(mat_inv)
    pbb = m_print.BoundBox
    if abs(pbb.ZMin) > 1e-6:
        m_print.translate(0.0, 0.0, -pbb.ZMin)
    m_print.write(str(PRINT_STL_OUT))

    refs = _load_r8_refs()
    d_pts = np.array([[p.x, p.y, p.z] for p in m.Points])
    checks = {
        "shroud_vs_r8_adapter_mm3": _mesh_common_vol(m, refs["r8"]),
        "shroud_vs_orbiter_mm3": _mesh_common_vol(m, refs["orbiter"]),
        "shroud_vs_x1c_hotend_mm3": _mesh_common_vol(m, refs["hotend"]),
        "shroud_vs_3010_fan_mm3": _mesh_common_vol(m, refs["fan3010"]),
        "shroud_vs_gray_carriage_mm3": _mesh_common_vol(m, refs["carriage"]),
        "min_dist_to_hotend_mm": _min_dist_to(d_pts, refs["hotend"]),
        "min_dist_to_orbiter_mm": _min_dist_to(d_pts, refs["orbiter"]),
    }

    bb = m.BoundBox
    report = {
        "source_model": R3_STL.name,
        "simplified_planes": {
            "left_front_bevel_sum_xy": BEVEL_SUM,
            "left_wall_x": X_LEFT_WALL,
            "right_wall_x": X_RIGHT_WALL,
            "rear_wall_y": Y_REAR_WALL,
            "bottom_plane_z": Z_BOT_FACE,
            "right_top_shelf_z": Z_RIGHT_TOP,
        },
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
    print(
        f"[FanShroudRecovered R4] Built in {report['build_seconds']}s | vol={report['volume_mm3']} | "
        f"comps={report['components']} solid={report['stl_solid']} nm={report['stl_non_manifolds']} "
        f"si={report['stl_self_intersections']} | checks={checks}"
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_recovered_shroud_r4()
