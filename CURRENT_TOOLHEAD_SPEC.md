# Current toolhead specification

Updated November 6, 2026 by explicit user correction.

- Printer: Flashforge AD5M rebuild.
- Toolboard: BTT EBB42. Supersedes EBB36 in previous planning.
- Exact EBB42 revision: V1.2.1, confirmed by user from the back of the board November 6, 2026. Original EBB42 family, not Gen2. MCU marking not independently inspected.
- Hotend: standard Bambu X1C, connector changed only, per existing build record.
- Extruder: retain the existing AD5M feeder and motor as the baseline. Primary goal is customization and design access, not improved extrusion performance. User reports the AD5M feeder + Bambu hotend performs very well.
- Current installed housing: BambuMod for FF Adventurer 5M, Printables model 1574762: https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m . User confirms this housing is currently installed and attached to the stock AD5M carriage mounts.
- Design starting point: use the installed BambuMod assembly and its stock carriage attachment as the reference. Preserve proven component alignment where useful; develop modular ducts, board bracket, covers and future carriage adapter around it. Local models located on desktop and inspected November 6: both STEP files contain valid solids. Exact mounting-hole dimensions and installed clearances remain to be verified.
- Toolboard bracket: design for the actual EBB42 hole pattern and connector envelope. A compact extruder with a 36 mm motor can still use EBB42 on a separate bracket; board choice does not establish motor compatibility.
- Wiring / firmware: previous EBB36 assignments require exact-revision EBB42 verification. No EBB42 pin map or flashed firmware is confirmed by this correction.
- Future direction: XY rails first after restoring printing; four complete interchangeable toolheads later.

## Local housing reference

Source folder: `C:/Users/PK800/Desktop/bambumod-for-ff-adventurer-5m-model_files/`.

- `bambumod_remix_and_vent_cover.step`: valid two-solid CAD model.
- `reverses_engineering_ad5m_bambumod.step`: valid single-solid CAD reference.
- Printable meshes: `bambumod-remix.stl`, `head-cover.stl`, `cable-clip.stl`.
- Included PDF identifies Kirill_Wawe, January 28, 2026; summary describes a P1S/P1P hotend housing and vented cover. This description does not supersede the user's confirmed X1C hotend hardware.
- PDF specifies CC BY-NC-SA 4.0.
- CAD validity and bounding boxes recorded in `outputs/bambumod_inspection/cad_inspection.json`. CAD bounding boxes are file-axis envelopes, not verified installed assembly dimensions.
- Start future customization from a copy of the combined STEP; preserve the existing desktop originals.

## Eddy Duo bracket prototype — November 7, 2026

User authorizes drilling the existing housing for inserts or plastic screws, while retaining the existing housing. R1 side bracket and drilling locator are saved in `outputs/Eddy_Duo_BambuMod_mount_R1/` and copied to Desktop/AD5M_Eddy_Duo_Mount_R1. Two new M3 insert centers, 20 mm apart, checked against source housing CAD. Full physical fan/carriage/frame and nozzle-height verification remains necessary before drilling. Refer to READ_ME_FIRST.md.

## Eddy Duo revision direction — November 8, 2026

Move the sensing coil closer to the nozzle, minimizing fore-aft offset. User confirms the LEFT MOUNTING HOLE ON THE EDDY DUO itself should anchor to the actual carriage. Prefer direct carriage attachment with a second rigid anti-rotation support. Stock carriage interface geometry is absent from the supplied housing CAD and must be located on the physical printer. R1 sidewall drill pattern is superseded as installation direction; R2 mounting holes are not yet designed. See outputs/Eddy_Duo_BambuMod_mount_R2/DESIGN_REQUIREMENTS.json.

## Temporary Eddy connection — November 8, 2026

User prefers direct USB from Eddy Duo to Pi 5 for the current setup, postponing the short local CAN connection until the integrated EBB42/Duo toolhead design. Actual USB/CAN selector position and flashed Eddy firmware are unverified. Preserve the EBB42 CAN plan independently; Eddy can communicate over USB while EBB42 uses CAN.

## Hotend CAD reference acquired — November 8, 2026

Downloaded and inspected Jorge/jorge_rui original X1C/P1P/P1S hotend STEP (Printables 533213): three valid solids. Reference and source/license metadata in reference/Bambu_X1_hotend_CAD/. Creator states approximately +/-0.2 mm, not independently certified. Nominal nozzle/Eddy component alignment saved in outputs/Custom_toolhead_reference_R1/Nozzle_Eddy_nominal_alignment.FCStd: nozzle tip Z=0; Eddy sensing-case bottom nominal Z=2.5 mm, width midpoint aligned in fore-aft direction. This allows nominal custom toolhead design without requiring a physical nozzle-height measurement first; final fit and calibration remain required. Reference layout is not the installed BambuMod assembly or a completed printable toolhead. Preserve original licensed hotend geometry as separate reference.

## Open EBB42 top bracket — November 8, 2026

User requests an open bracket with exactly two body/top-hat anchors, two EBB42 mounts, and two original strain-relief clip holes. Board tilt is 45 degrees from vertical, upper edge away from tube. User confirmed the 48 mm body-hole pair; the other pair is unused. R1 generated in outputs/EBB42_open_tophat_bracket_R1 and copied to Desktop/AD5M_Open_EBB42_Bracket_45deg_R1. Board pair 31 mm; clip pattern 14.5 mm from supplied cable-clip.stl, original physical clip match unverified. CAD valid single solid and watertight mesh; zero bracket/body overlap. Actual frame sweep, motor/connector and clip fit remain unchecked. This is an open replacement for the top cover, not a new bearing/belt carriage.

## EBB42 placement correction — November 8, 2026

User requires the EBB42 between the back of the carriage and the filament path. The prior open-bracket R1 put it outside the rear face and is superseded. User explicitly permits changing the angle; 45 degrees was only a starting point. Corridor study in outputs/EBB42_rear_corridor_study_R2 demonstrates a near-upright placement above the existing housing but adds approximately 26 mm above the old cover. Lower placements were found to intersect modeled housing features with multiple board components. No revised printable bracket is released from this study. Need reconcile compact rear-gap placement, real motor/gear clearances, and height before printing.

## EBB42 placement correction — November 8, 2026

User requires the EBB42 between the back of the carriage and the filament path. The prior open-bracket R1 put it outside the rear face and is superseded. User explicitly permits changing the angle; 45 degrees was only a starting point. Corridor study in outputs/EBB42_rear_corridor_study_R2 demonstrates a near-upright placement above the existing housing but adds approximately 26 mm above the old cover. Lower placements were found to intersect modeled housing features with multiple board components. No revised printable bracket is released from this study. Need reconcile compact rear-gap placement, real motor/gear clearances, and height before printing.

## Latest bracket — revised user sketch, November 8, 2026

R3 short U bridge in outputs/EBB42_sketch_bridge_R3 replaces the R1 bracket and R2 placement study. Uses four upward-facing cover holes (X +/-18 and +/-27, Y -7.498, axis Z), matching two holes per foot in the revised sketch; the prior 48 mm face pair is not used. Two 31 mm EBB mounting holes, two 14.5 mm supplied-clip pilot holes, 45-degree board supports and an open tube relief. Angle may be changed; user allows some PTFE flex. STL is one watertight solid; CAD checks have zero bracket/housing/board overlap. Board rear projection 11.85 mm from assumed housing plane, not validated against actual measured 13 mm clearance. Board top 19.47 mm above prior cover. Original clip pitch, motor, bearing carriage, plugs/cables and frame travel remain physical checks. Printable fit prototype; no claim of final installed fit.

## R4 bracket update — November 8, 2026

User removes strain-relief mounting from the current bracket and requests support-free printing. outputs/EBB42_sketch_bridge_R4 supersedes R3: no clip geometry/holes; two continuous ramps and pointed M3 bore roofs; extended footprint 60 x 35.5 x 17.85 mm. Print flat base down, supports off. Single watertight solid, zero CAD collisions, no downward surfaces beyond 45.2 degrees. Board placement and prior physical-clearance limitations unchanged.

## R5 radiused bracket — November 8, 2026

User requests radiused corners throughout, permitting sharp hole edges. R5 in outputs/EBB42_sketch_bridge_R5 supersedes R4: 1.2 mm main outline rounds and smaller edge blends, hole rims retained. Small edges adjacent to board-hole recesses preserved for seats and clearance. Final STL is watertight and one connected body; no CAD intersections; no large unsupported section regions at 0.2 mm spacing. Placement and physical fit limitations unchanged.

## R6 alternative — simple wedge, November 8, 2026

User approves the latest sketch interpretation: one central triangular wedge on a full rectangular plate; rounded exterior edges, sharp hole rims. Separate R6 alternative in outputs/EBB42_simple_wedge_R6; preserve R5 for the ongoing test print. Four housing holes unchanged. Two EBB holes are 2.5 mm plastic-threading pilots, 31 mm apart, axes normal to 45-degree mounting face. No nuts required; grip needs physical verification. Separate approximately 4 mm hardware spacers provide PCB back clearance. No clip mount. STL closed single solid, zero supplied housing collision; complete board arrangement and installed clearance unverified.

## R7 uniform posts — November 8, 2026

User requests removal of cut-in side shoulders on original two-post bracket. User approves making the entire post match prior 6.6 mm contact width after wider faces were found to intersect EBB reference components. R7 in outputs/EBB42_uniform_posts_R7 and Desktop/AD5M_EBB42_Uniform_Posts_R7; uniform sides, rounded edges, 2.5 mm M3 pilots normal to face. Original mounting coordinates and board pose retained. Single closed STL. No housing collision; two 0.003 mm3 overlaps with small cylindrical model objects concentric with EBB mounting holes remain in raw report; physical screw grip unverified. R5/R6 unchanged.

## Eddy adjustable mount proposal R3 — November 8, 2026

User wants to mount Eddy while installing EBB. R3 in outputs/Eddy_Duo_adjustable_side_mount_R3 and Desktop/AD5M_Eddy_Duo_Adjustable_Mount_R3: flat 4 mm side plate, two solid-edge housing anchors (original X30 Y-6 Z64/84), 20 mm pitch, two sensor slots 10.5 mm apart with 10 mm vertical travel, recessed M3 nut channels, rounded outline. Earlier direct-left-sensor-hole position is over honeycomb with insufficient material; proposal instead bridges to the solid edge, maintaining R2 near-nozzle fore-aft position. No bracket/housing overlap; anchor insert envelopes fully solid; STL watertight. New holes required and locator supplied for marking after dry fit. Actual nozzle height absent; set sensor bottom approx 2.5 mm above physical nozzle tip. This is a proposed printable fit prototype, not a calibrated installation.

## Eddy mount reinforced R4 — November 8, 2026

User identifies thin M3 nut walls. R4 side mount in outputs/Eddy_Duo_adjustable_side_mount_R4 and desktop equivalent widens nut-channel sections from 6.8 to 9 mm: side walls 1.6 mm, end walls 1.7 mm, front skin 1.5 mm. Mount hole coordinates, 10 mm adjustment, nut pockets and Eddy pose unchanged. Valid solid, watertight single mesh, zero housing overlap. Print sensor-contact face down, supports off; inspect perimeter count in slicer. R3 remains a fit-check option.

## Live commissioning & Eddy rapid-scan bed mesh — November 11, 2026

Printer commissioned with Octopus Pro V1.1 (STM32H723) + EBB42 V1.2.1 (CAN) + BTT Eddy Duo (USB) and completed a test print (`Voron_Design_Cube_v7_PETG.gcode`). Configured `EDDY_MESH` and KAMP `BED_MESH_CALIBRATE` for `METHOD=rapid_scan` (`horizontal_move_z=1.5`). Live mesh testing with the right-side Eddy mount (`x_offset = 44 mm`, `y_offset = 2.65 mm`) revealed a sharp apparent Z drop-off (`~0.35 mm`) when `probe_X > 196 mm` due to the Eddy's inductive magnetic field rolling off the right edge of the steel PEI build plate (`X ≈ 220 mm`). Capping `mesh_max: 195, 205` reduced full-bed variance from `0.506 mm` to `0.219 mm`, and motivated moving the Eddy inline with the nozzle in X (`x_offset = 0.0 mm`) for the new custom toolhead.

## Custom toolhead with inline front Eddy Duo R1 — November 11, 2026

User requests a custom toolhead keeping the proven BambuMod upper carriage / stock AD5M feeder backplate datums, stock `3010` hotend fan, and stock AD5M part-cooling blower, while skeletonizing/adapting the lower housing around the Bambu X1C hotend and centering the Eddy Duo inline with the nozzle in X (`x_offset = 0.0 mm`, `y_offset = -31.19 mm`). Released in `outputs/AD5M_custom_toolhead_inline_eddy_R1/` (`AD5M_Custom_Housing_R1` and `Eddy_Duo_Inline_Mount_R1`):
- `AD5M_Custom_Housing_R1`: preserves all rear carriage, feeder/motor, `3010` fan, and top EBB42 `R7` mounting holes; relieves the internal heatsink top-fin shelf (`52.05 mm3` reference overlap eliminated to `0.0 mm3`); reinforces the front left/right pillars with `6.0 mm` deep `2.5 mm` M3 plastic-threading pilot bosses (`24.0 x 8.0 mm` pattern at `X = ±12.0 mm, Z = 11.5 / 19.5 mm`); adds a support-free hexagonal side window on the upper `+X` wall; and relieves an upstream non-manifold knife-edge kiss so both STEP and STL are 100% manifold and watertight.
- `Eddy_Duo_Inline_Mount_R1`: `4.0 mm` flat front plate with rounded external and concave neck corners (`33.0 x 28.5 x 4.0 mm`), four `3.3 mm` housing clearance holes (`24.0 x 8.0 mm` pattern), two `3.3 mm` vertical sensor slots (`10.5 mm` pitch, `10.0 mm` vertical travel), and rear recessed `5.8 x 16.6 x 2.5 mm` M3 nut channels (`4.70 mm` center wall, `1.85 mm` outer side walls, `1.50 mm` front skin). Also backward-compatible with an unmodified `bambumod-remix` housing (`3.0 mm` solid front wall at all four anchor locations). Physical print and fit on printer required.
