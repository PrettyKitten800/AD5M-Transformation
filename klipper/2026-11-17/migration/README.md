# AD5M Pi 5 → Intel Linux host migration — 2026-11-17

This handoff supplements the complete configuration snapshot one directory above. It captures the working Pi setup without sending printer commands, changing its settings, or restarting services. Intel hardware has not been configured or tested. The separate private Drive archive contains the database, original config tree, G-code library, source archives, installed frontend assets and optional existing firmware recovery images.

## What is already preserved

- All active Klipper configs, calibration/SAVE_CONFIG data, mesh backups, slicer presets and the two custom Python extras.
- Klipper, Moonraker, CAN and camera systemd units; Moonraker launch settings; both nginx sites and the shared nginx config as reference.
- Installed software commits, Python/package inventories, frontend configuration, KlipperScreen settings and a reference Moonraker PolicyKit rule.
- Private archive: a consistent SQLite database backup, the entire original config/G-code trees, non-secret service launch files, exact tracked Klipper/Moonraker/Katapult/mainsail-config/KlipperScreen source snapshots, frontend web assets and existing EBB42/Eddy-CAN recovery images. No firmware is read from hardware during packaging.

## 1. Prepare the Intel PC

Use a supported 64-bit Linux distribution. The source is Debian 13 on ARM64 with Python 3.13.5; see `host-inventory.json` and the dependency inventories for the captured versions. Create a printer service account. Keeping username `curby` and `/home/curby` avoids rewriting the archived paths; otherwise update every absolute path in Klipper, Moonraker, service units, launch settings, frontend update-manager paths and symlinks.

Install native x86_64 prerequisites for Python virtual environments/building C extensions, git, nginx, iproute2/SocketCAN, ustreamer, V4L2 tools and Moonraker's D-Bus/PolicyKit requirements. `pi-package-versions.tsv` is an inventory, not an apt command: ARM-specific packages/version strings must not be installed blindly on Intel. The frozen pip files record the working versions; install upstream requirements for the pinned source first, using the inventories to resolve differences. ARM Python virtual environments, native binaries and generated Klipper C helper libraries must be rebuilt, not copied.

Disable automatic suspend/hibernate during printer operation. If the PC is also a desktop, avoid workloads that starve Klipper of CPU or memory. USB autosuspend behavior must be tested on the target rather than copying Pi boot/kernel settings. Do not migrate this Pi's unrelated DNS/Pi-hole, VPN identity, Wi-Fi credentials or desktop services as part of the printer port.

## 2. Install the matching software

`host-inventory.json` records exact commits. Start with Klipper `0cee841e31d701595b3e509a0b502f6e320f52a8`, Moonraker `b559b9a81161f958a43c2f527b6ad96f73310d5d`, Katapult `3b973a485388b4ef0f9efef46f78152e302aea8e`, and the recorded mainsail-config version. Clone the upstream repositories and check out these commits so future updates work normally. The private `sources/*.tar.gz` files are an offline source fallback; they do not contain Git history/remotes. Preserve their included licenses.

Build fresh native Python environments named `klippy-env` and `moonraker-env`. Install the pinned source's prerequisites; do not run an old Pi installer without reviewing its distro/Python assumptions. Install both archived custom extras into `klipper/klippy/extras/`; `[z_speed_control]` requires `z_speed_control.py`. `two_stage_probe.py` remains an inactive historical helper. No other tracked local Klipper patches were found.

Restore the snapshot's active config set and relative includes. `config/mainsail.cfg` is materialized, so the archive works without the original symlink. The private original config tree retains backup files; only the manifest's ten active config files belong to the current include closure. Retain the existing printer calibration. There is no active Pi GPIO/Linux-MCU dependency in this configuration.

## 3. Restore Moonraker state privately

Install Moonraker first, then stop Moonraker **on the Intel target** before restoring `printer_data/database/moonraker-sql.db`. The private copy was generated with SQLite's consistent backup API and passed `PRAGMA quick_check`. This is SQLite, not the architecture-dependent old LMDB format. Restore the database with target-account ownership and private permissions. It preserves accounts, API identity, camera definitions, frontend preferences and history; treat it as sensitive and keep it out of GitHub. If opting for a fresh database, recreate accounts, webcam entries and frontend settings instead.

Copy G-code files into the target's `printer_data/gcodes`; make the log, comms, database and systemd directories owned by the service user. Recreate Unix sockets/PID files at runtime; never restore live sockets from the Pi. Copy `host/moonraker.env.example` to its original `printer_data/systemd/moonraker.env` destination. `moonraker.asvc` is a service allowlist, not proof that each listed optional service is installed.

Install the archived systemd units after adapting paths. The Moonraker unit requires the `moonraker-admin` group; camera access requires `video`. Use the pinned Moonraker `scripts/set-policykit-rules.sh` to generate rules for the **target** account/group. The captured `host/polkit/moonraker.rules.reference` contains Pi GID **1002** and is provenance only; copying it to a host with a different group ID will break authorization. Apply the installer-required permissions for service control/package management. Reload systemd and verify service dependencies during target setup.

## 4. Restore web interfaces and camera

Install Mainsail/Fluidd from the archived assets (or matching releases) into `/var/www/mainsail` and `/var/www/fluidd`. Enable both archived nginx sites using same-named symlinks in `/etc/nginx/sites-enabled`. Avoid competing default sites. Use the target distro's packaged nginx defaults, consulting `host/nginx/nginx.conf.reference`; validate `nginx -t` before reload. Mainsail uses port 80 and Fluidd 8080; Moonraker 7125 and camera 8081 bind to loopback behind nginx.

Install native ustreamer and connect the same USB camera. Verify its `/dev/v4l/by-id/` path and supported MJPEG mode before enabling the camera unit. The captured command requests 1920×1080 at 30 fps with `--format=MJPEG --encoder=HW`; here HW means using camera-provided JPEG frames, not a Pi-specific GPU requirement. The `/webcam/` proxy exists in both sites; saved webcam definitions are in the private Moonraker database. Check both the live stream and snapshot endpoint on the target.

KlipperScreen is optional. Its config and exact source snapshot are included, but the Pi ran it as a desktop app with no standalone service/autostart. Reinstall its native dependencies and set up the desired Intel display/touch/autostart separately.

## 5. Network and CAN cutover

Choose the target hostname/IP and update Moonraker CORS/LAN rules, slicer upload address and any remote access configuration. Do not duplicate the Pi hostname/IP while both machines are on the LAN. Certificate/secrets files are included privately only if present; none were present at capture. Reauthorize external clients if choosing fresh account/API state.

Keep the existing MCU firmware for the initial host move. The Octopus Pro is the USB-to-CAN bridge; EBB42 and Eddy Duo are CAN nodes. Existing UUIDs are in the config and remain tied to the controller hardware. The captured CAN service configures `can0` at 1,000,000 bit/s and txqueuelen 128; the bridge firmware determines its actual bus timing. Configure Linux SocketCAN and ensure CAN is ready before Klipper connects.

The systemd CAN unit is bound/enabled to the can0 device. Test both cold boot and unplug/replug/controller restart recovery on Intel; bridge resets remove/recreate the interface. Choose one CAN manager (the archived service or target-supported networking setup), not overlapping configurations. Confirm the adapter still gets the expected name. A CAN query only lists uninitialized nodes; an empty query while Klipper owns them does not mean they are missing.

During cutover, stop Klipper on the Pi, then move the Octopus USB and camera USB connections to Intel. Only one host should control the printer. No reflash is planned. Optional EBB42/Eddy recovery files in the private archive are for recovery only. An authoritative installed Octopus Pro build .config/image was not found on the Pi, so this archive does **not** claim complete Octopus firmware disaster recovery. Build-smoke/test configs are not substitutes for installed firmware.

## 6. Validate before retiring the Pi

With the user present and plate clear: verify MCU connectivity and versions, idle temperatures, fans/camera, endstop state, and the corrected Z → rear Y → right X homing. Preserve Y12..220, X−10..213.4, 0.4 mm nozzle, Eddy X+35/Y0 and purge at Y15. Confirm the front cooler and Eddy clear the frame. Then verify Eddy operation, bed mesh and a supervised small first layer using the saved ASA-GF test parameters. Test RESTART/FIRMWARE_RESTART and a host reboot while idle. Inspect CAN retransmits/errors and Moonraker warnings. Retain the Pi unchanged as rollback until these checks pass.

## Capture limits and references

The printer was not commanded or reflashed; no services were stopped or restarted. `can0` was absent during inventory, so live CAN recovery was not tested. Source checkouts had no tracked edits; the two untracked Klipper extras were separately preserved. Logs, caches, sockets, ARM venvs, unrelated host services and OS/SSH/VPN credentials are intentionally outside this handoff. Python wheels/system packages may still require internet or target-specific resolution; this is not a fully offline Intel OS installer.

- [Klipper x86 host guidance](https://www.klipper3d.org/FAQ.html#can-i-run-klipper-on-something-other-than-a-raspberry-pi-3)
- [Klipper CAN bridge configuration and reset behavior](https://www.klipper3d.org/CANBUS.html#usb-to-can-bus-bridge-mode)
- [Moonraker installation, permissions and database restore](https://moonraker.readthedocs.io/en/latest/installation/)
