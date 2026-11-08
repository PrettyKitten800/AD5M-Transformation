> November 8 revision: user requests the Duo left mounting hole attach directly to the carriage and the probe move closer in line with the nozzle. This R1 sidewall drilling layout is superseded as the installation direction; retain only as a prototype reference. R2 geometry awaits the actual carriage interface.

# Eddy Duo / existing BambuMod housing — R1 fit prototype

November 7, 2026. Designed from your desktop BambuMod combined STEP. The housing itself is not modified in these files. User permits drilling / inserts; this bracket uses two NEW holes.

## Print

- Eddy_Duo_side_bracket_R1.stl: one bracket, supplied flat on its 4 mm face. 35 x 27.25 x 4 mm print envelope.
- Drill_locator_1p6mm_R1.stl: one locating/marking template, flat broad face on bed with registration fences up. 1.6 mm pilot/marking holes. It is a short-use plastic positioning aid, not a hardened drill bushing.
- Hole_pitch_coupon_R1.stl: optional 20 mm pitch / M3-clearance fit coupon, not an installed part.

Use ABS/ASA for a service bracket near the hotend. A PETG fit prototype is reasonable but must be checked for softening in actual service. Suggested initial profile: 0.2 mm layers, 4 perimeters, 5 top/bottom layers, 40% infill. Supports should not be needed in supplied orientations. These are proposed settings, not a tested print profile.

## Attachment and hardware

The bracket goes on the side shown in the preview, attached to the solid narrow edge beside the honeycomb vent. The probe projects forward of that edge so the bracket does not cover the honeycomb opening.

Two new housing attachment holes: 20 mm vertical spacing, each 5.117 mm from the original front-face plane toward the housing interior. In the agreed upright orientation, centers are 8.218 mm and 28.218 mm above the main housing's lowest CAD extent. Original STEP coordinates: X=30, Y=-6, Z=84 and 64. Do not use the top lid as a drill datum.

Use two M3 heat-set inserts approximately 4 mm long, with an outer envelope no greater than the checked 4.2 mm diameter. The CAD contains material around that envelope for its full 4 mm depth at both locations, but the real printed wall and any inside components must be checked. Final pilot diameter must follow YOUR insert specification; the template's 1.6 mm holes are for locating only. Do not assume a 4.2 mm drill is appropriate for a 4.2 mm insert.

Suggested bracket fasteners: two M3x8 with washers, checking engagement and bottoming in the actual inserts. Probe: two M3x30 screws, washers and M3 nuts, checking actual casing thickness and screw length. Sensor fastening holes are 10.5 mm apart; bracket slots are 3.3 mm wide and provide 12 mm center travel. Clamp with washers, without crushing the sensor case. Hardware lengths remain physical-fit selections.

Alternatively, use an appropriate plastic-thread screw and pilot hole after checking your material and wall. Machine screws do not establish their own suitable thread in an undrilled printed wall. This alternative has not been dimensioned as a specific screw system here.

## Fit and installation sequence

1. Print the bracket and locator. Hold the bracket and real Duo on the housing BEFORE drilling. Check that the coil can sit 2–3 mm above the actual nozzle tip within the slot range. The nozzle tip is not present in the source CAD, so nominal probe height is not a calibrated installed height.
2. Check the bracket side shown against your actual blower, fan screws, hotend wires, carriage and frame at the full XY travel limits. The housing-only collision check cannot verify these absent parts. Probe extends beyond the original side and front envelope and may reduce usable XY reach. Stop and revise placement if it cannot clear.
3. Remove the housing from the toolhead before drilling. The locator registers on the front-face and bottom-edge datums shown by its two fences. Confirm both fences seat on the real housing, without rocking. If they do not seat, do not drill from that template; verify the dimensioned hole positions instead.
4. Mark centers through the locator. Remove it for final drilling to the insert manufacturer's pilot size. Install inserts from outside after verifying inside space, then attach bracket.
5. Attach Duo, slide to set its sensing bottom face 2–3 mm above the clean nozzle tip, then tighten both screws. Keep connector / CAN-selector access and cable slack. Use the actual Duo connector pinout and previously verified EBB42 CAN wiring.
6. Move through the full travel by controlled commissioning before probing. Recalibrate probe height and XY coil offsets from the real assembly; housing relocation later requires reassessment.

## What was checked

- Bracket, locator and coupon are each a valid single CAD solid; exported STLs are closed meshes.
- Bracket intersection with supplied housing: 0 mm3.
- Both proposed insert envelopes: 100% within main housing CAD material.
- Reference sensor clears housing in X by approximately 4.10 mm. Its mounting face touches bracket's outer face, without penetrating their bounding boxes.
- Vents remain uncovered by the bracket in the modeled placement.

Not checked: physical fit, actual nozzle location, full-frame/carriage clearance, existing fan and wires, hotend heat exposure, print tolerances, exact Duo casing revision or functional probing. R1 is a fit prototype; do not drill until the real parts pass the dry fit.

## Files / sources

- Eddy_Duo_BambuMod_assembly_R1.FCStd: editable FreeCAD assembly; includes separate housing, bracket, official sensor reference, and drill-template reference. Hide/remove the drill-template reference when assessing operating clearance.
- Individual STEP files: bracket, template, coupon.
- Housing_and_bracket_reference_R1.step: supplied housing plus designed bracket, retaining source coordinates.
- parameters.json and validation.json: dimensions and checks.

Housing: user-supplied BambuMod for FF Adventurer 5m, Kirill_Wawe, Printables 1574762; supplied PDF identifies CC BY-NC-SA 4.0. Retain that attribution for shared reference housing derivatives.
https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m

Sensor reference: official BTT EDDY.STEP (shared-family reference; actual Duo must be checked), retrieved November 7, 2026.
https://github.com/bigtreetech/Eddy/blob/master/3D/EDDY.STEP
BTT Eddy Series Manual 20250507, dimensions and mounting height:
https://github.com/bigtreetech/Eddy/blob/master/BIGTRRETECH%20Eddy%20Series%20User%20Manual%2020250507.pdf
