---
name: cad-workflow
description: >-
  Build, validate, and render printable FreeCAD bracket revisions in AD5M-Transformation.
  Activate this skill whenever creating or modifying CAD geometry, running FreeCAD builders
  in scripts/cad/, checking mesh watertightness or housing/board collisions, or rendering
  4-view PNG previews.
---

# AD5M Toolhead CAD Workflow

Follow this workflow whenever inspecting, modifying, or creating a new printable bracket revision in `AD5M-Transformation`.

## 1. Pre-Flight Rules
1. Read `AGENTS.md` and `CURRENT_TOOLHEAD_SPEC.md` before changing any geometry.
2. **Never overwrite an existing revision folder** (`outputs/<part>_R<n>/`). Create the next revision (`outputs/<part>_R<n+1>/`) and a portable builder/renderer in `scripts/cad/`.
3. **Preserve mounting datums and board orientation** unless the user explicitly asks to move them:
   - **BambuMod upright housing transform:** `body = source.Solids[1].copy(); body.rotate(Vector(), Vector(0,1,0), 180); body.translate(Vector(0,0,92.21775))`
   - **Four upward-facing housing cover holes:** `X in [-27, -18, 18, 27]`, `Y = -7.498`, `Z = 80.1515` (`base`), clearance diameter `4.3 mm` (`r = 2.15 mm`).
   - **EBB42 mounting holes:** `31 mm` pitch, `2.5 mm` (`r = 1.25 mm`) plastic-threading pilots normal to the sloped mounting face (cut *after* filleting so hole rims remain sharp).
   - **Eddy Duo solid-edge housing anchors (source CAD frame):** `[30, -6, 64]` and `[30, -6, 84]` (`20 mm` pitch), sensor slot pitch `10.5 mm`, vertical travel `10 mm`.
4. **Design style:** Simple geometry faithful to user sketches, rounded exterior edges, sharp hole rims allowed, support-free print orientation.

## 2. Running Builders & Renderers

### Local Windows Workstation
- **FreeCAD Python (for `build_*.py`):**
  ```powershell
  & "C:\Program Files\FreeCAD 1.1\bin\python.exe" scripts/cad/build_<part>_R<n>.py
  ```
- **Preview Renderer (for `render_*.py`):**
  ```powershell
  & "C:\Program Files\FreeCAD 1.1\bin\python.exe" scripts/cad/render_<part>_R<n>.py
  ```
  *(System Python at `C:\Python314\python.exe` can also run `render_*.py` if `numpy` and `Pillow` are installed.)*

### Cloud Environment (Codex Cloud / Linux)
- Use the environment's native FreeCAD Python runtime plus packages in `requirements-cloud.txt`.

## 3. Required Validation Checks
Every `build_<part>_R<n>.py` script must verify and write `validation.json` (or `parameters.json`) into `outputs/<part>_R<n>/`:
- `s.isValid() == True` and `len(s.Solids) == 1` (single valid CAD solid).
- `mesh.isSolid() == True` (single watertight, consistently wound STL exported in print orientation at `XMin=0, YMin=0, ZMin=0`).
- `housing_overlap_mm3`: `s.common(body).Volume` must be `0.0` (zero collision with supplied BambuMod housing).
- `board_bracket_clashes` / `board_housing_clashes`: Check each solid in `outputs/ebb42_mockup/EBB42_CAN_V1.1_reference.step` (separating reference-fastener cylinder indices `[1667, 1669, 1671, 1673]` at the mounting holes from actual PCB/connector components).
- Export `.step`, `.stl`, `.FCStd` assembly, `preview_parts.json`, and `validation.json`.

## 4. Visual Inspection & Documentation
1. Run the renderer to produce `Bracket_preview.png`, `Assembly_preview.png`, and `Bracket_isometric.png` via `scripts/cad/render_mockup.py`.
2. View the generated PNGs to confirm exterior fillets, sharp hole rims, and support-free print orientation.
3. Add `PRINT_AND_FIT.md` (or `PRINT_AND_INSTALL.md`) in the new output folder including CC BY-NC-SA 4.0 attribution where derived from BambuMod (`Kirill_Wawe`, Printables 1574762).
4. **Never claim a CAD check proves physical fit:** Explicitly note that stock feeder/motor, bearing carriage, cables, and frame travel are absent from the supplied housing CAD.
5. Update `CURRENT_TOOLHEAD_SPEC.md`, `README.md`, `outputs/INDEX.md`, and `AGENTS.md`.
