# AD5M wiring map R3 — CONTROL polarity assigned by user

This is a circuit connection plan for the user's Octopus Pro V1.1 H723, EBB36 CAN V1.2.1 without MAX31865, Raspberry Pi 5, ReliaBot MOSFET, stock bed and sensors, X1C hotend, and two loose A3144 sensors. It is not a connector-face pin-position drawing. Amber routes are incomplete and must remain disconnected until their stated details are resolved. Continuity checks are deferred, not completed.

## Power and communications

Use the existing stock 24 V DC supply and preserve its protective-earth connections. The drawing does not modify mains wiring. Provide appropriately protected DC distribution, with terminal capacity, conductor sizing and fuse selection finalized before assembly. Do not put an arbitrary number of wires under one screw.

| From | To |
|---|---|
| PSU V+ | Octopus POWER + |
| PSU V- | Octopus POWER - |
| PSU V+ / V- | Octopus MOTOR-POWER + / - |
| PSU V+ / V- | Octopus BED-POWER + / - |
| PSU V+ / V- | ReliaBot DC IN + / - |
| Protected 24 V branch + / - | EBB36 VIN / GND |
| Pi kit power adapter | Pi USB-C power input |
| Pi USB-A data port | Octopus USB-C |
| Octopus CAN H / L | EBB36 CAN H / L |

The Octopus is planned to run Klipper USB-to-CAN bridge firmware, allowing it to control its own motors while connecting the Pi to the EBB36. A separate U2C is therefore not part of this plan. Verify firmware configuration for this board. EBB36 firmware uses its CAN interface. Use a twisted H/L pair and two 120-ohm terminations, one per physical end; confirm which terminations are built in and which need jumpers or external resistors. The Octopus CAN connector carries communications; do not expect it to power the EBB. The EBB combines separate DC power and CAN contacts in one four-contact plug. Match the actual +, -, H, L markings, not a mirrored rear photograph.

TMC2209 supply must be 24 V in this build. Check each driver's supply-selection jumper and orientation using the V1.1 manual. Set UART mode for the three used drivers. Proposed motor assignments: MOTOR0=CoreXY A, MOTOR1=CoreXY B, MOTOR2=Z. Match each connector to its driver socket, not just the connector's position in a row. MOTOR3A and MOTOR3B share one driver; they are not independent axes. The fourth purchased driver is spare. Motor coils, rotation direction, UART setup and current require configuration.

## Bed

| Breakout pin(s) | Purpose | Destination |
|---|---|---|
| 1-11 together | Heater negative | ReliaBot HOT BED - |
| 12-22 together | Heater positive | ReliaBot HOT BED + |
| 23 | Bed-sensor board supply | Octopus 5 V |
| 26 | Bed probe signal | Compatible Octopus input; exact header and voltage compatibility pending |
| 28 | Bed-sensor board ground | Octopus GND |
| 29 | Bed thermistor lead | One TB contact |
| 30 | Bed thermistor lead | Other TB contact |
| 24,25,27 | Unused by the reference conversion | Leave unconnected and insulated |

The pin map comes from ChaoticWeaponry's conversion, not a completed electrical verification of this particular harness. Each group of eleven heater wires must terminate into a suitably sized heater lead; a single 22 AWG lead must not carry the combined load. The user's breakout wires are 22 AWG solid and must stay fixed and supported; moving runs need flexible stranded wire. Secure and insulate all joins. The reference uses groups of five and six 22 AWG wires into two 16 AWG leads, then a 12 AWG lead for each heater pole. Actual splice methods and wire insulation ratings still need selection.

Octopus BED-OUT + connects to the CONTROL wire beside the + marking, as identified by the user on 2026-10-30. BED-OUT - connects to the other CONTROL wire. This is the agreed wiring premise, not an independent measurement. BED-OUT - is the switched return: do not substitute PSU DC ground for it. BED-POWER must be supplied for the bed output to supply this control signal. The heater itself is supplied through the external ReliaBot, not through the Octopus BED-OUT.

The stock bed probe signal and stock Z-endstop sensor are separate circuits. Do not combine their outputs. Z endstop and filament runout require individual signal assignments; identify their connector orientation and voltage compatibility first.

## Toolhead

| EBB36 connection | Load or sensor |
|---|---|
| Motor / EM | Extruder motor with two correctly paired coils |
| HE0/E0, PB13 | X1C heater pair; heater has no polarity |
| TH0, PA3 | X1C thermistor pair; no polarity |
| Fan output PA0, VIN and switched negative | Peerless hotend fan, 24 V 0.09 A |
| Blower control interface, pending | HXH HBB0524VD, 24 V 0.25 A, four wires |
| Two inputs, allocation pending | X and Y A3144 sensor outputs |

PA0 is intentionally assigned to the hotend fan to match the AD5M reference's allocation; BTT's generic sample assigns it differently. Match the final Klipper configuration to this drawing. Physical fan socket names vary between diagrams; identify the socket by its PA0 mapping. Powering this EBB at 24 V supplies its fan VIN at 24 V. Fan negative is a switched output, not permanent ground.

For an NTC on TH0, leave the PT1000 jumper removed (4.7 kohm pull-up). The exact X1C thermistor curve must be selected independently; BTT's sample EPCOS sensor setting is not confirmation of the Bambu sensor curve. Configure and tune heater control before heating. Leave VUSB removed during normal operation on 24 V; it is only needed when deliberately powering the electronics through USB for setup.

The AD5M project's blower diagram identifies red=24 V, black=GND, blue=PWM, yellow=speed feedback. This remains a reference mapping rather than independent verification of this exact blower's specifications. It proposes a switched fan output as PWM control, but its electrical compatibility has not been established. Reserve PA1 for blower control if that interface proves suitable; otherwise use a suitable logic/open-collector interface and revise the map. Do not connect the blue wire to 24 V. Yellow feedback has no destination assigned; insulate it individually. The blower's power negative must be real ground if using a separate PWM-control wire.

A3144 sensors: use 5 V supply and common ground, separate X/Y open-collector outputs with pull-ups to 3.3 V. Verify actual sensor package leg orientation and the selected board input pull-ups. Exact EBB signal header allocation is pending because the AD5M illustration and BTT examples disagree. Configure multi-MCU homing appropriately for CoreXY motors on the Octopus and endstops on the EBB; do not copy the reference configuration blindly.

## Sources

- BTT Octopus Pro hardware: https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-Pro
- BTT Octopus power and driver setup: https://global.bttwiki.com/Octopus%20Pro.html (use V1.1-specific files for pin assignments)
- BTT EBB36 hardware: https://neo.bttwiki.com/en/docs/board-docs/ebb-series/ebb-36/ebb-36-hardware
- BTT EBB V1.2 sample: https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/sample-bigtreetech-ebb-canbus-v1.2.cfg
- Klipper CAN and bridge requirements: https://www.klipper3d.org/CANBUS.html
- AD5M bed breakout: https://github.com/ChaoticWeaponry/AD5M_HardwareReplacement/blob/main/Mainboard/Photos/m8p-accessory-pinouts.jpg
- AD5M fan adaptation: https://github.com/sedmenti/FlashForge_A5M_raspberry/blob/main/IMG/fan_part.png
- A3144 original datasheet: https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx?la=en

Sources consulted 2026-10-29. User photos establish board markings, fan ratings and physical arrangement; they do not establish electrical continuity or absence of shorts.
