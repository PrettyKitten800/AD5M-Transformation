# Recovered Printables 1404902 fan shroud for R8 — R4 (installed)

**Status: installed on the printer.** The user printed and mounted it on the [`R8` adapter](../BambuMod_Orbiter25_Remix_R8/) on 2026-11-19 and adjusted its Z height on the toolhead.

## Which file to print

| File | Use |
| --- | --- |
| **`Fan_Shroud_Recovered_PrintPose_R4.stl`** | **Print this one.** Shroud in its print orientation. |
| `Fan_Shroud_Recovered_R8_R4.stl` | Same shroud placed in `R8` assembly coordinates, for CAD checks only |
| `r8_recovered_shroud_r4_report.json` | Mesh and interference results |

## Lineage

1. Printables model 1404902, the AD5M lightweight fan duct for 5 × 2 mm magnets ([`reference/AD5M_Lightweight_FanDuct_1404902/`](../../reference/AD5M_Lightweight_FanDuct_1404902/)), recovered as `Fan_Shroud_Recovered.stl`.
2. [`R2`](../BambuMod_Orbiter25_R8_FanDuct_1404902_R2/): aligned onto `R8` around the shifted nozzle.
3. [`R3`](../BambuMod_Orbiter25_R8_FanDuct_1404902_R3/): magnet-tab rear faces trimmed flush with the shroud rear face (Y = −31.65 mm).
4. **R4** (this folder, built by [`scripts/cad/build_r8_recovered_shroud_R4.py`](../../scripts/cad/build_r8_recovered_shroud_R4.py)): the four pinned step/groove regions (left-front bevel, side walls, underside) flattened onto their main planes with Blender manifold booleans.

Mounting is by the two magnet pockets (Ø5.2 mm, at X = ±24.5 mm), as in the original model.

## Mesh and CAD checks (from the report)

- 26,966 facets, 15,145.67 mm³, one solid component, no non-manifold edges.
- The report flags **self-intersections** in this mesh (R3 does too; R2 did not). The printed part came out fine, but run a slicer mesh repair if a future slicer complains.
- 0.0 mm³ overlap with the `R8` adapter, Orbiter, X1C hotend reference, 3010 fan and carriage mock-up. Minimum gap 4.60 mm to the hotend and 8.78 mm to the Orbiter.
- CAD nozzle-to-bed clearance 2.03 mm, measured against the X1C reference nozzle. The real clearance is set by the installed TZ 2.0 clone and the Z-height adjustment made on the printer.

## Not recorded yet

- Print material and settings used.

## License

Based on Printables model 1404902. Its author and license are not recorded in this repository yet; see the reference folder's `SOURCE.md` and check the Printables page before sharing derivatives.
