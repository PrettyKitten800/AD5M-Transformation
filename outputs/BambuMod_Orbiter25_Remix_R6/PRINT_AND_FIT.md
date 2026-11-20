# BambuMod × Orbiter v2.5 Primary_R6 — Print & Fit Notes

**Active print-ready revision (`Primary_R6`)** replacing earlier unprinted drafts (`R1`–`R5` preserved for history).
Upstream attribution: remixed from **Kirill_Wawe — BambuMod for FF Adventurer 5M** (`CC BY-NC-SA 4.0`, <https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m>) and **Orbiter v2.5** (<https://www.orbiterprojects.com/orbiter-v2-5/>); reference hotend envelope is the user-confirmed **Bambu Lab X1C** heatsink (`Jorge` reference STEP). Physical test-fit pending after printing.

---

## What Changed from Primary_R5 -> Primary_R6

1. **Restored Twin Rear Captive M3 Hex-Nut Pockets (X1C Hotend Screws):**
   - Centered coaxially with the shifted X1C M3 screw bores (`(-9.760, 27.220)` and `(-2.910, 27.220)`, matching Kirill's `6.85 mm` pitch and `R1`–`R5` front holes).
   - Horizontal flat-top/flat-bottom hexagonal profile (`AF = 5.60 mm`, circumradius `3.233 mm`), opening at the rear (`-Y`) carriage face (`Y = -11.117`) with a `0.45 mm` build-plate entry bevel (`AF = 6.30 -> 5.60 mm`) so elephant's foot does not pinch DIN 934 M3 nuts.
   - Stops forward at a flat perpendicular bearing shoulder at `Y_HEX_SEAT = -3.500 mm` (`7.62 mm` pocket depth), maintaining **`0.89 mm` minimum solid wall** behind the smooth C2 air tunnel (`0.0000 mm³` fin or duct clash) and transitioning cleanly into the `Ø3.30 mm` (`r = 1.65 mm`) screw bores through to `Y = 8.28`.
2. **Smooth Rear Motor Circle Refined to `Ø41.00 mm` (`R = 20.50 mm`):**
   - Centered at `(X = 0.000, Z = 51.900)` (`1.50 mm` smaller radius than `R5`'s `Ø44.00 mm`).
   - Preserves `> 1.6–2.5 mm` air gap completely around the `Ø36.4–37.8 mm` Orbiter/LDO motor (`0.0 mm³` contact), strengthens the upper EBB42 portal bridge by `+1.50 mm` (`7.60 mm` min bridge height), and guarantees a **`>= 1.06 mm` solid rim even at the right bevel mouth** (`1.42 mm` along the full pocket body) above the Right `(-2.910, 27.220)` hex pocket.
3. **Preserved All `R4` & `R5` Verified Improvements:**
   - Smooth 15-station C2 periodic B-spline cooling tunnel (`build_smooth_duct_void()`, `0.0000 mm³` X1C collision / `0.0` duct obstruction).
   - Perpendicular `Ø9.00 mm` `+X` Orbiter nut boss (`Z_NUT_FACE = 27.60 mm`, `4.98 mm` plate grip, `Ø12.40 mm` moat, `Ø3.60 mm` through-bore).
   - 4 blind rear-only carriage holes (`low_R/L`, `up_R/L`, `5.54 mm` deep, hidden from front), clean EBB42 top bridge (`4× Ø4.1 mm` bores at `X = ±18, ±27`), and `3010` fan cradle.

---

## Hardware / Fastener Notes

| Joint | Fastener | Notes |
| --- | --- | --- |
| Bambu X1C heatsink -> adapter | **2× M3×22** or **M3×25 SHCS** + **2× M3 DIN 934 hex nuts** | Front heatsink flange sits at `Y = 15.83 mm`; nut seats at `Y = -3.50 .. -5.90 mm` (`19.33–21.73 mm` grip). `M3×22` fills the nut flush; `M3×25` ends at `Y = -9.17 mm`, recessed `1.95 mm` shy of the steel carriage face (`-11.12 mm`). *(An `M3×20` reaches `-4.17 mm`, engaging `< 0.7 mm` / ~1.3 threads — use `M3×22` or `M3×25` for full engagement.)* |
| Orbiter v2.5 `-X` lug `(-23.85, 12.08)` | M3×10–12 + M3 heat-set or self-tapping | `4.3 mm` blind bore in `32.60 mm` top plate. |
| Orbiter v2.5 `+X` lug `(+13.15, 12.08)` | M3×10–12 + M3 hex/flange nut (bottom) | `4.98 mm` flat boss (`Z_NUT_FACE = 27.60 mm`), open `Ø12.4 mm` clearance pocket below. |
| Steel X-carriage -> adapter (`4×` blind) | Stock 4× M3 carriage bolts (`~5.5 mm` pocket) | Check bolt length does not bottom `5.54 mm` blind bore; add 1 M3 washer if needed. |
| `3010` hotend fan | 4× M2.5 self-tapping screws | Aligned coaxially with Kirill's `Ø2.6–3.6 mm` fan cradle bosses. |
| EBB42 top bridge | 4× M3 heat-set inserts / bolts | `±18.0, ±27.0 mm`, `Y = -7.498 mm`, `Z = 73.1..80.0 mm`. |

---

## Recommended Print Settings

- **STL orientation:** [`BambuMod_Orbiter25_Primary_R6.stl`](BambuMod_Orbiter25_Primary_R6.stl) is pre-oriented flat on its rear (`-Y`) carriage face (`Z_bed = 0.000..43.236 mm`, X `[-29.998..30.000]`, Y `[-0.000..80.002]`).
- **Material:** ABS, ASA, PC-CF, or PA12-CF (`>= 95 °C` HDT for enclosed chamber & hotend proximity).
- **Perimeters / Infill / Layer:** `0.20 mm` layer height, **4 perimeters** (`0.40–0.42 mm` line width), `>= 40%` gyroid or grid infill, **no supports** on screw bores or smooth cooling tunnel (horizontal rear-plate hex-to-bore bridge steps only `1.15 mm` at `Z_bed = 7.62 mm`; use selective tree supports under the suspended front shroud / Orbiter plate shelf only if your bridging profile needs them).
- **Pre-assembly check:** Insert the two DIN 934 M3 hex nuts into the rear hex mouths (`Z_bed = 0`) using a helper M3 screw to draw them snug up against the flat `-3.50 mm` shoulder BEFORE bolting the adapter to the steel carriage.

---

## Automated CAD Validation Summary (`validation.json`)

- **STEP (`BambuMod_Orbiter25_Primary_R6.step`):** Valid BRep, `1` solid, **`38,465.86 mm³`**.
- **STL (`BambuMod_Orbiter25_Primary_R6.stl`):** Watertight solid, `0` non-manifold edges (`trimesh: True True 38441.19 1`), `40,874` facets, **`38,440.89 mm³`** (`0.0649%` diff vs STEP).
- **Collisions (`9` envelopes):** `0.0 mm³` (`adapter_vs_x1c_hotend = 0.0`, Orbiter, M3 bolts, `3010` fan, EBB42 bracket, carriage plane, low/high belts).
- **Hex pockets:** `0.0 mm³` screw-bore/hex-prism obstruction, `1.0` flat bearing shoulder, `>= 0.890 mm` solid wall to cooling duct, `>= 1.058 mm` solid rim above Right hex to `Ø41.00 mm` motor circle (`1.0` upper bridge integrity).
