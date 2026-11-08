# AD5M linear-rail conversion research

Searched November 3, 2026. XY gantry redesign is the first upgrade after the printer is working again. Triple Z and toolchanging remain later projects.

## Result

No completed AD5M XY conversion with verified downloadable MGN rail mounts, gantry CAD and build instructions was located in this search. This is a limited search result, not proof that nobody has built one. Search engines may omit private groups, unindexed files and unpublished work.

Queries included AD5M / Adventurer 5M with linear rail, rail conversion, MGN9, MGN12, gantry, CAD, STEP and Russian rail terminology. Site-targeted searches covered GitHub, Printables and MakerWorld. GitHub repository searches for `AD5M rail`, `Adventurer 5M gantry` and `Flashforge linear` returned zero repositories. No claim is made that private sites or every model library were searched exhaustively.

## Useful reference found and downloaded

[Flashforge's official Printer Mod and DIY page](https://www.flashforge.com/a/docs/knowledge-corner/printer-mod-and-diy) provides `ad5m-printer_source_model.zip`, described as an AD5M frame model for DIY work. Saved here with source metadata and archive checksum in SOURCE.json. ZIP integrity passed.

- [AD5M frame STEP](official_frame_model/AD5M_Frame.STEP)
- [Frame preview](official_frame_model/AD5M_Frame_Preview.png)
- [Enclosure STEP](official_frame_model/AD5M_Enclosure.STEP)

The archive also includes PDF previews and SolidWorks assembly files. The STEP files are the preferred neutral-format starting point; completeness of SolidWorks dependencies has not been established. This is frame/enclosure reference geometry, not a verified complete motion-system model. Dimensions and available mounting surfaces must be checked against the physical printer.

## Leads that do not establish a conversion

- [Sleeper project: CAD files](https://www.reddit.com/r/FlashForge/comments/1l95fuf/sleeper_project_cad_files/): a builder describes searching for AD5M Pro gantry CAD and planning a new gantry; the inspected thread supplies no completed rail conversion files.
- [ILYASmod public preview](https://t.me/s/ILYAS_mod_AD5m?before=173): inspected results show enclosure, lighting and spool-holder work, not a verified XY rail conversion.
- Results using the word "rail" frequently refer to stock guide shafts, enclosure features or unrelated printer conversions. Those were not counted as conversion evidence.

## Starting approach when the gantry project begins

1. Establish a measured frame and mounting-hole model using the official STEP as reference.
2. Lay out both CoreXY belt planes, motor/idler locations, carriage envelope, nozzle reach and travel limits together.
3. Compare one X rail plus two Y rails against the available frame surfaces. Choose rail sizes and lengths from the measured layout, not nominal bed size.
4. Prototype mounting/clearance parts before committing to the complete gantry. Include alignment provisions and verify free motion across travel.
5. Use a replaceable toolhead mounting plate where practical so a future coupling can be evaluated without forcing toolchanger design into this upgrade.

These are planning steps, not a validated mechanical design or parts order. The already archived Voron Trident design is the architectural reference, not a drop-in AD5M conversion.
