# BambuMod x Orbiter v2.5 Offset-Hotend Carriage Adapter — Revision 4 (`Primary_R4`)

## Summary of R4 Changes (Built on `Primary_R3`)
1. **Plain, Smooth Wider Circular Motor Opening (`Ø44.0 mm` / `R = 22.00 mm`):**
   - Replaces `R3`'s stepped rings, `±30°` diagonal ear cutouts, `7:30` JST notch, and Kirill's top stadium slot/stock extruder recesses with a **single plain, smooth `Ø44.0 mm` through-circle** centered at `(X_mot = 0.000, Z_mot = 51.900 mm)`.
   - Gives `3.77 mm` radial clearance around the LDO stepper barrel (`Ø36.5 mm`, `R = 18.23 mm`) and clears the rear 7:30 JST-PH connector shell (`maxR = 21.64 mm`) cleanly with `circle_core_obstruction_mm3 = 0.0`.
2. **Simplified Upper Backplate Portal & EBB42 Top Bridge (`3.27 mm` Recessed Web + Full-Thickness Pillars & Top Bridge):**
   - Frames the motor circle inside a clean, flat recessed central web (`Y = [-11.117, -7.850]`, `portal_web_thickness_mm = 3.27 mm`) bounded by full-thickness vertical side columns (`|X| >= 22.50 mm`, `left/right_column_solid_fraction = 1.0`) and a full-thickness horizontal top bridge (`Z >= 67.00 mm`, `top_bridge_min_height_mm = 6.10 mm` above the `Ø44.0 mm` crown, `top_bridge_solid_fraction = 1.0`).
   - Preserves all 4 EBB42 top M3 mounting bores (`X = -27, -18, +18, +27 mm`, `Y = -7.498 mm`, `0.0 mm³` obstruction) and rear belt slots (`0.0 mm³` belt collision), while cleanly trimming unused upper front cover-magnet wings above the horizontal plate (`-X`) and above the `3010` fan shroud roof (`Z = 37.35 mm`, `+X`).
3. **Retained `R3` 4-Hole Blind Carriage Mounts & `R2` Offset-Hotend Cooling Duct:**
   - Retains only the 4 symmetric AD5M blind rear-entry (`-Y`) carriage bores (`low_R (-19.0, 3.5)`, `low_L (+19.0, 3.5)`, `up_R (-24.0, 61.0)`, `up_L (+24.0, 61.0)`, `blind_depth_from_rear_mm = 5.54 mm`, `hidden_from_front = true`, `1.7 mm` / `1.13 mm` solid front skins).
   - Preserves `X_fil = -6.335 mm`, `Z_mount = 32.600 mm`, full `+X` `3010` fan shroud arch, 4/4 open `3010` corner M3 bores (`0.0 mm³` obstruction), 5-section `Part.makeLoft` enclosed cooling plenum (`0.0` duct core solid fraction across all 6 tested X stations), sealed `X = 0` floor, internal upper deflector hood, and front X1C M3 wrench pocket.

---

## Exported Artifacts
| File | Description | Verified Checks |
| --- | --- | --- |
| [`BambuMod_Orbiter25_Primary_R4.stl`](BambuMod_Orbiter25_Primary_R4.stl) | Print-ready STL rotated flat on rear `-Y` carriage face (`Z_stl = 0.0 mm`) | `8350` facets, `is_solid = true`, `has_non_manifolds = false`, `watertight = True`, `winding = True`, `components = 1`, `volume = 35642.78 mm³`, bed bbox `[-29.998..30.0] × [-0.0..80.002] × [0.0..43.236] mm` |
| [`BambuMod_Orbiter25_Primary_R4.step`](BambuMod_Orbiter25_Primary_R4.step) | Single-solid BRep STEP (`35627.45 mm³`) | `step_valid = true`, `step_solids = 1`, upright bbox `[-29.998..30.0] × [-11.117..32.119] × [-0.0..80.002] mm` |
| [`BambuMod_Orbiter25_Assembly_R4.FCStd`](BambuMod_Orbiter25_Assembly_R4.FCStd) | FreeCAD assembly (adapter + Orbiter v2.5 + X1C + 3010 fan + EBB42 short bridge) | `0.0 mm³` collision across all 9 reference checks |
| [`Primary_R4_part_views.png`](Primary_R4_part_views.png) | Adapter orthographic front/rear + ISO renders | Visual check: plain `Ø44.0 mm` motor circle, clean portal & bridge, 4 rear bores |
| [`Primary_R4_assembly_views.png`](Primary_R4_assembly_views.png) | Full toolhead assembly orthographic views | Visual check: motor clearance inside `Ø44.0 mm` hole, EBB42 top bridge, 3010 fan, Orbiter & X1C |
| [`Primary_R4_duct_cutaways.png`](Primary_R4_duct_cutaways.png) | BRep internal duct section views | Visual check: continuous 5-section plenum, sealed `X = 0` floor, internal upper baffle hood |
| [`validation.json`](validation.json) | Machine-readable BRep, collision, portal, EBB42, blind-hole, fan-hole, and STL metrics | All assertions pass |

---

## Print Settings & Orientation
- **Orientation:** Import `BambuMod_Orbiter25_Primary_R4.stl` as-is — the rear AD5M carriage face sits flat on `Z = 0.0 mm` (`[-29.998..30.0] × [-0.0..80.002] × [0.0..43.236] mm`).
- **Material:** ABS, ASA, PC-CF, or PETG-CF recommended for enclosed chamber temperatures near the X1C heatsink & stepper flange.
- **Overhang / Supports note:** Printed flat on `-Y`, overhanging/bridged faces are reduced vs `R2`/`R3` to `overhang_gt45deg_mm2 = 4572.04 mm²` and `flat_bridge_gt70deg_mm2 = 4429.83 mm²` (with zero tall unused `+X` cover-magnet chimney). Review slicer preview around the X1C top block pocket and `3010` fan overhang lips — light tree/snug supports under external bridges or tuned bridging recommended; avoid placing support inside the closed cooling duct or the 4 blind `-Y` bores.

## Hardware & Fit Notes (Test-Fit Required)
- **4× Rear-Only Blind Carriage Fasteners:** All 4 symmetric carriage bores have `5.54 mm` blind pocket depth behind `1.7 mm` (`1.13 mm` on `up_R`) front skins — keep M3 screw engagement inside plastic `< 5.3 mm`.
- **Orbiter v2.5 & EBB42 (`Z_mount = 32.600 mm`, `Z_bridge = 80.002 mm`):** Check manual filament feeding (`X_fil = -6.335 mm` with captive Ø4 mm OD PTFE tube guide) and M3 heatset installation in the 4 top EBB42 bores (`X = -27, -18, +18, +27 mm`).
- **Klipper Geometry Offsets (`X_fil = -6.335 mm`):** Re-calibrate `[probe_eddy_current]` `x_offset`, `[stepper_x]` / `[bed_mesh]` limits, and perform a cold mechanical test-fit before powering heaters.

## License & Attribution
- Derived from **Kirill_Wawe**'s BambuMod for FlashForge Adventurer 5M (`Printables #1574762`) — **CC BY-NC-SA 4.0**.
- Reference extruder geometry: **Orbiter v2.5** by **dr. Lorincz Robert**.
- R4 remix files inherit **CC BY-NC-SA 4.0** non-commercial ShareAlike licensing and attribution.
- CAD checks (`0.0 mm³` interference, valid 1-solid STEP, watertight 1-component STL) are digital only; **physical test-fit on hardware is unverified.**
