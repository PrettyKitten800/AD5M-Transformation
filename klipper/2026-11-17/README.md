# AD5M Klipper configuration snapshot — 2026-11-17

This is a file-for-file snapshot of the printer configuration on CurberryPi, with custom Klipper modules, host service definitions, firmware build configs, and the completed first-layer test. It is machine-specific.

## Contents

- `config/`: the entire printer config directory, including `printer.cfg`'s SAVE_CONFIG block (Eddy height/thermal calibration, saved meshes, heater PID and shaping), all included macros/configs, host/UI configs, slicer presets/bundles, historical `.pre-*`/dated backups and protected mesh copies.
- `klippy/extras/z_speed_control.py`: required by `[z_speed_control]`; includes native safe homing when Z is unknown and the restored stuck-endstop safeguard.
- `klippy/extras/two_stage_probe.py`: legacy inactive helper, preserved for history; not included by the current printer setup.
- `firmware-build-configs/`: Klipper/Katapult build options for the main/current and historical controller setups; no flash/readback binaries.
- `validation/first-layer/`: the actual Siraya Tech ASA-GF 30×30×0.20 mm test, details, final status. It completed on November 16 at 260°C nozzle / 105°C bed, 20 mm/s, with zero toolhead/Eddy retransmitted or invalid bytes. The user reported: **“Sticking, with lines joining together.”** This is a successful small first-layer test, not full-bed or long-print certification.
- `MANIFEST.json`: SHA-256 and original path for each source file; identifies the active include closure separately from inactive/historical configs.

## Current verified operating setup

- Octopus Pro V1.1 H723 USB-to-CAN bridge; EBB42 V1.2.1 and Eddy Duo both on CAN in the current config. Older USB-Eddy design notes are historical.
- User-confirmed 0.4 mm nozzle. Eddy offset X+35 mm, Y0; height map 101 points, temperature reference 35.280055°C, previous nine drift polynomials retained.
- XY range: X −10..213.4, Y **12..220**. Slicer printable polygon: `0x12,213.4x12,213.4x220,0x220`. The Y12 front boundary was positioned by the user to clear the part cooler; rear home is Y220.
- Homing: **Z → rear Y → right X**. Every Home X request first establishes rear Y clearance. XY backs off 5 mm after contact; 2 s stall-clearance delays remain. Y SGTHRS restored to 64 after a suspected premature trigger at 80.
- Purge: X15..75 at **Y15**, Z0.8. Requested 30 mm extrusion is automatically capped for the configured nozzle cross-section (about 15.17 mm filament with the 0.4 mm nozzle).
- `START_PRINT` validates object geometry, resets offsets/limits, heats, homes in the corrected order, waits for printing temperatures, creates a fresh adaptive Eddy mesh, and purges. `END_PRINT` turns off heaters and parks with the bed lowered.
- Slicer output must use Klipper G-code with object labels/exclusion definitions before START_PRINT, the configured bed origin/boundary, and the physical nozzle size. The old centered −110..110 Benchy file caused the Y−110 startup failure and must not be used.

## Restore notes

1. Inspect `MANIFEST.json` → `active_config_files`; those ten files form the active printer include closure. Historical/checkout configs beside them must not be blindly included.
2. Back up the destination first. Preserve relative includes when restoring the active files into `printer_data/config/`. `mainsail.cfg` is a materialized copy of the original symlink target so this archive is self-contained.
3. Install `klippy/extras/z_speed_control.py` into the corresponding Klipper checkout. The recorded installed Klipper commit is `0cee841e31d701595b3e509a0b502f6e320f52a8`; compare APIs before using the custom helper with another version.
4. Serial/CAN identifiers are specific to this printer. Host-service files, Moonraker authentication/network configuration and KlipperScreen connection settings are excluded from this Klipper-only snapshot.
5. Restore the matching `printer.cfg` SAVE_CONFIG calibration block together with this hardware configuration. Nozzle, probe mounting or frame changes require physical checks/calibration.
6. Restart/reload only when idle, inspect warnings, then verify endstops and supervised cold travel before printing. Do not treat a configuration upload as a physical test.

## Scope and attribution

No printer movement, heating, configuration edits or sharing changes were performed to create this snapshot. Credential fields were checked; no assigned API/password/token/secret fields were found in the config directory. Firmware readbacks, account credentials, host-service files, Moonraker/KlipperScreen settings, runtime logs/databases and unrelated CAD are outside this configuration snapshot. Retain source copyright/license headers; copied Klipper modules are GPL licensed as their headers state. First-layer temperature selection was checked against [Siraya Tech's ASA-GF manual](https://siraya.tech/pages/siraya-tech-asa-gf-filament-user-manual).
