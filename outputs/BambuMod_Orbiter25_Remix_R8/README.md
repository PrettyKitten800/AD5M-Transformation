# BambuMod × Orbiter v2.5 adapter — R8 (installed)

**Status: installed on the printer** (user-confirmed 2026-11-20), carrying the [`R4` fan shroud](../BambuMod_Orbiter25_R8_FanDuct_1404902_R4/).

`R8` is the live parametric version of the BambuMod × Orbiter v2.5 carriage adapter. It is rebuilt from cached `R7` solids by [`scripts/cad/r8_live_builder.py`](../../scripts/cad/r8_live_builder.py) (a rebuild takes a few seconds). [`scripts/cad/r8_web_server.py`](../../scripts/cad/r8_web_server.py) with `scripts/cad/r8_web_workspace/` serves a browser viewer. `Open_R8_Live_FreeCAD.cmd`, `open_r8_freecad.ps1`, `R8_Live_Watcher.FCMacro` and `Open_R8_Web_Workspace.cmd` are the Windows launchers.

## Files

| File | What it is |
| --- | --- |
| `BambuMod_Orbiter25_R8_Live.stl` | Printable mesh of the adapter |
| `BambuMod_Orbiter25_R8_Live.step` | CAD solid of the adapter |
| `R8_Live_Workspace.FCStd` | FreeCAD workspace with the adapter and reference parts |
| `r8_params.json` | Current parameter set used by the builder |
| `r8_live_report.json` | Derived dimensions and interference results from the last build |
| `r8_shared_notes.json` | Annotations saved from the web workspace |
| `r8_user_snapshot.png` | Screenshot of the workspace |
| `web_meshes/` | Meshes loaded by the browser viewer (includes a copy of the `R4` shroud) |

## Key geometry (from `r8_live_report.json`)

- Hotend offset: the nozzle sits **6.335 mm right of the toolhead centerline** so the Orbiter motor can stay centered. The report places the nozzle at X = +6.335 mm in its display coordinates (front = −Y, up = +Z).
- Extruder/hotend Z shift −14.65 mm; motor opening Ø39.0 mm; 22 × 10 mm oval cutout centered at Z 68.5 mm; carriage hex-nut pockets AF 5.6 mm.
- Adapter solid valid, volume 38,737.56 mm³, bounding box X −30.0..30.0, Y −32.04..11.12, Z −9.15..80.0 mm.

## CAD checks (not a physical fit test)

- 0.0 mm³ overlap between the adapter and the Orbiter v2.5, the X1C hotend reference, the 3010 fan, the carriage `knubs` reference, the belts and the EBB42 `R7` short-bridge reference.
- The report also lists **43.96 mm³ of overlap between the Orbiter reference and the gray carriage mock-up**. That pair does not involve the printed adapter, but check it if the Orbiter position is ever changed.
- The hotend reference is the original Bambu X1/P1 STEP. The installed hotend is a TZ 2.0 clone, so hotend clearances here are nominal.

## Not recorded yet

- Print material and settings used for the installed part.
- Which EBB42 bracket and which Eddy Duo bracket are mounted on it (see `CURRENT_TOOLHEAD_SPEC.md`).

## License

Derived from Kirill_Wawe's BambuMod for FF Adventurer 5M (Printables 1574762), CC BY-NC-SA 4.0; share derivatives under the same license with attribution. The Orbiter v2.0/v2.5 model (dr. Lorincz Robert, CC BY-NC-SA 4.0) is used only as a fit reference.
