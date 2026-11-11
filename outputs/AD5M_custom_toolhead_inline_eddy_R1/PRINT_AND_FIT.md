# R1 — Custom AD5M Bambu X1C Toolhead Housing & Inline (`x_offset = 0`) Eddy Duo Mount

## Overview

`AD5M_custom_toolhead_inline_eddy_R1` is a modular two-part custom toolhead revision designed around the confirmed AD5M hardware stack:
- **Stock AD5M feeder + motor** and **stock AD5M X-carriage** mounting datums
- **BTT EBB42 V1.2.1** top-rear angled toolboard mount (`EBB42_uniform_posts_R7`)
- **Bambu Lab X1C hotend** (`X = 0.00, Y = +12.08 mm` filament centerline, nozzle tip at `Z = -13.58 mm` in upright housing coordinates)
- **Stock 3010 24V hotend fan (`Peerless DF3010B24H`)** on the `+X` wall exhausting across the heatsink out the `-X` side vents
- **BTT Eddy Duo (USB)** relocated from the right side (`x_offset = 44 mm`) to the **nozzle X centerline (`x_offset = 0.0 mm`, `y_offset = -31.2 mm`)**

Relocating the Eddy Duo to `x_offset = 0.0 mm` eliminates the right-edge magnetic field roll-off (`probe_X > 196 mm`) that occurred with the `44 mm` side mount, allowing `probe_X == nozzle_X` across the full width of the steel build plate while isolating the probe from the `-X` heatsink exhaust stream.

---

## Included CAD & Printable Files

1. **`AD5M_Custom_Housing_R1.stl` / `AD5M_Custom_Housing_R1.step`**
   - **Retained Datums:** Preserves the rear carriage backplate (`Y = -11.12 to -3.88 mm`), four carriage screw bores (`X = ±24.0, Z = 61.0` and `X = ±19.0, Z = 3.5`), stock AD5M feeder/motor bay (`Z = 31.0 to 60.0`), four top cover / `EBB42_uniform_posts_R7` mounting holes (`X = ±18.0, ±27.0, Y = -7.55, Z = 80.0`), `3010` heatsink fan cavity (`X = +14.5 to +19.5`), and Bambu X1C hotend M3 mounting holes (`X = -3.44, +3.41, Z = 27.22`).
   - **Internal Hotend Fin Relief:** Relieves the internal heatsink top-fin shelf (`Z = 23.90 to 25.72 mm`) against the Bambu X1C hotend reference CAD (`Bambu_X1_P1_original_hotend_Jorge.STEP`), reducing CAD hotend overlap from `52.05 mm³` to `0.0 mm³`.
   - **Reinforced Front Bulkhead Bosses & M3 Pilot Bores:** Reinforces the rear of the left and right front pillars (`X = ±12.0 mm`, `Y = 24.12 to 30.12 mm`, `6.0 mm` solid depth) and adds **four `2.5 mm` M3 direct plastic-threading pilot bores** (`24.0 mm` horizontal pitch at `X = ±12.0 mm`, `8.0 mm` vertical pitch at `Z = 11.5 mm` and `Z = 19.5 mm`).
   - **Self-Supporting Upper Side Windows:** Skeletonizes the non-load-bearing upper side walls (`X = ±30.0 mm`, `Z = 40.0 to 54.0 mm`, `Y = 7.0 to 23.0 mm`) with `45°`-sloped hexagonal windows that print without supports when the housing lies flat on its rear carriage face (`Y = -11.12 mm`).

2. **`Eddy_Duo_Inline_Mount_R1.stl` / `Eddy_Duo_Inline_Mount_R1.step`**
   - **Inline Nozzle Alignment (`x_offset = 0.0 mm`):** Centers the BTT Eddy Duo at `X = 0.00 mm` on the front of the lower housing (`Y = 30.12 to 34.12 mm`, `4.0 mm` plate thickness), shielding the probe from the heatsink cavity behind it.
   - **Housing Attachment (`24.0 x 8.0 mm` pattern):** Four `3.3 mm` M3 clearance holes at `X = ±12.0 mm`, `Z = 11.5 mm` and `19.5 mm` sit outside the Eddy Duo's `18.1 mm` body width (`X = -9.05 to +9.05 mm`) so housing screws remain accessible.
   - **Vertical Adjustment (`10.0 mm` travel):** Two `3.3 mm` vertical slots at `X = ±5.25 mm` (`10.5 mm` pitch) run from `Z = 5.50 mm` to `Z = 15.50 mm`, allowing the Eddy Duo sensing bottom to adjust from `Z = -15.79 mm` (`2.2 mm` below the reference nozzle tip) to `Z = -5.79 mm` (`7.8 mm` above the reference nozzle tip), centered on the nominal `+2.5 mm` target (`Z = -11.08 mm`).
   - **Captive M3 Nut Channels:** Rear recessed M3 nut channels (`5.8 mm` wide x `16.6 mm` tall x `2.5 mm` deep) leave a `1.5 mm` front skin, `4.7 mm` solid center wall between channels, and `1.85 mm` outer side walls.

---

## Print Settings

- **Material:** PETG, PETG-CF, ABS, or ASA recommended for thermal stability near the hotend.
- **Scale:** `100%` (both STLs are pre-oriented for flat, support-free printing).
  - `AD5M_Custom_Housing_R1.stl`: Rear carriage backplate flat on the build plate, **supports OFF**.
  - `Eddy_Duo_Inline_Mount_R1.stl`: Front sensor-contact face flat on the build plate (recessed nut channels facing up), **supports OFF**.
- **Walls / Infill:** `4` perimeters, `35–40%` gyroid or cubic infill, `0.20 mm` layer height.

---

## Klipper Configuration Update After Physical Installation

When transitioning from the side-mounted R4 bracket (`x_offset: 44, y_offset: 0`) to `Eddy_Duo_Inline_Mount_R1`:

1. Update `/home/curby/printer_data/config/eddy-duo.cfg`:
   ```ini
   [probe_eddy_current btt_eddy]
   x_offset: 0.0
   y_offset: -31.2
   ```
2. Update `/home/curby/printer_data/config/calibration.cfg` `[bed_mesh]` bounds to take advantage of the centered `X = 0` probe reach:
   ```ini
   [bed_mesh]
   mesh_min: 15, 15
   mesh_max: 195, 188
   ```
3. Set the physical Eddy height `~2.5 mm` above the nozzle tip using a spacer/card, snug the two M3 sensor screws into the rear captive nuts, and run `EDDY_CALIBRATE` followed by `EDDY_MESH`.

---

## Validation & Attribution

- Both exported STLs are single-body, watertight, consistently wound meshes with `0.0 mm³` CAD overlap between the housing, bracket, and Bambu X1C hotend reference solids (`validation.json`).
- **Physical verification note:** CAD and mesh checks do not substitute for a physical fit test on the printer. Verify physical clearance with your front part-cooling blower shroud, heater/thermistor wiring, USB cable strain relief, and full XY travel before commissioning.
- **License & Attribution:** Housing derived from Kirill_Wawe, *BambuMod for FF Adventurer 5M* (https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m, CC BY-NC-SA 4.0). Shared under CC BY-NC-SA 4.0. Hotend reference: Jorge (`jorge_rui`), *Bambu Lab X1C P1P P1S original hotend 3D model* (CC BY-ND 4.0, unmodified reference only).
