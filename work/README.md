# work/ — historical scratch scripts and intermediate studies

Everything in this folder is **history**. It was produced on the Windows workstation in early November 2026, while the EBB36/EBB42 brackets, Eddy mounts, wiring diagrams and handoff packages were being developed.

- **Do not run these scripts from the cloud.** Most of them hard-code Windows paths (`C:\Users\PK800\...`, `C:\Program Files\FreeCAD 1.1\...`). A few locate the repository with `Path(__file__).resolve().parents[...]`, which is why the folder stays at `work/` rather than moving under `docs/history/`.
- **The current, portable builders and renderers are in [`scripts/cad/`](../scripts/cad/).** Seven files share a name with a `scripts/cad/` copy (`build_uniform_posts_R7.py`, `build_simple_wedge_R6.py`, `build_eddy_adjustable_R4.py` and their renderers, plus `render_mockup.py`). The `scripts/cad/` versions are the ones to use.
- **The outputs these scripts made** are in `outputs/` and `docs/history/AD5M_HANDOFF_2026-11-02/`. Some images here (`BOOT0_reference_zoom.png`, `VBUS_reference_zoom.png`, `bed_probe_compare/m8p-accessory-pinouts.jpg`) are byte-identical copies of files in that handoff package.

| What | Files |
| --- | --- |
| EBB42 bracket builders and checks (R1–R7 era) | `build_open_EBB42_bracket.py`, `build_sketch_bridge.py`, `build_support_free_bridge.py`, `build_rounded_bridge.py`, `build_simple_wedge_R6.py`, `build_uniform_posts_R7.py`, `check_*.py`, `fillet_*.py`, `finish_rounding.py` |
| Eddy Duo mount builders and studies | `build_eddy_mount_R1.py`, `build_eddy_adjustable_R3.py`, `build_eddy_adjustable_R4.py`, `inspect_eddy_shape.py`, `check_eddy_direct_anchors.py`, `render_eddy_*.py` |
| Wiring diagrams and handoff tooling (Node.js) | `annotate_*.cjs`, `add_*.cjs`, `consolidate_handoff.cjs`, `verify_handoff.cjs`, `generate_trident_bom_reference.cjs` |
| EBB36 wiring guide (superseded by EBB42) | `ebb36_wiring_guide_R1/` (writes into `outputs/EBB36_wiring_guide_R1/`) |
| Probe comparison images | `bed_probe_compare/` |
| Intermediate geometry and caches | `*.json`, `*.npy`, `rounded_*.step` |
