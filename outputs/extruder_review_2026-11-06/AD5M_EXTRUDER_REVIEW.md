# Extruder review for the AD5M rebuild

November 6, 2026. Working toolboard: **BTT EBB42**, exact revision unconfirmed. Existing hotend: Bambu X1C. This report is a design recommendation, not a measured fit certification.

## Recommendation

Keep the functioning AD5M feeder for printer recovery and as a reference. For a new modular toolhead, prototype one Wristwatch G2 using a genuine LDO Galileo 2 extruder hardware kit and the exact WWG2 BOM. Buy one complete Orbiter 2.5 instead if reducing assembly and printed-bearing-fit work is the priority. For lowest-cost DIY exploration, build ProtoXtruder 2.0 with a matched HGX 2.0 kit and specified motor. Do not buy four sets until one complete head has passed printing and clearance checks.

Wristwatch G2 is my first DIY choice because its Orbiter 2 mount, available CAD, simple housing and documented build give a practical starting point. This is an integration judgment, not a claim that it has experimentally beaten every alternative. G2 uses a large driven hob against a bearing idler: dual powered filament hobs are not inherently superior. Removing that extra hob-to-hob mesh can remove one source of periodic feed error.

Orbiter 2.5 is my assembled choice because its manufacturer specifically revised shaft concentricity and the hob profile. The manufacturer measurements are not an independent comparison with AD5M. ProtoXtruder 2.0 has Sherpa mounting and large gears, but the author notes possible twisting effects from oblique teeth under demanding conditions. Its BOM is substantially different from original ProtoXtruder; do not mix versions.

Sherpa Mini Release 2 with a compatible quality RIDGA kit is the conservative fourth option. Wristwatch BMG with RIDGA is also sensible. I would not choose between these two by cosmetic preference until the carriage and hotend stack are laid out.

## Buying and making

- WWG2: genuine LDO G2 **extruder** kit (not a G2Z Z-drive kit); current WWG2 printed body, rear plate and tension arm; two M3 inserts; M3x15, M3x25 and M3x30 per published BOM. Check kit contents against the manual before ordering loose parts. Do not substitute a generic 10T motor for the G2 custom motor.
- Orbiter: complete genuine 2.5 assembly including its matched motor. An upgrade kit alone requires a compatible genuine Orbiter 2.0 donor.
- ProtoXtruder 2.0: matched HGX 2.0 oblique-gear kit; 36 mm round pancake 10T motor; six MR63ZZ bearings, specified shafts, tension hardware, three M3 inserts and listed screws. Verify which items the seller actually includes. Author recommends ABS/ASA, at least three perimeters and 40% infill.
- Make a separate EBB42 bracket, a rigid carriage adapter, an X1C hotend holder, constrained filament guide and cooling ducts. Select housing material/print settings from the chosen project's instructions. EBB42 does not require choosing a NEMA17 extruder: a separate bracket can carry it behind a smaller motor.
- Establish nozzle position and available travel before ordering rails or committing to the toolchanger coupling. Buying an extruder alone does not establish hotend, duct or AD5M carriage compatibility.

I have not priced complete delivered baskets: the index's historical kit prices exclude important variables such as motors, shipping, and hardware. Compare complete assemblies rather than gear-kit sticker prices. The linked Bondtech LGX Lite V2 listing is specifically without a motor, despite appearing under preassembled extruders in the index.

## AD5M comparison and reuse feasibility

The most important difference is interface documentation. The AD5M feeder is part of a proprietary integrated head. The shortlisted standalone feeders have public housing designs and established attachment patterns. This does not prove better extrusion than the AD5M; I found no controlled, same-hotend comparison establishing force, feed uniformity or maximum flow among them.

| Option | AD5M intact feeder | WWG2 / Orbiter 2.5 | ProtoXtruder 2.0 / Sherpa Mini |
|---|---|---|---|
| Upfront parts spending | Lowest if owned and serviceable | New matched assembly/kit | New gears, motor and printed housing |
| Custom carriage work | Must measure and adapt proprietary interface | Published Orbiter-pattern interface | Published Sherpa-pattern interface |
| Housing redesign | Preserve original bearing supports if possible | Public WWG2 CAD; Orbiter factory housing | Public printed-housing designs |
| Existing AD5M gear transplant | No documented kit interchange found | Do not assume compatible | Do not assume BMG/HGX compatibility |
| Current X1C hotend | Requires independently supported alignment | Requires compatible holder and guide | Requires compatible holder and guide |
| EBB42 | Separate verified bracket | Separate verified bracket | Separate verified bracket |
| Suitability for several future heads | Useful prototype/donor | My preferred standardization candidates | Budget standardization candidates |

**Reuse the complete feeder and motor: plausible and worth prototyping.** Mount the existing feeder as a self-contained module on a new rigid adapter. Preserve its gear bearing supports and tension mechanism. Independently mount the X1C hotend, align the two filament axes and minimize the unsupported gap with a properly seated guide. This keeps gear center distances and motor engagement intact. No completed adapter or dimensional fit is established yet.

**Reuse the motor in a different feeder: conditional.** Confirm mounting face, hole spacing, shaft length, pinion tooth count, pitch/module, axial gear location and electrical ratings. A similar-looking round motor or matching tooth count is insufficient. G2 has a custom motor; do not assume the stock motor can drive its gearbox. Avoid removing a pressed pinion until there is a proven reason.

**Reuse AD5M gears in a new printed body: a reverse-engineering project.** None of the reviewed designs documents AD5M internals as its intended gear kit. Measure shaft diameters, bearing seats, gear pitch, center distances, hob groove heights, axial spacers and idler travel. Replacing the metal/proprietary support with printed bearing seats may reduce stiffness and alignment unless deliberately engineered. The new housing must maintain support on the loaded shafts and allow cleaning and tension release.

**Reuse the entire original head housing: possible for recovery, less attractive for the long-term modular design.** It carries legacy packaging constraints while you already use a different hotend and toolboard. Retaining the feeder module while replacing its outer carrier is the more promising middle ground.

A community AD5M conversion config drives the feeder from an EBB-class toolboard and gives rotation_distance 4.4 without a separate gear_ratio. This supports electrical feasibility, not a verified setting for this unit or proof of an exact mechanical ratio. Calibrate the actual feeder; do not combine an effective rotation distance with an additional reduction factor. Do not copy that file's heater limits, permissive extrusion settings or EBB36 pin assignments into this build.

## What would establish fit

1. Measure the intact feeder and motor envelope, mounting holes, filament inlet/outlet axis and nozzle offset; weigh feeder plus motor separately from the full head.
2. Lay out the X1C holder, feeder, EBB42, connectors and cable bend space against the proposed X carriage. Keep the board clear of hot metal and preserve access to tensioner and fasteners.
3. Print a simple feeder adapter/filament-guide prototype. Check insertion, release, alignment, backlash and unobstructed full XY travel before final cooling ducts.
4. Verify EBB42 revision, motor coil mapping and appropriate current. Test measured filament advance with the hotend disconnected, then extrusion under normal thermal conditions; tune pressure advance after basic feed calibration.
5. Compare equal material/nozzle/temperature prints and usable flow with the stock feeder and one replacement. Only then choose a repeatable standard for additional heads.

For the future changer, allow board/connector service access and dock clearance. Revisit the head-mounted XY homing sensors: homing must remain defined when a head is absent. A future toolchanger does not itself require a filament cutter or four new extruder drivers on the mainboard.

## Full index screening

Every indexed extruder is covered below. These are suitability judgments for this build, not a performance ranking. Sparse or inaccessible external documentation limits confidence in the affected options.

| Design | Recommendation for this build |
|---|---|
| [Clockwork1](https://github.com/VoronDesign/Voron-Afterburner/releases) | Pass unless choosing Afterburner. |
| [Clockwork2](https://github.com/VoronDesign/Voron-Stealthburner) | Only if choosing Stealthburner; do not let this set the whole carriage design. |
| [Pocket Watch](https://github.com/VoronDesign/Voron-0/tree/Voron0.0/VORON_Pocketwatch) | Remote-feed option; not selected for the short direct filament path planned here. |
| [Pocket Watch Nema17](https://mods.vorondesign.com/details/1rw8IyTJO2hoMYllya1IgQ) | Remote-feed option; not selected for the short direct filament path planned here. |
| [Night Watch](https://github.com/VoronDesign/Pocket-Watch/tree/main) | Remote-feed option; not selected for the short direct filament path planned here. |
| [Dual Nightwatch](https://github.com/hartk1213/MISC/tree/main/Voron%20Mods/Extruders/Dual_Nightwatch) | Remote-feed option; not selected for the short direct filament path planned here. |
| [M4 Mobius](https://github.com/VoronDesign/Mobius-Extruder) | Remote-feed option; not selected for the short direct filament path planned here. |
| [Mini14](https://github.com/hartk1213/MISC/tree/main/Voron%20Mods/Extruders/Mini14) | Remote-feed option; not selected for the short direct filament path planned here. |
| [Wristwatch BMG](https://github.com/bythorsthunder/Voron_Mods/tree/main/Wristwatch_Extruder_BMG) | Strong alternate: compact, inexpensive if buying a good RIDGA kit; verify exact body and pinion. |
| [WWBMG IDGA](https://github.com/minilogique/ww-extruder-for-idga) | Useful if IDGA already owned; its forward-shifted filament path changes packaging. |
| [Sherpa Mini](https://github.com/Annex-Engineering/Sherpa_Mini-Extruder) | Conservative DIY choice; use current Release 2 and matched RIDGA/pinion. |
| [Sherpa Micro](https://github.com/Annex-Engineering/Sherpa_Micro-Extruder) | Consider when envelope demands it; avoid experimental fixed-idler alpha for baseline. |
| [Sherpa Heavy](https://github.com/Annex-Engineering/Sherpa_Heavy-Extruder) | Specialist high-force choice; no demonstrated need with the current X1C hotend. |
| [Sherpa Extra Heavy](https://www.printables.com/model/549890-sherpa-extra-heavy-with-nema17-update-2) | Only if a suitable standard NEMA17 is already available; not my default moving-head choice. |
| [Sherpa Crew Mini](https://github.com/jrlomas/Sherpa-Crew-Mini) | Extra parts and adjustment; defer. Author points to Miro as its evolution. |
| [Sherpa Zero](https://github.com/jrlomas/Sherpa-Zero) | Interesting backlash experiment; defer until a measured extrusion defect justifies it. |
| [Sheperd](https://github.com/odbee/shepherd/tree/main?fbclid=IwRlRTSANY_pNleHRuA2FlbQIxMQABHhML2hOx8zadzG2nzILrX3HnMdU5N6_FB9lNbvKDGy4oQdN78GPfmhmRN6_c_aem_9hzl1_RPQ__LE-mjas_uyA) | Choose only with Archetype Breakneck; integrated duct geometry constrains reuse. |
| [Fz](https://github.com/FZaii/FZ-Extruder) | Viable alternate housing; no compelling build-specific advantage established. |
| [Miro](https://github.com/jrlomas/miro-extruder) | Experiment later: public beta, two drive stages, STL-only and more alignment work. |
| [Sailfin](https://github.com/CroXY3D/Sailfin-Extruder) | Viable alternate; check motor height, not just mounting holes. |
| [Sharkfin](https://github.com/KayosMaker/Sharkfin_Extruder) | Good alternate if its Xol mounting ear or idler options are useful. |
| [Sharketype](https://github.com/Armchair-Heavy-Industries/Sharketype) | Choose with compatible Archetype design; excludes Breakneck. |
| [HextrudORT](https://github.com/MirageC79/HextrudORT) | Interesting integrated carriage architecture; less attractive for a replaceable extruder module. |
| [Vorxtrudort](https://github.com/nhchiu/VoronMods/tree/main/Extruders/Vorxtrudort) | Useful modular alternative with Sherpa/Orbiter mount variants. |
| [Vz HextrudORT](https://github.com/VzBoT3D/Vz-HextrudORT) | Worth considering for a Vz-style head; CNC and printed gear compatibility differs. |
| [BoomBox](https://www.printables.com/model/1236812-boombox-the-best-bowden-extruder-on-earth) | Remote-feed option; not selected for the short direct filament path planned here. |
| [RoundHouseBMG](https://github.com/chirpy2605/voron/tree/main/general/RoundHouse) | V0-oriented WIP; lower priority for this new carriage. |
| [Hummingbird](https://github.com/nhchiu/VoronMods/tree/main/Extruders/Hummingbird) | Good alternative if selecting LGX mounting. |
| [Large Gear Clockwork2](https://github.com/nhchiu/VoronMods/tree/main/Extruders/Large_Gear_Clockwork2) | Only if selecting Stealthburner. |
| [ProtoXtruder](https://github.com/nhchiu/VoronMods/tree/main/Extruders/ProtoXtruder) | Budget alternate; buy the exact compatible kit revision. |
| [ProtoXtruder 2.0](https://github.com/nhchiu/3DPrinter-Designs/tree/main/ProtoXtruder_2.0) | Budget shortlist winner. Match HGX 2.0 kit, motor, shafts and bearings to BOM. |
| [StealthProtoXtruder 2.0](https://www.printables.com/model/1372682-stealthprotoxtruder-20) | Conditional alternate; external model details were not independently retrieved. |
| [ProtoXtruder NX](https://www.printables.com/model/1020272-protoxtruder-nx) | Conditional alternate; verify latch and exact BOM on model page before buying. |
| [Papilio/Papilio Lite](https://github.com/kevinakasam/Papilio-Belt-Extruder) | Interesting belt-feed experiment; defer for recovery head. Lite has a more constrained flexible path. |
| [Tsunami](https://www.printables.com/model/1175316-beta-tsunami-extruder) | Defer; external model details were not independently retrieved. |
| [Galileo 2](https://github.com/JaredC01/Galileo2/tree/main/galileo2_extruder) | Choose G2E only with Stealthburner. |
| [Galileo 2 Standalone](https://github.com/JaredC01/Galileo2/tree/main/galileo2_standalone) | Good alternate, but upstream still labels G2SA public beta. |
| [Wristwatch G2](https://github.com/tetsu97/WristWatch-G2-Extruder) | First DIY choice: G2 internals, Orbiter mounting, documented assembly and CAD. |
| [Escapement](https://github.com/Armchair-Heavy-Industries/Escapement) | Consider with Archetype/Xol integration; sparse assembly documentation. |
| [Micro-cosm](https://github.com/Okanoa/micro-cosm) | Experimental rehousing; sparse documentation makes it a poor baseline. |
| [Orbiter 2](https://www.orbiterprojects.com/orbiter-v2-0/) | Reuse if already owned; for new buying prefer evaluating 2.5. |
| [Orbiter 2.5](https://www.orbiterprojects.com/orbiter-v2-5/) | First assembled choice; redesigned drive shaft and gears target extrusion consistency. |
| [BMG Extruder](https://www.bondtech.se/product/bmg-extruder/) | Reuse if already owned; not my first new purchase for compact packaging. |
| [LGX Lite Extruder](https://www.bondtech.se/product/lgx-lite-v2-large-gears-extruder-no-motor/) | Quality alternative; linked V2 product excludes motor and requires a specific 10T round motor. |
| [RoundAbout](https://github.com/chirpy2605/voron/tree/main/general/RoundAbout) | Donor/WIP project; buying an Orbiter to dismantle adds work without a demonstrated need. |
| [RoundTrip](https://github.com/chirpy2605/voron/tree/main/general/RoundTrip) | Useful for donor gear reuse; no AD5M gear variant documented. |
| [Lowboi Mk4](https://github.com/Shaunuss/Lowboi-Mk4) | Interesting second-head experiment; requires cut-down worm, lubrication and careful assembly. |
| [Waterweel](https://github.com/abigexplosion/WATERHWEEL-EXTRUDER/tree/main) | Pass for baseline: upstream seeks 48 V for best performance; current build is 24 V. |
| [Orbiter 1(1.5)](https://www.orbiterprojects.com/orbiter-1-5/) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Galileo 1](https://github.com/JaredC01/Galileo) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Stargazer](https://www.printables.com/model/245121-stargazer-v1) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Double Folded Ascender](https://github.com/Annex-Engineering/Folded_Ascender-Extruder) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [NF-Cannon](https://github.com/Mellow-3D/NF-Cannon) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Zesty-Nimble V3](https://zestytechnology.readthedocs.io/en/latest/nimble/nimblev3/index.html) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Titania](https://www.printables.com/model/729823-titania-extruder-with-e3d-titan-gears-made-in-sher) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Titanic](https://www.printables.com/model/1607304-titanic-extruder) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |
| [Cyclops](https://github.com/D3vil-Design/Cyclops-Extruder) | Do not buy into this family for this baseline; revisit only with existing donor parts and verified sourcing. |

## Evidence and coverage

The entire index repository was cloned: README, metadata, license and three gear-family images. All extruder listings were screened; 42 linked extruder/project README files were retrieved (some overlap with index community picks), plus the toolhead index. This is not an audit of every CAD body, issue, external manual or every file in all linked repositories. Pocket Watch/Night Watch README retrieval and Printables-hosted details were incomplete. Entries without retrieved primary project documentation remain preliminary.

The metadata is not a final interface authority: it marks several patterns unknown and omits the README's Titanic entry. It separates Papilio and Papilio Lite, while the README groups them. Always use the selected design's drawing for hole coordinates, axis position and clearance.

Primary sources:
- [Full index](https://github.com/SartorialGrunt0/Awesome-Extruders), snapshot commit ed451da4ab176daa55259d8e62707bb700b79793.
- [WWG2 and build manual](https://github.com/tetsu97/WristWatch-G2-Extruder).
- [Galileo 2 architecture, status and configuration](https://github.com/JaredC01/Galileo2).
- [Orbiter 2.5 manufacturer design notes](https://www.orbiterprojects.com/orbiter-v2-5/).
- [ProtoXtruder 2.0 BOM, warnings and assembly](https://github.com/nhchiu/3DPrinter-Designs/tree/main/ProtoXtruder_2.0).
- [Sherpa Mini Release 2](https://github.com/Annex-Engineering/Sherpa_Mini-Extruder).
- [LGX Lite V2 motor requirements](https://www.bondtech.se/product/lgx-lite-v2-large-gears-extruder-no-motor/).
- [AD5M feeder manufacturer listing](https://www.flashforge.com/products/filament-feeding-assembly-for-adventurer-5m-series).
- [Community AD5M conversion config](https://github.com/sedmenti/FlashForge_A5M_raspberry/blob/main/Klipper/printer.cfg).
- [BTT EBB official hardware](https://github.com/bigtreetech/EBB).

No measured AD5M mounting drawing, validated adapter, identical-condition mass comparison, or controlled extruder performance test was established in this review. Reuse is therefore a feasible design direction with explicit measurements remaining, not an already proven drop-in conversion.
