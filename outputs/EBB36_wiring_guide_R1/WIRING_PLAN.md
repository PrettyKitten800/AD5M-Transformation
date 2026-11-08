# EBB36 toolhead wiring plan - R1

Prepared November 3, 2026 for this AD5M build. Board identity and existing parts come from the project handoff and the user's saved photographs. This plan does not record any physical work, firmware flash or powered test as completed.

## Start here

The seven-page visual guide is [EBB36 toolhead wiring R1](../../output/pdf/EBB36_toolhead_wiring_R1.pdf). Individual numbered PNG pages in this folder are the same guide at full resolution.

Use BIGTREETECH as the primary source for connector positions, polarity, pin functions and jumper behavior. Use the saved build decisions for which device occupies each supported connector. Sedmenti remains secondary context for the AD5M-specific arrangement, especially the blower; its settings are not manufacturer specifications for the connected parts.

The board is **EBB36 CAN V1.2.1 without MAX31865**. Follow the first-generation V1.1/V1.2 reference with the V1.2 heater pin **PB13**. The old V1.1 manual is stored as supporting reference; the V1.2 schematic and current pinout take precedence for changed pins.

## Work order

1. Disconnect printer power and USB. Place the EBB on an insulated work surface and label existing component leads. Plan the board mount with underside clearance and strain relief.
2. Wire the X1C heater to the green E0/HE0 screw pair; one lead per clamp, no polarity. Use an appropriate wire/ferrule termination, not a solder-tinned wire end. The control pin is PB13 on the EBB MCU.
3. Wire the two X1C thermistor leads to TH0/PA3 and GND. No polarity. Keep the PT1000 jumper open for the planned NTC connection. This does not establish the exact X1C temperature curve.
4. Wire the existing Peerless DF3010B24H 24 V, 0.09 A hotend fan to the PA0 channel. In BTT's front view, the upper contact is the PA0 switched negative (black fan wire); the lower contact is VIN (red fan wire).
5. With the extruder motor disconnected, measure and label its two coil pairs. BTT schematic P11 is pin 1=A2, pin 2=A1, pin 3=B1, pin 4=B2. Locate physical pin 1 on the actual connector before repinning. No cavity orientation or wire colors have been inferred from the photo.
6. Prepare the X/Y Hall harness. BTT front-view ENDSTOP order is **+5 V, GND, PB6, PB5, PB7**. Both sensors share +5 V and GND; X OUT goes to PB6, Y OUT to PB7, PB5 stays unused. Split shared supplies with suitable insulated splices rather than forcing multiple unsuitable wires into one contact.
7. Prepare the four-conductor main harness: protected +24 V, common GND, CAN H, CAN L. Keep H/L twisted together and select a cable suitable for repeated toolhead motion. Verify the board-front contact mapping and every wire end to end before insertion. Record actual wire colors below.
8. Keep the four-wire blower separate until its control interface is verified. It is not an ordinary two-wire load. PA1 remains reserved; no PWM adapter, voltage or control frequency is approved by this plan.
9. Set jumpers with everything unpowered. VUSB open for normal 24 V operation; PT1000 open for NTC; EBB 120R fitted at the bus end. The Octopus end needs the second 120 Ohm termination. Measure about 60 Ohm between H and L with the connected bus fully unpowered.
10. Inspect crimps, shorts, contact mapping, connector retention, mounting clearance and strain relief. Select branch protection from actual wiring/contact ratings and total load; no fuse value is invented here.
11. Disconnect heater and motor for initial flashing/electronics bring-up. Identify each board and establish communications before reconnecting loads with power off. Check room-temperature sensor readings, fan response and both endstop states. Verify the X1C sensor curve and heater condition before heating. Account for multi-MCU homing before motion tests.

## Connection register

All MCU pins below are on the EBB. `EBBCan:` is the placeholder MCU name used by BTT; use the actual configured MCU name consistently.

| Device | Destination | Wiring/meaning | Current status |
|---|---|---|---|
| X1C heater | E0/HE0, PB13 | One nonpolar heater lead per screw clamp | Plan only |
| X1C thermistor | TH0, PA3/GND | Nonpolar pair; PT1000 jumper open for NTC | Exact sensor curve pending |
| Peerless hotend fan | PA0 / BTT FAN1 | Black -> switched PA0; red -> VIN (+24 V) | Physical installation unreported |
| Extruder | P11 / E0 / EM | Pins 1/2 = coil A; pins 3/4 = coil B | Measure coils and identify pin 1 |
| X Hall output | ENDSTOP PB6 | Sensor VCC to +5 V; GND shared | Actual package legs/test pending |
| Y Hall output | ENDSTOP PB7 | Sensor VCC to +5 V; GND shared | Actual package legs/test pending |
| ENDSTOP PB5 | Unused | Leave unconnected | Reserved/unassigned |
| Blower | PA1 reserved | Four-wire interface requires validation | Do not connect yet |
| Main harness VIN | Upper right in board-front view | Protected +24 V | Color/contact continuity unrecorded |
| Main harness GND | Upper left in board-front view | PSU V- / common ground | Color/contact continuity unrecorded |
| Main harness CAN L | Lower left in board-front view | Octopus CAN L | Color/contact continuity unrecorded |
| Main harness CAN H | Lower right in board-front view | Octopus CAN H | Color/contact continuity unrecorded |

Do not translate board-front positions to a cable wire-entry view by eye; that view may be mirrored or rotated. Use the mating key and continuity tests.

The [CAN harness close-up](CAN_harness_to_Octopus_Pro_V11.png) adds the Octopus Pro V1.1 socket orientation. With motor sockets across the top and power screw terminals on the left, its two-contact CAN socket is at the lower-right edge: **upper = CAN L, lower = CAN H**. The adjacent two-pin **CAN-120R** header takes the termination jumper. Only H/L go to this CAN socket; the cable's +24 V and GND split to the existing protected power-distribution junction. BTT's [V1.1 pinout](https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-Pro/blob/master/Hardware/BIGTREETECH%20Octopus%20Pro%20V1.1-Pin.jpg) is the source for this orientation.

## Important details resolved by the primary documents

- The ENDSTOP header really is PB6/PB5/PB7. PB3/PB4 belong to the adjacent I2C/filament expansion header.
- BTT's V1.2 schematic already includes 10 kOhm pull-ups to 3.3 V on the endstop inputs (R35-R37). An additional pull-up is not part of this baseline plan for the loose open-collector sensors.
- A 5 V Hall supply does not imply a 5 V signal pull-up. Keep the signal pull-ups at the board's 3.3 V rail.
- For a genuine Allegro A3144 -UA package, the branded-face/leads-down reference is 1=VCC, 2=GND, 3=OUT. The actual loose parts may be compatible replacements; verify their markings/package before applying that orientation.
- BTT's sample configuration assigns PA0 to part cooling and PA1 to hotend cooling. This build's prior wiring allocation is PA0=hotend fan, PA1=blower reserved. Preserve that allocation in the final configuration. Do not paste the example fan sections unchanged.
- The EBB's ADXL345 and TMC2209 are onboard. They do not require a separate accelerometer lead or a plug-in extruder driver for this layout.

## Prepare at the bench

Motor-connector clarification after checking both conversion guides: neither specifies a required stock extruder motor pin swap. ChaoticWeaponry's custom front socket is labeled A+, A-, B+, B- and its assembly instructions say to plug in the retained motor. This supports keeping the stock plug order; the coil-check step above is verification, not an instruction to repin it automatically. See [guide evidence and limits](../../reference/ebb36_motor_research/FINDINGS.md).

- Multimeter with resistance and continuity functions; fine probes suitable for the small contacts.
- Correct mating housings and contacts for the actual board connectors; compatible crimp tool and wire stripper. Confirm housing/pitch and wire range before crimping.
- Suitable ferrules where supported by the screw clamp and conductor size; no solder-tinned wire ends in screw clamps.
- Heat shrink for each splice/unused wire, wire labels, cable supports and a service loop.
- Flexible copper power conductors sized for the actual toolhead load and selected branch protection; a twisted CAN pair rated for repeated motion. Reuse suitable existing short component leads.

No purchase is assumed. Existing inventory, branch fuse value and final connector kit are not fully documented.

## Records to fill as we wire

| Function | Actual color/mark | Rear termination | EBB contact verified | Continuity |
|---|---|---|---|---|
| +24 V | Red, proposed power assignment | Fused branch from the existing positive junction feeding Octopus POWER+ and MOTOR-POWER+ | Board-front upper right | Pending |
| GND | Black, proposed power assignment | Existing negative junction feeding Octopus POWER- and MOTOR-POWER- | Board-front upper left | Pending |
| CAN H | Yellow, user reports pinned into data connector | Octopus CAN H; lower contact in the documented board view | Board-front lower right | Pending |
| CAN L | White, user reports pinned into data connector | Octopus CAN L; upper contact in the documented board view | Board-front lower left | Pending |

User update, November 3: yellow = CAN H and white = CAN L, already pinned into a connector. Red/black power connections are still being planned; no completed power termination, polarity measurement or continuity test was reported. Add the EBB red/black as an additional outgoing branch of the two existing harness power junctions near MOTOR-POWER, preserving one termination per Octopus board clamp. Red needs the selected EBB branch fuse; its rating remains unselected.

| Check | Recorded result |
|---|---|
| Motor coil A wires / resistance | Pending |
| Motor coil B wires / resistance | Pending |
| Actual motor connector pin 1 located | Pending |
| Loose Hall part identification and leg orientation | Pending |
| X and Y sensor states with/without magnet | Pending |
| H/L resistance, all power disconnected | Pending; expected about 60 Ohm with two 120 Ohm ends |
| +24 V harness polarity and shorts | Pending |
| Branch wire/contact ratings and fuse | Pending |
| Exact X1C thermistor curve | Pending |
| Blower PWM electrical requirements/interface | Pending |
| Board flash/CAN discovery records | Pending |

## Primary sources

Checked November 3, 2026. Downloaded BTT material is in `reference/ebb36_btt`; URLs and SHA-256 hashes are saved in its `SOURCES.json`.

- B1: [BIGTREETECH EBB36 hardware](https://neo.bttwiki.com/en/docs/board-docs/ebb-series/ebb-36/ebb-36-hardware)
- B2: [BIGTREETECH EBB36 V1.2 schematic](https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/EBB36%20CAN%20V1.1%20and%20V1.2/Hardware/BIGTREETECH%20EBB36%20CAN%20V1.2-SCH.pdf)
- B3: [BIGTREETECH V1.2 sample configuration](https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/sample-bigtreetech-ebb-canbus-v1.2.cfg)
- B4: [BIGTREETECH V1.1/V1.2 pinout](https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/EBB36%20CAN%20V1.1%20and%20V1.2/Hardware/EBB36%20CAN%20V1.1%26V1.2-PIN.png)
- K1: [Klipper CAN bus and termination](https://www.klipper3d.org/CANBUS.html)
- K2: [Klipper multi-MCU homing](https://www.klipper3d.org/Multi_MCU_Homing.html)
- A1: [Allegro A3141-A3144 datasheet](https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx)

Secondary: [Sedmenti AD5M conversion](https://github.com/sedmenti/FlashForge_A5M_raspberry). Its blower color/function mapping is not an independently verified HXH specification. Existing project photos confirm board identity and fan labels; they do not prove electrical continuity or successful powered operation.
