# Recovered 1404902 fan shroud for R8 — R2

**Status: history.** Kept for provenance; do not print or design from it without checking [`CURRENT_TOOLHEAD_SPEC.md`](../../CURRENT_TOOLHEAD_SPEC.md). Superseded by `R3` and then [`R4`](../BambuMod_Orbiter25_R8_FanDuct_1404902_R4/), the installed shroud.

Built by [`scripts/cad/build_r8_recovered_shroud_R2.py`](../../scripts/cad/build_r8_recovered_shroud_R2.py). It takes `reference/AD5M_Lightweight_FanDuct_1404902/Fan_Shroud_Recovered.stl`, rotates it −90° about X into `R8` coordinates and moves it onto its mating position on the adapter (dx +0.80, dy −49.59, dz +0.70 mm). It aims at the shifted nozzle at (+6.335, −11.78, −28.23) mm, with magnets at (±24.5, −30.04, 3.35) mm.

- `Fan_Shroud_Recovered_PrintPose_R2.stl` is byte-identical to the recovered source mesh in `reference/`. `Fan_Shroud_Recovered_R8_R2.stl` is the placed copy.
- Report: 26,726 facets, 15,290.93 mm³, one component, no self-intersections; 0.0 mm³ overlap with `R8`, Orbiter, hotend reference, 3010 fan and carriage mock-up.
