# Voron Trident reference library

Collected November 3, 2026 for the AD5M build. The Voron Trident is the reference architecture for the eventual machine: fixed-height CoreXY gantry, linear guides and a bed supported by three independently driven Z screws. Getting the AD5M printing again remains the immediate priority; triple Z is long term, and toolchanging is longer term.

## Start with these files

| Reference | Local file |
|---|---|
| Trident assembly manual | [Assembly manual PDF](Voron-Trident/Manual/Assembly_Manual_Trident.pdf) |
| Complete Trident design | [Trident repository README](Voron-Trident/README.md) |
| Trident assembly CAD, STEP | [STEP archive](Voron-Trident/CAD/trident_assembly.step.zip) |
| Trident assembly CAD, Fusion | [Fusion assembly](Voron-Trident/CAD/Trident_Assembly.f3d) |
| StealthBurner assembly manual | [Assembly manual PDF](Voron-Stealthburner/Manual/Assembly_Manual_SB.pdf) |
| StealthBurner high-contrast manual | [High-contrast PDF](Voron-Stealthburner/Manual/Assembly_Manual_SB_High_Contrast_7-7-23.pdf) |
| Trident gantry wiring | [Gantry wiring](Voron-Documentation/build/electrical/trident_gantry_wires.md) |
| Trident / V1 Octopus wiring | [Octopus wiring guide](Voron-Documentation/build/electrical/v1_octopus_wiring.md) |
| Trident Octopus configuration example | [Configuration file](Voron-Trident/Firmware/Octopus/Trident_Octopus_Config.cfg) |
| Initial startup and checks | [Startup guide](Voron-Documentation/build/startup/startup.md) |
| Software configuration | [Configuration guide](Voron-Documentation/build/software/configuration.md) |
| First print | [First-print guide](Voron-Documentation/build/slicer/first_print.md) |
| Maintenance | [Maintenance guide](Voron-Documentation/maintenance.md) |
| Published Trident sourcing guide | [Saved HTML](BOM_and_sourcing/Trident_sourcing_guide.html), [original CSV export](BOM_and_sourcing/Trident_sourcing_guide.csv) |
| Standard-size parts lists | [250 mm](BOM_and_sourcing/REFERENCE_BOM_250.md), [300 mm](BOM_and_sourcing/REFERENCE_BOM_300.md), [350 mm](BOM_and_sourcing/REFERENCE_BOM_350.md) |

The three readable parts lists were generated from the archived official configurator logic using new-build, blind-joint, direct-drive options and 250 mm Z height. They are stock Trident references, not a shopping list for this AD5M conversion. The original scripts and source URLs are saved alongside them. Different choices change the BOM.

## What is included

- **Voron-Trident/**: complete snapshot of the official repository, including Manual, CAD/native assemblies, Drawings_DXFs, STLs, Firmware, experimental files, README and license. Experimental content remains experimental.
- **Voron-Stealthburner/**: complete snapshot of the separately maintained official toolhead repository, including manuals, CAD, printable parts and license. Included for completeness; this does not select StealthBurner for the AD5M.
- **Voron-Documentation/**: complete source snapshot of the official documentation site, including build, electrical, software, startup, slicer, tuning, maintenance, images and community contributions. This shared repository also contains other printer models and historical manuals; use the Trident-specific entries where applicable.
- **BOM_and_sourcing/**: saved Trident product/configurator page, official BOM/configurator scripts, published sourcing guide in HTML and CSV, and three derived reference BOMs.
- **source_archives/**: original downloaded ZIP snapshots. Archive integrity was checked before extraction.
- **SOURCES.json** and per-repository source records: exact repository commits, download URLs and archive checksums.
- **FILE_MANIFEST.json**: file sizes and SHA-256 checksums for the collection, excluding the manifest itself.

The Markdown documentation is readable locally, but some original site links, Liquid/Jekyll includes and embedded online material require the live website. The saved configurator HTML is source capture, not a packaged offline application. Videos, external vendor sites, Discord and every third-party modification are not mirrored. The repository snapshots include their license files and preserve upstream content unchanged.

## Applying this to the AD5M

Use the Trident as the mechanical design reference, not as proof of AD5M component fit. Frame dimensions, rail lengths, screw lead, motor mounts and bed joints must match the eventual conversion design.

The archived Trident Octopus configuration explicitly targets **Octopus V1 / STM32F446**. It is not the configuration for the original **Octopus Pro V1.1 H723** or an automatically verified match for the replacement board. Existing AD5M wiring remains governed by the project-specific references, including HE0 control of the external DC bed MOSFET. Voron AC-heater/SSR examples do not replace that circuit.

The four-head toolchanger is an additional future project beyond the stock Trident documentation. No new motors, rails, frame size, probe or toolhead have been selected by archiving these references.

## Official online sources

- [Trident project and configurator](https://vorondesign.com/voron_trident)
- [Trident source repository](https://github.com/VoronDesign/Voron-Trident)
- [StealthBurner source repository](https://github.com/VoronDesign/Voron-Stealthburner)
- [Voron documentation website](https://docs.vorondesign.com/)
- [Voron documentation source repository](https://github.com/VoronDesign/Voron-Documentation)
- [Trident sourcing guide](https://vorondesign.com/sourcing_guide?model=VT)

These are dated snapshots, not an automatic update subscription. Compare source commits when updating the library; preserve the AD5M's current working configuration separately.
