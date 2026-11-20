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
- Plans: [Upgrade roadmap](docs/plans/UPGRADE_ROADMAP.md) · [Frame conversion plan (Voron Trident 300×300×300 mm)](docs/plans/FRAME_CONVERSION.md)
- History (superseded hardware; read the banner at the top of each): [Build sequence](docs/history/BUILD_SEQUENCE.md) · [Toolhead-first plan](docs/history/TOOLHEAD_FIRST.md) · [Start-here handoff](docs/history/START_HERE_AD5M.txt) · [Rebuild handoff](docs/history/AD5M_REBUILD_HANDOFF.txt) · [Controller options, Nov 2](docs/history/BTT_CONTROLLER_OPTIONS_2026-11-02.md) · [Nov 2 handoff package](docs/history/AD5M_HANDOFF_2026-11-02/)
- [Working instructions and physical test status](AGENTS.md)
- [Cloud setup and remaining connection steps](CLOUD_SETUP.md)

## CAD and references

- [Outputs index (active vs. historical revisions)](outputs/INDEX.md)
- [Portable current CAD builders/renderers](scripts/cad/)
- [Original user-supplied BambuMod housing](reference/BambuMod/)
- [X1 hotend reference](reference/Bambu_X1_hotend_CAD/)
- Historical scripts and intermediate studies: [work/](work/) (see its README) and outputs/.

Native FreeCAD Python bindings are required for builders. NumPy, Pillow, trimesh and Shapely support rendering and checks. Python package dependencies are in requirements-cloud.txt. Windows-only historical scripts are preserved; prefer scripts/cad/ in the cloud.

Large downloaded upstream archives/checkouts and machine-specific flash backups are excluded from Git. Source metadata and download links remain under reference/. No local files were deleted. This is a curated source workspace, not an automatic backup of the entire Windows Desktop.

## Useful bookmarks

- [ScanRuler by CNC Kitchen](https://scanruler.com) — browser-local 3D scan & CAD/mesh analysis (STL, PLY, OBJ, 3MF, STEP: 3D measure, surface deviation, wall thickness, feature fitting, reverse engineering).

Per-revision details for every part (including the BambuMod × Orbiter `R1`–`R8` line) are in [outputs/INDEX.md](outputs/INDEX.md) and each folder's `PRINT_AND_FIT.md`.

## Attribution

This repository contains mixed original and third-party content. Preserve each source's license and attribution. BambuMod-derived brackets retain the stated CC BY-NC-SA 4.0 attribution in their installation notes. The Jorge hotend is an unchanged reference with its own source/license. Do not apply a blanket license to upstream material.

## Current Klipper configuration

- **[2026-11-19 Kalico snapshot](klipper/2026-11-19-kalico/) — current:** Kalico `v2026.11.00-73-gfb4e09bc` + eddy-ng on the Intel host; `limited_corexy`, MPC hotend control, eddy-ng Eddy on CAN (`x_offset: 28.7`), `forge-x-macros.cfg` renamed `tridont_macros.cfg`, sanitized host units and firmware provenance.
- **[2026-11-19 printer snapshot](klipper/2026-11-19/) (mainline Klipper, superseded that evening; slicer presets still current):** Live 10-file active Klipper closure (`extruder.cfg` for Orbiter v2.5 + LDO: `4.69` rotation distance, `120 mm/s` / `3000 mm/s²` E limits, `0.85` current; `printer-behavior.cfg` & `forge-x-macros.cfg` with timed bed `PREHEAT` / `CANCEL_PREHEAT` macros) and updated `Moron_Tridont_04_Corrected.orca_printer` bundle (Sunlu ABS tuned `260 °C / 100 °C / 20 mm³/s / PA 0.02`, 4 ABS process profiles).
- **[2026-11-17 printer snapshot](klipper/2026-11-17/):** Baseline configs/calibration, historical config backups, custom modules, [host services/configs](klipper/2026-11-17/host/), [Intel host migration handoff](klipper/2026-11-17/migration/), presets, and the successful Siraya ASA-GF first-layer test.
