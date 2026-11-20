"""Build two BambuMod x Orbiter v2.5 AD5M carriage adapter remixes:

1. BambuMod_Orbiter25_Primary_R1:
   - Keeps motor centered (X_mot = 0.00 mm), re-oriented for Orbiter v2.5's +-30 deg slanted
     motor mount ears + LDO-36STH20-1004AHG stator + 7:30 JST-PH connector relief.
   - Offsets the Bambu X1C hotend mount -6.335 mm right (-X_upright, toward right-side Eddy probe)
     so the filament path remains straight vertically despite Orbiter's 6.335 mm motor-to-filament offset.
   - Adds a horizontal Orbiter v2.5 mounting plate (XY plane at Z_mount = 32.60 mm) replacing stock
     perpendicular extruder mount, keeping stock 3010 fan pocket untouched.

2. BambuMod_Orbiter25_Alt_ShiftedMotor_R1:
   - Preserves stock Bambu X1C hotend & nozzle position (X_fil = 0.00 mm), cleaning up the stock
     top-fin collision (52.05 mm^3) with a full-clearance heatsink pocket.
   - Shifts & enlarges the backplate motor cutout off-center (X_mot = +6.335 mm) with +-30 deg
     slanted ear pockets and JST connector relief, while keeping (+24, 61) M3 carriage hole intact.
   - Relocates the 3010 heatsink fan pod (-5.5 mm down, +3.5 mm outboard to X=[23.0, 33.0],
     Z=[1.75, 31.75]) cleanly below the horizontal Orbiter plate (Z_mount = 32.00 mm) and outboard of
     the (+19.0, 3.5) carriage bolt.

Coordinate system (upright STEP & internal CAD):
  +X : Left (3010 fan side)     -X : Right (BTT Eddy side)
  +Y : Front (vent cover side)  -Y : Rear (AD5M steel X-carriage @ Y = -11.117 mm)
  +Z : Up (EBB42 top @ Z = 80)  -Z : Down (nozzle tip @ Z = -13.58 mm)

STL print orientation:
  Rotated +90 deg about +X and translated so the flat rear carriage face (Y = -11.117 mm)
  sits on Z_stl = 0.000 mm (+Y_upright grows vertically up for support-free printing).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import FreeCAD as App
from FreeCAD import Vector
import Mesh
import MeshPart
import Part

REPO = Path(__file__).resolve().parents[2]
REF_DIR = REPO / "reference"
OUT_DIR = REPO / "outputs" / "BambuMod_Orbiter25_Remix_R1"


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl_y(r: float, x: float, z: float, y0: float, y1: float) -> Part.Shape:
    return Part.makeCylinder(r, y1 - y0, Vector(x, y0, z), Vector(0, 1, 0))


def cyl_z(r: float, x: float, y: float, z0: float, z1: float) -> Part.Shape:
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def cyl_x(r: float, y: float, z: float, x0: float, x1: float) -> Part.Shape:
    return Part.makeCylinder(r, x1 - x0, Vector(x0, y, z), Vector(1, 0, 0))


def stadium_xz_y(x0: float, z0: float, x1: float, z1: float, r: float, y0: float, y1: float) -> Part.Shape:
    """Rounded slot extruded along Y between (x0, z0) and (x1, z1) with radius r."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    nx, nz = -uz, ux
    p1 = Vector(x0 + nx * r, y0, z0 + nz * r)
    p2 = Vector(x1 + nx * r, y0, z1 + nz * r)
    p3 = Vector(x1 - nx * r, y0, z1 - nz * r)
    p4 = Vector(x0 - nx * r, y0, z0 - nz * r)
    mid1 = Vector(x1 + ux * r, y0, z1 + uz * r)
    mid2 = Vector(x0 - ux * r, y0, z0 - uz * r)
    e1 = Part.makeLine(p1, p2)
    e2 = Part.Arc(p2, mid1, p3).toShape()
    e3 = Part.makeLine(p3, p4)
    e4 = Part.Arc(p4, mid2, p1).toShape()
    face = Part.Face(Part.Wire([e1, e2, e3, e4]))
    return face.extrude(Vector(0, y1 - y0, 0))


def upright_bm(shape: Part.Shape) -> Part.Shape:
    c = shape.copy()
    c.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 180)
    c.translate(Vector(0, 0, 92.21775))
    return c


def orbiter_xform(shape: Part.Shape, x_fil: float, z_mount: float) -> Part.Shape:
    c = shape.copy()
    c.translate(Vector(1.437, 7.859, 10.3032))
    c.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 180)
    c.translate(Vector(x_fil, 12.08, z_mount))
    return c


def load_references() -> dict:
    bm_shape = Part.read(str(REF_DIR / "BambuMod" / "bambumod_remix_and_vent_cover.step"))
    bm_cover = upright_bm(bm_shape.Solids[0])
    bm_body = upright_bm(bm_shape.Solids[1])

    ebb_bkt = Part.read(str(REPO / "outputs" / "EBB42_uniform_posts_R7" / "EBB42_short_bridge_R7.step")).Solids[0]

    he_shape = Part.read(str(REF_DIR / "Bambu_X1_hotend_CAD" / "Bambu_X1_P1_original_hotend_Jorge.STEP"))
    he_raw = he_shape.Solids[0].copy()
    for s in he_shape.Solids[1:]:
        he_raw = he_raw.fuse(s)
    he_raw.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 90)
    he_raw.translate(Vector(0, 0, 4))
    he_raw.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 90)
    he_raw.translate(Vector(0, 12.08, -13.58))

    orb_step = Part.read(str(REF_DIR / "Orbiter_v2_5" / "Orbiter_v2.0_mockup" / "Orbiter v2.0 mockup.step"))
    # Exclude floating mounting bolts (1, 2); add +3 mm cylinder tail representing LDO-36STH20-1004AHG
    orb_body_solids = [s for i, s in enumerate(orb_step.Solids) if i not in (1, 2)]
    mot_tail = Part.makeCylinder(18.2, 3.0, Vector(-7.772, 27.50, 8.997), Vector(0, 1, 0))
    orb_body_solids.append(mot_tail)
    orb_bolts = [orb_step.Solids[1], orb_step.Solids[2]]

    return {
        "bm_body": bm_body,
        "bm_cover": bm_cover,
        "ebb_bkt": ebb_bkt,
        "he_raw": he_raw,
        "orb_body_solids": orb_body_solids,
        "orb_bolts": orb_bolts,
    }


def detect_backplate_y_planes(bm_body: Part.Shape) -> tuple[float, float]:
    """Find exact coplanar rear/front Y planes of the BambuMod backplate."""
    rear_y = bm_body.BoundBox.YMin
    front_candidates = []
    for f in bm_body.Faces:
        if f.Area > 200 and f.Surface.TypeId == "Part::GeomPlane":
            n = f.normalAt(0, 0)
            if abs(n.y) > 0.99 and -4.5 < f.CenterOfMass.y < -3.5:
                front_candidates.append((f.Area, f.CenterOfMass.y))
    front_y = max(front_candidates)[1] if front_candidates else -3.881
    return float(rear_y), float(front_y)


def build_variant(refs: dict, cfg: dict) -> tuple[Part.Shape, dict]:
    """Build either Primary or Alternate carriage adapter from shared parametric rules."""
    bm_body = refs["bm_body"]
    rear_y, front_y = detect_backplate_y_planes(bm_body)

    x_fil = cfg["x_fil"]
    x_mot = x_fil + 6.335
    z_mount = cfg["z_mount"]
    z_mot = z_mount + 19.300
    mot_hole_r = cfg["mot_hole_r"]
    relocate_fan = cfg["relocate_fan"]

    work = bm_body.copy()
    # Heal upstream BambuMod STEP 0.0002 mm micro-slit at (-27.2, 27.1..30.1, Z=30.8928) so BRep
    # tessellates to a strictly 2-manifold watertight solid with zero non-manifold pinch edges.
    work = work.fuse(box(-28.10, -27.15, 27.05, 30.119, 30.80, 31.05))

    # 1. Remove stock interior upright extruder mount, funnel, and stock hotend M3 block
    cuts = [
        box(-27.8, 14.3, front_y - 0.1, 27.8, 23.6, 59.8),
        box(-14.0, 14.3, front_y - 0.1, 27.8, 59.5, 69.5),
        # Full Bambu X1C heatsink & top neck clearance at final X_fil
        box(x_fil - 8.4, x_fil + 8.4, -3.2, 23.6, 4.8, 25.22),
        box(x_fil - 6.6, x_fil + 6.6, 8.28, 26.5, 24.8, 31.10),
    ]

    if cfg["name"] == "Primary":
        # Open -X right side wall cleanly above plate level (past inner -26.89 corner chamfer)
        # from front_y+0.05 up to Z=59.0 (preserving the top 45-deg overhanging rail bevel above 59.0)
        cuts.append(box(-31.5, -26.70, front_y + 0.05, 32.5, z_mount - 0.02, 59.00))
        cuts.append(box(-31.5, -26.70, -2.0, 32.5, 58.90, 64.00))
        # Trim inner +X fan baffle above plate top where Orbiter Hub's +X wing sits (preserving
        # front/rear 3010 fan corner screw bosses at Y=-0.63 and Y=23.37)
        cuts.append(box(14.0, 19.3, 2.2, 25.2, z_mount - 0.02, 45.0).cut(
            cyl_x(3.0, 23.37, 34.25, 13.5, 20.0)
        ))
        # Clear stock 3010 fan pocket with +0.10 mm clearance so both 0.30 mm3 corner chamfers
        # and bm_body's tangent X=19.50 STEP seam are replaced by crisp clean pocket walls
        cuts.append(box(19.40, 30.5, -3.72, 26.46, 7.16, 37.35))
    else:
        # Remove stock +X 3010 fan frame & overlap ribbon cleanly (X=13.8..30.5, Z=5.2..40.5)
        cuts.append(box(13.8, 30.5, front_y + 0.05, 26.8, 5.2, 40.5))
        # Open +X upper wall cleanly past inner +26.89 corner chamfer where Orbiter Hub flares out
        cuts.append(box(26.70, 31.5, 0.0, 32.5, z_mount - 0.02, 64.0))
        # Notch -X right wall top edge cleanly for Tensioner thumbwheel
        cuts.append(box(-31.5, -27.4, 8.5, 22.8, 55.6, 64.0))

    for c in cuts:
        work = work.cut(c)

    # 2. Plug unused old stock (0, 40) extruder cutouts in backplate without touching belt channels
    # (Z<=20.2, Z>=64.8) or upper carriage/oval/cable slots (Z>=58.6 outside |X|>19.5).
    # Note: slight 0.05..0.15 mm interior overlap into solid walls avoids coplanar OCCT slivers;
    # spare existing mid_R (-21.5, 51.0) bore so we never coaxially plug and re-cut its face.
    adds = [
        box(-27.8, 27.8, rear_y, front_y, 20.6, 58.6).cut(
            cyl_y(2.50, -21.5, 51.0, rear_y - 1.0, front_y + 1.0)
        ),
        box(-12.5, 19.5, rear_y, front_y, 58.4, 64.2),
    ]

    if cfg["name"] == "Primary":
        # Shift the +X lower wing floor edge symmetrically with X_fil=-6.335
        adds.append(box(x_fil + 9.2, 9.2, -3.5, 23.6, 5.55, 7.45))

    # 3. Horizontal Orbiter v2.5 Mounting Plate (XY plane at Z = z_mount - 0.02 to eliminate exact
    # coplanar boolean contact kiss while preserving flush physical mating)
    plate_top = z_mount - 0.02
    plate_bot = z_mount - 5.80
    neck_ceil_z = 31.02 if cfg["name"] == "Primary" else 30.88
    px_min = x_fil - 22.50
    px_max = x_fil + 24.50 if cfg["name"] == "Primary" else x_fil + 22.80

    # Slightly embed rear edge at front_y - 0.15 so fuse into backplate has zero coplanar boundary
    adds.append(box(px_min, px_max, front_y - 0.15, 25.0, neck_ceil_z, plate_top))
    adds.append(box(px_min, x_fil - 6.60, front_y - 0.15, 25.0, plate_bot, neck_ceil_z + 0.08))
    adds.append(box(x_fil + 6.60, px_max, front_y - 0.15, 25.0, plate_bot, neck_ceil_z + 0.08))

    # Rear X1C Hotend Mounting Block (behind X1C neck Y=8.26, above top heatsink fin Z=25.00)
    adds.append(box(x_fil - 7.0, x_fil + 7.0, front_y - 0.15, 8.26, 25.25, neck_ceil_z + 0.08))

    # Print-friendly 45-deg triangular vertical gussets under left & right Orbiter mount wings
    for gx0, gx1 in [(x_fil - 21.5, x_fil - 9.0), (x_fil + 9.0, min(px_max - 0.5, x_fil + 22.0))]:
        if gx1 - gx0 > 3.0:
            gw = Part.makePolygon([
                Vector(gx0, front_y - 0.15, plate_bot - 6.5),
                Vector(gx0, front_y - 0.15, plate_bot + 0.08),
                Vector(gx0, front_y + 12.0, plate_bot + 0.08),
                Vector(gx0, front_y - 0.15, plate_bot - 6.5),
            ])
            adds.append(Part.Face(gw).extrude(Vector(gx1 - gx0, 0, 0)))

    # 4. Relocated 3010 Fan Pod for Alternate (X=[23.0, 33.0], Y=[-3.63, 26.37], Z=[1.75, 31.75])
    fan_reloc = None
    if relocate_fan:
        fx0, fx1 = 23.00, 33.00
        fy0, fy1 = -3.63, 26.37
        fz0, fz1 = 1.75, 31.75
        fan_reloc = (fx0, fx1, fy0, fy1, fz0, fz1)

        adds.append(box(17.5, fx1 + 0.5, front_y - 0.15, fy1 + 1.2, 0.85, fz1 + 0.15))
        # 45-deg support-free transition under the +3.5 mm outboard pod edge along backplate
        flare_wire = Part.makePolygon([
            Vector(29.7, front_y - 3.6, 0.85),
            Vector(fx1 + 0.5, front_y - 0.05, 0.85),
            Vector(29.7, front_y - 0.05, 0.85),
            Vector(29.7, front_y - 3.6, 0.85),
        ])
        adds.append(Part.Face(flare_wire).extrude(Vector(0, 0, fz1 - 0.70)))
        adds.append(box(28.0, 30.0, front_y - 0.15, 0.25, fz1 - 0.5, 58.85))

    for a in adds:
        work = work.fuse(a)

    # 5. Cut ONLY new/modified features cleanly (never re-cutting untouched coaxial existing holes)
    final_cuts = []

    # In Alternate, trim (+24.0, 61.0) ONLY inside Y=[-7.0..4.2] where motor_front flange passes,
    # keeping rear steel-carriage flange (Y=-11.12..-7.0) 100% closed; reduce (+24,61) screw bore
    # gently only if needed (stock r=2.15 has 0.0 mm3 clash with motor barrel if trimmed at r=1.65?
    # Note: stock bm_body already has r=2.15 at (24,61); physical M3 shaft r=1.55 has 0.000 mm3 clash).

    # 5a. Re-oriented Orbiter v2.5 Motor Cutout
    # Through-bore across backplate:
    final_cuts.append(cyl_y(mot_hole_r, x_mot, z_mot, rear_y - 1.0, 4.2))
    # Front-of-backplate step for motor_front (Solid[37]) front shoulder collar (Y=-7.0..+4.2)
    # Spares a 3.0 mm protective rim around mid_R (-21.5, 51.0) so its M4/M3 hole keeps closed wall
    collar_cut = cyl_y(21.45, x_mot, z_mot, -7.00, 4.2).common(
        box(-40, 40, -8.0, 5.0, 32.0, 66.20)
    )
    if cfg["name"] == "Primary":
        collar_cut = collar_cut.cut(cyl_y(3.00, -21.5, 51.0, -7.5, 5.0))
    final_cuts.append(collar_cut)

    # +-30 deg Slanted Motor Mounting Ears (Y=[-8.20, +4.2], leaving 2.92 mm rear carriage flange)
    ear_dx = 21.90 * math.cos(math.radians(30.0))
    ear_dz = 21.90 * math.sin(math.radians(30.0))
    ur_x, ur_z = x_mot - ear_dx, z_mot + ear_dz
    ll_x, ll_z = x_mot + ear_dx, z_mot - ear_dz
    ear_y0 = -8.20
    final_cuts.append(stadium_xz_y(x_mot, z_mot, ur_x, ur_z, 4.10, ear_y0, 4.2))
    final_cuts.append(stadium_xz_y(x_mot, z_mot, ll_x, ll_z, 4.10, ear_y0, 4.2))

    # 7:30 o'clock JST-PH Motor Connector & Pigtail Pass-Through Notch (through full backplate)
    jst_x, jst_z = x_mot - 10.74, z_mot - 15.50
    final_cuts.append(stadium_xz_y(x_mot, z_mot, jst_x, jst_z, 4.80, rear_y - 1.0, 4.2))

    # 5b. Front-of-backplate Orbiter Gearset Housing Pocket (Y=[-5.00, +4.2], strictly <= Z=65.5
    # on full R=23.1 dome + narrow upper filament tower so Z=66..74 oval slot is never torn)
    final_cuts.append(cyl_y(23.1, x_mot, z_mot, -5.00, 4.2).common(
        box(-35.0, 35.0, -6.0, 5.0, 32.0, 65.4)
    ))
    final_cuts.append(box(x_fil - 11.2, x_fil + 11.2, -5.00, 4.2, 65.0, 70.3))
    final_cuts.append(box(x_mot - 23.0, x_mot + 23.0, -5.00, 4.2, z_mount + 0.8, z_mount + 15.0))

    # 5c. Horizontal Orbiter Plate Bores
    # Central 4 mm OD PTFE / filament pass-through
    final_cuts.append(cyl_z(2.15, x_fil, 12.08, neck_ceil_z - 0.5, z_mount + 0.5))
    # Two M3x4x5 heatset insert bores (r = 2.10 mm)
    for mx in (x_fil - 17.500, x_fil + 19.500):
        z_bot = plate_bot - 0.5 if not (relocate_fan and mx > 15.0) else 27.0
        final_cuts.append(cyl_z(2.10, mx, 12.076, z_bot, z_mount + 0.5))

    # 5d. Bambu X1C Hotend M3 Mounts: front M3x4x5 heatset pockets + clean M3 pass-through to rear
    for hx_rel in (-3.440, 3.410):
        hx_abs = x_fil + hx_rel
        # Front heatset insert pocket (Y = +3.0..8.30, r = 2.05) + rear pass-through (r = 1.75)
        final_cuts.append(cyl_y(2.05, hx_abs, 27.22, 3.00, 8.80))
        final_cuts.append(cyl_y(1.75, hx_abs, 27.22, rear_y - 1.0, 8.80))

    # 5e. Alternate Relocated 3010 Fan Cutouts + (+19.0, 3.5) Front Wrench Access
    if fan_reloc is not None:
        fx0, fx1, fy0, fy1, fz0, fz1 = fan_reloc
        final_cuts.append(box(fx0, fx1 + 1.0, fy0 - 0.2, fy1 + 0.2, fz0 - 0.2, fz1 + 0.2))
        fc_y = 0.5 * (fy0 + fy1)  # 11.37
        fc_z = 0.5 * (fz0 + fz1)  # 16.75
        air_cyl = cyl_x(14.50, fc_y, fc_z, 16.5, fx0 + 0.2)
        air_cap = box(16.5, fx0 + 0.2, fy0 - 1.0, fy1 + 1.0, 2.0, 27.20)
        final_cuts.append(air_cyl.common(air_cap))
        for sy in (fc_y - 12.0, fc_y + 12.0):
            for sz in (fc_z - 12.0, fc_z + 12.0):
                final_cuts.append(cyl_x(1.55, sy, sz, 16.5, fx0 + 0.5))
        # Straight-in front wrench/head corridor for lower-left carriage bolt (+19.0, 3.5)
        final_cuts.append(cyl_y(1.80, 19.0, 3.5, front_y - 0.25, front_y + 0.05))
        final_cuts.append(cyl_y(3.30, 19.0, 3.5, front_y - 0.01, 31.0))

    for c in final_cuts:
        work = work.cut(c)

    try:
        cleaned = work.removeSplitter()
        if cleaned.isValid() and len(cleaned.Solids) == 1 and cleaned.Volume > work.Volume * 0.99:
            work = cleaned
    except Exception:
        pass
    if not work.isValid():
        work.fix(1e-6, 1e-6, 1e-6)
    assert work.isValid() and len(work.Solids) == 1, f"{cfg['name']} BRep validity check failed!"

    metrics = verify_variant(refs, work, cfg, fan_reloc)
    return work, metrics


def verify_variant(refs: dict, adapter: Part.Shape, cfg: dict, fan_reloc) -> dict:
    bm_body = refs["bm_body"]
    x_fil = cfg["x_fil"]
    z_mount = cfg["z_mount"]
    x_mot = x_fil + 6.335
    z_mot = z_mount + 19.300

    he_t = refs["he_raw"].copy()
    he_t.translate(Vector(x_fil, 0, 0))
    ov_he = adapter.common(he_t).Volume

    ov_orb = 0.0
    ov_orb_details = {}
    for idx, s in enumerate(refs["orb_body_solids"]):
        ts = orbiter_xform(s, x_fil, z_mount)
        if ts.BoundBox.intersect(adapter.BoundBox):
            c = ts.common(adapter)
            if not c.isNull() and c.Volume > 1e-4:
                ov_orb += c.Volume
                ov_orb_details[f"solid_{idx}"] = round(c.Volume, 4)

    ov_ebb = adapter.common(refs["ebb_bkt"]).Volume
    orb_zmax = max(orbiter_xform(s, x_fil, z_mount).BoundBox.ZMax for s in refs["orb_body_solids"])

    if fan_reloc is not None:
        fx0, fx1, fy0, fy1, fz0, fz1 = fan_reloc
        fan_box = box(fx0, fx1, fy0, fy1, fz0, fz1)
    else:
        fan_box = box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)

    ov_fan_adapter = adapter.common(fan_box).Volume
    ov_fan_orb = 0.0
    for s in refs["orb_body_solids"]:
        ts = orbiter_xform(s, x_fil, z_mount)
        if ts.BoundBox.intersect(fan_box.BoundBox):
            c = ts.common(fan_box)
            if not c.isNull():
                ov_fan_orb += c.Volume

    steel_carriage = box(-40.0, 40.0, -30.0, -11.12, -20.0, 95.0)
    ov_carriage = adapter.common(steel_carriage).Volume

    # Measure ONLY *new* intrusion into belt groove cavities compared to unmodified bm_body
    belt_low = box(-27.0, 27.0, -11.11, -9.20, 10.6, 19.4)
    belt_high = box(-27.0, 27.0, -11.11, -9.20, 66.6, 74.4)
    ov_belt_low_new = max(0.0, adapter.common(belt_low).Volume - bm_body.common(belt_low).Volume)
    ov_belt_high_new = max(0.0, adapter.common(belt_high).Volume - bm_body.common(belt_high).Volume)

    # Check both M3 carriage bolt shaft clearances (r=1.55) AND full clearance against 36STH20
    screw_checks = {}
    for lbl, sx, sz in [
        ("low_R", -19.0, 3.5), ("low_L", 19.0, 3.5),
        ("up_R", -24.0, 61.0), ("up_L", 24.0, 61.0),
    ]:
        bore = cyl_y(1.55, sx, sz, -12.0, -3.5)
        screw_checks[lbl] = round(adapter.common(bore).Volume, 4)

    bb = adapter.BoundBox
    return {
        "name": cfg["name"],
        "is_valid_brep": bool(adapter.isValid()),
        "solid_count": len(adapter.Solids),
        "volume_mm3": round(float(adapter.Volume), 2),
        "bbox_upright_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
        "datums_mm": {
            "x_fil_nozzle": round(x_fil, 3),
            "x_mot_center": round(x_mot, 3),
            "z_mount_plate": round(z_mount, 3),
            "z_mot_center": round(z_mot, 3),
            "x1c_neck_to_plate_clearance": round(z_mount - 30.720, 3),
            "orbiter_latch_zmax": round(orb_zmax, 3),
            "latch_to_ebb42_r7_clearance": round(80.1515 - orb_zmax, 3),
        },
        "collisions_mm3": {
            "adapter_vs_x1c_hotend": round(ov_he, 5),
            "adapter_vs_orbiter_v25": round(ov_orb, 5),
            "adapter_vs_orbiter_breakdown": ov_orb_details,
            "adapter_vs_ebb42_r7": round(ov_ebb, 5),
            "adapter_vs_3010_fan": round(ov_fan_adapter, 5),
            "orbiter_vs_3010_fan": round(ov_fan_orb, 5),
            "adapter_vs_steel_carriage_plane": round(ov_carriage, 5),
            "new_intrusion_lower_belt_channel": round(ov_belt_low_new, 5),
            "new_intrusion_upper_belt_channel": round(ov_belt_high_new, 5),
        },
        "carriage_m3_shaft_obstruction_mm3": screw_checks,
    }


def export_stl_print_orientation(shape: Part.Shape, out_stl: Path) -> dict:
    """Rotate upright CAD (+Z up, rear @ Y=-11.117) into flat backplate print pose on Z_stl=0."""
    pr = shape.copy()
    pr.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 90)
    pr.translate(Vector(0, 0, -pr.BoundBox.ZMin))

    mesh = MeshPart.meshFromShape(Shape=pr, LinearDeflection=0.035, AngularDeflection=0.14, Relative=False)
    mesh.removeDuplicatedPoints()
    mesh.removeDuplicatedFacets()
    mesh.fixIndices()
    mesh.harmonizeNormals()
    if not mesh.isSolid():
        mesh.fillupHoles(200)
        mesh.harmonizeNormals()
    mesh.write(str(out_stl))
    m_check = Mesh.Mesh(str(out_stl))
    assert m_check.isSolid() and not m_check.hasNonManifolds(), (
        f"{out_stl.name} is not a closed 2-manifold solid mesh "
        f"(isSolid={m_check.isSolid()}, hasNonManifolds={m_check.hasNonManifolds()})"
    )
    bb = m_check.BoundBox
    return {
        "stl_path": str(out_stl.relative_to(REPO)),
        "facets": int(m_check.CountFacets),
        "is_solid": bool(m_check.isSolid()),
        "has_non_manifolds": bool(m_check.hasNonManifolds()),
        "volume_mm3": round(float(m_check.Volume), 2),
        "print_bbox_mm": {
            "x": [round(bb.XMin, 3), round(bb.XMax, 3)],
            "y": [round(bb.YMin, 3), round(bb.YMax, 3)],
            "z": [round(bb.ZMin, 3), round(bb.ZMax, 3)],
        },
    }


def export_preview_meshes(shape: Part.Shape, refs: dict, cfg: dict, out_json: Path, fan_box: Part.Shape) -> None:
    """Tessellate assembly meshes for fast standalone headless rendering."""
    x_fil = cfg["x_fil"]
    z_mount = cfg["z_mount"]
    he_t = refs["he_raw"].copy()
    he_t.translate(Vector(x_fil, 0, 0))
    orb_comp = Part.makeCompound([orbiter_xform(s, x_fil, z_mount) for s in refs["orb_body_solids"]])
    bolt_comp = Part.makeCompound([orbiter_xform(s, x_fil, z_mount) for s in refs["orb_bolts"]])

    entries = [
        ("adapter", shape, [145, 168, 190], 0.25),
        ("x1c_hotend", he_t, [212, 162, 62], 0.35),
        ("orbiter", orb_comp, [48, 56, 68], 0.75),
        ("orbiter_bolts", bolt_comp, [195, 198, 205], 0.50),
        ("ebb42_r7", refs["ebb_bkt"], [235, 145, 42], 0.30),
        ("fan_3010", fan_box, [52, 168, 212], 0.50),
    ]
    payload = []
    for name, sh, col, dev in entries:
        v, f = sh.tessellate(dev)
        payload.append({
            "name": name,
            "color": col,
            "v": [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in v],
            "f": [list(tri) for tri in f],
        })
    out_json.write_text(json.dumps(payload), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading reference STEPs...", flush=True)
    refs = load_references()

    configs = [
        {
            "name": "Primary",
            "stem": "BambuMod_Orbiter25_Primary_R1",
            "x_fil": -6.335,
            "z_mount": 32.600,
            "mot_hole_r": 18.60,
            "relocate_fan": False,
        },
        {
            "name": "Alternate",
            "stem": "BambuMod_Orbiter25_Alt_ShiftedMotor_R1",
            "x_fil": 0.000,
            "z_mount": 32.000,
            "mot_hole_r": 18.50,
            "relocate_fan": True,
        },
    ]

    results = {}
    built_shapes = {}
    for cfg in configs:
        print(f"Building {cfg['name']} ({cfg['stem']})...", flush=True)
        solid, metrics = build_variant(refs, cfg)
        built_shapes[cfg["name"]] = solid

        step_path = OUT_DIR / f"{cfg['stem']}.step"
        stl_path = OUT_DIR / f"{cfg['stem']}.stl"
        solid.exportStep(str(step_path))
        step_read = Part.read(str(step_path))
        assert step_read.isValid() and len(step_read.Solids) == 1, f"{step_path.name} STEP readback failed!"
        stl_metrics = export_stl_print_orientation(solid, stl_path)
        metrics["stl"] = stl_metrics
        metrics["step_path"] = str(step_path.relative_to(REPO))

        fan_box = (
            box(23.00, 33.00, -3.63, 26.37, 1.75, 31.75)
            if cfg["relocate_fan"]
            else box(19.50, 29.50, -3.63, 26.37, 7.25, 37.25)
        )
        export_preview_meshes(
            solid, refs, cfg, OUT_DIR / f"preview_{cfg['name'].lower()}.json", fan_box
        )
        results[cfg["name"]] = metrics
        print(
            f"  Valid={metrics['is_valid_brep']} Solids={metrics['solid_count']} "
            f"Vol={metrics['volume_mm3']} | STL solid={stl_metrics['is_solid']} "
            f"nonman={stl_metrics['has_non_manifolds']} | Overlaps={metrics['collisions_mm3']}",
            flush=True,
        )

    fcstd_path = OUT_DIR / "BambuMod_Orbiter25_Remix_R1.FCStd"
    doc = App.newDocument("BambuMod_Orbiter25_Remix_R1")
    for cfg in configs:
        obj = doc.addObject("Part::Feature", cfg["stem"])
        obj.Shape = built_shapes[cfg["name"]]
        if cfg["name"] == "Alternate":
            obj.Placement.Base = Vector(90.0, 0.0, 0.0)
    he_p = refs["he_raw"].copy()
    he_p.translate(Vector(-6.335, 0, 0))
    for lbl, sh in [
        ("Ref_Primary_X1C_Hotend", he_p),
        ("Ref_Primary_Orbiter_v25", Part.makeCompound([orbiter_xform(s, -6.335, 32.600) for s in refs["orb_body_solids"]])),
        ("Ref_EBB42_ShortBridge_R7", refs["ebb_bkt"]),
        ("Ref_Stock_BambuMod_VentCover", refs["bm_cover"]),
    ]:
        o = doc.addObject("Part::Feature", lbl)
        o.Shape = sh
    doc.recompute()
    doc.saveAs(str(fcstd_path))

    val_path = OUT_DIR / "validation.json"
    val_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved assembly & validation to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
