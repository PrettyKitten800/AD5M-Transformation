> **Hardware & status update — November 2026:** The confirmed toolboard is **BTT EBB42 V1.2.1** (original EBB42 family, not Gen2), replacing EBB36. The replacement mainboard is confirmed as **BTT Octopus Pro V1.1 (STM32H723ZET6)** and has been flashed with the Klipper USB-to-CAN bridge (`outputs/flashing_2026-11-03/`). Eddy Duo uses direct USB to the Pi 5 for now. Historical EBB36 wiring, connector positions, pin assignments, firmware settings and mounting drawings below are retained as history and are not an approved EBB42 wiring plan; verify against exact EBB42 V1.2.1 documentation before use. Read `AGENTS.md` and `CURRENT_TOOLHEAD_SPEC.md` first.

# AD5M upgrade roadmap

Updated November 3, 2026 (America/New_York).

## User goals and current status

- November 3, 2026: the user previously completed the BootyCallJones linear-rail conversion on a K1 Max but no longer owns that printer. Use the published CAD/documentation and the user's experience as references; the K1 Max is not available for physical measurements. A full source snapshot, including STEP parts, is saved in `reference/BootyCallJones_K1_Gantry/`; see its START_HERE.md. Adapt concepts to measured AD5M geometry; the exact previously installed K1 conversion revision is not established.
- November 3, 2026: the user established Voron Trident as the reference architecture for the eventual machine. Official source snapshots, manuals, CAD, STLs, firmware examples, build guides and BOM/sourcing references are collected in `reference/Voron_Trident/`; start with `reference/Voron_Trident/START_HERE.md`. This does not change the immediate restoration priority.
- Immediate priority: restore reliable single-tool printing with the replacement Octopus Pro and existing motion hardware. This takes precedence over upgrade planning.
- November 3, 2026: user selected the XY gantry redesign for linear rails as the first upgrade after restoring printing. It is not a prerequisite for recovery. Search findings and official AD5M frame CAD are in `reference/AD5M_gantry_research/`.
- Long-term goal: one independently controlled motor per Z screw (three total).
- Longer-term goal: four complete interchangeable toolheads.
- User reports the existing Octopus Pro is defective and needs to be returned. User has now ordered a replacement Octopus Pro. Exact ordered revision/MCU and arrival date have not been confirmed; do not assume they match the original V1.1 H723 until checked.
- User also wants to consider FYSETC Spider V3.0 F446; reports the H7 variant is unavailable. The stray message "bigtreetech" was explicitly withdrawn and does not establish a brand preference.
- Compare retaining the frame with reduced print area against preserving 220 x 220 mm with possible extensions. No extension has been selected; the existing stock rear-cover constraint remains in effect.
- Existing hardware: Pi 5, EBB36 V1.2.1, four conventional TMC2209 modules, 24 V 14.6 A PSU, external bed MOSFET, Bambu X1C hotend.
- User confirms the purchased screen is a BTT HDMI5 and is considering returning it if a controller/display bundle is worthwhile. No return or replacement decision has been made.
- The newer controller comparison reports the EBB flashed; the older handoff predates that report. Successful printer commissioning remains unconfirmed.

## Controller selection: replacement Octopus Pro ordered

The user selected and ordered a replacement Octopus Pro. The alternatives below are retained as research history, not pending selection decisions. Confirm the delivered revision before reusing the existing wiring map or firmware. Establish basic board power and communication with peripherals disconnected before reconnecting the printer harness.

Octopus Pro V1.1 H723 remains the recommendation for minimum rework. FYSETC Spider V3.0 F446 is a viable compact alternative; there is no established requirement here to wait for its H7 version. Both provide eight independent driver channels covering CoreXY A/B plus Z/Z1/Z2, leaving three spare. Reuse compatible conventional TMC2209 modules after their condition is established, with board-specific orientation and UART settings. Five modules are required for the final motion system: one more than the four owned, or two more if retaining a spare.

Use one toolboard per complete toolhead. Each handles its own extruder motor, heater, thermistor and fans. Four heads therefore do not require four additional mainboard driver channels. With all extruders on the mainboard instead, the system would require nine independent channels before any changer actuator.

Alternatives:

| Board | Channels | Assessment |
|---|---:|---|
| Octopus Pro V1.1 H723 | 8 | Preferred for this build: existing drivers, Pi, wiring plan and carrier design. Physical carrier fit still needs checking. |
| FYSETC Spider V3.0 F446 | 8 | Strong compact alternative: 155.3 x 76.5 mm PCB versus Octopus Pro's 160 x 100 mm. Conventional drivers, Pi USB communication and onboard CAN. New carrier, wiring map and firmware required; assembled clearance remains unverified. |
| Makerbase MKS Monster8 V2 | 8 | Main Makerbase candidate for retaining the Pi 5. STM32F407, conventional UART/SPI drivers, onboard CAN, 12-24 V input. Covers XY/triple Z plus three spare motion channels. Board-specific CAN pin allocation and mounting need review. |
| FYSETC S6 | 6 | Compact 117 x 87 mm alternative with one spare motion channel. Older design; do not confuse exposed CAN MCU pins with a complete onboard CAN transceiver. Plan a separate CAN adapter unless a suitable interface is verified. |
| FYSETC Spider King | 10 | Extra capacity but 177 x 108 mm footprint; unnecessary for baseline distributed toolheads. Confirm control-core variant and conventional-driver setup before purchase; automatic driver identification requires matching FYSETC drivers. |
| FYSETC Catalyst.K | 5 | H723 with CAN, USB and conventional driver sockets; meets motion requirement exactly with toolboard extruders, leaving no spare onboard motion channel. Different product from the older Catalyst kits. |
| Makerbase MKS SKIPR | 7 | Includes RK3328 Linux host plus motion MCU. Viable integrated architecture but duplicates the host role of the already-owned Pi 5; not preferred while retaining that Pi. |
| Octopus MAX EZ | 10 | Consider for deliberate extra onboard expansion and EZ sockets. Requires EZ drivers; existing conventional modules do not fit directly. Wiring and mounting review required. |
| Manta M8P V2.0 | 8 | Capable alternative with conventional drivers, but its compute-module integration adds less value when keeping the standalone Pi 5. Different mounting and wiring. |

Linear rails do not add controller channels. The existing 24 V driver plan remains the baseline. Do not apply a board's higher voltage rating to TMC2209 modules.

Spider V3 F446 specifics: STM32F446 at 180 MHz. Its onboard CAN termination is permanently fitted at 120 ohms, so locate the board at a bus end and terminate only the other physical end. FYSETC documents a Spider V3 F446 CAN toolhead setup without an additional CAN adapter. The existing EBB need not match the mainboard brand. Retain the Pi 5's separate power supply in the baseline plan. The Spider's probe inputs and external bed-MOSFET control must be reassigned and electrically checked; Octopus connector positions and GPIO assignments do not transfer. Processor speed alone does not establish a printer speed limit; no final step-rate target or stress test has been defined.

### Amazon kit and screen comparison

User link: https://www.amazon.com/dp/B0DHSTPR5F . Retrieved listing title describes an MKS 8 V2 F407 board with TMC2209 and LCD; specifications appear consistent with a Monster8 V2-style kit, but branding is YDuupxe, not Makerbase. This does not prove counterfeiting; exact manufacturer/revision is not independently established. User explicitly confirms NO TMC drivers are included, superseding the earlier uncertainty from the title. Value comparison is board plus Mini12864 display only. Reusing the four owned conventional TMC2209 modules still requires one additional working module for the five-motor target. No reliable delivered-price comparison has been established.

The listed display is an MKS Mini12864 V3: basic graphic LCD with knob/menu controls and Klipper support, connected through EXP headers. It can provide local temperature/movement/print controls with configuration; custom toolchanger functions require menu/macro work. It is not an HDMI touchscreen or a KlipperScreen display.

The user's BTT HDMI5 is a five-inch touchscreen connecting to the Pi by HDMI and USB. It can remain in the build with BTT, FYSETC or Makerbase motion boards. Recommended to retain for convenient local control during commissioning and future multi-tool operation if budget permits. Returning it and using a Mini12864 plus browser-based Mainsail/Fluidd is a valid cost-saving choice, with reduced local UI capability. No screen return has been recommended as necessary for compatibility.

Keep the existing USB-to-CAN bridge plan as a starting point. For four heads, design bus wiring, termination, protected power branches and moving cables as a complete system. A separate USB-to-CAN adapter remains an optional architecture choice. Parked tools should remain electrically connected in the baseline design; mechanical toolchanging does not require hot-plugging their controllers.

## Mechanical architecture

See [FRAME_CONVERSION.md](FRAME_CONVERSION.md) for the Euro `4040` (`315 × 315 mm` plate / `300 × 300 × 315 mm` build volume) extrusion plan, rail/slot compatibility rules, and pre-order checklist.

The AD5M has a fixed-height XY gantry and a moving bed. Toolchangers that depend on vertical gantry movement require a separate source of relative vertical motion, such as a lifting dock assembly. Triple Z bed motors do not supply that motion between the gantry and frame-mounted docks.

MadMax is a candidate to investigate because it uses XY-only toolchanges and supports front-facing MGN9H/MGN12H rails. This is not a confirmed AD5M conversion or a verified four-tool layout. StealthChanger/TapChanger-style arrangements require explicit evaluation of pickup motion and dock adaptation.

Proposed rail arrangement: one X rail and two Y rails, with the X-rail face, carriage and belt planes chosen together with the future tool coupling. Rail lengths and sizes are not yet selected. Measure available mounting surfaces, full carriage travel, belt clearance and nozzle reach before ordering.

Triple Z requires removing the shared mechanical synchronization or redesigning it into independent drives. Inspect screw supports, motor mounting space, couplings or individual belt reductions, and bed/guide attachment freedom. A rigid bed support that cannot accommodate small tilt corrections may bind. Use Klipper Z_TILT_ADJUST only after the mechanics and probe are validated; bed mesh remains a separate function.

## Layout comparison

| Approach | Benefit | Main uncertainty |
|---|---|---|
| Keep frame, park tools inside | Less structural reconstruction; compact footprint | Four docks and their pickup paths must fit. Parked heads may reduce printable area, not necessarily by a simple rectangular strip. |
| Preserve 220 x 220 mm, move docks outside print envelope | More useful bed area for multi-tool work | Docks must remain reachable: may require longer travel, changed gantry/belts/rails and structural extensions. An enclosure spacer alone does not extend motion travel. |

Neither layout is dimensionally validated. Model four complete heads, docks, pickup/parking paths, belt hardware, cable bends, bed travel and printed-object clearance. Consider a single row and split banks if reach permits. Do not infer docking width from nominal bed width.

## Build sequence

### Immediate: restore printing

1. Receive the ordered replacement Octopus Pro, confirm revision/MCU, and establish board power and Pi communication with peripherals disconnected.
2. Complete and verify the existing single-tool wiring and firmware, including EBB communication, sensor interfaces, blower control and temperature-sensor configuration. Retain the current single-motor Z drive and existing XY mechanics.
3. Commission sensors, motors/homing, fans and heaters in stages, then calibrate and complete a successful test print.
4. Establish repeatable printing before beginning mechanical upgrades. Current mainboard driver requirement is three (CoreXY A/B and Z); the EBB drives the extruder. The four owned modules cover this stage if serviceable, with one spare.

### Future upgrades, separately scheduled

- XY rails: first upgrade project after restoring reliable printing. Measure the AD5M and design the gantry using the Trident as a reference; evaluate a replaceable toolhead mounting interface before finalizing the carriage. Full toolchanger design remains a later project.
- Long term: independent triple Z and validated tilt correction.
- Longer term: select and dimension the toolchanger layout, prove two-tool operation, then expand to four.

Future compatibility should inform choices when convenient, but toolchanger CAD, dock layout, rail purchases and additional Z motors must not delay restoring the printer. Revisit toolhead-mounted X/Y endstops during the future toolchanger project so homing remains defined when a tool is parked or absent.

The existing PSU is rated 350.4 W by its 24 V x 14.6 A nameplate. Four hotends plus bed, motors and electronics need a calculated load budget before assuming it can be retained. Heater ratings and concurrent heat-up/standby strategy are not yet established.

## Primary references

- [BTT Octopus Pro](https://global.bttwiki.com/Octopus%20Pro.html) and [V1.1 changes](https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-Pro).
- [BTT Octopus MAX EZ](https://global.bttwiki.com/Octopus%20MAX%20EZ.html).
- [BTT Manta M8P V2.0](https://global.bttwiki.com/M8P-V2_0.html).
- [BTT EBB36](https://global.bttwiki.com/EBB%2036%20CAN.html).
- [FYSETC Spider V3 F446 documentation](https://github.com/FYSETC/FYSETC-SPIDER) and [official CAN setup guide](https://docs.fysetc.com/en/article/sb-can-setup-guide-1d6nj5s/).
- [FYSETC S6](https://wiki.fysetc.com/docs/FYSETCS6), [Spider King](https://wiki.fysetc.com/docs/FYSETCSPIDERKING), and [Catalyst.K](https://docs.fysetc.com/en/article/catalystk-1i84435/).
- [Makerbase Monster8](https://github.com/makerbase-mks/MKS-Monster8) and [SKIPR](https://github.com/makerbase-mks/MKS-SKIPR).
- [Makerbase Mini12864 V3](https://github.com/makerbase-mks/MKS-MINI12864-V3) and [BTT HDMI5](https://global.bttwiki.com/HDMI5.html).
- [Klipper CAN bus](https://www.klipper3d.org/CANBUS.html).
- [Klipper Z tilt](https://www.klipper3d.org/Config_Reference.html#z_tilt).
- [MadMax](https://github.com/zruncho3d/madmax) and [FAQ](https://github.com/zruncho3d/madmax/blob/main/FAQ.md).
- [StealthChanger](https://stealthchanger.com/) and [TapChanger](https://github.com/viesturz/tapchanger).

This roadmap updates future capacity requirements relative to BTT_CONTROLLER_OPTIONS_2026-11-02.md, whose initial comparison assumed only three mainboard motors. It does not supersede verified physical wiring assignments or complete unresolved electrical checks.
