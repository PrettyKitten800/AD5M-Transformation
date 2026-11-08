# R7 — uniform angled posts

Revision of the original two-post bracket, not the simple-wedge R6. Both previous versions remain unchanged.

Each angled post now has one continuous 6.6 mm width through to its PCB contact face. The full post matches the old contact-face width; the wider body and cut-in side shoulders are removed. Widening the contact face instead was checked and rejected because it touched small components in the EBB reference model.

The 45-degree board angle, board position, 31 mm board screw pitch, four housing fastener positions and rounded exterior are retained. Base footprint approximately 60 x 35.5 mm; bracket height approximately 17.85 mm. The wider feet remain for attachment/support; the angled posts above them have uniform sides.

EBB pilot holes are 2.5 mm, normal to the board face, following the user's latest M3 plastic-threading preference. They are pilot bores, not modeled helical threads. Select screw length for the actual PCB stack and about 5 mm plastic engagement; snug gently. Actual grip and stripping strength need a physical check. Housing holes remain 4.3 mm at the original four locations. Hole rims stay sharp.

Print the STL at 100% scale, flat base down, supports OFF. Suggested fit print: 0.2 mm layers, 4 walls, 35–40% infill. Check the layer preview and first-layer adhesion along the small rounded underside edges.

The final exported STL is a closed, consistently wound single body. The supplied housing has no bracket collision. See validation.json in the workspace output for the complete CAD intersection report, including any tiny overlaps with cylindrical reference items concentric with the EBB mounting holes. Those reference items do not establish actual screw fit. No physical print of R7 has been tested.

Installed motor, bearing carriage, plugs/cables, filament routing and full frame travel remain physical fit checks. The board top is still approximately 19.5 mm above the original cover; board placement has not changed.

Housing source: Kirill_Wawe, BambuMod for FF Adventurer 5M, https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m , CC BY-NC-SA 4.0. Bracket shared under CC BY-NC-SA 4.0. Original source housing files unchanged. Board reference: original-generation BIGTREETECH EBB42 V1.1 CAD, user's actual board V1.2.1.
