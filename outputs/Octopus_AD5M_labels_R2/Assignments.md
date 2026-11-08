# AD5M labels adapted to Octopus Pro V1.1 H723

The diagram uses the user's actual board photograph, rotated 180 degrees, with native vector annotations. The board image is not regenerated. Label placement was checked against BTT's V1.1 pinout.

| Printer connection | Proposed Octopus destination |
|---|---|
| External bed MOSFET CONTROL | BED-OUT, PA1; polarity follows the user's CONTROL-wire identification |
| Bed-output supply | BED-POWER +24 V and ground |
| Main board supply | POWER +24 V and ground |
| Driver supply | MOTOR-POWER +24 V and ground, with driver selectors configured appropriately |
| X / CoreXY A motor | MOTOR0, driver 0 |
| Y / CoreXY B motor | MOTOR1, driver 1 |
| Z motor | MOTOR2, driver 2 |
| Stock Z endstop | STOP2, PG10 / GND / 5 V |
| Bed probe from breakout 23,28,26 | Three-pin PROBE: DC set to 5 V / GND / PC5 |
| Bed thermistor, breakout 29 and 30 | TB, PF3 / GND; no thermistor polarity |
| Filament runout | STOP3, PG11 / GND / 5 V |
| EBB CAN | CAN L and CAN H; EBB needs separate DC power contacts |
| Pi communication | USB-C, with the Octopus configured for USB-to-CAN bridge mode |
| Chamber fan 1, optional | FAN0, PA8 |
| Chamber fan 2, optional | FAN1, PE5 |
| Mainboard fan, rating unconfirmed | FAN2, PD12 |
| Stepper cooling fans, ratings unconfirmed | FAN3, PD13 |
| 24 V LEDs, optional and rating unconfirmed | HE0, VIN / PA0 |

These are chosen assignments, not evidence that the sensors and optional accessories have been electrically tested. Match the final firmware configuration to them. Fan/LED voltage and current must be established before connecting those loads. The existing Manta example includes optional chamber hardware not established in this build.

In the photo's displayed orientation, the three-pin PROBE connector reads top-to-bottom: DC supply, GND, PC5 signal. Configure its supply selector to 5 V, and its optocoupler/pull-up and firmware for the actual bed probe's output behavior. Do not copy the Manta five-pin probe contact order. Octopus also has a distinct five-pin BLTouch-style header, which is not this assigned connection.

The EBB36 Endstop header has +5 V, GND, PB6, PB5, PB7 in the order pictured by BTT. Use X=PB6 and Y=PB7 per the AD5M guide; PB5 is unused. Earlier notes claiming a discrepancy with PB3/PB4 were incorrect: those are a different expansion header. A3144 outputs need pull-ups to 3.3 V. Physical sensor-leg identification remains required. Do not confuse EBB36 PB6/PB7 with similarly named Octopus pins.

Sources:

- https://raw.githubusercontent.com/bigtreetech/BIGTREETECH-OCTOPUS-Pro/master/Hardware/BIGTREETECH%20Octopus%20Pro%20V1.1-Pin.jpg
- https://raw.githubusercontent.com/bigtreetech/docs/master/docs/img/EBB36CAN/G0B1/EBB_G0B1_Pin.webp
- https://github.com/sedmenti/FlashForge_A5M_raspberry/blob/main/Klipper/printer.cfg
- https://global.bttwiki.com/Octopus%20Pro.html


R2 adds the actual ReliaBot photograph. CONTROL positive uses the user-identified wire beside the + mark; the other wire returns to Octopus BED-OUT negative. Blue output leaders identify the HOT BED pair without claiming its individual contact polarities.
