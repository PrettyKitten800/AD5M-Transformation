# Custom dual-horn part-cooling duct for R8 — R1

**Status: history.** Kept for provenance; do not print or design from it without checking [`CURRENT_TOOLHEAD_SPEC.md`](../../CURRENT_TOOLHEAD_SPEC.md). This was an original duct design for `R8`. The project switched to the recovered Printables 1404902 shroud instead; [`R4`](../BambuMod_Orbiter25_R8_FanDuct_1404902_R4/) of that line is installed.

Built by [`scripts/cad/build_r8_part_cooling_duct_R1.py`](../../scripts/cad/build_r8_part_cooling_duct_R1.py). It attaches below the Orbiter onto `R8`'s front face with Kirill's two Ø5.1 mm magnets, keeps the BambuMod front radial-blower cavity for the stock AD5M blower, and splits the airflow into two horns around the shifted nozzle.

- `R8_PartCooling_Duct_R1.step` / `.stl` (6,836 facets), `r8_fanduct_report.json`.
- Report: valid solid, 11,243.92 mm³, 2.0 mm nozzle-to-bed clearance against the X1C reference; 0.0 mm³ overlap with `R8`, Orbiter, hotend reference, 3010 fan and carriage mock-up; minimum gap 2.35 mm to the hotend.
