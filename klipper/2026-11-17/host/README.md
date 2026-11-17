# Host configuration addendum — 2026-11-17

These are read-only copies of the installed Moonraker, CAN and USB camera configuration, added at the user's request. The original Klipper/calibration snapshot is unchanged. No services were restarted and no printer commands were sent.

| Archived file | Installed destination |
| --- | --- |
| `../config/moonraker.conf` | `/home/curby/printer_data/config/moonraker.conf` |
| `systemd/moonraker.service` | `/etc/systemd/system/moonraker.service` |
| `systemd/can0.service` | `/etc/systemd/system/can0.service` |
| `systemd/ad5m-camera.service` | `/etc/systemd/system/ad5m-camera.service` |
| `moonraker.env.example` | `/home/curby/printer_data/systemd/moonraker.env` |
| `nginx/mainsail` | `/etc/nginx/sites-available/mainsail` |
| `nginx/fluidd` | `/etc/nginx/sites-available/fluidd` |

The three units have no systemd drop-ins. Both nginx sites are enabled by same-named symlinks in `/etc/nginx/sites-enabled/`. Their shared nginx configuration and packaged executables remain host prerequisites; this is a configuration backup, not an operating-system image.

Moonraker launches from `/home/curby/moonraker-env` with the non-secret environment values copied exactly in `moonraker.env.example`. Its API binds to loopback port 7125 and both frontend sites proxy it. The CAN unit brings `can0` up at 1,000,000 bit/s with a transmit queue of 128. The camera uses `ustreamer`, its stable `/dev/v4l/by-id/` path, loopback port 8081 and 1920×1080 MJPEG at a desired 30 fps. Both frontends expose it through `/webcam/` (Mainsail port 80, Fluidd port 8080).

For a restore, back up destination files, install the required software/users/groups, review machine paths and LAN rules, then place each file at the destination above. The `.example` suffix is only an archive convention: copy it to the original `moonraker.env` path. Preserve nginx enablement symlinks. Validate nginx configuration and reload systemd only during a planned idle maintenance window. Account credentials and Moonraker databases are intentionally absent; restore account state separately or recreate it.
