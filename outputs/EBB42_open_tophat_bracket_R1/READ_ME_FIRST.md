> SUPERSEDED: board was positioned outside the carriage back. User requires it between carriage back and filament path, with angle allowed to change. Do not print this R1 as the intended final arrangement.

# Open top-hat replacement bracket for EBB42 — R1 fit prototype

November 8, 2026. Designed for the existing BambuMod structural body supplied by the user. Replaces the top cover with an open bracket; does not require reprinting the BambuMod body. No Eddy mount is included in this bracket.

## Six functional mounting holes

| Interface | Count | Center spacing | Modeled holes |
|---|---|---|---|
| BambuMod body: user-confirmed front-face pair near top-cover division | 2 | 48 mm | 4.4 mm clearance |
| EBB42: two lower-row board holes | 2 | 31 mm | 3.3 mm clearance |
| Strain-relief clip | 2 | 14.5 mm | 3.3 mm clearance |

The second pair of holes on the BambuMod face is not used. Body hole centers were derived from the supplied CAD; user confirmed the 48 mm pair. Do not drill new housing holes for this bracket.

The clip pattern comes from cable-clip.stl in the supplied BambuMod folder. Its measured center spacing is approximately 14.501 mm, with a small 0.061 mm fore-aft discrepancy rounded to a common centerline. This is a reference for reusing the original AD5M clip; the actual stock clip still needs a physical spacing check. Reuse the actual stock clip if it matches; it is not necessary to print the supplied clip.

## Board orientation

EBB42 leans 45 degrees from vertical, upper edge away from the filament-tube axis, with components/connectors outward. It has two screw posts approximately 3.85 mm high above the carrier rails, providing clearance behind the PCB. Original 20 mm spacers included in BTT's reference CAD are excluded.

The board CAD is BTT's original-family V1.1 reference, used for the user's V1.2.1 board. Check the actual connector and underside clearances. This is a mechanical bracket, not a revised wiring diagram.

Nominal model heights in the upright design coordinates:
- Old top-cover reference maximum: 96.218 mm.
- Bracket maximum: 93.345 mm.
- Board reference maximum: 93.691 mm.
- Supplied clip reference maximum: 95.000 mm.

Thus the modeled solid assembly is below the old cover maximum. This does not certify clearance against the frame: the 45-degree board projects forward, and plugs/cable bends, motor, extruder internals and carriage are not fully represented. The cyan tube in the preview is a nominal 4 mm outside-diameter placement reference derived from the housing's filament-axis location, not a measured routed tube.

## Print and dry fit

1. Print Six_hole_spacing_coupon.stl first. The three pairs are arranged on one flat coupon: 48 mm (larger holes), 31 mm, and 14.5 mm. Check each against its actual component separately. The rows are a print aid and not their assembled positions.
2. Print Open_EBB42_45deg_bracket_R1.stl after the patterns match. Suggested starting settings: ABS/ASA, 0.2 mm layers, four perimeters, five top/bottom layers, 40% infill. PETG can serve for a cool fit prototype.
3. Supplied STL stands on the carriage-attachment crossbar. Use a brim as needed and supports beneath the horizontal strain-relief bridge; inspect the tilted screw posts and mounting-hole overhangs in the slicer. No tested slicer profile is supplied.
4. Fit to the selected existing body holes with appropriate original fasteners or matched replacements. The 4.4 mm bracket holes are clearance holes; they do not identify the thread type in the housing. Account for the added 4 mm bracket thickness and verify engagement without bottoming out.
5. Board holes and clip holes are through-clearance holes for M3 hardware, not modeled threads or heat-set pockets. Use nuts/washers where needed. Select lengths from the actual stack. Board mounting stack is roughly 3 mm carrier + 3.85 mm post + PCB; clip stack is roughly 4 mm bridge + clip. Tighten without flexing the board or crushing the clip.
6. Check board backside, extruder access, filament path and strain-relief routing. With the machine unpowered, check full XY reach and front-frame clearance, including the actual cable plugs. Do not assume equal maximum Z height alone proves clearance.

## Files and validation

- Open_EBB42_45deg_bracket_R1.stl: full bracket, one connected watertight mesh.
- Open_EBB42_45deg_bracket_R1.step: editable neutral solid.
- Open_EBB42_bracket_assembly_R1.FCStd: separate bracket, existing body, and tilted board reference. Clip/tube visual references appear in the PNG, not as objects in this native assembly.
- Bracket_and_BambuMod_reference.step: bracket plus existing body in assembly coordinates.
- Six_hole_spacing_coupon.stl / .step: flat hole-pattern check.
- Preview PNGs: assembly and unobstructed bracket views.
- parameters.json / validation.json: dimensions and recorded checks.

Validated single CAD solid, closed mesh, and zero bracket/body intersection. Bracket print envelope approximately 58 x 28.77 x 37.34 mm; solid volume approximately 7.36 cm3. This is an unprinted fit prototype, not a verified installed design.

## Reference attribution

BambuMod for FF Adventurer 5m, Kirill_Wawe, supplied desktop files / Printables 1574762. Included source PDF identifies CC BY-NC-SA 4.0. Existing body reference retained without modification.
https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m

Official BTT EBB42 original-family V1.1 CAD reference, obtained from bigtreetech/EBB. Hardware selection is the user's EBB42 V1.2.1.
https://github.com/bigtreetech/EBB
