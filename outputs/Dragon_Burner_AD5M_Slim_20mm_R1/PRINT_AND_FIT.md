# AD5M Dragon Burner Full-Slim `-20.0 mm` Pack (`R1`)

Full `-20.0 mm` depth reduction of the AD5M Dragon Burner adapter (`#1406257 v11`), keeping **both original fan-shroud screwhole ear tabs** intact (`Y = -44.16..-33.30`, `Z = 3.45..8.90`), adding baked-in 45° anti-warp bed corner chamfers on all four corners, and pairing with the **Reverse-Orbiter** mounts (`180°` motor-forward orientation).

## 1. Root Cause of Missing Tabs & Reverse-Orbiter Requirement

- In the earlier `-15 mm` prototype, an upper bridge notch (`top_trim` + `center_roof_notch` above `Y = -45.78`) was added to clear a **Regular Rear-Motor Orbiter**. That cut accidentally removed `#1406257`'s two front fan-shroud screwhole ear tabs (`Y = -44.16..-33.30`, holes near `X = 14.5 / 55.3, Y = -40.7`).
- In **`AD5M_Dragon_Burner_Slim_20mm_Adapter_R1`**, both trims are completely removed, restoring **100% (`1466.94 mm³`, `0.00 mm³` diff)** of the original fan-shroud screw tabs shifted forward by `-20.0 mm` (`Z = 3.45..8.90`).
- **Reverse-Orbiter Required:** Using an approximate `Ø36 × 20 mm` LDO motor + `49.5 × 47.0 mm` gearbox envelope (`Orbiter 2.0/2.5`), a **Regular Rear-Motor** collides with the `-20.0 mm` adapter by **`505.60 mm³` total (`214.34 mm³` directly inside the restored shroud screw tabs)**, whereas **Reverse-Orbiter (`180°` motor-forward)** clears all geometry with **`0.00 mm³` overlap** (`+14.17 mm` motor clearance from the adapter, `+1.72 mm` gearbox-to-adapter gap).

## 2. Exported Manifold Files

All files in [`outputs/Dragon_Burner_AD5M_Slim_20mm_R1/`](file:///C:/Users/PK800/.gemini/antigravity/scratch/AD5M-Transformation/outputs/Dragon_Burner_AD5M_Slim_20mm_R1) are BRep-valid single solids with watertight non-manifold-free STL meshes (`validation.json`):

| Part | Print Orientation | BBox (`X × Y × Z` mm) | Volume (`mm³`) | Purpose |
| :--- | :--- | :---: | :---: | :--- |
| `AD5M_Dragon_Burner_Slim_20mm_Adapter_R1.stl` | Rear carriage face (`Z=0`) on bed | `60.0 × 91.0 × 13.4` | `24576.65` | `-20.0 mm` AD5M steel-carriage adapter w/ restored shroud screw tabs & corner chamfers |
| `Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1.stl` | Rear face (`Z=0`) on bed | `55.0 × 21.3 × 21.0` | `13902.80` | `Bambu_Mount(2)` remix w/ mirrored `(-17.49, +19.51 mm)` M3 heatsets + `R=3.85 mm` boss |
| `Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1.stl` | Flat bottom (`Z=0`) on bed | `50.7 × 24.0 × 6.9` | `5869.06` | `180°` rotated `Orbiter2_Mount(4)` around filament axis |

## 3. Verified Dimensions & Clearances (`validation.json`)

- **Nozzle Tip Position:** `(34.924, -138.401, 24.697) mm` (`-20.00 mm` vs stock `#1406257`'s `44.697 mm`, and just **`+1.50 mm`** ahead of `AD5M_Custom_Housing_R1`'s `23.197 mm`).
- **Mount Interface Depth:** `Z_mount = 13.40 mm` (`33.40 -> 13.40 mm`), prismatic cut `Z = [3.45, 23.45]` mm (`no Hall magnet pockets`; sensorless homing assumed).
- **Anti-Warp Corner Chamfers (all 4 bed-contact corners @ `Z = 0`):**
  - Bottom-Left / Bottom-Right (`BL/BR`): **`5.0 × 5.0 mm`** 45° vertical XY chamfers.
  - Top-Left / Top-Right (`TL/TR`): **`3.45 mm`** 45° lofted tapered chamfers terminating at `Z = 3.40 mm` so the `Z = 3.45..8.90 mm` shroud screw tabs remain 100% intact.
- **Upper Carriage Bolt Backing Bosses (`UL = 15.302, UR = 54.503, Y = -47.700`):**
  - Compact `R = 4.0 mm` backing bosses across `Z = 2.95..7.00 mm` (`Y <= -44.16`) provide `7.00 mm` boss thickness (`30.561 / 30.561 mm³` solid backing over `Z = 3.1..6.9`, `0.0 mm³` overlap in `Z = 0..2.8` rear pocket) while staying `5.71 mm` behind the Orbiter gearbox (`ZMin = 12.71 mm`).
- **Lower Carriage Bolts & Slot (`lower_left`, `lower_right`, `fifth_±14`, `42×9 slot`):** `0.0 mm³` front tool corridor obstruction.
- **Toolhead Component Intersections:**
  - `steel_carriage`: `0.0 mm³`
  - `Dragon Burner MainBody`: `0.0 mm³` (`duct_right` rear face sits `+9.868 mm` ahead of steel carriage)
  - `Bambu_Mount_RevOrb` / `Orbiter2_Mount_RevOrb` / `Hotend`: all `0.0 mm³`
  - `Bambu_Mount_RevOrb` mirrored heatset wall solidity: `mirr_L = 100.0%`, `mirr_R = 99.93%`
  - `Reverse-Orbiter` motor span: `Z = [24.71, 44.71] mm` (`5.16 mm` behind `MainBody` nose at `Z = 49.87 mm`).

## 4. Print & Assembly Notes

- **Recommended Material:** ABS / ASA (`0.20 mm` layer height, `4–5` walls, `35–40%` gyroid/grid infill, no supports required on any of the three parts with `Z=0` flat faces down).
- **Sensorless Homing:** Hall-effect sensor magnet pockets are omitted; configure Klipper sensorless XY homing.
- **Bed Mesh Probe (BTT Eddy Duo):** Mount on the front/side toolhead mount position; verify X/Y probe offsets after installation.
- **Motor Direction & Rotation:** Mounting Orbiter 2.0/2.5 `180°` reversed does **not** reverse filament rotation around the shaft axis as seen from the filament gear (`Z`-up extrusion axis unchanged — test extrude 10 mm and invert `dir_pin` in Klipper only if it extrudes backward).
