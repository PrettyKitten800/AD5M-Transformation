# BambuMod × Orbiter v2.5 AD5M Carriage Adapter Remix (R1) — Print & Fit Guide

This directory contains two complete, CAD-verified carriage-adapter remixes built from [Kirill_Wawe's BambuMod (`bambumod_remix_and_vent_cover.step`)](https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m) and [dr. Lorincz Robert's Orbiter v2.5 STEP (`Orbiter v2.0 mockup.step` + LDO-36STH20 `3 mm` rear tail)](https://www.orbiterprojects.com/orbiter-v2-5/) using [`scripts/cad/build_bambumod_orbiter25_R1.py`](../../scripts/cad/build_bambumod_orbiter25_R1.py) and [`scripts/cad/render_bambumod_orbiter25_R1.py`](../../scripts/cad/render_bambumod_orbiter25_R1.py).

Both adapters replace the stock perpendicular AD5M feeder cutout with:
1. Re-oriented backplate motor cutout for Orbiter v2.5's **±30° slanted mounting ears** and **7:30 o'clock JST-PH motor connector/pigtail** relief.
2. **Horizontal (`XY`) Orbiter v2.5 mounting plate** aligned parallel to the buildplate above the Bambu X1C heatsink neck.
3. Bambu X1C heatsink/neck pocket + M3 clamping mounts (`M3×4×5` front heatset inserts + rear pass-throughs) positioned relative to the filament path.

---

## 1. Variant Comparison (Primary vs. Alternate)

| Metric | Primary (`BambuMod_Orbiter25_Primary_R1`) | Alternate (`BambuMod_Orbiter25_Alt_ShiftedMotor_R1`) |
| --- | --- | --- |
| **Motor Center (`X_mot, Z_mot`)** | **Centered:** `X = 0.000`, `Z = 51.900 mm` | **Shifted Left (+X):** `X = +6.335`, `Z = 51.300 mm` |
| **Nozzle / Hotend `X_fil`** | **Shifted Right (-X):** `X = -6.335 mm` (closer to right-side Eddy mount) | **Stock:** `X = 0.000 mm` |
| **Orbiter Plate `Z_mount`** | `32.600 mm` | `32.000 mm` |
| **X1C Neck-to-Plate Gap** | `1.880 mm` (`Z = 30.720` to `32.600`) | `1.280 mm` (`Z = 30.720` to `32.000`) |
| **Orbiter Latch `ZMax` / EBB42 `R7` Gap** | `79.818 mm` / `0.334 mm` below `Z = 80.1515` | `79.218 mm` / `0.934 mm` below `Z = 80.1515` |
| **`3010` Heatsink Fan** | **Stock location untouched** (`X = [19.50, 29.50], Z = [7.25, 37.25]`) | **Relocated** (`X = [23.00, 33.00], Z = [1.75, 31.75]`, `-5.5 mm` down, `+3.5 mm` outboard) |
| **Upright Bounding Box (`X × Y × Z`)** | `[-29.998, 30.000] × [-11.117, 32.119] × [0.000, 80.002]` mm | `[-29.998, 33.500] × [-11.117, 32.119] × [0.000, 80.002]` mm |
| **Tensioner Thumbwheel (`XMin`)** | Overhangs right side at `X = -36.526 mm` (`-6.53 mm` past body) | Nearly flush at `X = -30.191 mm` (`-0.19 mm` past body) |
| **STL Print Volume / Facets** | `37,734.46 mm³` / `20,504` facets (watertight, 1 shell) | `36,941.32 mm³` / `14,852` facets (watertight, 1 shell) |
| **All CAD Reference Collisions** | `0.0 mm³` (X1C, Orbiter+`36STH20`, EBB42 `R7`, `3010` fan, steel plane, belt channels, all 4 M3 shafts) | `0.0 mm³` (X1C, Orbiter+`36STH20`, EBB42 `R7`, `3010` fan, steel plane, belt channels, all 4 M3 shafts) |

---

## 2. Files Included

- [`BambuMod_Orbiter25_Primary_R1.stl`](BambuMod_Orbiter25_Primary_R1.stl) / [`BambuMod_Orbiter25_Primary_R1.step`](BambuMod_Orbiter25_Primary_R1.step) — Centered motor, hotend `-6.335 mm` right (`-X`).
- [`BambuMod_Orbiter25_Alt_ShiftedMotor_R1.stl`](BambuMod_Orbiter25_Alt_ShiftedMotor_R1.stl) / [`BambuMod_Orbiter25_Alt_ShiftedMotor_R1.step`](BambuMod_Orbiter25_Alt_ShiftedMotor_R1.step) — Stock nozzle `X = 0.000`, shifted motor `+6.335 mm` left (`+X`), relocated `3010` fan pod.
- [`BambuMod_Orbiter25_Remix_R1.FCStd`](BambuMod_Orbiter25_Remix_R1.FCStd) — Combined FreeCAD inspection assembly with X1C hotend, Orbiter v2.5, `EBB42_short_bridge_R7`, and stock BambuMod vent cover references.
- [`validation.json`](validation.json) — Machine-generated BRep validity, collision matrix, bolt-shaft clearance, and print STL metrics.
- Previews: [`Primary_part_views.png`](Primary_part_views.png), [`Primary_assembly_views.png`](Primary_assembly_views.png), [`Alternate_part_views.png`](Alternate_part_views.png), [`Alternate_assembly_views.png`](Alternate_assembly_views.png).

---

## 3. Print Orientation & Recommended Slicer Settings

Both STLs are exported **flat on the rear steel-carriage mating face (`Z_stl = 0.000 mm`)**:
- **Material:** ABS, ASA, PC-CF, or PA-CF (PETG acceptable for dry-fit only if chamber stays cool; backplate/motor pocket sit near heated bed & stepper motor).
- **Orientation:** As exported (rear steel-carriage face down on `Z = 0`, `3010` & Orbiter openings facing upward).
- **Supports:** **OFF.** All overhangs (including Alternate's `45°` backplate pod flare and under-shelf gussets) are chamfered for support-free printing.
- **Walls / Infill:** `4` perimeters (`~1.6 mm`), `5` top/bottom layers, `25–40%` gyroid or cubic infill, `0.20 mm` layer height (`0.40 mm` nozzle).
- **Bed footprint check:** `Primary` fits within `60.0 × 80.0 × 43.24 mm`; `Alternate` fits within `63.5 × 80.0 × 43.24 mm`.

---

## 4. Hardware BOM & Assembly Sequence

1. **Heatset Inserts (4× total):**
   - Install **2× M3×4×5 mm (Ø4.2 mm bores)** downward into the top of the horizontal Orbiter mounting shelf at `(X_fil - 17.500, 12.076)` and `(X_fil + 19.500, 12.076)`.
   - Install **2× M3×4×5 mm (Ø4.1 mm front bores)** into the Bambu X1C hotend mounting block (`Z = 27.22`, `Y = 3.0..8.80 mm`). Note: rear pass-through holes (`Ø3.5 mm`) stay open to the backplate in case you also wish to reinforce from behind.
2. **PTFE Filament Guide Stub:**
   - Cut a straight section of **`4 mm OD × 2 mm ID` PTFE** tube (`~14–16 mm` typical; **dry-fit and trim flush** so it seats fully down into the Bambu X1C coldend throat and stops flush with `Z_mount` against the Orbiter v2.5 Hub exit before final tightening).
   - Central PTFE bore in the horizontal shelf is `Ø4.30 mm` (`(X_fil, Y = 12.08)`).
3. **Bolt Backplate to Steel X-Carriage:**
   - Mount the adapter backplate to the AD5M steel carriage **before** bolting on the Orbiter v2.5!
   - Lower bolts `(±19.0, 3.5)`: in **Alternate**, the lower-left `(19.0, 3.5)` bolt uses the dedicated front wrench/socket-head access corridor (`Ø6.6 mm` to `Y = front_y`, stepped cleanly into stock `Ø3.6 mm` rear bore).
   - Upper bolts `(±24.0, 61.0)`: in **Alternate**, `(24.0, 61.0)` opens cleanly into the front motor-collar pocket (`Y = -7.0..4.2`) while keeping the rear steel-carriage flange (`Y = -11.12..-7.0`) closed; verify screw length (`M3×8..10 mm` typical) does not protrude beyond the `LDO-36STH20` front step.
4. **Install Bambu X1C Hotend & PTFE Stub:**
   - Seat X1C heatsink (`0.0 mm³` top-fin interference in both variants) and secure with **2× M3×14–16 mm** socket-head bolts into the front M3 heatset inserts.
5. **Install Orbiter v2.5 + LDO-36STH20-1004AHG:**
   - Feed the motor's JST-PH pigtail through the **7:30 o'clock notch**, seat the motor rear through the slanted pocket, and fasten the Orbiter v2.5 base downward into the two horizontal shelf heatset inserts using **2× M3×10 mm** socket-head cap screws (Orbiter reference screws penetrate `3.69 mm` below `Z_mount`).
6. **Install `3010` Axial Hotend Fan & Stock Part-Cooling Blower/Cover:**
   - Attach the `3010` fan (`M3` corner screws into stock pocket in Primary, or the relocated `+X` fan pod in Alternate). Verify wires route cleanly out of the motor cutout.

---

## 5. Klipper & Slicer Offsets (`Primary` vs. `Alternate`)

- **Primary (`X_fil = -6.335 mm` right):**
  - Nozzle sits **`6.335 mm` to the right (`-X` upright)** relative to the centered motor / carriage origin.
  - Subtract `6.335 mm` from the effective bed probe X offset (`[probe]` / `[probe_eddy_current]` `x_offset`: e.g. if Eddy sits on `-X`, probe-to-nozzle X distance shrinks by `6.335 mm`!), re-measure physical **`[probe_eddy_current]` `x_offset` / `y_offset`**, and verify **`[stepper_x]` `position_min` / `position_max` / `position_endstop`** so the nozzle reaches the full bed without hitting the right/left frame rails.
- **Alternate (`X_fil = 0.000 mm` stock):**
  - Preserves stock BambuMod nozzle `X = 0.000 mm`; bed/nozzle X-offsets remain unchanged, though **you MUST verify physical `-X` / `+X` rail/endstop clearance** because the relocated `3010` fan pod extends to **`X = +33.500 mm`** (`+3.500 mm` wider on `+X` than stock `30.000 mm`).

---

## 6. Verification Scope & Physical Caveats (Untested Physically)

All geometric checks pass in FreeCAD 1.1 OCCT BRep and `trimesh` against the repo's CAD reference solids (`bambumod_remix_and_vent_cover.step`, `Orbiter v2.0 mockup.step` + `3 mm` tail, `Bambu_X1_P1_original_hotend_Jorge.STEP`, `EBB42_short_bridge_R7.step`):
- **Not verified in CAD (must check on printer before homing/printing):**
  1. Rear-of-carriage AD5M gantry beam / linear-rail block / XY belt clamp clearance against the **`15.16 mm` rearward `36STH20` overhang** (`Y = -26.279..-11.117 mm` upright).
  2. Frame / gantry travel limits at X=min / X=max / Y=max against Primary's **`-36.526 mm` tensioner thumbwheel** (`6.53 mm` past body) and Alternate's **`+33.500 mm` relocated `3010` fan pod** (`3.50 mm` past body), plus Alternate's `(+24.0, 61.0)` carriage bolt protrusion inside the front `Y = -7.0..4.2` collar pocket and fan cable routing.
  3. Actual Bambu X1C coldend PTFE seat depth and heatset insert pull-out strength in your chosen print filament.
  4. `Primary` places Orbiter Latch `ZMax = 79.818 mm`, leaving only **`0.334 mm`** nominal vertical clearance under `EBB42_short_bridge_R7` (`Z = 80.1515 mm`) — verify printed EBB42 bracket clearances (`Alternate` has `0.934 mm`) and shim EBB42 spacers if needed.

---

## 7. Attribution & License

Derived geometry preserves upstream attribution and share-alike terms:
- **BambuMod AD5M carriage housing** by **Kirill_Wawe** ([Printables #1574762](https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m)) — **CC BY-NC-SA 4.0**.
- **Orbiter v2.5 Extruder** reference STEP by **dr. Lorincz Robert** ([orbiterprojects.com/orbiter-v2-5/](https://www.orbiterprojects.com/orbiter-v2-5/)) — **CC BY-NC-SA 4.0**.
- All remixed adapter files in `outputs/BambuMod_Orbiter25_Remix_R1/` remain under **CC BY-NC-SA 4.0**.
