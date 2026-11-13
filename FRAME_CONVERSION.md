> **Status — November 2026:** Planning reference for the future structural frame conversion (post-toolhead / post-gantry-measurement phase). Immediate priority remains reliable single-tool printing with the Octopus Pro V1.1 H723, EBB42 V1.2.1, and Eddy Duo on the existing AD5M chassis. Do not order extrusion cut lengths until the physical bed/Z measurements and tool-dock Y-depth envelope below are locked in. Read [AGENTS.md](AGENTS.md) and [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) first.

# Frame Conversion Plan (Aluminum Extrusion & Structural Materials)

This document defines the material selection, aluminum extrusion profile tradeoffs, fastener ecosystem rules, and pre-order measurements for rebuilding the FlashForge AD5M into a rigid, Trident-like AWD CoreXY printer with independent triple-Z and eventual 4-head toolchanging.

---

## 1. Structural Medium: Why T-Slot Aluminum Extrusion

For a one-off custom CoreXY / AWD conversion, **anodized T-slot aluminum extrusion (`6063-T5` / `6063-T6`)** is the only practical structural candidate:
- **Welded steel square tube:** High stiffness, but requires weld fixtures and post-weld machining, adds major weight, and lacks continuous T-slots for adjustable rail/panel/dock mounting.
- **Custom bent sheet metal / CNC plates (like stock AD5M):** Requires new laser/brake runs for any dimensional revision and complicates custom linear-rail, AWD motor, and triple-Z alignments.
- **Carbon fiber square tube:** Poor local bolt-clamping and crush resistance without bonded metal inserts; poor dimensional repeatability for rail seating.

**Rule on profile style:** Buy **T-slot** (flat outer shoulders and square slot lips for full-width linear-rail contact and rigid T-nut clamping), **not V-slot** (chamfered V-grooves reduce rail seating area and T-nut contact).

---

## 2. Extrusion Size Comparison (`4040` vs `3030` vs `2040` vs `2020`)

The target machine combines **AWD (4 XY motors)**, **triple-Z**, and **4 parked toolheads**, which places much higher belt tension and corner-motor reaction torque on the upper frame than a standard stock Voron Trident. However, using oversized extrusion everywhere creates rail-mounting and moving-mass problems.

| Architecture Option | Outer Posts / Frame | Moving X-Axis Beam | Linear Rail Seating (`MGN9`/`MGN12`) | Mass & Stiffness | Key Pros & Tradeoffs |
|---|---|---|---|---|---|
| **A. Hybrid `4040` (20-series) + `2020`** *(Strong candidate if choosing 4040)* | **20-series `4040`** (Slot 5 or 6, 20 mm slot pitch) | **`2020`** (or light CNC alloy) | Center on `2020` X; offset on one `4040` sub-slot or via adapter plate for Y | Frame ~1.5–1.9 kg/m ($I \approx 8.5\text{–}10.5\text{ cm}^4$); X ~0.55 kg/m | Maximum corner stiffness and wide mounting faces for AWD motor blocks + gussets while keeping low moving X-axis mass and shared `M3`/`M5` 20-series hardware. Adds `+40 mm` outer X/Y footprint vs `2020` and requires custom/remixed motor & rail mounts. |
| **B. `3030` Frame + `2020` X-Gantry** *(Balanced AWD sweet spot)* | **`3030`** (Slot 8, single centered slot) | **`2020`** (or CNC alloy) | **Centered directly** on every 30 mm face (`MGN9`/`MGN12` bolt straight down the middle) | Frame ~0.95–1.1 kg/m ($I \approx 2.8\text{–}3.5\text{ cm}^4$) | ~4× stiffer in bending than `2020`, **single centered slot** avoids `4040`'s dual-slot rail offset issue, and only adds `+20 mm` outer width vs `2020`. Uses M6/M8 blind joints or Slot-8 brackets; requires custom motor/Z mounts (non-stock-Trident). |
| **C. `2040` Perimeter + `2020` X-Gantry** | **`2040`** (20-series Slot 5/6) | **`2020`** | **Centered directly** on the 20 mm narrow face | Frame ~0.95–1.1 kg/m (anisotropic stiffness) | Double-slot stiffness along the primary bending axis while keeping a native 20 mm rail face and 100% `M3`/`M5` 20-series T-nut compatibility. Requires care with corner joint orientation. |
| **D. Standard `2020` (Voron Trident Baseline)** | **`2020`** (e.g. Misumi `HFSB5-2020`) | **`2020`** | **Centered directly** on all faces | Frame ~0.5–0.6 kg/m ($I \approx 0.7\text{ cm}^4$) | 100% compatible with archived [`reference/Voron_Trident/`](reference/Voron_Trident/) STLs, AWD Trident mods, and BOMs ([250 mm](reference/Voron_Trident/BOM_and_sourcing/REFERENCE_BOM_250.md)). Relies on blind joints + metal corner gussets + 3–4 mm stressed-skin panels to resist AWD racking. |

### Critical Engineering Notes on `4040`
1. **Never use `4040` as the moving X-axis beam:** At ~1.5–1.9 kg/m (~3× the mass of `2020`), a `4040` X-beam adds ~400–500 g of moving mass to the Y-axis, hurting acceleration and lowering Y-axis input-shaper resonance (`zv`/`mzv`). Always keep the moving X beam to `2020` (or a dedicated lightweight CNC aluminum/CF beam).
2. **`4040` has TWO parallel T-slots, not a center slot:** Each 40 mm face has two slots at `±10 mm` from centerline (`20 mm` pitch). An `MGN9` (9 mm) or `MGN12` (12 mm) rail cannot bolt down the centerline of a `4040` face using a single row of T-nuts—you must either mount the rail over one of the two offset slots (shifting gantry/belt geometry by 10 mm), use a wider rail/adapter plate, or step down to `3030` / `2040` / `2020` on rail-bearing faces.
3. **Avoid mixing slot systems (`20-series 4040` vs `40-series 4040`):**
   - **20-series `4040` (Slot 5 or Slot 6, e.g., Misumi `HFS5-4040`):** Four `20×20` quadrants on a `20 mm` pitch; accepts the same `M3`/`M5` T-nuts and mates cleanly to `2020` / `2040` sub-members.
   - **40-series `4040` (Slot 8 or Slot 10, heavy industrial):** Uses bulky M8/M10 hardware and does **not** share T-nuts or slot geometry with `2020`. If going with `4040` in a hybrid frame, strongly prefer **20-series `4040`** (or keep `3030` Slot 8 + `2020` X beam separate via printed/CNC XY joint blocks).

---

## 3. Sourcing & Material Specs to Check Before Buying

- **Alloy & Wall Thickness:** Specify `6063-T5` (standard industrial/Misumi) or `6063-T6`. Avoid thin-wall "lite" extrusions (`< 1.5 mm` wall); look for standard/heavy wall (`≥ 1.8–2.0 mm` on 20-series, `≥ 2.2–2.5 mm` on `3030`/`4040`) so tapped ends and T-slots resist thread stripping under AWD belt preload.
- **Slot Width Standard (lock one before ordering T-nuts):**
  - *Misumi 5-series (`HFS5`/`HFSB5`):* **5 mm slot** — requires 5-series T-nuts (many generic 6 mm Amazon M5 T-nuts will not drop into Misumi 5 mm slots).
  - *Generic / Open-style 20-series:* **6 mm slot** — wider T-nut availability, slightly looser fit with Misumi-spec parts.
  - *`3030`:* Usually **8 mm slot** (some profiles 6 mm — verify drawing before ordering fasteners).
  - *`4040` (20-series vs 40-series):* Confirm whether the vendor sells **Slot 5/6 (20-series)** or **Slot 8/10 (40-series)**.
- **Cut Accuracy & Squareness:** Order **precision-cut, paired/matched lengths** (`±0.2 mm` tolerance or better, square end faces) so all 4 verticals, all X horizontals, and all Y horizontals match identically without racking the linear rails.
- **Corner Joinery Strategy:**
  - **Blind joints** (center-tapped extrusion ends + access bore in mating beam): Cleanest flush interior/exterior faces for enclosure panels and rail clearance; requires accurate drilling/tapping or vendor machining (`LCP`/`RCP`/`TPW` style).
  - **External/Internal Gussets & Corner Plates** (CNC aluminum 90° plates or cast corners): Zero end-drilling required, high racking stiffness for AWD frames, especially straightforward on `4040` or `3030` outer faces.
- **Finish:** Clear/silver anodized is typically cheaper and ships faster than black anodized (`REFERENCE_BOM_250` sourcing notes flag black Misumi lead-time spikes).

---

## 4. Architecture & Envelope Sizing Decisions (Lock Before Ordering Cuts)

Before calculating exact extrusion lengths, resolve these four design choices from [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md):

1. **Toolchanger Dock Envelope (`Y` Depth & Bed Size):**
   - Stock AD5M build area is `220 × 220 mm`.
   - Parking 4 toolheads inside a tight `220 × 220` enclosure steals ~`60–90 mm` of Y travel unless the frame is stretched in **Y** (or tool docks are mounted in a deeper front/rear bay). Decide whether to target **`220 × 220 mm` printable + ~80–120 mm dock bay** or expand to a **`250 × 250 mm` Trident bed** (`REFERENCE_BOM_250.md`).
2. **AWD Corner Motor Layout:**
   - 4 XY motors (2 rear + 2 front corners) need clear corner geometry and double-shear pulley/idler support (`F695` bearings, `5 mm` shafts, 6 mm or 9 mm GT2 belts). `4040` or `3030` corner posts handle front AWD bracket overhang well, provided motor plates don't block front toolchanger docks.
3. **Z-Axis Architecture (Stock Single-Z vs Independent Triple-Z):**
   - Decide whether the frame conversion transitions directly to **Trident-style independent triple-Z** (`3× NEMA17 TR8x4` integrated leadscrew motors or belted triple-Z + `GE5C` spherical joints + `MGN9H`/`MGN12H` Z rails) or temporarily adapts the AD5M bed/leadscrews.
4. **AD5M Carryover vs Replacement Hardware:**
   - **Carry over:** `Pi 5`, `Octopus Pro V1.1 H723`, `BTT HDMI5`, `EBB42 V1.2.1` (plus 3 more for 4 heads), `Eddy Duo`, `Dragon Burner` + `Orbiter 2.5` + `Bambu X1C` hotend; optionally AD5M `220×220` bed + external ReliaBot MOSFET + `24 V 14.6 A` PSU (re-evaluate `350.4 W` PSU budget before powering 4 concurrent hotends).
   - **Replace:** Stock stamped/bent sheet-metal frame, plastic top/side skins, smooth XY guide rods/bushings (`MGN12`/`MGN9` rails replace them), and synchronized single-motor Z.

---

## 5. Physical Measurements Required From the AD5M First

Use [STOCK_GANTRY_AND_BELTS.md](reference/AD5M_gantry_research/STOCK_GANTRY_AND_BELTS.md) together with these frame/bed measurements before drafting final cut lengths:
1. Measure actual AD5M build-plate outer width/depth, bed-carriage mounting hole spacing, and minimum nozzle overhang outside the bed (needed to size dock reach).
2. Measure stock Z leadscrew pitch/diameter, guide-rod spacing, and usable Z stroke if reusing any stock bed/Z components.
3. Measure the electronics deck footprint (`Octopus Pro V1.1`, `Pi 5`, `ReliaBot MOSFET`, `24 V` PSU, and future 2nd PSU or DIN rail clearances) to determine lower electronics skirt height (`Z_bottom`).
4. Cross-check against [`AD5M_Frame.STEP`](reference/AD5M_gantry_research/official_frame_model/AD5M_Frame.STEP) only after spot-checking physical dimensions on the printer (official STEP files omit moving gantry/belt hardware and are not yet verified against the physical machine).
