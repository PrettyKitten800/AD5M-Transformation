# Nozzle-to-Eddy nominal alignment reference — R1

**Status: reference data (still used).** Component alignment only; no carriage or fans included.

Created on 2026-11-08 from the original Bambu X1/P1 hotend STEP ([`reference/Bambu_X1_hotend_CAD/`](../../reference/Bambu_X1_hotend_CAD/)) and the Eddy Duo case:

- Nozzle tip at the origin (0, 0, 0), taken from the 0.4 mm orifice of the creator's model.
- Eddy case sensing bottom at Z = 2.5 mm, the nominal target height above the nozzle; Eddy width midline aligned fore-aft with the nozzle.
- About 6.2 mm X gap between the hotend envelope and the sensor case in this layout.

| File | What it is |
| --- | --- |
| `Nozzle_Eddy_nominal_alignment.FCStd` / `.png` | FreeCAD document and picture of the alignment |
| `alignment.json` | The numbers above |
| `preview_mesh.json` | Pre-tessellated preview read by `scripts/cad/render_custom_toolhead_inline_eddy_R1.py`; keep it, the renderer runs without FreeCAD |
| `reference_views.png` | Reference views |

The installed hotend is now a TZ 2.0 clone, so treat these heights as nominal. Final Eddy height is set and calibrated on the printer (`EDDY_TAP`).
