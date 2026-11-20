# R5: external bed MOSFET controlled from HE0

This revision supersedes the earlier BED-OUT control drawings. The user has connected the ReliaBot CONTROL plug to Octopus HE0.

- PSU 24 V still supplies Octopus POWER and MOTOR-POWER, ReliaBot DC IN and a protected EBB power branch.
- Octopus BED-POWER and BED-OUT are unused and do not need supply wiring for this arrangement.
- HE0 positive (VIN) -> MOSFET CONTROL positive, using the user's identified positive CONTROL wire.
- HE0 negative (PA0 switched output) -> MOSFET CONTROL negative. Do not substitute PSU ground.
- The external MOSFET DC IN supplies bed-heater current. Its HOT BED output feeds the breakout's heater groups as previously mapped.
- Bed thermistor remains on TB / PF3; the probe connections remain unchanged.
- In the existing Klipper [heater_bed] section, set heater_pin: PA0 (Octopus HE0), replacing PA1 / BED-OUT. Keep the correct bed sensor configuration and tune bed control for the completed system.
- No other Octopus configuration section may own PA0. The hotend heater is controlled by the separate EBB36 MCU (PB13).
- Optional LEDs are now reserved on Octopus HE1 / PA3, subject to electrical-rating confirmation. HE0 is no longer available for LEDs.

The EBB hotend fan uses its own PA0, e.g. head:PA0 or EBBCan:PA0. That is a different physical MCU pin from Octopus PA0, so there is no conflict when the configuration correctly names the MCUs.

Reference: https://github.com/Klipper3d/klipper/blob/master/config/generic-bigtreetech-octopus-pro-v1.1.cfg (HE0=PA0; HE1=PA3; TB=PF3).
