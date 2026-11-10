# AD5M Build working instructions

Read README.md and CURRENT_TOOLHEAD_SPEC.md before changing designs. This project prioritizes customization and reuse of the existing AD5M feeder/motor and Bambu X1C hotend. EBB42 V1.2.1 is confirmed; do not revert to EBB36 or Gen2. Eddy Duo uses USB for now.

## Current designs and physical feedback
- EBB42 two-post bracket: outputs/EBB42_uniform_posts_R7/. Uniform 6.6 mm angled posts, rounded edges, 2.5 mm M3 pilots. Prior R5 was printed and the user called it usable; R7 has not been confirmed printed.
- EBB42 simple wedge alternative: outputs/EBB42_simple_wedge_R6/. One central triangular wedge on a rectangular plate, 2.5 mm M3 pilots normal to face. User said this was printing; physical installation unconfirmed. Requires PCB-back spacers.
- Eddy side mount: outputs/Eddy_Duo_adjustable_side_mount_R4/. Reinforced 1.6 mm side walls / 1.7 mm end walls around M3 nut channels; 10 mm height slots; sensor hole pitch 10.5 mm. Earlier R3 was being printed for fit inspection. R4 not physically tested.
- Current BambuMod structural housing: reference/BambuMod/. Preserve originals and source attribution.

Keep old revisions. Do not call a CAD or mesh check a physical fit test. Full motor/stock bearing carriage/frame motion geometry is absent. Do not infer the actual nozzle height from the housing bounding box. Eddy sensing bottom target is approximately 2.5 mm above the physical nozzle tip, adjustable on the printer. Earlier left-Eddy-hole direct mount placement overlapped vent openings; current proposal uses two new solid-edge anchors, source CAD X30 Y-6 Z64/84.

User expects simple geometry faithful to sketches, rounded external edges, sharp hole rims allowed, and support-free printing. Avoid adding structures beyond the requested change. Mount positions and board orientation must not silently change. Typical M3 plastic-threading pilots are modeled at 2.5 mm; clearances are 3.3 mm. Check actual print and material before promising screw grip.

## Files, tools and checks
scripts/cad/ contains portable copies of the current three builders and renderers. Historical work/ scripts retain Windows/Desktop paths; do not treat those as cloud paths. CAD builders need native FreeCAD Python modules FreeCAD, Part and MeshPart, not the unrelated PyPI package named freecad. Rendering/check packages are listed in requirements-cloud.txt. Have cloud setup install a compatible native FreeCAD runtime and test its imports before claiming CAD generation works. On the Windows workstation, FreeCAD 1.1 Python is located at `C:\Program Files\FreeCAD 1.1\bin\python.exe` and system Python is at `C:\Python314\python.exe`.

After geometry changes validate one valid CAD solid, a watertight consistently wound single STL body, unchanged datums where required, and actual relevant CAD clearances. Investigate reference-fastener overlaps separately from electronics collisions. Inspect a CAD preview. Run checks proportional to the change. Keep hardware source attribution/license files; mixed third-party content has no blanket project-wide license.

Large upstream checkouts and duplicate ZIP archives remain local and are ignored. Their sources/provenance are retained in reference/. Do not delete local data to reduce repository size. Avoid committing credentials, .env files or machine flash-readback backups.

## Multi-agent coordination and Git sync
This repository is accessed by multiple agent harnesses (including ChatGPT / Codex Cloud and local Antigravity). Follow these rules so concurrent or alternating agents do not overwrite work or read stale state:
1. **Sync before reading or writing:** Always run `git fetch` and `git pull --rebase` at the start of a task before inspecting state or editing files, and push completed atomic commits promptly.
2. **Authoritative state order:** Treat `AGENTS.md` and `CURRENT_TOOLHEAD_SPEC.md` as the authoritative current specification. Older handoff files (`START_HERE_AD5M.txt`, `AD5M_REBUILD_HANDOFF.txt`, `AD5M_HANDOFF_2026-11-02/`, `BUILD_SEQUENCE.md`, `TOOLHEAD_FIRST.md`, `UPGRADE_ROADMAP.md`, `BTT_CONTROLLER_OPTIONS_2026-11-02.md`) contain historical EBB36 and pre-flashing records; check their top banners and do not revert confirmed hardware (Octopus Pro V1.1 H723 flashed with Klipper USB-to-CAN bridge, EBB42 V1.2.1, Bambu X1C hotend in BambuMod housing, Eddy Duo over USB).
3. **Append-only CAD revisions:** Never overwrite an existing `outputs/<part>_R<n>/` folder when changing geometry. Create a new revision directory `outputs/<part>_R<n+1>/` and a portable builder/renderer in `scripts/cad/` using `Path(__file__).resolve().parents[2]` so historical revisions remain intact and binary `.stl`/`.FCStd`/`.png` merge conflicts are avoided.
4. **Update indices together:** When adding a new output revision or recording user physical fit feedback, update `CURRENT_TOOLHEAD_SPEC.md`, `README.md`, `outputs/INDEX.md`, and `AGENTS.md` in the same commit.
