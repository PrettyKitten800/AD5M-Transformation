# BootyCallJones K1 gantry design reference

Added November 3, 2026. The user previously installed the BootyCallJones linear-rail conversion on a K1 Max and selected it as an additional reference for the future AD5M XY redesign. The user no longer owns the K1 Max; it is not available for physical inspection or measurements. Use the published design and the user's installation experience alongside measurements of the AD5M.

## Archived source

- Project: https://github.com/tlace17/K1-Linear-Rail-Gantry
- Snapshot: `d4fa8b9919a68f8c4dd4b3dbbdcb9fd2c099fb25`
- Full repository ZIP and 69 extracted files are saved here. ZIP CRC check passed; provenance and SHA-256 are in SOURCE.json.
- `source/STEPs/` contains editable solid geometry for K1 Max XY joints, rail carriages, stepper mounts, tensioners, spacers and a pulley alignment tool.
- `source/STLs/` contains printable source parts. These are K1-family parts, not validated AD5M parts.
- Original license is retained in `source/LICENSE.md`; preserve attribution and review its terms before distributing derivatives.
- [Author-linked assembly guide](https://docs.google.com/document/d/1SqA1cdwyPaCVLiMiMXChLrdn-k710LjkxOklKdxjZtY/) and [installation video](https://www.youtube.com/watch?v=lZPC6AAUhGk). These external resources are linked, not archived or fully reviewed.

## Application to the AD5M project

Use this as a reference for practical gantry conversion details: XY joint construction, belt/idler packaging, tensioner access, carriage mounting and pulley alignment. Use the Voron Trident reference for the broader intended XY-rail/triple-Z architecture.

CoreXY machines share the motion principle, but mounting geometry and belt routing are not interchangeable. Measure the AD5M's frame interfaces, both belt planes, motor/idler centers, carriage and nozzle offsets, tensioner travel and motion envelope before adapting parts. A K1 Max component should not simply be scaled to the AD5M bed size.

The intended AD5M design includes rails on both X and Y. Inspect how the K1 conversion supports each axis before borrowing its joints; its rail conversion should not be assumed to supply a complete two-axis rail design for the AD5M. No rail sizes, lengths, pulley layout or derived parts have been selected or validated yet.

The exact BootyCallJones revision previously installed by the user is not established. Any comparison with that installation must rely on recollection or existing records, not access to the printer. Restore AD5M printing before gantry disassembly or conversion work.
