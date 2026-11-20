# Eddy marking buttons — no wraparound locator

The user clarified that the DRILLING HELPER/LOCATOR collides with the gantry rods/belts; the Eddy mounting plate itself was not identified as colliding. Keep the existing R3/R4 side plate for dry fitting. Do not use the wraparound locator shipped with those versions.

These two small slip-fit buttons center a 1.6 mm marking aperture inside the plate's existing 3.3 mm HOUSING-ATTACHMENT holes (the two round holes, 20 mm apart). They have no fences or tabs around the carriage. Do not put them in the slotted sensor holes.

## Print

Centering_button_PRINT_TWO.stl contains ONE button; print TWO COPIES at 100% scale. Collar flat on the bed, short sleeve up; already oriented. Supports off, 0.2 mm layers. The button has a 3.1 mm OD sleeve, 3.8 mm insertion length, 8 mm diameter x 2 mm collar and a 1.6 mm marking aperture. The 4 mm plate is thicker than the sleeve, so the sleeve stops about 0.2 mm before its back surface. Check fit without forcing it; a printed bore may need gentle clearing with a 1.6 mm bit before use.

## Use

1. Dry-fit the actual Eddy plate on the installed housing. Verify its position, sensor height adjustment, reachable solid housing material and access around rods/belts. These buttons DO NOT establish the plate's absolute position or prove clearance. The prior CAD anchor locations remain the proposed solid-edge locations; the failed locator did not validate those on the physical printer.
2. Insert a button into each round attachment hole FROM THE OUTSIDE of the plate, so its collar sits on the accessible face and its sleeve sits inside the plate thickness.
3. Hold or clamp the plate in the verified position. Use a fine marking point or a 1.6 mm bit turned gently by hand to locate the two centers. These are disposable centering aids, not drill bushings for powered drilling.
4. Remove both buttons and the plate. Check clearance behind the marked positions, then make the final pilot holes separately. For M3 screws threading into plastic, 2.5 mm is the nominal pilot used in this project; heat-set insert holes must follow the actual insert dimensions. Do not run a 2.5 mm drill through the 1.6 mm guide.

If the plate cannot be positioned reliably without the wraparound locator, document the actual accessible housing edges and collision location before drilling. A flat template does not replace a physical datum.

If you already have a suitable transfer punch or another way to center marks in the plate holes, no additional print is necessary.

Checked: valid CAD single solid; watertight consistently wound single STL body; sleeve length stops inside the plate thickness. This revision avoids the locator's wraparound geometry. Gantry geometry is still absent from the housing CAD, so installed access is not certified.

The Eddy mounting plate and sensor position are unchanged. The broad fixture in Guide_preview.png is a reference to the EXISTING plate; only print the small button STL.

Attribution: helper for the BambuMod-derived mount; shared under CC BY-NC-SA 4.0. Housing source Kirill_Wawe, https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m .
