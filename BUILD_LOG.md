# The Moron Tridont Project — Build Log

> A FlashForge Adventurer 5M (AD5M) being turned, one stage at a time, into a Trident-like AWD printer.
> This log is the running record of what was done, when, what it changed, and what is still open.
> What is physically installed *right now* is defined by [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md); this file tells the story and tracks status around it.

| | |
|---|---|
| **Owner** | Matt (GitHub: PrettyKitten800) |
| **Repository** | <https://github.com/PrettyKitten800/AD5M-Transformation> |
| **Drive folder** | *3D Printing → 1 - The Moron Tridont Project* (layout in [README.md](README.md#github-and-google-drive)) |
| **Local workstation** | `C:\Users\PK800\Documents\3D Printing\1 - The Moron Tridont Project\` holding `AD5M-Transformation\` (this repo), `Google Drive mirror\` and `Archive\` |
| **Printer host** | CurbyServer (Intel Linux PC), `http://192.168.4.31` (Mainsail :80, Fluidd :8080) |
| **Log started** | 2026-11-20 (earlier entries reconstructed from repo history, handoffs, snapshots and the local working copy) |
| **Last updated** | 2026-11-25 |

**Authoritative order:** [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md) and [AGENTS.md](AGENTS.md) → newest `klipper/` snapshot → this log. Everything in [docs/history/](docs/history/) is superseded history.

---

## Contents

1. [Status at a glance](#1-status-at-a-glance)
2. [Machine record: stock vs. current](#2-machine-record-stock-vs-current)
3. [Live firmware and calibration](#3-live-firmware-and-calibration)
4. [Phase tracker](#4-phase-tracker)
5. [Chronological log](#5-chronological-log)
6. [Print and test record](#6-print-and-test-record)
7. [Bill of materials](#7-bill-of-materials)
8. [Open issues](#8-open-issues)
9. [Next steps](#9-next-steps)
10. [Safety and change checklist](#10-safety-and-change-checklist)
11. [How to add an entry](#11-how-to-add-an-entry)
12. [References](#12-references)

---

## 1. Status at a glance

*As of 2026-11-20.*

| Area | State |
|---|---|
| **Overall phase** | Phase 3 (toolhead) on the stock AD5M chassis. The printer prints. |
| **Electronics** | Octopus Pro V1.1 H723 (USB-to-CAN bridge) + EBB42 V1.2.1 (CAN) + Eddy Duo (CAN): commissioned |
| **Host** | Intel Linux PC (CurbyServer); Raspberry Pi 5 retired |
| **Firmware** | **Kalico** `v2026.11.00-73-gfb4e09bc` + **eddy-ng** `v0.1-188-ga09ec8e` (from mainline Klipper on 2026-11-19) |
| **Toolhead** | BambuMod × Orbiter v2.5 housing **R8**, fan shroud **R4**, Orbiter v2.5 + LDO 36STH20, TZ 2.0 clone hotend (nozzle 6.335 mm right of centre), Eddy Duo on side mount **R4** |
| **Materials qualified** | Sunlu ABS (tuned profile), Siraya ASA-GF (first layer only), PETG (test cube) |
| **Biggest open questions** | Bed on-current unmeasured (BED-OUT at its 10 A rating); which EBB42 bracket is mounted |
| **Next milestone** | Full-bed and long-print qualification on Kalico, then the XY linear-rail gantry |

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

Mirrors the table in [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md); if they disagree, that page wins.

| Subsystem | Installed hardware | Bus / pins | Notes |
|---|---|---|---|
| Host | Intel Linux PC "CurbyServer" | — | Pi 5 retired; migration plan in [klipper/2026-11-17/migration/](klipper/2026-11-17/migration/README.md) |
| Screen | BTT HDMI5 | — | |
| Mainboard | BTT Octopus Pro V1.1, STM32H723ZET6 | Kalico USB-to-CAN bridge, `can0` 1 Mbps | Replacement for a defective board; flashed 2026-11-03 |
| Drivers | 3× TMC2209 V1.3 (X, Y, Z) + 1 spare | UART | Sensorless XY homing (SGTHRS 64) |
| Toolboard | BTT EBB42 V1.2.1 (original family, not Gen2), STM32G0B1 | CAN, MCU `head` | Bracket on R8 not recorded |
| Probe | BTT Eddy Duo (LDC1612) | CAN, MCU `eddy`, eddy-ng | `x_offset 28.7`, `y_offset 0` |
| Probe mount | Eddy Duo adjustable side mount **R4** | — | Board rotated 180° on 2026-11-11 |
| Housing | BambuMod × Orbiter v2.5 remix **R8** | — | CC BY-NC-SA 4.0, from Printables 1574762 |
| Part-cooling shroud | Recovered Printables 1404902 shroud **R4** | Fan on `head:PA0` | Z-height adjusted on the printer |
| Extruder | Orbiter v2.5 + LDO-36STH20-1004AHG | EBB42 driver | `rotation_distance 4.69`, verified by 50 mm test |
| Hotend | TZ 2.0 clone (Bambu X1C-style mount), 0.4 mm nozzle | Heater `head:PB13`, thermistor `head:PA3` (Generic 3950) | Nozzle 6.335 mm right of toolhead centreline; MPC |
| Hotend fan | 3010 (Peerless DF3010B24H, 24 V 0.09 A) | `head:PA1` (heater_fan) | |
| Bed | Stock AD5M DC bed (~250 W at 24 V, unmeasured), PEI steel sheet | Heater **direct on BED-OUT `PA1`**, thermistor `PF3` | `max_power 0.93`; ReliaBot MOSFET plan not installed |
| PSU | A-350GF-24-CX, 24 V 14.6 A (≈350 W) | — | Not a Mean Well |
| XY endstops | Sensorless (TMC StallGuard) | virtual endstops | Homing order Z → rear Y → right X |
| Z endstop | Stock Z sensor | Octopus STOP2 `^PG10` | Final Z from Eddy tap |
| Filament runout | Stock switch | `^!PG12` | |
| Accelerometer | ADXL345 on toolhead | `head:PB12` CS | |
| Lights | Enclosure LED output | `PA8` | |
| Camera | USB camera via ustreamer, 1080p30 MJPEG | nginx `/webcam/` | |

---

## 3. Live firmware and calibration

Source: [klipper/2026-11-19-kalico/](klipper/2026-11-19-kalico/). Mainline values from [klipper/2026-11-19/](klipper/2026-11-19/) are shown where they differ, for history.

### 3.1 Software versions

| Component | Version |
|---|---|
| Kalico (Klipper fork) | `v2026.11.00-73-gfb4e09bc` |
| eddy-ng | `v0.1-188-ga09ec8e` |
| Previous mainline Klipper | `0cee841e31d701595b3e509a0b502f6e320f52a8` (v0.13.0-820) |
| Moonraker / Katapult (Pi baseline) | `b559b9a8…` / `3b973a48…` (see migration inventory) |

### 3.2 Motion

| Setting | Kalico (current) | Mainline 2026-11-19 (history) |
|---|---|---|
| Kinematics | `limited_corexy` | `corexy` |
| `max_velocity` | 500 | 500 |
| `max_accel` | 7500 (X 7500 / Y 5000) | 9000 |
| Z limits | `max_z_velocity 40`, `max_z_accel 300`; 5-zone Z travel macro | — |
| X range | −3.7 … 219.7 (moved +6.3 mm on 2026-11-18 with the nozzle) | same |
| Y range | 5 … 220 (user-measured front limit) | same |
| Z | `position_endstop 206.473`, `position_max 206.7`, `min −0.2` | `max 206.353`, `min −0.4` |
| XY / Z rotation distance | 39.9 / 7.98 | same |
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
| Offsets | X 28.7, Y 0 (44 → 35 after the 180° board flip on 11-11 → 28.7 after the nozzle shift on 11-18) |
| Drive currents | reg 16 (h-range 0.255–15.0 mm, rms 0.0045), tap 17 (h-range 0.0005–2.14 mm, rms 0.0018) |
| Tap | `tap_start_z 1.6`, `tap_target_z −0.2`, `tap_adjust_z 0.130` (cold paper-verified) |
| Mesh | rapid_scan, 13 × 13, `mesh_min 32,25`, `mesh_max 210,205`, `horizontal_move_z 2.0`, adaptive margin 5 |

### 3.5 Extrusion and slicer

| Setting | Value |
|---|---|
| Extruder | `rotation_distance 4.69` (verified: 50 mm requested = 50 mm measured), 32 microsteps, E limits 120 mm/s / 3000 mm/s² |
| Pressure advance | Fallback 0.025 in config; Sunlu ABS profile sets 0.02 |
| OrcaSlicer bundle | `Moron_Tridont_04_Corrected.orca_printer` |
| Sunlu ABS baseline | 260 °C / 100 °C, 20 mm³/s, PA 0.02, flow 0.95, XY shrink 99.4 %, 45 % overhang fan |
| Flow rule | If `rotation_distance` changes: new flow = 0.95 × new value ÷ 4.69 |
| Process presets | 0.16 / 0.20 / 0.24 mm Sunlu ABS, 0.20 mm Sunlu ABS Voron (4 walls, 5/5 shells, 40 % gyroid), 0.16 / 0.20 / 0.24 mm ASA |
| Printable area | `0x5, 219.7x5, 219.7x220, 0x220` |
| G-code rules | Klipper flavour, object labels + `EXCLUDE_OBJECT_DEFINE` before `START_PRINT`, bed origin at 0,0 (not centred) |

---

## 4. Phase tracker

Legend: ✅ done · 🔄 in progress · ⏳ planned

| # | Phase | Status | Exit criteria | Key docs |
|---|---|---|---|---|
| 0 | Stock baseline and teardown records | ✅ | Photos, labels, stock wiring notes | [Nov 2 handoff](docs/history/AD5M_HANDOFF_2026-11-02/) |
| 1 | Electronics swap (Octopus Pro, EBB, rear carrier, power harness) | ✅ | Boards mounted, harness built, firmware flashed | [build sequence](docs/history/BUILD_SEQUENCE.md), [flashing record](outputs/flashing_2026-11-03/) |
| 2 | Commissioning (CAN, homing, heaters, probe, first prints) | ✅ | Test cube printed; first-layer test passed | [klipper/2026-11-17/](klipper/2026-11-17/) |
| 3 | Toolhead (Orbiter v2.5, R8 housing, cooling, Eddy placement, EBB42 mount) | 🔄 | Installed toolhead documented and long-print qualified | [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md), [outputs/INDEX.md](outputs/INDEX.md) |
| 3b | Kalico + eddy-ng (MPC, smooth shapers, tap) | 🔄 | Snapshot in Git ✅; long print passes | [klipper/2026-11-19-kalico/](klipper/2026-11-19-kalico/) |
| 4 | Host migration Pi 5 → Intel Linux PC | ✅ | Printer running on the Intel host | [migration](klipper/2026-11-17/migration/README.md) |
| 5 | XY linear-rail gantry (`3× MGN12H 300 mm` miniature Voron Trident R1) | 🔄 | CAD + `Z = 0` print-pose STLs verified ✅; sourcing motion BOM, printing & installing, re-tuning shaper | [GANTRY_SPEC](docs/plans/AD5M_MGN12_GANTRY_SPEC.md), [Gantry R1](outputs/AD5M_MGN12_Gantry_R1/) |
| 6 | Independent triple Z + `Z_TILT_ADJUST` | ⏳ | 3 Z motors on 3 driver channels, tilt converges | [roadmap](docs/plans/UPGRADE_ROADMAP.md) |
| 7 | Frame conversion to Voron Trident 300 × 300 × 300 (2020), AWD | ⏳ | Frame built, AC bed + SSR, enclosure | [frame plan](docs/plans/FRAME_CONVERSION.md) |
| 8 | Toolchanger (2 tools, then 4) | ⏳ | Two-tool print, then four | [roadmap](docs/plans/UPGRADE_ROADMAP.md) |

---

## 5. Chronological log

Newest entries at the bottom. "Evidence" points to the repo file, Drive item or local file that backs the entry.

### 2026-11-01 — Toolhead-first assembly order; power plan
- Assembly order changed: build the unpowered toolhead harness first, then the rear assembly.
- Rear electronics carrier finalized at **R10** (5 mm base+posts, 167 × 172 mm). Octopus, Pi 5 and ReliaBot MOSFET mounted on it.
- Power plan: PSU pair 1 → Octopus POWER + MOTOR-POWER (split in harness connectors) + protected EBB branch; pair 2 → external bed MOSFET DC IN.
- Evidence: [toolhead-first plan](docs/history/TOOLHEAD_FIRST.md), [build sequence](docs/history/BUILD_SEQUENCE.md), [decisions](docs/history/AD5M_HANDOFF_2026-11-02/DECISIONS_AND_CORRECTIONS.txt)

### 2026-11-02 — Bed MOSFET plan moved to HE0; original Octopus defective
- Wiring plan R5: external MOSFET CONTROL on Octopus **HE0 (PA0)**, BED-OUT unused. *Later superseded: the bed was finally wired straight to BED-OUT (see 2026-11-20).*
- PSU confirmed as A-350GF-24-CX (not Mean Well).
- Original Octopus Pro reported defective; replacement ordered.
- Evidence: [outputs/AD5M_HE0_wiring_R5/](outputs/AD5M_HE0_wiring_R5/), [rebuild handoff](docs/history/AD5M_REBUILD_HANDOFF.txt)

### 2026-11-03 — Replacement Octopus Pro flashed; long-term direction set
- Replacement confirmed as **Octopus Pro V1.1, STM32H723ZET6**. Flashed through ROM DFU from WSL: Klipper `0cee841e`, USB-to-CAN bridge, 1 Mbps, 128 KiB offset. Read-back matched; original bootloader verified unchanged; full 1 MiB backup saved.
- **Voron Trident** set as the reference architecture. **XY linear rails** chosen as the first upgrade after printing is restored. Triple Z, then a four-head toolchanger, are the long-term goals.
- Evidence: [outputs/flashing_2026-11-03/](outputs/flashing_2026-11-03/), [roadmap](docs/plans/UPGRADE_ROADMAP.md)

### 2026-11-06 — EBB42 V1.2.1 confirmed; extruder review
- Toolboard confirmed as **EBB42 V1.2.1** (read off the board). EBB36 retired.
- BambuMod housing (Printables 1574762) installed on the stock carriage mounts.
- Extruder review: keep the AD5M feeder for now; Orbiter 2.5 is the pick for an assembled replacement.
- Evidence: [design journal](docs/history/TOOLHEAD_SPEC_JOURNAL_2026-11.md), [extruder review](outputs/extruder_review_2026-11-06/AD5M_EXTRUDER_REVIEW.md)

### 2026-11-07 → 11-08 — Bracket iterations, hotend CAD, repo created
- Eddy Duo brackets R1 → R4 (side mount with reinforced nut channels).
- EBB42 brackets R1 → R7. **R5 printed and fit-checked as usable.**
- Bambu X1 hotend STEP (Printables 533213) acquired.
- GitHub repository created.
- Evidence: [outputs/INDEX.md](outputs/INDEX.md), `git log` 2026-11-08

### 2026-11-11 — First live commissioning and test print ✅; inline Eddy R1 rejected
- Octopus Pro + EBB42 (CAN) + Eddy Duo commissioned. **First test print: `Voron_Design_Cube_v7_PETG.gcode`.**
- Rapid-scan mesh with the side Eddy (`x_offset 44`) showed a ~0.35 mm false drop past probe X 196 mm (field runs off the steel plate). Capping `mesh_max 195, 205` cut variance from 0.506 to 0.219 mm.
- Eddy board rotated 180° on the R4 side mount: coil moved from 44 to 35 mm right of the nozzle.
- Custom housing + **inline front Eddy mount R1** designed (`x_offset 0`), then **rejected by the user**: it only works without the part-cooling fan. Rule recorded: inline alignment must not displace the blower and duct.
- Fit feedback on the drilling helper: the Eddy wraparound locator collides with gantry rods/belts that are missing from the housing CAD. Don't reuse it for installation.
- Follow-up [inline Eddy toolhead R2](outputs/AD5M_toolhead_R2/) (side housing + front cradle around the cooling module) designed the same day; CAD only. Replacement [marking buttons R5](outputs/Eddy_Duo_nonwrap_marking_guides_R5/) made for drilling without the locator.
- Evidence: [REJECTED_FAN_INTERFERENCE.md](outputs/AD5M_custom_toolhead_inline_eddy_R1/REJECTED_FAN_INTERFERENCE.md), `outputs/Eddy_Duo_adjustable_side_mount_R4/DO_NOT_USE_WRAPAROUND_LOCATOR.txt` (committed 2026-11-20 from the local working copy)

### 2026-11-12 → 11-13 — Dragon Burner path explored; frame decision
- Dragon Burner #1406257 v11 adapter remixed with a rear Mode-A Eddy pocket (R1); Dragon Burner v8 STLs archived. *Path dropped on 2026-11-20.*
- **Frame conversion locked to standard Voron Trident 300 × 300 × 300 mm, HFSB5-2020.**
- Evidence: [frame plan](docs/plans/FRAME_CONVERSION.md)

### 2026-11-14 → 11-18 — BambuMod × Orbiter v2.5 adapter line
- R1: Primary (motor centred, hotend −6.335 mm) and Alternate remixes. R2–R7: shroud arch, smooth C2 duct, blind carriage bores, hex-nut pockets, reinforced bosses, fillets. R8: live parametric FreeCAD + web workspace.
- Evidence: [outputs/INDEX.md](outputs/INDEX.md)

### 2026-11-15 — Eddy Duo moved from USB to CAN
- Evidence: `klipper/2026-11-17/config/eddy-duo.cfg.pre-can-20261115-225700`

### 2026-11-16 — First-layer qualification on ASA-GF ✅
- Siraya Tech ASA-GF, 30 × 30 × 0.20 mm, 260 °C / 105 °C, 20 mm/s. Zero CAN retransmits. Result: "Sticking, with lines joining together."
- Evidence: [klipper/2026-11-17/](klipper/2026-11-17/)

### 2026-11-17 — Nozzle brush and wiper prepared
- [Rear nozzle brush](outputs/AD5M_nozzle_brush_MK2_plus5/) (Tinkering Poko MK2, seat moved 5 mm toward the bed) and [Stormage nozzle wiper](outputs/AD5M_nozzle_wiper/) sliced in ASA-CF. Print, fit and wipe coordinates not recorded; no wipe macro exists yet.

### 2026-11-17 — Config archived; host backed up; Intel migration plan
- Full config snapshot committed (including `z_speed_control.py`), host units backed up, Intel migration handoff written; private archive in Drive.
- Evidence: [klipper/2026-11-17/](klipper/2026-11-17/), Drive `Backups (PRIVATE)/AD5M_Intel_Migration_PRIVATE_2026-11-17.zip`

### 2026-11-18 — Nozzle shifted 6.335 mm for the centred Orbiter motor
- Hotend moved to the R2–R8 offset datum: nozzle now 6.335 mm right of the toolhead centreline so the Orbiter motor stays centred. (The R8 housing is the one on the printer; user confirmed 2026-11-20, install date not recorded.)
- X limits moved +6.3 mm (−3.7 … 219.7); Eddy offset now 28.7.
- Evidence: [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md), `klipper/2026-11-19/config/eddy-duo.cfg` header

### 2026-11-19 — Shroud R4 fitted; ABS tuned; project renamed
- **Fan shroud R4** printed, mounted and height-adjusted.
- Timed `PREHEAT` / `CANCEL_PREHEAT` macros added.
- Sunlu ABS profile tuned (260/100, 20 mm³/s, PA 0.02); temperature test photographed (Drive `Photos/sunlu temp test`).
- Project renamed **The Moron Tridont Project**.
- Evidence: [klipper/2026-11-19/](klipper/2026-11-19/)

### 2026-11-19 (late) — Migrated to Kalico + eddy-ng
- Mainline Klipper → **Kalico** with **eddy-ng** on CurbyServer. The Intel host had replaced the Pi 5 by this point (cutover date not recorded).
- Changes: `limited_corexy`; smooth shapers; **MPC**; eddy-ng tap (`tap_adjust_z 0.130`); separate home current; 5-zone Z travel; `forge-x-macros.cfg` → `tridont_macros.cfg`; `LINE_PURGE` fix; legacy mesh blocks removed; telemetry off.
- Evidence: [klipper/2026-11-19-kalico/](klipper/2026-11-19-kalico/)

### 2026-11-20 — Records reconciled; Drive reorganized; build log started
- Installed hardware confirmed and recorded (PR #2): R8 + R4 shroud, TZ 2.0 clone hotend, Eddy on side mount R4 via CAN, **bed wired directly to BED-OUT** with `max_power 0.93`, Intel host. `rotation_distance 4.69` verified by a 50 mm extrusion test.
- **Dragon Burner path dropped.**
- Repo reorganized (history and plans moved to `docs/`); Kalico snapshot committed; Drive split into NotebookLM sources, Current printables, CAD references, Klipper snapshots, Backups (PRIVATE) and Photos.
- This build log created and mirrored to Drive. Local work that had never been pushed (inline R1 rejection, locator warning, toolhead R2, marking buttons R5, nozzle brush and wiper) committed to GitHub.
- **Workstation reorganized to mirror Drive:** `Documents\3D Printing\1 - The Moron Tridont Project\` (repo + Drive mirror + archive) and `2 - Voron Trident & Other Printers\`.

### 2026-11-25 — Phase 5 AD5M `3× MGN12H 300 mm` miniature Voron Trident gantry R1 & BOM locked (🔄)
- **What changed:** Designed parametric 16-part support-free CoreXY gantry [`AD5M_MGN12_Gantry_R1`](outputs/AD5M_MGN12_Gantry_R1/) anchored to `AD5M_Frame.STEP` & `AD5M_Enclosure.STEP` (vertical inward `300 mm` MGN12H Y-rail spines, self-supporting `300 mm` X-rail above both belt planes, rigid double-shear `48 mm`-ready rear motor mounts with `F695` top shaft caps, door-accessible Voron BFI front compression tensioners, and 2/3-piece flat-bed-printable Trident split XY joints). Retuned all heat-set pockets to **`M3 × 4.6 × 5.7 mm`** (`Ø4.00 × 6.2–6.5 mm`), widened `XY_2_20T` bays to `Ø18.6 mm` (`X = ±146.8 mm`) and lowered motor faces `-0.5 mm` (`L: 356.5`, `R: 367.5`) for the selected FULARR kit, exported `Z = 0` [`parts_print_pose/`](outputs/AD5M_MGN12_Gantry_R1/parts_print_pose/), and logged the official Phase 5 BOM in §7.2.
- **Physically tested?** CAD only (75 interference checks = `0.0000 mm³`, 16/16 single-solid valid BREPs & watertight single-component STLs; untested physically).
- **Evidence:** [AD5M_MGN12_GANTRY_SPEC.md](docs/plans/AD5M_MGN12_GANTRY_SPEC.md), [PRINT_AND_FIT.md](outputs/AD5M_MGN12_Gantry_R1/PRINT_AND_FIT.md), [build_gantry_r1.py](scripts/cad/gantry_r1/build_gantry_r1.py), [validation.json](outputs/AD5M_MGN12_Gantry_R1/validation.json)

---

## 6. Print and test record

| Date | File / test | Material | Nozzle / bed | Firmware | Result | Notes |
|---|---|---|---|---|---|---|
| 2026-11-11 | `Voron_Design_Cube_v7_PETG.gcode` | PETG | — | Klipper | ✅ Completed | First print on the new electronics |
| 2026-11-11 | Rapid-scan mesh, side Eddy | — | — | Klipper | ⚠️ Edge roll-off past X 196 | Variance 0.506 → 0.219 mm after capping |
| 2026-11-16 | First layer 30 × 30 × 0.20 mm | Siraya ASA-GF | 260 / 105 °C | Klipper | ✅ Adhered, lines joined | Small test, not full bed |
| before 11-19 | 50 mm extrusion test | — | — | Klipper | ✅ 50.0 mm measured | Confirms `rotation_distance 4.69` |
| 2026-11-19 | Sunlu ABS temp test and tuning | Sunlu ABS | 260 / 100 °C | Klipper | ✅ Profile saved | 20 mm³/s, PA 0.02, flow 0.95 |
| 2026-11-19 | `LINE_PURGE VALIDATE_ONLY=1` | — | — | Kalico | ✅ | Purge macro fix |
| *next* | Full-bed first layer | ABS | 260 / 100 °C | Kalico | | Checks mesh to X 210 |
| *next* | Long print (≥ 4 h) | ABS / ASA | | Kalico | | Thermal soak, CAN stability, MPC, BED-OUT temperature |
| *next* | Dimensional cube / shrink check | ABS | | Kalico | | Validates 99.4 % shrink |

---

## 7. Bill of materials

> **Canonical single-document BOM (with product links, ASINs, and notes):** **[BOM.md](BOM.md)**

Costs are left blank for you to fill in.

### 7.1 Installed or on hand

| Part | Qty | Status | Cost | Notes |
|---|---:|---|---:|---|
| FlashForge Adventurer 5M (base) | 1 | Installed | | Chassis, bed, XY/Z mechanics, PSU |
| Intel Linux PC (CurbyServer) | 1 | Installed | | Host |
| Raspberry Pi 5 8 GB (Vemico kit) | 1 | Retired | | Former host |
| BTT HDMI5 touchscreen | 1 | Installed | | |
| BTT Octopus Pro V1.1 H723 | 1 | Installed | | Replacement unit |
| BTT TMC2209 V1.3 | 4 | 3 installed + 1 spare | | |
| BTT EBB42 V1.2.1 CAN | 1 | Installed | | |
| BTT EBB36 V1.2.1 (no MAX31865) | 1 | Spare | | Superseded |
| BTT Eddy Duo | 1 | Installed | | CAN |
| ReliaBot external bed MOSFET V1.3 | 1 | On hand, not installed | | Option if bed current is too close to 10 A |
| Orbiter v2.5 + LDO-36STH20-1004AHG | 1 | Installed | | |
| TZ 2.0 clone hotend (X1C-style), 0.4 mm | 1 | Installed | | Upgrade ordered: AJOYIB `24 V 60 W` ceramic heater + `100K B3950` thermistor + clip (`MPC_CALIBRATE` after swap) |
| Bambu X1C hotend | 1 | Removed | | Earlier records called the hotend X1C |
| Peerless DF3010B24H 3010 fan | 1 | Installed | | Hotend fan |
| Part-cooling blower (stock HXH HBB0524VD) | 1 | Installed? | | Confirm |
| ADXL345, USB camera | 1 each | Installed | | |
| 4-core CAN cable (≈18 AWG), 12/16 AWG copper, lugs, JST/Molex | — | Installed | | |
| Printed: rear carrier R10, R8 housing, R4 shroud, Eddy mount R4, EBB42 bracket | — | Installed | | ABS / ASA |

### 7.2 Phase 5: AD5M `3× MGN12H 300 mm` Linear-Rail CoreXY Gantry (`AD5M_MGN12_Gantry_R1`)

| Part / Kit | Qty | Status | Cost | Allocation & Notes |
|---|---:|---|---:|---|
| **`uxcell MGN12 300 mm` Linear Rail + `MGN12H` Block** | 1 | Ordered | | Self-supporting X-axis rail (`Z_mid = 394.5`); bearing steel w/ plastic mini guide & end limit blocks (remove end blocks before seating) |
| **`IMETRX MGN12H 300 mm` Linear Rail Guides + Blocks** | 2 | Ordered | | Vertical inward Y rails on side spines (`\|X\| = 171.5`, `11` bolts/side); pre-oiled heavy-duty bearing steel |
| **FULARR `5 m` GT2 Timing Belt & Pulley Kit** (ASIN `B07TFCPCJ2`) | 1 kit | Selected (Amazon) | | `5 m × 6 mm` open rubber GT2 belt (`~2.52 m` needed installed; planned future upgrade to genuine Gates `LL-2GT-6`), `5×` `20T` `5 mm`-bore `16 × 16 mm` drive pulleys (`2` used), `5×` `20T` `5 mm`-bore `Ø18 × 8 mm` toothed idlers (`2` used), springs/blocks/wrench |
| **M METERXITY `F695-2RS` Flanged Ball Bearings** (ASIN `B0F4XNK1GM` / `mma250226ty002421jp`, `20`-pack) | 20 pcs | Selected (Amazon) | | Chrome steel double-rubber-seal `5 × 13 × 4 mm` (`Ø15 mm` flange); `14` used (`12×` in `6` back-to-back smooth idler stacks + `2×` rear double-shear motor caps); verify 20-pack variant at checkout |
| **`Ø5 mm` 304 Stainless Steel Dowel Pin Assortment** (`10/16/20/25/30/35/40 mm`) | 1 set | Selected (Amazon) | | `8` pins used total (`7×` `5 × 20 mm` for BFI + `5×` XY pins + `1×` `5 × 30 mm` for Left `XY_2_20T`); verify `>= 7× 5×20` and `>= 1× 5×30` inside pack |
| **`5 × 8 × 0.5 mm` 304 Stainless Steel Bearing Shims** (`100`-pack) | 100 pcs | Selected (Amazon) | | RC `5 mm` inner-race bearing shims (`~28` used: `2× 0.5 mm` above/below each `F695` pair, `1 + 2` shims on `8 mm` FULARR `20T` toothed idlers) |
| **`M3 × 4.6 mm OD × 5.7 mm` Brass Heat-Set Inserts** | ~39 used | On hand | | CAD tuned to `Ø4.00 mm × 6.2–6.5 mm` pockets across Y-spines (`11×`/side), rear motor mounts (`3×`/side), and split XY joints |
| **`M3 / M4 / M5` SHCS & Nuts** (`M3×8/12/16/20/35`, `M4×12/16`, `M5×12`) | ~100 pcs | Standard fasteners | | `48×` `M3×8` rail/block bolts, `4× M3×35` + `4×` M3 hex nuts for Front BFI, `M3×12/16/20` XY-joint & DS cap bolts, `M4`/`M5` frame mounts |
| **AJOYIB `24 V 60 W` Ceramic Heater + `100K B25/50=3950K ±1%` Thermistor + Clip** (Bambu X1/X1C compatible) | 1 set | Ordered | | Hotend upgrade (`350 °C` max heater, `-30..300 °C` thermistor); keep `Generic 3950`, set `heater_power: 60`, re-run `MPC_CALIBRATE` |
| **Future `48 mm` XY Stepper Upgrade (`LDO-42STH48-2004MAH` / `2504MAH`)** | 2 | Future (optional) | | `0.9°`, `48 mm` body, `24 mm` shaft; stock `40 mm` AD5M steppers fit initially once press-fit pulleys are swapped for `20T` set-screw pulleys |

### 7.3 Planned: Phases 6–7 (Trident 300 × 300 × 300)

| Part | Qty | Notes |
|---|---:|---|
| Misumi HFSB5-2020 extrusions (19 pieces, 8,152 mm) | 19 | Cut list in the [frame plan](docs/plans/FRAME_CONVERSION.md) |
| MGN12H rail 350 mm (X) | 1 | |
| MGN9H rail 350 mm (2× Y, 3× Z) | 5 | |
| NEMA17 TR8×4 350 mm integrated leadscrew steppers | 3 | Triple Z |
| LL-2GT-6 belt, 1,890 mm | 2 | Recalculate for 9 mm belts / AWD |
| Additional TMC2209 | 2–5 | Triple Z + AWD |
| AWD motors | 2 | |
| 12" × 12" MIC6 plate 5/16" + PEI | 1 | |
| 250 × 250 mm 450 W AC silicone heater + SSR + 150 °C thermal fuse | 1 | Stock PSU can't run a 300-class bed |
| Enclosure panels (coroplast deck/back, acrylic top/sides/doors) | — | Sizes in the frame plan |
| DIN rail 420 mm | 2 | |
| 5-series M3/M5 T-nuts | — | 6 mm-slot nuts don't fit |

---

## 8. Open issues

| # | Issue | Why it matters | Suggested action |
|---|---|---|---|
| 8.1 | **Bed on-current not measured.** The bed is on BED-OUT (10 A continuous, 12 A max) with `max_power 0.93`. The cap limits average current; RMS at 93 % duty is about 3.7 % above average. | Board MOSFET, fuse and connector heat with RMS current. | Power off, measure the bed's cold resistance, compute on-current = 24 V ÷ R, and set `max_power ≤ (10 ÷ on-current)²`. Details in [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md). |
| 8.2 | **EBB42 bracket on R8 not recorded.** | Needed to reproduce the toolhead. | Note which bracket and revision is mounted. |
| 8.3 | **`Toolhead_layout_R2.FCStd` only on the workstation.** It embeds a part-cooling duct of unknown origin, so it isn't in the public repo; 23 MB is also over the Drive connector's upload limit. | Lost if the workstation copy goes. | Identify the duct's source/license, then commit it or upload it to Drive `CAD references` by hand. |
| 8.4 | **No TZ 2.0 clone CAD.** All R1–R8 clearance checks used the original Bambu X1/P1 hotend STEP. | Hotend clearances are nominal. | Model or measure the clone. |
| 8.5 | **Electrical verification deferred.** Continuity and polarity checks were never recorded; DC branch fuses aren't sized. | Safety. | Meter checks; record results here. |
| 8.6 | **Blower PWM interface** for the 4-wire blower never formally recorded. | Fan control / tach. | Record the wiring in use. |
| 8.7 | **PSU budget for future phases.** 350 W won't cover a 300 mm bed or several hotends. | Phase 7/8 planning. | Write the load budget before buying the bed. |
| 8.8 | **Drive Master Spec doc** was last synced from GitHub on Nov 12 (Eddy on USB, HE0 bed, Dragon Burner). | NotebookLM reads it. | Re-sync from CURRENT_TOOLHEAD_SPEC.md. |

---

## 9. Next steps

1. **Measure the bed** (8.1) and adjust `max_power` if needed.
2. **Qualify on Kalico:** full-bed first layer, then a ≥ 4 h ABS print. Watch BED-OUT and connector temperature. Log both in §6.
3. **Record the EBB42 bracket** (8.2).
4. **Re-run calibrations once hardware settles:** shaper, MPC, PA per filament, `EDDY_TAP`. Log values in §3.
5. **Close Phase 3:** tag `v0.3-toolhead` in Git.
6. **Phase 5 prep:** photograph and trace both belt paths; measure pulley centres, heights and clamp heights before touching the gantry.

---

## 10. Safety and change checklist

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

Also update §1, §4, §6 and §7 as needed.

---

## 12. References

**In this repo:** [README.md](README.md) · [AGENTS.md](AGENTS.md) · [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md) · [outputs/INDEX.md](outputs/INDEX.md) · [frame plan](docs/plans/FRAME_CONVERSION.md) · [roadmap](docs/plans/UPGRADE_ROADMAP.md) · [design journal](docs/history/TOOLHEAD_SPEC_JOURNAL_2026-11.md) · [klipper/](klipper/)

**Third-party designs used (keep their licenses):**
- BambuMod for FF Adventurer 5M — Kirill_Wawe, Printables 1574762 (CC BY-NC-SA 4.0)
- Orbiter v2.0/2.5 mockup — dr. Lorincz Robert (CC BY-NC-SA 4.0)
- AD5M lightweight fan duct — Printables 1404902
- AD5M nozzle brush MK2 — Tinkering Poko, Printables 1168757 (CC BY 4.0)
- AD5M nozzle wiper — Stormage, Printables 1262881 (CC BY-SA 4.0)
- Bambu X1/P1 hotend CAD — Jorge (jorge_rui), Printables 533213
- AD5M Dragon Burner adapter v11 — Printables 1406257 (dropped path)
- Voron Trident — VoronDesign (GPL-3.0)
- BootyCallJones K1 gantry — reference only

**Firmware and hardware docs:** [Kalico](https://github.com/KalicoCrew/kalico) · [eddy-ng](https://github.com/vvuk/eddy-ng) · [Klipper CAN bus](https://www.klipper3d.org/CANBUS.html) · [BTT Octopus Pro](https://global.bttwiki.com/Octopus%20Pro.html) · [FlashForge AD5M wiki](https://wiki.flashforge.com/en/adventurer-series/manual/intro-ad5m)
