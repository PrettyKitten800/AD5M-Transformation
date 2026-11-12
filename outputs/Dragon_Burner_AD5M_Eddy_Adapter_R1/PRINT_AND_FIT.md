# AD5M Dragon Burner (#1406257 v11) — Mode-A Rear Eddy Duo Remix (R1)

## 1. Deliverable Files

| File | Description |
| :--- | :--- |
| `AD5M_Dragon_Burner_Eddy_Adapter_R1.stl` | Single-component, watertight, consistently wound manifold print mesh (`5,298` facets, `84,506.8 mm³`). |
| `AD5M_Dragon_Burner_Eddy_Adapter_R1.step` | Exact OCCT BRep solid export (`freecad_valid_brep: true`, `freecad_solid_count: 1`). |
| `AD5M_Dragon_Burner_Eddy_Adapter_R1.FCStd` | Inspection assembly containing the remixed adapter alongside `#1406257`, `Dragon_Burner_v0.2_v8_reference.step`, `Bambu_X1_P1_original_hotend_Jorge.STEP`, and `EDDY_official.step`. |
| `validation.json` | Machine-generated geometry, envelope, thermal-baffle, and 3D collision audit (`0.0 mm³` addition overlaps). |
| `adapter_remix_multiview.png` | 4-panel shaded 3D inspection views of the remixed adapter STL. |
| `toolhead_full_assembly.png` | 4-panel aligned toolhead assembly (carriage + adapter + Dragon Burner + Bambu hotend + Eddy Duo). |
| `engineering_sections.png` | 1:1 FreeCAD BRep cross-sections through centerline YZ, ear/5th-bolt XZ, and USB/Hall-magnet XY planes. |

---

## 2. Coordinate Frame & Aligned Reference Datums

Printables `#1406257` v11 (`adventurer-5m-dragon-burner-adapter-v11.stl`) uses the following native STL axes:
- `+X` = Right across X-gantry width (bounding box `[4.902, 64.899]` mm)
- `+Y` = Vertical **UP** (`+Z_printer`; bounding box `[-136.000, -33.300]` mm in R1; stock flange bottom at `-124.300` mm)
- `+Z` = Forward toward Dragon Burner & hotend (`+Y_printer`; `Z = 0.000` mm rests flush against the stock AD5M steel carriage front face; front mount plane = `33.400` mm)

Aligning `Dragon_Burner_v0.2_v8_reference.step` (`Bambu_Mount (1)`) onto `#1406257`'s `33.400` mm front face with `Bambu_X1_P1_original_hotend_Jorge.STEP` seated at its filament bore gives:

| Datum | Adapter Native `(X, Y_up, Z_fwd)` (mm) | Relative to Nozzle Tip `(X, Y_behind, Z_up)` |
| :--- | :--- | :--- |
| **Nozzle Tip** | `(34.924, -138.401, +44.697)` | `(0.0, 0.0, 0.0)` mm |
| **Stock Steel Carriage Bottom** | `(34.924, -124.801, <= 0.000)` | `+13.600 mm` above nozzle tip |
| **Target Eddy Coil Center (Nominal)** | `(34.924, -135.901, +9.697)` | **`X = 0.0`, `Y = 35.0 behind`, `Z = +2.5 above`** (`-11.1 mm` below steel carriage bottom) |

---

## 3. Mode-A De-Shelled Eddy Pocket, Thermal Baffle & Collision Audit

- **Probe Envelope & Mode-A Entry:** Centered on `X = 34.924 mm` with a `18.50 mm` inner pocket width (`18.10 mm` lower housing / `18 × 11 mm` bare coil PCB + `0.40 mm` fit clearance) and open rear/bottom coil cradle (`Z = 4.20..23.30 mm` lower rails, `Y = -136.00..-131.00 mm`) extending upward to `POCKET_CEIL_Y = -98.00 mm`.
- **26.61 mm M3 Mounting Slots (`±1.0 mm` Travel):** Left and right mounting ears at `X = 21.619` and `48.229 mm` (`26.61 mm` pitch, `Y = -128.50 mm`) provide `Ø3.40 mm` vertical M3 slots with `±1.0 mm` travel (`1.5–3.5 mm` above nozzle) and side-load captive M3 DIN 934 hex-nut channels (`7.8 mm` tall × `2.8 mm` deep at `Z = 16.60..19.40 mm`).
- **Thermal Baffle (`>= 2.4 mm` Requirement):** Solid continuous ABS/ASA front barrier at `Z = 23.30 mm`:
  - `4.30 mm` solid thickness over the main Mode-A pocket (`Z = 19.00..23.30 mm`)
  - `3.90 mm` solid skin in front of captive nut channels (`Z = 19.40..23.30 mm`)
  - **`2.70 mm` minimum solid baffle** over the upward USB relief channel (`Z = 20.60..23.30 mm`)
  - Air gaps forward of baffle: `11.568 mm` to `Dragon Burner MainBody` / 3010 exhaust region, `13.547 mm` to `Bambu X1/P1` hotend.
- **Upward USB Relief Channel:** `12.60 mm` wide × `7.10 mm` deep (`Z = 13.50..20.60 mm`) behind the solid thermal baffle, clearing the inward-facing `90°` 4-pin JST-ZH USB connector (`1.68 mm` min wall clearance) and exiting cleanly upward at `Y = -82.3 mm` into `#1406257`'s existing `20 × 23.4 mm` central cable tunnel.
- **Collision & Existing Feature Checks (`validation.json`):**
  - **X/Y Hall-Endstop Magnet Pockets (`+X` wall, `Z = 29.40`):** Both `3 mm` magnet pockets remain `0.0 mm³` unobstructed (`36.035 mm` minimum distance to added pocket/ear geometry).
  - **5 Carriage M3×10 mm Bolts & `42 × 9 mm` 5th-Bolt Slot (`Y = [-117.30, -108.30]`):** Zero overlap between added remix geometry and all 5 bolt head/tool-access corridors (`addition_overlap_head_corridor_mm3 = 0.0`, `slot_42x9_head_corridor_Z3p45_to_11p5_overlap_mm3 = 0.0`, `2.507 mm` lateral clearance to both `X = ±14.0 mm` 5th-bolt candidates).
  - **Toolhead & Carriage Overlap:** `0.0 mm³` overlap with `Steel Carriage`, `Dragon Burner Bambu Mount`, `Dragon Burner MainBody`, and `Bambu Hotend`.

---

## 4. Printing & Assembly Instructions

1. **Material (Required):** Print in **ABS or ASA** (`<= 100°C` / chamber heat resistant; do not use PLA or PETG next to the hotend/3010 heatsink). Suggested walls: `4` perimeters (`1.6 mm` wall), `40%+` gyroid/grid infill, `0.20 mm` layer height.
2. **Orientation & Supports:** Place the flat rear carriage face (`Z = 0.000 mm`) down on the build plate. Enable **touching-buildplate supports only** (`Z = 0..13.0 mm` under the drop-down Mode-A cradle rails, M3 ear undersides, and side-load hex nut roofs); keep `#1406257`'s screw holes and Hall magnet pockets support-free.
3. **De-Shelling & Mounting the BTT Eddy Duo:**
   - Remove the upper plastic shell half (`Z_eddy > +4.90 mm`); leave the `90°` coil PCB intact and connect the 4-pin JST-ZH USB cable before sliding the sensor into the pocket.
   - Orient the de-shelled Eddy with the `90° Coil90` extending rearward (`-Z`, away from nozzle) and the inward-facing `4-pin` USB cable routed upward through the rear channel into `#1406257`'s central tunnel.
   - Insert `2× M3` hex nuts into the side-load ear channels (`Z = 16.6..19.4 mm`) and secure the `26.61 mm` mounting clamp / retention plate from the rear (`Z = 13.0 mm`) with `2× M3` socket-head or button-head screws (check head clearance against the steel carriage `Z = 0` -> maximum protrusion behind `Z = 13.0 mm` must stay `< 12.0 mm`; short `M3×6` or `M3×8` BHCS leaves `>= 7–9 mm` air gap behind the ear).
4. **Height Adjustment & Bench Verification:**
   - Verify with a straightedge/feeler gauge on the assembled toolhead (CAD verification does not substitute for physical nozzle-to-coil inspection): confirm the coil bottom sits **`+2.5 mm`** (`1.5–3.5 mm` via the `±1.0 mm` slots) above the nozzle tip before tightening both M3 bolts.

---

## 5. Klipper `printer.cfg` Configuration

Klipper `[probe_eddy_current]` defines offsets **from the nozzle to the coil center** (`+y_offset` = behind the nozzle):

```ini
[probe_eddy_current btt_eddy]
sensor_type: ldc1612
i2c_mcu: eddy
i2c_bus: i2c0f
x_offset: 0.0
y_offset: 35.0
z_offset: 2.5
# Physical coil height is +2.5 mm above nozzle (+1.5 to +3.5 mm slotted travel).
# Do NOT guess final trigger threshold: run both Klipper eddy calibration commands
# after heat-soaking the chamber / bed!
```

Run Klipper's Eddy calibration sequence after mounting and thermal soak (`PROBE_EDDY_CURRENT_CALIBRATE` overrides nominal trigger `z_offset`):
```text
SET_GCODE_OFFSET Z=0
LDC_CALIBRATE_DRIVE_CURRENT CHIP=btt_eddy
PROBE_EDDY_CURRENT_CALIBRATE CHIP=btt_eddy
SAVE_CONFIG
```
