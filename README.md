# AD5M-Transformation

Mods to turn a FlashForge AD5M into a frankenstein'd Trident-like AWD printer.

This repository is the shared file workspace for the AD5M Build project: build notes, hardware references, printable toolhead brackets and CAD scripts. The current goal is customizable tooling using the existing AD5M feeder/motor, Bambu X1C hotend, EBB42 V1.2.1 and Eddy Duo. Gantry/rail changes and a future tool changer are longer-term work.

## Current printable designs

| Part | Files | Status |
| --- | --- | --- |
| EBB42 bracket with uniform angled posts | [R7](outputs/EBB42_uniform_posts_R7/) | Revised after R5 printed successfully enough for a fit check; R7 untested physically |
| Simple central wedge EBB42 mount | [R6](outputs/EBB42_simple_wedge_R6/) | User reported printing; requires PCB-back spacers |
| Reinforced adjustable Eddy Duo mount | [R4](outputs/Eddy_Duo_adjustable_side_mount_R4/) | Proposal with thicker nut-channel walls; 10 mm vertical travel; two new housing holes |

Read each part's PRINT_AND_FIT.md or PRINT_AND_INSTALL.md. Older output revisions are retained as history, including superseded placements. CAD checks do not establish installed frame, motor, nozzle or cable clearance.

## Build records

- [Current specification](CURRENT_TOOLHEAD_SPEC.md)
- [Build sequence](BUILD_SEQUENCE.md)
- [Toolhead-first plan](TOOLHEAD_FIRST.md)
- [Upgrade roadmap](UPGRADE_ROADMAP.md)
- [Working instructions and physical test status](AGENTS.md)
- [Cloud setup and remaining connection steps](CLOUD_SETUP.md)

## CAD and references

- [Portable current CAD builders/renderers](scripts/cad/)
- [Original user-supplied BambuMod housing](reference/BambuMod/)
- [X1 hotend reference](reference/Bambu_X1_hotend_CAD/)
- Historical scripts and intermediate studies: work/ and outputs/.

Native FreeCAD Python bindings are required for builders. NumPy, Pillow, trimesh and Shapely support rendering and checks. Python package dependencies are in requirements-cloud.txt. Windows-only historical scripts are preserved; prefer scripts/cad/ in the cloud.

Large downloaded upstream archives/checkouts and machine-specific flash backups are excluded from Git. Source metadata and download links remain under reference/. No local files were deleted. This is a curated source workspace, not an automatic backup of the entire Windows Desktop.

## Attribution

This repository contains mixed original and third-party content. Preserve each source's license and attribution. BambuMod-derived brackets retain the stated CC BY-NC-SA 4.0 attribution in their installation notes. The Jorge hotend is an unchanged reference with its own source/license. Do not apply a blanket license to upstream material.
