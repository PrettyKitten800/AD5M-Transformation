# BTT controller options for the AD5M

Research date: November 2, 2026, America/New_York.

This is a purchasing comparison, not a change to the active build. Current hardware remains Octopus Pro V1.1 H723, Pi 5 and EBB36 V1.2.1. The user reports the EBB flashed. The Octopus 3.3 V indicator is unlit, but voltages and the cause have not been measured. No replacement has been selected.

## Build requirements used for comparison

- Three mainboard motor channels: CoreXY A/B and Z. The EBB handles the extruder.
- Keep the standalone Pi 5 and stock rear-cover position.
- Existing conventional BTT TMC2209 V1.3 modules: three used, one spare; their electrical condition is not established.
- Prefer native USB plus onboard CAN hardware for a Klipper USB-to-CAN bridge to the EBB.
- External bed MOSFET remains in the plan. Current Octopus HE0/PA0 controls it; BED-POWER and BED-OUT are unused. GPIO assignments must change if the controller model changes.
- Stock bed-probe signal behavior and the four-wire toolhead blower interface remain unresolved. A different board does not by itself validate either interface.

## Other mainboard candidates

| Board | Independent motor channels | Existing driver type | PCB size, mm | Onboard CAN | Assessment for this build |
|---|---:|---|---|---|---|
| SKR 3 EZ | 5 | Accepts conventional and EZ modules | 109.7 x 98 | Yes | Compact H7 alternative with a future change to EZ drivers available. Separate motor supply supports up to 48 V with suitable drivers. |
| SKR 3 | 5 | Conventional modules | 110 x 85 | Yes | Smaller, capable conventional-driver board; fewer expansion connections than the Octopus. |
| SKRat V1.0 | 5 | Conventional modules | 110 x 85 | Yes | Strong value for a 24 V build focused on fans and sensors. G0B1 processor; four two-wire PWM fan ports, two four-wire fan ports, configurable proximity input. |
| SKR Mini E3 V3.0 | 4 | Integrated TMC2209s | 103.75 x 70.25 | No | Can cover current motor count, but needs a separate CAN adapter for the EBB and offers less expansion. |
| SKR Pico V1.0 | 4 | Integrated TMC2209s | 85 x 56 | No | Very compact RP2040 board. Adequate motor count; fewer peripherals and separate CAN hardware needed. |
| Kraken V1.1 | 8 | Integrated TMC2160s | 200 x 113 | Yes | Designed for larger, high-current machines; substantial packaging change for this AD5M. Two MAX31865 interfaces. |

Motor channels count independent drivers, not motor plugs. Parallel Z plugs on one channel do not create independently controlled Z motors. Integrated drivers cannot be swapped as plug-in modules.

All six use an external host; none requires a compute module. Onboard CAN denotes hardware capability, not a tested firmware build or verified device discovery for this printer. Bridge firmware, CAN pin selection and connector/termination mapping still need model-specific preparation.

SKR 3/EZ details: the optional SKR 3-DC MODE module provides selectable 5/12 V fan power; this is not the same as the Octopus's independent onboard fan selectors. SKR 3 EZ documentation also restricts some mixed conventional UART/SPI driver combinations. Check the intended mixture before buying future drivers. Current SKR 3 units may have H743 or H723 MCUs; inspect the actual chip before building firmware.

Kraken V1.1 must not inherit V1.0 driver sense-resistor settings. BTT's updated documentation specifies 50 milliohm for V1.1 S1-S4 and 75 milliohm for S5-S8, whereas V1.0 S1-S4 use 22 milliohm. No motor-current settings are being selected here.

## Price and availability snapshot

BTT's direct product variant data returned the following USD prices and available=true for the named variants during this research. These exclude tax/shipping and are not a delivery promise.

| Named variant | USD |
|---|---:|
| SKR 3, board only | 82.68 |
| SKR 3 EZ, board only | 90.36 |
| SKRat V1.0 | 49.00 |
| SKR Pico V1.0, integrated drivers | 39.85 |
| Kraken V1.1, integrated drivers | 129.99 |

The Mini E3 V3.0 product listing showed approximately $49.85; its live variant JSON could not be retrieved. BTT catalog "from" prices sometimes refer to accessories such as a DC module or driver connector, not the controller board.

## Other catalog entries

- SKR V1.4 and V1.4 Turbo remain listed. They can run printers, but are older LPC-generation platforms with no onboard CAN transceiver; they are not the preferred new purchase for this CAN toolhead conversion.
- Rodent and Scylla are CNC-oriented controllers, rather than the printer-mainboard alternatives shortlisted here.
- MMB CAN is a dedicated multi-material mechanism controller. It can be evaluated separately if a future filament changer is chosen; spare mainboard drivers are not the only way to expand.
- Pi/CB boards are hosts; U2C is a USB-to-CAN adapter; EBB boards are toolhead controllers. They do not replace the printer motion board in the same role.
- Older documented SKR Pro/GTR/SE BX boards were not verified as current standalone board variants in the checked catalog; do not describe them as discontinued or in stock without another check.

## Recommendation

Keep Octopus Pro V1.1 on the shortlist for least physical/wiring change and broad expansion. SKR 3 EZ is the strongest smaller alternative when higher-voltage motor upgrades and both driver formats matter. SKRat is the best-priced smaller option when retaining 24 V and prioritizing fan/sensor connections. MAX EZ remains an expansion option, with the previously established cost of new EZ driver modules.

Any different board needs new mounting holes, wiring references and firmware. A smaller PCB is not proof of assembled clearance under the stock cover. No existing sensor behavior, thermal parameters or CAN harness measurements are promoted to verified by this comparison.

## Primary sources

- [BTT current controller catalog](https://biqu.equipment/collections/control-board) and [page 2](https://biqu.equipment/collections/control-board?page=2).
- [SKR 3 hardware documentation](https://global.bttwiki.com/SKR%203.html), [store](https://biqu.equipment/products/bigtreetech-btt-skr-3-control-board-for-3d-printer), [current Klipper example including MCU variants](https://raw.githubusercontent.com/Klipper3d/klipper/master/config/generic-bigtreetech-skr-3.cfg).
- [SKR 3 EZ hardware documentation](https://global.bttwiki.com/SKR%203%20EZ.html), [store](https://biqu.equipment/products/btt-skr-3-ez-control-board).
- [SKRat hardware documentation](https://global.bttwiki.com/SKRat.html), [store](https://biqu.equipment/products/bigtreeetech-skrat-v1-0-control-board), [BTT Klipper example](https://raw.githubusercontent.com/bigtreetech/SKRat/master/Firmware/Klipper/generic-bigtreetech-skrat-v1.0.cfg).
- [Mini E3 documentation](https://global.bttwiki.com/SKR%20MINI%20E3.html), [store](https://biqu.equipment/products/btt-skr-mini-e3-v2-control-board) (URL retains old V2 wording, displayed product is V3).
- [Pico documentation](https://global.bttwiki.com/SKR%20Pico.html), [store](https://biqu.equipment/products/btt-skr-pico-v1-0).
- [Kraken documentation with V1.0/V1.1 differences](https://global.bttwiki.com/Kraken.html), [store](https://biqu.equipment/products/kraken-for-voron-phoenix), [BTT Klipper example](https://raw.githubusercontent.com/bigtreetech/BIGTREETECH-Kraken/master/Firmware/generic-bigtreetech-kraken.cfg).
- [SKR V1.4 documentation](https://global.bttwiki.com/SKR%20V1.4.html), [Scylla store description](https://biqu.equipment/products/bigtreetech-scylla-v1-0).
- [Klipper CAN and USB-to-CAN bridge documentation](https://www.klipper3d.org/CANBUS.html).

Prices above were read from each store product's .js variant endpoint to select the board variant rather than an accessory. Failed lookups were not treated as out-of-stock evidence.
