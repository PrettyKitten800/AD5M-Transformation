# EBB42 board reference and mock-ups

**Status: reference data (still used by the renderers).**

- `EBB42_CAN_V1.1_reference.step`: BigTreeTech's official EBB42 CAN V1.1 CAD, from the URL in `SOURCE.txt`. It is used as the board envelope. The installed board is **V1.2.1**; connector-level details may differ from this V1.1 model.
- `board.json`: pre-tessellated board mesh read by `scripts/cad/render_uniform_posts_R7.py`. `housing.json`: housing mesh read by `scripts/cad/render_mockup.py`. Keep both; the renderers use them to draw previews without FreeCAD.
- `placement.json`, `placement_02.json`, `EBB42_close_mount_mockup_0*.png`, `mockup_views*.png`, `housing_views.png`: early close-mount placement studies (November 2026), superseded by the bracket revisions listed in `outputs/INDEX.md`.
