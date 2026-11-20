# AD5M rear nozzle brush with 5 mm more reach

Adapted from [Tinkering Poko’s MK2](https://www.printables.com/model/1168757-flashforge-ad5mpro-nozzle-brush-using-bambulab-a1) under CC BY 4.0. The mount uses the existing M4 fasteners and a Bambu A1 silicone brush. The screw interface and silicone recess retain their original geometry. The seat moves 5 mm toward the bed, increasing overall reach from 22.8 to 27.8 mm. The author published MK2 as an untested clearance revision. Installed clearance with the extended seat remains to be checked.

The Orca project sets the part on its end with tree supports and a 5 mm brim. It uses the rebuilt AD5M’s 0.4 mm profile, Tinmorry ASA-CF, 0.20 mm layers and three walls. Orca estimates 46 minutes and 3.7 g. The project uses the printer’s existing start and end macros.

## Establish the wipe path

1. Fit the holder and silicone strip. Check the lip and fasteners as the bed moves through the wipe and print positions. The added 5 mm projects closer to the print and mesh area.
2. With the nozzle cold, locate the strip’s actual X ends, wipe Y, and working Z on the installed machine. Find a clear approach and exit with the bed lowered. Check the duct and Eddy housing throughout the travel, including homing, the rear park and the rear edge of the mesh.
3. Start with a short straight X stroke over the right end of the strip. Live Klipper reports an Eddy coil offset of X+35, Y0. At the stroke’s leftmost nozzle position, the left edge of the Eddy enclosure must remain to the right of the strip and holder with clearance. Use the measured enclosure edge. The configured coil offset alone cannot establish that clearance.
4. Once the cold pass clears, use those measured coordinates for a standalone wipe macro. For startup, place the verified wipe after homing and before `KAMP` and the existing purge. Repeat the checked approach and exit at a clearance Z and use a fixed Y and Z during the wipe.

The live travel limits are X −10 to 213.4 mm and Y 12 to 220 mm. The author’s sample path uses a different installation. This project includes no live wiping motion.
