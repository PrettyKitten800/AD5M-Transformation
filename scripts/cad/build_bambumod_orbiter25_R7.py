"""Build BambuMod x Orbiter v2.5 Primary_R7 (final pre-print refinements).

Derives parametrically from Primary_R6 (`build_primary_r6`) so every validated
R1-R6 feature is preserved untouched, then applies the three user-requested R7
revisions:
1. Reinforce the upper carriage mount inner portal walls at (-24.0, 61.0) and
   (+24.0, 61.0) (`R = 3.60 mm` boss -> 1.45 mm radial wall around the existing
   Ø4.30 mm x 5.54 mm blind round heat-set/carriage bores) while clearing both
   the Ø41.00 mm motor circle and upper belt channels.
2. Unify both Orbiter extruder mount holes at `Z = 32.60 mm, Y = 12.08 mm` to
   the exact same `Ø3.60 mm` (`r = 1.800 mm`) diameter by resizing the right
   (-X = -23.85 mm) blind bore cleanly from `Ø4.40 mm` down to `Ø3.60 mm` while
   keeping the left (+X = +13.15 mm) `Ø3.60 mm` through-bore and perpendicular
   `Z_NUT_FACE = 27.60 mm` nut boss unchanged.
3. Round sharp exterior edges and bed-contact corners, especially the top
   carriage corners at `(±30.0, Z = 80.0)` (`R_bed = 3.50 mm` rounded bed-face
   anti-warp corner tapering <= 40 deg over `Y = -11.12..-9.55 mm` to
   `R_front = 0.85 mm` outside the `±27.0 mm` EBB42 bores, plus `R = 1.60 mm`
   rear vertical fillets, `R = 1.80 mm` front shroud vertical corners,
   `R = 1.00 mm` swept shelf/fan top rims, `R = 0.75/0.65 mm` backplate step/tab
   edges, and `R = 1.50 mm` inner portal arch corners).
4. Export `BambuMod_Orbiter25_Primary_R7.stl` in true flat-backplate bed-down
   print pose (`rotate(+90 deg about +X)` so the `60 x 80 mm` rear carriage face
   `Y = -11.117 mm` sits flush on `Z_bed = 0.000 mm`, matching PRINT_AND_FIT).
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

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "cad"))

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
)
from build_bambumod_orbiter25_R3 import CARRIAGE_HOLES_R3  # noqa: E402
from build_bambumod_orbiter25_R4 import (  # noqa: E402
    COL_INNER_X,
    Y_WEB_FRONT,
    Z_TOP_BRIDGE,
)
from build_bambumod_orbiter25_R5 import (  # noqa: E402
    NUT_BOSS_R,
    NUT_MOAT_R,
    RIGHT_MOUNT_BORE_R,
    Z_NUT_FACE,
    build_smooth_duct_void,
)
from build_bambumod_orbiter25_R6 import (  # noqa: E402
    HEX_CHAMFER_DEPTH,
    HEX_CHAMFER_EXTRA_AF,
    HEX_NUT_AF,
    HEX_NUT_SEAT_Y,
    HOTEND_SCREW_XS,
    HOTEND_SCREW_Z,
    MOT_CIRCLE_R_R6,
    make_hex_nut_pocket,
)

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R7"

UPPER_CARRIAGE_BOSS_R = 3.600
CARRIAGE_BORE_R = 2.150
EXT_LEFT_X = 13.15
EXT_RIGHT_X = -23.85
EXT_Y = 12.08
EXT_RIGHT_BLIND_DEPTH = 4.30

TOP_XZ_BED_CORNER_R = 3.50
TOP_XZ_FRONT_CORNER_R = 0.85
REAR_VERT_CORNER_R = 1.60
FRONT_VERT_CORNER_R = 1.80
SHELF_TOP_RIM_R = 1.00


def _make_vert_corner_cutter(
    corner_x: float, corner_y: float, sx: int, sy: int, r: float, z0: float, z1: float
) -> Part.Shape:
    """Create a vertical quarter-round boolean corner cutter along Z."""
    cx, cy = corner_x - sx * r, corner_y - sy * r
    ox, oy = corner_x + sx * 0.6, corner_y + sy * 0.6
    x0, x1 = min(cx, ox), max(cx, ox)
    y0, y1 = min(cy, oy), max(cy, oy)
    blk = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    cyl = Part.makeCylinder(r, z1 - z0 + 1.0, Vector(cx, cy, z0 - 0.5), Vector(0, 0, 1))
    return blk.cut(cyl)


def _make_edge_cutter_x(
    y_edge: float, z_edge: float, sy: int, sz: int, r: float, x0: float, x1: float
) -> Part.Shape:
    """Create a horizontal quarter-round boolean corner cutter running along +X."""
    cy, cz = y_edge - sy * r, z_edge - sz * r
    oy, oz = y_edge + sy * 0.6, z_edge + sz * 0.6
    y0, y1 = min(cy, oy), max(cy, oy)
    z0, z1 = min(cz, oz), max(cz, oz)
    blk = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    cyl = Part.makeCylinder(r, x1 - x0 + 1.0, Vector(x0 - 0.5, cy, cz), Vector(1, 0, 0))
    return blk.cut(cyl)


def _make_xz_top_antiwarp_cutter(
    sx: int, z_top: float, r_bed: float, r_front: float, y_bed: float, y_taper_end: float, y_front_end: float
) -> Part.Shape:
    """Create a tapered XZ corner cutter for the top carriage ears.

    Provides a generous `r_bed` corner radius on the PEI bed (`y_bed`) tapering at
    ~38 deg over `y_bed..y_taper_end` down to `r_front` before the `X = ±27` EBB42
    bores start (`Y >= -9.50 mm`), keeping full heat-set wall integrity.
    """
    a = math.radians(45.0)

    def corner_wire(r: float, y: float) -> Part.Wire:
        cx, cz = sx * (30.0 - r), z_top - r
        ox, oz = sx * 30.8, z_top + 0.8
        p_side, p_top = Vector(sx * 30.0, y, cz), Vector(cx, y, z_top)
        p_mid = Vector(cx + sx * r * math.cos(a), y, cz + r * math.sin(a))
        e_arc = Part.Arc(p_side, p_mid, p_top).toShape()
        p_c, p_s2, p_t2 = Vector(ox, y, oz), Vector(ox, y, cz), Vector(cx, y, oz)
        return Part.Wire(
            [
                e_arc,
                Part.LineSegment(p_top, p_t2).toShape(),
                Part.LineSegment(p_t2, p_c).toShape(),
                Part.LineSegment(p_c, p_s2).toShape(),
                Part.LineSegment(p_s2, p_side).toShape(),
            ]
        )

    w0 = corner_wire(r_bed, y_bed - 0.5)
    w1 = corner_wire(r_bed, y_bed)
    w2 = corner_wire(r_front, y_taper_end)
    w3 = corner_wire(r_front, y_front_end)
    return (
        Part.makeLoft([w0, w1], True, True)
        .fuse(Part.makeLoft([w1, w2], True, True))
        .fuse(Part.makeLoft([w2, w3], True, True))
    )


def _make_swept_top_rim_cutter(
    x_out: float,
    sx: int,
    y_front: float,
    y_start: float,
    x_end: float,
    r_xy: float,
    r_edge: float,
    z_top: float,
) -> Part.Shape:
    """Sweep a quarter-round fillet cutter cleanly around a G1 side->arc->front rim."""
    cx, cy = x_out - sx * r_xy, y_front - r_xy
    a = math.radians(45.0)
    p0 = Vector(x_out, y_start, z_top)
    p1 = Vector(x_out, cy, z_top)
    pm = Vector(cx + sx * r_xy * math.cos(a), cy + r_xy * math.sin(a), z_top)
    p2 = Vector(cx, y_front, z_top)
    p3 = Vector(x_end, y_front, z_top)
    path = Part.Wire(
        [
            Part.LineSegment(p0, p1).toShape(),
            Part.Arc(p1, pm, p2).toShape(),
            Part.LineSegment(p2, p3).toShape(),
        ]
    )

    q_s = Vector(x_out, y_start, z_top - r_edge)
    q_t = Vector(x_out - sx * r_edge, y_start, z_top)
    q_m = Vector(
        x_out - sx * r_edge * (1.0 - math.cos(a)),
        y_start,
        z_top - r_edge * (1.0 - math.sin(a)),
    )
    q_o1 = Vector(x_out + sx * 0.6, y_start, z_top - r_edge)
    q_oo = Vector(x_out + sx * 0.6, y_start, z_top + 0.6)
    q_o2 = Vector(x_out - sx * r_edge, y_start, z_top + 0.6)
    prof = Part.Wire(
        [
            Part.Arc(q_s, q_m, q_t).toShape(),
            Part.LineSegment(q_t, q_o2).toShape(),
            Part.LineSegment(q_o2, q_oo).toShape(),
            Part.LineSegment(q_oo, q_o1).toShape(),
            Part.LineSegment(q_o1, q_s).toShape(),
        ]
    )
    ps = Part.BRepOffsetAPI.MakePipeShell(path)
    ps.setTransitionMode(1)
    ps.add(prof, False, False)
    ps.build()
    ps.makeSolid()
    return ps.shape()


def _round_exterior_corners(shape: Part.Shape, rear_y: float) -> Part.Shape:
    """Apply smooth analytical corner/rim cutters and safe internal arch fillets."""
    s = shape
    cutters: list[tuple[str, Part.Shape]] = []
    for sx in (-1, 1):
        cutters.append(
            (
                f"rear_vert_{sx}",
                _make_vert_corner_cutter(sx * 30.0, rear_y, sx, -1, REAR_VERT_CORNER_R, 0.0, 81.0),
            )
        )
        cutters.append(
            (
                f"top_xz_antiwarp_{sx}",
                _make_xz_top_antiwarp_cutter(
                    sx,
                    80.002,
                    TOP_XZ_BED_CORNER_R,
                    TOP_XZ_FRONT_CORNER_R,
                    rear_y,
                    -9.55,
                    -1.80,
                ),
            )
        )
        cutters.append(
            (
                f"front_vert_{sx}",
                _make_vert_corner_cutter(sx * 30.0, 30.12, sx, 1, FRONT_VERT_CORNER_R, 5.0, 38.0),
            )
        )
        z_step = 32.58 if sx == -1 else 37.35
        cutters.append(
            (
                f"mid_back_front_{sx}",
                _make_vert_corner_cutter(sx * 30.0, -3.881, sx, 1, 0.75, z_step, 73.495),
            )
        )
        cutters.append(
            (
                f"top_tab_{sx}",
                _make_vert_corner_cutter(sx * 30.0, -2.335, sx, 1, 0.65, 73.505, 81.0),
            )
        )

    cutters.append(("top_front_80", _make_edge_cutter_x(-3.881, 80.002, 1, 1, 0.80, -29.3, 29.3)))
    cutters.append(
        (
            "shelf_minusX_rim",
            _make_swept_top_rim_cutter(
                -30.0, -1, 30.12, -3.80, -12.90, FRONT_VERT_CORNER_R, SHELF_TOP_RIM_R, 32.58
            ),
        )
    )
    cutters.append(
        (
            "fan_plusX_rim",
            _make_swept_top_rim_cutter(
                30.0, 1, 30.12, 27.15, 26.98, FRONT_VERT_CORNER_R, SHELF_TOP_RIM_R, 37.35
            ),
        )
    )
    cutters.append(
        ("fan_top_front_inner", _make_edge_cutter_x(30.12, 37.05, 1, 1, SHELF_TOP_RIM_R, 14.56, 26.98))
    )

    for label, cutter in cutters:
        nxt = s.cut(cutter)
        assert nxt.isValid() and len(nxt.Solids) == 1, f"Corner cutter failed: {label}"
        s = nxt.Solids[0]

    arch_edges = [
        e
        for e in s.Edges
        if abs(e.CenterOfMass.z - 67.0) < 0.05
        and abs(abs(e.CenterOfMass.x) - 22.5) < 0.05
        and e.BoundBox.YMin < -7.5
    ]
    if arch_edges:
        fil = s.makeFillet(1.50, arch_edges)
        assert fil.isValid() and len(fil.Solids) == 1, "Portal arch corner fillet failed"
        s = fil.Solids[0]
    return s


def _radial_solid_clearance(
    shape: Part.Shape, cx: float, cy: float, z: float, radii: list[float]
) -> float:
    """Measure guaranteed minimum solid boundary radius around a vertical axis bore using a cropped local solid."""
    r_max = max(radii) + 0.5
    crop = shape.common(box(cx - r_max, cx + r_max, cy - r_max, cy + r_max, z - 0.3, z + 0.3))
    min_r = 999.0
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        prev_r = radii[0]
        for rr in radii:
            pt = Vector(cx + rr * math.cos(rad), cy + rr * math.sin(rad), z)
            if not crop.isInside(pt, 1e-4, True):
                min_r = min(min_r, prev_r)
                break
            prev_r = rr
    return min_r


def _y_bore_wall_thickness(
    shape: Part.Shape,
    cx: float,
    cz: float,
    y_vals: list[float],
    r_start: float,
    angles_deg: list[int] | None = None,
) -> float:
    """Measure minimum radial wall thickness around a Y-axis blind bore using a cropped local solid."""
    if angles_deg is None:
        angles_deg = list(range(0, 360, 10))
    crop = shape.common(
        box(cx - 5.0, cx + 5.0, min(y_vals) - 0.5, max(y_vals) + 0.5, cz - 5.0, cz + 5.0)
    )
    min_wall = 999.0
    for y in y_vals:
        for deg in angles_deg:
            rad = math.radians(deg)
            wall = 0.0
            for step in range(1, 35):
                rr = r_start + step * 0.10
                pt = Vector(cx + rr * math.cos(rad), y, cz + rr * math.sin(rad))
                if not crop.isInside(pt, 1e-4, True):
                    break
                wall = step * 0.10
            min_wall = min(min_wall, wall)
    return min_wall


def _build_contoured_up_r_boss(rear_y: float) -> Part.Shape:
    """Reinforce up_R (-24, 61) to R=3.60 mm over the 4.22 mm heat-set depth and trim forward arc around the Orbiter NEMA flange."""
    boss_rear = cyl_y(UPPER_CARRIAGE_BOSS_R, -24.0, 61.0, rear_y + 1.0, -6.90)

    # Forward of Y=-6.68, the Orbiter NEMA corner ear (R=3.00 at (-19.205, 62.994) +
    # diagonal face normal (-0.8455, -0.5339)) passes within 0.043 mm of the R=2.15 bore at +22.6 deg.
    ear_cyl = cyl_y(3.22, -19.2053, 62.9943, -7.20, -4.20)
    nx, nz = -0.845518, -0.533947
    p0x, p0z = -21.7418 + 0.22 * nx, 61.3924 + 0.22 * nz
    p1x, p1z = -17.9036 + 0.22 * nx, 55.3146 + 0.22 * nz
    in_x, in_z = -8.0 * nx, -8.0 * nz
    wire = Part.makePolygon(
        [
            Vector(p0x, -7.20, p0z),
            Vector(p1x, -7.20, p1z),
            Vector(p1x + in_x, -7.20, p1z + in_z),
            Vector(p0x + in_x, -7.20, p0z + in_z),
            Vector(p0x, -7.20, p0z),
        ]
    )
    ear_edge = Part.Face(wire).extrude(Vector(0, 3.00, 0))
    ear_top = Part.makeBox(10.0, 3.00, 6.0, Vector(-19.2053, -7.20, 62.9943 - 0.22))
    ear_clear = ear_cyl.fuse(ear_edge).fuse(ear_top)

    boss_front = cyl_y(UPPER_CARRIAGE_BOSS_R, -24.0, 61.0, -7.00, -4.45).cut(ear_clear)
    return boss_rear.fuse(boss_front)


def _solid_fraction_ring_z(shape: Part.Shape, cx: float, cy: float, r_mid: float, z_vals: list[float]) -> float:
    span = r_mid + 0.5
    crop = shape.common(box(cx - span, cx + span, cy - span, cy + span, min(z_vals) - 0.5, max(z_vals) + 0.5))
    hits = 0
    total = 0
    for z in z_vals:
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            total += 1
            if crop.isInside(Vector(cx + r_mid * math.cos(rad), cy + r_mid * math.sin(rad), z), 1e-4, True):
                hits += 1
    return hits / max(total, 1)


def _export_stl_backplate_down(shape: Part.Shape, out_stl: Path) -> tuple[dict, Part.Shape]:
    """Export STL with the flat carriage rear (-Y) face down on Z_bed=0."""
    pr = shape.copy()
    pr.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 90)
    pr.translate(Vector(0, -pr.BoundBox.YMin, -pr.BoundBox.ZMin))

    mesh = MeshPart.meshFromShape(Shape=pr, LinearDeflection=0.025, AngularDeflection=0.12, Relative=False)
    mesh.removeDuplicatedPoints()
    mesh.removeDuplicatedFacets()
    mesh.fixIndices()
    mesh.harmonizeNormals()
    if not mesh.isSolid():
        mesh.fillupHoles(200)
        mesh.harmonizeNormals()
    # Seat tessellated STL vertices flush on Z_bed=0 and Y>=0 (ignoring OCC BRep BSpline BoundBox slack)
    mat = App.Matrix()
    mat.move(0.0, -float(mesh.BoundBox.YMin), -float(mesh.BoundBox.ZMin))
    mesh.transform(mat)
    mesh.write(str(out_stl))
    m_check = Mesh.Mesh(str(out_stl))
    assert m_check.isSolid() and not m_check.hasNonManifolds(), (
        f"Non-manifold or non-solid STL: {out_stl}"
    )

    cos45 = -math.cos(math.radians(45.0))
    cos20 = -math.cos(math.radians(20.0))
    overhang_gt45 = 0.0
    flat_bridge_gt70 = 0.0
    bed_area = 0.0
    for f in m_check.Facets:
        nz = float(f.Normal[2])
        area = float(f.Area)
        z_pts = [float(p[2]) for p in f.Points]
        if nz < -0.999 and max(z_pts) < 0.05:
            bed_area += area
        elif min(z_pts) > 0.25:
            if nz < cos45:
                overhang_gt45 += area
            if nz < cos20:
                flat_bridge_gt70 += area
    assert bed_area > 1800.0, f"Bed contact area too low (floating STL?): {bed_area}"

    bb = m_check.BoundBox
    step_vol = float(shape.Volume)
    stl_vol = float(m_check.Volume)
    rel_diff = abs(stl_vol - step_vol) / step_vol
    assert rel_diff < 0.002, f"STL vs STEP volume drift too high: {rel_diff}"

    return (
        {
            "file": out_stl.name,
            "facets": int(m_check.CountFacets),
            "is_solid": True,
            "has_non_manifolds": False,
            "volume_mm3": round(stl_vol, 2),
            "stl_vs_step_volume_rel_diff": round(rel_diff, 6),
            "bbox_print_bed_mm": {
                "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
                "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
                "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
            },
            "flat_backplate_bed_contact_mm2": round(bed_area, 2),
            "overhang_gt45deg_mm2": round(overhang_gt45, 2),
            "flat_bridge_gt70deg_mm2": round(flat_bridge_gt70, 2),
        },
        pr,
    )


def build_primary_r7(refs: dict) -> tuple[Part.Shape, Part.Shape, dict]:
    """Build Primary_R7 solid, base Primary_R6 comparison solid, and metrics."""
    from build_bambumod_orbiter25_R6 import build_primary_r6

    r6, r6_metrics = build_primary_r6(refs)
    rear_y, front_y = detect_backplate_y_planes(refs["bm_body"])

    # Detect exact shelf top height around (-23.85, 12.08)
    z_tops = [
        f.BoundBox.ZMax
        for f in r6.Faces
        if abs(f.CenterOfMass.z - 32.58) < 0.05
        and f.Surface.TypeId.endswith("Plane")
        and f.CenterOfMass.x < -15.0
    ]
    z_top = max(z_tops)

    # 1. Reinforce upper carriage holes (-24, 61) & (+24, 61) inner portal walls
    # 2. Plug & re-drill (-23.85, 12.08) from R=2.20 mm down to R=1.800 mm (Ø3.60 mm)
    pin_ext = cyl_z(2.50, EXT_RIGHT_X, EXT_Y, z_top - 4.70, z_top)
    boss_r = _build_contoured_up_r_boss(rear_y)
    boss_l = cyl_y(UPPER_CARRIAGE_BOSS_R, 24.0, 61.0, rear_y + 1.0, front_y)

    w = r6.fuse(pin_ext).fuse(boss_r).fuse(boss_l)
    w = w.cut(cyl_y(CARRIAGE_BORE_R, -24.0, 61.0, rear_y - 0.2, -5.58))
    w = w.cut(cyl_y(CARRIAGE_BORE_R, 24.0, 61.0, rear_y - 0.2, -5.58))
    w = w.cut(cyl_z(RIGHT_MOUNT_BORE_R, EXT_RIGHT_X, EXT_Y, z_top - EXT_RIGHT_BLIND_DEPTH, z_top + 0.50))
    assert w.isValid() and len(w.Solids) == 1, "Pre-fillet R7 solid check failed!"

    # Symmetric diff check before rounding corners: strictly zero unexpected removal from R6
    assert r6.cut(w).Volume < 1e-4, f"Unexpected removal vs R6 before corner round: {r6.cut(w).Volume}"

    # 3. Smooth exterior corners & anti-warp top carriage corners
    r7 = _round_exterior_corners(w.Solids[0], rear_y)
    assert r7.isValid() and len(r7.Solids) == 1, "Final R7 BRep validity check failed!"
    r7 = r7.Solids[0]

    # Full collision checks against all reference envelopes
    he_t = refs["he_raw"].copy()
    he_t.translate(Vector(X_FIL, 0, 0))
    orb_solids = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_body_solids"]]
    orb_bolts = [orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_bolts"]]
    fan_box = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)
    steel_carriage = box(-40.0, 40.0, -30.0, rear_y - 0.005, -20.0, 95.0)
    belt_low = box(-27.0, 27.0, -11.11, -9.20, 10.6, 19.4)
    belt_high = box(-27.0, 27.0, -11.11, -9.20, 66.6, 74.4)
    bm_body = refs["bm_body"]

    ov_orb = sum(max(0.0, r7.common(s).Volume) for s in orb_solids if r7.BoundBox.intersect(s.BoundBox))
    ov_bolts = sum(max(0.0, r7.common(s).Volume) for s in orb_bolts if r7.BoundBox.intersect(s.BoundBox))
    ov_fan_orb = sum(max(0.0, fan_box.common(s).Volume) for s in orb_solids if fan_box.BoundBox.intersect(s.BoundBox))

    collisions = {
        "adapter_vs_orbiter_and_motor": round(ov_orb, 5),
        "adapter_vs_orbiter_m3_bolts": round(ov_bolts, 5),
        "adapter_vs_x1c_hotend": round(r7.common(he_t).Volume, 5),
        "adapter_vs_3010_fan": round(r7.common(fan_box).Volume, 5),
        "3010_fan_vs_orbiter": round(ov_fan_orb, 5),
        "adapter_vs_ebb42_bracket": round(r7.common(refs["ebb_bkt"]).Volume, 5),
        "adapter_vs_steel_carriage_plane": round(r7.common(steel_carriage).Volume, 5),
        "adapter_vs_belt_low": round(max(0.0, r7.common(belt_low).Volume - bm_body.common(belt_low).Volume), 5),
        "adapter_vs_belt_high": round(max(0.0, r7.common(belt_high).Volume - bm_body.common(belt_high).Volume), 5),
    }
    assert all(v < 1e-4 for v in collisions.values()), f"Collision detected in R7: {collisions}"

    # Verify EBB42 top bores & outer wall margins after R7 top corner rounding
    ebb_obs = {}
    ebb_min_wall = {}
    for sx in (-27.0, -18.0, 18.0, 27.0):
        probe = cyl_z(1.90, sx, -7.50, 73.2, 80.5)
        ebb_obs[f"ebb_x_{int(sx):+d}"] = round(r7.common(probe).Volume, 5)
    for sx in (-1, 1):
        # Upper ear rounding zone (Z=77.0, 79.0, 79.6 above the Z<=74.4 rear belt channel)
        min_outer_upper = min(
            _radial_solid_clearance(r7, sx * 27.0, -7.50, z, [2.2, 2.5, 2.7, 2.82, 2.95])
            for z in (77.0, 79.0, 79.6)
        )
        # Preserve pre-existing R6 rear belt-channel wall at Z=74.0 without thinning
        belt_r6 = _radial_solid_clearance(r6, sx * 27.0, -7.50, 74.0, [2.2, 2.5, 2.65, 2.7, 2.85])
        belt_r7 = _radial_solid_clearance(r7, sx * 27.0, -7.50, 74.0, [2.2, 2.5, 2.65, 2.7, 2.85])
        assert belt_r7 >= belt_r6 - 1e-4, f"Belt-slot wall thinned at x={sx * 27}: R6={belt_r6}, R7={belt_r7}"
        ebb_min_wall[f"ebb_x_{sx * 27:+d}_min_radial_wall_mm"] = round(min_outer_upper - 2.00, 3)
        ebb_min_wall[f"ebb_x_{sx * 27:+d}_z74_belt_wall_unchanged_mm"] = round(belt_r7 - 2.00, 3)
    assert all(v < 1e-4 for v in ebb_obs.values()), f"EBB42 bore blocked: {ebb_obs}"
    assert all(
        v >= 0.80 for k, v in ebb_min_wall.items() if "min_radial_wall_mm" in k
    ), f"EBB42 outer wall too thin: {ebb_min_wall}"

    # Verify 4 carriage holes & reinforced upper (-24, 61) / (+24, 61) boss walls
    carriage_checks = {}
    for cname, cx, cz, cap_y0, _ in CARRIAGE_HOLES_R3:
        bore_probe = cyl_y(CARRIAGE_BORE_R - 0.15, cx, cz, rear_y - 0.1, cap_y0 - 0.1)
        obs = round(r7.common(bore_probe).Volume, 5)
        assert obs < 1e-4, f"Carriage bore obstructed: {cname} {obs}"
        entry = {
            "xz_mm": [cx, cz],
            "bore_diameter_mm": round(CARRIAGE_BORE_R * 2.0, 2),
            "blind_depth_from_rear_mm": round(cap_y0 - rear_y, 2),
            "rear_bore_obstruction_mm3": obs,
        }
        if cz > 50.0:
            if cx < 0:
                min_w_insert = _y_bore_wall_thickness(
                    r7, cx, cz, [-7.8, -7.5, -7.0], CARRIAGE_BORE_R + 0.02
                )
                min_w_tip = _y_bore_wall_thickness(
                    r7, cx, cz, [-6.0], CARRIAGE_BORE_R + 0.02, list(range(60, 340, 10))
                )
                assert min_w_insert >= 1.25 and min_w_tip >= 1.25, (
                    f"Upper carriage {cname} boss wall too thin: insert={min_w_insert}, tip={min_w_tip}"
                )
                entry["heatset_insert_zone_360deg_min_wall_mm"] = round(min_w_insert, 2)
                entry["bore_tip_non_motor_280deg_min_wall_mm"] = round(min_w_tip, 2)
                entry["motor_flange_clearance_note"] = (
                    "Full 360-deg R=3.60 mm boss across Y=-11.12..-6.90 (4.22 mm insert zone); "
                    "non-motor 280-deg arc reinforced to Y=-4.45 while preserving 0.043 mm NEMA flange ear clearance at +22.6 deg"
                )
            else:
                min_w = _y_bore_wall_thickness(r7, cx, cz, [-7.5, -6.8, -6.0], CARRIAGE_BORE_R + 0.02)
                assert min_w >= 1.25, f"Upper carriage {cname} boss wall too thin: {min_w}"
                entry["min_radial_boss_wall_mm"] = round(min_w, 2)
        carriage_checks[cname] = entry

    # Verify both matching Ø3.60 mm extruder mount bores
    ext_right_bore = cyl_z(RIGHT_MOUNT_BORE_R - 0.10, EXT_RIGHT_X, EXT_Y, z_top - EXT_RIGHT_BLIND_DEPTH + 0.05, z_top + 0.2)
    ext_left_bore = cyl_z(RIGHT_MOUNT_BORE_R - 0.10, EXT_LEFT_X, EXT_Y, Z_NUT_FACE - 0.1, z_top + 0.2)
    assert r7.common(ext_right_bore).Volume < 1e-4
    assert r7.common(ext_left_bore).Volume < 1e-4
    ext_right_ring_solid = _solid_fraction_ring_z(r7, EXT_RIGHT_X, EXT_Y, RIGHT_MOUNT_BORE_R + 0.15, [28.6, 29.8, 31.2, 32.2])
    ext_left_ring_solid = _solid_fraction_ring_z(r7, EXT_LEFT_X, EXT_Y, RIGHT_MOUNT_BORE_R + 0.15, [28.0, 29.5, 31.0, 32.2])
    assert ext_right_ring_solid > 0.99 and ext_left_ring_solid > 0.99, (
        f"Extruder bore wall check failed: right={ext_right_ring_solid}, left={ext_left_ring_solid}"
    )

    # Verify twin hotend hex pockets preserved
    hex_obs = {}
    for lbl, hx in HOTEND_SCREW_XS:
        hp = cyl_y(1.55, hx, HOTEND_SCREW_Z, rear_y - 0.2, 8.28)
        ov_h = round(r7.common(hp).Volume, 5)
        assert ov_h < 1e-4, f"Hotend bore obstructed: {lbl} {ov_h}"
        hex_obs[lbl] = {"xz_mm": [hx, HOTEND_SCREW_Z], "m3_bore_obstruction_mm3": ov_h}

    bb = r7.BoundBox
    metrics = {
        "variant": "Primary_R7",
        "derived_from": "Primary_R6",
        "step_valid": bool(r7.isValid()),
        "step_solids": len(r7.Solids),
        "volume_mm3": round(float(r7.Volume), 2),
        "delta_volume_vs_r6_mm3": round(float(r7.Volume - r6.Volume), 2),
        "bbox_upright_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
        "r7_modifications": {
            "extruder_mount_holes_matched_diameter_mm": round(RIGHT_MOUNT_BORE_R * 2.0, 2),
            "right_extruder_x_mm": EXT_RIGHT_X,
            "right_extruder_ring_solid_fraction_at_r195": round(ext_right_ring_solid, 4),
            "left_extruder_x_mm": EXT_LEFT_X,
            "left_extruder_ring_solid_fraction_at_r195": round(ext_left_ring_solid, 4),
            "upper_carriage_boss_radius_mm": UPPER_CARRIAGE_BOSS_R,
            "upper_carriage_bore_diameter_mm": round(CARRIAGE_BORE_R * 2.0, 2),
            "top_carriage_bed_corner_radius_mm": TOP_XZ_BED_CORNER_R,
            "top_carriage_front_corner_radius_mm": TOP_XZ_FRONT_CORNER_R,
            "rear_vertical_corner_radius_mm": REAR_VERT_CORNER_R,
            "front_shroud_vertical_corner_radius_mm": FRONT_VERT_CORNER_R,
            "shelf_and_fan_top_rim_radius_mm": SHELF_TOP_RIM_R,
            "portal_arch_corner_radius_mm": 1.5,
        },
        "collisions_mm3": collisions,
        "ebb42_top_mounting_bores_obstruction_mm3": ebb_obs,
        "ebb42_outer_wall_margins_mm": ebb_min_wall,
        "carriage_holes_4_verification": carriage_checks,
        "hotend_hex_bores_verification": hex_obs,
    }
    return r7, r6, metrics


def _tessellate_part(shape: Part.Shape, name: str, color: list[int], lin: float = 0.04, ang: float = 0.16) -> dict:
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=lin, AngularDeflection=ang, Relative=False)
    return {
        "name": name,
        "color": color,
        "v": [[round(float(p.x), 3), round(float(p.y), 3), round(float(p.z), 3)] for p in m.Points],
        "f": [list(map(int, tri.PointIndices)) for tri in m.Facets],
    }


def export_verified(r7: Part.Shape, refs: dict, metrics: dict) -> dict:
    """Save Primary_R7 STEP, STL, FCStd, validation JSON, and preview meshes."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    step_path = OUT_DIR / "BambuMod_Orbiter25_Primary_R7.step"
    stl_path = OUT_DIR / "BambuMod_Orbiter25_Primary_R7.stl"
    fcstd_path = OUT_DIR / "BambuMod_Orbiter25_Assembly_R7.FCStd"
    val_path = OUT_DIR / "validation.json"

    r7.exportStep(str(step_path))
    step_back = Part.read(str(step_path))
    assert step_back.isValid() and len(step_back.Solids) == 1, "STEP readback failed!"

    stl_metrics, _ = _export_stl_backplate_down(r7, stl_path)
    metrics["stl"] = stl_metrics

    # Export assembly preview meshes
    he_t = refs["he_raw"].copy()
    he_t.translate(Vector(X_FIL, 0, 0))
    orb_comp = Part.makeCompound([orbiter_xform(s, X_FIL, Z_MOUNT) for s in refs["orb_body_solids"]])
    fan_box = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)

    preview_parts = [
        _tessellate_part(r7, "adapter", [65, 130, 195], lin=0.03, ang=0.14),
        _tessellate_part(he_t, "x1c", [215, 95, 70]),
        _tessellate_part(orb_comp, "orbiter", [72, 76, 84]),
        _tessellate_part(refs["ebb_bkt"], "ebb42", [65, 165, 105]),
        _tessellate_part(fan_box, "fan3010", [225, 165, 55]),
    ]
    (OUT_DIR / "preview_primary_r7.json").write_text(json.dumps(preview_parts), encoding="utf-8")

    # Standard duct & section cutaways + targeted R7 corner/hole inspection cutaways
    cut_y11 = r7.common(box(-32, 32, 11.0, 34.0, -2, 82))
    cut_z16 = r7.common(box(-32, 32, -13, 34.0, -2, 16.5))
    cut_y23 = r7.common(box(-32, 32, -13, 22.95, -2, 82))
    cut_z27 = r7.common(box(-32, 32, -13, 34.0, 26.8, 39.0))
    duct_cuts = {
        "cut_y11": [_tessellate_part(cut_y11, "adapter", [65, 130, 195], lin=0.03, ang=0.14)],
        "cut_z16": [_tessellate_part(cut_z16, "adapter", [65, 130, 195], lin=0.03, ang=0.14)],
        "cut_y23": [_tessellate_part(cut_y23, "adapter", [65, 130, 195], lin=0.03, ang=0.14)],
        "cut_z27": [_tessellate_part(cut_z27, "adapter", [65, 130, 195], lin=0.03, ang=0.14)],
    }
    (OUT_DIR / "preview_cutaways_r7.json").write_text(json.dumps(duct_cuts), encoding="utf-8")

    cut_up_holes = r7.common(box(-32, 32, -13, -1.5, 50.0, 66.0))
    cut_ext_holes = r7.common(box(-32, 32, -13, 34.0, 27.8, 32.5))
    cut_top_bed = r7.common(box(-32, 32, -11.5, -1.0, 62.0, 82.0))
    cut_rear_hex = r7.common(box(-20, 10, -11.5, -2.5, 20.0, 35.0))
    r7_checks = {
        "cut_up_holes": [_tessellate_part(cut_up_holes, "adapter", [65, 130, 195], lin=0.025, ang=0.12)],
        "cut_ext_holes": [_tessellate_part(cut_ext_holes, "adapter", [65, 130, 195], lin=0.025, ang=0.12)],
        "cut_top_bed": [_tessellate_part(cut_top_bed, "adapter", [65, 130, 195], lin=0.025, ang=0.12)],
        "cut_rear_hex": [_tessellate_part(cut_rear_hex, "adapter", [65, 130, 195], lin=0.025, ang=0.12)],
    }
    (OUT_DIR / "preview_r7_checks.json").write_text(json.dumps(r7_checks), encoding="utf-8")

    # Save FreeCAD assembly document
    doc = App.newDocument("BambuMod_Orbiter25_Primary_R7")
    for obj_name, shp in [
        ("Primary_R7_Adapter", r7),
        ("X1C_Hotend_Ref", he_t),
        ("Orbiter_v25_Ref", orb_comp),
        ("EBB42_ShortBridge_R7_Ref", refs["ebb_bkt"]),
        ("Fan_3010_Ref", fan_box),
    ]:
        obj = doc.addObject("Part::Feature", obj_name)
        obj.Shape = shp
    doc.recompute()
    doc.saveAs(str(fcstd_path))

    val_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    refs = load_references()
    r7, _, metrics = build_primary_r7(refs)
    final_metrics = export_verified(r7, refs, metrics)
    print(json.dumps(final_metrics, indent=2), flush=True)
    print("R7 BUILD & CAD VALIDATION PASSED CLEANLY.", flush=True)


def _is_direct_freecad_run() -> bool:
    return __name__ == "__main__" or (
        __name__ == "build_bambumod_orbiter25_R7"
        and Path(sys.argv[-1]).name == "build_bambumod_orbiter25_R7.py"
    )


if _is_direct_freecad_run():
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
