# BambuMod x Orbiter v2.5 AD5M Adapter — Offset-Hotend Remix (`Primary_R5`)

> **Untested physically on hardware:** Verify printed clearances, rear M3 blind-hole bolt length (`< 5.3 mm` insertion into rear face), Orbiter v2.5 bolt + nut clamping, X1C heatbreak seating, and Klipper `[probe_eddy_ng]` / hotend X offset (`-6.335 mm`) before powering or printing live.

## What Changed in `R5` (over preserved `R1`–`R4`)

`Primary_R5` builds on Kirill_Wawe's BambuMod AD5M carriage adapter (`#1574762`, CC BY-NC-SA 4.0) and retains all `R4` structural simplifications while refining the internal cooling duct and the `+X` extruder mounting hole near the hotend fan:

1. **Smooth C2 B-Spline Hotend Air Tunnel:**
   - Backfills Kirill's noisy interior shroud pockets/ledges (`Y = [-3.881, +26.50]`, `Z = [7.20, 32.58]`) cleanly while sparing all four `3010` fan screw bosses and outer front/rear/bottom walls.
   - Replaces `R2`–`R4`'s 6-vertex sharp polygonal `isRuled=True` duct loft with `build_smooth_duct_void()` — a **15-station uniform-arc-length periodic B-spline loft** (`Part.makeLoft(..., isRuled=False)`, verified clean under strict OCCT `BOPCheck`):
     - Blends smoothly from Kirill's circular `+X` `3010` fan inlet (`Y = [-3.10, +25.85]`, `Z = [7.75, 34.90]`, `R = 14.30 mm`) through a cosine-eased curved diffuser into a sleek rounded rectangular throat framing the shifted Bambu X1C heatsink fins (`Y = [-2.90, +24.80]`, `Z = [6.65, 25.15]`, `r = 2.00 mm` corners) and flares seamlessly out Kirill's `-X` hex exhaust grille (`X = -27.60 mm`, `r = 3.20 mm`).
   - STL exported at `LinearDeflection = 0.025`, `AngularDeflection = 0.12` so curved tunnel walls slice smoothly (`40,774` watertight manifold facets; STL vs STEP volume diff `0.064%`).
2. **Extended Perpendicular `+X` Extruder Mount Boss & Through-Bore (`+13.15, 12.08`):**
   - Right beside the `+X` `3010` hotend fan, `R4`'s `4.30 mm` blind bore met Kirill's sloped fan ceiling at an angle, leaving a tilted wedge on the underside.
   - `R5` adds a solid **`Ø9.00 mm` (`R = 4.50 mm`) vertical cylindrical boss** down to a crisp flat horizontal plane at **`Z = 27.60 mm`** (`4.98 mm` plate thickness below `plate_top = 32.58 mm`), clears a **`Ø12.40 mm` (`R = 6.20 mm`, confined `X <= 18.20 mm`)** circumferential wrench/nut clearance pocket strictly below `Z = 27.60 mm`, and extends the **`Ø3.60 mm` (`R = 1.80 mm`) M3 through-bore** all the way through `Z = 27.60 mm` so a standard M3 hex nut, M3 washer, or M3 flange locknut sits **100% flush and perpendicular** across all 360°.
   - Left Orbiter mount `(-23.85, 12.08)` remains a `Ø4.40 mm` × `4.30 mm` blind M3x4x5 heatset insert pocket (`6.78 mm` solid ceiling thickness above the smooth `-X` duct).
3. **Preserved `R4` & `R3` Geometry:**
   - **Plain `Ø44.00 mm` smooth circular motor cutout** centered at `(0.000, 51.900)` + clean `3.27 mm` recessed portal web (`Y = [-11.117, -7.850]`) framed by full-thickness vertical side pillars (`|X| >= 22.50 mm`) and EBB42 top bridge (`Z >= 67.00 mm`, `6.10 mm` minimum crown height, all `4/4` top EBB42 bores open).
   - **4/4 symmetric blind rear-entry AD5M carriage bores** (`(±19.0, 3.5)` and `(±24.0, 61.0)`, hidden from `+Y`).
   - **Offset hotend datum:** `X_mot = 0.000 mm`, `Z_mot = 51.900 mm`, `X_fil = -6.335 mm` (`-6.335 mm` nozzle shift toward `+X` Eddy probe / `-6.335 mm` in adapter `+X` coordinates), `Z_mount = 32.600 mm`.

## CAD Verification Summary (`validation.json`)

- **STEP (`BambuMod_Orbiter25_Primary_R5.step`):** Valid BRep (`step_valid = true`), `1` solid, volume **`38,064.63 mm³`**, upright bounds `[-29.998..30.000] × [-11.117..32.119] × [0.000..80.002] mm`.
- **STL (`BambuMod_Orbiter25_Primary_R5.stl`):** Watertight & winding-consistent (`is_solid = true`, `has_non_manifolds = false`, `trimesh: True True 1`), `40,774` facets, **`38,040.22 mm³`** (`0.064%` delta vs STEP), oriented flat-back on the print bed (`60.00 × 80.00 × 43.24 mm`).
- **Interference (`0.0 mm³` across all 9 checks):** `0.0 mm³` vs Orbiter v2.5 body/stepper/JST, Orbiter M3 bolts, Bambu X1C hotend, `3010` fan, EBB42 bracket, rear steel carriage plane, and lower/upper belts.
- **Bores & Walls:** `0.0 mm³` obstruction across all `4` `3010` fan bores, `4` EBB42 bores, `4` blind rear carriage bores (`hidden_from_front = true`), `6` duct X stations (`0.0`), `+X` nut boss underside (`0.0 mm³` obstruction, `1.0` annulus solid fraction), and `1.000` solid bottom/rear/front outer walls.

## Print & Assembly Notes

- **Orientation:** Already oriented flat rear-face down in `BambuMod_Orbiter25_Primary_R5.stl` (`Z = 0` build plate).
- **Material & Settings:** ABS, ASA, PC-CF, or PETG-CF (`>= 85 °C` HDT); `4` perimeters, `25–40%` gyroid/cubic infill; enable **Tree Supports (touching buildplate / on-bridge as needed)** for Kirill's overhanging front shroud deck, duct ceiling (`4,236.86 mm²` flat bridge area), and the `+X` nut boss seat (`Z = 27.60 mm` inside the `3010` bay — easily cleanable from the open `+X` fan opening before mounting the `3010` fan).
- **Hardware Checklist:**
  - **Carriage (`4×` blind rear M3):** Keep rear screw penetration **`< 5.3 mm`** (`low_R/low_L/up_L/up_R` depth `5.54 mm`).
  - **Orbiter v2.5 Left Mount `(-23.85, 12.08)`:** `1×` M3×4×5 mm brass heat-set insert + `1×` M3×8 or M3×10 SHCS (verify `orb_bolts` tip clears bottom of insert pocket).
  - **Orbiter v2.5 Right Mount by Fan `(+13.15, 12.08)`:** Pass **`1×` M3×12 mm** (standard hex nut) or **`1×` M3×14 mm** (nyloc/flange locknut) downward through the Orbiter ear (`~4.2 mm`) + plate boss (`4.98 mm`) and thread a standard **M3 nut** flush against the flat `Ø9.00 mm` underside boss inside the fan cavity BEFORE bolting the `3010` fan onto the `+X` shroud!
  - **Hotend (`X1C`), `3010` Fan, `EBB42`:** `2×` M3 heat-set inserts + `M3×14` front screws for X1C; `4×` M3 fan screws; `2×` M3 top screws for EBB42 bracket.

## Credits & Attribution

- **BambuMod AD5M Adapter Base:** Derived from [BambuMod for FF Adventurer 5M](https://www.printables.com/model/1574762-bambumod-for-ff-adventurer-5m) by **Kirill_Wawe** — **CC BY-NC-SA 4.0**.
- **Orbiter v2.5 Geometry Reference:** **dr. Lorincz Robert** ([orbiterprojects.com/orbiter-v2-5](https://www.orbiterprojects.com/orbiter-v2-5/)).
- This `R5` remix is shared under **CC BY-NC-SA 4.0**.
