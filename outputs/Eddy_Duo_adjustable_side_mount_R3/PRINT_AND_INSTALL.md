# Eddy Duo adjustable side mount R3 — proposed fit prototype

This is a new printable proposal using the near-nozzle fore-aft location from the accepted R2 placement. It is separate from the EBB42 brackets at the top of the toolhead. It replaces the R1 forward sensor position. R2 was a placement-only study.

## Design
- 4 mm flat side plate; approximate print footprint 33 x 30 mm; radiused outline (0.8 mm).
- Two housing attachments, 20 mm apart, on the SOLID edge beside the honeycomb vent.
- Two 3.3 mm slots, 10.5 mm apart, with 10 mm vertical adjustment for the Eddy.
- Recessed channels accept standard M3 nuts, approximately 5.5 mm across flats and 2.4 mm thick. Channels are 5.8 mm wide and 2.5 mm deep. Nuts sit inside the plate so they do not protrude against the housing. Fit the nuts into the channels before attaching the plate.
- No EBB board attachment holes are shared; installing either top bracket does not locate the Eddy height.

The earlier preference for the Eddy's left hole to attach DIRECTLY to the housing cannot be realized at the proposed location: the sensor hole lies over vent openings. A 4.2 mm insert envelope there is mostly unsupported in the supplied CAD. This plate bridges to solid material while retaining the near-nozzle position. Both new housing anchor locations have a full 4.2 mm diameter x 4 mm deep solid-material envelope in the CAD.

## Printing
Print Eddy_Duo_adjustable_mount_R3.stl at 100% scale. It is oriented SENSOR-CONTACT FACE DOWN, with recessed nut channels up. Supports OFF. Suggested fit print: 0.2 mm layers, 4 walls, 40% infill. Use a heat-suitable material for the installed toolhead. The STL is one connected, watertight, consistently wound body.

## Hardware
- Two M3 screws into the housing (or matching inserts). With this 4 mm plate, M3x8 plus a washer gives roughly 3.5 mm plastic engagement; confirm actual geometry and screw stack.
- Two M3 sensor screws, two M3 nuts and washers for clamping the height slots. Choose screw length against the ACTUAL Eddy case; its screw path is not established by the housing CAD. Avoid bottoming or contacting internal sensor electronics.
- 2.5 mm pilot bores if threading M3 screws directly into printed housing plastic; insert holes depend on the actual insert dimensions. The 4.2 x 4 mm envelope is a material check, not a universal insert drill specification.

## Location and installation
This design requires TWO NEW HOUSING HOLES. Hole centers in original BambuMod STEP coordinates: X=30, Y=-6, Z=64 and 84 mm. Dry-fit the plate and actual sensor before marking or drilling. The exact printed housing and access to its interior must be checked.

Optional_anchor_locator_R3.stl uses the same two verified anchor positions, with 1.6 mm marking guides. It seats against the outer side face, adjacent front edge and bottom datum of the supplied housing CAD. It is reused from the original solid-edge locator; the SENSOR POSITION is now different. Confirm the locator seats unambiguously on your actual print; use it only to mark the two anchor centers, then remove it to drill the final pilot/insert holes. Its CAD overlap with the housing is negligible (0.00024 mm3 at coincident datum faces).

Attach the plate with the nut channels against the housing. Fit the Eddy to its two slots. The preview uses a nominal screw height of original CAD Z=82. The actual nozzle tip is absent from the housing model, so that nominal height is NOT a calibrated installation datum. Use the slots to set the sensor's bottom approximately 2.5 mm higher than the nozzle tip (the middle of the previously discussed 2–3 mm mounting range), then perform the relevant Eddy calibration. If 10 mm travel does not cover the actual nozzle/case geometry, revise the mount rather than forcing an assumed position.

## Checked and unchecked
CAD: valid single bracket solid; zero bracket/housing overlap; full insert-size material at both new anchors. The sensor placement uses the official shared-family EDDY case mesh; actual Duo case and hole fit must be checked. The bracket occupies part of the side vent, consistent with the earlier accepted placement concept. Actual nozzle XY offset, airflow, motor internals, original bearing carriage, frame/bed travel and USB plug/cable bend are not certified by this model. The complete printer and nozzle are not present in the supplied CAD.

The teal top bracket in the preview is the R6 simple EBB wedge reference. It does not imply either EBB bracket has been installed. R5/R6/R7 files remain unchanged.

## Attribution
Housing: Kirill_Wawe, BambuMod for FF Adventurer 5M, https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m , CC BY-NC-SA 4.0. Bracket/locator shared under CC BY-NC-SA 4.0. Original files unchanged. Sensor reference: BIGTREETECH Eddy repository shared-family EDDY STEP, not a certified measurement of the physical Duo.
