> **Hardware correction — November 6, 2026:** The current toolboard specification is **BTT EBB42**, replacing EBB36. Exact EBB42 revision and MCU are not yet established. Historical EBB36 wiring, connector positions, pin assignments, firmware settings and mounting drawings below are not an approved EBB42 wiring plan; verify against the exact EBB42 documentation before use. The X1C hotend and other established build components remain the current baseline.

# AD5M electronics replacement: build sequence

## Priority update — November 2, 2026

The user has ordered a replacement Octopus Pro for the defective board. Immediate scope is restoring reliable single-tool printing with the existing XY mechanics and single-motor Z drive. Triple Z is a long-term goal; a four-head toolchanger is a longer-term goal. On November 3, the user selected an XY linear-rail gantry redesign as the first upgrade after restoring printing; it is not a prerequisite for recovery. Confirm the replacement board revision/MCU on arrival, test the board independently, then finish the existing wiring and staged commissioning below. No additional mainboard drivers are required for this stage if the existing modules are serviceable: three used, one spare. See UPGRADE_ROADMAP.md for the current priority and future research.

Prepared November 1, 2026. Current power wiring is in `outputs/AD5M_HE0_wiring_R5/`; its HE0 revision supersedes the old BED-OUT assignment. The older R3 photo overlays and connection notes are archived in `reference/wiring_R3/`. These are planning references, not a record of tested wiring.

## Current priority: toolhead first

User changed the assembly order: complete the unpowered EBB36 toolhead harness before the rear assembly. Follow `TOOLHEAD_FIRST.md` for this stage. The numbered stages below describe the remaining work; rear assembly is no longer the starting task.

## 1. Unpowered rear assembly — start here

- [ ] Unplug the printer and Pi power adapter. Preserve the stock mains wiring and protective earth.
- [ ] Photograph and label original connections before removing any remaining stock electronics.
- [ ] Dry-fit the printed carrier in the printer. Check mounting alignment, clearance behind the circuit boards, screw lengths, connectors, cable bends, cooler clearance and rear-cover fit. The original depth estimate was not a physical fit measurement.
- [ ] Mount the Octopus, Pi and ReliaBot. Keep conductive hardware and exposed conductors clear of the undersides of the boards.
- [ ] Check that wiring can reach the terminals without pulling on connectors or blocking the Pi cooler and driver airflow.
- [ ] Keep the bed heater, hotend heater and moving toolhead harness disconnected during this stage.

## 2. Lay out and label the power harness

Measure actual routed lengths with service slack before cutting. The intended wire allocation below assumes correctly rated copper wire, insulation, connectors and branch protection. Final fuse selection and distribution hardware still need to be established.

| Label | From | To | Planned conductor |
|---|---|---|---|
| MAIN | 24 V distribution + / - | Octopus POWER + / - | 16 AWG stranded copper |
| MOTORS | 24 V distribution + / - | Octopus MOTOR-POWER + / - | 16 AWG stranded copper |
| BED CONTROL SUPPLY | From Octopus main POWER internally | HE0 output; BED-POWER unused | No separate branch |
| BED HEATER SUPPLY | 24 V distribution + / - | ReliaBot DC IN + / - | 12 AWG stranded copper |
| TOOLHEAD POWER | Protected 24 V branch + / - | EBB36 VIN / GND | CAN cable power pair, reported 18 AWG |
| BED CONTROL | Octopus HE0 + / - | ReliaBot CONTROL + / - | Supplied control cable |

CONTROL positive is the wire beside the + marking, by the user's instruction. CONTROL negative returns to HE0 negative; it must not be substituted with PSU ground. This polarity is an agreed premise, not an independent measurement.

Fork lugs are for compatible captive screw terminals, with correct stud and wire sizes. Octopus wire-entry terminals require an appropriate stripped-wire or ferrule termination. Use the correct crimp contacts for the toolhead cable. Provide appropriate distribution capacity rather than stacking an unspecified number of lugs under one screw. The two CAN data conductors must form a twisted pair; the cable's product specifications and contact layout are still unverified.

## 3. Board preparation and communications

- [ ] Use the exact Octopus Pro V1.1 H723 documentation to establish driver orientation, UART jumpers, driver supply selection and USB power configuration.
- [ ] Assign three TMC2209s to the two CoreXY motors and Z; the fourth purchased driver is spare. The EBB36 includes the extruder driver.
- [ ] Configure the Pi and identify the board firmware/bootloader arrangements before flashing. Keep heaters disconnected during bring-up.
- [ ] Planned communication: Pi USB -> Octopus USB-to-CAN bridge -> EBB36 CAN. Establish CAN H/L connector contacts and end termination before plugging in the harness.
- [ ] Use the kit PSU for Pi power initially. A suitable internal 24 V-to-5 V supply is a later addition.

## 4. Bed and toolhead harnesses

Use the full connection notes for the bed pin map. Pins 1-11 form one heater pole, 12-22 the other; pins 29 and 30 remain separate thermistor leads. User's 22 AWG solid breakout wires stay fixed and supported; use flexible stranded wire in moving sections. Finish, insulate and support the high-current joins before use.

The remaining assignments are actual unfinished design work, not just continuity checks:

- Four-wire HXH blower: electrical PWM interface and final connection.
- A3144 X/Y: package leg orientation and exact EBB input allocation.
- Bed probe, stock Z endstop and filament sensor: compatible inputs and exact contacts.
- X1C thermistor curve and final heater configuration.
- ReliaBot HOT BED output contact polarity on the physical module.
- DC branch protection, terminal capacity and final cable contact assignments.

## 5. Electrical checks and staged commissioning

Continuity and polarity checks were explicitly deferred by the user; they have not been performed. A multimeter is needed before first power-up. Start with isolated electronics and disconnected heaters, verify supply rails and communications, then sensors, motors, and finally one heater at a time with suitable firmware protection and temperature configuration. Never insert or remove drivers or motor connectors while powered.

The next practical milestone is the carrier fitted inside the printer, with the rear cover checked and the power branches laid out and labeled. That can proceed before the unresolved toolhead interfaces are finalized.

