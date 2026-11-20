# The Moron Tridont Project — Kalico + eddy-ng Live Snapshot (2026-11-19)

This snapshot captures the commissioned **Kalico (`v2026.11.00-73-gfb4e09bc`) + `eddy-ng` (`v0.1-188-ga09ec8e`)** configuration live on CurbyServer (`http://192.168.4.31`) after migrating off mainline Klipper (`0cee841e3`), including the `LINE_PURGE` fix for Kalico's `max_extrude_cross_section` default.

Historical snapshots under [`klipper/2026-11-17/`](../2026-11-17/) and [`klipper/2026-11-19/`](../2026-11-19/) remain intact.

## Contents

- `config/`: Live 10-file active Klipper/Kalico include closure (`printer.cfg`, `mainsail.cfg`, `bed-heater-check.cfg`, `motion-check.cfg`, `extruder.cfg`, `calibration.cfg`, `eddy-duo.cfg`, `eddy-macros.cfg`, `tridont_macros.cfg`, `printer-behavior.cfg`). Note `forge-x-macros.cfg` was renamed to `tridont_macros.cfg`.
- `host/`: Sanitized systemd units (`klipper.service` launching `/home/<user>/kalico-env/bin/python /home/<user>/kalico/klippy/klippy.py`, and `can0.service` bringing `can0` up at `1000000` bps).
- `firmware-build-configs/README.md`: Kalico & `eddy-ng` repository commits, CAN UUIDs, bootloader offsets, and compiled `.bin` SHA-256 checksums.
- `MANIFEST.json`: Inventory (`active_config_files` and `files`) with exact byte sizes and SHA-256 hashes.
- **Slicer presets reference:** The OrcaSlicer bundle (`Moron_Tridont_04_Corrected.orca_printer` with Sunlu ABS `260 C / 100 C / 20 mm^3/s / PA 0.02`) remains unchanged in [`../2026-11-19/config/slicer-presets/`](../2026-11-19/config/slicer-presets/).

## Key Calibration & Configuration State

- **Kinematics & Motion (`config/printer.cfg`, `config/calibration.cfg`):**
  - `[printer]` upgraded to Kalico `kinematics: limited_corexy` with `max_velocity: 500`, `max_accel: 7500`, `max_x_accel: 7500`, `max_y_accel: 5000`, `scale_xy_accel: False`, `max_z_velocity: 40`, `max_z_accel: 300`.
  - `[input_shaper]` calibrated in `SAVE_CONFIG` with Kalico smooth shapers (`shaper_type_x = smooth_mzv` at `smoother_freq_x = 52.0`, `shaper_type_y = smooth_zvd_ei` at `smoother_freq_y = 56.0`) and PA synchronization (`enabled_extruders: extruder`).
  - `[telemetry] enabled: False`.
  - Pruned 17 legacy mainline `#*# [bed_mesh ...]` blocks from `printer.cfg`.
- **Hotend MPC (`config/extruder.cfg`, `config/printer.cfg`):**
  - Switched `[extruder]` from PID to Kalico `control: mpc` (`heater_power: 48`, `cooling_fan: fan`, `filament_diameter: 1.750`, `filament_density: 1.06`, `filament_heat_capacity: 1.80`).
  - Calibrated `SAVE_CONFIG` MPC model: `block_heat_capacity = 8.82836`, `sensor_responsiveness = 0.0882052`, `ambient_transfer = 0.0975298`, `fan_ambient_transfer = 0.0975298, 0.0968694, 0.0960767, 0.0962984, 0.0951734`.
  - Configured fallback `pressure_advance: 0.025`, `pressure_advance_smooth_time: 0.030` (OrcaSlicer Sunlu ABS profile sets `PA 0.02`).
  - Replaced `PID_TUNE_EXTRUDER` with `[gcode_macro MPC_TUNE_EXTRUDER]`; replaced `M109 S150` settling waits before tap in `START_PRINT` and `EDDY_MESH` with `M104 S150` + `TEMPERATURE_WAIT SENSOR=extruder MINIMUM=148 MAXIMUM=155`.
- **Eddy Duo on `eddy-ng` (`config/eddy-duo.cfg`, `config/eddy-macros.cfg`, `config/calibration.cfg`, `config/printer.cfg`):**
  - `[probe_eddy_ng btt_eddy]` configured at `x_offset: 28.7`, `y_offset: 0`, `tap_start_z: 1.6`, `tap_target_z: -0.200`.
  - Calibrated dual drive currents (`calibration_version = 7`, `calibrated_drive_currents = 16, 17`):
    - `reg_drive_current = 16`: `h_range = [0.2552, 14.9990] mm`, `rms = 0.004463`.
    - `tap_drive_current = 17`: `h_range = [0.00045, 2.1415] mm`, `rms = 0.001842`.
  - Cold paper-verified `tap_adjust_z = 0.130` and `[stepper_z] position_endstop = 206.473` (`position_max: 206.7`, `position_min: -0.2`).
  - `[bed_mesh]` updated to `horizontal_move_z: 2.0` (matching `eddy-ng` `home_trigger_height`), `speed: 40`, `mesh_min: 32, 25`, `mesh_max: 210, 205`, `probe_count: 13, 13`, `adaptive_margin: 5`; `KAMP`, `EDDY_STATUS`, `EDDY_TAP`, and `EDDY_MESH` invoke `PROBE_EDDY_NG_TAP` and `BED_MESH_CALIBRATE ... METHOD=rapid_scan`.
- **Sensorless XY & 5-Zone Z Homing (`config/motion-check.cfg`):**
  - `[tmc2209 stepper_x]` / `[tmc2209 stepper_y]` use Kalico `home_current: 0.600` vs `run_current: 0.800` with `current_change_dwell_time: 0.5`, `homing_accel: 500`, `min_home_dist: 5`, `driver_SGTHRS: 64`.
  - `[homing_override]` and `[gcode_macro _Z_ZONE_MOVE]` implement 5-zone Z homing/travel (`10 mm/s` in `0–5 mm` and `200–Zmax`, smooth `80 mm/s^2` `SET_KINEMATICS_LIMIT` ramps across `5–10 mm` and `195–200 mm`, `30 mm/s` 3x cruise across `10–195 mm`, restoring `Z_ACCEL=300` afterward).
- **Macro Rename & Kalico `LINE_PURGE` Fix (`config/tridont_macros.cfg`):**
  - Renamed `forge-x-macros.cfg` to `tridont_macros.cfg`.
  - Fixed `LINE_PURGE` so when `printer.configfile.settings.extruder.max_extrude_cross_section` is omitted by Kalico (`None` internal default until `SET_NOZZLE_DIAMETER` or explicit config), it falls back cleanly to `4.0 * nozzle_diameter^2` instead of raising Jinja `UndefinedError`. Verified live with `EXCLUDE_OBJECT_DEFINE` + `LINE_PURGE VALIDATE_ONLY=1 CHECK_PURGE=1`.

## Exclusions & Safety Notes

- Credentials, Moonraker databases, `moonraker.conf`, `.bin` firmware blobs, and timestamped pre-edit backup files (`*.pre-*`) are excluded from this Git snapshot.
- The printer service account's home folder is written as `/home/<user>` in `host/klipper.service`, this README and `firmware-build-configs/README.md` (this repository is public). Substitute the real service account before restoring the unit. The unmodified copy is in the private Drive archive.
- Do not modify `tap_adjust_z` or `position_endstop` blindly across nozzle/hotend/mount changes; re-verify cold nozzle clearance and run `EDDY_TAP` physically after hardware or bed-plate changes.
