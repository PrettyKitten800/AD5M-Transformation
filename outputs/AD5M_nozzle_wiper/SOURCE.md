# Flashforge AD5M Nozzle Wiper

Unmodified STL by Stormage, licensed CC BY-SA 4.0. Source: https://www.printables.com/model/1262881-flashforge-ad5m-nozzle-wiper

The printed frame mount accepts a Bambu A1 Mini silicone nozzle wiper. Verify clearance and wipe height with the installed Bambu X1C hotend and Eddy Duo before programming the wipe path. The downloaded STL is in the author's print orientation.

The OrcaSlicer project uses the rebuilt AD5M's 0.4 mm profile and Tinmorry ASA-CF preset, with 0.20 mm layers and three walls. The G-code prints the holder and uses the existing START_PRINT and END_PRINT macros.

## Right side concept

First try relocating the existing Stormage print farther back on the right side. Keep the silicone seat and use the print to locate the required inboard reach and mounting height before trimming it or designing a small adapter. A rearward shift addresses Y reach. Check X separately against the 213.4 mm nozzle limit.

The user prefers a wiper beside the right edge of the bed near the middle of Y travel. The live travel limits are X −10 to 213.4 mm and Y 12 to 220 mm. Start fit evaluation at approximately X210, Y116 and orient the silicone strip front to back for a Y-only wipe. Those coordinates are a provisional nozzle position. Locate the actual bed edge and attachment geometry on the printer before sizing an arm or clip.

[cwohltat's AD5M snap-on wiper](https://www.printables.com/model/1359952-snapon-nozzle-wiper-for-flashforge-ad5m) includes a STEP model useful as a clip reference. Confirm the right edge profile and clearance under the plate before adapting it. During a cold fit check, verify the complete duct and Eddy Duo sweep. The Eddy coil is configured 35 mm to the right of the nozzle, and the full scan reaches probe X210. Check clearance during bed motion, parking and probing, as well as the pad's intrusion into usable bed area. Measure the working Z and both wipe endpoints after fitting the pad.
