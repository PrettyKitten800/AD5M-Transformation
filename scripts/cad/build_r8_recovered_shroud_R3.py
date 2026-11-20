"""Build R8-mounted Fan_Shroud_Recovered revision R3 (magnet tabs flush with shroud rear face).

Takes outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R2/Fan_Shroud_Recovered_R8_R2.stl and trims
the two magnet-holding tab rear faces (Y = -30.05 mm, inside |X| <= 30.180 mm, Z in [-2.50, +9.50])
flush with the main shroud rear face (Face #3, Y = -31.651 mm) using Blender 5.2 MANIFOLD Boolean.
Both outer side guide rails (|X| >= 30.180 mm) and both Ø5.20 mm magnet pockets (Y = -34.66..-32.25)
remain intact. Exports both R8 display-pose STL and flat print-pose STL (ZMin = 0.000).
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
R2_STL = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R2" / "Fan_Shroud_Recovered_R8_R2.stl"

R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R3"
R8_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R3.stl"
PRINT_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R3.stl"
REPORT_OUT = OUT_DIR / "r8_recovered_shroud_r3_report.json"

BLENDER_EXE = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

# Exact Face #3 rear shroud plane (-31.6509 mm; offset +0.001 mm avoids coplanar grazing)
Y_FLUSH_FACE = -31.650
X_RAIL_INNER = 30.180
X_TAB_INNER = 19.000
Z_CUT_MIN = -2.500
Z_CUT_MAX = 9.500
Y_CUT_MAX = -28.000

# R2 alignment parameters (used to invert cleanly back to print-on-front pose)
DZ_SHIFT = -14.65
DX_ALIGN = 0.8024
DY_ALIGN = -49.5939
DZ_ALIGN = 0.7037
NOZZLE_TIP = App.Vector(6.335, -11.78, -28.23)


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


def _run_blender_trim(src_stl: Path, cut_stl: Path, out_stl: Path) -> None:
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
cutter = import_stl(r"{cut_stl}", "TabCutters")

mod = base.modifiers.new(name="TrimTabsFlush", type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
mod.object = cutter
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter, do_unlink=True)

bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(base.data)
bm.free()

bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.wm.stl_export(filepath=r"{out_stl}", export_selected_objects=True)
print("Blender MANIFOLD trimmed:", len(base.data.polygons), "tris")
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


def build_recovered_shroud_r3() -> dict:
    t0 = time.perf_counter()
    if not R2_STL.exists():
        raise FileNotFoundError(f"Missing R2 STL: {R2_STL}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    left_cut = make_box(-X_RAIL_INNER, -X_TAB_INNER, Y_FLUSH_FACE, Y_CUT_MAX, Z_CUT_MIN, Z_CUT_MAX)
    right_cut = make_box(X_TAB_INNER, X_RAIL_INNER, Y_FLUSH_FACE, Y_CUT_MAX, Z_CUT_MIN, Z_CUT_MAX)
    cut_compound = Part.makeCompound([left_cut, right_cut])

    with tempfile.TemporaryDirectory() as tmpd:
        cut_stl = Path(tmpd) / "tab_cutters.stl"
        MeshPart.meshFromShape(Shape=cut_compound, LinearDeflection=0.02, AngularDeflection=0.20, Relative=False).write(str(cut_stl))
        _run_blender_trim(R2_STL, cut_stl, R8_STL_OUT)

    # Reload, strip any tiny slivers (<50 facets), harmonize normals
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
        cleaned.fixIndices()
        cleaned.harmonizeNormals()
        cleaned.write(str(R8_STL_OUT))
        m = Mesh.Mesh(str(R8_STL_OUT))

    # Also export flat print-on-front pose (inverse of R2 transform)
    m_print = m.copy()
    m_print.translate(-DX_ALIGN, -DY_ALIGN, -DZ_ALIGN)
    mat_inv = App.Matrix()
    mat_inv.rotateX(math.pi / 2.0)
    m_print.transform(mat_inv)
    pbb = m_print.BoundBox
    if abs(pbb.ZMin) > 1e-6:
        m_print.translate(0.0, 0.0, -pbb.ZMin)
    m_print.write(str(PRINT_STL_OUT))

    # Verify flushness of magnet tabs (|X| in [20, 30.15], Z in [-2, 9])
    d_pts = np.array([[p.x, p.y, p.z] for p in m.Points])
    l_tab = d_pts[(d_pts[:, 0] > -30.15) & (d_pts[:, 0] < -20.0) & (d_pts[:, 2] > -2.0) & (d_pts[:, 2] < 9.0)]
    r_tab = d_pts[(d_pts[:, 0] > 20.0) & (d_pts[:, 0] < 30.15) & (d_pts[:, 2] > -2.0) & (d_pts[:, 2] < 9.0)]
    left_tab_max_y = round(float(l_tab[:, 1].max()), 4) if len(l_tab) else None
    right_tab_max_y = round(float(r_tab[:, 1].max()), 4) if len(r_tab) else None

    refs = _load_r8_refs()
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
        "source_model": R2_STL.name,
        "flush_plane_y_mm": Y_FLUSH_FACE,
        "left_tab_rear_max_y_mm": left_tab_max_y,
        "right_tab_rear_max_y_mm": right_tab_max_y,
        "rail_inner_x_mm": X_RAIL_INNER,
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
        f"[FanShroudRecovered R3] Built in {report['build_seconds']}s | vol={report['volume_mm3']} | "
        f"comps={report['components']} solid={report['stl_solid']} nm={report['stl_non_manifolds']} "
        f"si={report['stl_self_intersections']} | tab_max_y=(L:{left_tab_max_y}, R:{right_tab_max_y}) | "
        f"checks={checks}"
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_recovered_shroud_r3()
