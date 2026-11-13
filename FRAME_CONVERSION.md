> **Status — November 2026:** Planning reference for the future structural frame conversion (post-toolhead / post-gantry-measurement phase). Immediate priority remains reliable single-tool printing with the Octopus Pro V1.1 H723, EBB42 V1.2.1, and Eddy Duo on the existing AD5M chassis. Do not order extrusion cut lengths until the CAD assembly locks exact AWD motor/rail/tool-dock clearances. Read [AGENTS.md](AGENTS.md) and [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) first.

# Frame Conversion Plan (300×300×315 mm Euro 4040 Architecture)

This document defines the target envelope, Euro `4040` T-slot profile rules, linear-rail slot compatibility, preliminary Trident-derived sizing math, and power/heating implications for rebuilding the FlashForge AD5M into a `300 × 300 × 315 mm` Trident-like AWD CoreXY printer with independent triple-Z and eventual 4-head toolchanging.

---

## 1. Confirmed Target Envelope

- **Build plate:** `315 × 315 mm` (cast MIC6 / ATP-5 tooling plate + magnetic PEI spring steel)
- **Target printable XY area:** `300 × 300 mm` (`7.5 mm` plate margin per side)
- **Target Z travel:** `315 mm` (`+65 mm` taller than a standard `250 mm` Voron Trident)
- **Primary frame profile:** **Euro-standard `4040` T-slot aluminum extrusion** (single centered T-slot per face)

---

## 2. Structural Medium & Euro `4040` Profile Standards

For a one-off custom CoreXY / AWD conversion, **anodized T-slot aluminum extrusion (`6063-T5` / `6063-T6`)** is the only practical structural candidate (welded steel tube lacks T-slot adjustability; custom sheet metal locks geometry per revision; carbon tube crushes under bolt preload). Buy **T-slot** (flat bearing shoulders), **not V-slot**.

### Critical Distinction: Euro `4040` vs. 20-Series `4040`
Not all `4040` extrusions have the same face geometry:

| Standard | Slot Layout per 40 mm Face | Typical Slot Width | Core / End-Tap | Notes |
|---|---|---|---|---|
| **Euro `4040` Type-I** *(Item-style)* | **1 centered T-slot** | **8 mm** | M8 (or Ø6.8–7.3 mm smooth bore) | Centered rail mounting; smaller slot gap (`8 mm`) gives better rail shoulder width than Slot 10. |
| **Euro `4040` Type-B** *(Bosch-style)* | **1 centered T-slot** | **10 mm** | M8 / M10 (usually Ø8.5 / Ø10 mm) | Centered rail mounting, heavy-duty industrial hardware; wide `10 mm` slot requires care with narrow linear rails (see §3). |
| **20-Series `4040`** *(e.g. Misumi `HFS5-4040`)* | **2 parallel slots** (`20 mm` apart) | **5 mm or 6 mm** | Dual/quad M5/M6 | Shares `2020` T-nuts, but has **no center slot** on the 40 mm face. |

**Since you are targeting Euro `4040` with a single centered slot:** check your supplier's exact CAD cross-section to confirm whether it is **Slot 8 (Type-I)** or **Slot 10 (Type-B)** before buying any T-nuts, corner gussets, or linear rails.

---

## 3. Linear-Rail & Moving-Beam Compatibility on Euro `4040`

Having a centered slot solves the `20 mm`-offset problem, **but Euro `4040`'s wide slot (`8 mm` or `10 mm`) creates a rail-width and fastener mismatch with standard small Voron rails**:

| Rail Size | Rail Base Width | Rail Bolt | Direct Fit on Euro `4040` **Slot 8 (8 mm)** | Direct Fit on Euro `4040` **Slot 10 (10 mm)** | Recommendation |
|---|---|---|---|---|---|
| **`MGN9`** | `9.0 mm` | M3 | **Unsafe** (`0.5 mm`/side lip before chamfer) | **Impossible** (narrower than `10 mm` slot!) | Do **not** bolt `MGN9` directly onto Euro `4040` without a solid backing plate or `2020` sub-rail. |
| **`MGN12`** | `12.0 mm` | M3 | **Marginal–workable** (`2.0 mm`/side before lip chamfer; needs Slot-8 **M3** T-nuts + lip check) | **Very tight** (`1.0 mm`/side before chamfer — often overlaps slot radius) | Verify exact extrusion lip chamfer; or use a thin aluminum backing strip / `2020` rail bar. |
| **`MGN15`** | `15.0 mm` | **M4** | **Good** (`3.5 mm`/side shoulder; native M4 Slot-8 T-nuts) | **Good** (`2.5 mm`/side shoulder; native M4 Slot-10 T-nuts) | Strongest direct-bolt option for **Y and Z rails** on Euro `4040`. |

### Keep the Moving X-Axis Beam Light (`2020` or CNC Alloy, Not `4040`)
Even with a `4040` outer cube, **do not use `4040` for the moving X-axis gantry beam**:
- Euro `4040` is ~`1.5–1.9 kg/m` vs ~`0.5–0.6 kg/m` for `2020` (~`400–500 g` extra dead moving mass on a ~`420 mm` span).
- Use **`2020` (5/6 mm slot) + `MGN12H`** (or a lightweight CNC aluminum / carbon-backed X beam) so Y-axis acceleration and input-shaper resonance (`zv`/`mzv`) stay high. Printed/CNC XY joints bridge the `4040` Y-rail carriages to the `2020` X beam cleanly.

---

## 4. Preliminary Envelope & Extrusion Sizing Math

Derived from the archived Voron Trident configurator formulas ([`configurator_trident.js`](reference/Voron_Trident/BOM_and_sourcing/configurator_trident.js) and [`REFERENCE_BOM_300.md`](reference/Voron_Trident/BOM_and_sourcing/REFERENCE_BOM_300.md)) and adjusted for:
1. **`315 × 315 mm` plate** (`+10 mm` wider than stock Trident `304.8 mm` 12" plate → `+10 mm` internal X/Y clearance recommended).
2. **`315 mm` Z travel** (`+65 mm` over Trident `250 mm` Z).
3. **`4040` outer frame members** (`40 mm` thickness vs `20 mm` in Trident → `+40 mm` outer X/Y for the same internal cavity, and `+20 mm` per `4040` horizontal beam height in Z).

> **Important:** These are **starting envelope estimates**, not final cut lengths. Exact lengths depend on your chosen corner joinery (blind joints vs corner gussets/cubes), AWD front-motor overhang, and whether 4 toolhead docks sit inside a stretched Y bay.

| Parameter | Stock `300×300×250` Trident (`2020`) | Baseline `4040` Euro (`315` plate, `315` Z, no dock stretch) | Dock-Ready `4040` Euro (`300×300` + 4 tool docks in `+Y`) | Notes |
|---|---|---|---|---|
| **Build plate** | `304.8 × 304.8 mm` (12") | `315 × 315 mm` | `315 × 315 mm` | `300 × 300 mm` printable area |
| **Internal X cavity** | `420 mm` | `~430 mm` | `~430 mm` | Keeps Trident's `~120 mm` X clearance + `10 mm` plate oversize |
| **Internal Y cavity** | `420 mm` | `~430 mm` | `~510–550 mm` | Add `+80–120 mm` Y if parking 4 heads without losing `300 mm` printable Y |
| **Outer Frame X** | `460 mm` | **`~510 mm`** | **`~510 mm`** | `inner_X + 2 × 40 mm` |
| **Outer Frame Y** | `460 mm` | **`~510 mm`** | **`~590–630 mm`** | `inner_Y + 2 × 40 mm` |
| **Outer Frame Z** | `500 mm` (`250` Z) | **`~605–625 mm`** | **`~605–625 mm`** | `315` Z + `~250` Trident overhead + `+40 to +60 mm` for `4040` top/deck/bottom beams |
| **Linear Rail Lengths (nominal)** | X: `350`, Y: `350`, Z: `300` | X: `~360–400`, Y: `~360–400`, Z: `~370–400` | X: `~360–400`, Y: `~450–490`, Z: `~370–400` | Verify carriage + bumper + endstop stroke before picking standard `350`/`400`/`450`/`500 mm` rails |
| **Z Leadscrews (`TR8×4`)** | `300 mm` | `~370–400 mm` | `~370–400 mm` | `400 mm` integrated NEMA17 `TR8×4` is a common off-the-shelf length |

---

## 5. Joinery, Materials & Hardware Checklist

- **Precision cuts:** Request `±0.2 mm` cut tolerance and **paired matched lengths** (all 4 verticals cut identically, all X horizontals identically, all Y horizontals identically).
- **Corner joinery on Euro `4040`:**
  - **Blind joints (`M8` end-tap + access hole):** Very clean flush surfaces for enclosure panels; requires an `M8` tap (often self-tapping or standard cut tap depending on bore size) and accurate access holes in mating beams.
  - **Heavy `4040` cast corner brackets / CNC gusset plates:** Zero end-drilling required, high shear/racking stiffness for AWD frames; ensure bracket ribs don't interfere with Y/Z linear rail faces or enclosure panels.
- **Wall thickness:** Choose standard/heavy-wall Euro `4040` (`≥ 2.2–2.5 mm` minimum wall, ~`1.5–1.9 kg/m`), not ultra-light `~1.2 kg/m` economy profiles.
- **Finish:** Clear/silver anodized is cheaper and typically faster to source than black anodized.

---

## 6. Power, Bed Heating & AD5M Carryover Reality Check

Scaling from the stock AD5M `220 × 220 mm` bed to a **`315 × 315 mm` plate** changes the electrical/thermal architecture:
- **Bed heater:** Voron's sizing formula (`0.0055 × 300 × 300 ≈ 495 W`, stock `300` Trident uses a `250 × 250 mm` `450 W` **AC silicone heater + SSR + 150 °C thermal fuse**). Heating a `315 × 315 mm` thick cast plate (`~250×250` or `280×280 mm` silicone pad, `500–600 W`) via mains **AC + SSR** (Voron Trident style) is far cleaner than trying to pull `500+ W` (`>20 A` continuous) at `24 V DC`.
- **PSU budget:** The stock AD5M **`24 V 14.6 A` (`350.4 W`) PSU** cannot power a `500 W` bed + 4 concurrent hotends + 7–8 steppers. Keep the existing `24 V` PSU + ReliaBot MOSFET for the active AD5M phase, and plan an AC bed + SSR (plus `≥ 200–350 W` dedicated `24 V` logic/stepper/toolhead PSU, or `48 V` XY motor rail if going high-speed AWD) for the `4040` frame conversion.
- **Carryover from current AD5M build:** `Pi 5`, `Octopus Pro V1.1 H723`, `BTT HDMI5`, `EBB42 V1.2.1` (CAN), `Eddy Duo`, `Dragon Burner` + `Orbiter 2.5` + `Bambu X1C` hotend, and existing `TMC2209` drivers (add extra drivers for triple-Z + AWD).

---

## 7. Next Steps Before Ordering Extrusions

1. **Confirm Euro `4040` vendor profile** (`Slot 8` Type-I vs `Slot 10` Type-B) and check exact rail lip width (`MGN12` vs `MGN15`).
2. **Decide toolchanger Y strategy:** Stretch Y (`~590–630 mm` outer Y) to preserve full `300 × 300 mm` print area with 4 parked toolheads, or build compact (`~510 × 510 mm`) and lose ~`70–90 mm` of Y when docks are installed.
3. **Select AWD motor placement** (front corners inside vs outside frame profile) and **triple-Z leadscrew/rail layout** in CAD so exact cut lengths (`X`, `Y`, `Z`, and `2020` X-beam + bed-frame members) can be exported cleanly.
