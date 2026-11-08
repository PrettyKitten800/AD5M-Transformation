# AD5M Build working instructions

Read README.md and CURRENT_TOOLHEAD_SPEC.md before changing designs. This project prioritizes customization and reuse of the existing AD5M feeder/motor and Bambu X1C hotend. EBB42 V1.2.1 is confirmed; do not revert to EBB36 or Gen2. Eddy Duo uses USB for now.

## Current designs and physical feedback
- EBB42 two-post bracket: outputs/EBB42_uniform_posts_R7/. Uniform 6.6 mm angled posts, rounded edges, 2.5 mm M3 pilots. Prior R5 was printed and the user called it usable; R7 has not been confirmed printed.
- EBB42 simple wedge alternative: outputs/EBB42_simple_wedge_R6/. One central triangular wedge on a rectangular plate, 2.5 mm M3 pilots normal to face. User said this was printing; physical installation unconfirmed. Requires PCB-back spacers.
- Eddy side mount: outputs/Eddy_Duo_adjustable_side_mount_R4/. Reinforced 1.6 mm side walls / 1.7 mm end walls around M3 nut channels; 10 mm height slots; sensor hole pitch 10.5 mm. Earlier R3 was being printed for fit inspection. R4 not physically tested.
- Current BambuMod structural housing: reference/BambuMod/. Preserve originals and source attribution.

Keep old revisions. Do not call a CAD or mesh check a physical fit test. Full motor/stock bearing carriage/frame motion geometry is absent. Do not infer the actual nozzle height from the housing bounding box. Eddy sensing bottom target is approximately 2.5 mm above the physical nozzle tip, adjustable on the printer. Earlier left-Eddy-hole direct mount placement overlapped vent openings; current proposal uses two new solid-edge anchors, source CAD X30 Y-6 Z64/84.

User expects simple geometry faithful to sketches, rounded external edges, sharp hole rims allowed, and support-free printing. Avoid adding structures beyond the requested change. Mount positions and board orientation must not silently change. Typical M3 plastic-threading pilots are modeled at 2.5 mm; clearances are 3.3 mm. Check actual print and material before promising screw grip.

## Files, tools and checks
scripts/cad/ contains portable copies of the current three builders and renderers. Historical work/ scripts retain Windows/Desktop paths; do not treat those as cloud paths. CAD builders need native FreeCAD Python modules FreeCAD, Part and MeshPart, not the unrelated PyPI package named freecad. Rendering/check packages are listed in requirements-cloud.txt. Have cloud setup install a compatible native FreeCAD runtime and test its imports before claiming CAD generation works.

After geometry changes validate one valid CAD solid, a watertight consistently wound single STL body, unchanged datums where required, and actual relevant CAD clearances. Investigate reference-fastener overlaps separately from electronics collisions. Inspect a CAD preview. Run checks proportional to the change. Keep hardware source attribution/license files; mixed third-party content has no blanket project-wide license.

Large upstream checkouts and duplicate ZIP archives remain local and are ignored. Their sources/provenance are retained in reference/. Do not delete local data to reduce repository size. Avoid committing credentials, .env files or machine flash-readback backups.
