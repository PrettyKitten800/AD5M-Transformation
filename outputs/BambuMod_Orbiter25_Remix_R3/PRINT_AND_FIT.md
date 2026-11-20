# BambuMod x Orbiter v2.5 Offset-Hotend Carriage Adapter — Revision 3 (`Primary_R3`)

## Summary of R3 Changes (Built on `Primary_R2`)
1. **Offset-hotend configuration (`X_mot = 0.000 mm`, `Z_mot = 51.900 mm`, `X_fil = -6.335 mm`, `Z_mount = 32.600 mm`):** Retains the centered `-30°` stepper cutout and the `-6.335 mm` (`-X`, Eddy probe side) shifted Bambu X1C hotend below the horizontal Orbiter v2.5 mounting shelf.
2. **4/4 Symmetric Blind Rear-Entry (`-Y`) AD5M Carriage Holes:**
   - Keeps only the 4 true AD5M steel carriage mounting bores: `low_R (-19.0, 3.5)`, `low_L (+19.0, 3.5)`, `up_R (-24.0, 61.0)`, and `up_L (+24.0, 61.0)`.
   - All 4 bores are blind from the rear (`blind_depth_from_rear_mm = 5.54 mm`, `rear_bore_obstruction_mm3 = 0.0`) and terminate behind solid front skins (`1.7 mm` on `low_R`/`low_L`/`up_L`, `1.13 mm` on `up_R`, `front_skin_solid_fraction = 1.0`, `hidden_from_front = true`), leaving zero carriage screw holes visible from `+Y`.
3. **3/3 Obsolete Stock-Extruder Holes Plugged Solid:**
   - Completely fills the 3 asymmetric stock-extruder holes that are no longer needed with Orbiter v2.5:
     - `old_mid_R (-21.5, 51.0)` (`Y = [-11.05, -7.0]`)
     - `old_up_L_hi (+23.7, 66.5)` (`Y = [-9.05, -4.0]`, trimmed with `.cut(belt_high_zone)`)
     - `old_top_R (-14.0, 71.5)` (`Y = [-9.05, -7.0]`)
   - All 3 plugged regions verify `solid_fraction = 1.0` (`completely_plugged = true`), eliminating unnecessary inner protective pins inside the motor pocket while keeping the rear belt channels (`Y <= -9.12 mm`) clear.
4. **Retained `R2` `3010` Fan Bay & Enclosed Convergent Cooling Ducting:**
   - Keeps the full `+X` `3010` fan shroud arch (`YZ = (11.372, 22.246)`, `R = 14.50 mm`, clearing Orbiter's `+X` hub with `0.0 mm³` collision), all 4 open `3010` corner M3 bores (`(-0.63, 10.25)`, `(23.37, 10.25)`, `(-0.63, 34.25)`, `(23.37, 34.25)`, `0.0 mm³` obstruction), 5-section `Part.makeLoft` plenum (`duct_core_solid_fraction = 0.0` at all 6 X stations `18.5, 14.0, 8.0, 2.5, -18.0, -25.0`), sealed `Z = [5.50, 7.50]` floor, internal upper deflector hood, and flush sealed front shroud (`shroud_front_y = 30.119 mm`) exposing only the upper shifted X1C M3 wrench pocket (`Z = 24.80..31.10 mm`, bores at `(-9.760, 27.220)` & `(-2.910, 27.220)`).

---

## Exported Artifacts
| File | Description | Verified Checks |
| --- | --- | --- |
| [`BambuMod_Orbiter25_Primary_R3.stl`](BambuMod_Orbiter25_Primary_R3.stl) | Print-ready STL rotated flat on rear `-Y` carriage face (`Z_stl = 0.0 mm`) | `9402` facets, `is_solid = true`, `has_non_manifolds = false`, `watertight = True`, `winding = True`, `components = 1`, `volume = 36078.41 mm³`, bed bbox `[-29.998..30.0] × [-0.0..80.002] × [0.0..43.236] mm` |
| [`BambuMod_Orbiter25_Primary_R3.step`](BambuMod_Orbiter25_Primary_R3.step) | Single-solid BRep STEP (`36060.31 mm³`) | `step_valid = true`, `step_solids = 1`, upright bbox `[-29.998..30.0] × [-11.117..32.119] × [-0.0..80.002] mm` |
| [`BambuMod_Orbiter25_Assembly_R3.FCStd`](BambuMod_Orbiter25_Assembly_R3.FCStd) | FreeCAD assembly (adapter + Orbiter v2.5 + X1C + 3010 fan + EBB42 short bridge) | `0.0 mm³` collision across all 9 checks (`Orbiter`, `Orbiter M3 bolts`, `X1C`, `3010` fan & vs Orbiter, `EBB42`, steel carriage plane, low/high belt pockets) |
| [`Primary_R3_part_views.png`](Primary_R3_part_views.png) | Adapter orthographic front/rear + ISO renders | Visual check: 0 front holes, smooth motor pocket rim, only 4 symmetric rear carriage bores |
| [`Primary_R3_assembly_views.png`](Primary_R3_assembly_views.png) | Full toolhead assembly orthographic views | Visual check: zero overlaps across Orbiter, X1C, 3010 fan arch, and EBB42 bracket |
| [`Primary_R3_duct_cutaways.png`](Primary_R3_duct_cutaways.png) | BRep internal duct section views | Visual check: continuous 5-section plenum, sealed `X = 0` floor, internal upper baffle hood |
| [`validation.json`](validation.json) | Machine-readable BRep, collision, 4-hole blind, 3-hole plug, fan-hole, and STL metrics | All assertions pass |

---

## Print Settings & Orientation
- **Orientation:** Import `BambuMod_Orbiter25_Primary_R3.stl` as-is — the rear AD5M carriage face sits flat on `Z = 0.0 mm` (`[-29.998..30.0] × [-0.0..80.002] × [0.0..43.236] mm`).
- **Material:** ABS, ASA, PC-CF, or PETG-CF recommended for enclosed chamber temperatures near the X1C heatsink & stepper flange.
- **Overhang / Supports note:** Printed flat on `-Y`, overhanging/bridged faces measure `overhang_gt45deg_mm2 = 4784.76 mm²` and `flat_bridge_gt70deg_mm2 = 4638.89 mm²`. Review slicer preview around the X1C top block pocket, slanted motor flange steps, and `3010` fan overhang lips — light tree/snug supports under external bridges or tuned bridging recommended; avoid placing hard-to-remove support inside the closed duct chamber or the 4 blind `-Y` bores.

## Hardware & Fit Notes (Test-Fit Required)
- **4× Rear-Only Blind Carriage Fasteners (Important):**
  - All 4 symmetric carriage bores (`low_R`, `low_L`, `up_R`, `up_L`) have **`5.54 mm` blind pocket depth** from `Y = -11.117 mm` behind `1.7 mm` (`1.13 mm` on `up_R`) front skins.
  - Measure steel carriage thickness + M3 screw protrusion carefully before tightening (`< 5.3 mm` engagement inside plastic) so screws never bottom out and punch through the front skin (`up_R` is tightest at `1.13 mm` front skin).
- **Orbiter v2.5 & Filament Path (`Z_mount = 32.600 mm`, `X_fil = -6.335 mm`):**
  - Verify M3 hardware into the Orbiter shelf bores, cut a short captive Ø4 mm OD PTFE guide tube bridging X1C heatsink top to Orbiter exit, and confirm smooth manual filament feeding with zero binding.
- **Bambu X1C Hotend & `3010` Cooling Fan:**
  - Seat the shifted X1C heatsink (`X_fil = -6.335 mm`), fasten via the 2 front M3 wrench-pocket bores (`(-9.760, 27.220)` and `(-2.910, 27.220)`), and mount the `3010` fan onto the `+X` bay using all 4 M3 corner bores (`(-0.63, 10.25)`, `(23.37, 10.25)`, `(-0.63, 34.25)`, `(23.37, 34.25)`).
- **Klipper Geometry Offsets (`X_fil = -6.335 mm`):**
  - Nozzle shifted **`-6.335 mm` along `X`** relative to Kirill_Wawe's centered BambuMod hotend datum. Re-calibrate `[probe_eddy_current]` `x_offset` (`eddy_x - nozzle_x`), `[stepper_x]` / `[bed_mesh]` travel limits, and run a physical first-fit check before powering heaters.

## License & Attribution
- Derived from **Kirill_Wawe**'s BambuMod for FlashForge Adventurer 5M (`Printables #1574762`) — **CC BY-NC-SA 4.0**.
- Reference extruder geometry: **Orbiter v2.5** by **dr. Lorincz Robert**.
- R3 remix files inherit **CC BY-NC-SA 4.0** non-commercial ShareAlike licensing and attribution.
- CAD checks (`0.0 mm³` interference, valid 1-solid STEP, watertight 1-component STL) are digital only; **physical test-fit on hardware is unverified.**
