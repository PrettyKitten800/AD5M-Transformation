# BambuMod x Orbiter v2.5 — `Primary_R7` Print & Fit Guide

## Attribution & License
- **Base AD5M Carriage & Shroud Concept:** Kirill_Wawe BambuMod (`CC BY-NC-SA 4.0`) — see [reference/BambuMod/SOURCE.md](../../reference/BambuMod/SOURCE.md)
- **Extruder Reference:** Orbiter v2.5 (`LDO / Róbert Lőrincz`) — see [reference/Bambu_X1_hotend_CAD/SOURCE.json](../../reference/Bambu_X1_hotend_CAD/SOURCE.json)
- **Revision R7 Builder:** [`scripts/cad/build_bambumod_orbiter25_R7.py`](../../scripts/cad/build_bambumod_orbiter25_R7.py) (derived parametrically from `Primary_R6`, preserving `R1`–`R6` untouched)

---

## What Changed in `Primary_R7` (Final Pre-Print Refinements)

1. **Reinforced Upper Carriage Mount Bosses (`up_R = (-24.0, 61.0)`, `up_L = (+24.0, 61.0)`):**
   - Kept the **`Ø4.30 mm × 5.54 mm`** blind round bores on all 4 carriage mounting holes (`low_R`, `low_L`, `up_R`, `up_L`, `0.0 mm³` bore obstruction) for heat-set inserts / carriage fasteners, with zero front passthrough openings.
   - Reinforced both upper bosses to **`R = 3.60 mm`**:
     - `up_L (+24.0, 61.0)`: full `360°` **`1.40 mm`** minimum radial wall across the full plate depth (`Y = -11.12..-3.88 mm`).
     - `up_R (-24.0, 61.0)`: full `360°` **`1.40 mm`** minimum radial wall across the rear **`4.22 mm` heat-set insert zone** (`Y = -11.12..-6.90 mm`, `0.224 mm` axial clearance behind the Orbiter stepper flange ear), plus **`1.30 mm`** minimum radial wall along the non-motor `280°` arc forward to `Y = -4.45 mm` while preserving the existing `0.043 mm` NEMA flange ear clearance at `+22.6°` (`0.0 mm³` motor collision).

2. **Matched `Ø3.60 mm` Orbiter Extruder Mount Holes (`Y = 12.08 mm, Z_mount = 32.60 mm`):**
   - Resized the right (`-X = -23.85 mm`) blind bore cleanly from `Ø4.40 mm` down to **`Ø3.60 mm`** (`r = 1.800 mm`, `4.30 mm` blind depth to `Z = 28.28 mm`, leaving `>= 2.0 mm` solid roof above the `-X` exhaust duct), matching the left (`+X = +13.15 mm`) **`Ø3.60 mm`** through-bore down to the perpendicular **`Z_nut_face = 27.60 mm`** M3 nut boss.
   - Verified `1.00` (`100%`) solid circumferential wall rings around both bores at `r = 1.95 mm`.

3. **Rounded Exterior Edges & Top Carriage Anti-Warp Bed Corners:**
   - Top carriage XZ ears `(±30.0, Z = 80.002 mm)`: **`R_bed = 3.50 mm`** rounded anti-warp corner on the `Y = -11.117 mm` PEI bed face, tapering at `<= 40°` (self-supporting without supports) over `Y = -11.12..-9.55 mm` down to **`R_front = 0.85 mm`** (`Y = -9.55..-1.80 mm`). Both outer `(±27.0, -7.50)` EBB42 mounting bores remain fully intact with **`>= 0.82 mm`** upper radial wall (`0.87 mm` exact at `Z = 79.6`), and Kirill's `Z = 74.0 mm` rear belt-slot wall (`0.65 mm`) is unchanged from `R6`.
   - Exterior vertical corners: rear carriage edges `R = 1.60 mm` (`Z = 0..81 mm`), front shroud corners `R = 1.80 mm` (`Z = 5..38 mm`), backplate front edges `R = 0.75 mm` (`Z = z_step..73.495 mm`), top wire tabs `R = 0.65 mm` (`Z = 73.505..81.0 mm`), top front edge `R = 0.80 mm` (`Z = 80.002 mm`), swept `R = 1.00 mm` top rims along the `-X` Orbiter shelf and `+X` `3010` fan shroud, and `R = 1.50 mm` inner portal arch fillets (`Z = 67.0 mm`).

4. **True Flat-Backplate Print Orientation (`Z_bed = 0.000 mm`):**
   - Fixed the STL export orientation bug present in `R4`–`R6` (`rotate(+90° about +X)` + vertex-bounds alignment) so the `60 × 80 mm` carriage rear face rests directly on the PEI bed with **`1,952.65 mm²`** of flat bed contact at `Z = 0.000 mm` (zero `0.05 mm` OCC BRep slack lift).

---

## Verified Metrics (`validation.json` + `trimesh`)

| Check / Property | Measured Result |
|---|---|
| STEP Validity / Solids | `step_valid = true`, `step_solids = 1` |
| STEP / STL Volume | `38,375.68 mm³` (STEP, `-90.19 mm³` vs `R6`) / `38,350.37 mm³` (FreeCAD STL) / `38,350.16 mm³` (`trimesh`) |
| STL Integrity | `46,810` facets, `is_solid = true`, `has_non_manifolds = false`, `watertight = true`, `1` shell, rel diff `0.000659` |
| Print-Bed Bounding Box | `X = [-29.998, 30.000]`, `Y = [0.000, 80.002]`, `Z = [0.000, 43.236]` mm |
| Flat PEI Bed Contact (`Z = 0`) | **`1,952.65 mm²`** |
| Elevated Overhangs (`>45°` / `>70°`) | `2,633.43 mm²` / `1,867.87 mm²` (smooth duct roof, `+X` fan bridge & shelf lip) |
| All 9 Assembly Collisions | **`0.0 mm³`** (`adapter` vs Orbiter+motor, M3 bolts, X1C hotend, 3010 fan, EBB42 short bridge, steel carriage, low/high belts; and fan vs Orbiter) |
| 4× EBB42 Top Bores (`±27`, `±18`, `Y=-7.5`) | `0.0 mm³` obstructed; upper `±27` outer radial wall `>= 0.82 mm` (`0.65 mm` belt wall at `Z=74` unchanged) |
| 2× Hotend Rear Hex Pockets (`-9.76`, `-2.91`, `Z=27.22`) | `0.0 mm³` M3 bore obstruction; twin chamfered M3 hex pockets (`5.50 mm` AF) preserved |

---

## Slicing, Printing & Assembly Notes

- **Drop straight into slicer:** Open `BambuMod_Orbiter25_Primary_R7.stl` as-is — the flat carriage backplate (`1,952.65 mm²`) is already oriented down on `Z = 0.000 mm` with rounded `R = 3.50 mm` top ear corners to reduce PEI corner lift.
- **Recommended Material & Settings:** ABS, ASA, or PC-CF (`4–5` perimeters, `25–40%` gyroid infill, `0.20 mm` layer height).
- **Supports:** Use organic/tree supports from the build plate **only** for elevated exterior shelf/fan-bridge overhangs (`+X` 3010 fan bay roof and `-X` Orbiter shelf overhang). Add support blockers inside the smooth internal airflow tunnel, rear M3 hex pockets, `Ø4.30 mm` carriage bores, and top EBB42 bores.
- **Hardware Checklist:**
  - **Carriage (`4×`):** `4×` M3×4mm heat-set inserts (`Ø4.30 × 5.54 mm` blind rear bores at `(±19.0, 3.5)` and `(±24.0, 61.0)`), installed from the rear face (`-Y`), fastened from behind Kirill's carriage frame.
  - **Bambu X1C Hotend (`2×`):** `2×` M3 hex nuts (`5.5 mm` AF) pressed into the rear chamfered hex pockets at `(-9.76, 27.22)` and `(-2.91, 27.22)`, fastened with `2×` M3 screws through the hotend heatsink.
  - **Orbiter v2.5 Extruder (`2×`):** Matched `Ø3.60 mm` mounts at `X = +13.15 mm` (M3×10–12mm screw through to an M3 nut seated flat on the perpendicular `Z = 27.60 mm` boss) and `X = -23.85 mm` (`4.30 mm` blind `Ø3.60 mm` bore — thread an M3 self-tapping screw or short M3×6mm bolt up to `<= 4.0 mm` thread engagement).
  - **3010 Heatsink Fan & `EBB42_short_bridge_R7`:** `3010` axial fan mounted in the `+X` bay (`X = 19.50..29.50 mm`); EBB42 short-bridge bracket mounted to the top `X = ±27.0, ±18.0 mm` heat-set bores.

---

## Verification Visuals

- [Primary_R7_part_views.png](./Primary_R7_part_views.png)
- [Primary_R7_assembly_views.png](./Primary_R7_assembly_views.png)
- [Primary_R7_duct_cutaways.png](./Primary_R7_duct_cutaways.png)
- [Primary_R7_r7_checks.png](./Primary_R7_r7_checks.png)
