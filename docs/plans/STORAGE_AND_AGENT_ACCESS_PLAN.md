# Storage and Agent Access Plan

Drafted 2026-11-20. Status: **proposal, nothing installed yet.** Decisions marked **Decide** need the owner's answer before that phase starts.

## Goal

One storage layer that every assistant can use: Claude Code (cloud and local), Codex, Antigravity, NotebookLM, and later OpenClaw or local models. It has to outlive any single tool, keep private material private, and keep working when the internet or a provider is down.

## Principles

1. **Files are the source of truth.** Markdown, `.cfg`, scripts and CAD files in git. Databases, vector stores and chat histories are caches that can be rebuilt.
2. **One home per kind of data.** Each kind of file has exactly one primary location (table below); everything else is a copy or a link.
3. **Harnesses read conventions, not private state.** Every tool starts from `AGENTS.md` and the current-state files. Anything an agent learns that matters goes into a repo file (spec, log, plan) before the session ends, never only into that tool's memory.
4. **3-2-1 backups.** Three copies, two kinds of storage, one off-site.
5. **Public and private stay separate by design.** The GitHub repo is public; private material never depends on remembering to leave it out.

## Where things live today

| Place | Holds | Limits |
| --- | --- | --- |
| GitHub `AD5M-Transformation` (public) | Specs, logs, plans, sanitized printer snapshots, CAD revisions, scripts | Public; 366 MB packed and growing with CAD binaries |
| Google Drive `3D Printing/` (private) | NotebookLM sources, printables, large upstream CAD, private archives, photos | No version history worth relying on; cloud-only |
| Windows workstation | FreeCAD 1.1, local repo clone, Desktop originals | Not reachable from cloud sessions |
| CurbyServer (Intel Linux, printer host) | Live Kalico config in `printer_data/config`, Moonraker, camera | Not versioned; single disk; also runs the printer |
| Retired Raspberry Pi 5 | Nothing assigned | Could become a backup or service node |

## Target layout

| Kind of data | Primary home | Copies |
| --- | --- | --- |
| Specs, plans, build log text, agent rules (`AGENTS.md`) | GitHub `main` | Every clone; NotebookLM copy in Drive |
| Live printer config | CurbyServer `printer_data/config`, auto-committed to a **private** repo | Sanitized snapshots in the public repo (`klipper/<date>/`) |
| Private archives (Moonraker DB, unredacted configs, firmware images) | Private repo or backup store at home | Drive `Backups (PRIVATE)` as the off-site copy |
| CAD sources and outputs | Git (as now) | See Phase 4 for the large-file decision |
| Large upstream downloads (vendor STEP, manuals) | Drive `CAD references` / `NotebookLM sources` | `SOURCE.md` with link and license in `reference/` |
| Photos and camera snapshots | Drive `Photos` | Backup store |
| Personal-assistant notes (not this printer) | Separate private markdown repo | Backup store |

## Phases

### Phase 0: done (2026-11-20)
Repo and Drive reorganized, `CURRENT_TOOLHEAD_SPEC.md` made the single installed-state record, snapshot and file-size rules added to `AGENTS.md`, Drive docs updated in place.

### Phase 1: local harnesses where the hardware is
- Install Claude Code (or keep using Codex/Antigravity) on the **workstation** for CAD work and on **CurbyServer** for printer config, camera snapshots and measurements.
- Clone the repo on CurbyServer, separate from `printer_data/config`.
- **Exit:** a local session on each machine reads `AGENTS.md`, finds the current spec, and can push a commit.

### Phase 2: automatic printer-config history
- A systemd timer on CurbyServer commits `printer_data/config` to a **private** git repo whenever it changes (existing community tools such as Klipper-Backup do this; check its current state before adopting it).
- A small script produces the sanitized public snapshot: active include closure only, `/home/<user>` paths, manifest hashes (AGENTS.md rule 5).
- Run commits only when the printer is idle so the host never stalls Kalico mid-print.
- **Decide:** where the private repo lives. Options: Forgejo (self-hosted, light) on the retired Pi 5 or on CurbyServer; or a private GitHub repo.
- **Exit:** a config edit in Mainsail shows up as a private commit within minutes; a sanitized snapshot is one command.

### Phase 3: backups
- restic (or borg) on the home node, backing up the private repo, `printer_data` (including the Moonraker database), photos and personal notes.
- Targets: a local USB disk plus one off-site target.
- **Decide:** off-site target. Options: Google Drive through rclone (already paid for) or Backblaze B2 (cheap, built for this).
- **Exit:** a test restore of last week's printer config succeeds; restore tested again every three months.

### Phase 4: large-file strategy
The repo grows by about 150 MB per big CAD session. Before choosing, test what each harness can actually fetch:
- **Git LFS:** simplest; GitHub hosts it. Check that cloud harness clones download LFS files instead of pointer stubs, because the CAD scripts read STEP files directly.
- **git-annex:** most flexible (contents on the home node, Drive and a USB disk at once), but cloud agents cannot fetch contents stored at home.
- **Keep as now:** binaries in git, with large vendor files in Drive plus a manifest.
- Existing history stays as is; any change applies to new files only. Rewriting history in a repo several agents use is not worth it.
- **Exit:** a written decision in this file and a matching rule in `AGENTS.md`.

### Phase 5: shared access layer for any harness
- **Tailscale** (or WireGuard) so your own devices reach home services from anywhere without opening ports.
- **MCP servers** on the home node: filesystem (scoped to the project and notes folders) and git, plus small tools for printer status and camera snapshots. Every harness that speaks MCP then sees the same files and tools.
- Cloud agents get **no** home access by default. Exposing anything to them is a separate decision, read-only first.
- Connect OpenClaw or other harnesses here, to the same `AGENTS.md` and MCP servers; being provider-agnostic then mostly means pointing a new tool at existing endpoints.
- **Exit:** two different harnesses (for example Claude Code and one other) complete the same small task using only the shared files and MCP tools.

### Phase 6: personal knowledge base
- A separate private markdown repo for notes beyond this printer, with the same conventions (an `AGENTS.md`, a current-state file, a dated log).
- Optional: a markdown-based memory tool that exposes notes over MCP, chosen for keeping data in plain files.

## Rules that prevent the usual failures

- **Never sync a git working tree with Syncthing or Drive sync.** Sync tools and git fight over the same files. Git repos move through git; Syncthing is for folders that are not repos (photos, exports).
- **Secrets never enter a public repo, even temporarily.** Sanitize before commit, not after.
- **Heavy jobs wait for an idle printer.** Backups, indexing and sync on CurbyServer run when no print is active.
- **A harness-specific feature is fine, a harness-specific record is not.** If something only exists in one tool's memory or chat history, it is not saved yet.

## Open decisions

1. Home node for services: retired **Pi 5** (keeps CurbyServer dedicated to the printer) or **CurbyServer** (one less box).
2. Private repo host: self-hosted Forgejo or a private GitHub repo.
3. Off-site backup target: Google Drive through rclone, or Backblaze B2.
4. Whether this project's repo stays public.
5. Whether cloud agents should ever reach home services, and with what limits.
