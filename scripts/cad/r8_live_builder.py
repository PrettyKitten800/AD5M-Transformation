"""Fast cached parametric builder and FreeCAD live workspace for BambuMod x Orbiter v2.5 R8.

Maintains R1-R7 untouched. Caches static R7 split solids and reference shapes as BREPs once,
then rebuilds R8 + full interference report + native FreeCAD VarSet workspace in ~3-5 seconds.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import FreeCAD as App
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "cad"))

import build_bambumod_orbiter25_R1 as r1
import build_bambumod_orbiter25_R3 as r3
import build_bambumod_orbiter25_R4 as r4
import build_bambumod_orbiter25_R6 as r6

OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R8"
CACHE_DIR = OUT_DIR / "cache"
WEB_MESH_DIR = OUT_DIR / "web_meshes"
PARAMS_PATH = OUT_DIR / "r8_params.json"
LIVE_STEP_PATH = OUT_DIR / "BambuMod_Orbiter25_R8_Live.step"
LIVE_STL_PATH = OUT_DIR / "BambuMod_Orbiter25_R8_Live.stl"
FCSTD_PATH = OUT_DIR / "R8_Live_Workspace.FCStd"
REPORT_PATH = OUT_DIR / "r8_live_report.json"

R7_FCSTD_PATH = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R7" / "BambuMod_Orbiter25_Assembly_R7.FCStd"

Y_REAR_MATING = -11.117
Y_FRONT_BP = -3.881
Y_WEB_FRONT = getattr(r4, "Y_WEB_FRONT", -7.85)
COL_INNER_X = getattr(r4, "COL_INNER_X", 22.5)
BASE_Z_MOT = 51.9
BASE_Z_MOUNT = 32.6
BASE_HOTEND_SCREW_Z = float(r6.HOTEND_SCREW_Z)
GRAY_CARRIAGE_BORE_Z = 37.25

DEFAULT_PARAMS: dict[str, Any] = {
    "extruder_hotend_z_shift_mm": -14.65,
    "motor_circle_diameter_mm": 39.0,
    "orbiter_flank_clearance_mm": 0.4,
    "oval_cutout_enabled": True,
    "oval_z_center_mm": 68.5,
    "oval_height_mm": 10.0,
    "oval_width_mm": 22.0,
    "oval_cut_full_depth": True,
    "carriage_hole_access_cutouts": False,
    "duct_sleeve_radius_mm": 4.4,
    "access_bore_radius_mm": 3.1,
    "hotend_wire_cutout_extra_x_mm": 7.1,
    "simplify_hotend_fan_duct": True,
    "carriage_hex_nut_pockets": True,
    "carriage_hex_nut_af_mm": 5.6,
    "lower_rear_flush_extension": True,
    "show_carriage_mockup": True,
    "show_reference_parts": True,
    "export_stl": False,
}

CACHE_FILES = {
    "bp_blank": "bp_blank.brep",
    "front_toolhead": "front_toolhead_r7.brep",
    "ref_orbiter": "ref_orbiter.brep",
    "ref_hotend": "ref_hotend.brep",
    "ref_hotend_fast": "ref_hotend_fast.brep",
    "ref_ebb42": "ref_ebb42.brep",
    "ref_fan3010": "ref_fan3010.brep",
    "ref_carriage": "ref_gray_carriage.brep",
    "ref_knubs": "ref_carriage_knubs.brep",
    "ref_belts": "ref_belts_keepout.brep",
}


def make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    """Create an axis-aligned solid box safely."""
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def make_cyl_y(x: float, z: float, r: float, y0: float, y1: float) -> Part.Shape:
    """Create a cylinder oriented along +Y from y0 to y1."""
    return Part.makeCylinder(r, y1 - y0, App.Vector(x, y0, z), App.Vector(0, 1, 0))


def make_stadium_y(cx: float, cz: float, width: float, height: float, y0: float, y1: float) -> Part.Shape:
    """Create a clean extruded horizontal stadium (oval slot) solid along +Y with zero boolean seams."""
    radius = max(0.5, min(height * 0.5, width * 0.5 - 0.01))
    return make_rounded_rect_y(cx, cz, width, height, radius, y0, y1)


def make_rounded_rect_y(cx: float, cz: float, width: float, height: float, corner_r: float, y0: float, y1: float) -> Part.Shape:
    """Create a clean extruded rounded rectangle solid along +Y with zero boolean seams."""
    r = max(0.2, min(corner_r, width * 0.5 - 0.01, height * 0.5 - 0.01))
    hw, hh = width * 0.5, height * 0.5
    p1 = App.Vector(cx - hw + r, y0, cz + hh)
    p2 = App.Vector(cx + hw - r, y0, cz + hh)
    p3 = App.Vector(cx + hw, y0, cz + hh - r)
    p4 = App.Vector(cx + hw, y0, cz - hh + r)
    p5 = App.Vector(cx + hw - r, y0, cz - hh)
    p6 = App.Vector(cx - hw + r, y0, cz - hh)
    p7 = App.Vector(cx - hw, y0, cz - hh + r)
    p8 = App.Vector(cx - hw, y0, cz + hh - r)
    d = r * (1.0 - math.sqrt(0.5))
    c_tr = App.Vector(cx + hw - d, y0, cz + hh - d)
    c_br = App.Vector(cx + hw - d, y0, cz - hh + d)
    c_bl = App.Vector(cx - hw + d, y0, cz - hh + d)
    c_tl = App.Vector(cx - hw + d, y0, cz + hh - d)
    wire = Part.Wire([
        Part.LineSegment(p1, p2).toShape(),
        Part.Arc(p2, c_tr, p3).toShape(),
        Part.LineSegment(p3, p4).toShape(),
        Part.Arc(p4, c_br, p5).toShape(),
        Part.LineSegment(p5, p6).toShape(),
        Part.Arc(p6, c_bl, p7).toShape(),
        Part.LineSegment(p7, p8).toShape(),
        Part.Arc(p8, c_tl, p1).toShape(),
    ])
    return Part.Face(wire).extrude(App.Vector(0.0, y1 - y0, 0.0))


def build_gray_carriage_mockup() -> tuple[Part.Shape, Part.Shape, Part.Shape]:
    """Construct ruler-measured AD5M gray carriage, twin top knubs, and belts keepout solids."""
    # Main plate: X [-30, 30], Z [0, 76], mating plane at Y = -11.117
    plate = make_box(-30.0, 30.0, -16.5, Y_REAR_MATING, 0.0, 76.0)
    # Notched waist & top corners matching AD5M carriage silhouette from photos
    notches = Part.makeCompound([
        make_box(-31.0, -14.0, -17.0, Y_REAR_MATING + 0.5, -1.0, 1.5),
        make_box(14.0, 31.0, -17.0, Y_REAR_MATING + 0.5, -1.0, 1.5),
        make_box(-13.0, 13.0, -17.0, Y_REAR_MATING + 0.5, -1.0, 4.5),
        make_box(-31.0, -25.0, -17.0, Y_REAR_MATING + 0.5, 10.0, 52.0),
        make_box(25.0, 31.0, -17.0, Y_REAR_MATING + 0.5, 10.0, 52.0),
    ])
    # Motor pocket housing rear wall: internal depth ~17.2 mm behind Y = -11.117
    cavity_housing = make_cyl_y(0.0, GRAY_CARRIAGE_BORE_Z, 21.0, Y_REAR_MATING - 20.0, -16.2)
    carriage = plate.cut(notches).fuse(cavity_housing)

    # Stepped circular motor bore: front lip ~34.8 mm ID (20.0..54.5 mm), rear pocket ~37.5 mm ID
    bore_front_lip = make_cyl_y(0.0, GRAY_CARRIAGE_BORE_Z, 17.4, -15.0, Y_REAR_MATING + 0.5)
    bore_rear_pocket = make_cyl_y(0.0, GRAY_CARRIAGE_BORE_Z, 18.75, Y_REAR_MATING - 17.2, -14.8)
    holes = [bore_front_lip, bore_rear_pocket]
    for _name, hx, hz, _y_cb, _cb_r in r3.CARRIAGE_HOLES_R3:
        holes.append(make_cyl_y(hx, hz, 1.55, -17.0, Y_REAR_MATING + 0.5))
    carriage = carriage.cut(Part.makeCompound(holes))

    # Twin top protruding knubs (measured Z ≈ 64..71 mm, X ≈ +-5 mm, ~3.1 mm forward +Y)
    knub_l = make_cyl_y(-5.0, 67.5, 3.4, Y_REAR_MATING - 1.0, Y_REAR_MATING + 3.1)
    knub_r = make_cyl_y(5.0, 67.5, 3.4, Y_REAR_MATING - 1.0, Y_REAR_MATING + 3.1)
    knubs = knub_l.fuse(knub_r)
    carriage = carriage.fuse(knubs)

    # Upper and lower GT2 belt keepout envelopes inside the open carriage channels (|X| <= 27.5)
    belts = Part.makeCompound([
        make_box(-27.5, 27.5, Y_REAR_MATING, -9.90, 13.0, 17.0),
        make_box(-27.5, 27.5, Y_REAR_MATING, -9.90, 68.0, 73.0),
    ])
    return carriage, knubs, belts


def _keep_significant_solids(shape: Part.Shape, min_vol: float = 5.0) -> Part.Shape:
    """Filter out micro-sliver artifacts (< min_vol mm3) left by grazing OCCT cuts."""
    solids = [s for s in shape.Solids if s.Volume >= min_vol]
    if not solids:
        return shape
    if len(solids) == 1:
        return solids[0]
    return solids[0].multiFuse(solids[1:])


def init_cache(force: bool = False) -> None:
    """Extract and heal static BREPs from R7 Assembly FCStd into OUT_DIR/cache."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not force and all((CACHE_DIR / fn).exists() for fn in CACHE_FILES.values()):
        return

    if not R7_FCSTD_PATH.exists():
        raise FileNotFoundError(f"Missing R7 FCStd source at {R7_FCSTD_PATH}")

    t0 = time.perf_counter()
    doc = App.openDocument(str(R7_FCSTD_PATH))
    try:
        r7_shape = _bake_placement(doc.getObject("Primary_R7_Adapter").Shape)
        ref_hotend = _bake_placement(doc.getObject("X1C_Hotend_Ref").Shape)
        ref_orbiter = _bake_placement(doc.getObject("Orbiter_v25_Ref").Shape)
        ref_ebb42 = _bake_placement(doc.getObject("EBB42_ShortBridge_R7_Ref").Shape)
        ref_fan3010 = _bake_placement(doc.getObject("Fan_3010_Ref").Shape)
    finally:
        App.closeDocument(doc.Name)

    if ref_hotend.BoundBox.ZMin > -10.0 or not ref_hotend.Placement.isIdentity():
        raise RuntimeError(f"Hotend reference failed upright placement bake: {ref_hotend.BoundBox}, {ref_hotend.Placement}")

    # 1. Split Front Toolhead + Fan Shroud slightly forward of Y_FRONT_BP to avoid coplanar face cuts
    front_toolhead = _keep_significant_solids(
        r7_shape.common(make_box(-35.0, 35.0, Y_FRONT_BP + 0.02, 40.0, 0.0, 42.0))
    )
    front_toolhead.exportBrep(str(CACHE_DIR / CACHE_FILES["front_toolhead"]))

    # 2. Extract Rear Backplate + Top EBB42 Pad cleanly without coplanar grazing cuts
    # Subtract only the front toolhead zone (Z < 45, Y > Y_FRONT_BP + 0.002), keeping Z=73.5..80 EBB42 pad
    bp_raw = _keep_significant_solids(
        r7_shape.cut(make_box(-35.0, 35.0, Y_FRONT_BP + 0.002, 45.0, -5.0, 45.0))
    )
    # Heal web Y = [Y_WEB_FRONT, Y_FRONT_BP + 0.002] between side columns across Z = [20.0, 74.8]
    web_heal = make_box(-COL_INNER_X, COL_INNER_X, Y_WEB_FRONT, Y_FRONT_BP + 0.002, 20.0, 74.8)
    # Heal old hotend screw hex nut recesses inside Y = [Y_REAR_MATING, Y_FRONT_BP + 0.002] at Z = 27.22
    plugs = [bp_raw, web_heal]
    for _hname, hx in r6.HOTEND_SCREW_XS:
        plugs.append(make_cyl_y(hx, BASE_HOTEND_SCREW_Z, 3.8, Y_REAR_MATING, Y_FRONT_BP + 0.002))
    bp_blank = _keep_significant_solids(plugs[0].multiFuse(plugs[1:]).removeSplitter())
    bp_blank.exportBrep(str(CACHE_DIR / CACHE_FILES["bp_blank"]))

    # 3. Export reference shapes, fast hotend collision box, and generated gray AD5M carriage mockup
    ref_hotend.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_hotend"]))
    he_bb = ref_hotend.BoundBox
    he_fast = make_box(he_bb.XMin + 0.1, he_bb.XMax - 0.1, he_bb.YMin + 0.1, he_bb.YMax - 0.1, he_bb.ZMin + 0.1, he_bb.ZMax - 0.1)
    he_fast.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_hotend_fast"]))
    ref_orbiter.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_orbiter"]))
    ref_ebb42.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_ebb42"]))
    ref_fan3010.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_fan3010"]))

    carriage, knubs, belts = build_gray_carriage_mockup()
    carriage.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_carriage"]))
    knubs.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_knubs"]))
    belts.exportBrep(str(CACHE_DIR / CACHE_FILES["ref_belts"]))

    print(f"[cache] Initialized all R8 BREPs in {time.perf_counter() - t0:.2f}s")


def load_cache() -> dict[str, Part.Shape]:
    """Load pre-generated static BREP shapes into memory."""
    init_cache(force=False)
    shapes: dict[str, Part.Shape] = {}
    for key, fname in CACHE_FILES.items():
        sh = Part.Shape()
        sh.read(str(CACHE_DIR / fname))
        shapes[key] = sh
    return shapes


def load_params() -> dict[str, Any]:
    """Load persisted parameters or initialize default r8_params.json."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    params = dict(DEFAULT_PARAMS)
    if PARAMS_PATH.exists():
        loaded = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
        missing = [k for k in DEFAULT_PARAMS if k not in loaded]
        for key in DEFAULT_PARAMS:
            if key in loaded:
                params[key] = loaded[key]
        if missing:
            PARAMS_PATH.write_text(json.dumps(params, indent=2), encoding="utf-8")
    else:
        PARAMS_PATH.write_text(json.dumps(params, indent=2), encoding="utf-8")
    return params


def save_params(params: dict[str, Any]) -> None:
    """Persist current parameter dictionary."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean = {k: params.get(k, v) for k, v in DEFAULT_PARAMS.items()}
    PARAMS_PATH.write_text(json.dumps(clean, indent=2), encoding="utf-8")


def _bake_placement(shape: Part.Shape) -> Part.Shape:
    """Bake any non-identity TopLoc_Location Placement into geometry vertices."""
    if shape.Placement.isIdentity():
        return shape.copy()
    m = shape.Placement.toMatrix()
    out = shape.copy()
    out.Placement = App.Placement()
    out.transformShape(m, True)
    return out


def _rotate_z180_baked(shape: Part.Shape) -> Part.Shape:
    """Return a copy rotated 180 deg about Z with Placement baked to Identity."""
    out = _bake_placement(shape)
    m = App.Matrix()
    m.rotateZ(math.pi)
    out.transformShape(m, True)
    return out


def _export_stl_fast(shape: Part.Shape, dest: Path, linear_deflection: float = 0.14) -> None:
    """Write a binary STL mesh atomically for fast browser loading."""
    tmp = dest.with_name(f"_tmp_{dest.name}")
    mesh = MeshPart.meshFromShape(
        Shape=shape,
        LinearDeflection=linear_deflection,
        AngularDeflection=0.45,
        Relative=False,
    )
    mesh.write(str(tmp))
    os.replace(tmp, dest)


def _export_web_meshes(
    r8_display: Part.Shape,
    cache: dict[str, Part.Shape],
    report: dict[str, Any],
) -> None:
    """Export lightweight STL meshes + manifest for the shared browser 3D workspace."""
    WEB_MESH_DIR.mkdir(parents=True, exist_ok=True)
    stamp_path = WEB_MESH_DIR / ".refs_stamp"
    expected_stamp = "z180_baked_v1"
    refresh_refs = (not stamp_path.exists()) or (stamp_path.read_text(encoding="utf-8").strip() != expected_stamp)

    _export_stl_fast(r8_display, WEB_MESH_DIR / "R8_Adapter.stl", linear_deflection=0.12)

    ref_specs = [
        ("Ref_Gray_AD5M_Carriage", "ref_carriage", False, 0.25),
        ("Ref_Belts_Keepout", "ref_belts", False, 0.30),
        ("Ref_Orbiter_v25", "ref_orbiter", True, 0.20),
        ("Ref_X1C_Hotend", "ref_hotend", True, 0.14),
        ("Ref_3010_Fan", "ref_fan3010", True, 0.20),
        ("Ref_EBB42_ShortBridge", "ref_ebb42", False, 0.20),
    ]
    for obj_name, cache_key, _uses_dz, lin_def in ref_specs:
        stl_path = WEB_MESH_DIR / f"{obj_name}.stl"
        if refresh_refs or not stl_path.exists():
            _export_stl_fast(_rotate_z180_baked(cache[cache_key]), stl_path, linear_deflection=lin_def)
    if refresh_refs:
        stamp_path.write_text(expected_stamp, encoding="utf-8")

    manifest = {
        "version": time.time(),
        "report": report,
        "parts": [
            {"id": "R8_Adapter", "label": "R8 Carriage Adapter", "stl": "/meshes/R8_Adapter.stl", "color": "#3d82cd", "opacity": 1.0, "uses_dz": False, "movable": False},
            {"id": "Ref_Gray_AD5M_Carriage", "label": "Gray AD5M Carriage", "stl": "/meshes/Ref_Gray_AD5M_Carriage.stl", "color": "#949ba3", "opacity": 0.55, "uses_dz": False, "movable": True},
            {"id": "Ref_Belts_Keepout", "label": "GT2 Belts Keepout", "stl": "/meshes/Ref_Belts_Keepout.stl", "color": "#d13838", "opacity": 0.45, "uses_dz": False, "movable": False},
            {"id": "Ref_Orbiter_v25", "label": "Orbiter v2.5 Extruder", "stl": "/meshes/Ref_Orbiter_v25.stl", "color": "#383c42", "opacity": 1.0, "uses_dz": True, "movable": True},
            {"id": "Ref_X1C_Hotend", "label": "Bambu X1C Hotend", "stl": "/meshes/Ref_X1C_Hotend.stl", "color": "#dc732d", "opacity": 1.0, "uses_dz": True, "movable": True},
            {"id": "Ref_3010_Fan", "label": "3010 Cooling Fan", "stl": "/meshes/Ref_3010_Fan.stl", "color": "#595e66", "opacity": 0.90, "uses_dz": True, "movable": True},
            {"id": "Ref_EBB42_ShortBridge", "label": "EBB42 Short Bridge", "stl": "/meshes/Ref_EBB42_ShortBridge.stl", "color": "#329b5f", "opacity": 1.0, "uses_dz": False, "movable": True},
        ],
    }
    duct_src = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R4" / "Fan_Shroud_Recovered_R8_R4.stl"
    duct_dst = WEB_MESH_DIR / "Fan_Shroud_Recovered.stl"
    if duct_src.exists():
        if (not duct_dst.exists()) or (duct_src.stat().st_mtime > duct_dst.stat().st_mtime):
            shutil.copy2(duct_src, duct_dst)
        manifest["parts"].append(
            {"id": "Fan_Shroud_Recovered", "label": "Fan Shroud Recovered (R4 — Simplified)", "stl": "/meshes/Fan_Shroud_Recovered.stl", "color": "#26a69a", "opacity": 0.95, "uses_dz": False, "movable": True}
        )
    (WEB_MESH_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _translate_copy(shape: Part.Shape, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Part.Shape:
    cp = _bake_placement(shape)
    cp.translate(App.Vector(dx, dy, dz))
    return _bake_placement(cp)


def _build_carriage_access_sleeves(
    front_shifted: Part.Shape,
    sleeve_r: float,
    bore_r: float,
) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Build sealed duct sleeves (on -X side) and hex-driver access tunnels for low_R / low_L."""
    sleeves: list[Part.Shape] = []
    cutters: list[Part.Shape] = []
    for name, hx, hz, y_cb, _cb_r in r3.CARRIAGE_HOLES_R3:
        if hz > 20.0:
            continue
        test_cyl = make_cyl_y(hx, hz, bore_r, Y_FRONT_BP + 0.1, 35.0)
        if front_shifted.common(test_cyl).Volume < 1.0:
            continue
        # Cut driver access tunnel straight from front wall to socket seat y_cb
        cutters.append(make_cyl_y(hx, hz, bore_r, y_cb, 35.0))
        if hx < 0.0:
            # Seal ONLY across the hollow duct chamber behind the solid front grille (ends cleanly inside front wall)
            raw_sleeve = make_cyl_y(hx, hz, sleeve_r, Y_FRONT_BP - 0.1, 25.8)
            y_box = make_box(hx - sleeve_r - 0.5, hx + sleeve_r + 0.5, Y_FRONT_BP - 0.1, 25.8, hz - sleeve_r - 0.5, hz + sleeve_r + 0.5)
            sleeves.append(raw_sleeve.common(y_box))
    return sleeves, cutters


def _make_rounded_wire_notch_prism(
    x_in: float,
    x_out: float,
    y_back: float,
    y_front: float,
    z0: float,
    z1: float,
    fillet_r: float = 2.0,
) -> Part.Shape:
    """Build an extruded Z-prism extending -X with a single tangent fillet at (x_out, y_back)."""
    r = min(fillet_r, 0.45 * abs(x_in - x_out), 0.45 * abs(y_front - y_back))
    s2 = math.sqrt(0.5)
    p0 = App.Vector(x_in, y_front, z0)
    p1 = App.Vector(x_out, y_front, z0)
    p2 = App.Vector(x_out, y_back + r, z0)
    cx, cy = x_out + r, y_back + r
    p_mid = App.Vector(cx - r * s2, cy - r * s2, z0)
    p3 = App.Vector(x_out + r, y_back, z0)
    p4 = App.Vector(x_in, y_back, z0)
    edges = [
        Part.makeLine(p0, p1),
        Part.makeLine(p1, p2),
        Part.Arc(p2, p_mid, p3).toShape(),
        Part.makeLine(p3, p4),
        Part.makeLine(p4, p0),
    ]
    wire = Part.Wire(edges)
    return Part.Face(wire).extrude(App.Vector(0.0, 0.0, z1 - z0))


def _build_hotend_wire_cutouts(dz: float, extra_x_mm: float) -> list[Part.Shape]:
    """Enlarge the hotend thermistor/heater wire notch rightward (-X internal / +X display).

    Preserves the 1.48 mm top bridge supporting Orbiter v2.5 behind Y_display = -24.42
    while widening both the front sky slot and under-deck wire bay past the heatsink flank.
    """
    if extra_x_mm <= 0.1:
        return []
    x_in = -12.40  # slight overlap into existing open notch (X_wall = -12.935)
    x_out = -12.935 - extra_x_mm
    return [
        # Upper open-sky extension in front of Orbiter housing (display Y = -31.5..-24.42)
        _make_rounded_wire_notch_prism(
            x_in=x_in,
            x_out=x_out,
            y_back=24.42,
            y_front=31.50,
            z0=24.80 + dz,
            z1=35.00 + dz,
            fillet_r=2.0,
        ),
        # Under-deck wire bay extension behind display Y = -24.42 (display Z = 8.50..16.45)
        _make_rounded_wire_notch_prism(
            x_in=x_in,
            x_out=x_out,
            y_back=20.00,
            y_front=25.40,
            z0=23.15 + dz,
            z1=31.10 + dz,
            fillet_r=2.0,
        ),
    ]


def _build_simplified_fan_duct_parts(dz: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Replace the angled/lumpy internal BSpline duct walls with clean planar chambers.

    Built in internal builder coords (+X = fan side, +Y = front, +Z = up) before Z-180 rotate:
    - Fuses a uniform >= 3.00 mm partition wall (display X = -3.27..-0.265, Y = -25.00..+2.90,
      Z = 9.60..16.20) extending continuously from the rear hotend M3 block across the fan tunnel
      to the front wall (thickened solely toward the -X fan side, never toward the +X hotend bay).
    - Cuts the left fan-to-hotend chamber up to display Z = 16.20 mm while preserving the R=4.4 mm
      boss for the left Orbiter M3 heatset at display (-13.15, -12.00).
    - Cuts the lower plenum across the full width below display Z = 9.60 mm.
    """
    z_bot = 12.15 + dz          # -2.50 display (clears lower 3010 fan screw bosses)
    z_ceil_left = 30.85 + dz    # +16.20 display (1.73 mm flat top roof under Orbiter)
    z_ceil_right = 24.25 + dz   # +9.60 display (stays below hotend M3 mounts & wire deck)
    z_boss0 = 27.05 + dz        # +12.40 display (preserves Z=12.95..17.93 M3 heatset hole)
    y_back = -2.90              # +2.90 display (flush with flat rear backplate wall)
    y_front = 25.00             # -25.00 display (5.04 mm solid front bumper wall)

    partition_wall = make_box(0.265, 3.27, y_back - 0.60, y_front + 1.00, z_ceil_right, z_ceil_left + 0.50)

    box_left = make_box(3.27, 19.55, y_back, y_front, z_bot, z_ceil_left)
    boss_left = Part.makeCylinder(
        4.40,
        6.00,
        App.Vector(13.15, 12.00, z_boss0),
        App.Vector(0.0, 0.0, 1.0),
    )
    cut_left = box_left.cut(boss_left)
    cut_right = make_box(-26.80, 3.28, y_back, y_front, z_bot, z_ceil_right)
    return [partition_wall], [cut_left, cut_right]


def _make_front_hex_nut_pocket(
    hx: float,
    hz: float,
    af: float,
    y_entry: float,
    y_seat: float,
    bevel_d: float = 0.35,
    bevel_extra_af: float = 0.45,
) -> Part.Shape:
    """Build a front-entry (+Y internal) captive M3 hex pocket tapering into y_seat."""
    y_ext = y_entry + 0.15
    y_bev_end = y_entry - bevel_d
    af_ext = af + bevel_extra_af * (bevel_d + 0.15) / bevel_d
    bevel = Part.makeLoft(
        [r6._hex_wire(hx, hz, af_ext, y_ext), r6._hex_wire(hx, hz, af, y_bev_end)],
        True,
        True,
    )
    shaft = Part.Face(r6._hex_wire(hx, hz, af, y_bev_end + 0.05)).extrude(
        App.Vector(0.0, y_seat - (y_bev_end + 0.05), 0.0)
    )
    return bevel.fuse(shaft)


def _build_carriage_hex_nut_parts(af: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Replace rear blind M3 heat-set bores on the 4 AD5M carriage mounts with captive hex nuts.

    Plugs the oversized Ø4.30 mm rear heat-set pockets solid, drills clean Ø3.50 mm M3
    through-bores from Y_REAR_MATING (-11.117), and cuts front-entry captive hex pockets
    ending at y_seat = -7.30 mm (3.82 mm clamped flange behind each M3 nut).
    """
    plugs: list[Part.Shape] = []
    cutters: list[Part.Shape] = []
    y_seat = -7.30
    for _name, hx, hz, _y_cb, _cb_r in r3.CARRIAGE_HOLES_R3:
        plugs.append(make_cyl_y(hx, hz, 2.25, Y_REAR_MATING - 0.10, -5.00))
        y_entry = -1.90 if hz < 20.0 else Y_FRONT_BP
        cutters.append(_make_front_hex_nut_pocket(hx, hz, af, y_entry=y_entry, y_seat=y_seat))
        cutters.append(make_cyl_y(hx, hz, 1.75, Y_REAR_MATING - 1.50, y_seat + 0.60))
    return plugs, cutters


def _make_corner_fillet_cutter(
    xc: float,
    yc: float,
    r: float,
    x_out: float,
    y_out: float,
    z0: float,
    z1: float,
) -> Part.Shape:
    """Build a corner trim prism removing everything outside a Z-axis fillet cylinder."""
    xmin, xmax = min(xc, x_out), max(xc, x_out)
    ymin, ymax = min(yc, y_out), max(yc, y_out)
    corner_box = make_box(xmin, xmax, ymin, ymax, z0, z1)
    keep_cyl = Part.makeCylinder(r, z1 - z0 + 1.0, App.Vector(xc, yc, z0 - 0.5), App.Vector(0.0, 0.0, 1.0))
    return corner_box.cut(keep_cyl)


def _build_lower_rear_flush_parts(dz: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Extend the recessed lower back face flush with Y_REAR_MATING (-11.117 mm).

    Fuses a clean planar block across the full backplate width (-29.998..+30.000)
    from the shifted bottom (5.500 + dz = -9.15 mm) up into the central arch (Z = +6.50 mm),
    then trims both rear vertical corners to the matching R = 1.60 mm backplate fillet.
    Cutting after fusing avoids OCCT co-cylindrical tangent-seam failures.
    """
    z0 = 5.500 + dz
    z1 = 6.500
    if z1 <= z0 + 0.1:
        return [], []
    rear_block = make_box(-29.998, 30.000, Y_REAR_MATING - 0.10, Y_FRONT_BP, z0, z1)
    r_fillet = 1.600
    y_c = Y_REAR_MATING + r_fillet
    corner_cutters = [
        _make_corner_fillet_cutter(-28.400, y_c, r_fillet, -31.0, Y_REAR_MATING - 1.0, z0 - 0.5, z1 + 0.5),
        _make_corner_fillet_cutter(28.400, y_c, r_fillet, 31.0, Y_REAR_MATING - 1.0, z0 - 0.5, z1 + 0.5),
    ]
    return [rear_block], corner_cutters


def _safe_common_vol(a: Part.Shape, b: Part.Shape) -> float:
    """Fast BRep intersection volume with bounding-box pruning across sub-solids."""
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    solids = b.Solids if len(b.Solids) > 1 else [b]
    total = 0.0
    for s in solids:
        if not a.BoundBox.intersect(s.BoundBox):
            continue
        try:
            cm = a.common(s)
            if not cm.isNull():
                total += cm.Volume
        except Part.OCCError:
            pass
    return total


def build_r8(params: dict[str, Any], update_fcstd: bool = True, full_checks: bool = False) -> dict[str, Any]:
    """Rebuild R8 STEP, diagnostics, and native VarSet FCStd from cached BREPs."""
    t0 = time.perf_counter()
    cache = load_cache()

    dz = float(params["extruder_hotend_z_shift_mm"])
    mot_r = float(params["motor_circle_diameter_mm"]) * 0.5
    flank_clear = float(params["orbiter_flank_clearance_mm"])
    oval_on = bool(params["oval_cutout_enabled"])
    oval_zc = float(params["oval_z_center_mm"])
    oval_h = float(params["oval_height_mm"])
    oval_w = float(params["oval_width_mm"])
    oval_full = bool(params["oval_cut_full_depth"])
    access_on = bool(params["carriage_hole_access_cutouts"])
    sleeve_r = float(params["duct_sleeve_radius_mm"])
    bore_r = float(params["access_bore_radius_mm"])
    wire_extra_x = float(params["hotend_wire_cutout_extra_x_mm"])
    simplify_duct = bool(params["simplify_hotend_fan_duct"])
    carriage_hex_on = bool(params["carriage_hex_nut_pockets"])
    carriage_hex_af = float(params["carriage_hex_nut_af_mm"])
    lower_rear_flush = bool(params["lower_rear_flush_extension"])

    z_mot = BASE_Z_MOT + dz
    z_mount = BASE_Z_MOUNT + dz
    z_hotend_screw = BASE_HOTEND_SCREW_Z + dz

    bp_blank = cache["bp_blank"].copy()
    # Overlap -0.08 mm along Y (from Y_FRONT_BP + 0.02 -> Y_FRONT_BP - 0.06) to prevent coplanar OCCT fuse issues
    front_shifted = _translate_copy(cache["front_toolhead"], 0.0, -0.08, dz)

    fuse_parts: list[Part.Shape] = [bp_blank, front_shifted]
    cut_parts: list[Part.Shape] = []

    if lower_rear_flush:
        flush_fuses, flush_cuts = _build_lower_rear_flush_parts(dz)
        fuse_parts.extend(flush_fuses)
        cut_parts.extend(flush_cuts)

    if access_on:
        sleeves, access_tunnels = _build_carriage_access_sleeves(front_shifted, sleeve_r, bore_r)
        fuse_parts.extend(sleeves)
        cut_parts.extend(access_tunnels)

    if simplify_duct:
        duct_fuses, duct_cuts = _build_simplified_fan_duct_parts(dz)
        fuse_parts.extend(duct_fuses)
        cut_parts.extend(duct_cuts)

    if carriage_hex_on:
        hex_fuses, hex_cuts = _build_carriage_hex_nut_parts(carriage_hex_af)
        fuse_parts.extend(hex_fuses)
        cut_parts.extend(hex_cuts)

    body = fuse_parts[0]
    for fp in fuse_parts[1:]:
        body = body.fuse(fp)

    # Skim any sub-micron tolerance protrusion or overlap behind exact Y_REAR_MATING so the rear plane is one clean face
    cut_parts.append(make_box(-35.0, 35.0, Y_REAR_MATING - 3.0, Y_REAR_MATING, -20.0, 90.0))

    # 1. Lowered circular motor portal through backplate (Y <= Y_FRONT_BP + 0.1)
    cut_parts.append(make_cyl_y(0.0, z_mot, mot_r, Y_REAR_MATING - 2.0, Y_FRONT_BP + 0.1))

    # 2. Smooth rounded-rectangle relief in web matching Orbiter heatsink shoulders
    flank_w = 2.0 * (22.47 + flank_clear)
    flank_h = (70.12 - 33.90) + 2.0 * flank_clear
    flank_zc = 0.5 * (33.90 + 70.12) + dz
    cut_parts.append(
        make_rounded_rect_y(
            0.0,
            flank_zc,
            flank_w,
            flank_h,
            8.0,
            Y_WEB_FRONT - 0.05,
            Y_FRONT_BP + 0.1,
        )
    )

    # 3. Restored Kirill top oval/stadium cutout for protruding AD5M carriage knubs
    if oval_on and oval_w > 1.0 and oval_h > 1.0:
        oval_y0 = (Y_REAR_MATING - 2.0) if oval_full else Y_WEB_FRONT
        cut_parts.append(make_stadium_y(0.0, oval_zc, oval_w, oval_h, oval_y0, Y_FRONT_BP + 0.2))

    # 4. Shifted X1C hotend M3 hex nut pockets + bores cleanly passing Y_REAR_MATING..Y_FRONT_BP
    for _hname, hx in r6.HOTEND_SCREW_XS:
        cut_parts.append(
            r6.make_hex_nut_pocket(
                hx,
                z_hotend_screw,
                r6.HEX_NUT_AF,
                rear_y=Y_REAR_MATING - 1.5,
                y_seat=r6.HEX_NUT_SEAT_Y,
            )
        )
        cut_parts.append(
            r6.make_hex_nut_pocket(
                hx,
                z_hotend_screw,
                r6.HEX_NUT_AF + r6.HEX_CHAMFER_EXTRA_AF,
                rear_y=Y_REAR_MATING - 1.5,
                y_seat=Y_REAR_MATING + r6.HEX_CHAMFER_DEPTH,
            )
        )
        cut_parts.append(make_cyl_y(hx, z_hotend_screw, 1.75, Y_REAR_MATING - 1.5, r6.HEX_NUT_SEAT_Y + 0.6))

    # 5. Enlarged thermistor / heater wire passage beside hotend heatsink (+X display / -X internal)
    cut_parts.extend(_build_hotend_wire_cutouts(dz, wire_extra_x))

    # Apply cuts sequentially (avoids OCCT compound self-intersection failures)
    r8_shape = body
    for tool in cut_parts:
        r8_shape = r8_shape.cut(tool)
    r8_shape = _keep_significant_solids(r8_shape)

    # Rotate 180 deg about Z on export & workspace so -Y is toolhead Front and +Y is carriage Back
    # (matches FreeCAD Navigation Cube Front = looking from -Y toward +Y).
    r8_display = _rotate_z180_baked(r8_shape)

    tmp_step = OUT_DIR / "_tmp_live.step"
    r8_display.exportStep(str(tmp_step))

    if bool(params.get("export_stl", False)):
        stl_shape = r8_display.copy()
        mesh = MeshPart.meshFromShape(Shape=stl_shape, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False)
        mesh.write(str(LIVE_STL_PATH))

    # Collision / alignment checks against fixed & shifted references (in internal builder coords)
    orb_shifted = _translate_copy(cache["ref_orbiter"], 0.0, 0.0, dz)
    he_shifted = _translate_copy(cache["ref_hotend"], 0.0, 0.0, dz)
    fan_shifted = _translate_copy(cache["ref_fan3010"], 0.0, 0.0, dz)
    ebb = cache["ref_ebb42"]
    carriage = cache["ref_carriage"]
    knubs = cache["ref_knubs"]
    belts = cache["ref_belts"]

    checks = {
        "orbiter_vs_adapter_mm3": round(_safe_common_vol(r8_shape, orb_shifted), 3),
        "orbiter_vs_gray_carriage_mm3": round(_safe_common_vol(carriage, orb_shifted), 3),
        "hotend_vs_adapter_mm3": round(_safe_common_vol(r8_shape, he_shifted), 3) if full_checks else "skipped_fast_mode",
        "fan3010_vs_adapter_mm3": round(_safe_common_vol(r8_shape, fan_shifted), 3),
        "knubs_vs_adapter_mm3": round(_safe_common_vol(r8_shape, knubs), 3),
        "belts_vs_adapter_mm3": round(_safe_common_vol(r8_shape, belts), 3),
        "ebb42_vs_adapter_mm3": round(_safe_common_vol(r8_shape, ebb), 3),
    }

    report = {
        "params": params,
        "derived": {
            "coordinate_convention": "Front = -Y, Back = +Y, Up = +Z (matches FreeCAD Front view)",
            "z_mot_mm": round(z_mot, 3),
            "gray_carriage_bore_z_mm": GRAY_CARRIAGE_BORE_Z,
            "motor_to_carriage_z_offset_mm": round(z_mot - GRAY_CARRIAGE_BORE_Z, 3),
            "z_mount_mm": round(z_mount, 3),
            "z_hotend_screw_mm": round(z_hotend_screw, 3),
            "nozzle_z_mm": round(he_shifted.BoundBox.ZMin, 3),
            "motor_portal_z_span_mm": [round(z_mot - mot_r, 3), round(z_mot + mot_r, 3)],
            "oval_z_span_mm": [round(oval_zc - oval_h * 0.5, 3), round(oval_zc + oval_h * 0.5, 3)] if oval_on else None,
            "adapter_bbox": {
                "x": [round(r8_display.BoundBox.XMin, 3), round(r8_display.BoundBox.XMax, 3)],
                "y": [round(r8_display.BoundBox.YMin, 3), round(r8_display.BoundBox.YMax, 3)],
                "z": [round(r8_display.BoundBox.ZMin, 3), round(r8_display.BoundBox.ZMax, 3)],
            },
            "adapter_volume_mm3": round(r8_display.Volume, 2),
            "adapter_valid": bool(r8_display.isValid()),
        },
        "interferences": checks,
        "build_seconds": round(time.perf_counter() - t0, 3),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _export_web_meshes(r8_display, cache, report)

    # Atomically swap LIVE_STEP_PATH after report + meshes are written so viewers see fresh data
    os.replace(tmp_step, LIVE_STEP_PATH)

    if update_fcstd:
        _write_fcstd_workspace(r8_display, cache, params, dz)

    print(
        f"[R8] Built in {report['build_seconds']}s | Z_mot={z_mot:.2f} (carriage={GRAY_CARRIAGE_BORE_Z}) | "
        f"vol={report['derived']['adapter_volume_mm3']} valid={report['derived']['adapter_valid']} | "
        f"interferences={checks}"
    )
    return report


def _ensure_varset(doc: App.Document, params: dict[str, Any]) -> App.DocumentObject:
    """Create or sync the native App::VarSet holding user-tunable R8 parameters."""
    vs = doc.getObject("Params")
    if vs is None:
        vs = doc.addObject("App::VarSet", "Params")
    specs = [
        ("extruder_hotend_z_shift_mm", "App::PropertyFloat", "Vertical Z shift applied to Orbiter + Hotend + Fan shroud (mm)"),
        ("motor_circle_diameter_mm", "App::PropertyFloat", "Backplate motor clearance hole diameter (mm)"),
        ("orbiter_flank_clearance_mm", "App::PropertyFloat", "Extra side/vertical clearance around Orbiter heatsink shoulders (mm)"),
        ("oval_cutout_enabled", "App::PropertyBool", "Enable Kirill top oval cutout for protruding carriage knubs"),
        ("oval_z_center_mm", "App::PropertyFloat", "Vertical Z center of top oval cutout (mm)"),
        ("oval_height_mm", "App::PropertyFloat", "Height of top oval cutout (mm)"),
        ("oval_width_mm", "App::PropertyFloat", "Width of top oval cutout (mm)"),
        ("oval_cut_full_depth", "App::PropertyBool", "Cut top oval full depth through rear carriage backplate"),
        ("carriage_hole_access_cutouts", "App::PropertyBool", "Add front access tunnels + sealed duct sleeve for lower carriage bolts"),
        ("duct_sleeve_radius_mm", "App::PropertyFloat", "Outer radius of sealed duct bypass sleeve around (-19, 3.5) (mm)"),
        ("access_bore_radius_mm", "App::PropertyFloat", "Inner radius of M3 hex driver access tunnel for lower carriage bolts (mm)"),
        ("hotend_wire_cutout_extra_x_mm", "App::PropertyFloat", "Extra +X width added to hotend thermistor/heater wire notch (mm)"),
        ("simplify_hotend_fan_duct", "App::PropertyBool", "Replace angled BSpline internal duct walls with flat rectangular wind tunnel"),
        ("carriage_hex_nut_pockets", "App::PropertyBool", "Use front-entry captive M3 hex-nut pockets instead of heat-set inserts for carriage bolts"),
        ("carriage_hex_nut_af_mm", "App::PropertyFloat", "Across-flats width for carriage bolt captive M3 hex-nut pockets (mm)"),
        ("lower_rear_flush_extension", "App::PropertyBool", "Extend lower rear shroud back flush with carriage mating plane (Y=-11.117)"),
        ("show_carriage_mockup", "App::PropertyBool", "Display ruler-measured gray AD5M carriage & belts keepout"),
        ("show_reference_parts", "App::PropertyBool", "Display Orbiter v2.5, X1C Hotend, 3010 Fan, EBB42"),
        ("export_stl", "App::PropertyBool", "Also write STL on rebuild (slightly slower)"),
    ]
    for name, ptype, tip in specs:
        if not hasattr(vs, name):
            vs.addProperty(ptype, name, "R8_Parameters", tip)
        setattr(vs, name, params[name])
    return vs


def _add_part_obj(doc: App.Document, name: str, shape: Part.Shape, dz: float = 0.0) -> None:
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = _bake_placement(shape)
    if abs(dz) > 1e-6:
        obj.Placement = App.Placement(App.Vector(0.0, 0.0, dz), App.Rotation())


def _write_fcstd_workspace(
    r8_display: Part.Shape,
    cache: dict[str, Part.Shape],
    params: dict[str, Any],
    dz: float,
) -> None:
    """Create R8_Live_Workspace.FCStd with VarSet + Adapter + Reference parts (-Y=Front, +Y=Back)."""
    doc = App.newDocument("R8_Live_Workspace")
    _ensure_varset(doc, params)
    _add_part_obj(doc, "R8_Adapter", r8_display)
    _add_part_obj(doc, "Ref_Gray_AD5M_Carriage", _rotate_z180_baked(cache["ref_carriage"]))
    _add_part_obj(doc, "Ref_Belts_Keepout", _rotate_z180_baked(cache["ref_belts"]))
    _add_part_obj(doc, "Ref_Orbiter_v25", _rotate_z180_baked(cache["ref_orbiter"]), dz)
    _add_part_obj(doc, "Ref_X1C_Hotend", _rotate_z180_baked(cache["ref_hotend"]), dz)
    _add_part_obj(doc, "Ref_3010_Fan", _rotate_z180_baked(cache["ref_fan3010"]), dz)
    _add_part_obj(doc, "Ref_EBB42_ShortBridge", _rotate_z180_baked(cache["ref_ebb42"]))
    doc.recompute()
    doc.saveAs(str(FCSTD_PATH))
    App.closeDocument(doc.Name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build BambuMod x Orbiter v2.5 R8 live model.")
    parser.add_argument("--init-cache", action="store_true", help="Force regenerate static BREP cache.")
    parser.add_argument("--skip-fcstd", action="store_true", help="Skip rewriting .FCStd (used during GUI live reload).")
    parser.add_argument("--full-checks", action="store_true", help="Include slow fin-by-fin hotend common check.")
    args, _ = parser.parse_known_args()

    force_cache = args.init_cache or os.environ.get("R8_INIT_CACHE") == "1"
    skip_fcstd = args.skip_fcstd or os.environ.get("R8_SKIP_FCSTD") == "1"
    full_checks = args.full_checks or os.environ.get("R8_FULL_CHECKS") == "1"
    if force_cache:
        init_cache(force=True)
    params = load_params()
    build_r8(params, update_fcstd=not skip_fcstd, full_checks=full_checks)


if __name__ == "__main__" or (
    __name__ == "r8_live_builder"
    and any("r8_live_builder.py" in str(a) for a in sys.argv)
    and os.environ.get("R8_IMPORT_ONLY") != "1"
):
    main()
