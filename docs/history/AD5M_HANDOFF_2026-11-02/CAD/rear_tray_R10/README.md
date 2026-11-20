# AD5M rear electronics tray — DRAFT R10

This is a printable first draft for the Octopus Pro V1.1, a bare Raspberry Pi 5 with the installed active cooler, and a ReliaBot MOSFET module. It targets the stock rear-cover position. It has not been test-fitted in a printer.

R10 supersedes R9. The three cable-tie pads (each with two small openings) now have 2 mm radius outer corners. Overall dimensions remain 167 x 172 x 5 mm, with a 2 mm base and 3 mm standoffs. All mounting holes remain through holes.

## Files

- `rear_tray_DRAFT_R10.stl`: full carrier, 167 × 172 × 5 mm overall; 2 mm base and 3 mm integral standoffs above it. The 5 mm is the plastic only, not the assembled electronics height.
- `rear_tray_DRAFT_R10.step`: editable solid geometry.
- `expanded_footprint_fit_check.stl`: 1.2 mm outline with six reference mounting holes. Use this new template to check the full draft footprint; the earlier 167 × 142 template checks only the smaller reference adapter.
- `MOSFET_52p5x42p5_pattern_check.stl`: a 60 x 50 x 1.2 mm coupon with 52.5 x 42.5 mm hole spacing. This uses your final dimensions, with 52.5 mm horizontally and 42.5 mm vertically. Compare it with the loose module before the full print.
- `layout_preview.png`: component arrangement. Colored rectangles show PCB footprints, not complete connector or wiring envelopes.
- `parameters.json` and `rebuild_model.py`: adjustable source. Requires Python, CadQuery and trimesh. Edit board origins, tray dimensions, pilot diameters or assumed MOSFET size or user-estimated pitch, then run the builder. The STEP file can also be edited directly in a CAD application.
- `validation.json`: exported geometry checks.

## Open frame and rounded standoff roots

The plate is now a network of 4 mm wide perimeter/support rails, 3.5 mm diagonal braces and local mounting pads, rather than a mostly filled plate with small ventilation windows. All mounts remain joined in one printable piece. A 1.5 mm radius concave fillet blends each 8 mm diameter standoff into its pad; this stays below the 3 mm standoff top and does not increase the 5 mm overall height. The 2 mm dimension applies to the flat ribs/base; the curved transitions rise above that plane locally. This is a geometric revision, not a stiffness or load-test result.

## What is established, and what is provisional

The mounting-hole coordinates were extracted from sedmenti's `CAD/Main_board_adapt.step`, shifted by +66.5 mm in X and +71.5 mm in Y. The four main holes form a 112 × 132 mm rectangle. Two auxiliary holes are retained on the right. All six are 3.3 mm clearance holes. Use the auxiliary holes only where corresponding attachment points exist in your printer.

The Octopus mounting pattern is 90 × 150 mm in this orientation; its PCB footprint is 100 × 160 mm. The Pi has a 49 × 58 mm mounting pattern in this orientation and a 56 × 85 mm PCB. Its USB/Ethernet end faces upward in the preview. The side-facing Pi USB-C power connection also needs room for its plug and bend; its route relative to the nearby PSU must be checked. The PCB gap is now 5 mm between Octopus and Pi, and 3 mm between Octopus and the assumed MOSFET footprint. These are PCB-edge gaps, not verified connector clearance. The side-facing Pi power plug may need a low-profile connection or another board orientation; a normal plug is not confirmed to fit within this width. Connector bodies, plugs and cable bends may extend beyond the colored rectangles and tray outline.

R10 uses your final MOSFET hole spacing: 52.5 mm along X and 42.5 mm along Y. The assumed 60 x 50 mm PCB retains its R5 position. Outer dimensions and installed height remain unverified. Compare the coupon with the loose module before committing to the full tray. If it differs, revise the parameters and regenerate the model.

The tray now matches the 167 mm width of the reference adapter and extends 30 mm below its 142 mm height. That extra lower area has not been verified against the printer housing, bed-ribbon breakout, fan shrouds, PSU, existing wires or cover ribs. Matching the reference width and mounting holes alone does not establish complete printer fit. The rear cover and connector envelopes have not been modeled.

Your estimate gives 35 mm nominal depth. The board undersides are 5 mm above the tray's back face. A component envelope measured from the PCB underside must therefore be at most 25 mm to meet the preferred 30 mm installed height, or less than 30 mm to leave any clearance within the estimated 35 mm space. Actual usable depth may vary locally. PCB components, driver heatsinks, plugs, screw heads and cooler airflow all need checking. No claim is made that the installed assembly already meets the depth target.

## Printing and fitting

1. Print the small MOSFET coupon and expanded footprint template first, at 100% scale, flat face down. They need no supports. The MOSFET can be checked now, without opening the printer; check the larger template when the printer is opened for the conversion.
2. If the template aligns and the added footprint is unobstructed, check the real boards and cable paths against the layout before printing the full tray. Resolve any obstruction by revising the draft.
3. Use a 0.20 mm layer height, including the first layer, for the 2 mm base and 5 mm overall height. Start with 4-5 walls and enough top/bottom layers to make the thin ribs solid (5 top and 5 bottom layers at 0.20 mm); inspect the sliced preview. Print flat face down with posts up, at 100% scale, without supports or mirroring. PETG is used in the reference project; choose a material suitable for the actual compartment temperature. All pieces fit a 220 x 220 mm build area with room for a brim.
4. Board mounting bores pass through the complete 5 mm height: diameter 2.5 mm for the Octopus/MOSFET and 2.0 mm for the Pi. These retain the existing screw pilot diameters; they are not enlarged clearance holes for loose M3/M2.5 bolts. Suggested starting fasteners remain M3 x 4 plastic-thread screws for the Octopus/MOSFET and M2.5 x 4 for the Pi, subject to actual board thickness and fit. Select screw length so the tips do not project into the chassis or adjacent wiring. Do not force or over-tighten.
5. Fit the empty tray to the existing chassis attachment points first, then the boards: some chassis screws are beneath the board footprints. Check original chassis-screw length for the new 2 mm base. Chassis screw heads under a PCB must be lower than 2 mm above the plate surface, and must clear every underside component.
6. Verify the closed cover clears all installed parts and cables, and that the Pi cooler and driver heatsinks have an airflow path. The ventilation windows and tie slots are mounting features; they do not validate operating temperatures.

This carrier is for rear electronics only. TMC2209 drivers plug into the Octopus. EBB36 and Hall-sensor mounts belong on the toolhead/axes and are not included here. No board-specific FPC breakout mount is included; its dimensions and location still need accommodating in the installation.

## Sources

- Reference adapter and EBB36 conversion: https://github.com/sedmenti/FlashForge_A5M_raspberry
- Alternative conversion, including different mainboard/toolhead and housing modifications: https://github.com/ChaoticWeaponry/AD5M_HardwareReplacement
- Octopus dimensions: https://global.bttwiki.com/Octopus%20Pro.html
- Pi 5 mechanical drawing: https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf
- LRS-350 nominal 30 mm thickness: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF
- User's MOSFET: https://www.amazon.com/dp/B078S6221G
- User's Pi kit: https://www.amazon.com/dp/B0DFMNHL62

The tray is newly constructed geometry using measured reference mounting coordinates. Repository STL meshes were not copied into it.

Validation completed: valid single CAD solids; watertight single-component STL meshes with consistent winding and positive volume; mounting pitches and open holes checked. Physical fit, fastener fit, electronics clearance and thermal performance remain unverified.
