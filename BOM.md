# The Moron Tridont Project — Official Bill of Materials (`BOM.md`)

> **Canonical single-document hardware & parts BOM** for turning a FlashForge Adventurer 5M (AD5M) into **The Moron Tridont** (installed Phases 1–4 + Phase 5 miniature Voron Trident `3× MGN12H 300 mm` CoreXY gantry + future Phases 6–8).
>
> Companion docs: [README.md](README.md) · [CURRENT_TOOLHEAD_SPEC.md](CURRENT_TOOLHEAD_SPEC.md) · [BUILD_LOG.md](BUILD_LOG.md) · [AD5M_MGN12_GANTRY_SPEC.md](docs/plans/AD5M_MGN12_GANTRY_SPEC.md) · [PRINT_AND_FIT.md](outputs/AD5M_MGN12_Gantry_R1/PRINT_AND_FIT.md)

---

## 1. Electronics, Host & Toolhead (Phases 1–4 Installed + Pending Hotend Upgrade)

| Subsystem | Exact Part / Kit | Qty | Status | Source / Link | Notes |
|---|---|---:|---|---|---|
| **Printer Base** | FlashForge Adventurer 5M (AD5M) | 1 | Installed | Stock | Steel frame/enclosure, `24 V` A-350GF-24-CX (`350 W`) PSU, triple-Z belted bed, `~250 W` DC bed |
| **Host Computer** | Intel Linux PC ("CurbyServer") | 1 | Installed | On hand | Runs Kalico `v2026.11.00-73` + `eddy-ng` + Mainsail (`:80`) / Fluidd (`:8080`) |
| **Display** | BTT HDMI5 Touchscreen | 1 | Installed | — | Connected to CurbyServer |
| **Mainboard** | BTT Octopus Pro V1.1 (`STM32H723ZET6`) | 1 | Installed | — | USB-to-CAN bridge (`can0` 1 Mbps); bed wired direct to `BED-OUT` (`PA1`, `max_power 0.93`) |
| **Stepper Drivers** | BTT TMC2209 V1.3 | 4 | `3` installed + `1` spare | — | Sensorless XY homing (`SGTHRS 64`) + Z |
| **Toolboard** | BTT EBB42 V1.2.1 (`STM32G0B1`, CAN) | 1 | Installed | — | CAN MCU `head`, built-in ADXL345 |
| **Bed Probe** | BTT Eddy Duo (`LDC1612`, CAN) | 1 | Installed | — | CAN MCU `eddy`, `eddy-ng` tap + rapid scan (`R4` adjustable side mount, `x_offset 28.7`) |
| **Extruder** | Orbiter v2.5 + `LDO-36STH20-1004AHG` | 1 | Installed | — | `rotation_distance 4.69` (`R8` housing + `R4` shroud) |
| **Hotend** | TZ 2.0 Clone (Bambu X1C-style mount, `0.4 mm` nozzle) | 1 | Installed | — | Nozzle `6.335 mm` right of toolhead centerline; `-3.65 mm` hotend length datum |
| **Hotend Heater / Thermistor (Upgrade)** | **AJOYIB `24 V 60 W` Ceramic Heater + `100K B25/50=3950K ±1%` Thermistor + Clip** (Bambu Lab X1/X1C compatible) | 1 set | Ordered | *(link pending)* | Heater rated `24 V / 60 W` up to `350 °C`; thermistor `-30 °C..300 °C`. **Kalico note:** keep `Generic 3950`, change `[extruder]` `heater_power: 48 -> 60`, re-run `MPC_CALIBRATE` |
| **Hotend Fan** | Peerless `DF3010B24H` (`3010`, `24 V 0.09 A`) | 1 | Installed | — | Wired to `head:PA1` (`heater_fan`) |
| **Part-Cooling Blower** | Stock HXH `HBB0524VD` (`24 V` 4-wire) | 1 | Installed | Stock | Wired to `head:PA0` |
| **Backup MOSFET / Toolboard** | ReliaBot External Bed MOSFET V1.3 · BTT EBB36 V1.2.1 | 1 ea | On hand (spare) | — | Backup hardware not installed |

---

## 2. Phase 5: Miniature Voron Trident `3× MGN12H 300 mm` CoreXY Gantry (`AD5M_MGN12_Gantry_R1`)

| Item | Exact Spec / Kit | Qty | Used | Status | Source / Link | Notes |
|---|---|---:|---:|---|---|---|
| **X-Axis Linear Rail + Block** | **uxcell `MGN12 300 mm` Linear Guide Rail + `MGN12H` Carriage Block** | 1 | 1 | Ordered | *(link pending)* | Bearing steel, includes plastic mini install guide & end limit blocks (**remove end blocks before seating ends into `XY_Joint` C-channels**) |
| **Y-Axis Linear Rails + Blocks** | **IMETRX `MGN12H 300 mm` Linear Rail Guides** (pair) | 2 | 2 | Ordered | *(link pending)* | Pre-oiled heavy-duty bearing steel, mounted vertically inward on `Y_Rail_Spine_L/R` (`\|X\| = 171.50 mm`, `11` bolts/side) |
| **Timing Belt, Pulleys & Toothed Idlers Kit** | **FULARR `5 m` GT2 Timing Belt Kit** (`5 m × 6 mm` rubber GT2 belt, `5× 20T Ø16 × 16 mm` `5 mm`-bore pulleys, `5× 20T Ø18 × 8 mm` `5 mm`-bore toothed idlers, torsion springs, 2× mounting blocks, wrench) | 1 kit | `2.52 m` belt, `2×` pulleys, `2×` idlers | Selected (Amazon) | https://www.amazon.com/dp/B07TFCPCJ2 | Budget starter kit (`Ø18.6 mm` XY-joint bays & `-0.5 mm` motor plates fit `Ø18 × 8 mm` idlers & `16 mm` pulleys directly); see §4 for Gates belt upgrade |
| **Flanged Ball Bearings** | **M METERXITY `F695-2RS`** Chrome Steel Double-Rubber-Seal Flanged Bearings (`5 × 13 × 4 mm`, `Ø15 mm` flange, `mma250226ty002421jp`) | 20 pcs | 14 | Selected (Amazon) | https://www.amazon.com/dp/B0F4XNK1GM | **Verify 20-pack variant at checkout** (12× in `6` back-to-back smooth idler pairs: `2×` BFI + `4×` XY joints; `2×` in rear double-shear motor caps; `6` spares) |
| **Smooth Idler Axles (`Ø5 mm` Pins)** | **`Ø5 mm` 304 Stainless Steel Dowel Pin Assortment** (`5×10/16/20/25/30/35/40 mm`) | 1 set | 8 | Selected (Amazon) | *(link pending)* | **Verify pack contains `≥ 7× 5×20 mm` and `≥ 1× 5×30 mm`** (`7× 5×20` for BFI + 5× XY pins; `1× 5×30` for Left `XY_2_20T`) |
| **Precision Bearing Shims** | **`5 × 8 × 0.5 mm` 304 Stainless Steel RC Bearing Shims** | 100 pcs | ~28–30 | Selected (Amazon) | *(link pending)* | Fits `Ø5 mm` inner race cleanly (`0` seal rub): `2× 0.5 mm` above + below each `F695` pair (`24×`); `1 + 2` shims (`1.5 mm` total) on `8 mm` FULARR `20T` idlers |
| **Heat-Set Inserts** | **`M3 × 4.6 mm OD × 5.7 mm`** Brass Heat-Set Inserts (CNC Kitchen / Ruthex size) | ~39+ | ~39 | On hand | *(link pending)* | CAD pockets tuned to **`Ø4.00 mm × 6.2–6.5 mm`** across Y-spines (`11×`/side), rear motor mounts (`3×`/side), `XY_Joint_L/R_Upper` (`4×`/side), `XY_Joint_R_Lower` (`3×`) |
| **Structural Fasteners** | `M3×8/12/16/20/35` SHCS, `4× M3` hex nuts, `M4×12/16`, `M5×12` BHCS | ~100 | ~90 | Fastener stock | — | `~44× M3×8` rail/block screws, `4× M3×35` + `4×` M3 hex nuts for door-accessible BFI tensioners, `M3×12/16/20` XY joints & DS caps, `M4`/`M5` factory frame holes |

---

## 3. Printable Parts (`outputs/AD5M_MGN12_Gantry_R1/`)

- **Pre-oriented `Z = 0` Drag-and-Drop STLs (`16` Parts, Zero Supports):** [`outputs/AD5M_MGN12_Gantry_R1/parts_print_pose/`](outputs/AD5M_MGN12_Gantry_R1/parts_print_pose/)
- **Recommended Print Settings:** `ABS` / `ASA` (or `ABS-GF` / `ASA-GF`), `0.20 mm` layer height, `4–5` perimeters/walls, `5` top & bottom shells, `40%` gyroid infill, **0 supports**.
- Follow the 3-stage test-print checklist in [`PRINT_AND_FIT.md`](outputs/AD5M_MGN12_Gantry_R1/PRINT_AND_FIT.md) *(note: skip `X_Carriage_MGN12_Base_R1` for final install — wait for the `R2` monolithic `MGN12H` toolhead chassis)*.

---

## 4. Planned Future Upgrades (Phases 5b–8)

| Phase | Item | Qty | Rationale / Link |
|---|---|---:|---|
| **5b (Belt Upgrade)** | Genuine **Gates PowerGrip `LL-2GT-6`** Fiberglass-Core Open Belt (`6 mm`) | `3–4 m` | Replaces starter FULARR rubber belt with low-stretch, chamber-rated genuine Gates belting (`2.52 m` installed) |
| **5b (Motors)** | **`LDO-42STH48-2004MAH`** or **`2504MAH`** (`0.9°`, `48 mm` body, `24 mm` shaft) | 2 | Drop-in compatible (`Rear_Motor_Mount_L/R` already has `48 mm` clearance + `24 mm` double-shear top bearings); stock `40 mm` AD5M motors work initially once press-fit pulleys are swapped |
| **6–7 (Trident Frame & AWD)** | **Misumi `HFSB5-2020` Frame**, `3×` Z leadscrew steppers, `12"×12"` MIC6 + `450 W` AC bed + SSR, `2×` AWD motors, extra `TMC2209`s | Kit | Full cut list & BOM in [docs/plans/FRAME_CONVERSION.md](docs/plans/FRAME_CONVERSION.md) |
