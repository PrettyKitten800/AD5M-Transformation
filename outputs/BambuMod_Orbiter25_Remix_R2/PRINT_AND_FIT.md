# BambuMod x Orbiter v2.5 Offset-Hotend Carriage Adapter — Revision 2 (`Primary_R2`)

## Summary of R2 Changes (Built on `Primary_R1`)
1. **Offset-hotend configuration only (`X_mot = 0.000 mm`, `X_fil = -6.335 mm`):** Keeps the stepper centered on the AD5M carriage (`X = 0.000, Z = 51.900 mm`) at its slanted `-30°` orientation and mounts the Bambu X1C hotend shifted `-6.335 mm` toward `-X` (Eddy probe side) below the horizontal Orbiter v2.5 shelf (`Z_mount = 32.600 mm`).
2. **Restored BambuMod `3010` hotend fan bay & enclosed convergent ducting:**
   - Restores the full `+X` `3010` fan shroud arch (`Z = 7.25..37.25 mm`, `Ø29.0 mm` discharge centered at `YZ = (11.372, 22.246)`) while trimming only the narrow inner `+X` edge needed to clear the Orbiter hub (`0.000 mm³` collision) and preserving all 4 `3010` corner M3 mounting bores (`0.000 mm³` obstruction).
   - Replaces `R1`'s open upper chamber with a 5-section ruled `Part.makeLoft` plenum curving cleanly from `+X` `3010` exit (`X = 19.65 mm`) over/around the shifted X1C heatsink fins (`X = [-14.185, +1.515]`, `Y = [-2.17, +22.83]`, `Z = [5.72, 24.50]`) out through Kirill_Wawe's `-X` hex exhaust grille (`X <= -27.2 mm`).
   - Plugs the obsolete centered `X = 0` floor aperture (`floor_seal` `Z = [5.50, 7.50]`) and seals the front shroud wall (`Y = 24.0..30.119`, `Z = [21.80, 32.58]`) flush to exact `shroud_front_y`, while keeping an accessible front M3 wrench pocket (`X = [-12.935, +0.265]`, `Z = [24.80, 31.10]`) above the cooling tunnel roof.
3. **Blind rear-entry (`-Y`) carriage mounting holes (all 7 hidden from front):**
   - All 7 carriage mounting holes (`(-19.0, 3.5)`, `(19.0, 3.5)`, `(-21.5, 51.0)`, `(-24.0, 61.0)`, `(24.0, 61.0)`, `(23.7, 66.5)`, `(-14.0, 71.5)`) now terminate inside `1.13–1.70 mm` solid front skins (`hidden_from_front = true`, `front_skin_solid_fraction = 1.0`, `rear_bore_obstruction_mm3 = 0.0` across all 7 bores).

---

## Exported Artifacts
| File | Description | Verified Checks |
| --- | --- | --- |
| [`BambuMod_Orbiter25_Primary_R2.stl`](BambuMod_Orbiter25_Primary_R2.stl) | Print-ready STL rotated flat on rear `-Y` carriage face (`Z_stl = 0.0 mm`) | `10124` facets, `is_solid = true`, `watertight = true`, `components = 1`, `volume = 36014.82 mm³`, bed bbox `60.00 × 80.00 × 43.24 mm` |
| [`BambuMod_Orbiter25_Primary_R2.step`](BambuMod_Orbiter25_Primary_R2.step) | Single-solid BRep STEP (`35996.85 mm³`) | `step_valid = true`, `step_solids = 1` on re-read |
| [`BambuMod_Orbiter25_Assembly_R2.FCStd`](BambuMod_Orbiter25_Assembly_R2.FCStd) | FreeCAD assembly (adapter + Orbiter v2.5 + X1C + 3010 fan + EBB42 short bridge) | `0.000 mm³` collision across all 9 reference volumes |
| [`Primary_R2_part_views.png`](Primary_R2_part_views.png) | Adapter orthographic front/rear + ISO renders | Visual check: 0 front carriage holes, open rear bores & hex vents |
| [`Primary_R2_assembly_views.png`](Primary_R2_assembly_views.png) | Full toolhead assembly orthographic views | Visual check: X1C screw bay, 3010 arch, Orbiter & EBB42 clearances |
| [`Primary_R2_duct_cutaways.png`](Primary_R2_duct_cutaways.png) | BRep internal duct section views (`Y<=11.37`, `Z<=16.50`, `Y<=23.00`, ISO) | Visual check: continuous plenum, sealed floor, upper 3010 baffle hood |
| [`validation.json`](validation.json) | Machine-readable BRep, collision, blind-hole, fan-hole, and STL metrics | All assertions pass |

---

## Print Settings & Orientation
- **Orientation:** Import `BambuMod_Orbiter25_Primary_R2.stl` as-is — the rear AD5M carriage face sits flat on `Z = 0.0 mm` (`[-29.998..30.000] × [0.000..80.002] × [0.000..43.236] mm`).
- **Material:** ABS, ASA, PC-CF, or PETG-CF recommended for enclosed chamber temperatures near the X1C heatsink & stepper flange.
- **Overhang / Supports note:** Printed flat on `-Y`, overhanging/bridged faces total `4784.69 mm²` (`>45°`) and `4638.82 mm²` (`>70°`, slightly lower than upstream `bm_body`'s `5325.9` / `4932.4 mm²`). Review slicer preview around the X1C top block pocket (`Z = 24.8..31.1`), slanted motor flange steps, and `3010` fan overhang lips — light tree/snug supports under external bridges or tuned bridging recommended; avoid placing hard-to-remove support inside the closed duct chamber or blind `-Y` bores.

## Hardware & Fit Notes (Test-Fit Required)
- **Rear-Only Blind Carriage Fasteners (Important):**
  - The 6 lower/upper carriage bores have **`5.54 mm` blind pocket depth** from `Y = -11.117 mm` (`1.13–1.70 mm` front skin); `top_R_5th (-14.0, 71.5)` has **`5.92 mm` pocket depth** (`1.32 mm` front skin).
  - Measure steel carriage thickness + M3 screw protrusion carefully before tightening (`<= 5.0 mm` engagement inside the plastic for M3 heatset inserts such as M3x4x5 or short M3 fasteners) so screws never bottom out and punch through the front skin.
- **Orbiter v2.5 Mounting (`Z_mount = 32.600 mm`):**
  - Install 2× M3 heatset inserts into the top horizontal shelf at `(-23.85, 12.08)` and `(+13.15, 12.08)` (`Ø4.40 mm × 4.28 mm` deep).
  - Cut a short captive segment of `Ø4.0 mm` OD PTFE tubing (`~1.9 mm` bridging the `Z = 30.72 → 32.60 mm` transition) through the `(-6.335, 12.08)` filament bore between X1C heatsink top and Orbiter exit.
- **Bambu X1C Hotend (`X_fil = -6.335 mm`):**
  - Drop heatsink upward/inward into the `-6.335 mm` lower duct slot (`Z = 5.20..7.65 mm`) and secure with 2× M3 screws from the front (`+Y`) wrench pocket (`(-9.760, 27.220)` and `(-2.910, 27.220)`, `Ø3.30 mm` self-tap bores `~9.9 mm` deep behind `Y = 8.28`).
- **3010 Cooling Fan:** Mount into the `+X` bay (`Y = [-3.63, 26.37]`, `Z = [7.25, 37.25]`) blowing `-X` through the duct onto the X1C fins using all 4 M3 corner bores (`(-0.63, 10.25)`, `(23.37, 10.25)`, `(-0.63, 34.25)`, `(23.37, 34.25)`).
- **Klipper Geometry Offsets (`X_fil = -6.335 mm`):**
  - Nozzle shifted **`-6.335 mm` along `X`** relative to Kirill_Wawe's centered BambuMod hotend datum. Re-calibrate `[probe_eddy_current]` `x_offset` (`eddy_x - nozzle_x`), `[stepper_x]` / `[bed_mesh]` travel limits, and run a physical first-fit check before powering heaters.

## License & Attribution
- Derived from **Kirill_Wawe**'s BambuMod for FlashForge Adventurer 5M (`Printables #1574762`) — **CC BY-NC-SA 4.0**.
- Reference extruder geometry: **Orbiter v2.5** by **dr. Lorincz Robert**.
- R2 remix files inherit **CC BY-NC-SA 4.0** non-commercial ShareAlike licensing and attribution.
- CAD checks (`0.000 mm³` interference, valid 1-solid STEP, watertight 1-component STL) are digital only; **physical test-fit on hardware is unverified.**
