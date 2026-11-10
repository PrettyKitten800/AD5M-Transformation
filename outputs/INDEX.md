# Outputs Directory Index

This index separates **active printable designs** and **active technical records** from **superseded historical revisions** preserved in `outputs/`.

> **Rule for agents:** Never overwrite an existing revision folder when modifying geometry. Always create a new `outputs/<part>_R<n+1>/` directory and update this index, [README.md](../README.md), [CURRENT_TOOLHEAD_SPEC.md](../CURRENT_TOOLHEAD_SPEC.md), and [AGENTS.md](../AGENTS.md).

## 1. Active Printable Toolhead Designs

| Component | Directory | Builder / Renderer | Physical Status |
| --- | --- | --- | --- |
| **EBB42 two-post bracket (uniform 6.6 mm angled posts)** | [`EBB42_uniform_posts_R7/`](EBB42_uniform_posts_R7/) | [`build_uniform_posts_R7.py`](../scripts/cad/build_uniform_posts_R7.py) / [`render_uniform_posts_R7.py`](../scripts/cad/render_uniform_posts_R7.py) | Revised from R5 (which printed and fit-checked as usable); R7 not yet confirmed printed |
| **EBB42 simple central wedge mount** | [`EBB42_simple_wedge_R6/`](EBB42_simple_wedge_R6/) | [`build_simple_wedge_R6.py`](../scripts/cad/build_simple_wedge_R6.py) / [`render_simple_wedge.py`](../scripts/cad/render_simple_wedge.py) | User reported printing; requires ~4 mm M3 spacers behind PCB; physical installation unconfirmed |
| **Eddy Duo reinforced adjustable side mount** | [`Eddy_Duo_adjustable_side_mount_R4/`](Eddy_Duo_adjustable_side_mount_R4/) | [`build_eddy_adjustable_R4.py`](../scripts/cad/build_eddy_adjustable_R4.py) / [`render_eddy_adjustable_R4.py`](../scripts/cad/render_eddy_adjustable_R4.py) | Widened M3 nut-channel walls (1.6 mm side / 1.7 mm end); 10 mm vertical travel; requires two drilled holes in solid housing edge; untested physically |

## 2. Active Reference, Wiring & Commissioning Records

| Directory | Contents |
| --- | --- |
| [`flashing_2026-11-03/`](flashing_2026-11-03/) | Confirmed Octopus Pro V1.1 (STM32H723ZET6) DFU flash verification, Klipper USB-to-CAN bridge build record, and Windows USB enumeration |
| [`AD5M_HE0_wiring_R5/`](AD5M_HE0_wiring_R5/) | Current Octopus Pro + external ReliaBot MOSFET power/control wiring plan using `HE0` (`PA0`) |
| [`bambumod_inspection/`](bambumod_inspection/) | CAD solid validation and bounding-box inspection of the installed BambuMod housing |
| [`Custom_toolhead_reference_R1/`](Custom_toolhead_reference_R1/) | Nominal Bambu X1C nozzle tip (`Z=0`) to Eddy Duo sensing bottom (`Z=2.5 mm`) alignment reference (`Nozzle_Eddy_nominal_alignment.FCStd`) |
| [`ebb42_mockup/`](ebb42_mockup/) | EBB42 V1.1 STEP reference (`EBB42_CAN_V1.1_reference.step`) and pre-tessellated `board.json` / `housing.json` used by `scripts/cad/` |
| [`eddy_reference/`](eddy_reference/) | Reference mesh and dimensions for Eddy Duo |
| [`extruder_review_2026-11-06/`](extruder_review_2026-11-06/) | Extruder evaluation notes (baseline remains stock AD5M feeder + motor) |

## 3. Superseded / Historical Revisions (Retained for Provenance)

- **Superseded EBB42 brackets:**
  - [`EBB42_open_tophat_bracket_R1/`](EBB42_open_tophat_bracket_R1/) — Placed board outside rear face (superseded).
  - [`EBB42_rear_corridor_study_R2/`](EBB42_rear_corridor_study_R2/) — Near-upright corridor study (+26 mm height).
  - [`EBB42_sketch_bridge_R3/`](EBB42_sketch_bridge_R3/) — First 4-hole bridge with strain-relief clip holes.
  - [`EBB42_sketch_bridge_R4/`](EBB42_sketch_bridge_R4/) — Support-free bridge without clip holes, unradiused.
  - [`EBB42_sketch_bridge_R5/`](EBB42_sketch_bridge_R5/) — Radiused two-post bracket (printed and fit-checked by user; superseded by uniform-post `R7`).
- **Superseded Eddy Duo mounts:**
  - [`Eddy_Duo_BambuMod_mount_R1/`](Eddy_Duo_BambuMod_mount_R1/) — Early sidewall drill pattern.
  - [`Eddy_Duo_BambuMod_mount_R2/`](Eddy_Duo_BambuMod_mount_R2/) — Direct carriage hole concept over honeycomb region.
  - [`Eddy_Duo_adjustable_side_mount_R3/`](Eddy_Duo_adjustable_side_mount_R3/) — Adjustable side mount prior to nut-channel wall reinforcement (`R4`).
- **Superseded EBB36 & earlier diagram iterations:**
  - [`EBB36_wiring_guide_R1/`](EBB36_wiring_guide_R1/) (and `../output/pdf/EBB36_toolhead_wiring_R1.pdf`) — Historical EBB36 wiring guide; **not** an approved EBB42 V1.2.1 wiring plan.
  - [`AD5M_board_diagrams_R4/`](AD5M_board_diagrams_R4/), [`AD5M_PSU_annotated/`](AD5M_PSU_annotated/), [`AD5M_PSU_annotated_R2/`](AD5M_PSU_annotated_R2/), [`Octopus_AD5M_labels/`](Octopus_AD5M_labels/), [`Octopus_AD5M_labels_R2/`](Octopus_AD5M_labels_R2/), [`Octopus_AD5M_labels_R3/`](Octopus_AD5M_labels_R3/).
