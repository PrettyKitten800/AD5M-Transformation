# The Moron Tridont Project — Current Toolhead Specification

Updated November 20, 2026, from the user's confirmation of the installed hardware and the [2026-11-19 Kalico snapshot](klipper/2026-11-19-kalico/).

This page records **what is physically on the printer now**. When hardware changes, edit the table below rather than appending dated sections. The design reasoning and per-revision notes from November 6–19 are kept in [`docs/history/TOOLHEAD_SPEC_JOURNAL_2026-11.md`](docs/history/TOOLHEAD_SPEC_JOURNAL_2026-11.md). Where the journal or any older handoff disagrees with this page, this page wins.

## On the printer now

| Subsystem | Installed | Evidence |
| --- | --- | --- |
| Toolhead housing | **BambuMod × Orbiter v2.5 remix `R8`**: [`outputs/BambuMod_Orbiter25_Remix_R8/`](outputs/BambuMod_Orbiter25_Remix_R8/) (`BambuMod_Orbiter25_R8_Live.step` / `.stl`, builder `scripts/cad/r8_live_builder.py`). Derived from Kirill_Wawe's BambuMod (Printables 1574762), CC BY-NC-SA 4.0. | User, 2026-11-20 |
| Part-cooling shroud | **Recovered Printables `1404902` shroud `R4`**: [`outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R4/`](outputs/BambuMod_Orbiter25_R8_FanDuct_1404902_R4/) (`Fan_Shroud_Recovered_PrintPose_R4.stl`); Z-height adjusted on the printer | User, 2026-11-19 and 2026-11-20 |
| Extruder | **Orbiter v2.5 + LDO-36STH20-1004AHG** on the EBB42 driver: `rotation_distance: 4.69`, `run_current: 0.85`, 120 mm/s / 3000 mm/s² extrude-only limits. 4.69 is Orbiter Projects' published starting value and has **not** been calibrated on this printer; the user chose to keep it (2026-11-20) because the OrcaSlicer flow ratio (0.95 for Sunlu ABS) was tuned on top of it. Changing it means retuning flow ratio: new flow = 0.95 × new value ÷ 4.69. | `config/extruder.cfg`; user, 2026-11-20 |
| Hotend | **TZ 2.0 clone** (Bambu X1C-style mount), 0.4 mm nozzle, `Generic 3950` thermistor, heater on EBB42 `PB13`, Kalico MPC control (`heater_power: 48`) | User, 2026-11-20; `config/extruder.cfg` |
| Hotend position | **Nozzle sits 6.335 mm right of the toolhead centerline** so the Orbiter v2.5 motor can stay centered (`R8` datum `X_fil = -6.335`, `X_mot = 0`). Shifted on 2026-11-18. | User, 2026-11-20; `R2`–`R8` design notes |
| Travel limits | X `-3.7 .. 219.7` (endstop `219.7`), both moved +6.3 mm from `-10 .. 213.4` to follow the nozzle shift; Y `5 .. 220` (user-measured front limit Y5). OrcaSlicer printable area matches: `0x5, 219.7x5, 219.7x220, 0x220`. | `config/motion-check.cfg`; `Moron_Tridont_Printer_04.json` |
| Toolboard | **BTT EBB42 V1.2.1** (original family, not Gen2), STM32G0B1, CAN 1 Mbps, MCU name `head` | `config/printer.cfg` |
| Mainboard | **BTT Octopus Pro V1.1** (STM32H723), Kalico USB-to-CAN bridge on `can0` at 1 Mbps | `config/printer.cfg`, `firmware-build-configs/README.md` |
| Bed probe | **BTT Eddy Duo on CAN** (MCU name `eddy`), eddy-ng `[probe_eddy_ng btt_eddy]`, `x_offset: 28.7`, `y_offset: 0` (coil 28.7 mm right of the nozzle) | `config/eddy-duo.cfg` |
| Firmware | **Kalico** `v2026.11.00-73-gfb4e09bc` + **eddy-ng** `v0.1-188-ga09ec8e` on all three MCUs; `limited_corexy` kinematics; replaced mainline Klipper `0cee841e3` on 2026-11-19 | [`klipper/2026-11-19-kalico/`](klipper/2026-11-19-kalico/) |
| Host | **Intel Linux PC** (`CurbyServer`); the Raspberry Pi 5 is retired | User, 2026-11-20 |
| Bed heater | External ReliaBot MOSFET driven from Octopus `HE0` (`PA0`); bed thermistor on `TB` (`PF3`) | [`outputs/AD5M_HE0_wiring_R5/`](outputs/AD5M_HE0_wiring_R5/) |
| Slicer | OrcaSlicer bundle `Moron_Tridont_04_Corrected.orca_printer` (Sunlu ABS 260 °C / 100 °C, 20 mm³/s, PA 0.02) | [`klipper/2026-11-19/config/slicer-presets/`](klipper/2026-11-19/config/slicer-presets/) |

All `config/` paths above are inside [`klipper/2026-11-19-kalico/`](klipper/2026-11-19-kalico/).

## Not yet recorded

- **Which printed part holds the Eddy Duo:** the mounting itself has not moved since the 2026-11-11 remount (board rotated 180°, long end toward the nozzle, coil 35 mm right of the old nozzle). The current `x_offset: 28.7` is that same position measured from the shifted nozzle: 35 − 6.3 = 28.7. The config does not name the bracket, so it is not tied to a design in `outputs/`.
- **EBB42 bracket on `R8`:** the `R8` CAD was checked against the EBB42 `R7` short-bridge reference, but which bracket is physically mounted is not recorded.
- **Hotend geometry in CAD:** every clearance check from `R1` to `R8` used the original Bambu X1/P1 hotend STEP in [`reference/Bambu_X1_hotend_CAD/`](reference/Bambu_X1_hotend_CAD/). No TZ 2.0 clone model is in the repository, so treat hotend clearances as nominal.

## Replaced or dropped

These are kept in the repository as history only. Do not design against them or restore them without a new user decision.

- **Dragon Burner v8 path: dropped** (user, 2026-11-20). Kept for reference: `outputs/Dragon_Burner_AD5M_Eddy_Adapter_R1/`, `outputs/Dragon_Burner_AD5M_Slim_15mm_R1/`, `outputs/Dragon_Burner_AD5M_Slim_20mm_R1/`, `reference/Dragon_Burner_v8_STLs/`, `reference/AD5M_Dragon_Burner_Adapter_1406257/`, and the `scripts/cad/*dragon_burner*` builders.
- **Original BambuMod housing (Printables 1574762):** replaced on the printer by the `R8` remix. [`reference/BambuMod/`](reference/BambuMod/) remains the source geometry and license record.
- **Stock AD5M feeder and motor:** replaced by the Orbiter v2.5 + LDO.
- **Bambu X1C hotend** named in earlier records: the installed hotend is a TZ 2.0 clone.
- **Eddy Duo over USB:** moved to CAN on 2026-11-15 (see the `eddy-duo.cfg.pre-can-20261115-225700` backup in `klipper/2026-11-17/config/`).
- **Raspberry Pi 5 host:** replaced by the Intel host.
- **Mainline Klipper:** replaced by Kalico + eddy-ng.
- **EBB36 V1.2.1:** assembled and flashed in early November, then replaced by the EBB42 V1.2.1. **EBB42 Gen2 and Manta M8P V2:** considered, not used in this build. Their notes are history.

## Standing rules

- A CAD or mesh check is not a physical fit test. Record physical results only when the user reports them.
- After any nozzle, hotend, probe-mount or bed-plate change, re-verify cold nozzle clearance and run `EDDY_TAP` before printing. Do not carry `tap_adjust_z` or `position_endstop` across hardware changes blindly.
- New geometry goes in a new `outputs/<part>_R<n+1>/` folder (see [`AGENTS.md`](AGENTS.md)); the current design list is [`outputs/INDEX.md`](outputs/INDEX.md).
- Long-term direction is unchanged: XY linear rails first, four interchangeable toolheads later; frame plan in [`docs/plans/FRAME_CONVERSION.md`](docs/plans/FRAME_CONVERSION.md).
