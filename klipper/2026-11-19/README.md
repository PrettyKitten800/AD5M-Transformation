# The Moron Tridont Project — Klipper & Slicer Snapshot (2026-11-19)

> **Superseded the same evening:** the printer moved from mainline Klipper to Kalico + eddy-ng. The current configuration is [`../2026-11-19-kalico/`](../2026-11-19-kalico/). The OrcaSlicer presets in this folder are still the current ones.

This snapshot captures the live 10-file Klipper active include closure from `http://192.168.4.31` along with pre-edit backups from 2026-11-19 and the tuned OrcaSlicer profile bundle (`Moron_Tridont_04_Corrected.orca_printer`).

## Contents

- `config/`: Live active Klipper configuration files (`printer.cfg`, `mainsail.cfg`, `bed-heater-check.cfg`, `motion-check.cfg`, `extruder.cfg`, `calibration.cfg`, `eddy-duo.cfg`, `eddy-macros.cfg`, `forge-x-macros.cfg`, `printer-behavior.cfg`) plus pre-change backups (`*.pre-preheat-20261119-194252`).
- `config/slicer-presets/`: Updated `Moron_Tridont_04_Corrected.orca_printer` bundle alongside extracted JSON presets (`bundle_structure.json`, `printer/`, `filament/`, `process/`) for human-readable Git diffs.
- `MANIFEST.json`: File list (`active_config_files`) with exact byte sizes and SHA-256 hashes.

## Key Changes Captured (vs. 2026-11-17 Snapshot)

- **Orbiter v2.5 + LDO (`config/extruder.cfg`):** Configured with `rotation_distance: 4.69`, `pressure_advance_smooth_time: 0.030`, `max_extrude_only_velocity: 120`, `max_extrude_only_accel: 3000`, and `[tmc2209 extruder]` `run_current: 0.85` (`interpolate: False`).
- **Timed Bed Preheat Macros (`config/printer-behavior.cfg` & `config/forge-x-macros.cfg`):**
  - Added `[gcode_macro PREHEAT]` (`TEMP` default `100` C up to `< heater_bed.max_temp`, `MINUTES` default `30` up to `240` min), `[gcode_macro CANCEL_PREHEAT]`, `_PREHEAT_STOP`, and `[delayed_gcode _PREHEAT_TICK]` (updates Mainsail `M117` countdown and shuts off `heater_bed` cleanly on completion).
  - Updated `_PRINTER_IDLE` so the 20-minute `[idle_timeout]` does not shut down `heater_bed` while a `PREHEAT` timer is active, and updated `START_PRINT` / `_PRINTER_CANCEL_CLEANUP` to disarm any active preheat timer safely.
- **OrcaSlicer Bundle (`Moron_Tridont_04_Corrected.orca_printer`):**
  - `Moron Tridont 0.4`: Updated extruder machine limits (`120 mm/s` E speed, `3000 mm/s^2` E & retract acceleration).
  - `Moron Tridont Sunlu ABS 0.4`: Tuned baseline (`260 C` nozzle, `100 C` bed, `20 mm^3/s` max volumetric speed, `PA 0.02`, `0.95` flow ratio, `99.4%` XY shrink, `45%` overhang/bridge fan).
  - Process lineup (`7` presets): Added `Moron Tridont 0.16mm Sunlu ABS`, `0.24mm Sunlu ABS`, and `0.20mm Sunlu ABS Voron` (`4` walls, `5`/`5` shells, `40%` gyroid infill) alongside tuned `0.20mm Sunlu ABS` (`40 mm/s` first-layer speed, `skirt_speed: 0` matching first layer) and existing `0.16 / 0.20 / 0.24mm ASA` presets.

## Restore & Safety Notes

- Credentials, Moonraker databases, `moonraker.conf`, and machine secrets are excluded from this snapshot.
- `START_PRINT` requires `RESTART` / Klipper reload after uploading edited `.cfg` files so new macros (`PREHEAT`, `CANCEL_PREHEAT`) take effect.
- Always verify endstops, probe Z-offset, and cold clearances physically after restoring configurations or changing hotend/shroud hardware.
