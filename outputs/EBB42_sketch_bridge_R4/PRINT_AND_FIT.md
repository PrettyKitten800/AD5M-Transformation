# EBB42 bridge R4 — no strain relief, support-free geometry

Supersedes R3 for printing. The original R3 files remain unchanged.

Changes:
- Removed strain-relief mounting holes and clip reference completely.
- Replaced the floating rail/gusset arrangement with two ramps growing directly from the feet.
- Extended the footprint beneath the ramps by approximately 6.5 mm; overall bracket 60 x 35.5 x 17.85 mm.
- Added pointed roofs above the M3 clearance bores.
- Restored full material around the four original cover screw seats.
- Kept the board angle, board position, 31 mm board screw pitch and housing screw coordinates.

Print EBB42_short_bridge_R4.stl at 100% scale, broad flat base on the bed (already oriented), supports OFF. Suggested first fit print: 0.2 mm layers, 4 walls, 35–40% infill. Use appropriate material for the eventual toolhead temperature. The assembly FCStd and STEP are editable references; print only the bracket STL.

Mounting: four upward-facing original cover locations, X +/-18 and +/-27 mm, Y -7.498 mm, holes 4.3 mm diameter. Reuse the actual housing fastener type with allowance for 4 mm base thickness. Two EBB mounts remain 31 mm apart with 3.3 mm round-bottom clearance and pointed roofs. Use M3 fasteners and washers; select screw length against the actual bracket/PCB/nut stack and ensure access before installation. No clip holes or clip-specific geometry remain.

Verification: one valid CAD solid; one connected, watertight, consistently wound STL. No bracket/housing/EBB CAD collisions. No downward-facing surfaces steeper than 45.2 degrees outside the bed contact face. Sections at 0.2 mm spacing contain only tiny corner departures from the ideal 45-degree offset at the pointed bore roofs (less than 0.09 mm), with no large unsupported ledges. These are geometry checks, not a completed physical print or a printer-specific extrusion test.

Fit limits unchanged: the EBB reference projects 11.85 mm behind the assumed housing rear plane and its top is 19.47 mm above the previous cover. The supplied housing CAD omits the installed motor, stock bearing carriage and printer frame. Check those, actual connectors, tube bend and full hand-moved travel before powering. Original EBB42 V1.1 CAD is used as reference for the user's physical V1.2.1 board.

Housing reference: Kirill_Wawe, BambuMod for FF Adventurer 5M, https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m , CC BY-NC-SA 4.0. Bracket shared under CC BY-NC-SA 4.0. Original housing files unchanged. Board reference: BIGTREETECH EBB original-generation EBB42 V1.1 STEP.
