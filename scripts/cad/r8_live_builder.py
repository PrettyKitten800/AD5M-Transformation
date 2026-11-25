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
REAR_EXT_MM = 2.00                   # Extend rear carriage face (#5-#8) back 2.00 mm (moves chassis 2 mm forward)
Y_REAR_EXT = Y_REAR_MATING - REAR_EXT_MM  # -13.117 internal (+13.117 mm display)
Y_FRONT_NEW = 26.400                 # -26.400 mm display (exact 1.01 mm perimeter from Ø4.20 #4 heat-set bore; flush w/ 3010 fan!)
SHROUD_BOLT_XL_DISP = -16.80         # Left M2 shroud bolt (#9-#10 cheek): 0.60 mm wall to -19.50 fan, 0% plenum obstruction!
SHROUD_BOLT_XR_DISP = 24.30          # Right M2 shroud bolt (#7/#9): 1.20 mm clear of +X honeycomb grille
SHROUD_BOLT_Z_DISP = 5.80            # Shared shroud bolt height: 1.32 mm clear below #4 3010 heat-set boss
NOZZLE_DZ_EXTRA = -3.650             # Lower Eddy Duo & Shroud R7 exits for 47.8 mm real Bambu hotend (nozzle Z = -31.88 mm)
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
    "remove_front_magnet_holders_and_add_hex": True,
    "orbiter_tunnel_hex_nut_pockets": True,
    "fan3010_lower_front_heatset_boss": False,
    "fan3010_z_shift_mm": -6.40,
    "fan3010_remove_bottom_floor": True,
    "airflow_ramp_6_to_7": True,
    "lower_floor_airflow_ramp": True,
    "top_backplate_trim_z_mm": 65.08,
    "top_bridge_full_thickness": True,
    "motor_portal_full_through_square": True,
    "motor_portal_top_raise_mm": 1.0,
    "hotend_top_profile_ceiling_match": True,
    "round_outer_corners_3_to_7": True,
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


def _rounded_rect_wire_y(
    cx: float,
    cz: float,
    width: float,
    height: float,
    r_top: float,
    r_bot: float,
    y: float,
) -> Part.Wire:
    """Build a closed 8-segment rounded-rectangle wire in XZ at plane Y (supports distinct top/bottom radii)."""
    hw, hh = width * 0.5, height * 0.5
    rt = max(0.2, min(r_top, hw - 0.01, hh - 0.01))
    rb = max(0.2, min(r_bot, hw - 0.01, hh - 0.01))
    p1 = App.Vector(cx - hw + rt, y, cz + hh)
    p2 = App.Vector(cx + hw - rt, y, cz + hh)
    p3 = App.Vector(cx + hw, y, cz + hh - rt)
    p4 = App.Vector(cx + hw, y, cz - hh + rb)
    p5 = App.Vector(cx + hw - rb, y, cz - hh)
    p6 = App.Vector(cx - hw + rb, y, cz - hh)
    p7 = App.Vector(cx - hw, y, cz - hh + rb)
    p8 = App.Vector(cx - hw, y, cz + hh - rt)
    dt = rt * (1.0 - math.sqrt(0.5))
    db = rb * (1.0 - math.sqrt(0.5))
    c_tr = App.Vector(cx + hw - dt, y, cz + hh - dt)
    c_br = App.Vector(cx + hw - db, y, cz - hh + db)
    c_bl = App.Vector(cx - hw + db, y, cz - hh + db)
    c_tl = App.Vector(cx - hw + dt, y, cz + hh - dt)
    return Part.Wire([
        Part.LineSegment(p1, p2).toShape(),
        Part.Arc(p2, c_tr, p3).toShape(),
        Part.LineSegment(p3, p4).toShape(),
        Part.Arc(p4, c_br, p5).toShape(),
        Part.LineSegment(p5, p6).toShape(),
        Part.Arc(p6, c_bl, p7).toShape(),
        Part.LineSegment(p7, p8).toShape(),
        Part.Arc(p8, c_tl, p1).toShape(),
    ])


def make_rounded_rect_y(cx: float, cz: float, width: float, height: float, corner_r: float, y0: float, y1: float) -> Part.Shape:
    """Create a clean extruded rounded rectangle solid along +Y with zero boolean seams."""
    wire = _rounded_rect_wire_y(cx, cz, width, height, corner_r, corner_r, y0)
    return Part.Face(wire).extrude(App.Vector(0.0, y1 - y0, 0.0))


def _make_rounded_rect_chamfer_frustum_y(
    cx: float,
    cz: float,
    width: float,
    height: float,
    r_top: float,
    r_bot: float,
    y_inner: float,
    y_face: float,
    chamfer: float,
    expand_outward: bool = True,
) -> Part.Shape:
    """Build a 45-deg lofted chamfer frustum between y_inner and y_face (with +0.25 mm face overcut)."""
    sgn = 1.0 if y_face > y_inner else -1.0
    over = 0.25
    delta = (chamfer + over) if expand_outward else -(chamfer + over)
    w_in = _rounded_rect_wire_y(cx, cz, width, height, r_top, r_bot, y_inner)
    w_out = _rounded_rect_wire_y(
        cx,
        cz,
        width + 2.0 * delta,
        height + 2.0 * delta,
        max(0.2, r_top + delta),
        max(0.2, r_bot + delta),
        y_face + sgn * over,
    )
    return Part.makeLoft([w_in, w_out], True, True)


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


def _build_bare_eddy_pcb_display(eddy_official_step: Path | None = None) -> tuple[Part.Shape, Part.Shape] | None:
    """Extract and position the official bare BTT Eddy Duo PCB in display coords (+NOZZLE_DZ_EXTRA)."""
    step_path = eddy_official_step or (REPO / "outputs" / "Eddy_Duo_BambuMod_mount_R1" / "EDDY_official.step")
    if not step_path.exists():
        return None
    eddy_raw = Part.read(str(step_path))
    pcb_shells = [
        sh for idx, sh in enumerate(eddy_raw.Shells)
        if idx != 818 and max(sh.BoundBox.XLength, sh.BoundBox.YLength, sh.BoundBox.ZLength) >= 0.35
    ]
    main_pcb = Part.makeBox(14.08, 29.00, 2.045, App.Vector(-81.405, -27.79, 2.857))
    # Punch the two exact official Ø3.20 mm (R=1.60 mm, 10.50 mm pitch) M3 mounting holes from EDDY_official.step
    for hx_raw in (-79.58, -69.08):
        main_pcb = main_pcb.cut(
            Part.makeCylinder(1.60, 4.00, App.Vector(hx_raw, -8.09, 2.00), App.Vector(0.0, 0.0, 1.0))
        )
    bare_pcb = Part.makeCompound([main_pcb] + pcb_shells)
    mx = App.Matrix()
    mx.rotateX(math.pi * 0.5)
    bare_pcb.transformShape(mx, True)
    main_pcb_rot = main_pcb.copy()
    main_pcb_rot.transformShape(mx, True)
    bo = bare_pcb.BoundBox
    # Place sunken in rear chassis behind X1C nozzle (X=+6.33, coil bottom Z=-25.73 + NOZZLE_DZ_EXTRA = -29.38 = +2.50 mm above -31.88 mm nozzle,
    # USB-C back at Y=+10.80 + REAR_EXT_MM = +12.80 = 0.32 mm recessed inside Y=+13.117 extended carriage plane!)
    shift_v = App.Vector(
        6.33 - 0.5 * (bo.XMin + bo.XMax),
        (10.80 + REAR_EXT_MM) - bo.YMax,
        (-25.73 + NOZZLE_DZ_EXTRA) - bo.ZMin,
    )
    bare_pcb.translate(shift_v)
    main_pcb_rot.translate(shift_v)
    return bare_pcb, main_pcb_rot


def _extend_hotend_ref_display(sh_disp: Part.Shape, dz_extra: float = NOZZLE_DZ_EXTRA) -> Part.Shape:
    """Elongate Ref_X1C_Hotend heating zone cleanly above the thermistor hole (raw Z=[-4.00,+0.20]) by dz_extra."""
    if abs(dz_extra) <= 1e-6:
        return sh_disp.copy()
    upper = sh_disp.common(make_box(-30.0, 30.0, -30.0, 30.0, -4.00, 40.0))
    lower = sh_disp.common(make_box(-30.0, 30.0, -30.0, 30.0, -30.0, 0.20))
    lower.translate(App.Vector(0.0, 0.0, dz_extra))
    return upper.fuse(lower).removeSplitter()


def _export_web_meshes(
    r8_display: Part.Shape,
    cache: dict[str, Part.Shape],
    report: dict[str, Any],
    dz_fan: float = 0.0,
) -> None:
    """Export lightweight STL meshes + manifest for the shared browser 3D workspace."""
    WEB_MESH_DIR.mkdir(parents=True, exist_ok=True)
    stamp_path = WEB_MESH_DIR / ".refs_stamp"
    expected_stamp = f"z180_baked_v8_hotend4795_clean_rearext_{REAR_EXT_MM:.2f}_dzfan_{dz_fan:.2f}"
    refresh_refs = (not stamp_path.exists()) or (stamp_path.read_text(encoding="utf-8").strip() != expected_stamp)

    _export_stl_fast(r8_display, WEB_MESH_DIR / "R8_Adapter.stl", linear_deflection=0.12)

    ref_specs = [
        ("Ref_Gray_AD5M_Carriage", "ref_carriage", False, 0.25, 0.0, REAR_EXT_MM),
        ("Ref_Belts_Keepout", "ref_belts", False, 0.30, 0.0, REAR_EXT_MM),
        ("Ref_Orbiter_v25", "ref_orbiter", True, 0.20, 0.0, 0.0),
        ("Ref_X1C_Hotend", "ref_hotend", True, 0.14, 0.0, 0.0),
        ("Ref_3010_Fan", "ref_fan3010", True, 0.20, dz_fan, 0.0),
    ]
    for obj_name, cache_key, _uses_dz, lin_def, extra_dz, extra_dy in ref_specs:
        stl_path = WEB_MESH_DIR / f"{obj_name}.stl"
        if refresh_refs or not stl_path.exists():
            sh_ref = _rotate_z180_baked(cache[cache_key])
            if obj_name == "Ref_X1C_Hotend":
                sh_ref = _extend_hotend_ref_display(sh_ref, NOZZLE_DZ_EXTRA)
            if abs(extra_dz) > 1e-6 or abs(extra_dy) > 1e-6:
                sh_ref.translate(App.Vector(0.0, extra_dy, extra_dz))
            _export_stl_fast(sh_ref, stl_path, linear_deflection=lin_def)

    # Remove deprecated viewer STLs (bracket, cased Eddy sensor, EBB42 short bridge)
    for stale_name in ("Ref_Eddy_Duo_Bracket.stl", "Ref_Eddy_Duo_Sensor.stl", "Ref_EBB42_ShortBridge.stl"):
        stale_path = WEB_MESH_DIR / stale_name
        if stale_path.exists():
            stale_path.unlink()

    # Export bare BTT Eddy Duo PCB into R8 display frame
    eddy_official_step = REPO / "outputs" / "Eddy_Duo_BambuMod_mount_R1" / "EDDY_official.step"
    eddy_pcb_stl = WEB_MESH_DIR / "Ref_Eddy_Duo_BarePCB.stl"
    if refresh_refs or (eddy_official_step.exists() and not eddy_pcb_stl.exists()):
        eddy_built = _build_bare_eddy_pcb_display(eddy_official_step)
        if eddy_built is not None:
            bare_pcb, _ = eddy_built
            _export_stl_fast(bare_pcb, eddy_pcb_stl, linear_deflection=0.10)

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
            {"id": "Ref_X1C_Hotend", "label": "Bambu X1C Hotend (47.95 mm)", "stl": "/meshes/Ref_X1C_Hotend.stl", "color": "#dc732d", "opacity": 1.0, "uses_dz": True, "movable": True},
            {"id": "Ref_3010_Fan", "label": "3010 Cooling Fan", "stl": "/meshes/Ref_3010_Fan.stl", "color": "#595e66", "opacity": 0.90, "uses_dz": True, "movable": True},
        ],
    }
    if eddy_pcb_stl.exists():
        manifest["parts"].append(
            {"id": "Ref_Eddy_Duo_BarePCB", "label": "BTT Eddy Duo Bare PCB (Rear Sunken)", "stl": "/meshes/Ref_Eddy_Duo_BarePCB.stl", "color": "#1db954", "opacity": 1.0, "uses_dz": False, "movable": True}
        )
    duct_r7 = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R7" / "Fan_Shroud_Recovered_R8_R7.stl"
    duct_r6 = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R6" / "Fan_Shroud_Recovered_R8_R6.stl"
    duct_r5 = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R5" / "Fan_Shroud_Recovered_R8_R5.stl"
    duct_r4 = REPO / "outputs" / "BambuMod_Orbiter25_R8_FanDuct_1404902_R4" / "Fan_Shroud_Recovered_R8_R4.stl"
    duct_src = duct_r7 if duct_r7.exists() else (duct_r6 if duct_r6.exists() else (duct_r5 if duct_r5.exists() else duct_r4))
    duct_label = (
        "Fan Shroud V3.1 (R7 — -3.65 mm Drop, Flush Y=-26.45, M2)" if duct_src == duct_r7
        else (
            "Fan Shroud V3.0 (R6 — Flush Y=-26.45, Button-Head M2)" if duct_src == duct_r6
            else ("Fan Shroud V2.0 (Native NURBS/BREP CAD)" if duct_src == duct_r5 else "Fan Shroud Recovered (R4 — Simplified)")
        )
    )
    duct_dst = WEB_MESH_DIR / "Fan_Shroud_Recovered.stl"
    if duct_src.exists():
        if (not duct_dst.exists()) or (duct_src.stat().st_mtime > duct_dst.stat().st_mtime):
            shutil.copy2(duct_src, duct_dst)
        manifest["parts"].append(
            {"id": "Fan_Shroud_Recovered", "label": duct_label, "stl": "/meshes/Fan_Shroud_Recovered.stl", "color": "#26a69a", "opacity": 0.95, "uses_dz": False, "movable": True}
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


def _build_simplified_fan_duct_parts(
    dz: float,
    airflow_ramp: bool = True,
    dz_fan: float = 0.0,
) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Replace the angled/lumpy internal BSpline duct walls with clean planar chambers & airflow ramp.

    Built in internal builder coords (+X = fan side, +Y = front, +Z = up) before Z-180 rotate:
    - Fuses the partition wall & smooth 54.6-deg airflow ramp connecting Pin #7 (display X=-7.67,
      Z=16.20) down to Pin #6 (display X=-3.27, Z=10.00), guiding upper fan air cleanly into the
      X1C heatsink fins instead of hitting a 90-deg step wall (clears Pin #4 Orbiter boss by 0.48 mm).
    - Levels the entire hotend tunnel ceiling across Pins #1-#4 to one dead-flat plane at Z=10.00 mm.
    - When the 3010 fan is shifted down (dz_fan < -2.0), lowers the tunnel floor cut to Z=-7.15 mm
      (flush with the floor) to maximize airflow across the bottom X1C heatsink fins & heatbreak.
    """
    z_bot = (7.50 + dz) if dz_fan < -2.0 else (12.15 + dz)  # -7.15 display when fan lowered, else -2.50
    z_ceil_left = 30.85 + dz    # +16.20 display (1.73 mm flat top roof under Orbiter)
    z_ceil_right = 24.65 + dz   # +10.00 display (single flat ceiling flush across Pins #1-#4; 0.82 mm below hotend M3 bores)
    z_boss0 = 26.40 + dz        # +11.75 display (room for upward-entry captive M3 hex nut socket)
    y_back = -2.90              # +2.90 display (flush with flat rear backplate wall)
    y_front = 25.00             # -25.00 display (5.04 mm solid front bumper wall)
    y_front_right = 24.55       # -24.55 display (preserves Pin #2 full 5.44 mm front wall)

    if airflow_ramp:
        # Smooth planar ramp from Pin #7 (X_int=7.67, Z=16.20) down to Pin #6 (X_int=3.27, Z=10.00)
        ramp_pts = [
            App.Vector(0.265, y_back - 0.60, z_ceil_right),
            App.Vector(3.27,  y_back - 0.60, z_ceil_right),
            App.Vector(7.67,  y_back - 0.60, z_ceil_left),
            App.Vector(7.67,  y_back - 0.60, z_ceil_left + 0.50),
            App.Vector(0.265, y_back - 0.60, z_ceil_left + 0.50),
            App.Vector(0.265, y_back - 0.60, z_ceil_right),
        ]
        partition_wall = Part.Face(Part.makePolygon(ramp_pts)).extrude(
            App.Vector(0.0, (y_front + 1.00) - (y_back - 0.60), 0.0)
        )
    else:
        partition_wall = make_box(0.265, 3.27, y_back - 0.60, y_front + 1.00, z_ceil_right, z_ceil_left + 0.50)

    # Fill the upstream curved BSpline ceiling arches above z_ceil_right so cut_right leaves ONE dead-flat plane
    # across the entire hotend tunnel ceiling (Pins #1, #2, #3, #4) without touching the open chimney or wire bay.
    z_fill_top = z_ceil_right + 1.40  # +11.40 display (stays inside solid roof & hotend screw block)
    ceil_fill_rear = make_box(-26.80, 3.27, y_back - 0.60, 8.20, z_ceil_right - 0.20, z_fill_top)
    ceil_fill_right = make_box(-26.80, -12.93, 8.00, 20.00, z_ceil_right - 0.20, z_fill_top)
    ceil_fill_far_right = make_box(-26.80, -20.04, 19.80, y_front + 0.50, z_ceil_right - 0.20, z_fill_top)

    box_left = make_box(3.27, 19.55, y_back, y_front, z_bot, z_ceil_left)
    boss_left = Part.makeCylinder(
        5.00,
        7.00,
        App.Vector(13.15, 12.00, z_boss0),
        App.Vector(0.0, 0.0, 1.0),
    )
    cut_left = box_left.cut(boss_left).cut(partition_wall)
    cut_right = make_box(-26.80, 3.28, y_back, y_front_right, z_bot, z_ceil_right)
    return [partition_wall, ceil_fill_rear, ceil_fill_right, ceil_fill_far_right], [cut_left, cut_right]


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


def _hex_wire_xz(hx: float, hz: float, af: float, y: float, rot_deg: float = 0.0) -> Part.Wire:
    """Return closed 6-gon wire in X-Z plane at Y (rot_deg=0: flat top/bot; rot_deg=30: flat left/right)."""
    r_circ = af / math.sqrt(3.0)
    pts = [
        App.Vector(
            hx + r_circ * math.cos(math.radians(60 * k + rot_deg)),
            y,
            hz + r_circ * math.sin(math.radians(60 * k + rot_deg)),
        )
        for k in range(6)
    ]
    pts.append(pts[0])
    return Part.makePolygon(pts)


def _make_rear_entry_hex_nut_pocket(
    hx: float,
    hz: float,
    af: float,
    y_entry: float,
    y_seat: float,
    bevel_d: float = 0.35,
    bevel_extra_af: float = 0.45,
    rot_deg: float = 0.0,
) -> Part.Shape:
    """Build an inside-tunnel (-Y internal -> +Y internal) captive M3 hex pocket ending at y_seat."""
    y_ext = y_entry - 0.15
    y_bev_end = y_entry + bevel_d
    af_ext = af + bevel_extra_af * (bevel_d + 0.15) / bevel_d
    bevel = Part.makeLoft(
        [_hex_wire_xz(hx, hz, af_ext, y_ext, rot_deg), _hex_wire_xz(hx, hz, af, y_bev_end, rot_deg)],
        True,
        True,
    )
    shaft = Part.Face(_hex_wire_xz(hx, hz, af, y_bev_end - 0.05, rot_deg)).extrude(
        App.Vector(0.0, y_seat - (y_bev_end - 0.05), 0.0)
    )
    return bevel.fuse(shaft)


def _hex_wire_xy(hx: float, hy: float, af: float, z: float, rot_deg: float = 0.0) -> Part.Wire:
    """Return closed 6-gon wire in X-Y plane at Z (rot_deg=0: flat front/back; rot_deg=30: flat left/right)."""
    r_circ = af / math.sqrt(3.0)
    pts = [
        App.Vector(
            hx + r_circ * math.cos(math.radians(60 * k + rot_deg)),
            hy + r_circ * math.sin(math.radians(60 * k + rot_deg)),
            z,
        )
        for k in range(6)
    ]
    pts.append(pts[0])
    return Part.makePolygon(pts)


def _make_bottom_entry_z_hex_pocket(
    hx: float,
    hy: float,
    af: float,
    z_entry: float,
    z_seat: float,
    bevel_d: float = 0.35,
    bevel_extra_af: float = 0.45,
    rot_deg: float = 0.0,
) -> Part.Shape:
    """Build an upward-entry (from tunnel ceiling z_entry up to z_seat) captive M3 hex pocket."""
    z_ext = z_entry - 0.25
    z_bev_end = z_entry + bevel_d
    af_ext = af + bevel_extra_af * (bevel_d + 0.25) / bevel_d
    bevel = Part.makeLoft(
        [_hex_wire_xy(hx, hy, af_ext, z_ext, rot_deg), _hex_wire_xy(hx, hy, af, z_bev_end, rot_deg)],
        True,
        True,
    )
    shaft = Part.Face(_hex_wire_xy(hx, hy, af, z_bev_end - 0.05, rot_deg)).extrude(
        App.Vector(0.0, 0.0, z_seat - (z_bev_end - 0.05))
    )
    return bevel.fuse(shaft)


def _build_front_shroud_mount_hex_parts(dz: float, af: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Thin front face (#5) to Y=-26.60 mm (1.01 mm outside #4 insert), remove lip #1-#3 & -X arm, add symmetric M3 hex mounts (#8/#9).

    Built in internal builder coords (+X = -X display fan side, +Y = -Y display front, +Z = up):
    - Trims entire front face dead-flush to Y_FRONT_NEW = 26.600 mm (Y_display = -26.600 mm, -3.44 mm thinner!)
      and removes the obsolete -X side shroud arm (X_int > 19.50) completely.
    - Removes the protruding lip along #1-#2-#3 (Z=9.50..10.30, Y_disp=-24.55..-23.00) inside the #8 hotend window.
    - Left mount (#8 -> aligns with Shroud #6): Display (-14.80, Z=5.80) -> Internal (+14.80, Z=5.80),
      sleek R=4.60 mm inside-tunnel boss (Y_int=22.60..26.60, clipped to X_int<=19.50), 2.60 mm deep
      captive M3 hex pocket (y_entry=22.60, y_seat=25.20 -> 1.40 mm front flange, rot_deg=30 -> 1.90 mm wall to fan).
    - Right mount (#9 -> aligns with Shroud #7): Display (+24.30, Z=5.80) -> Internal (-24.30, Z=5.80),
      sleek R=4.60 mm inside-tunnel boss (Y_int=22.60..26.60, clipped to X_int>=-27.60), 2.60 mm deep
      captive M3 hex pocket (y_entry=22.60, y_seat=25.20 -> 1.40 mm front flange, rot_deg=30 -> 0.50 mm clear of grille).
    """
    z_pin = SHROUD_BOLT_Z_DISP
    xl_int = -SHROUD_BOLT_XL_DISP   # +14.80 internal (-14.80 display)
    xr_int = -SHROUD_BOLT_XR_DISP   # -24.30 internal (+24.30 display)
    y_front_flat = Y_FRONT_NEW      # 26.400 internal (-26.400 display)
    # Compact M2 captive hex sockets (DIN 934 M2 nut: 4.00 mm AF x 1.60 mm thick -> 4.20 mm snug pocket!)
    m2_af = 4.20
    y_boss_rear = 23.600            # -23.600 display (protrudes only 0.95-1.40 mm into tunnel for max airflow!)
    y_hex_seat = 25.200             # -25.200 display (1.20 mm solid front flange + 1.60 mm M2 nut pocket)
    boss_r = 3.50                   # Compact Ø7.00 mm boss (1.07 mm radial wall around M2 hex vertices!)

    # Seal Kirill's legacy +X magnet cavity (#3-#6), smooth the lower-front step, and level the Z=-9.15 underside (#10-#17)
    front_wall_patch = make_box(-29.99, -18.04, 24.55, y_front_flat, 5.50 + dz, 32.58 + dz).fuse([
        make_box(-29.99, 2.00, 24.55, y_front_flat, 5.50 + dz, 24.65 + dz),
        make_box(-29.99, 2.00, 23.17, y_front_flat, 5.50 + dz, 7.50 + dz),
        make_box(-29.99, -14.63, -3.88, y_front_flat, 5.50 + dz, 7.50 + dz),
    ])
    boss_l = make_cyl_y(xl_int, z_pin, boss_r, y_boss_rear, y_front_flat).common(
        make_box(0.0, 19.50, y_boss_rear - 0.5, y_front_flat + 0.5, -15.0, 20.0)
    )
    boss_r = make_cyl_y(xr_int, z_pin, boss_r, y_boss_rear, y_front_flat).common(
        make_box(-27.60, 0.0, y_boss_rear - 0.5, y_front_flat + 0.5, -15.0, 20.0)
    )

    cutters = [
        # Trim entire front face dead-flush to Y_FRONT_NEW (-26.400 mm display)
        make_box(-35.0, 35.0, y_front_flat, 36.0, -18.0, 30.0),
        # Remove obsolete -X protruding shroud arm completely (flush with X_disp = -19.500)
        make_box(19.50, 35.0, 18.0, 36.0, -18.0, 30.0),
        # Shave lip #1-#2-#3 AND level entire #8 window floor dead-flat at Z=10.00 mm (eliminates step #1+#2!)
        make_box(-18.04, 0.27, 22.80, y_front_flat + 0.50, 24.65 + dz, 25.20 + dz),
        # Left mount (#8): Ø2.30 mm M2 clearance bore + shallow inside-tunnel captive M2 hex socket
        make_cyl_y(xl_int, z_pin, 1.15, y_boss_rear - 0.50, y_front_flat + 2.0),
        _make_rear_entry_hex_nut_pocket(xl_int, z_pin, m2_af, y_entry=y_boss_rear, y_seat=y_hex_seat, bevel_d=0.25, bevel_extra_af=0.35, rot_deg=30.0),
        # Right mount (#9): Ø2.30 mm M2 clearance bore + shallow inside-tunnel captive M2 hex socket
        make_cyl_y(xr_int, z_pin, 1.15, y_boss_rear - 0.50, y_front_flat + 2.0),
        _make_rear_entry_hex_nut_pocket(xr_int, z_pin, m2_af, y_entry=y_boss_rear, y_seat=y_hex_seat, bevel_d=0.25, bevel_extra_af=0.35, rot_deg=30.0),
    ]
    return [front_wall_patch, boss_l, boss_r], cutters


def _build_orbiter_tunnel_hex_parts(dz: float, af: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Add upward-entry captive M3 hex nut sockets on the inside tunnel ceiling for Orbiter mounts (Pins #3 & #4).

    Both mounts share an identical Z_seat = 14.80 mm (3.13 mm solid top deck under Z=17.93 Orbiter pad,
    so standard M3x10 or M3x12 SHCS through Orbiter's 4.50 mm ears engage 100% of a 2.40 mm M3 nut):
    - Pin #3 (display +23.85, -12.00 -> internal -23.85, +12.00): enters from Z=8.995 tunnel ceiling.
    - Pin #4 (display -13.15, -12.00 -> internal +13.15, +12.00): extends R=5.00 mm hanging boss down
      to Z=11.75 (0.000 mm^3 clash with 3010 fan or hotend) and cuts a 3.05 mm deep upward hex socket.
    """
    z_top_deck = 32.58 + dz      # 17.93 mm display
    z_seat_pin3 = 29.45 + dz     # 14.80 mm display (3.13 mm solid deck above Pin #3 nut)
    z_pin3_ceil = 24.65 + dz     # 10.00 mm display (single flat hotend tunnel ceiling under Pin #3)
    # Pin #4 boss (#4-#7): extended down 1.00 mm (z_pin4_bot=14.50) for a solid 1.50 mm deep M3 hex nut pocket!
    z_seat_pin4 = 30.65 + dz     # 16.00 mm display (1.93 mm solid clamped deck under Z=17.93 Orbiter pad)
    z_pin4_bot = 29.15 + dz      # 14.50 mm display (1.50 mm deep M3 hex nut pocket!)

    # Shortened Pin #4 hanging boss (R=5.00 mm, Z=15.50..17.43)
    pin4_boss = Part.makeCylinder(
        5.00,
        (z_top_deck - 0.50) - z_pin4_bot,
        App.Vector(13.15, 12.00, z_pin4_bot),
        App.Vector(0.0, 0.0, 1.0),
    )

    cutters = [
        # Pin #3 (+X display / -X internal): upward captive hex socket (flat facing +X grille) + clean M3 through-bore
        _make_bottom_entry_z_hex_pocket(-23.85, 12.00, af, z_entry=z_pin3_ceil, z_seat=z_seat_pin3, rot_deg=30.0),
        Part.makeCylinder(1.75, (z_top_deck + 1.50) - (z_seat_pin3 - 0.50), App.Vector(-23.85, 12.00, z_seat_pin3 - 0.50), App.Vector(0.0, 0.0, 1.0)),
        # Pin #4 (-X display / +X internal): trim legacy R7 hanging boss below z_pin4_bot so shortened hex face is exposed!
        Part.makeCylinder(5.50, z_pin4_bot - (25.00 + dz), App.Vector(13.15, 12.00, 25.00 + dz), App.Vector(0.0, 0.0, 1.0)),
        # Pin #4 exact 0.50 mm deep upward captive hex socket + clean M3 through-bore
        _make_bottom_entry_z_hex_pocket(13.15, 12.00, af, z_entry=z_pin4_bot, z_seat=z_seat_pin4, bevel_d=0.12, bevel_extra_af=0.20),
        Part.makeCylinder(1.75, (z_top_deck + 1.50) - (z_seat_pin4 - 0.50), App.Vector(13.15, 12.00, z_seat_pin4 - 0.50), App.Vector(0.0, 0.0, 1.0)),
        # Pin #5 central filament pass-through bore: widen +2.00 mm diameter (Ø4.00 -> Ø6.00 mm, r=3.00) + 0.35 mm top chamfer
        Part.makeCylinder(3.00, (z_top_deck + 1.50) - (z_top_deck - 2.50), App.Vector(-6.335, 12.00, z_top_deck - 2.50), App.Vector(0.0, 0.0, 1.0)),
        Part.makeCone(3.00, 3.60, 0.60, App.Vector(-6.335, 12.00, z_top_deck - 0.35), App.Vector(0.0, 0.0, 1.0)),
    ]
    return [pin4_boss], cutters


def _build_fan3010_lower_front_heatset_boss(dz: float) -> tuple[Part.Shape, Part.Shape]:
    """Build solid integrated boss & M3 heat-set bore for lower-front 3010 fan mount (Pin #1).

    Coaxial with lower-front 3010 fan screw at display (Y=-23.29, Z=-4.40) -> internal (+23.29, 10.25+dz):
    - Solid R=4.20 mm cylindrical boss from X_int=19.50 (3010 fan seating face) inward to X_int=11.50
      (8.00 mm length), integrated seamlessly down to the floor (Z_bot=5.50+dz=-9.15) and forward
      into the front wall (Y_int=27.50) so there are zero overhangs or thin walls.
    - Clean Ø4.20 mm (R=2.10 mm) x 6.00 mm deep M3 heat-set insert bore from X_int=19.50 to 13.50
      with a 0.40 mm lead-in chamfer at the X_int=19.50 entry face (2.10 mm radial wall all around,
      2.00 mm solid backstop, 0.000 mm^3 clash with 3010 fan and >10 mm clear of X1C hotend).
    """
    yc = 23.29
    zc = 10.25 + dz      # -4.40 mm display
    z_floor = 5.50 + dz  # -9.15 mm display
    x_entry = 19.50      # -19.50 mm display (3010 fan face)
    x_back = 11.50       # -11.50 mm display (8.00 mm deep boss)

    cyl_boss = Part.makeCylinder(
        4.20,
        x_entry - x_back,
        App.Vector(x_back, yc, zc),
        App.Vector(1.0, 0.0, 0.0),
    )
    # Integrate boss smoothly into floor & front wall (no floating cylinder underside)
    pedestal_bot = make_box(x_back, x_entry, yc - 4.20, 27.50, z_floor, zc)
    pedestal_front = make_box(x_back, x_entry, yc, 27.50, zc, zc + 4.20)
    boss_solid = cyl_boss.fuse([pedestal_bot, pedestal_front]).removeSplitter()

    # Ø4.20 mm (R=2.10 mm) x 6.00 mm deep M3 heat-set bore + 0.40 mm entry chamfer
    bore_depth = 6.00
    bore_r = 2.10
    chamf_d = 0.40
    chamf_r_outer = bore_r + 0.40
    bore_shaft = Part.makeCylinder(
        bore_r,
        bore_depth + 0.20,
        App.Vector(x_entry - bore_depth, yc, zc),
        App.Vector(1.0, 0.0, 0.0),
    )
    bore_chamfer = Part.makeCone(
        bore_r,
        chamf_r_outer,
        chamf_d + 0.20,
        App.Vector(x_entry - chamf_d, yc, zc),
        App.Vector(1.0, 0.0, 0.0),
    )
    bore_cut = bore_shaft.fuse(bore_chamfer)
    return boss_solid, bore_cut


def _build_lowered_fan3010_mount_parts(
    dz: float,
    dz_fan: float,
    remove_floor: bool = True,
    lower_floor_ramp: bool = True,
) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Shift the entire 3010 cooling fan mount downward into the frame (Pins #1-#5) + lower floor ramp (#7->#8/#9).

    Built in internal builder coords (+X = -X display fan side, +Y = -Y display front, +Z = up):
    - At dz_fan = -6.40 mm, 3010 fan spans Z = [-13.80, +16.20] (center +1.20 mm, dead-center on
      the X1C heatsink fin stack Z = [-8.50, +9.57] and heatbreak), with fan top flush with the
      Z = 16.20 mm fan chamber ceiling and 1.73 mm below the flat Z = 17.93 mm Orbiter top deck.
    - Removes the protruding upper fan hood above Z = 17.93 mm and floor strip #5 under the fan.
    - Builds 4 identical R = 4.00 mm M3 heat-set bosses (Ø4.20 x 5.20 mm + 0.40 mm chamfer).
    - Extends rear support gusset on lower-rear boss #4 smoothly from #5 (Y_disp=+3.90, Z=-14.80)
      up-back to #6 (Y_disp=+11.117, Z=-9.15), printable support-free on the rear bed plane.
    - Adds a sealed lower airflow ramp (#7 -> #8/#9) starting at the bottom of bosses #2 & #4
      (X_disp=-19.50, Z_outer=-14.80 / Z_inner=-13.30) sloping smoothly at 24.6 deg up to the flat
      tunnel floor (X_disp=-6.00, Z_outer=-9.15 / Z_inner=-7.15).
    """
    z_top_deck = 32.58 + dz       # 17.93 mm display
    z_ceil_left = 30.85 + dz      # 16.20 mm display
    z_floor = 5.50 + dz           # -9.15 mm display
    z_tunnel_floor = 7.50 + dz    # -7.15 mm display
    z_old_bot = 10.25 + dz        # -4.40 mm display (old lower 3010 screw Z)
    z_new_bot = z_old_bot + dz_fan  # -10.80 mm display at dz_fan=-6.40
    z_new_top = (34.25 + dz) + dz_fan  # +13.20 mm display at dz_fan=-6.40

    y_front_scr = 23.29           # -23.29 mm display
    y_rear_scr = -0.71            # +0.71 mm display
    x_entry = 19.50               # -19.50 mm display (3010 fan seating face)
    x_back_top = 12.00            # -12.00 mm display (7.50 mm deep upper bosses for 4.6x5.7 mm M3 inserts)
    x_back_bot = 12.30            # -12.30 mm display (7.20 mm deep lower boss for 4.6x5.7 mm M3 insert)
    boss_r = 3.65                 # Uniform 1.55 mm radial wall around Ø4.20 mm bore (1.35 mm around 4.6 mm OD insert)
    z_hull_bot = z_new_bot - 5.40 # -16.20 display at X=-19.50 (keeps >= 0.80 mm solid floor under 6.20 mm deep bore)
    x_ramp_end = 2.00             # -2.00 display (exact edge of bottom hotend window at Pins #13 & #15!)

    fuses: list[Part.Shape] = []
    boss_protects: list[Part.Shape] = []
    cuts: list[Part.Shape] = []

    # 1. Seal any old curved roof divot above Z = 16.20 mm so the top roof (Z = 16.20..17.93) is 100% solid & flat
    roof_seal = make_box(7.67, x_entry, -3.60, 26.80, z_ceil_left, z_top_deck)
    fuses.append(roof_seal)
    boss_protects.append(roof_seal)

    # 1b. Orbiter Z-axis stiffening brace (#7-#8-#9): extends edge #9 (X_disp=-19.50, Z=16.20) down 1.00 mm
    #     across Y_disp=[-20.50, -2.00] (Y_int=[2.00, 20.50]), tying both upper 3010 bosses & Pin #4 boss into one stiff beam
    #     with a 45-deg inner bevel for smooth airflow and support-free printability.
    brace_pts = [
        App.Vector(x_entry,        2.00, z_ceil_left + 0.40),
        App.Vector(x_entry,        2.00, z_ceil_left - 1.00),
        App.Vector(x_entry - 2.00, 2.00, z_ceil_left - 1.00),
        App.Vector(x_entry - 3.00, 2.00, z_ceil_left + 0.00),
        App.Vector(x_entry - 3.00, 2.00, z_ceil_left + 0.40),
        App.Vector(x_entry,        2.00, z_ceil_left + 0.40),
    ]
    orbiter_z_brace = Part.Face(Part.makePolygon(brace_pts)).extrude(App.Vector(0.0, 20.50 - 2.00, 0.0))
    fuses.append(orbiter_z_brace)
    boss_protects.append(orbiter_z_brace)

    # 2. Build ONE unified, sculpted continuous-surface lower hull integrating both lower fan bosses,
    #    the rear support gusset (#5->#6), the seamless front blend (#1->#2 into F219), and the lower airflow ramp.
    #    Internal coords: +X = -X display, +Y = -Y display (front), +Z = up.
    if lower_floor_ramp:
        z_front_blend = z_floor + 2.50  # -6.65 display (tucked flush into front curve F219 at Pin #2)
        z_end_blend = z_floor + 1.43    # -7.72 display (exact edge where underside bevel F124 meets F219)
        # Integrated 1.20 mm rear-bottom chamfer directly in loft cross-section for anti-warp smoothness
        w_fan = Part.makePolygon([
            App.Vector(x_entry,  26.80,         z_hull_bot),
            App.Vector(x_entry,  -2.70,         z_hull_bot),
            App.Vector(x_entry,  -4.55,         z_hull_bot + 1.00),
            App.Vector(x_entry,  Y_REAR_EXT,    z_floor),
            App.Vector(x_entry,  Y_REAR_EXT,    z_tunnel_floor),
            App.Vector(x_entry,  26.50,         z_front_blend),
            App.Vector(x_entry,  29.72,         z_front_blend),
            App.Vector(x_entry,  26.80,         z_hull_bot),
        ])
        w_end = Part.makePolygon([
            App.Vector(x_ramp_end,  25.00, z_floor),
            App.Vector(x_ramp_end,  -3.88, z_floor),
            App.Vector(x_ramp_end,  -3.90, z_floor + 0.01),
            App.Vector(x_ramp_end,  -3.92, z_floor + 0.02),
            App.Vector(x_ramp_end,  -3.92, z_tunnel_floor),
            App.Vector(x_ramp_end,  26.50, z_end_blend),
            App.Vector(x_ramp_end,  28.33, z_end_blend),
            App.Vector(x_ramp_end,  25.00, z_floor),
        ])
        sculpted_lower_hull = Part.makeLoft([w_fan, w_end], True, True)
        # Cut the front face of the lower duct ramp cleanly back to the exact plane through Pins #1-#2-#3
        # Display: P1=(-19.50,-29.61,-6.73), P2=(-19.50,-22.36,-15.29), P3=(-2.00,-25.16,-9.08)
        p1 = App.Vector(x_entry, 29.61, 7.92 + dz)
        p2 = App.Vector(x_entry, 22.36, -0.64 + dz)
        p3 = App.Vector(x_ramp_end, 25.16, 5.57 + dz)
        n_out = (p2 - p1).cross(p3 - p1)
        n_out.normalize()  # Points outward (+Y_int front, -Z down) into the region to cut away
        u_ax = p2 - p1
        u_ax.normalize()
        v_ax = n_out.cross(u_ax)
        v_ax.normalize()
        c_pl = (p1 + p2 + p3) * (1.0 / 3.0)
        half = 60.0
        pl_poly = Part.makePolygon([
            c_pl - u_ax * half - v_ax * half,
            c_pl + u_ax * half - v_ax * half,
            c_pl + u_ax * half + v_ax * half,
            c_pl - u_ax * half + v_ax * half,
            c_pl - u_ax * half - v_ax * half,
        ])
        plane_cut_123 = Part.Face(pl_poly).extrude(n_out * 40.0)
        # Keep a 1.50 mm solid front wall behind the 1-2-3 plane so the inner airway never breaks through
        wall_guard_123 = Part.Face(pl_poly).translated(-n_out * 1.50).extrude(n_out * 45.0)
        sculpted_lower_hull = sculpted_lower_hull.cut(plane_cut_123)
        # Anti-warp 1.00 mm x 45 deg bevel along the left-bottom fan-bay ridge (X_disp=-19.50, Z=-15.50)
        bevel_x_pts = [
            App.Vector(x_entry - 1.00, -12.0, z_hull_bot - 0.50),
            App.Vector(x_entry + 0.50, -12.0, z_hull_bot - 0.50),
            App.Vector(x_entry + 0.50, -12.0, z_hull_bot + 1.00),
            App.Vector(x_entry - 1.00, -12.0, z_hull_bot - 0.50),
        ]
        bevel_x_cut = Part.Face(Part.makePolygon(bevel_x_pts)).extrude(App.Vector(0.0, 45.0, 0.0))
        sculpted_lower_hull = sculpted_lower_hull.cut(bevel_x_cut)
        # Anti-warp 0.90 mm front-bottom ridge chamfer blending the #1-#2-#3 cut plane into the underside ramp
        p_fb0 = App.Vector(x_entry, 22.18, z_hull_bot)
        p_fb1 = App.Vector(x_ramp_end, 25.00, z_floor)
        t_fb = p_fb1 - p_fb0
        t_fb.normalize()
        # Outward normal halfway between underside (-Z tilted slightly +X) and #1-#2-#3 front plane (n_out)
        n_bot = App.Vector(z_floor - z_hull_bot, 0.0, -(x_entry - x_ramp_end))
        n_bot.normalize()
        n_fb = n_out + n_bot
        n_fb.normalize()
        v_fb = n_fb.cross(t_fb)
        v_fb.normalize()
        c_fb = (p_fb0 + p_fb1) * 0.5 - n_fb * 0.65
        fb_poly = Part.makePolygon([
            c_fb - t_fb * 40.0 - v_fb * 30.0,
            c_fb + t_fb * 40.0 - v_fb * 30.0,
            c_fb + t_fb * 40.0 + v_fb * 30.0,
            c_fb - t_fb * 40.0 + v_fb * 30.0,
            c_fb - t_fb * 40.0 - v_fb * 30.0,
        ])
        sculpted_lower_hull = sculpted_lower_hull.cut(Part.Face(fb_poly).extrude(n_fb * 30.0))
        fuses.append(sculpted_lower_hull)
    else:
        sculpted_lower_hull = None
        wall_guard_123 = None

    # 3. Build 4 sleek, uniform-wall R=3.45 mm M3 heat-set bosses (zero boxy 90-deg inner corners!)
    #    Upper bosses anchor cleanly to ceiling & outer walls; lower bosses sit 100% flush inside
    #    sculpted_lower_hull externally while keeping pure uniform 1.35 mm circular arcs inside the airway.
    bore_r = 2.10
    chamf_d = 0.40
    for is_top, zc in ((True, z_new_top), (False, z_new_bot)):
        x_bk = x_back_top if is_top else x_back_bot
        bore_depth = 6.20  # Spec'd for 4.6x5.7 mm M3 heat-set inserts (Ø4.20 x 6.20 mm + 0.40 mm chamfer)
        for is_front, yc in ((True, y_front_scr), (False, y_rear_scr)):
            cyl = Part.makeCylinder(boss_r, x_entry - x_bk, App.Vector(x_bk, yc, zc), App.Vector(1.0, 0.0, 0.0))
            y_out0 = yc if is_front else -3.90
            y_out1 = 27.20 if is_front else yc
            if is_top:
                parts = [
                    cyl,
                    make_box(x_bk, x_entry, y_out0, y_out1, zc - boss_r, z_ceil_left + 0.50),
                    make_box(x_bk, x_entry, yc - boss_r, yc + boss_r, zc, z_ceil_left + 0.50),
                ]
                boss_u = parts[0].multiFuse(parts[1:]).removeSplitter()
                fuses.append(boss_u)
                boss_protects.append(boss_u)
            else:
                # Clip lower boss cleanly to sculpted_lower_hull so ZERO extra ledges/bumps protrude outside!
                parts = [
                    cyl,
                    make_box(x_bk, x_entry, y_out0, y_out1, z_hull_bot, zc + boss_r),
                    make_box(x_bk, x_entry, yc - boss_r, yc + boss_r, z_hull_bot, zc),
                ]
                boss_u = parts[0].multiFuse(parts[1:]).removeSplitter()
                if sculpted_lower_hull is not None:
                    boss_u = boss_u.common(sculpted_lower_hull)
                boss_protects.append(boss_u)

            # Skip the compromised lower-front heat-set bore (sliced by the #1-#2-#3 duct clearance plane)
            # so the flat front cut face stays 100% solid; the other 3 full-depth M3 heat-set bosses remain intact.
            if not is_top and is_front:
                continue

            bore_shaft = Part.makeCylinder(
                bore_r,
                bore_depth + 0.25,
                App.Vector(x_entry - bore_depth, yc, zc),
                App.Vector(1.0, 0.0, 0.0),
            )
            bore_chamfer = Part.makeCone(
                bore_r,
                bore_r + chamf_d,
                chamf_d + 0.25,
                App.Vector(x_entry - chamf_d, yc, zc),
                App.Vector(1.0, 0.0, 0.0),
            )
            cuts.append(bore_shaft.fuse(bore_chamfer))

    # 4. Carve the open sloped inner airway inside sculpted_lower_hull (1.50 mm solid bottom ramp & sealed side cheeks)
    #    Slopes smoothly from Z=-13.80 (fan bottom!) at X_disp=-19.50 up to Z=-7.15 at X_disp=-2.00,
    #    hugging the sleek R=3.45 mm lower bosses cleanly with zero 90-deg inner corners.
    if lower_floor_ramp:
        z_ramp_in0 = z_new_bot - 3.00   # -13.80 display (exact 3010 fan bottom; >= 0.80 mm solid floor under 6.20 mm bore!)
        inner_ramp_pts = [
            App.Vector(x_entry + 0.30, -2.40, z_ramp_in0 - 0.10),
            App.Vector(x_ramp_end - 0.30, -2.40, z_tunnel_floor),
            App.Vector(x_ramp_end - 0.30, -2.40, z_tunnel_floor + 3.00),
            App.Vector(x_entry + 0.30, -2.40, z_tunnel_floor + 3.00),
            App.Vector(x_entry + 0.30, -2.40, z_ramp_in0 - 0.10),
        ]
        inner_ramp_cut = Part.Face(Part.makePolygon(inner_ramp_pts)).extrude(
            App.Vector(0.0, 23.50 - (-2.40), 0.0)
        )
        lower_boss_guard = boss_protects[0].multiFuse(boss_protects[1:]) if len(boss_protects) > 1 else boss_protects[0]
        if wall_guard_123 is not None:
            lower_boss_guard = lower_boss_guard.fuse(wall_guard_123)
        cuts.append(inner_ramp_cut.cut(lower_boss_guard))

    # 3. Trim protruding upper fan hood dead-flush with Z = 17.93 mm top deck (in front of backplate Y_int > -3.80)
    cuts.append(make_box(6.00, 31.50, -3.80, 31.50, z_top_deck, 26.00))

    # 4. Remove bottom floor strip marked by Pin #5 so the lowered 3010 fan drops cleanly into the frame
    if remove_floor:
        cuts.append(make_box(x_entry, 31.50, -3.88, 26.80, z_floor - 1.50, z_floor + 2.50))

    # 5. Guarantee 100% clear 3010 fan pocket space in X_int = [19.50, 31.0], Y_int = [-3.65, 26.40]
    fan_z0 = (7.25 + dz) + dz_fan  # -13.80 display
    fan_z1 = (37.25 + dz) + dz_fan  # +16.20 display
    cuts.append(make_box(x_entry, 31.00, -3.65, 26.40, fan_z0 - 0.20, fan_z1 + 0.15))

    return fuses, cuts, boss_protects


def _build_carriage_hex_nut_parts(af: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Replace rear blind M3 heat-set bores on the 4 AD5M carriage mounts with captive hex nuts.

    Plugs the oversized Ø4.30 mm rear heat-set pockets solid, drills clean Ø3.50 mm M3
    through-bores from Y_REAR_EXT (-13.117), and cuts front-entry captive hex pockets
    ending at y_seat = -9.30 mm (3.82 mm clamped flange behind each M3 nut).
    """
    plugs: list[Part.Shape] = []
    cutters: list[Part.Shape] = []
    y_seat = -7.30 - REAR_EXT_MM
    for _name, hx, hz, _y_cb, _cb_r in r3.CARRIAGE_HOLES_R3:
        plugs.append(make_cyl_y(hx, hz, 2.25, Y_REAR_EXT - 0.10, -5.00))
        y_entry = -1.90 if hz < 20.0 else Y_FRONT_BP
        cutters.append(_make_front_hex_nut_pocket(hx, hz, af, y_entry=y_entry, y_seat=y_seat))
        cutters.append(make_cyl_y(hx, hz, 1.75, Y_REAR_EXT - 1.50, y_seat + 0.60))
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


def _make_y_edge_fillet_cutter(
    xc: float,
    zc: float,
    r: float,
    x_out: float,
    z_out: float,
    y0: float,
    y1: float,
) -> Part.Shape:
    """Build a Y-axis corner trim prism removing everything outside an R-fillet cylinder."""
    xmin, xmax = min(xc, x_out), max(xc, x_out)
    zmin, zmax = min(zc, z_out), max(zc, z_out)
    corner_box = make_box(xmin, xmax, y0, y1, zmin, zmax)
    keep_cyl = Part.makeCylinder(r, (y1 - y0) + 1.0, App.Vector(xc, y0 - 0.5, zc), App.Vector(0.0, 1.0, 0.0))
    return corner_box.cut(keep_cyl)


def _make_x_edge_fillet_cutter(
    yc: float,
    zc: float,
    r: float,
    y_out: float,
    z_out: float,
    x0: float,
    x1: float,
) -> Part.Shape:
    """Build an X-axis corner trim prism removing everything outside an R-fillet cylinder."""
    ymin, ymax = min(yc, y_out), max(yc, y_out)
    zmin, zmax = min(zc, z_out), max(zc, z_out)
    corner_box = make_box(x0, x1, ymin, ymax, zmin, zmax)
    keep_cyl = Part.makeCylinder(r, (x1 - x0) + 1.0, App.Vector(x0 - 0.5, yc, zc), App.Vector(1.0, 0.0, 0.0))
    return corner_box.cut(keep_cyl)


def _build_hotend_top_profile_ceiling(dz: float) -> Part.Shape:
    """Extend the #8 hotend-pocket ceiling down to match the #9 X1C hotend stepped top profile.

    X1C hotend upper collar (display coords, dz=-14.65):
    - X=[0.34, 2.21]: flat Z=14.57 mm; X=[2.21, 3.75]: 45 deg ramp; X=[3.75, 12.33]: flat Z=16.07 mm.
    Adapter #8 ceiling currently sits flat at Z=16.45 mm (+0.38 mm above right flat) across Y=[-24.42, -8.20].
    This adds a matching +0.40 mm clearance step on the left:
    - Flat ceiling Z=14.97 mm for X_disp=[-0.60, +2.03]
    - 45 deg bevel from (X_disp=+2.03, Z=14.97) up to (X_disp=+3.51, Z=16.45) (0.22 mm clear of PTFE cone)
    Built in internal builder coords (X_int = -X_disp, Y_int = -Y_disp).
    """
    z_high = 31.10 + dz        # 16.45 mm display (existing #8 ceiling)
    z_low = 29.62 + dz         # 14.97 mm display (+0.40 mm clearance above X1C hotend Z=14.57)
    z_top_anchor = 31.85 + dz  # 17.20 mm display (solidly anchored inside roof below Z=17.93 deck)
    y_back = 8.00              # -8.00 mm display (overlaps 0.20 mm into -8.20 rear wall)
    y_front = 24.42            # -24.42 mm display (dead-flush with front edge of #8 ceiling)
    pts = [
        App.Vector(0.60, y_back, z_low),
        App.Vector(-2.03, y_back, z_low),
        App.Vector(-3.51, y_back, z_high),
        App.Vector(-3.51, y_back, z_top_anchor),
        App.Vector(0.60, y_back, z_top_anchor),
        App.Vector(0.60, y_back, z_low),
    ]
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0.0, y_front - y_back, 0.0))


def _build_high_airflow_honeycomb_grille(dz: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Replace the legacy 6-hex +X grille with a high-airflow, easy-to-print peak-Y honeycomb grille.

    Pins #1-#4 define the max outlet window on X_disp=+30.00: Y=[-24.30, +2.60], Z=[-6.65, +9.55].
    - Plugs the entire legacy grille wall (including the 3 half-cut top slivers) solid across
      X_disp=[27.35, 30.00] (0.70 mm clear of Pin #3 Orbiter hex nut, clear of Pin #2 mouth at -24.60).
    - Cuts a symmetric 13-cell (3-2-3-2-3) peak-in-Y honeycomb pattern (AF=5.50 mm vs legacy 6.93 mm,
      sturdy 1.10 mm ribs, ~300 mm2 open area = +20% more exhaust airflow, zero small edge slivers)
      clipped cleanly inside the R=2.50 mm rounded-rectangle window.
    - Pointed peaks face -Y (+Z_print when printed flat on rear plane Y=+11.117), so every sloped rib
      prints at a self-supporting 30-deg overhang with zero flat bridging.
    """
    # 1. Solid wall plug sealing all legacy grille holes & top slivers cleanly flush with X_disp=+30.00
    #    X_disp=[27.60, 30.00] stays 0.30 mm outside Pin #2 hex flat (XMax=27.30) while sealing to Y_disp=-26.50!
    wall_plug = make_box(-30.00, -27.60, -3.50, 26.50, 7.50 + dz, 30.65 + dz)
    wall_plug_inner = make_box(-27.65, -27.20, -3.50, 24.40, 7.50 + dz, 30.65 + dz)

    # 2. Rounded-rectangle outlet window (display Y=[-24.30, +2.60], Z=[-6.65, +9.55], R=2.50)
    y0_d, y1_d = -24.30, 2.60
    z0_d, z1_d = 8.00 + dz, 24.20 + dz  # -6.65 .. +9.55 mm display
    rw = 2.50
    y_mid_i = -0.5 * (y0_d + y1_d)      # +10.85 internal
    z_mid = 0.5 * (z0_d + z1_d)         # +1.45 display
    hw = 0.5 * (y1_d - y0_d)            # 13.45 mm
    hh = 0.5 * (z1_d - z0_d)            # 8.10 mm

    def _rrect_x(x_start: float, x_end: float, expand: float = 0.0) -> Part.Shape:
        w2 = hw + expand
        h2 = hh + expand
        r = max(0.2, min(rw + expand, w2 - 0.01, h2 - 0.01))
        d = r * (1.0 - math.sqrt(0.5))
        p1 = App.Vector(x_start, y_mid_i - w2 + r, z_mid + h2)
        p2 = App.Vector(x_start, y_mid_i + w2 - r, z_mid + h2)
        p3 = App.Vector(x_start, y_mid_i + w2,     z_mid + h2 - r)
        p4 = App.Vector(x_start, y_mid_i + w2,     z_mid - h2 + r)
        p5 = App.Vector(x_start, y_mid_i + w2 - r, z_mid - h2)
        p6 = App.Vector(x_start, y_mid_i - w2 + r, z_mid - h2)
        p7 = App.Vector(x_start, y_mid_i - w2,     z_mid - h2 + r)
        p8 = App.Vector(x_start, y_mid_i - w2,     z_mid + h2 - r)
        c_tr = App.Vector(x_start, y_mid_i + w2 - d, z_mid + h2 - d)
        c_br = App.Vector(x_start, y_mid_i + w2 - d, z_mid - h2 + d)
        c_bl = App.Vector(x_start, y_mid_i - w2 + d, z_mid - h2 + d)
        c_tl = App.Vector(x_start, y_mid_i - w2 + d, z_mid + h2 - d)
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
        return Part.Face(wire).extrude(App.Vector(x_end - x_start, 0.0, 0.0))

    win_solid = _rrect_x(-30.60, -26.80, 0.0)

    # 3. Symmetric 13-cell peak-in-Y honeycomb cells (AF=5.50 mm, rib=1.10 mm, pitch=6.60 mm)
    af = 5.50
    rib = 1.10
    r_vert = af / math.sqrt(3.0)
    pitch = af + rib
    dz_hex = pitch
    dy_hex = pitch * math.sqrt(3.0) * 0.5

    cell_cuts: list[Part.Shape] = []
    for ic in range(-2, 3):
        yc = y_mid_i + ic * dy_hex
        z_offsets = (-dz_hex, 0.0, dz_hex) if (ic % 2 == 0) else (-0.5 * dz_hex, 0.5 * dz_hex)
        for z_off in z_offsets:
            zc = z_mid + z_off
            pts = []
            for k in range(6):
                # Peak-in-Y (ang=0, 60, ..., 300 deg) -> 30-deg self-supporting overhangs when printed on Y=+11.117!
                ang = math.radians(60.0 * k)
                pts.append(App.Vector(-30.60, yc + r_vert * math.cos(ang), zc + r_vert * math.sin(ang)))
            pts.append(pts[0])
            hex_prism = Part.Face(Part.makePolygon(pts)).extrude(App.Vector(3.80, 0.0, 0.0))
            clipped = hex_prism.common(win_solid)
            if not clipped.isNull() and clipped.Volume > 10.0:
                cell_cuts.append(clipped)

    return [wall_plug, wall_plug_inner], cell_cuts


def _build_left_wing_pare_down_cutter(dz: float) -> Part.Shape:
    """Pare down the tall hanging -X front wing (#10-#13) to a sleek chamfered mounting arm for Pin #1.

    Retains only a smooth R=5.20 mm rounded ear centered on the M3 shroud bolt (-24.50, Z=3.353)
    with R=3.00 mm top and bottom root fillets into the X_disp=-19.50 main front wall, plus
    clean 0.65 mm x 45 deg anti-warp chamfers on both the front (Y=-30.04) and rear (Y=-27.04) arm edges.
    """
    xc = 24.50               # -24.50 mm display (Pin #1 M3 shroud bolt X)
    zc = 18.003 + dz         # +3.353 mm display (Pin #1 M3 shroud bolt Z)
    x_root = 19.50           # -19.50 mm display (flush with 3010 fan wall)
    r_ear = 5.20             # >= 1.97 mm wall around captive M3 hex vertices, tip at X=-29.70
    r_root = 3.00            # Smooth top & bottom stress-relief root fillets into X=-19.50
    y0, y1 = 26.00, 31.50    # Spans full front wing thickness (Y_disp=-30.04..-26.64)
    y_arm_rear = 27.04       # -27.04 mm display (rear face of front wing)
    y_arm_front = 30.039     # -30.039 mm display (front face of adapter)
    ch = 0.65                # 0.65 mm x 45 deg chamfer on both front & rear outer edges of arm

    def _arm_wire_at_y(y_val: float, shrink: float) -> Part.Wire:
        re = r_ear - shrink
        rr = r_root + shrink
        # Closed 7-segment wire in XZ at y=y_val:
        # Start at root top (x_root - 0.5, zc + re + rr) -> top fillet arc -> top bar -> ear semicircle -> bot bar -> bot fillet arc -> close
        x_f = x_root + rr
        z_top_arc = zc + re + rr
        z_bot_arc = zc - re - rr
        p0 = App.Vector(x_root - 0.50, y_val, z_top_arc)
        p1 = App.Vector(x_root, y_val, z_top_arc)
        # Quarter-arc from (x_root, z_top_arc) around (x_f, z_top_arc) to (x_f, zc + re)
        pm_t = App.Vector(x_f - rr * math.sqrt(0.5), y_val, z_top_arc - rr * math.sqrt(0.5))
        p2 = App.Vector(x_f, y_val, zc + re)
        p3 = App.Vector(xc, y_val, zc + re)
        pm_e = App.Vector(xc + re, y_val, zc)
        p4 = App.Vector(xc, y_val, zc - re)
        p5 = App.Vector(x_f, y_val, zc - re)
        pm_b = App.Vector(x_f - rr * math.sqrt(0.5), y_val, z_bot_arc + rr * math.sqrt(0.5))
        p6 = App.Vector(x_root, y_val, z_bot_arc)
        p7 = App.Vector(x_root - 0.50, y_val, z_bot_arc)
        segs = [
            Part.LineSegment(p0, p1).toShape(),
            Part.Arc(p1, pm_t, p2).toShape(),
            Part.LineSegment(p2, p3).toShape(),
            Part.Arc(p3, pm_e, p4).toShape(),
            Part.LineSegment(p4, p5).toShape(),
            Part.Arc(p5, pm_b, p6).toShape(),
            Part.LineSegment(p6, p7).toShape(),
            Part.LineSegment(p7, p0).toShape(),
        ]
        return Part.Wire(segs)

    # 1. Outer blank covering entire -X wing beyond x_root
    wing_blank = make_box(x_root, 31.50, y0, y1, -12.00, 22.00)

    # 2. Chamfered keep-arm solid (rear 45-deg bevel + straight core + front 45-deg bevel)
    #    Also keep the R=4.60 inside hex boss cylinder at Y_disp=-26.64 (Y_int=26.0..27.04) intact!
    w_rear_out = _arm_wire_at_y(y_arm_rear - 0.15, ch + 0.15)
    w_rear_in = _arm_wire_at_y(y_arm_rear + ch, 0.0)
    w_front_in = _arm_wire_at_y(y_arm_front - ch, 0.0)
    w_front_out = _arm_wire_at_y(y_arm_front + 0.15, ch + 0.15)
    keep_arm = Part.makeLoft([w_rear_out, w_rear_in, w_front_in, w_front_out], True, True)
    boss_keep = make_cyl_y(xc, zc, 4.65, y0 - 0.50, y_arm_rear + ch + 0.20)
    keep_arm = keep_arm.fuse(boss_keep)

    return wing_blank.cut(keep_arm)


def _build_eddy_rear_pocket_and_cable_channel(dz: float) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Build print-friendly downward Eddy housing cradle + sunken rear pocket (#1-#2) + #10-#15 channel.

    With NOZZLE_DZ_EXTRA = -3.650 mm (nozzle tip Z = -31.88 mm for 47.8 mm real Bambu hotend):
    - Bare BTT Eddy Duo PCB sits centered at X_disp=+6.33 (inline with X1C nozzle!), Z=[-29.38,+2.26],
      Y=[-3.39,+12.80] (90-deg coil facing -Y nozzle at dZ=+2.50 mm above nozzle tip).
    - Downward Eddy cradle (eddy_lower_cradle): extends backplate bed-contacting frame down to Z=-11.90 mm
      across X_disp=[-2.60,+15.20], Y_disp=[+2.780,+13.117] (prints 100% flat & support-free on rear bed
      plane while clearing X1C heatsink by 0.61 mm), with 1.20 mm corner & 0.60 mm bottom-front bevels.
    - Main PCB sunken pocket: X_disp=[-1.01,+13.67], Y_disp=[+5.00,+13.50], Z=[-12.50,+9.00] (open at bottom),
      carved around two Ø5.20 mm standoffs at lowered Z=-8.090 mm (10.50 mm pitch, Y_seat=+6.955 mm)
      with tunnel-side captive M2 hex pockets at Y_disp=[+2.78,+4.58].
    """
    z_cradle_bot = -11.90
    z_cradle_top = -8.50     # +0.65 mm overlap into Z=-9.15 backplate floor
    # Internal coords: X_int=[-15.20,+2.60] (Display [-2.60,+15.20]), Y_int=[Y_REAR_EXT-0.10, -2.780] (Display [+2.780,+13.117+])
    cradle = make_box(-15.20, 2.60, Y_REAR_EXT - 0.10, -2.780, z_cradle_bot, z_cradle_top)
    # Anti-warp R=1.40 mm rounded bottom-left & bottom-right outer corners + 0.60 mm bottom-front bevel
    bevel_l = _make_y_edge_fillet_cutter(-13.80, -10.50, 1.40, -15.50, -12.20, Y_REAR_EXT - 1.00, -2.00)
    bevel_r = _make_y_edge_fillet_cutter(1.20, -10.50, 1.40, 2.90, -12.20, Y_REAR_EXT - 1.00, -2.00)
    ch_bf = 0.60
    bevel_front = Part.Face(Part.makePolygon([
        App.Vector(-15.60, -2.780 + 0.30, z_cradle_bot - 0.30),
        App.Vector(-15.60, -2.780 - ch_bf - 0.30, z_cradle_bot - 0.30),
        App.Vector(-15.60, -2.780 + 0.30, z_cradle_bot + ch_bf + 0.30),
        App.Vector(-15.60, -2.780 + 0.30, z_cradle_bot - 0.30),
    ])).extrude(App.Vector(18.60, 0.0, 0.0))
    cradle = cradle.cut(bevel_l).cut(bevel_r).cut(bevel_front)
    fuses: list[Part.Shape] = [cradle]

    cuts: list[Part.Shape] = []
    # 1. Unified sunken Bare Eddy Duo PCB pocket + #1-#4 cable-bend relief above JST-SH header:
    #    Display X=[-1.01,+13.67], Y=[+5.00,+13.50], Z=[-12.50,+9.00] (open at bottom for downward coil drop).
    #    Carved around two monolithic Ø5.20 mm (R=2.60 mm) M2 mounting standoffs at exact lowered Eddy Duo PCB
    #    hole centers: Display (X=+1.115, Z=-8.090) and (X=+11.615, Z=-8.090) (10.50 mm pitch, Y_seat=+6.955 mm).
    pocket_box = make_box(-13.67, 1.01, Y_REAR_EXT - 1.50, -5.00, -12.50, 23.65 + dz)
    y_seat_int = -6.955      # Display Y=+6.955 mm (exact Bare Eddy Duo PCB front seating face!)
    y_floor_int = -5.000     # Display Y=+5.000 mm (pocket floor)
    r_standoff = 2.60        # Ø5.20 mm (matches BTT official Ø5.32 mm component-free pad keepout)
    ch_outer = 0.30          # 0.30 mm x 45 deg top outer chamfer on standoff seating face
    r_m2_bore = 1.15         # Ø2.30 mm M2 clearance through-bore (for M2x6 bolts into captive tunnel-side M2 nuts)
    ch_bore = 0.30           # 0.30 mm x 45 deg screw lead-in chamfer on standoff seating face
    m2_hex_af = 4.20         # DIN 934 M2 hex nut (4.00 mm nominal AF + 0.20 mm FDM snug press-fit clearance)
    y_m2_seat_int = -4.580   # Display Y=+4.580 mm (~1.80 mm deep from Y=+2.78 tunnel wall; 2.375 mm solid clamped seat!)
    y_m2_open_int = -1.500   # Exits cleanly into open hotend bay (wall front Y=+2.36..+2.90)

    eddy_hole_xs_int = (-1.115, -11.615)  # Display X = +1.115, +11.615 (10.50 mm exact pitch)
    eddy_hole_z = -4.440 + NOZZLE_DZ_EXTRA  # -8.090 mm display (exact -3.650 mm nozzle compensation!)

    standoff_keeps: list[Part.Shape] = []
    bore_cuts: list[Part.Shape] = []
    for hx_int in eddy_hole_xs_int:
        # Standoff body + chamfered seating tip (internal Y from y_seat_int to y_floor_int + 0.15)
        cyl_main = make_cyl_y(hx_int, eddy_hole_z, r_standoff, y_seat_int + ch_outer, y_floor_int + 0.15)
        cone_tip = Part.makeCone(
            r_standoff - ch_outer,
            r_standoff,
            ch_outer,
            App.Vector(hx_int, y_seat_int, eddy_hole_z),
            App.Vector(0.0, 1.0, 0.0),
        )
        standoff_keeps.append(cyl_main.fuse(cone_tip))

        # M2 clearance through-bore + lead-in chamfer from rear seating face into tunnel-side M2 hex pocket
        bore_shaft = make_cyl_y(hx_int, eddy_hole_z, r_m2_bore, y_seat_int - 0.50, y_m2_open_int)
        bore_chamf = Part.makeCone(
            r_m2_bore + ch_bore + 0.25,
            r_m2_bore,
            ch_bore + 0.25,
            App.Vector(hx_int, y_seat_int - 0.25, eddy_hole_z),
            App.Vector(0.0, 1.0, 0.0),
        )
        bore_cuts.append(bore_shaft.fuse(bore_chamf))

        # Tunnel-side captive M2 hex nut pocket (~1.80 mm deep from Y_disp=+2.78 tunnel wall to Y_disp=+4.58 seat)
        r_hex = m2_hex_af / math.sqrt(3.0)
        hex_pts = [
            App.Vector(
                hx_int + r_hex * math.cos(math.radians(60.0 * k + 30.0)),
                y_m2_seat_int,
                eddy_hole_z + r_hex * math.sin(math.radians(60.0 * k + 30.0)),
            )
            for k in range(6)
        ]
        hex_pts.append(hex_pts[0])
        m2_hex_pocket = Part.Face(Part.makePolygon(hex_pts)).extrude(
            App.Vector(0.0, y_m2_open_int - y_m2_seat_int, 0.0)
        )
        bore_cuts.append(m2_hex_pocket)

    standoff_keep_all = standoff_keeps[0].fuse(standoff_keeps[1])
    cuts.append(pocket_box.cut(standoff_keep_all))
    cuts.extend(bore_cuts)

    # 2. Smooth swept rear cable channel along Pins #10-#15 (Display XZ -> Internal X_int=-X_disp, Z)
    pts_disp = [
        (6.37,  7.05),   # #10 top of Eddy PCB bend pocket (Z_top=8.95 flush with pocket ceiling!)
        (11.40, 7.20),   # #11 gentle rightward sweep cleanly below right hotend hex nut
        (15.00, 8.80),   # #12 curving cleanly around right hotend hex nut (>=0.70 mm wall)
        (16.40, 11.40),  # #13 entering rear belt recess floor
        (16.95, 14.80),  # #14 climbing cleanly behind GT2 belt channel
        (17.00, 19.00),  # #15+ exiting cleanly into open motor portal (Z=17.75)
    ]
    r_ch = 1.90          # 3.80 mm channel width (comfortable 4-wire Eddy CAN/USB cable bend)
    y_ch_front = -7.50   # Y_disp=+7.50 (3.62 mm behind Y=+11.12 belt recess floor, 3.62 mm solid wall ahead!)
    y_ch_rear = Y_REAR_EXT - 1.50  # Open to extended rear face Y_disp=+13.117

    ch_parts: list[Part.Shape] = []
    for (x0d, z0d), (x1d, z1d) in zip(pts_disp[:-1], pts_disp[1:]):
        x0, z0 = -x0d, z0d
        x1, z1 = -x1d, z1d
        dx_s, dz_s = x1 - x0, z1 - z0
        seg_len = math.hypot(dx_s, dz_s)
        nx, nz = -dz_s / seg_len, dx_s / seg_len
        poly = Part.makePolygon([
            App.Vector(x0 + nx * r_ch, y_ch_rear, z0 + nz * r_ch),
            App.Vector(x1 + nx * r_ch, y_ch_rear, z1 + nz * r_ch),
            App.Vector(x1 - nx * r_ch, y_ch_rear, z1 - nz * r_ch),
            App.Vector(x0 - nx * r_ch, y_ch_rear, z0 - nz * r_ch),
            App.Vector(x0 + nx * r_ch, y_ch_rear, z0 + nz * r_ch),
        ])
        ch_parts.append(Part.Face(poly).extrude(App.Vector(0.0, y_ch_front - y_ch_rear, 0.0)))
        ch_parts.append(make_cyl_y(x0, z0, r_ch, y_ch_rear, y_ch_front))
    ch_parts.append(make_cyl_y(-pts_disp[-1][0], pts_disp[-1][1], r_ch, y_ch_rear, y_ch_front))
    channel_cut = ch_parts[0].multiFuse(ch_parts[1:]).removeSplitter()
    cuts.append(channel_cut)
    return fuses, cuts


def _build_eddy_side_heatset_pockets(dz: float) -> list[Part.Shape]:
    """Add two M3 heat-set insert pockets on the +X backplate side wall (4.6x5.7 mm insert spec).

    Display coords (dead-flat +X = +30.00 mm backplate wall, 9.24 mm thick with REAR_EXT_MM=2.00):
    - Shared Y_disp = +8.50 mm (4.62 mm forward of rear mating plane Y=+13.117, 2.52 mm rear wall,
      3.80 mm front wall to nearest grille opening, mouth chamfer clears R=1.60 rear fillet at Y=11.52).
    - Exact 12.00 mm vertical center-to-center pitch: Z = +7.50 mm and Z = -4.50 mm.
    - Ø4.20 mm (R=2.10 mm) x 6.50 mm deep + 0.40 mm entry chamfer.
    """
    x_entry = -30.00     # +30.00 mm display outer +X face
    y_int = -8.50        # +8.50 mm display (centered in extended 9.24 mm backplate)
    bore_r = 2.10        # Ø4.20 mm bore spec'd for 4.6x5.7 mm M3 heat-set inserts
    bore_depth = 6.50    # 6.50 mm deep (0.80 mm relief past 5.7 mm insert; ends at X=+23.50, 1.27 mm clear of hex nut)
    chamf_d = 0.40
    z_top = 22.15 + dz   # +7.50 mm display (#1)
    z_bot = 10.15 + dz   # -4.50 mm display (#2, exact 12.00 mm pitch)

    cuts: list[Part.Shape] = []
    for zc in (z_top, z_bot):
        shaft = Part.makeCylinder(
            bore_r,
            bore_depth + 0.25,
            App.Vector(x_entry - 0.25, y_int, zc),
            App.Vector(1.0, 0.0, 0.0),
        )
        chamf = Part.makeCone(
            bore_r + chamf_d,
            bore_r,
            chamf_d + 0.25,
            App.Vector(x_entry - 0.25, y_int, zc),
            App.Vector(1.0, 0.0, 0.0),
        )
        cuts.append(shaft.fuse(chamf))
    return cuts


def _build_outer_edge_round_cutters(dz: float, top_trim_z: float) -> list[Part.Shape]:
    """Round & chamfer all outer edges/corners for FDM anti-warping and clean aesthetics.

    Internal coords: +X = -X display (fan side), +Y = -Y display (front), +Z = up.
    - Top backplate outer corners: R=3.00 mm (preserves 2.96 mm wall around upper carriage hex nuts).
    - Front-left (#5) & front-right backplate vertical edges: symmetric R=1.60 mm all the way to top.
    - Bottom-left (#5) & bottom-right (#6, #7) outer edges: symmetric R=1.80 mm (0.44 mm clear of grille).
    - Entire rear bed-contacting outer perimeter (Y_disp=+11.117): continuous 0.80 mm x 45 deg
      anti-warp / anti-elephant's-foot chamfer around all four sides & rounded corners.
    - Top backplate front edge (Z=65.08): 0.80 mm x 45 deg chamfer.
    - Pared-down -X shroud mounting arm (#10-#13): 0.65 mm x 45 deg front & rear chamfers + R=1.00
      front-left vertical and top-left shoulder fillets at X_disp=-19.50.
    - Bottom hotend window (Z=-9.15) & front #8 hotend recess (Y_disp=-30.04): 45 deg perimeter chamfers.
    """
    z_floor = 5.50 + dz      # -9.15 mm display
    z_top_deck = 32.58 + dz  # +17.93 mm display
    z_top_bp = top_trim_z    # +65.08 mm display
    r_bot = 1.80
    r_top_bp = 3.00
    r_top = 1.00

    cutters: list[Part.Shape] = []

    # 1. Bottom-right (#6, #7) & bottom-left (#5) outer edges: symmetric R=1.80 mm
    cutters.append(_make_y_edge_fillet_cutter(-30.00 + r_bot, z_floor + r_bot, r_bot, -31.50, z_floor - 1.50, Y_REAR_EXT - 1.00, 29.00))
    cutters.append(_make_y_edge_fillet_cutter(30.00 - r_bot, z_floor + r_bot, r_bot, 31.50, z_floor - 1.50, Y_REAR_EXT - 1.00, -3.50))

    # 2. Symmetric R=1.60 mm front-left (#5) & front-right backplate vertical edges all the way to top trim
    cutters.append(_make_corner_fillet_cutter(28.40, -5.48, 1.60, 31.50, -3.40, z_floor - 1.00, z_top_bp + 1.50))
    cutters.append(_make_corner_fillet_cutter(-28.40, -5.48, 1.60, -31.50, -3.40, z_top_deck - 0.50, z_top_bp + 1.50))

    # 3. Top-left & top-right backplate outer corners: symmetric R=3.00 mm (eliminates sharp 90-deg top corners)
    cutters.append(_make_y_edge_fillet_cutter(30.00 - r_top_bp, z_top_bp - r_top_bp, r_top_bp, 31.50, z_top_bp + 1.50, Y_REAR_EXT - 1.50, Y_FRONT_BP + 1.50))
    cutters.append(_make_y_edge_fillet_cutter(-30.00 + r_top_bp, z_top_bp - r_top_bp, r_top_bp, -31.50, z_top_bp + 1.50, Y_REAR_EXT - 1.50, Y_FRONT_BP + 1.50))

    # 4. Entire bed-contacting rear outer perimeter (Y_disp=+13.117 -> Y_int=Y_REAR_EXT): 0.80 mm x 45 deg anti-warp chamfer
    #    Seamless L-junction union with downward Eddy cradle perimeter (X_int=[-15.20,+2.60], Z=[-11.90,-8.00])!
    ch_bed = 0.80
    bp_h = z_top_bp - z_floor
    bp_zc = 0.5 * (z_top_bp + z_floor)
    rear_slab = make_box(-32.0, 32.0, Y_REAR_EXT - 1.50, Y_REAR_EXT + ch_bed, -13.00, z_top_bp + 2.0)
    rear_keep_frustum = _make_rounded_rect_chamfer_frustum_y(
        0.0, bp_zc, 60.00, bp_h, r_top_bp, r_bot,
        y_inner=Y_REAR_EXT + ch_bed, y_face=Y_REAR_EXT, chamfer=ch_bed, expand_outward=False
    )
    # Matching pure Cone+Plane keep-frustum for downward Eddy cradle (R=1.40 mm corners + 0.80 mm rear bed chamfer)
    cradle_keep_frustum = _make_rounded_rect_chamfer_frustum_y(
        -6.30, -9.50, 17.80, 4.80, 1.40, 1.40,
        y_inner=Y_REAR_EXT + ch_bed, y_face=Y_REAR_EXT, chamfer=ch_bed, expand_outward=False
    )
    cutters.append(rear_slab.cut(rear_keep_frustum.fuse(cradle_keep_frustum)))

    # 5. Top backplate front edge (Z=65.08, Y_int=Y_FRONT_BP): 0.80 mm x 45 deg chamfer across full width
    ch_top_f = 0.80
    top_f_pts = [
        App.Vector(-32.0, Y_FRONT_BP - ch_top_f, z_top_bp + 0.50),
        App.Vector(-32.0, Y_FRONT_BP + 0.50, z_top_bp + 0.50),
        App.Vector(-32.0, Y_FRONT_BP + 0.50, z_top_bp - ch_top_f - 0.50),
        App.Vector(-32.0, Y_FRONT_BP - ch_top_f - 0.50, z_top_bp + 0.50),
        App.Vector(-32.0, Y_FRONT_BP - ch_top_f, z_top_bp + 0.50),
    ]
    cutters.append(Part.Face(Part.makePolygon(top_f_pts)).extrude(App.Vector(64.0, 0.0, 0.0)))

    # 6. Top-front & BOTH side-top R=1.00 mm fillets + continuous front-left & front-right vertical R=1.00 mm corners at Y_FRONT_NEW
    cutters.append(_make_x_edge_fillet_cutter(Y_FRONT_NEW - r_top, z_top_deck - r_top, r_top, Y_FRONT_NEW + 2.00, z_top_deck + 1.50, 0.27, 20.50))
    cutters.append(_make_x_edge_fillet_cutter(Y_FRONT_NEW - r_top, z_top_deck - r_top, r_top, Y_FRONT_NEW + 2.00, z_top_deck + 1.50, -30.50, -18.04))
    cutters.append(_make_y_edge_fillet_cutter(19.50 - r_top, z_top_deck - r_top, r_top, 21.00, z_top_deck + 1.50, Y_FRONT_BP + 0.05, Y_FRONT_NEW + 1.00))
    # +X top deck edge R=1.00 mm continuous fillet stopping cleanly at Y_FRONT_BP (zero bite into backplate #10!)
    cutters.append(_make_y_edge_fillet_cutter(-30.00 + r_top, z_top_deck - r_top, r_top, -31.50, z_top_deck + 1.50, Y_FRONT_BP + 0.05, Y_FRONT_NEW + 1.00))
    # Continuous front-left vertical corner at (X_disp=-19.50, Y_disp=-26.40) extended past lower ramp (eliminates notch #8!)
    cutters.append(_make_corner_fillet_cutter(19.50 - r_top, Y_FRONT_NEW - r_top, r_top, 21.50, Y_FRONT_NEW + 2.00, z_floor - 8.00, z_top_deck + 1.00))
    # Continuous front-right vertical corner at (X_disp=+30.00, Y_disp=-26.40)
    cutters.append(_make_corner_fillet_cutter(-30.00 + r_top, Y_FRONT_NEW - r_top, r_top, -31.50, Y_FRONT_NEW + 2.00, z_floor - 1.50, z_top_deck + 1.00))
    # Bottom-front horizontal 0.80 mm x 45 deg anti-warp bevel along Y_FRONT_NEW, Z=-9.15 (smooths #11!)
    ch_bf = 0.80
    bf_pts = [
        App.Vector(-31.0, Y_FRONT_NEW - ch_bf, z_floor - 0.50),
        App.Vector(-31.0, Y_FRONT_NEW + 0.50, z_floor - 0.50),
        App.Vector(-31.0, Y_FRONT_NEW + 0.50, z_floor + ch_bf + 0.50),
        App.Vector(-31.0, Y_FRONT_NEW - ch_bf - 0.50, z_floor - 0.50),
        App.Vector(-31.0, Y_FRONT_NEW - ch_bf, z_floor - 0.50),
    ]
    cutters.append(Part.Face(Part.makePolygon(bf_pts)).extrude(App.Vector(33.50, 0.0, 0.0)))

    # 8. Bottom hotend window perimeter (Z=-9.15, X_disp=[-1.97,+14.63], Y_disp=[-23.17,+2.58]): 0.75 mm x 45 deg chamfer
    #    Rear Y edge clamped at -2.780 so #8 stops cleanly flush with downward Eddy cradle front wall (zero hex notch!).
    ch_win = 0.75
    # Internal coords: X_int=[-14.63,+1.97], Y_int=[-2.58,+23.17]
    w_win_in = Part.makePolygon([
        App.Vector(-14.63, -2.58, z_floor + ch_win),
        App.Vector(1.97, -2.58, z_floor + ch_win),
        App.Vector(1.97, 23.17, z_floor + ch_win),
        App.Vector(-14.63, 23.17, z_floor + ch_win),
        App.Vector(-14.63, -2.58, z_floor + ch_win),
    ])
    over_w = ch_win + 0.25
    w_win_out = Part.makePolygon([
        App.Vector(-14.63 - over_w, -2.78, z_floor - 0.25),
        App.Vector(1.97 + over_w, -2.78, z_floor - 0.25),
        App.Vector(1.97 + over_w, 23.17 + over_w, z_floor - 0.25),
        App.Vector(-14.63 - over_w, 23.17 + over_w, z_floor - 0.25),
        App.Vector(-14.63 - over_w, -2.78, z_floor - 0.25),
    ])
    cutters.append(Part.makeLoft([w_win_in, w_win_out], True, True))

    # 9. Front #8 hotend recess perimeter (Y_disp=-26.40, X_disp=[-0.27,+18.04], Z=[10.00,17.93]): 0.60 mm x 45 deg chamfer
    ch_f8 = 0.60
    # Internal coords: X_int=[-18.04,+0.27], Y_int=Y_FRONT_NEW
    z_f8_bot = 24.65 + dz  # 10.00 mm display (flush with leveled floor #1+#2!)
    y_f8 = Y_FRONT_NEW
    w_f8_in = Part.makePolygon([
        App.Vector(-18.04, y_f8 - ch_f8, z_f8_bot),
        App.Vector(0.27, y_f8 - ch_f8, z_f8_bot),
        App.Vector(0.27, y_f8 - ch_f8, z_top_deck + 1.00),
        App.Vector(-18.04, y_f8 - ch_f8, z_top_deck + 1.00),
        App.Vector(-18.04, y_f8 - ch_f8, z_f8_bot),
    ])
    over_f8 = ch_f8 + 0.25
    w_f8_out = Part.makePolygon([
        App.Vector(-18.04 - over_f8, y_f8 + 0.25, z_f8_bot - over_f8),
        App.Vector(0.27 + over_f8, y_f8 + 0.25, z_f8_bot - over_f8),
        App.Vector(0.27 + over_f8, y_f8 + 0.25, z_top_deck + 1.00),
        App.Vector(-18.04 - over_f8, y_f8 + 0.25, z_top_deck + 1.00),
        App.Vector(-18.04 - over_f8, y_f8 + 0.25, z_f8_bot - over_f8),
    ])
    cutters.append(Part.makeLoft([w_f8_in, w_f8_out], True, True))

    # 9b. Smooth #4-#7 sharp edges along #8 upper-rear lip (Y_disp=-24.42 -> Y_int=24.42) & #3 wire-bay corner
    y_lip = 24.42
    # Upper deck rear lip chamfer (Z=17.93, Y_disp=-24.42): 0.70 mm x 45 deg across X_disp=[-0.27,+18.04]
    ch_lip = 0.70
    lip_top_pts = [
        App.Vector(-18.20, y_lip - ch_lip, z_top_deck + 0.40),
        App.Vector(-18.20, y_lip + 0.40, z_top_deck + 0.40),
        App.Vector(-18.20, y_lip + 0.40, z_top_deck - ch_lip - 0.40),
        App.Vector(-18.20, y_lip - ch_lip - 0.40, z_top_deck + 0.40),
        App.Vector(-18.20, y_lip - ch_lip, z_top_deck + 0.40),
    ]
    cutters.append(Part.Face(Part.makePolygon(lip_top_pts)).extrude(App.Vector(18.60, 0.0, 0.0)))
    # Smooth #3 protruding vertical wire-bay corner at (X_disp=+12.94, Y_disp=-20.00): R=1.50 mm vertical fillet
    cutters.append(_make_corner_fillet_cutter(-12.94 - 1.50, 20.00 - 1.50, 1.50, -12.00, 21.00, 24.50 + dz, 31.20 + dz))

    # 10. Subtle 0.40 mm x 45 deg bed-contact chamfer along Eddy rear pocket vertical edges (anti-elephant's-foot)
    ch_ed = 0.40
    z_ed0 = -12.20
    for x_edge, sign in [(-13.67, -1.0), (1.01, 1.0)]:
        ed_pts = [
            App.Vector(x_edge, Y_REAR_EXT - 0.30, z_ed0),
            App.Vector(x_edge + sign * (ch_ed + 0.30), Y_REAR_EXT - 0.30, z_ed0),
            App.Vector(x_edge - sign * 0.30, Y_REAR_EXT + ch_ed + 0.30, z_ed0),
            App.Vector(x_edge - sign * 0.30, Y_REAR_EXT - 0.30, z_ed0),
            App.Vector(x_edge, Y_REAR_EXT - 0.30, z_ed0),
        ]
        cutters.append(Part.Face(Part.makePolygon(ed_pts)).extrude(App.Vector(0.0, 0.0, (23.65 + dz) - z_ed0)))

    return cutters


def _build_lower_rear_flush_parts(dz: float, top_trim_z: float = 65.08) -> tuple[list[Part.Shape], list[Part.Shape]]:
    """Extend the entire rear carriage face (#5-#8) back by REAR_EXT_MM (2.00 mm -> Y_REAR_EXT=-13.117).

    Fuses a clean planar backplate extension across the full width (-29.998..+30.000) and height
    (5.500+dz .. top_trim_z+1.0), fills the lower recessed rear arch flush, trims both rear vertical
    corners to R=1.60 mm, and shifts the 2.00 mm deep horizontal GT2 belt channel onto the extended rear face.
    """
    z0 = 5.500 + dz
    z1 = max(6.500, top_trim_z + 1.00)
    # 1. Lower arch fill (from original Y_FRONT_BP all the way back to Y_REAR_EXT)
    lower_block = make_box(-29.998, 30.000, Y_REAR_EXT - 0.10, Y_FRONT_BP, z0, 6.500)
    # 2. Full-height 2.00 mm rear spacer extension: starts at Y_REAR_MATING+2.00 (-9.117) so it completely
    #    covers bp_blank's legacy R=1.60 rear corner fillets (which ended at -9.517), eliminating side seams (#5-#13)!
    rear_ext_slab = make_box(-29.998, 30.000, Y_REAR_EXT - 0.10, Y_REAR_MATING + 2.00, z0, z1)
    r_fillet = 1.600
    y_c = Y_REAR_EXT + r_fillet
    # Re-establish the 2.00 mm deep horizontal GT2 belt clearance channel on the extended rear face:
    # - Full 2.00 mm depth (Y_REAR_MATING=-11.117) across Z=[9.00,17.75] so both X1C hotend hex nuts sit 100%
    #   flush with zero protruding lower nubs (#1+#2) and clears shifted GT2 belt (Z=[13.0,17.0], Y_int=[-13.12,-11.90]).
    # - 45-deg lower bevel (Z=7.00..9.00) and 45-deg upper chamfer (Z=17.75..19.75) smoothing edges #3+#4!
    belt_prof = Part.makePolygon([
        App.Vector(-28.00, Y_REAR_EXT - 1.00, 7.00),
        App.Vector(-28.00, Y_REAR_EXT, 7.00),
        App.Vector(-28.00, Y_REAR_MATING, 9.00),
        App.Vector(-28.00, Y_REAR_MATING, 17.75),
        App.Vector(-28.00, Y_REAR_EXT, 19.75),
        App.Vector(-28.00, Y_REAR_EXT - 1.00, 19.75),
        App.Vector(-28.00, Y_REAR_EXT - 1.00, 7.00),
    ])
    belt_groove_cut = Part.Face(belt_prof).extrude(App.Vector(56.00, 0.0, 0.0))
    cutters = [
        _make_corner_fillet_cutter(-28.400, y_c, r_fillet, -31.0, Y_REAR_EXT - 1.0, z0 - 0.5, z1 + 0.5),
        _make_corner_fillet_cutter(28.400, y_c, r_fillet, 31.0, Y_REAR_EXT - 1.0, z0 - 0.5, z1 + 0.5),
        belt_groove_cut,
    ]
    return [lower_block, rear_ext_slab], cutters


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
    front_shroud_hex_on = bool(params["remove_front_magnet_holders_and_add_hex"])
    orbiter_hex_on = bool(params["orbiter_tunnel_hex_nut_pockets"])
    fan_heatset_boss_on = bool(params["fan3010_lower_front_heatset_boss"])
    dz_fan = float(params["fan3010_z_shift_mm"])
    fan_remove_floor = bool(params["fan3010_remove_bottom_floor"])
    airflow_ramp_on = bool(params["airflow_ramp_6_to_7"])
    lower_floor_ramp_on = bool(params["lower_floor_airflow_ramp"])
    top_trim_z = float(params["top_backplate_trim_z_mm"])
    top_bridge_full = bool(params["top_bridge_full_thickness"])
    motor_full_square = bool(params["motor_portal_full_through_square"])
    motor_top_raise = float(params["motor_portal_top_raise_mm"])
    hotend_ceil_match = bool(params["hotend_top_profile_ceiling_match"])
    round_outer_3_7 = bool(params["round_outer_corners_3_to_7"])

    z_mot = BASE_Z_MOT + dz
    z_mount = BASE_Z_MOUNT + dz
    z_hotend_screw = BASE_HOTEND_SCREW_Z + dz

    bp_blank = cache["bp_blank"].copy()
    # Overlap -0.08 mm along Y (from Y_FRONT_BP + 0.02 -> Y_FRONT_BP - 0.06) to prevent coplanar OCCT fuse issues
    front_shifted = _translate_copy(cache["front_toolhead"], 0.0, -0.08, dz)

    fuse_parts: list[Part.Shape] = [bp_blank, front_shifted]
    cut_parts: list[Part.Shape] = []

    if lower_rear_flush:
        flush_fuses, flush_cuts = _build_lower_rear_flush_parts(dz, top_trim_z=top_trim_z)
        fuse_parts.extend(flush_fuses)
        cut_parts.extend(flush_cuts)

    if access_on:
        sleeves, access_tunnels = _build_carriage_access_sleeves(front_shifted, sleeve_r, bore_r)
        fuse_parts.extend(sleeves)
        cut_parts.extend(access_tunnels)

    fan_lower_fuses: list[Part.Shape] = []
    fan_lower_cuts: list[Part.Shape] = []
    fan_boss_protects: list[Part.Shape] = []
    if abs(dz_fan) > 1e-3:
        fan_lower_fuses, fan_lower_cuts, fan_boss_protects = _build_lowered_fan3010_mount_parts(
            dz, dz_fan, remove_floor=fan_remove_floor, lower_floor_ramp=lower_floor_ramp_on
        )

    if top_bridge_full:
        # Fill the unused rear dome recess between Pins #10 & #11 flush with Y_REAR_EXT (-13.117)
        # AND fill the two 0.28 mm upper-corner bearing-groove remnants (#3-#6 at X=+-22..28, Z=64.80..65.08)
        fuse_parts.append(make_box(-22.00, 22.00, Y_REAR_EXT - 0.10, Y_FRONT_BP, 52.50, 66.00))
        fuse_parts.append(make_box(-28.40, -21.50, Y_REAR_EXT - 0.10, -8.50, 64.00, 66.00))
        fuse_parts.append(make_box(21.50, 28.40, Y_REAR_EXT - 0.10, -8.50, 64.00, 66.00))

    front_fuses: list[Part.Shape] = []
    front_cuts: list[Part.Shape] = []
    if front_shroud_hex_on:
        front_fuses, front_cuts = _build_front_shroud_mount_hex_parts(dz, carriage_hex_af)

    if simplify_duct:
        duct_fuses, duct_cuts = _build_simplified_fan_duct_parts(dz, airflow_ramp=airflow_ramp_on, dz_fan=dz_fan)
        if fan_heatset_boss_on:
            _boss_protect, _ = _build_fan3010_lower_front_heatset_boss(dz)
            duct_cuts = [dc.cut(_boss_protect) for dc in duct_cuts]
        if fan_boss_protects:
            # Protect all 4 lowered 3010 fan heat-set bosses & roof seal from the simplified tunnel cutout
            protect_all = fan_boss_protects[0].multiFuse(fan_boss_protects[1:]) if len(fan_boss_protects) > 1 else fan_boss_protects[0]
            duct_cuts = [dc.cut(protect_all) for dc in duct_cuts]
        if front_fuses:
            # Protect the two symmetric inside-tunnel M3 shroud hex nut bosses (#8 & #9) from tunnel cutouts!
            front_protect = front_fuses[0].multiFuse(front_fuses[1:]) if len(front_fuses) > 1 else front_fuses[0]
            duct_cuts = [dc.cut(front_protect) for dc in duct_cuts]
        fuse_parts.extend(duct_fuses)
        cut_parts.extend(duct_cuts)

    if fan_heatset_boss_on:
        fan_boss_solid, fan_boss_bore = _build_fan3010_lower_front_heatset_boss(dz)
        fuse_parts.append(fan_boss_solid)
        cut_parts.append(fan_boss_bore)

    if fan_lower_fuses or fan_lower_cuts:
        fuse_parts.extend(fan_lower_fuses)
        cut_parts.extend(fan_lower_cuts)

    if carriage_hex_on:
        hex_fuses, hex_cuts = _build_carriage_hex_nut_parts(carriage_hex_af)
        fuse_parts.extend(hex_fuses)
        cut_parts.extend(hex_cuts)

    if front_fuses or front_cuts:
        fuse_parts.extend(front_fuses)
        cut_parts.extend(front_cuts)

    if orbiter_hex_on:
        orb_fuses, orb_cuts = _build_orbiter_tunnel_hex_parts(dz, carriage_hex_af)
        fuse_parts.extend(orb_fuses)
        cut_parts.extend(orb_cuts)

    if hotend_ceil_match:
        fuse_parts.append(_build_hotend_top_profile_ceiling(dz))

    # Replace legacy 6-hex +X grille with high-airflow, self-supporting 13-cell peak-Y honeycomb grille
    grille_fuses, grille_cuts = _build_high_airflow_honeycomb_grille(dz)
    fuse_parts.extend(grille_fuses)
    cut_parts.extend(grille_cuts)

    # Downward Eddy housing cradle fused before cutters; rear pocket & cable channel cut in Step #8
    eddy_fuses, eddy_cuts = _build_eddy_rear_pocket_and_cable_channel(dz)
    fuse_parts.extend(eddy_fuses)

    body = fuse_parts[0]
    for fp in fuse_parts[1:]:
        body = body.fuse(fp)

    # Skim any sub-micron tolerance protrusion or overlap behind exact Y_REAR_EXT so the extended rear plane is one clean face
    cut_parts.append(make_box(-35.0, 35.0, Y_REAR_EXT - 3.0, Y_REAR_EXT, -20.0, 90.0))

    # 1 & 2. Backplate motor portal (either full-through raised rounded-square or legacy stepped circle + web relief)
    flank_w = 2.0 * (22.47 + flank_clear)
    if motor_full_square:
        portal_z0 = 32.58 + dz  # 17.93 mm (exact coplanar match with top deck; clears Orbiter 18.36 mm by 0.43 mm!)
        portal_z1 = max(z_mot + mot_r, 70.12 + flank_clear + dz) + motor_top_raise  # 57.75 mm (+1.0 mm above Pin #2)
        portal_h = portal_z1 - portal_z0
        portal_zc = 0.5 * (portal_z0 + portal_z1)
        cut_parts.append(
            make_rounded_rect_y(
                0.0,
                portal_zc,
                flank_w,
                portal_h,
                8.0,
                Y_REAR_EXT - 2.0,
                Y_FRONT_BP + 0.1,
            )
        )
        if round_outer_3_7:
            # Anti-warp 45-deg chamfers on BOTH front (1.00 mm, clipped >= Z=17.93 so top deck has zero seam) and rear/bed (0.80 mm)
            cut_parts.append(
                _make_rounded_rect_chamfer_frustum_y(
                    0.0, portal_zc, flank_w, portal_h, 8.0, 8.0,
                    y_inner=Y_FRONT_BP - 1.00, y_face=Y_FRONT_BP, chamfer=1.00, expand_outward=True,
                ).common(make_box(-35.0, 35.0, -20.0, 5.0, portal_z0, 80.0))
            )
            cut_parts.append(
                _make_rounded_rect_chamfer_frustum_y(
                    0.0, portal_zc, flank_w, portal_h, 8.0, 8.0,
                    y_inner=Y_REAR_EXT + 0.80, y_face=Y_REAR_EXT, chamfer=0.80, expand_outward=True,
                )
            )
    else:
        cut_parts.append(make_cyl_y(0.0, z_mot, mot_r, Y_REAR_EXT - 2.0, Y_FRONT_BP + 0.1))
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
        oval_y0 = (Y_REAR_EXT - 2.0) if oval_full else Y_WEB_FRONT
        cut_parts.append(make_stadium_y(0.0, oval_zc, oval_w, oval_h, oval_y0, Y_FRONT_BP + 0.2))
        if round_outer_3_7:
            oval_r = max(0.5, min(oval_h * 0.5, oval_w * 0.5 - 0.01))
            cut_parts.append(
                _make_rounded_rect_chamfer_frustum_y(
                    0.0, oval_zc, oval_w, oval_h, oval_r, oval_r,
                    y_inner=Y_FRONT_BP - 0.80, y_face=Y_FRONT_BP, chamfer=0.80, expand_outward=True,
                )
            )
            if oval_full:
                cut_parts.append(
                    _make_rounded_rect_chamfer_frustum_y(
                        0.0, oval_zc, oval_w, oval_h, oval_r, oval_r,
                        y_inner=Y_REAR_EXT + 0.80, y_face=Y_REAR_EXT, chamfer=0.80, expand_outward=True,
                    )
                )

    # 4. Shifted X1C hotend M3 hex nut pockets + bores cleanly passing Y_REAR_EXT..Y_FRONT_BP
    # (y_seat stays at r6.HEX_NUT_SEAT_Y so hotend bolts clamp identically; mouth chamfer sits on Y_REAR_MATING belt recess floor)
    for _hname, hx in r6.HOTEND_SCREW_XS:
        cut_parts.append(
            r6.make_hex_nut_pocket(
                hx,
                z_hotend_screw,
                r6.HEX_NUT_AF,
                rear_y=Y_REAR_EXT - 1.5,
                y_seat=r6.HEX_NUT_SEAT_Y,
            )
        )
        cut_parts.append(
            r6.make_hex_nut_pocket(
                hx,
                z_hotend_screw,
                r6.HEX_NUT_AF + r6.HEX_CHAMFER_EXTRA_AF,
                rear_y=Y_REAR_EXT - 1.5,
                y_seat=Y_REAR_MATING + r6.HEX_CHAMFER_DEPTH,
            )
        )
        cut_parts.append(make_cyl_y(hx, z_hotend_screw, 1.75, Y_REAR_EXT - 1.5, 9.50))

    # 5. Enlarged thermistor / heater wire passage beside hotend heatsink (+X display / -X internal)
    cut_parts.extend(_build_hotend_wire_cutouts(dz, wire_extra_x))

    # 6. Trim everything above Pins #8 & #9 (Z = 65.08 mm), removing bearing groove while retaining knub cradle
    if 60.0 < top_trim_z < 85.0:
        cut_parts.append(make_box(-35.0, 35.0, -35.0, 35.0, top_trim_z, 95.0))

    # 7. Round & chamfer all outer edges/corners (anti-warp FDM pass + pared-down -X arm)
    if round_outer_3_7:
        cut_parts.extend(_build_outer_edge_round_cutters(dz, top_trim_z))

    # 8. Carve sunken rear bare Eddy Duo PCB pocket (#1-#2) + #1-#4 bend relief + swept cable channel (#10-#15)
    #    (+X side Eddy bracket heat-set holes #14/#15 removed — bare Eddy now mounts centered in rear pocket)
    cut_parts.extend(eddy_cuts)

    # Apply cuts sequentially (avoids OCCT compound self-intersection failures)
    r8_shape = body
    for tool in cut_parts:
        r8_shape = r8_shape.cut(tool)
    r8_shape = _keep_significant_solids(r8_shape)
    r8_clean = r8_shape.removeSplitter()
    if r8_clean.isValid() and len(r8_clean.Solids) == 1:
        r8_shape = r8_clean

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
    fan_shifted = _translate_copy(cache["ref_fan3010"], 0.0, 0.0, dz + dz_fan)
    ebb = cache["ref_ebb42"]
    # Carriage, knubs & belts sit REAR_EXT_MM further back (-Y internal / +Y display) when rear face is extended
    carriage = _translate_copy(cache["ref_carriage"], 0.0, -REAR_EXT_MM, 0.0)
    knubs = _translate_copy(cache["ref_knubs"], 0.0, -REAR_EXT_MM, 0.0)
    belts = _translate_copy(cache["ref_belts"], 0.0, -REAR_EXT_MM, 0.0)

    eddy_pcb_vol = "skipped_fast_mode"
    eddy_pcb_min_dist = "skipped_fast_mode"
    if full_checks:
        eddy_built = _build_bare_eddy_pcb_display()
        if eddy_built is not None:
            bare_pcb_disp, main_pcb_disp = eddy_built
            eddy_pcb_vol = round(_safe_common_vol(r8_display, main_pcb_disp), 3)
            eddy_pcb_min_dist = round(float(r8_display.distToShape(bare_pcb_disp)[0]), 3)

    checks = {
        "orbiter_vs_adapter_mm3": round(_safe_common_vol(r8_shape, orb_shifted), 3),
        "orbiter_vs_gray_carriage_mm3": round(_safe_common_vol(carriage, orb_shifted), 3),
        "hotend_vs_adapter_mm3": round(_safe_common_vol(r8_shape, he_shifted), 3) if full_checks else "skipped_fast_mode",
        "fan3010_vs_adapter_mm3": round(_safe_common_vol(r8_shape, fan_shifted), 3),
        "knubs_vs_adapter_mm3": round(_safe_common_vol(r8_shape, knubs), 3),
        "belts_vs_adapter_mm3": round(_safe_common_vol(r8_shape, belts), 3),
        "ebb42_vs_adapter_mm3": round(_safe_common_vol(r8_shape, ebb), 3),
        "eddy_main_pcb_vs_adapter_mm3": eddy_pcb_vol,
        "eddy_bare_pcb_min_dist_mm": eddy_pcb_min_dist,
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
            "nozzle_z_real_mm": round(he_shifted.BoundBox.ZMin + NOZZLE_DZ_EXTRA, 3),
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
    _export_web_meshes(r8_display, cache, report, dz_fan=dz_fan)

    # Atomically swap LIVE_STEP_PATH after report + meshes are written so viewers see fresh data
    os.replace(tmp_step, LIVE_STEP_PATH)

    if update_fcstd:
        _write_fcstd_workspace(r8_display, cache, params, dz, dz_fan=dz_fan)

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
        ("remove_front_magnet_holders_and_add_hex", "App::PropertyBool", "Remove front semicircular magnet holders and add inside-tunnel M3 hex nut sockets"),
        ("orbiter_tunnel_hex_nut_pockets", "App::PropertyBool", "Add upward-entry inside-tunnel M3 hex nut sockets for Orbiter v2.5 mounts"),
        ("fan3010_lower_front_heatset_boss", "App::PropertyBool", "Add legacy Z=-4.40 boss (superseded when fan3010_z_shift_mm != 0)"),
        ("fan3010_z_shift_mm", "App::PropertyFloat", "Vertical Z shift applied to 3010 fan mount & 4 heat-set bosses (mm)"),
        ("fan3010_remove_bottom_floor", "App::PropertyBool", "Remove bottom floor strip under 3010 fan bay (Pin #5)"),
        ("airflow_ramp_6_to_7", "App::PropertyBool", "Angle partition wall into smooth ramp from Pin #7 (X=-7.67,Z=16.20) to Pin #6 (X=-3.27,Z=10.00)"),
        ("lower_floor_airflow_ramp", "App::PropertyBool", "Add sealed lower airflow ramp from bottom of lowered fan bosses up to flat tunnel floor"),
        ("top_backplate_trim_z_mm", "App::PropertyFloat", "Trim backplate above this Z height (retains carriage knub indexing cradle at Z=63.5..65.08)"),
        ("top_bridge_full_thickness", "App::PropertyBool", "Fill unused rear recess between Pins #10 & #11 to full backplate thickness"),
        ("motor_portal_full_through_square", "App::PropertyBool", "Cut rounded-square motor portal all the way through backplate (removing thin crescent walls)"),
        ("motor_portal_top_raise_mm", "App::PropertyFloat", "Extra upward height added to top of backplate motor portal (mm)"),
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
    dz_fan: float = 0.0,
) -> None:
    """Create R8_Live_Workspace.FCStd with VarSet + Adapter + Reference parts (-Y=Front, +Y=Back)."""
    doc = App.newDocument("R8_Live_Workspace")
    _ensure_varset(doc, params)
    _add_part_obj(doc, "R8_Adapter", r8_display)
    _add_part_obj(doc, "Ref_Gray_AD5M_Carriage", _rotate_z180_baked(_translate_copy(cache["ref_carriage"], 0.0, -REAR_EXT_MM, 0.0)))
    _add_part_obj(doc, "Ref_Belts_Keepout", _rotate_z180_baked(_translate_copy(cache["ref_belts"], 0.0, -REAR_EXT_MM, 0.0)))
    _add_part_obj(doc, "Ref_Orbiter_v25", _rotate_z180_baked(cache["ref_orbiter"]), dz)
    _add_part_obj(doc, "Ref_X1C_Hotend", _extend_hotend_ref_display(_rotate_z180_baked(cache["ref_hotend"])), dz)
    _add_part_obj(doc, "Ref_3010_Fan", _rotate_z180_baked(cache["ref_fan3010"]), dz + dz_fan)
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
