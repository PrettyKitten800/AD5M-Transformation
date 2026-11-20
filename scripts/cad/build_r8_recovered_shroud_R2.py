"""Build R8-mounted Fan_Shroud_Recovered revision (R2) for BambuMod x Orbiter v2.5 R8.

Takes reference/AD5M_Lightweight_FanDuct_1404902/Fan_Shroud_Recovered.stl (falling back to
C:/Users/PK800/Desktop/Fan_Shroud_Recovered.stl), archives a print-pose copy, rotates Rx = -90 deg
to R8 display coordinates (-Y = Front, +Y = Back, +Z = Up), translates to its exact mating datum
on R8_Adapter (dx = +0.8024, dy = -49.5939, dz = +0.7037 mm), and verifies zero interference and
clean manifold mesh properties.
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
REF_STL = REPO / "reference" / "AD5M_Lightweight_FanDuct_1404902" / "Fan_Shroud_Recovered.stl"
DESKTOP_STL = Path(r"C:\Users\PK800\Desktop\Fan_Shroud_Recovered.stl")

R8_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
R8_STEP = R8_DIR / "BambuMod_Orbiter25_R8_Live.step"
R8_CACHE = R8_DIR / "cache"

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R2"
PRINT_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_PrintPose_R2.stl"
R8_STL_OUT = OUT_DIR / "Fan_Shroud_Recovered_R8_R2.stl"
REPORT_OUT = OUT_DIR / "r8_recovered_shroud_report.json"

DZ_SHIFT = -14.65
DX_ALIGN = 0.8024
DY_ALIGN = -49.5939
DZ_ALIGN = 0.7037

NOZZLE_TIP = App.Vector(6.335, -11.78, -28.23)
MAGNET_POSITIONS = [(-24.50, -30.04, 3.35), (24.50, -30.04, 3.35)]


def _load_r8_refs() -> dict[str, Part.Shape]:
    """Load R8_Adapter STEP and Z180-rotated display-frame reference BREPs."""
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


def _min_dist_to(mesh_a: Mesh.Mesh, d_pts: np.ndarray, ref_shape: Part.Shape) -> float:
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


def build_recovered_shroud_r2() -> dict:
    """Transform Fan_Shroud_Recovered.stl into R8 display frame and write R2 outputs + report."""
    t0 = time.perf_counter()
    src_path = REF_STL if REF_STL.exists() else DESKTOP_STL
    if not src_path.exists():
        raise FileNotFoundError(f"Missing Fan_Shroud_Recovered.stl at {REF_STL} or {DESKTOP_STL}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, PRINT_STL_OUT)

    mesh = Mesh.Mesh(str(src_path))
    mat = App.Matrix()
    mat.rotateX(-math.pi / 2.0)
    mesh.transform(mat)
    mesh.translate(DX_ALIGN, DY_ALIGN, DZ_ALIGN)
    mesh.write(str(R8_STL_OUT))

    mesh_reload = Mesh.Mesh(str(R8_STL_OUT))
    refs = _load_r8_refs()
    d_pts = np.array([[p.x, p.y, p.z] for p in mesh_reload.Points])

    checks = {
        "shroud_vs_r8_adapter_mm3": _mesh_common_vol(mesh_reload, refs["r8"]),
        "shroud_vs_orbiter_mm3": _mesh_common_vol(mesh_reload, refs["orbiter"]),
        "shroud_vs_x1c_hotend_mm3": _mesh_common_vol(mesh_reload, refs["hotend"]),
        "shroud_vs_3010_fan_mm3": _mesh_common_vol(mesh_reload, refs["fan3010"]),
        "shroud_vs_gray_carriage_mm3": _mesh_common_vol(mesh_reload, refs["carriage"]),
        "min_dist_to_hotend_mm": _min_dist_to(mesh_reload, d_pts, refs["hotend"]),
        "min_dist_to_orbiter_mm": _min_dist_to(mesh_reload, d_pts, refs["orbiter"]),
    }

    bb = mesh_reload.BoundBox
    report = {
        "source_model": str(src_path.name),
        "transform_display_mm": {"rx_deg": -90.0, "dx": DX_ALIGN, "dy": DY_ALIGN, "dz": DZ_ALIGN},
        "nozzle_target_display_mm": [round(NOZZLE_TIP.x, 3), round(NOZZLE_TIP.y, 3), round(NOZZLE_TIP.z, 3)],
        "magnet_mounts_display_mm": [list(p) for p in MAGNET_POSITIONS],
        "bbox": {
            "x": [round(bb.XMin, 4), round(bb.XMax, 4)],
            "y": [round(bb.YMin, 4), round(bb.YMax, 4)],
            "z": [round(bb.ZMin, 4), round(bb.ZMax, 4)],
        },
        "nozzle_bed_clearance_mm": round(bb.ZMin - NOZZLE_TIP.z, 3),
        "volume_mm3": round(float(mesh_reload.Volume), 2),
        "components": int(mesh_reload.countComponents()),
        "stl_solid": bool(mesh_reload.isSolid()),
        "stl_facets": int(mesh_reload.CountFacets),
        "stl_non_manifolds": bool(mesh_reload.hasNonManifolds()),
        "stl_non_uniform_faces": int(mesh_reload.countNonUniformOrientedFacets()),
        "stl_self_intersections": bool(mesh_reload.hasSelfIntersections()),
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"[FanShroudRecovered R2] Built in {report['build_seconds']}s | vol={report['volume_mm3']} | "
        f"comps={report['components']} solid={report['stl_solid']} nm={report['stl_non_manifolds']} "
        f"si={report['stl_self_intersections']} | bed_clear={report['nozzle_bed_clearance_mm']}mm | "
        f"checks={checks}"
    )
    return report


if __name__ == "__main__" or os.environ.get("RUN_MAIN") == "1":
    build_recovered_shroud_r2()
