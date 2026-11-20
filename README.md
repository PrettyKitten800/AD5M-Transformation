# The Moron Tridont Project (AD5M-Transformation)

Mods to turn a FlashForge AD5M into a frankenstein'd Trident-like AWD printer.

This repository is the shared file workspace for **The Moron Tridont Project** (FlashForge AD5M conversion): build notes, hardware references, printable toolhead brackets and CAD scripts. The printer currently runs the `R8` BambuMod × Orbiter v2.5 housing with the `R4` fan shroud, an Orbiter v2.5 + LDO extruder, a TZ 2.0 clone hotend, EBB42 V1.2.1 and Eddy Duo (both on CAN), and Kalico + eddy-ng on an Intel host. The full table is in [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md). Gantry/rail changes and a future tool changer are longer-term work.

## Current printable designs

| Part | Files | Status |
| --- | --- | --- |
| **Installed:** BambuMod × Orbiter v2.5 housing | [R8](outputs/BambuMod_Orbiter25_Remix_R8/) | **On the printer** with the `R4` shroud (user-confirmed 2026-11-20). Live parametric workspace: `scripts/cad/r8_live_builder.py` |
| **Installed:** recovered Printables `1404902` fan shroud | [R4](outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R4/) | **On the printer** on `R8`, Z-height adjusted (2026-11-19) |
| BambuMod × Orbiter v2.5 carriage adapter remix (Primary & Alternate) | [R1](outputs/BambuMod_Orbiter25_Remix_R1/) | History; the Primary line led to the installed `R8`. Two watertight CC BY-NC-SA 4.0 remixes replacing stock extruder mount with ±30° slanted motor + 7:30 JST-PH relief and horizontal Orbiter v2.5 `XY` shelf: **Primary** (`X_mot = 0`, hotend `-6.335 mm` right, stock `3010` fan) & **Alternate** (`X_fil = 0`, motor `+6.335 mm` left, relocated `+X` `3010` fan pod); `0.0 mm³` CAD collisions; untested physically |
| BambuMod × Orbiter v2.5 offset-hotend progression & live workspace | [R2](outputs/BambuMod_Orbiter25_Remix_R2/)..[R8](outputs/BambuMod_Orbiter25_Remix_R8/) | Append-only revisions adding restored `3010` shroud arch + C2 B-spline cooling duct, 4 blind carriage bores, twin rear M3 hex pockets (`R6`), reinforced `R7` bosses/fillets, and live parametric workspace `R8` (`scripts/cad/r8_live_builder.py`); `R2`–`R7` are history, `R8` is installed |
| Recovered Printables `1404902` part-cooling fan shroud | [R1](outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R1/)..[R4](outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R4/) | Aligns Printables `1404902` shroud onto `R8` (`R2`), trims magnet tab rear faces flush (`R3`), and flattens all 4 pinned faces (`R4`, `26,966` facets, watertight 1-solid manifold); `R4` physically mounted & height-adjusted on printer (2026-11-19) |
| Dragon Burner (`#1406257` v11) AD5M Mode-A Rear Eddy Duo adapter | [R1](outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1/) | **Dropped (2026-11-20); history only.** Centered (`x_offset = 0.0`, `y_offset = 35.0 mm` behind nozzle, `+2.5 mm` above nozzle) rear Mode-A pocket for de-shelled Eddy Duo, `26.61 mm` M3 slots (`±1.0 mm` travel), `2.7 mm` min front thermal baffle, upward USB relief channel; watertight STL verified; untested physically |
| Custom toolhead housing + inline front Eddy Duo mount (`x_offset = 0`) | [R1](outputs/AD5M_custom_toolhead_inline_eddy_R1/) | Not installed. New custom housing (`AD5M_Custom_Housing_R1`) + inline front Eddy bracket (`Eddy_Duo_Inline_Mount_R1`); CAD & watertight mesh verified; untested physically |
| EBB42 bracket with uniform angled posts | [R7](outputs/EBB42_uniform_posts_R7/) | Revised after R5 printed successfully enough for a fit check; R7 untested physically |
| Simple central wedge EBB42 mount | [R6](outputs/EBB42_simple_wedge_R6/) | User reported printing; requires PCB-back spacers |
| Reinforced adjustable Eddy Duo mount | [R4](outputs/Eddy_Duo_adjustable_side_mount_R4/) | Side-mount proposal (`x_offset ≈ 44 mm`); live rapid-scan commissioning showed right-edge magnetic drop-off beyond `X = 196 mm`, motivating inline `R1` above |

Read each part's PRINT_AND_FIT.md or PRINT_AND_INSTALL.md. Older output revisions are retained as history, including superseded placements. CAD checks do not establish installed frame, motor, nozzle or cable clearance.

## Build records

- [Current specification: what is on the printer now](CURRENT_TOOLHEAD_SPEC.md)
- [Toolhead design journal, November 6–19 (history)](docs/history/TOOLHEAD_SPEC_JOURNAL_2026-11.md)
- [Build sequence](BUILD_SEQUENCE.md)
- [Toolhead-first plan](TOOLHEAD_FIRST.md)
- [Upgrade roadmap](UPGRADE_ROADMAP.md)
- [Frame conversion plan (Voron Trident 300×300×300 mm)](FRAME_CONVERSION.md)
- [Working instructions and physical test status](AGENTS.md)
- [Cloud setup and remaining connection steps](CLOUD_SETUP.md)

## CAD and references

- [Outputs index (active vs. historical revisions)](outputs/INDEX.md)
- [Portable current CAD builders/renderers](scripts/cad/)
- [Original user-supplied BambuMod housing](reference/BambuMod/)
- [X1 hotend reference](reference/Bambu_X1_hotend_CAD/)
- Historical scripts and intermediate studies: work/ and outputs/.

Native FreeCAD Python bindings are required for builders. NumPy, Pillow, trimesh and Shapely support rendering and checks. Python package dependencies are in requirements-cloud.txt. Windows-only historical scripts are preserved; prefer scripts/cad/ in the cloud.

Large downloaded upstream archives/checkouts and machine-specific flash backups are excluded from Git. Source metadata and download links remain under reference/. No local files were deleted. This is a curated source workspace, not an automatic backup of the entire Windows Desktop.

## Useful bookmarks

- [ScanRuler by CNC Kitchen](https://scanruler.com) — browser-local 3D scan & CAD/mesh analysis (STL, PLY, OBJ, 3MF, STEP: 3D measure, surface deviation, wall thickness, feature fitting, reverse engineering).

### BambuMod × Orbiter v2.5 CAD Revision Log (`R2`–`R7`)

- `outputs/BambuMod_Orbiter25_Remix_R2/`: **Offset-hotend Revision 2 (`Primary_R2`)** with restored BambuMod `3010` fan shroud arch + 5-section `Part.makeLoft` cooling duct (sealed `X=0` floor, shifted X1C heatsink slot & front M3 access pocket, all 4 `3010` M3 bores clear) and all 7 rear-entry blind carriage holes (`hidden_from_front = true`). Generated by `scripts/cad/build_bambumod_orbiter25_R2.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R2.py`; valid 1-solid STEP, watertight 1-component STL (`BambuMod_Orbiter25_Primary_R2.stl`), `0.0 mm³` CAD collisions (untested physically).
- `outputs/BambuMod_Orbiter25_Remix_R3/`: **Offset-hotend Revision 3 (`Primary_R3`, preserved prior revision)** retaining only the 4 symmetric AD5M rear-entry blind carriage holes (`(-19.0, 3.5)`, `(+19.0, 3.5)`, `(-24.0, 61.0)`, `(+24.0, 61.0)`, hidden from the front), plugging solid the 3 obsolete stock-extruder holes (`(-21.5, 51.0)`, `(+23.7, 66.5)`, `(-14.0, 71.5)`) while keeping belt channels clear and keeping the `R2` `3010` fan shroud arch + 5-section `Part.makeLoft` cooling ducting. Generated by `scripts/cad/build_bambumod_orbiter25_R3.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R3.py`; valid 1-solid STEP, watertight 1-component STL (`BambuMod_Orbiter25_Primary_R3.stl`, `9402` facets), `0.0 mm³` CAD collisions (untested physically).
- `outputs/BambuMod_Orbiter25_Remix_R4/`: **Preserved offset-hotend Revision 4 (`Primary_R4`)** simplifying the motor cutout & upper backplate into a plain, smooth `Ø44.0 mm` (`R = 22.00 mm`) circle inside a `3.27 mm` recessed web framed by full-thickness vertical columns (`|X| >= 22.50 mm`) and top EBB42 bridge (`Z >= 67.00 mm`, all 4 EBB42 M3 bores open), trimming unused upper front cover-magnet wings while keeping `R3`'s 4 symmetric blind carriage holes and `R2`'s `3010` fan shroud arch + 5-section cooling duct. Generated by `scripts/cad/build_bambumod_orbiter25_R4.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R4.py`; valid 1-solid STEP, watertight 1-component STL (`BambuMod_Orbiter25_Primary_R4.stl`, `8350` facets), `0.0 mm³` CAD collisions (untested physically).
- `outputs/BambuMod_Orbiter25_Remix_R5/`: **Preserved offset-hotend Revision 5 (`Primary_R5`)** replacing `R2`–`R4`'s sharp polygonal cooling duct and residual Kirill chamber ledges with a smooth 15-station C2 periodic B-spline air tunnel loft (`build_smooth_duct_void()`, strict OCCT `BOPCheck` clean), and adding a `Ø9.00 mm` flat perpendicular nut-landing boss (`Z_NUT_FACE = 27.60 mm`, `4.98 mm` plate grip, `Ø12.40 mm` clearance pocket, extended `Ø3.60 mm` M3 through-bore) on the `+X` Orbiter mount hole `(+13.15, 12.08)` by the `3010` hotend fan while retaining all `R4` upper-portal/circle/4-blind-bore features. Generated by `scripts/cad/build_bambumod_orbiter25_R5.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R5.py`; valid 1-solid STEP (`38064.63 mm³`), smooth watertight 1-component STL (`BambuMod_Orbiter25_Primary_R5.stl`, `40774` facets, `38040.22 mm³`), `0.0 mm³` CAD collisions (untested physically).
- `outputs/BambuMod_Orbiter25_Remix_R6/`: **Preserved offset-hotend Revision 6 (`Primary_R6`)** restoring Kirill's twin rear-entry (`-Y`) captive DIN 934 M3 hex-nut pockets coaxial with the shifted Bambu X1C mounting screws (`(-9.760, 27.220)` and `(-2.910, 27.220)`, `AF = 5.60 mm` with `0.45 mm` rear entry bevel `AF = 6.30 -> 5.60 mm`, flat axial shoulder at `Y_HEX_SEAT = -3.500 mm`, `0.89 mm` solid wall behind `R5`'s C2 duct), refining the smooth motor circle to `Ø41.00 mm` (`R = 20.50 mm`) for a continuous `>= 1.06 mm` solid rim above the Right hex pocket (`+1.50 mm` thicker top EBB42 portal bridge), and retaining all `R5` smooth C2 duct, `+X` nut boss, and 4-blind-bore features. Generated by `scripts/cad/build_bambumod_orbiter25_R6.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R6.py`; valid 1-solid STEP (`38465.86 mm³`), watertight 1-component STL (`BambuMod_Orbiter25_Primary_R6.stl`, `40874` facets, `38440.89 mm³`), `0.0 mm³` CAD collisions (untested physically).
- `outputs/BambuMod_Orbiter25_Remix_R7/`: **Offset-hotend Revision 7 (`Primary_R7`, preserved; superseded by the installed `R8`)** deriving parametrically from `Primary_R6` with (1) reinforced `R = 3.60 mm` upper carriage bosses `(±24.0, 61.0)` around the `Ø4.30 × 5.54 mm` blind heat-set bores (`1.40 mm` full `360°` wall over `4.22 mm` rear insert zone on `up_R` and full depth on `up_L`, clearing the Orbiter NEMA flange ear with `0.0 mm³` collision), (2) unified `Ø3.60 mm` Orbiter extruder mount holes (`(-23.85, 12.08)` `4.30 mm` blind bore shrunk cleanly from `Ø4.40` to match `(+13.15, 12.08)`), (3) rounded exterior edges + `R_bed = 3.50 mm` anti-warp top carriage corners tapering `<= 40°` to `R_front = 0.85 mm` (`>= 0.82 mm` upper EBB42 outer wall, `R = 1.60 mm` rear / `R = 1.80 mm` front shroud corners, `R = 1.00 mm` swept top rims, `R = 1.50 mm` portal arch fillets), and (4) corrected flat-backplate bed-down STL pose (`1,952.65 mm²` flat bed contact at `Z_bed = 0.000 mm`). Generated by `scripts/cad/build_bambumod_orbiter25_R7.py` and rendered by `scripts/cad/render_bambumod_orbiter25_R7.py`; valid 1-solid STEP (`38375.68 mm³`), watertight 1-shell STL (`BambuMod_Orbiter25_Primary_R7.stl`, `46810` facets, `38350.37 mm³`), `0.0 mm³` CAD collisions (untested physically).

## Attribution

This repository contains mixed original and third-party content. Preserve each source's license and attribution. BambuMod-derived brackets retain the stated CC BY-NC-SA 4.0 attribution in their installation notes. The Jorge hotend is an unchanged reference with its own source/license. Do not apply a blanket license to upstream material.

## Current Klipper configuration

- **[2026-11-19 Kalico snapshot](klipper/2026-11-19-kalico/) — current:** Kalico `v2026.11.00-73-gfb4e09bc` + eddy-ng on the Intel host; `limited_corexy`, MPC hotend control, eddy-ng Eddy on CAN (`x_offset: 28.7`), `forge-x-macros.cfg` renamed `tridont_macros.cfg`, sanitized host units and firmware provenance.
- **[2026-11-19 printer snapshot](klipper/2026-11-19/) (mainline Klipper, superseded that evening; slicer presets still current):** Live 10-file active Klipper closure (`extruder.cfg` for Orbiter v2.5 + LDO: `4.69` rotation distance, `120 mm/s` / `3000 mm/s²` E limits, `0.85` current; `printer-behavior.cfg` & `forge-x-macros.cfg` with timed bed `PREHEAT` / `CANCEL_PREHEAT` macros) and updated `Moron_Tridont_04_Corrected.orca_printer` bundle (Sunlu ABS tuned `260 °C / 100 °C / 20 mm³/s / PA 0.02`, 4 ABS process profiles).
- **[2026-11-17 printer snapshot](klipper/2026-11-17/):** Baseline configs/calibration, historical config backups, custom modules, [host services/configs](klipper/2026-11-17/host/), [Intel host migration handoff](klipper/2026-11-17/migration/), presets, and the successful Siraya ASA-GF first-layer test.
