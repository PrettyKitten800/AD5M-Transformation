# Voron Beefy Front Idlers (BFI) Reference

Retrieved November 24, 2026 from `https://github.com/clee/VoronBFI` for the AD5M `3× MGN12H` linear-rail gantry redesign (`AD5M_MGN12_Gantry_R1`).

- Upstream source is extracted under `source/VoronBFI-main/` (ignored in git; see `SOURCE.json`).
- Key design principles adapted to the AD5M front corners:
  - **Compression-loaded idler carrier:** the tension bolt pulls the carrier forward in compression against the outer tension wall so belt pull compresses printed layers rather than splitting them.
  - **Hardened Ø5 mm dowel pin + F695-2RS stack:** double-shear `Ø5 mm` pin with `M5 × 1 mm` precision shims eliminating screw-thread play and bearing rub.
  - **Enclosure-compatible access:** oriented for the AD5M front door opening so corner trim never blocks belt tensioning.
