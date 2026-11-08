# Stock AD5M gantry CAD and belt references

Checked November 3, 2026. This research supports the later XY rail conversion; restoring stock-mechanics printing remains the immediate priority.

## CAD availability

No verified downloadable CAD for the stock moving gantry end blocks, toolhead carriage, or motor/idler mounts was located in this search. This does not establish that no private or unindexed models exist.

The official archive already saved in this folder supplies frame/enclosure geometry. Its frame preview shows the bare structural frame with mounting holes, without the XY motion hardware. STEP product names include an `AD5M XY` assembly name, but the name alone is not evidence that the moving gantry or its mounts are included. The frame is useful for a mounting-hole reference, subject to measurement against the actual printer.

- [Official frame STEP](official_frame_model/AD5M_Frame.STEP)
- [Official frame preview](official_frame_model/AD5M_Frame_Preview.png)
- [Official source page](https://www.flashforge.com/a/docs/knowledge-corner/printer-mod-and-diy)
- [Community request for stock XY/carriage/motor/pulley files](https://www.reddit.com/r/FlashForge/comments/1gn0lez/adm5_stl_step_files/): firsthand reports of unsuccessful searches and reverse-engineering belt clips; no downloadable stock assembly found in the inspected thread.

## Official belt and gantry service references

1. [Flashforge: Adjust & Replace the XY-axis Synchronous Belt](https://wiki.flashforge.com/en/adventurer-series/maintenance/ad5mseries-adjust-and-replace-the-xy-axis-synchronous-belt)
   - [Direct video](https://www.youtube.com/watch?v=_mpRY145f-Y)
   - Page HTML archived as `belt_service.html`.
2. [Flashforge: Replace the XY-axis Guide Rail & Bearing](https://wiki.flashforge.com/en/adventurer-series/maintenance/ad5mseries-replace-the-xy-axis-guide-rail%26bearing)
   - [Direct video](https://www.youtube.com/watch?v=PvCuDEtlrYU)
   - Page HTML archived as `guide_bearing_service.html`.

Both wiki pages are labeled for the Adventurer 5M series; the linked video titles say Adventurer 5M Pro. Their video links were extracted from the official pages. The videos themselves have not been fully reviewed frame by frame or archived. The wiki pages contain video embeds rather than a readable, dimensioned belt diagram. Here, the manufacturer's term "guide rail" refers to the stock guide system and should not be interpreted as an MGN conversion.

No verified dimensioned AD5M belt-routing drawing was located. Exact pulley order, belt-plane heights, pulley diameters and clamp geometry remain unmeasured. Do not substitute a generic CoreXY or Trident diagram for an established AD5M route.

## Record before later gantry disassembly

- Trace each belt separately, from one toolhead clamp around every pulley to its other clamp; label the motor and every idler.
- Record belt height at each pulley and clamp, and which belt surface contacts each pulley.
- Measure pulley centers relative to frame datums, shaft/rail heights, mounting-hole spacing, and motor tensioner travel.
- Photograph the top, rear motor mounts, gantry end blocks, and toolhead belt clamps with the paths still intact.
- Use these observations to make a measured stock layout before deciding whether the rail conversion should retain or revise that routing.

This measurement plan does not require delaying the current electrical rebuild or disassembling the working stock gantry now.
