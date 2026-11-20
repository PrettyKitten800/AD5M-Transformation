# AD5M Dragon Burner `-15.0 mm` Slim Adapter & Reverse-Orbiter Mount Pack (R1)

**Target configuration:** Flashforge Adventurer 5M (sensorless homing — Hall-effect X/Y magnet pockets omitted), Dragon Burner v8, Bambu X1/P1 hotend, Orbiter v2.0/v2.5 (`LDO-36STH20`).

All CAD/BRep operations, FreeCAD 3D interference checks, and comparison renders are generated reproducibly by:
- Build script: `scripts/cad/build_dragon_burner_slim_15mm_R1.py`
- Render script: `scripts/cad/render_dragon_burner_slim_15mm_R1.py`
- Validation metrics: `validation.json`
- FreeCAD assembly inspection file: `AD5M_Dragon_Burner_Slim_15mm_Comparison_R1.FCStd`

---

## 1. Exported Printable Files (`Mesh.isSolid() = true`, `hasNonManifolds = false`)

| Deliverable | Purpose | BRep Valid / Solids | Facets | Volume (mm³) | STL Print Bounding Box (mm) | Print Bed Orientation |
|---|---|---:|---:|---:|---|---|
| `AD5M_Dragon_Burner_Slim_15mm_Adapter_R1.stl` / `.step` | `-15.0 mm` trimmed `#1406257 v11` adapter for sensorless homing, relieved upper bridge, `5.0 × 5.0 mm` `45°` anti-warp corner chamfers | Yes / 1 | 3,118 | 36,087.55 | `X=[4.902, 64.899]`, `Y=[-124.300, -44.150]`, `Z=[0.000, 18.400]` | Flat rear steel-carriage face (`Z = 0`) down on build plate; no supports needed |
| `Dragon_Burner_Bambu_Mount_ReverseOrbiter_R1.stl` / `.step` | `Bambu_Mount` with stock `-19.51 / +17.49` heatsets plugged, `R=3.85 mm` boss @ `mirr_L`, and mirrored `-17.49 / +19.51 mm` `Ø4.70 mm` heatset pockets | Yes / 1 (upstream STEP seam repaired on mesh export) | 11,562 | 13,902.80 | `X=[-27.480, 27.520]`, `Y=[-10.640, 10.640]`, `Z=[0.000, 21.000]` | Flat rear mount face (`Z = 0`) down on build plate (matches stock `Bambu_Mount.stl`) |
| `Dragon_Burner_Orbiter2_Mount_ReverseOrbiter_R1.stl` / `.step` | `Orbiter2_Mount (4)` rotated exact `180°` around the filament bore (`4.75 mm` forward housing shift) | Yes / 1 | 6,042 | 5,869.06 | `X=[-25.379, 25.338]`, `Y=[-14.395, 9.630]`, `Z=[0.000, 6.900]` | Flat bottom face (`Z = 0`) down on build plate |

**Recommended print material & settings (heated enclosure / ABS or ASA):**
- **Material:** ABS / ASA / PC-ABS (never PLA near the carriage/hotend).
- **Perimeters / Infill:** 4 perimeters, 5 top/bottom layers, 40% gyroid infill (`0.20 mm` layer height, `0.40 mm` nozzle).
- **Heatset inserts (`Bambu_Mount_ReverseOrbiter`):** 2× `M3×5×4 mm` heatset inserts into the mirrored `Ø4.70 mm` top pockets (`-17.49 mm` left / `+19.51 mm` right of filament bore). FreeCAD solid-wall verification around a `Ø7.70 mm` (`R = 3.85 mm`) sleeve confirmed **`100.0%` (`mirr_L`)** and **`99.93%` (`mirr_R`)** solid ring engagement while keeping the adjacent left-side wire slot unobstructed.

---

## 2. Regular Slim vs. Reverse-Orbiter Slim (`-15.0 mm` Comparison)

Both options share `AD5M_Dragon_Burner_Slim_15mm_Adapter_R1` (`Z_mount: 33.400 → 18.400 mm`):

| Metric | Stock `#1406257 v11` | **Option 1: Regular Slim (Rear Motor)** | **Option 2: Reverse-Orbiter Slim (Front Motor)** |
|---|---:|---:|---:|
| **Printable Parts** | Stock `#1406257` | `Slim_15mm_Adapter_R1` + stock `Bambu_Mount` + stock `Orbiter2_Mount` | `Slim_15mm_Adapter_R1` + `Bambu_Mount_ReverseOrbiter_R1` + `Orbiter2_Mount_ReverseOrbiter_R1` |
| **Nozzle Z Forward of Steel Carriage** | `44.70 mm` | **`29.70 mm` (`-15.00 mm`)** | **`29.70 mm` (`-15.00 mm`)** |
| **Delta vs. `AD5M_Custom_Housing_R1` (`23.20 mm`)** | `+21.50 mm` | **`+6.50 mm`** | **`+6.50 mm`** |
| **Right Duct (`Standard (1)`) Rear Clearance to Steel Carriage** | `29.87 mm` | `+14.87 mm` | `+14.87 mm` |
| **Max Front Protrusion (`MainBody` nose at `Z = 54.87 mm`)** | `69.87 mm` | `54.87 mm` | `54.87 mm` (`LDO Ø36×20` motor front at `49.71 mm`, **`-5.16 mm` behind MainBody nose**) |
| **Orbiter 2.5 Motor Envelope Span (`Z_fwd`)** *(approx envelope)* | `24.71 .. 44.71 mm` | `9.71 .. 29.71 mm` | `29.71 .. 49.71 mm` (gearbox rear at `17.71 mm`) |
| **Rear Motor / Gearbox Gap to Adapter Top Wall (`Z = 8.40 mm`)** | `~1.3 mm` | `1.31 mm` *(tight for 4-pin stepper plug; cable exits up/back near carriage)* | **`+1.72 mm` gearbox clearance / `>= 9.3 mm` wide open roof behind filament** |
| **Rear Gap to Steel Carriage (`Z = 0`)** | `24.71 mm` | `9.71 mm` *(envelope; actual motor+plug back may extend further)* | **`17.71 mm` (gearbox)** — full rear bay open above `MainBody` for EBB42 / CAN umbilical |

> **Caveat on Extruder Check:** Because no official OEM Orbiter v2.5 STEP file is stored in `reference/`, the `regular_orbiter_motor_envelope` and `reverse_orbiter_motor_envelope` checks in `validation.json` use an approximate parametric envelope (`Ø36 × 20 mm` LDO motor + `49.5 × 47 mm` gearbox prism). Visually confirm your physical Orbiter 2.5's 4-pin JST stepper plug orientation and thumbscrew clearance on assembly — in **Option 1 (Regular)**, a rear-facing 4-pin stepper plug sits closest to the steel carriage (`~9.7 mm` nominal gap from the `Ø36` cylinder), whereas **Option 2 (Reverse)** places the `Ø36` motor and plug completely forward in open air above `MainBody` while still staying `5.16 mm` behind Dragon Burner's front nose (`54.87 mm`).

---

## 3. Collision & Bolt Clearance Summary (`validation.json`)

- **Steel carriage (`Z <= 0`, `Y >= -124.801`):** `0.0 mm³` overlap.
- **Adapter vs. `MainBody` / `Bambu_Mount_RevOrb` / `Hotend`:** all `0.0 mm³` overlap.
- **`Orbiter2_Mount_RevOrb` vs. `MainBody` / `Slim_15mm_Adapter_R1`:** `0.0 mm³` overlap.
- **Carriage Mounting Bolts:**
  - `upper_left` (`X=15.302, Y=-47.700`) & `upper_right` (`X=54.503, Y=-47.700`): `0.0 mm³` obstruction in rear pockets (`Z=0..2.8 mm`) with **`8.40 mm` solid plastic wall** (trimmed cleanly from `#1406257`'s `Z=8.4..23.4` block; mounts from behind the steel carriage with `M3×10` bolts).
  - `lower_left`, `lower_right`, and `42×9 mm` 5th-bolt slot (`+14 / -14`): `0.0 mm³` tool-corridor overlap in front of `Z = 3.45 mm`.

---

## 4. BTT Eddy Duo Placement Note

Removing `15.0 mm` from `#1406257`'s spacer shrinks the cavity behind the Dragon Burner mounting plane (`Z = 18.400 mm`) down to `8.40 mm` (`Z = 8.40..18.40` bay) over the `Z = 0..8.40` carriage back wall, so the **Mode-A Rear Eddy pocket (`R1`, which needs `~22.7 mm` Z depth + thermal baffle + USB channel) no longer fits behind Dragon Burner**. If running this `-15.0 mm` Slim Adapter with the BTT Eddy Duo:
1. Mount the Eddy Duo **outboard (side-ear or front-right/left Dragon Burner Cowl probe mount)** clear of `AD5M` bed bounds, OR
2. Design a dedicated **side/front Eddy probe bracket** bolted to Dragon Burner's front/side M3 mount points after selecting Option 1 (Regular Slim) vs. Option 2 (Reverse-Orbiter Slim).

Visual verification plots:
- `regular_vs_reverse_slim_comparison.png`
- `slim_parts_multiview.png`
