Octopus Pro V1.1 H723 flashing preparation â€” November 3, 2026

STATUS: Application FLASHED and read-back verified. Original 128 KiB bootloader verified unchanged. Runtime USB enumeration verified as 1d50:606f stm32h723xx after BOOT0 removal. CAN communication and Pi operation remain unverified.
Board revision confirmed by user; photo confirms STM32H723ZET6.
USB ROM DFU detected on Windows as 0483:df11, serial 3757325D3432.
Windows USB bus ID at preparation: 6-4 (can change after reconnection).

Firmware: octopus-pro-v1.1-h723-canbridge.bin
Source: https://github.com/Klipper3d/klipper
Commit: 0cee841e31d701595b3e509a0b502f6e320f52a8
Build directory: Ubuntu WSL /home/pk800/ad5m-flashing/klipper

Configuration:
- STM32H723
- 128 KiB bootloader offset; application address 0x08020000
- 25 MHz crystal
- USB-to-CAN bridge; USB PA11/PA12
- CAN RX PD0 / TX PD1
- CAN bitrate 1000000 (must match EBB firmware)

Host/Pi Klipper version and EBB firmware version/bitrate are not yet verified.
Host and MCU protocol compatibility must be checked before printer operation.
Printer motion/heater configuration is separate and has not been commissioned.

Completed:
- Administrator USB sharing and WSL attachment.
- Full 1 MiB original-flash backup saved.
- 48,800-byte application written at 0x08020000.
- Application read-back matches exactly.
- First 128 KiB bootloader read-back matches original exactly.

Completed: BOOT0 removed and board reconnected; runtime USB VID:PID is 1d50:606f, product stm32h723xx, serial 2C0022001351323431323537. Windows reports code 28 (no matching driver installed); USB descriptors match the Klipper USB-to-CAN firmware.
Next: Connect to Pi, inspect lsusb, ip -brief link and fresh kernel log. Do not expect a serial/by-id device for USB-to-CAN firmware. CAN messaging and host/EBB compatibility remain unverified.

References:
https://github.com/Klipper3d/klipper/blob/master/config/generic-bigtreetech-octopus-pro-v1.1.cfg
https://www.klipper3d.org/CANBUS.html
https://github.com/bigtreetech/BIGTREETECH-OCTOPUS-Pro
