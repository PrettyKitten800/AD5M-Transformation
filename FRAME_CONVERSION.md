> **Status — November 2026:** Planning baseline for the future structural frame conversion (post-toolhead / post-gantry-measurement phase). Immediate priority remains reliable single-tool printing with the Octopus Pro V1.1 H723, EBB42 V1.2.1, and Eddy Duo on the existing AD5M chassis. Read [AGENTS.md](AGENTS.md) and [UPGRADE_ROADMAP.md](UPGRADE_ROADMAP.md) first.

# Frame Conversion Plan (Voron Trident 300×300×300 mm Baseline)

Per user decision (November 12, 2026), the structural frame conversion follows **standard Voron Trident `2020` sizing for `300 × 300 mm` in X/Y**, scaled to **`300 mm` Z travel** (`+50 mm` taller than the stock `250 mm` Z configurator preset).

This keeps direct compatibility with archived Voron Trident CAD, printed parts, and AWD-Trident community mods in [`reference/Voron_Trident/`](reference/Voron_Trident/START_HERE.md).

---

## 1. Frame Envelope & Motion Summary (`300 × 300 × 300 mm`)

Derived directly from [`configurator_trident.js`](reference/Voron_Trident/BOM_and_sourcing/configurator_trident.js) (`build_x = 300`, `build_y = 300`, `build_z = 300`, blind-joint `2020` frame):

| Parameter | Value | Notes |
|---|---|---|
| **Build volume** | **`300 × 300 × 300 mm`** | Standard Trident XY; `+50 mm` Z over `REFERENCE_BOM_300.md` |
| **Outer frame (`X × Y × Z`)** | **`460 × 460 × 550 mm`** | `build_xy + 160 mm`, `build_z + 250 mm` |
| **Internal XY cavity** | **`420 × 420 mm`** | `frame_xy - 40 mm` (`2 × 20 mm` uprights) |
| **Profile standard** | **Misumi `HFSB5-2020`** | `20 × 20 mm` T-slot, **5 mm slot**, black anodized (`HFS5-2020` for silver) |
| **Linear rails** | **`1× MGN12H 350 mm` (X)**, **`5× MGN9H 350 mm` (2× Y, 3× Z)** | `300 mm` Z puts X, Y, and Z rails all at standard `350 mm` length |
| **Z leadscrews** | **`3× NEMA17 TR8×4 350 mm`** | Standard `350 mm` integrated leadscrew steppers |
| **XY open belts** | **`2× LL-2GT-6 (6 mm)` — `1,890 mm` each** | Stock `300` Trident baseline; recalculate if using 9 mm belts or AWD front-motor routing |
| **Electronics DIN rails** | **`2× 420 mm` (35 mm DIN 3)** | Matches `420 mm` horizontal span |

---

## 2. Complete `2020` Extrusion Cut & Machining List

**Total `HFSB5-2020` extrusion:** **19 pieces = `8,152 mm` (`8.152 m`)**

| ID | Misumi Part Number | Qty | Length | Total | Role & Blind-Joint Machining |
|---|---|---:|---:|---:|---|
| **A** | `HFSB5-2020-420-TPW` | **9** | `420 mm` | `3,780 mm` | Horizontal outer frame X/Y beams + Y-rail gantry beams (`TPW` = M5 tapped both ends) |
| **B** | `HFSB5-2020-550-LCP-RCP-AV410` | **4** | `550 mm` | `2,200 mm` | 4 vertical corner uprights (`Ø6 mm` access bores at ends + `410 mm` from top/bottom per Trident blind-joint datum for electronics deck) |
| **C** | `HFSB5-2020-420-AH210-TPW` | **1** | `420 mm` | `420 mm` | Lower rear horizontal (`M5` tapped both ends + center `Ø6 mm` access hole at `210 mm` for `H`) |
| **D** | `HFSB5-2020-290` | **1** | `290 mm` | `290 mm` | Rear cross bar for gantry (`build_x - 10`; plain ends) |
| **E** | `HFSB5-2020-380` | **1** | `380 mm` | `380 mm` | Moving X-axis gantry extrusion (`build_x + 80`; plain ends) |
| **F** | `HFSB5-2020-420-AH210` | **1** | `420 mm` | `420 mm` | Front/main bed frame extrusion (`Ø6 mm` center access hole at `210 mm` for `G`) |
| **G** | `HFSB5-2020-282-LTP` | **1** | `282 mm` | `282 mm` | Rear bed frame leg (`build_y - 18`; `LTP` = M5 tapped one end) |
| **H** | `HFSB5-2020-380-LTP` | **1** | `380 mm` | `380 mm` | Vertical rear center Z-rail post (`build_z + 80`; `LTP` = M5 tapped one end) |

> **Sourcing note:** Many Voron frame kits (LDO / Formbot / Misumi) bundle standard `300 × 300 × 250` cuts (`500 mm` `B` and `330 mm` `H`). If ordering a custom `300 mm Z` frame or raw `HFS5-2020` lengths, swap `B` (`4× 550 mm`, `AV410`) and `H` (`1× 380 mm`) and add `+3× M3×8 SHCS` + `+3× M3 drop-in T-nuts` above [`REFERENCE_BOM_300.md`](reference/Voron_Trident/BOM_and_sourcing/REFERENCE_BOM_300.md) for the extra mounting screw on each `350 mm` Z rail.

---

## 3. Enclosure Panels & Build Plate Sizing (Scaled for `300 mm` Z)

From [`configurator_trident.js`](reference/Voron_Trident/BOM_and_sourcing/configurator_trident.js):
- **Deck + bottom Coroplast (`4 mm`):** `2×` `419 × 419 mm`
- **Back Coroplast (`4 mm`):** `1×` `432 × 522 mm` *(+50 mm height vs 250 Z)*
- **Top Acrylic (`3 mm`):** `1×` `433 × 433 mm`
- **Side Acrylic (`3 mm`):** `2×` `433 × 523 mm` *(+50 mm height vs 250 Z)*
- **Front Doors Acrylic (`3 mm`):** `2×` `216.5 × 523 mm` *(+50 mm height vs 250 Z)*
- **Build Plate & Bed Heating:** Stock Trident `300` specifies a `12" × 12"` (`304.8 × 304.8 mm`) `5/16"` MIC6 plate + PEI + `250 × 250 mm` `450 W` Keenovo **AC silicone heater + SSR + 150 °C thermal fuse** (do not attempt to run a 300-class heated bed off the stock AD5M `24 V 14.6 A` PSU).

---

## 4. AD5M-Transformation Integration Notes (AWD & Toolchanger)

1. **AWD Stiffness on a `2020` Frame:** `2020` is plenty rigid at `460 × 460 × 550 mm` when assembled with **true blind joints**, **metal corner gussets/brackets** where clear of belts/rails, and **rigid stressed-skin enclosure panels** (e.g., 3–4 mm ACM/aluminum composite or solid panels bolted cleanly to the frame).
2. **Slot Standard Lock (`5 mm` vs `6 mm`):** Genuine Misumi `HFSB5-2020` uses a **5 mm slot**—ensure `M3`/`M5` drop-in and hammerhead T-nuts match 5-series extrusions (generic 6 mm Amazon M5 T-nuts often do not fit 5 mm Misumi slots).
3. **Printable Area with AWD + 4 Toolheads:** Keeping the standard `420 × 420 mm` internal Trident cavity means front AWD motors and future 4-toolhead docks inside the frame will consume part of the `300 × 300 mm` envelope unless Y is later extended or dock geometry is tightly packaged.
4. **Hardware Carryover:** `Pi 5`, `Octopus Pro V1.1 H723`, `BTT HDMI5`, `EBB42 V1.2.1` (CAN), `Eddy Duo`, `Dragon Burner` + `Orbiter 2.5` + `Bambu X1C` hotend, and existing `TMC2209` modules carry forward; plan additional `TMC2209` drivers for triple-Z and AWD motors plus mains AC bed + SSR wiring.
5. *(Earlier notes exploring a custom Euro `4040` / `315 × 315 mm` plate conversion are superseded by this standard Trident `300 × 300 × 300 mm` `2020` baseline; preserved in git history.)*
