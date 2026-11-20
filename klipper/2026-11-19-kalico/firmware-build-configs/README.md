# Kalico + eddy-ng Firmware Provenance (2026-11-19)

This directory documents the exact upstream commits, MCU targets, symlinks, and compiled binary checksums running on the CurbyServer (`http://192.168.4.31`) printer host after migrating from mainline Klipper (`0cee841e3`) to **Kalico + eddy-ng**.

Raw `.bin` firmware images are excluded from Git and archived locally in `/home/<user>/kalico/out-builds/` as well as in the private Google Drive disaster-recovery archive (`Moron_Tridont_Kalico_PRIVATE_2026-11-19.zip`).

## Upstream Repositories & Host Integration

- **Kalico:** `https://github.com/KalicoCrew/kalico.git`
  - Local path: `/home/<user>/kalico`
  - Branch: `bleeding-edge-v2`
  - Commit: `fb4e09bc750b5a638ea873cb5211f95bd92efdac` (`v2026.11.00-73-gfb4e09bc`)
  - Python virtual environment: `/home/<user>/kalico-env` (`Python 3.13.5`)
- **eddy-ng:** `https://github.com/vvuk/eddy-ng.git`
  - Local path: `/home/<user>/eddy-ng`
  - Branch: `main`
  - Commit: `a09ec8e31b22b80ad31d634a0549a479402be42c` (`v0.1-188-ga09ec8e`)
  - Integrated into Kalico via symlinks:
    - `/home/<user>/kalico/klippy/plugins/probe_eddy_ng` -> `/home/<user>/eddy-ng/probe_eddy_ng`
    - `/home/<user>/kalico/src/extras/eddy-ng` -> `/home/<user>/eddy-ng/eddy-ng`

## Flashed MCUs & Binary Checksums

All three MCUs report `Kalico v2026.11.00-73-gfb4e09bc` in `klippy.log`:

| MCU (`printer.cfg` / `eddy-duo.cfg`) | Board | MCU Target / Clock | Interface & Bootloader Offset | CAN Bus UUID | Binary (`out-builds/`) | Size (bytes) | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mcu` | BTT Octopus Pro V1.1 H723 | `stm32h723xx` (`520 MHz`, `CANBUS_BRIDGE=1`) | USB-to-CAN bridge (`can0`, `1 Mbps`), `0x8020000` | `c16b9f102b59` | `kalico-octopus.bin` | `45564` | `d27feadbb6b149fe259d7d7055dc3bed1287f557264ac51818aed708c8bf1b44` |
| `head` | BTT EBB42 V1.2.1 | `stm32g0b1xx` (`64 MHz`) | CAN (`PB0/PB1`, `1 Mbps`), `0x8002000` | `5f3949396f0c` | `kalico-ebb42.bin` | `43016` | `50f3908f4ca88d5027d93d527d15cb356d99bc0feea2b95801cd065b1663135d` |
| `eddy` | BTT Eddy Duo (CAN) | `rp2040` (`12 MHz`, `154` commands incl. `eddy-ng`) | CAN (`gpio4/gpio5`, `1 Mbps`), `0x10004000`, built with `CONFIG_WANT_EDDY_NG=y` | `632e1e4d52f7` | `kalico-eddy.bin` | `52156` | `ee60200f8fa4dd0f738a10da167189f4e41b646f5cc9219f1e434be52813a2cb` |

## Rollback to Mainline Klipper (`0cee841e3`)

A complete pre-Kalico rollback bundle and step-by-step re-flash procedure remain on the host at `/home/<user>/klipper-rollback-20261119/ROLLBACK.md` (and are included in `Moron_Tridont_Kalico_PRIVATE_2026-11-19.zip`). Notice that EBB42 (`5f3949396f0c`) and Eddy Duo (`632e1e4d52f7`) must always be flashed over `can0` before flashing the Octopus Pro H723 USB-to-CAN bridge (`c16b9f102b59`).
