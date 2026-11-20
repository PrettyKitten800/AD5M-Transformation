# AD5M inline Eddy toolhead R2

Local design review, November 11, 2026. Open the FreeCAD assembly or preview first. The new housing and detachable cradle have STEP and STL exports. The STLs are in millimetres and oriented for slicing. Physical fit and full travel are open.

## How it mounts

The two rails carry the probe from the rigid housing around the outside of the front cooling module. The magnetic fan cover carries its original blower and duct. Removing four side screws releases the cradle for front-cover access. The housing retains the original rear carriage interface, feeder/motor cavity, hotend-fan seat, front shroud seats, filament entry and upper mounting pattern. Its four 2.5 mm blind pilots replace the earlier drilling helper. Material removal also provides local relief at the modeled X1C heatsink and an imported mesh-edge defect. There is no added housing material inside the feeder cavity or behind the carriage.

The cradle has rounded rails, two 3.3 mm holes per side on a 20 mm vertical pitch, and 0.30 mm total assembly clearance over the nominal 60 mm body. Select the housing screws using the measured ear thickness and about 3 mm thread engagement. The blind pilots are 4.0 mm deep. Two M3 screws and nuts secure the Eddy in the 10.5 mm pitch slots. The pockets open toward the duct, and the slots provide 6 mm total adjustment. Set the sensor bottom against the physical nozzle reference. The model shows 2.5 mm.

## Cooling and travel

The loose fan photos identify the HXH HBB0524VD part blower and Peerless DF3010B24H hotend fan. The front reference is the local part-fan-short-mk2.stl seated on the 49 mm magnet pattern. The user reports their installed duct has the stock shroud clearances. The exact installed file is unknown. The gray blower block and the 3010 frame represent the space required by the fans. The original blower, existing duct, heatsink fan, feeder, motor, heater, thermistor, EBB42 V1.2.1 and USB Eddy are intended for reuse. Transfer the current board mounting hardware and harness as installed. The R7 carrier and sibling-revision board are shown only to visualize the upper interface.

The candidate duct clears the cradle by at least 2.0 mm and the Eddy case by at least 7.07 mm. Both bounds use actual transformed duct geometry. The candidate duct tip falls 1.12 mm below the nominal X1C tip. Check the real nozzle-to-duct height before using these datums. The sensor case midpoint is 52.27 mm ahead of the reference nozzle, centered in X. This geometric estimate needs physical coil calibration.

The case projects 25.37 mm past the modeled front shroud before adding the USB plug and cable. Measure available front clearance at sensor height at the forward travel limit. The unplugged model does not establish access to the whole bed, cable flex, probe stiffness, or moving gantry clearance. The feeder/motor and rod/belt assembly have no complete installed model in this revision. Existing attachment geometry is preserved.

## Files and sources

- Toolhead_layout_R2.FCStd contains the proposed parts and individual component references. Toolhead_preview.png shows the complete cooling module and a second view with the cooling module removed.
- Side_interface_housing_R2.step / Housing_R2.stl and Front_cradle_R2.step / Front_cradle_R2.stl are the two proposed parts. The housing lies on its rear face and the cradle on the lower rails. Both meshes passed single-body, watertight and winding checks. Support settings have not been tested on the printer.
- checks.json records the numeric checks. build_layout.py uses native FreeCAD and takes the local candidate duct STL as its argument. check_layout.py uses FreeCAD's VTK and Pillow to reproduce the preview and contact checks.
- Housing derived from Kirill_Wawe's BambuMod under CC BY-NC-SA 4.0. Keep attribution and share-alike terms with the housing. https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m
- Unchanged Jorge X1C reference, CC BY-ND 4.0. https://www.printables.com/model/533213-bambu-lab-x1c-p1p-p1s-original-hotend-3d-model
- BTT board and shared-family Eddy CAD come from the project references. The local duct's upstream attribution is unresolved. The combined assembly is a local review file. The new project reference at GitHub revision 2517aa9 supplies the Eddy orientation and the R7 carrier reference.
