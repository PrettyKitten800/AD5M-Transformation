# AD5M `3× MGN12H 300 mm` Linear-Rail CoreXY Gantry Specification (`AD5M_MGN12_Gantry_R1`)

> **Status — November 24, 2026:** Master geometric specification for Phase 5 (`AD5M_MGN12_Gantry_R1`) anchored directly to the official FlashForge frame CAD ([`AD5M_Frame.STEP`](../../reference/AD5M_gantry_research/official_frame_model/AD5M_Frame.STEP)) and enclosure CAD ([`AD5M_Enclosure.STEP`](../../reference/AD5M_gantry_research/official_frame_model/AD5M_Enclosure.STEP)).

---

## 1. Design Decisions & Hardware Standard

| Subsystem | Confirmed Selection | Rationale |
|---|---|---|
| **Linear rails** | **`3× MGN12H 300 mm`** (uncut) | 2× Y rails mounted vertically inward on side spines (`\|X\| = 171.5`); 1× self-supporting X rail mounted front-facing (`-Y`) |
| **Belts** | **Gates PowerGrip `LL-2GT-6`** (`6 mm` wide, open) | Voron Trident standard; fits cleanly inside the `35 mm` AD5M top steel skirt |
| **Drive pulleys** | **`20T` 5 mm-bore**, `6 mm` belt (`R_pitch = 6.366 mm`, `OD_flange = 16 mm`) | Matched `39.9–40.0 mm/rev` CoreXY drive kinematics on standard `Ø5 mm` shafts |
| **Idlers** | **`F695-2RS`** (`5 × 13 × 4 mm`, flange `Ø15 mm`, `R_belt_center = 7.130 mm`) + **`2× 20T` toothed idlers** (`Ø18 × 8 mm` FULARR or `Ø16 × 8.5 mm` Voron, `Ø18.6 mm` bays) | Voron pin-mod / BFI standard on hardened `Ø5 mm` dowel pins + `5×8×0.5 mm` shims; `20T` toothed idlers used only where belt teeth contact inside `180°` turns |
| **Rear motors** | **Fixed rigid 48 mm-ready double-shear mounts** (`42.3 × 42.3 × 48 mm`, `24 mm` D-cut shaft, e.g. `LDO-42STH48-2004MAH`/`2504MAH`, also supports stock `40 mm` drop-in) | Removable 3-bolt `Motor_DS_Cap_L/R` top `F695-2RS` bearing caps put both `24 mm` shafts in true double shear with zero crossbar collision |
| **Tensioners** | **Voron BFI / BootyCallJones-style compression front idlers** (`±4.5 mm` travel) | Belt pull compresses printed layers instead of splitting them; **interior-front screw access** reachable through open front door (never blocked by enclosure corner trim) |
| **Toolhead** | **Monolithic `MGN12H` chassis** (`X_Carriage_MGN12_Base_R1` layout base first; detailed shell in `R2`) | Bolted directly to front X `MGN12H` block; retains `Orbiter v2.5 + LDO`, `TZ 2.0` (`-3.65 mm` long hotend datum), `3010` fan, `EBB42 V1.2.1`, Bare `Eddy Duo`, and `Shroud V3.0` |

---

## 2. AD5M Frame & Enclosure Coordinate System (`AD5M_Frame.STEP`)

All coordinates in this spec and CAD builder use the **native `AD5M_Frame.STEP` datum**:
- **`+X`:** Right (`-X` = Left when viewed from Front)
- **`+Y`:** Rear (`-Y` = Front door)
- **`+Z`:** Up (`-Z` = Down toward bed)

### Key Measured Frame & Enclosure Features
- **Top steel ring (`Solid[30]`):**
  - Inner walls: `X = [-178.81, +178.79]` (`357.60 mm`), `Y = [-180.26, +177.34]` (`357.60 mm`), `Z = [371.83, 406.83]` (`35.0 mm` vertical skirt, `1.20 mm` sheet steel; **top flange underside `Z = 405.63 mm`**).
  - Top opening: `X = [-143.51, +143.49]` (`287.00 mm`), `Y = [-151.46, +126.04]` (`277.50 mm`), center **`(0.00, -12.71)`**.
  - Top steel flange widths: `35.3 mm` L/R, `28.8 mm` Front, `51.3 mm` Rear.
- **Factory Frame Holes Reused (Zero Steel Drilling Required):**
  - **L/R side skirts (`X = ±179.4`):** `3× Ø5.0 mm` holes per side at `Y = -120.96, +2.04, +125.04`, **`Z = 388.83 mm`**.
  - **Front corner top deck (`Z = 406.83`):** Symmetric 4-bolt `22.0 × 31.5 mm` (`Ø4.2 mm` M4 clearance) pattern at `X = ±147.50, ±169.50`, `Y = -166.41, -134.91` (plus `Ø5.4 mm` at `(±150.15, -158.56)` and `(±166.85, -142.76)`).
  - **Rear corner top deck (`Z = 406.83`):** `(±173.00, 138.04, Ø4.2)`, `(±161.25, 163.64, Ø4.2)`, `(±138.50, 169.64, Ø5.4)`, `(±126.00, 157.54, Ø4.2)`, `(±108.15, 142.64, Ø5.4)` (avoiding rear filament cutout at `X ≈ +73, Y ≈ +158, D = 17.5`).
- **Keepout & Clearance Boundaries:**
  - **Side PEM bosses (`Solid[29,35,39,45]`):** Extend inward to `|X| = 176.8` at `Y = [+143.1..+151.0]` & `[-153.9..-146.0]`, `Z = [374.9..382.8]` & `[394.9..402.8]`. All spines/mounts stay inboard of `|X| = 176.0` in those zones or are notched clear.
  - **Lower horizontal side crossbars:** Left (`-X`) top face **`Z = 314.23 mm`**; Right (`+X`) top face **`Z = 304.23 mm`**. Minimum bottom for vertical `48 mm` motors = **`Z >= 317.50 mm`** (`≥ 3.27 mm` clearance).
  - **Front enclosure corner trim (`EncSolid[74,76]`):** Covers outer `-Y` corner face (`|X| > 136.5 mm`). Front BFI tension bolts point **inward/accessible from interior front opening (`+Y` / angled inward)**.

---

## 3. Vertical Z-Stack Budget (`Z_top_deck_bot = 405.63 mm`)

| Element | Z Range (mm) | Center / Key Plane (mm) | Notes |
|---|---|---|---|
| **Top deck steel** | `405.63 .. 406.83` | — | `1.20 mm` sheet steel |
| **Y-Rail Spine (`\|X\| = 171.5..178.5`)** | `381.00 .. 405.40` | Vertical side wall | Bolted to `3× Ø5.0 mm` side-skirt holes (`Z = 388.83`) + notched clear of PEMs; holds `11× M3×4.6×5.7` heat-sets (`Y = +145.5` PEM notch skipped) |
| **MGN12 Y-Rail** | `385.50 .. 397.50` | Base `\|X\| = 171.50` | Vertical facing inward (`±X`), `Z_Y_MID = 391.50 mm` |
| **MGN12H Y-Carriage block** | `378.00 .. 405.00` | Mount face `\|X\| = 158.50` | `27.0 mm` tall × `13.0 mm` deep (`0.63 mm` clear below `405.63` steel deck) |
| **Self-Supporting `300 mm` X-Rail** | `388.50 .. 400.50` | **`Z_X = 394.50`** | Sits cleanly **above** both belt planes; `MGN12H` block spans `381.0..408.0` inside top opening |
| **Upper Belt A (`Z_A`)** | `378.00 .. 384.00` | **`Z_A = 381.00`** | `20T` hub-down pulley `[370.0..386.0]` (`16 mm` FULARR) on Right shaft (`Z_face = 367.50`); `Motor_DS_Cap_R` + `F695` at `Z = [386.5..392.0]` |
| **Lower Belt B (`Z_B`)** | `367.00 .. 373.00` | **`Z_B = 370.00`** | `20T` hub-down pulley `[359.0..375.0]` (`16 mm` FULARR) on Left shaft (`Z_face = 356.50`); `Motor_DS_Cap_L` + `F695` at `Z = [376.0..381.5]` |
| **Motor Mounting Plates (Staggered)** | `L: 356.5..360.5`, `R: 367.5..371.5` | `24.0 mm` shafts | Left shaft `356.5..380.5` (`DS Cap_L` `[376.0..381.5]`), Right shaft `367.5..391.5` (`DS Cap_R` `[386.5..392.0]`) — both in true double shear strictly below split XY joints (`L_Lower >= 361.50`, `R_Lower >= 372.40`) |
| **`48 mm` Motor Bodies** | `L: 308.5..356.5`, `R: 319.5..367.5` | Clear of frame (`0.000 mm³`) | Positioned at `X = ±136.0` (inboard of `\|X\| >= 159.0` lower side crossbars) |
| **Voron Trident Split XY Joints** | `Upper: 375.52..404.00`, `Lower: 361.50..375.48` | Split plane **`Z = 375.50`** | `XY_Joint_R` 3-piece (`Upper` / `Lower` / `Bottom_Cap`) & `XY_Joint_L` 2-piece (`Upper` / `Lower`); 100% support-free flat-bed printing with `3× M3` clamp bolts + `X_Y_MID` belt pass-through slots |

---

## 4. Master XY Coordinates & Exact CoreXY Belt Tangents

Using **`R_20T = 6.366 mm`** (`20T` pulley / toothed idler) and **`R_F695 = 7.130 mm`** (`6.50 mm` bearing radius + `0.63 mm` GT2 back-to-pitch offset):

### Static Rail, Motor & BFI Positions (Left `-X` / Right `+X` Symmetric)
- **Y-Rails (`2× MGN12H 300 mm`):**
  - Vertical mounting base: **`X = ±171.500 mm`**, **`Z_Y_MID = 391.500 mm`** (carriage inner mount face **`X = ±158.500 mm`**, `100%` clear inboard for double-shear XY-joint towers!).
  - Span: **`Y = [-142.000 .. +158.000]`** (`300.00 mm`). Raw Y-carriage center travel `Y_yc ∈ [-119.30 .. +135.30]`.
- **Rear Motors (`20T` Pulleys):**
  - Left Motor B (`Z_B = 370.00`): **`(-136.000, +154.000)`**
  - Right Motor A (`Z_A = 381.00`): **`(+136.000, +154.000)`**
  - Motor pulley Y-tangents:
    - Outer Y-run (`X_Y_MID`): **`±142.366 mm`** (`±136.000 ± 6.366`) — teeth INWARD toward motor.
    - Inner Y-run (`X_Y_INNER`): **`±129.634 mm`** (`±136.000 ∓ 6.366`) — teeth INWARD toward motor.
- **Front BFI Idler Tensioners (`F695-2RS` pairs):**
  - `F695` stack centers: **`X = ±149.496 mm`** (`±(142.366 + 7.130)`), **`Y_nom = -154.000 mm`** (`-158.0 .. -150.0` ±4.0 mm travel; `F695` flange `±[142.0..157.0]` clears `±158.5` Y-carriage X line!).
  - BFI Y-tangents:
    - Inner tangent (`X_Y_MID`): **`±142.366 mm`** (dead collinear with Motor outer tangent, **`ΔX = 0.000 mm`**!).
    - Outer tangent (`X_Y_OUTER`): **`±156.626 mm`** (`±(149.496 + 7.130)`).

### Moving Gantry & XY-Joint Positions (as a function of `Y_yc`, with `X_rail` fixed at `Y_xrail_back = Y_yc - 2.000`)
- **`300 mm` X-Rail:** `X = [-150.000 .. +150.000]`, `Y = [Y_xrail_back - 8.000 .. Y_xrail_back]` (`Y_yc - 10.0 .. Y_yc - 2.0`), `Z = [388.50 .. 400.50]`.
  - End `16.0 mm` seats (`|X| = [134.0 .. 150.0]`) pocketed into XY-Joints and bolted at `±137.50 mm` M3 counterbored rail holes (`100%` flush screw heads — `MGN12H` block glides over without collision up to `|X_c| = 115.0+ mm`, **`230+ mm` X stroke**!).
- **X-Gantry Belt Planes (Both Below X-Rail):**
  - **`Y_clamp`:** **`Y_xrail_back - 6.500 = Y_yc - 8.500`** (`Z_A = 381.0`, `Z_B = 370.0`, teeth facing **`+Y`** rearward).
  - **`Y_pass`:** **`Y_clamp + 12.732 = Y_yc + 4.232`** (cross-gantry return behind X-rail, teeth facing **`-Y`** forward).
- **XY-Joint Idler Centers (`3` rotating centers per side = `6` total on XY Joints):**
  - **`Left_XY_1` (`F695`, `Z_B = 370.00`):** `(-149.496, Y_clamp - 7.130) = (-149.496, Y_yc - 15.630)` — turns `+Y` (`X = -156.626`) `90°` CW to `+X` (`Y_clamp`).
  - **`Left_XY_2` (`F695`, `Z_B = 370.00`):** `(-122.504, Y_pass + 7.130) = (-122.504, Y_yc + 11.362)` — turns `-Y` (`X = -129.634`) `90°` CCW to `+X` (`Y_pass`).
  - **`Left_XY_2_A` (`20T` toothed, `Z_A = 381.00`):** `(-146.800, Y_clamp + 6.366) = (-146.800, Y_yc - 2.134)` — `180°` toothed U-turn from Belt A `Y_pass` (`-X`) into `Y_clamp` (`+X`) inside `Ø18.6 mm` bay.
  - **`Right_XY_1` (`F695`, `Z_A = 381.00`):** `(+149.496, Y_yc - 15.630)` (exact X-mirror of `Left_XY_1`).
  - **`Right_XY_2` (`F695`, `Z_A = 381.00`):** `(+122.504, Y_yc + 11.362)` (exact X-mirror of `Left_XY_2`).
  - **`Right_XY_2_B` (`20T` toothed, `Z_B = 370.00`):** `(+146.800, Y_yc - 2.134)` (exact X-mirror of `Left_XY_2_A`).

### Travel Envelope Verification (`220 × 220 mm` Bed)
- With compact monolithic `MGN12H` toolhead (`Nozzle = Y_xrail_back - 29.50 = Y_yc - 31.50`):
  - **Rear limit (`Y_yc_max = +125.0` w/ `Ø18 mm` idlers):** Right `XY_2_20T` `Ø18 mm` flange rear edge = `125.0 - 2.134 + 9.00 = +131.87 mm` (`0.63 mm` clear of Right motor plate `+132.5` and `0.98 mm` clear of `48 mm` motor body `+132.85`). Reachable nozzle rear = **`Y = +93.5 mm`**.
  - **Front limit (`Y_yc_min = -100.0`):** Y-carriage front = `-122.7 mm` (`15.3 mm` clear of Front BFI `-138.0`). Reachable nozzle front = **`Y = -131.5 mm`** (total Y stroke = **`225.0 mm`** centered around `Y = -19.0 mm` inside the `235 × 235 mm` bed, `Shroud V3.0` front stays `> 16 mm` clear of front frame wall!).
  - **X stroke:** `X_c ∈ [-118.0 .. +118.0]` = **`236.0 mm`** (`220 mm` bed + `±8 mm` overtravel, `> 6 mm` clear of `XY_2_A`/`XY_2_B` pulleys at `±149.0`).

---

## 5. Complete Hardware Bill of Materials (BOM)

> **Master project BOM (with toolhead, electronics & links):** [`BOM.md`](../../BOM.md)

| Qty | Item | Specification | Allocation |
|---:|---|---|---|
| **1** | X-Axis Linear Rail + Block | **uxcell `MGN12 300 mm`** rail + `MGN12H` block + mini install guide *(Ordered)* | Self-supporting X rail (remove end limit blocks before seating in XY-joint C-channels) |
| **2** | Y-Axis Linear Rails + Blocks | **IMETRX `MGN12H 300 mm`** rails + blocks, pre-oiled *(Ordered)* | `2×` vertical inward Y rails (`\|X\| = 171.50 mm`, `11` bolts/side) |
| **5 m** | Open Timing Belt | **FULARR `5 m × 6 mm` GT2 Belt** (`B07TFCPCJ2`; `2.52 m` installed, future upgrade: **Gates `LL-2GT-6`**) | Belt A (`~1.26 m`) + Belt B (`~1.26 m`) + spare |
| **5** *(2 used)* | Drive Pulley | **FULARR GT2 `20T` Pulley** (`5 mm` bore, `Ø16 × 16 mm`, hub-down, `B07TFCPCJ2`) | Rear A/B motors (3 spares) |
| **5** *(2 used)* | Toothed Idler | **FULARR GT2 `20T` Toothed Idler** (`5 mm` bore, **`Ø18 × 8 mm`**, `B07TFCPCJ2`) | `Left_XY_2_A` (`Z_A`) & `Right_XY_2_B` (`Z_B`) inside `Ø18.6 mm` bays (3 spares) |
| **20** *(14 used)* | Flanged Bearing | **M METERXITY `F695-2RS`** (`5 × 13 × 4 mm`, `Ø15 mm` flange, chrome steel, `B0F4XNK1GM` / `mma250226ty002421jp`, 20-pack) | `6` back-to-back pairs (`2×` BFI, `4×` XY joints) + `2×` rear double-shear motor caps + 6 spares |
| **1 set** *(8 used)* | Stainless Dowel Pin | **`Ø5 mm` 304 Stainless Dowel Pin Assortment** (`10/16/20/25/30/35/40 mm`; requires `>= 7× 5×20` & `>= 1× 5×30`) | `7×` `5×20 mm` (BFI + 5× XY joints) + `1×` `5×30 mm` (Left `XY_2_20T`) |
| **100** *(28 used)* | Bearing Shim | **`5 × 8 × 0.5 mm` 304 Stainless RC Bearing Shims** (100-pack) | `2× 0.5 mm` above/below each `F695` pair (`24`); `1 + 2` shims on `8 mm` FULARR `20T` idlers (`6` total; `28–30` used) |
| **1 set** | Hotend Heater / Thermistor | **AJOYIB `24 V 60 W` Ceramic Heater + `100K B25/50=3950K ±1%` Thermistor + Clip** *(Ordered)* | Toolhead TZ 2.0 upgrade (keep `Generic 3950`, set `heater_power: 60`, re-run `MPC_CALIBRATE`) |
| **4** | Tension Screws | **`M3 × 35 mm`** SHCS + `4×` M3 hex nuts | Twin door-accessible BFI tensioners (`2×` per side) |
| **44+** | Rail / Block Screws | **`M3 × 8 mm`** SHCS | `22×` Y-rail mounts (`11`/side) + `10×` X-rail (`±137.5` flush) + `12×` `MGN12H` blocks |
| **~50** | Structural Screws & Inserts | **`M3×4.6×5.7`** heat-set inserts (*On hand*, `~39×`, `Ø4.00 × 6.2–6.5 mm` pockets), `M3×12/16/20` SHCS, `M4×12/16`, `M5×12` BHCS | Frame corner mounts, Y-spines, rear 48 mm motor mounts, 2/3-piece split XY joints, belt clamps |
| **2** | Future XY Steppers | **`LDO-42STH48-2004MAH`** or **`2504MAH`** (`0.9°`, Class H `180 °C`, `48 mm` body, `24 mm` shaft) | Drop-in compatible once gantry is installed; stock `40 mm` AD5M motors fit if pulley is replaced with `20T` set-screw |
