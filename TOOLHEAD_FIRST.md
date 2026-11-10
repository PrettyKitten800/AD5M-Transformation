> **Hardware & status update — November 2026:** The confirmed toolboard is **BTT EBB42 V1.2.1** (original EBB42 family, not Gen2), replacing EBB36. The replacement mainboard is confirmed as **BTT Octopus Pro V1.1 (STM32H723ZET6)** and has been flashed with the Klipper USB-to-CAN bridge (`outputs/flashing_2026-11-03/`). Eddy Duo uses direct USB to the Pi 5 for now. Historical EBB36 wiring, connector positions, pin assignments, firmware settings and mounting drawings below are retained as history and are not an approved EBB42 wiring plan; verify against exact EBB42 V1.2.1 documentation before use. Read `AGENTS.md` and `CURRENT_TOOLHEAD_SPEC.md` first.

# EBB36 toolhead first

User's assembly order, November 1, 2026. Board: EBB36 CAN V1.2.1 without MAX31865. Keep USB and 24 V disconnected while assembling. This page assigns circuits, not unreadable physical pin positions.

November 3, 2026: the current BTT-led visual guide and step order are in [EBB36 wiring plan R1](outputs/EBB36_wiring_guide_R1/WIRING_PLAN.md) and the [seven-page printable guide](output/pdf/EBB36_toolhead_wiring_R1.pdf). They retain the selected PA0 hotend-fan allocation. The BTT V1.2 schematic confirms existing 10 kOhm endstop pull-ups to 3.3 V (R35-R37); no extra pull-up is specified by the baseline plan.

## Start with these three circuits

| Circuit | EBB destination | Wiring |
|---|---|---|
| Bambu X1C heater | Green HE0/E0 screw terminal | Heater pair, one lead per terminal; heater has no polarity. Use a suitable stripped-wire/ferrule termination, not a fork or solder-tinned wire end. |
| Bambu X1C thermistor | TH0, software PA3 | Thermistor pair, one lead per contact; no polarity. Leave PT1000 jumper removed for the NTC arrangement. |
| Peerless DF3010B24H hotend fan, 24 V 0.09 A | Fan channel PA0 | Fan positive to VIN; negative to switched fan output. Match board polarity before inserting the connector. |

PA0 is this project's selected hotend-fan channel, following the AD5M conversion allocation. BTT's generic example uses PA0 for part cooling instead. The final configuration must match this project's wiring. No software configuration or temperature calibration is supplied by this page.

Mount the EBB so its underside and connector pins cannot touch the motor case or mounting hardware. Route short leads with service slack and strain relief, clear of the nozzle, belts and fan blades. Reuse existing suitable component leads rather than replacing all of them with the thick power wire.

## Then prepare the remaining connections

1. Extruder motor: angled four-contact motor connector at the upper left in the supplied front photo. Identify and record both coil pairs and the EBB coil-contact order before repinning; color alone is not evidence. The EBB's built-in TMC2209 drives this motor.
2. Four-conductor toolhead harness: VIN, GND, CAN H and CAN L. Match both connector ends to the actual board pinout. H/L must be a twisted pair. Record colors and contact positions before crimping; no color assignment has yet been established. Select CAN termination at both bus ends.
3. X and Y A3144 sensors: 5 V supply, GND, and separate outputs pulled up to 3.3 V. X output -> EBB36 PB6; Y output -> EBB36 PB7, matching the AD5M reference configuration. BTT's official EBB36 V1.1/V1.2 pinout confirms the Endstop header order, left to right as pictured: +5 V, GND, PB6, PB5, PB7. PB5 is unused here. Verify physical sensor package legs before soldering. PB3/PB4 belong to a different I2C/filament expansion header; they were previously compared incorrectly with the guide's PB6/PB7.
4. HXH HBB0524VD blower: retain the stock four-wire fan. The reference diagram gives red=24 V, black=GND, blue=PWM, yellow=speed feedback, but the electrical control interface is still unresolved. Do not treat its PWM lead as a second power wire or connect it directly to 24 V.

Keep VUSB removed for normal operation from 24 V. Heaters can be physically wired in this unpowered stage, but disconnect their removable connections for initial flashing and electronics bring-up. Continuity checks and first power-up remain later stages.

## References

- BTT hardware and thermistor jumpers: https://neo.bttwiki.com/en/docs/board-docs/ebb-series/ebb-36/ebb-36-hardware
- BTT V1.2 pin configuration: https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/sample-bigtreetech-ebb-canbus-v1.2.cfg
- AD5M fan allocation: https://github.com/sedmenti/FlashForge_A5M_raspberry/blob/main/Klipper/printer.cfg
- Existing photo overlay: reference/wiring_R3/02_toolhead_bed_photo_overlay.png
