# EBB42 short bridge R3 — fit prototype

Based on the user's revised U-bridge sketch. Replaces the earlier R1 bracket and R2 placement study.

## Files
- EBB42_short_bridge_R3.stl: bracket only, flat base at Z=0, dimensions in mm. Import at 100% scale.
- EBB42_short_bridge_R3.step: editable bracket in housing assembly coordinates.
- EBB42_bridge_assembly_R3.FCStd: bracket with separate housing, EBB42 and supplied clip references. Print only the bracket STL.
- Bracket_preview.png and Assembly_preview.png: CAD previews.

## Geometry and fasteners
- Bracket envelope 60 x 29 x 17.85 mm; 4 mm base, two angled board supports, open center and open-ended 8 mm tube relief.
- Four upward-facing original cover holes: X=-27,-18,+18,+27 mm; Y=-7.498 mm in assembly coordinates. Two holes per foot, matching the revised sketch. Hole diameter 4.3 mm. Reuse the correct existing fastener type; allow for the new 4 mm base thickness and avoid bottoming in the housing. This supersedes the previously selected 48 mm front-face pair.
- Two EBB42 lower-row holes, 31 mm apart, diameter 3.3 mm. Use M3 screws and nuts; inspect the actual screw stack before choosing length. Mounting posts stop at the PCB back plane, leaving approximately 3.85 mm between rail and PCB underside.
- Two clip pilot holes, 14.5 mm apart, diameter 2.7 mm, for gentle M3 threading in plastic. With a 3 mm-thick clip, M3x6 gives about 3 mm engagement without protruding below the 4 mm base. Confirm the ORIGINAL stock strain-relief clip spacing first: 14.5 mm comes from the supplied BambuMod cable-clip STL and has not been confirmed against that physical clip.
- Board is tilted 45 degrees from vertical, leaning away from the nominal filament inlet. The tube may need to bend forward; the bracket has an open relief, not a captured tube hole.

## First print
- Print with the broad flat base on the bed; the STL is already oriented this way.
- Suggested fit-print settings: 0.2 mm layers, 4 walls, 35–40% infill. PETG is suitable for assessing fit; use a heat-suitable material for the installed part.
- Inspect the layer preview under the angled rails. The gussets include short bridges; add local supports from the bed if your printer cannot bridge those regions cleanly. Remove supports before installing the PCB.
- Fit the empty bracket first. Check all four attachment locations, extruder/motor clearance and the original clip. Then fit the board and tube without powering it.

## Checked limits
The CAD bracket is one valid solid; the exported STL is watertight, consistently wound and one connected body. No positive-volume intersections were found between bracket, housing and the referenced EBB42, or between the supplied clip and EBB42.

The official reference is original-generation EBB42 V1.1 CAD; the user's physical board is V1.2.1. Actual connectors, mounting screws and attached plugs must be checked.

Board rear projection is 11.85 mm from the assumed housing rear plane, compared with the user's approximately 13 mm rear clearance. This comparison does not validate the measured plane or allow for mating plugs/cable bends. Board top is approximately 19.47 mm ABOVE the old cover top. Check full gantry travel by hand before powering; this may require the previously discussed nozzle/carriage height change. No build-volume reduction is specified by this model.

The supplied CAD excludes the stock bearing carriage, feeder/motor assembly and printer frame. Their installed clearance is unverified. This is a printable fit prototype, not an installation-certified assembly.

## Source and attribution
Housing reference: Kirill_Wawe, BambuMod for FF Adventurer 5M, https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m , CC BY-NC-SA 4.0. Original user-provided source files remain unchanged. Bracket shared under CC BY-NC-SA 4.0.
Board reference: BIGTREETECH EBB GitHub repository, original EBB42 V1.1 STEP. Board and housing are reference components, not printed as part of this bracket.
