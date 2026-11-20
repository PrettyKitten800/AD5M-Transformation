# The Moron Tridont Project — Build Log

> A FlashForge Adventurer 5M (AD5M) being turned, one stage at a time, into a Trident-like AWD printer.
> This log is the running record of what was done, when, what it changed, and what is still open.
> Detailed specs live in the linked docs; this file tells the story and tracks status.

| | |
|---|---|
| **Owner** | Matt (GitHub: PrettyKitten800) |
| **Repository** | <https://github.com/PrettyKitten800/AD5M-Transformation> |
| **Drive folder** | *1 - The Moron Tridont Project (Active Only)* (Google Drive) |
| **Printer host** | CurbyServer, `http://192.168.4.31` (Mainsail :80, Fluidd :8080) |
| **Log started** | 2026-11-20 (entries before this date reconstructed from repo history, handoffs and snapshots) |
| **Last updated** | 2026-11-20 |

**Authoritative spec order:** [AGENTS.md](AGENTS.md) → [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md) → the newest Klipper/Kalico snapshot → this log. Older handoffs (`START_HERE_AD5M.txt`, `AD5M_REBUILD_HANDOFF.txt`, `AD5M_HANDOFF_2026-11-02/`, `BUILD_SEQUENCE.md`, `TOOLHEAD_FIRST.md`, `UPGRADE_ROADMAP.md`) are history.

---

## Contents

1. [Status at a glance](#1-status-at-a-glance)
2. [Machine record: stock vs. current](#2-machine-record-stock-vs-current)
3. [Live firmware and calibration](#3-live-firmware-and-calibration)
4. [Phase tracker](#4-phase-tracker)
5. [Chronological log](#5-chronological-log)
6. [Print and test record](#6-print-and-test-record)
7. [Bill of materials](#7-bill-of-materials)
8. [Open issues and discrepancies](#8-open-issues-and-discrepancies)
9. [Next steps](#9-next-steps)
10. [Safety and change checklist](#10-safety-and-change-checklist)
11. [How to add an entry](#11-how-to-add-an-entry)
12. [References](#12-references)

---

## 1. Status at a glance

*As of 2026-11-20.*

| Area | State |
|---|---|
| **Overall phase** | Phase 3 (toolhead customization) on the stock AD5M chassis. The printer prints. |
| **Electronics** | Octopus Pro V1.1 H723 (USB-to-CAN bridge) + EBB42 V1.2.1 (CAN) + Eddy Duo (CAN): commissioned |
| **Firmware** | **Kalico** `v2026.11.00-73-gfb4e09bc` + **eddy-ng** `v0.1-188-ga09ec8e` (migrated from mainline Klipper `0cee841e3` on 2026-11-19) |
| **Extruder / hotend** | Orbiter v2.5 + LDO-36STH20-1004AHG; Bambu X1C-style hotend, 0.4 mm hardened-steel nozzle |
| **Part cooling** | Recovered Printables 1404902 shroud **R4**: printed, mounted, Z-height adjusted (2026-11-19) |
| **Materials qualified** | Sunlu ABS (tuned profile), Siraya ASA-GF (first layer only), PETG (test cube) |
| **Biggest open questions** | Bed heater wiring (see [8.1](#8-open-issues-and-discrepancies)); which carriage adapter is physically installed; Kalico snapshot not yet in Git |
| **Next milestone** | Long-print / full-bed qualification on Kalico, then the XY linear-rail gantry |

---

## 2. Machine record: stock vs. current

### 2.1 Stock FlashForge AD5M baseline (for reference)

| Item | Stock spec |
|---|---|
| Kinematics | CoreXY, direct drive |
| Build volume | 220 × 220 × 220 mm |
| Z system | Three lead screws belt-coupled to the Z stepper; moving bed, fixed-height XY gantry |
| Max travel / accel | 600 mm/s, 20,000 mm/s² (manufacturer figures) |
| Hotend | 280 °C max, quick-swap nozzle, 0.4 mm default (0.25/0.6/0.8 optional) |
| Bed | 110 °C max, flexible PEI spring steel, pressure-sensor auto-levelling |
| Positioning accuracy | XY 0.0125 mm, Z 0.0025 mm (manufacturer figures) |
| PSU | 24 V, 350 W class |
| Firmware | FlashForge's locked fork of an old Klipper |

### 2.2 Current configuration

| Subsystem | Installed hardware | Bus / pins | Status | Notes |
|---|---|---|---|---|
| Host | Raspberry Pi 5 8 GB ("CurberryPi" / CurbyServer), BTT HDMI5 touchscreen | — | Working | Intel host migration planned; see [migration handoff](klipper/2026-11-17/migration/README.md) |
| Mainboard | BTT Octopus Pro V1.1, STM32H723ZET6 | USB-to-CAN bridge, CAN PD0/PD1 @ 1 Mbps, 128 KiB bootloader, 25 MHz | Working | Replacement for a defective board; flashed 2026-11-03 |
| Drivers | 3× TMC2209 V1.3 (X, Y, Z) + 1 spare | UART | Working | Sensorless XY homing (SGTHRS 64) |
| Toolboard | BTT EBB42 V1.2.1 (original family, not Gen2) | CAN (`head`) | Working | Supersedes EBB36 |
| Probe | BTT Eddy Duo (LDC1612) | CAN (`eddy`) via eddy-ng | Working | `x_offset 28.7`, `y_offset 0`; tap + rapid-scan mesh |
| Extruder | Orbiter v2.5 + LDO-36STH20-1004AHG | EBB42 driver | Working | `rotation_distance 4.69`, `run_current 0.85` |
| Hotend | Bambu X1C-style (log: "TZ 2.0 X1C-mount"), 0.4 mm hardened steel | Heater `head:PB13`, thermistor `head:PA3` (Generic 3950) | Working | Kalico MPC control |
| Hotend fan | 3010 (Peerless DF3010B24H, 24 V 0.09 A) | `head:PA1` (heater_fan) | Working | |
| Part-cooling fan | Blower on 1404902 R4 shroud | `head:PA0` (`[fan]`) | Working | |
| Carriage adapter / housing | BambuMod-derived; Orbiter remix line R1–R8 in CAD | — | **Confirm** | See [8.2](#8-open-issues-and-discrepancies) |
| Bed | Stock AD5M DC bed (~250 W at 24 V, unmeasured), PEI steel sheet | Thermistor `PF3`; heater pin in live config `PA1` | Working | See [8.1](#8-open-issues-and-discrepancies) on bed control path |
| External bed MOSFET | ReliaBot V1.3 (25 A) | Planned on HE0/`PA0` | **Confirm** | Live config comment says direct BED-OUT |
| PSU | A-350GF-24-CX, 24 V 14.6 A (≈350 W) | — | Working | Not a Mean Well |
| XY endstops | Sensorless (TMC StallGuard); A3144 Hall sensors were on the earlier plan | — | Working | Homing order Z → rear Y → right X |
| Z endstop | Stock Z sensor | Octopus STOP2 `^PG10` | Working | Final Z from Eddy tap |
| Filament runout | Stock switch | `^!PG12` | Working | |
| Accelerometer | ADXL345 on toolhead | `head:PB12` CS | Working | |
| Lights | Enclosure LED output | `PA8` | Working | |
| Camera | USB camera via ustreamer, 1080p30 MJPEG | nginx `/webcam/` | Working | |

---

## 3. Live firmware and calibration

Source: Kalico snapshot of 2026-11-19 (Drive: `Moron_Tridont_Kalico_2026-11-19.zip` + README). Mainline values from [klipper/2026-11-19/](klipper/2026-11-19/) are shown where they differ, for history.

### 3.1 Software versions

| Component | Version |
|---|---|
| Kalico (Klipper fork) | `v2026.11.00-73-gfb4e09bc` |
| eddy-ng | `v0.1-188-ga09ec8e` |
| Previous mainline Klipper | `0cee841e31d701595b3e509a0b502f6e320f52a8` (v0.13.0-820) |
| Moonraker | `b559b9a81161f958a43c2f527b6ad96f73310d5d` |
| Katapult | `3b973a485388b4ef0f9efef46f78152e302aea8e` |
| Host OS | Debian 13 ARM64, Python 3.13.5 |

### 3.2 Motion

| Setting | Kalico (current) | Mainline 2026-11-19 (history) |
|---|---|---|
| Kinematics | `limited_corexy` | `corexy` |
| `max_velocity` | 500 | 500 |
| `max_accel` | 7500 (X 7500 / Y 5000) | 9000 |
| Z limits | `max_z_velocity 40`, `max_z_accel 300`; 5-zone Z travel macro | — |
| X range | −3.7 … 219.7 | same |
| Y range | 5 … 220 (printable front limit Y 12 for part-cooler clearance) | same |
| Z | `position_endstop 206.473`, `position_max 206.7`, `min −0.2` | `max 206.353`, `min −0.4` |
| XY rotation distance | 39.9 | same |
| Z rotation distance | 7.98 | same |
| XY current | run 0.80 A / home 0.60 A | run 0.80 A |
| Z current | 0.50 A | same |
| Input shaper | X `smooth_mzv` 52.0 Hz, Y `smooth_zvd_ei` 56.0 Hz | X `mzv` 70.8 Hz, Y `mzv` 56.8 Hz |

### 3.3 Thermal

| Setting | Value |
|---|---|
| Hotend control | Kalico **MPC**: `heater_power 48`, block heat capacity 8.828, sensor responsiveness 0.0882, ambient transfer 0.0975 |
| Hotend (previous PID) | Kp 14.032 / Ki 6.682 / Kd 7.367 |
| Hotend `max_temp` | 335 °C |
| Bed control | PID Kp 68.159 / Ki 2.283 / Kd 508.638, `max_power 0.93`, `max_temp 120` |
| Timed bed preheat | `PREHEAT TEMP= MINUTES=` (1–240 min), `CANCEL_PREHEAT`; idle timeout won't kill an active preheat |

### 3.4 Probe and mesh (eddy-ng)

| Setting | Value |
|---|---|
| Offsets | X 28.7, Y 0 (moved 6.3 mm closer to nozzle on 2026-11-18) |
| Drive currents | reg 16 (h-range 0.255–15.0 mm, rms 0.0045), tap 17 (h-range 0.0005–2.14 mm, rms 0.0018) |
| Tap | `tap_start_z 1.6`, `tap_target_z −0.2`, `tap_adjust_z 0.130` (cold paper-verified) |
| Mesh | rapid_scan, 13 × 13, `mesh_min 32,25`, `mesh_max 210,205`, `horizontal_move_z 2.0`, adaptive margin 5 |

### 3.5 Extrusion and slicer

| Setting | Value |
|---|---|
| Extruder | `rotation_distance 4.69`, 32 microsteps, E limits 120 mm/s / 3000 mm/s² |
| Pressure advance | Fallback 0.025 in config; Sunlu ABS profile sets 0.02 |
| OrcaSlicer bundle | `Moron_Tridont_04_Corrected.orca_printer` |
| Sunlu ABS baseline | 260 °C / 100 °C, 20 mm³/s, PA 0.02, flow 0.95, XY shrink 99.4 %, 45 % overhang fan |
| Process presets | 0.16 / 0.20 / 0.24 mm Sunlu ABS, 0.20 mm Sunlu ABS Voron (4 walls, 5/5 shells, 40 % gyroid), 0.16 / 0.20 / 0.24 mm ASA |
| Printable polygon | `0x12, 213.4x12, 213.4x220, 0x220` |
| G-code rules | Klipper flavour, object labels + `EXCLUDE_OBJECT_DEFINE` before `START_PRINT`, bed origin at 0,0 (not centred) |

---

## 4. Phase tracker

Legend: ✅ done · 🔄 in progress · ⏳ planned · ⛔ blocked / needs decision

| # | Phase | Status | Exit criteria | Key docs |
|---|---|---|---|---|
| 0 | Stock baseline and teardown records | ✅ | Photos, labels, stock wiring notes | [handoff](AD5M_HANDOFF_2026-11-02/) |
| 1 | Electronics swap (Pi 5, Octopus Pro, EBB, rear carrier, power harness) | ✅ | Boards mounted, harness built, firmware flashed | [BUILD_SEQUENCE.md](BUILD_SEQUENCE.md), [flashing record](outputs/flashing_2026-11-03/) |
| 2 | Commissioning (CAN, homing, heaters, probe, first prints) | ✅ | Test cube printed; first-layer test passed | [klipper/2026-11-17/](klipper/2026-11-17/) |
| 3 | Toolhead customization (EBB42 mount, Eddy placement, Orbiter v2.5, cooling) | 🔄 | One toolhead design physically fitted, documented, and long-print qualified | [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md), [outputs/INDEX.md](outputs/INDEX.md) |
| 3b | Firmware upgrade to Kalico + eddy-ng (MPC, smooth shapers, tap) | 🔄 | Snapshot committed to Git; long print passes | Drive Kalico snapshot |
| 4 | Host migration Pi 5 → Intel Linux PC | ⏳ | Staged cutover checks pass | [migration](klipper/2026-11-17/migration/README.md) |
| 5 | XY linear-rail gantry (MGN rails; BootyCallJones K1 as reference) | ⏳ | Rails installed, re-tuned shaper, dimensional test | [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md), `reference/AD5M_gantry_research/` |
| 6 | Independent triple Z + `Z_TILT_ADJUST` | ⏳ | 3 Z motors on 3 driver channels, tilt converges | [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) |
| 7 | Frame conversion to Voron Trident 300 × 300 × 300 (2020), AWD | ⏳ | Frame built, AC bed + SSR, enclosure | [FRAME_CONVERSION.md](FRAME_CONVERSION.md) |
| 8 | Toolchanger (2 tools, then 4) | ⏳ | Two-tool print, then four | [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) |

---

## 5. Chronological log

Newest entries at the bottom. "Evidence" points to the repo file or Drive item that backs the entry.

### 2026-11-01 — Toolhead-first assembly order; power plan
- Assembly order changed: build the unpowered toolhead harness first, then the rear assembly.
- Rear electronics carrier finalized at **R10** (5 mm base+posts, 167 × 172 mm). Octopus, Pi 5 and ReliaBot MOSFET mounted on it.
- Power plan: PSU pair 1 → Octopus POWER + MOTOR-POWER (split in harness connectors) + protected EBB branch; pair 2 → external bed MOSFET DC IN.
- Evidence: [TOOLHEAD_FIRST.md](TOOLHEAD_FIRST.md), [BUILD_SEQUENCE.md](BUILD_SEQUENCE.md), [DECISIONS_AND_CORRECTIONS](AD5M_HANDOFF_2026-11-02/DECISIONS_AND_CORRECTIONS.txt)

### 2026-11-02 — Bed MOSFET moved to HE0; original Octopus defective
- External MOSFET CONTROL wired to Octopus **HE0 (PA0)**, not BED-OUT (wiring R5). The CONTROL polarity was a stated assumption, not measured.
- PSU confirmed as A-350GF-24-CX (not Mean Well).
- Original Octopus Pro reported defective; replacement ordered.
- Consolidated restart handoff written.
- Evidence: [outputs/AD5M_HE0_wiring_R5/](outputs/AD5M_HE0_wiring_R5/), [AD5M_REBUILD_HANDOFF.txt](AD5M_REBUILD_HANDOFF.txt)

### 2026-11-03 — Replacement Octopus Pro flashed; long-term direction set
- Replacement confirmed as **Octopus Pro V1.1, STM32H723ZET6**. Flashed through ROM DFU from WSL: Klipper `0cee841e`, USB-to-CAN bridge, 1 Mbps, 128 KiB offset. Read-back matched; original bootloader verified unchanged; full 1 MiB backup saved.
- **Voron Trident** set as the reference architecture for the eventual machine.
- **XY linear rails** chosen as the first upgrade after printing is restored. BootyCallJones K1 gantry archived as a reference.
- Long-term goals recorded: triple independent Z, then a four-head toolchanger.
- Evidence: [outputs/flashing_2026-11-03/](outputs/flashing_2026-11-03/), [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md)

### 2026-11-06 — EBB42 V1.2.1 confirmed; extruder review
- Toolboard confirmed as **EBB42 V1.2.1** (read off the board). Supersedes all EBB36 planning.
- BambuMod housing (Printables 1574762) confirmed installed on the stock carriage mounts.
- Extruder review: keep the AD5M feeder for now; Orbiter 2.5 is the pick for an assembled replacement.
- Evidence: [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md), [extruder review](outputs/extruder_review_2026-11-06/AD5M_EXTRUDER_REVIEW.md)

### 2026-11-07 → 11-08 — Bracket iterations, hotend CAD, repo created
- Eddy Duo brackets R1 → R4 (side mount with reinforced nut channels).
- EBB42 brackets R1 → R7 (open top-hat → corridor study → sketch bridge R3–R5 → simple wedge R6 → uniform posts R7). **R5 printed and fit-checked as usable.**
- Eddy temporarily on direct USB to the Pi.
- Bambu X1 hotend STEP (Printables 533213) acquired; nominal nozzle-to-Eddy alignment model made.
- GitHub repository created and cloud workspace documented.
- Evidence: [outputs/INDEX.md](outputs/INDEX.md), `git log` 2026-11-08

### 2026-11-10 — Multi-agent rules
- Coordination rules (sync first, append-only CAD revisions, update indexes together) documented for ChatGPT/Codex, Antigravity and Claude.
- Evidence: [AGENTS.md](AGENTS.md)

### 2026-11-11 — First live commissioning and test print ✅
- Octopus Pro + EBB42 (CAN) + Eddy Duo commissioned. **First test print: `Voron_Design_Cube_v7_PETG.gcode`.**
- Rapid-scan mesh set up (`horizontal_move_z 1.5`). With the right-side Eddy mount (`x_offset 44`), the mesh showed a ~0.35 mm false drop past probe X 196 mm because the field runs off the steel plate edge. Capping `mesh_max 195, 205` cut variance from 0.506 to 0.219 mm.
- Custom toolhead housing + **inline front Eddy mount R1** designed (`x_offset 0`).
- Evidence: [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md)

### 2026-11-12 → 11-13 — Dragon Burner path and frame decision
- Dragon Burner #1406257 v11 AD5M adapter remixed with a centred rear Mode-A Eddy pocket (R1). Dragon Burner v8 STLs archived.
- Drive "Active Master Spec & Hardware Map" doc created.
- **Frame conversion locked to standard Voron Trident 300 × 300 × 300 mm, HFSB5-2020** (after briefly considering 315 mm / Euro 4040).
- Evidence: [FRAME_CONVERSION.md](FRAME_CONVERSION.md), `git log` 2026-11-12/13

### 2026-11-14 → 11-18 — BambuMod × Orbiter v2.5 adapter line
- R1: Primary (motor centred, hotend −6.335 mm) and Alternate (nozzle centred, motor +6.335 mm) remixes.
- R2–R7: restored 3010 shroud arch, smooth C2 B-spline duct, 4 blind carriage bores, captive hex-nut pockets, reinforced bosses, filleted edges, flat print pose. All CAD-verified; **none physically tested**.
- R8: live parametric FreeCAD + web workspace.
- Carriage reference photos with rulers uploaded to Drive (2026-11-15).
- Evidence: [AGENTS.md](AGENTS.md), [outputs/INDEX.md](outputs/INDEX.md)

### 2026-11-16 — First-layer qualification on ASA-GF ✅
- Siraya Tech ASA-GF, 30 × 30 × 0.20 mm, 260 °C / 105 °C, 20 mm/s. Zero CAN retransmits. Result: "Sticking, with lines joining together."
- Evidence: [klipper/2026-11-17/validation/first-layer/](klipper/2026-11-17/)

### 2026-11-17 — Config archived; host backed up; Intel migration plan
- Full Klipper config snapshot committed, including the custom `z_speed_control.py` extra.
- Moonraker, CAN, camera and nginx units backed up (no secrets).
- Intel host migration handoff written; private archive (DB, G-code, sources) put in Drive.
- Evidence: [klipper/2026-11-17/](klipper/2026-11-17/), Drive `AD5M_Intel_Migration_PRIVATE_2026-11-17.zip`

### 2026-11-18 — Eddy offset moved
- Eddy coil now 28.7 mm right of the new nozzle (6.3 mm closer than before), Y aligned.
- Fan shroud R1–R3 (recovered Printables 1404902) aligned to R8.
- Evidence: `klipper/2026-11-19/config/eddy-duo.cfg` header

### 2026-11-19 — Orbiter v2.5 live; shroud R4 fitted; ABS tuned; project renamed
- **Orbiter v2.5 + LDO 36STH20** running: `rotation_distance 4.69`, 0.85 A, E limits 120 mm/s / 3000 mm/s².
- **Fan shroud R4** printed, mounted and height-adjusted on the printer.
- Timed `PREHEAT` / `CANCEL_PREHEAT` macros added.
- Sunlu ABS profile tuned (260/100, 20 mm³/s, PA 0.02); new ABS process presets.
- Project renamed **The Moron Tridont Project**. Mainline snapshot committed.
- Evidence: [klipper/2026-11-19/](klipper/2026-11-19/), commit `4ae7c84`

### 2026-11-19 (late) — Migrated to Kalico + eddy-ng
- Moved from mainline Klipper to **Kalico** with **eddy-ng**.
- Changes: `limited_corexy`; smooth input shapers (X smooth_mzv 52 Hz, Y smooth_zvd_ei 56 Hz); **MPC** hotend control; eddy-ng dual drive currents and tap (`tap_adjust_z 0.130`); separate home current; 5-zone Z homing/travel; `forge-x-macros.cfg` renamed `tridont_macros.cfg`; `LINE_PURGE` fixed for Kalico's `max_extrude_cross_section` default; 17 legacy mesh blocks removed; telemetry off.
- Evidence: Drive `Moron_Tridont_Kalico_2026-11-19.zip` and README. **Not yet committed to the repo.**

### 2026-11-20 — Build log started
- This file created to track progress, the BOM, test results and open issues in one place.

---

## 6. Print and test record

| Date | File / test | Material | Nozzle / bed | Firmware | Result | Notes |
|---|---|---|---|---|---|---|
| 2026-11-11 | `Voron_Design_Cube_v7_PETG.gcode` | PETG | — | Klipper mainline | ✅ Completed | First print on the new electronics |
| 2026-11-11 | Rapid-scan mesh, side Eddy | — | — | Klipper mainline | ⚠️ Edge roll-off past X 196 | Variance 0.506 → 0.219 mm after capping |
| 2026-11-16 | First layer 30 × 30 × 0.20 mm | Siraya ASA-GF | 260 / 105 °C | Klipper mainline | ✅ Adhered, lines joined | Small test, not full bed |
| 2026-11-19 | Sunlu ABS tuning | Sunlu ABS | 260 / 100 °C | Klipper mainline | ✅ Profile saved | 20 mm³/s, PA 0.02, flow 0.95 |
| 2026-11-19 | `LINE_PURGE VALIDATE_ONLY=1` | — | — | Kalico | ✅ | Verifies purge macro fix |
| *next* | Full-bed first layer | ABS | 260 / 100 °C | Kalico | | Checks mesh to X 210 |
| *next* | Long print (≥ 4 h) | ABS / ASA | | Kalico | | Thermal soak, CAN stability, MPC |
| *next* | Dimensional cube / shrink check | ABS | | Kalico | | Validates 99.4 % shrink |

---

## 7. Bill of materials

Costs are left blank for you to fill in.

### 7.1 Installed (Phases 1–3)

| Part | Qty | Status | Cost | Notes |
|---|---:|---|---:|---|
| FlashForge Adventurer 5M (base) | 1 | Installed | | Donor chassis, bed, XY/Z mechanics, PSU |
| Raspberry Pi 5 8 GB (Vemico kit, active cooler) | 1 | Installed | | Host |
| BTT Octopus Pro V1.1 H723 | 1 | Installed | | Replacement unit |
| BTT TMC2209 V1.3 | 4 | 3 installed + 1 spare | | |
| BTT EBB42 V1.2.1 CAN | 1 | Installed | | |
| BTT EBB36 V1.2.1 (no MAX31865) | 1 | Spare / retired | | Superseded |
| BTT Eddy Duo | 1 | Installed | | CAN, eddy-ng |
| BTT HDMI5 touchscreen | 1 | Installed | | |
| ReliaBot external bed MOSFET V1.3 | 1 | Installed? | | See 8.1 |
| Orbiter v2.5 + LDO-36STH20-1004AHG | 1 | Installed | | |
| Bambu X1C-style hotend, 0.4 mm hardened nozzle | 1 | Installed | | |
| Peerless DF3010B24H 3010 fan | 1 | Installed | | Hotend fan |
| HXH HBB0524VD blower (stock) | 1 | Installed? | | Confirm vs. Dragon Burner 4010s |
| ADXL345 | 1 | Installed | | |
| USB camera | 1 | Installed | | |
| 4-core CAN cable (≈18 AWG) | — | Installed | | |
| 12 / 16 AWG stranded copper, fork lugs, JST/Molex | — | Installed | | |
| Printed: rear carrier R10, EBB42 bracket, Eddy mount, R4 shroud, adapter | — | Installed | | Material: ABS / ASA |
| Heat-set inserts M3 | — | | | |

### 7.2 On order / incoming

| Part | Qty | Status | Notes |
|---|---:|---|---|
| 2× 4010 24 V blowers (Dragon Burner) | 2 | ? | Listed as incoming in the Nov 12 Drive spec |
| *(add here)* | | | |

### 7.3 Planned: Phases 5–7 (Trident 300 × 300 × 300)

| Part | Qty | Notes |
|---|---:|---|
| Misumi HFSB5-2020 extrusions (19 pieces, 8,152 mm) | 19 | Cut list in [FRAME_CONVERSION.md](FRAME_CONVERSION.md) |
| MGN12H rail 350 mm (X) | 1 | |
| MGN9H rail 350 mm (2× Y, 3× Z) | 5 | |
| NEMA17 TR8×4 350 mm integrated leadscrew steppers | 3 | Triple Z |
| LL-2GT-6 belt, 1,890 mm | 2 | Recalculate for 9 mm belts / AWD |
| Additional TMC2209 | 2–5 | Triple Z + AWD |
| AWD motors | 2 | |
| 12" × 12" MIC6 plate 5/16" + PEI | 1 | |
| 250 × 250 mm 450 W AC silicone heater + SSR + 150 °C thermal fuse | 1 | Stock PSU can't run a 300-class bed |
| Enclosure: 2× 419 × 419 coroplast, 432 × 522 back, 433 × 433 top, 2× 433 × 523 sides, 2× 216.5 × 523 doors | — | |
| DIN rail 420 mm | 2 | |
| 5-series M3/M5 T-nuts | — | 6 mm-slot nuts don't fit |

---

## 8. Open issues and discrepancies

Found while reconciling the repo, Drive and live config on 2026-11-20. Each needs a physical check or a decision; nothing here was changed on the printer.

| # | Issue | Evidence | Why it matters | Suggested action |
|---|---|---|---|---|
| 8.1 | **Bed heater path.** The wiring plan (R5) and the Nov 12 Drive master spec say the external MOSFET is driven from **HE0 / PA0** and BED-OUT is unused. The live config uses `heater_pin: PA1` (BED-OUT), with the comment "Direct Octopus Pro BED-OUT checkout at reduced duty cycle", and `max_power 0.93`. | `bed-heater-check.cfg`; `outputs/AD5M_HE0_wiring_R5/`; Drive master spec | The stock bed is ~250 W, about 10.4 A at 24 V. BTT rates BED-OUT at 10 A continuous, which is why the external MOSFET was kept. | Trace the bed wires. If the bed runs straight off BED-OUT, decide whether to go back to the MOSFET or keep the power cap, and record the measured bed resistance. Update the wiring doc to match. |
| 8.2 | **Which carriage adapter is installed?** The Orbiter is live and the R4 shroud is mounted "on R8", yet R1–R8 adapters are all marked "untested physically". Separately, the Drive spec describes a Dragon Burner v8 transition. | AGENTS.md, CURRENT_TOOLHEAD_SPEC.md, Drive spec | The X offset (−6.335 mm Primary vs. 0 Alternate) and Eddy offsets depend on it. | Record the installed adapter and revision. Mark it physically tested in AGENTS.md, README, INDEX and the spec in one commit. |
| 8.3 | **Kalico snapshot not in Git.** The repo's newest snapshot is mainline Klipper; the live printer runs Kalico. | Drive `Moron_Tridont_Kalico_2026-11-19*` | Other agents read `klipper/2026-11-19/` as current and will give mainline advice. | Commit as `klipper/2026-11-19-kalico/` (sanitized zip only, not the PRIVATE one) and update README/AGENTS. |
| 8.4 | **Eddy bus and offset are described differently in different places.** Banners and the Drive spec say USB; the live config uses CAN. Offsets: 44 (side mount), 35 (11-17 README), 28.7 (live). | Header banners on old docs; eddy-duo.cfg | Stale guidance. | Update the banners in BUILD_SEQUENCE / UPGRADE_ROADMAP / TOOLHEAD_FIRST and AGENTS line 3 to "Eddy on CAN, x_offset 28.7". |
| 8.5 | **Extruder baseline text is stale.** CURRENT_TOOLHEAD_SPEC still says "retain the existing AD5M feeder and motor". | CURRENT_TOOLHEAD_SPEC.md §top | Contradicts the installed Orbiter. | Add a dated correction line. |
| 8.6 | **Electrical verification deferred.** Continuity and polarity checks were never recorded; MOSFET CONTROL polarity is an assumption; DC branch fuses aren't sized. | Handoff Nov 2 | Safety. | Use a multimeter and record results in this log. |
| 8.7 | **Blower PWM interface** for the 4-wire HXH blower was never formally resolved. | DECISIONS item 9 | Fan control / tach. | Record the actual wiring now in use. |
| 8.8 | **PSU budget for future phases.** 350 W won't cover a 300 mm bed or several hotends. | FRAME_CONVERSION, UPGRADE_ROADMAP | Phase 7/8 planning. | Write the load budget before buying the bed. |
| 8.9 | **Drive spec is out of date** (synced Nov 12). | Drive master spec | Same stale-guidance problem as 8.3–8.4. | Re-sync after 8.1–8.4 are settled. |

---

## 9. Next steps

In priority order:

1. **Settle 8.1 (bed heater path)**: physical trace and a decision.
2. **Commit the Kalico snapshot (8.3)** and record the installed adapter (8.2).
3. **Qualify on Kalico:** full-bed first layer, then a ≥ 4 h ABS print. Log both in §6.
4. **Re-run calibrations after the hardware settles:** shaper (accelerometer), MPC, PA per filament, `EDDY_TAP`. Log the values in §3.
5. **Freeze the toolhead (end of Phase 3):** pick one adapter, print it, fit it, update every index, and tag `v0.3-toolhead` in Git.
6. **Phase 4:** Intel host cutover per the migration README, keeping the Pi as a fallback.
7. **Phase 5 prep:** photograph and trace both belt paths; measure pulley centres, heights and clamp heights before touching the gantry.

---

## 10. Safety and change checklist

Run through this before any hardware or config change:

- [ ] `git fetch && git pull --rebase` before editing (multi-agent rule)
- [ ] Back up config, or copy it to `*.pre-<change>-<date>`
- [ ] Power off and unplug before touching wiring, drivers or connectors
- [ ] After a nozzle, hotend, shroud or probe-mount change: cold nozzle clearance check, `EDDY_TAP`, verify `tap_adjust_z`
- [ ] After restoring a config: check endstops, supervised cold travel, then heaters one at a time
- [ ] New CAD goes into a new `outputs/<part>_R<n+1>/` folder; never overwrite
- [ ] A CAD/mesh check is not a physical fit test. Say which one you did.
- [ ] Never commit credentials, `moonraker.conf`, databases, `*_PRIVATE_*` archives or flash read-backs
- [ ] Update this log in the same commit as the change

---

## 11. How to add an entry

Copy this to the bottom of §5:

```markdown
### YYYY-MM-DD — <short title> (✅ / 🔄 / ⚠️)
- **What changed:** <hardware / config / CAD, with exact values>
- **Why:** <problem or goal>
- **Result:** <what happened on the printer; measured numbers>
- **Physically tested?** yes / no / CAD only
- **Evidence:** <repo path, commit, Drive file, photo>
- **Follow-ups:** <new open items → add to §8>
```

Also update §1 (status), §4 (phase tracker), §6 (if anything was printed) and §7 (if parts changed).

---

## 12. References

**In this repo:** [README.md](README.md) · [AGENTS.md](AGENTS.md) · [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md) · [outputs/INDEX.md](outputs/INDEX.md) · [FRAME_CONVERSION.md](FRAME_CONVERSION.md) · [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) · [klipper/2026-11-19/](klipper/2026-11-19/) · [klipper/2026-11-17/](klipper/2026-11-17/) · `reference/Voron_Trident/START_HERE.md`

**Third-party designs used (keep their licenses):**
- BambuMod for FF Adventurer 5M — Kirill_Wawe, Printables 1574762 (CC BY-NC-SA 4.0)
- Orbiter v2.0/2.5 mockup — dr. Lorincz Robert (CC BY-NC-SA 4.0)
- AD5M Dragon Burner adapter v11 — Printables 1406257
- AD5M lightweight fan duct — Printables 1404902
- Bambu X1/P1 hotend CAD — Jorge (jorge_rui), Printables 533213
- Voron Trident — VoronDesign (GPL-3.0)
- BootyCallJones K1 gantry — reference only

**Firmware and hardware docs:** [Kalico](https://github.com/KalicoCrew/kalico) · [eddy-ng](https://github.com/vvuk/eddy-ng) · [Klipper CAN bus](https://www.klipper3d.org/CANBUS.html) · [BTT Octopus Pro](https://global.bttwiki.com/Octopus%20Pro.html) · [FlashForge AD5M wiki](https://wiki.flashforge.com/en/adventurer-series/manual/intro-ad5m)
