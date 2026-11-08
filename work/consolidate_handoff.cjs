const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=process.cwd(),pack=path.join(root,'AD5M_HANDOFF_2026-11-02');fs.mkdirSync(pack,{recursive:true});
function write(name,s){const dest=path.join(pack,name);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,s,'utf8');}
function copy(src,dest){const to=path.join(pack,dest);fs.mkdirSync(path.dirname(to),{recursive:true});fs.copyFileSync(src,to);}
function copyDir(src,dest){fs.mkdirSync(path.join(pack,dest),{recursive:true});for(const ent of fs.readdirSync(src,{withFileTypes:true})){const a=path.join(src,ent.name),b=path.join(dest,ent.name);if(ent.isDirectory())copyDir(a,b);else copy(a,b);}}
const summary=`AD5M BUILD — START HERE
Consolidated November 2, 2026. This package is the restart reference for the new chat.

READ IN THIS ORDER
1. This file (short current-state summary).
2. AD5M_REBUILD_HANDOFF.txt (full consolidated technical history, sources and details).
3. CURRENT_BUILD_STATE.json (structured decisions and incomplete tasks).
4. DECISIONS_AND_CORRECTIONS.txt (prevents repeating superseded advice).
5. Diagrams/ for current pictures; CAD/rear_tray_R10/ for the print model.

IMMEDIATE RESUME POINT
The user is preparing firmware flashing, most recently on Octopus Pro V1.1 H723.
They asked where BOOT0 and VBUS are. See Flashing_reference/ close-ups from BTT.
EBB36 V1.2.1 was connected to Pi USB but initially had no power; VUSB and DFU entry instructions were given.
No successful flash, lsusb result, CAN UUID, final printer.cfg, continuity test, homing or heating result has been supplied.
First determine current board/power/jumper state and obtain actual lsusb output; do not infer success from the conversation.

AUTHORITATIVE HARDWARE
Flashforge AD5M; Pi 5 8GB; Octopus Pro V1.1 H723; EBB36 CAN V1.2.1 without MAX31865;
3 used + 1 spare TMC2209 V1.3; ReliaBot external bed MOSFET V1.3; A3144 loose Hall sensors.
Actual PSU A-350GF-24-CX, 24V 14.6A. It is NOT the earlier assumed Mean Well.
Hotend is standard Bambu X1C, changed connector only. Stock bed and fans retained.

CRITICAL ACTIVE WIRING
- External bed MOSFET CONTROL is physically connected to OCTOPUS HE0, NOT BED-OUT.
- Octopus [heater_bed] heater_pin must therefore be PA0. Thermistor stays TB/PF3.
- Octopus BED-POWER and BED-OUT are UNUSED. Earlier diagrams showing their power feed are superseded.
- PSU feeds Octopus POWER + MOTOR-POWER, external MOSFET DC IN, and protected EBB power.
- Octopus main/motor shared feeder splits in harness connectors near the board; not two separate terminals under one clamp.
- MOSFET HOT BED + -> breakout 12-22 combined; HOT BED - -> breakout 1-11 combined.
- MOSFET CONTROL + is user-identified wire beside + mark; other wire -> HE0 switched negative. Independent polarity measurement not done.
- Breakout 23 -> Octopus PROBE DC selected to 5V; 28 -> GND; 26 -> PC5. Never feed 23 with 24V.
- Breakout 29 and 30 -> TB as separate thermistor wires.
- Z-max -> STOP2/PG10. Filament -> STOP3/PG11. Octopus STOP middle contact is GND, not 5V.
- In annotated portrait board view (power screws top, motors right), STOP left-to-right is 5V / GND / signal.
- EBB Hall X=PB6, Y=PB7; both share 5V/GND. PB3/PB4 was a mistaken comparison, now corrected.
- EBB heater PB13; TH0 PA3; hotend fan PA0; blower PA1 reserved but its electrical interface is unresolved.
- EBB and Octopus GPIO names are on different MCUs: EBB PA0 does not conflict with Octopus PA0 when namespaced correctly.

UNFINISHED DESIGN/TESTING
Blower PWM electrical interface; X1C thermistor curve; actual sensor signal levels and inversion;
CAN cable contact/color mapping and termination; driver setup; fuse sizing; completed bed splices and insulation;
sensor repinning verification; physical fit/thermal commissioning; all firmware/device IDs and powered tests.
User originally had no multimeter and deferred continuity checks. Acquisition/testing not confirmed.
Do not confuse this unfinished work with merely a documentation gap.

COMMUNICATION PREFERENCES
Help one concrete step at a time. Avoid repeating component/material questions already answered.
Post annotated PNGs directly in chat. Keep Octopus+MOSFET, EBB and PSU as separate pictures.
Preserve actual board photos; use vector overlays. An AI-generated preview altered hardware and was rejected.
Do not reopen the user-specified MOSFET CONTROL polarity premise as if it had never been discussed;
retain the premise while accurately recording that electrical verification is pending.

PACKAGE CONTENTS
Diagrams/01_Octopus_and_MOSFET_HE0.png and .svg : current HE0 power/control plan.
Diagrams/02_EBB36.png and .svg : separate EBB diagram; blower remains amber.
Diagrams/03_PSU_HE0.png and .svg : no BED-POWER feed; bed-adapter paths included.
Official_pinouts/ : saved BTT Octopus and EBB drawings.
Flashing_reference/ : BOOT0 and VBUS location close-ups.
CAD/rear_tray_R10/ : final delivered draft model, STEP/STL, source, parameters, fit coupons, validation.
Photos/ : selected original board, PSU, fan, adapter and Z-sensor photos.
Diagram_sources/ : frozen drawing scripts for reference; paths may need rebasing before rerun.
MANIFEST.json : relative file list, byte sizes and SHA256 hashes.

Project folder: ${root}
This folder's older outputs remain available as history; this package selects the current versions.
`;
write('START_HERE.txt',summary);
let full=fs.readFileSync('AD5M_REBUILD_HANDOFF.txt','utf8');
const preface=`CONSOLIDATED EDITION 2 — RESTART PACKAGE
This full handoff is accompanied by START_HERE.txt, CURRENT_BUILD_STATE.json, and portable copies of the selected diagrams, CAD and photos in AD5M_HANDOFF_2026-11-02/.
Local paths in the original detailed sections remain useful for provenance. Prefer the package's relative Diagrams/, CAD/, Photos/ and Official_pinouts/ copies when transferring to another computer or agent.
The latest user request is to preserve this conversation and continue in a new chat because of context length. No new wiring or flashing outcome was reported while consolidating.

`;
if(!full.startsWith('CONSOLIDATED EDITION 2'))full=preface+full;
fs.writeFileSync('AD5M_REBUILD_HANDOFF.txt',full,'utf8');write('AD5M_REBUILD_HANDOFF.txt',full);

const state={updated:'2026-11-02',timezone:'America/New_York',workspace:root,phase:'Firmware-flashing preparation; successful flash not reported',hardware:{printer:'Flashforge AD5M',host:'Raspberry Pi 5 8GB',mainboard:'BTT Octopus Pro V1.1 STM32H723',toolhead:'BTT EBB36 CAN V1.2.1 without MAX31865',drivers:{model:'BTT TMC2209 V1.3',purchased:4,usedOnOctopus:3,spare:1},psu:{model:'A-350GF-24-CX',volts:24,ampsTotal:14.6},bedMosfet:'ReliaBot V1.3 external module',hotend:'Bambu X1C; changed JST only',xySensors:'Loose three-leg A3144'},decisions:{stockRearCover:true,bedControl:{board:'Octopus',connector:'HE0',pin:'PA0',mosfetControlPositive:'Wire identified by user beside + mark',independentlyMeasured:false},unusedInputs:['BED-POWER','BED-OUT'],powerSplit:'Harness junction near MOTOR-POWER; one termination per board terminal',bedThermistor:{connector:'TB',pin:'PF3',breakout:[29,30]},bedProbe:{connector:'3-pin PROBE',signal:'PC5',volts:5,breakout:{supply:23,ground:28,signal:26},electricallyTested:false},zEndstop:{connector:'STOP2',signal:'PG10'},filament:{connector:'STOP3',signal:'PG11'},stopOrderInPortraitBoardView:['5V','GND','signal'],ebb:{heater:'PB13',thermistor:'PA3',hotendFan:'PA0',blowerReserved:'PA1',xEndstop:'PB6',yEndstop:'PB7',endstopHeaderBttLeftToRight:['5V','GND','PB6','PB5','PB7'],powerCanBoardFront:[['GND','VIN 24V'],['CAN L','CAN H']]},communications:'Pi USB -> Octopus USB-to-CAN bridge -> EBB CAN',piPower:'Kit USB-C adapter initially'},unverified:{successfulOctopusFlash:null,successfulEbbFlash:null,dfuOutput:null,canDiscovery:null,canUuids:null,finalKlipperConfig:null,continuityTesting:null,multimeterAcquired:null,sensorRepinningCompleted:null,heaterTests:null,homing:null},openItems:['Four-wire blower PWM electrical interface','X1C thermistor curve','Signal voltage/inversion and bed-probe optocoupler mode','CAN conductor mapping, cable twist/flexibility, termination','Branch fuses and splice ratings','Driver UART/power jumpers/current/coil mapping','Actual cover fit, thermal clearance and strain relief'],cad:{revision:'R10',boundsMm:[167,172,5],baseMm:2,standoffAboveBaseMm:3,mosfetPitchMm:[52.5,42.5],throughHoles:true,geometricallyValidated:true,printerFitVerified:false}};
write('CURRENT_BUILD_STATE.json',JSON.stringify(state,null,2));
write('DECISIONS_AND_CORRECTIONS.txt',`DECISION HISTORY AND PRECEDENCE

1. Rear carrier evolved through R10. Final base is 2mm + 3mm posts = 5mm, not the earlier 1.5mm base/4.5mm total. Final width167mm, height172mm. All holes through. Three tie pads have 2mm corner radius; standoff roots fillet1.5mm. Final MOSFET pitch52.5x42.5mm; discard earlier41x51 or53x43 values.
2. Stock cover position is required. No spacer/extension authorization. Reference designs using rear extensions are not proof of this build's fit.
3. Actual PSU photo superseded assumed Mean Well identity: A-350GF-24-CX24V14.6A.
4. Original power drawings assumed MOSFET controlled from BED-OUT, hence included BED-POWER feed. User actually wired CONTROL to HE0. R5 supersedes all that: HE0/PA0 controls bed, BED-POWER and BED-OUT unused. LED reservation moved toHE1/PA3. External module still supplies bed current directly from PSU.
5. User explicitly said CONTROL wire beside + is positive and instructed continued work on that basis. Treat as user premise, not a measurement. Square pad vs round pad and nearby LED anode markings did not independently prove polarity.
6. EBB X/Y endstops ARE PB6/PB7. Earlier concern about PB3/PB4 was an assistant comparison error involving another expansion header. BTT diagram verifies correct Endstop header:5V,GND,PB6,PB5,PB7.
7. Stock sensor center is5V; Octopus STOP center isGND. Swap only at controller end as needed to obtain correct final functions. Saying "swap two wires" assumes signal already aligns; orientation of opposite cable faces can reverse apparent order. No completed repinning test was reported.
8. Final power split is inside harness connectors near MOTOR-POWER, not multiple separately terminated wires in one board clamp. It can feed both Octopus inputs from one PSU pair; EBB adds its own protected branch. Other PSU pair feeds MOSFET.
9. Blower is four-wire24V0.25A, not an ordinary two-wire output load. Keep electrical PWM adaptation unresolved until properly established. The guide's PA1 switched-output scheme is an observation, not this build's validated interface.
10. Hotend is standard BambuX1C with connector changed, not stock AD5M thermal hardware. Exact sensor curve still needs establishing. Generic BTT PID/current/temperature defaults do not become build specs by being in an example.
11. Firmware flashing is NOW the immediate task. EBB and Octopus jumper instructions were given; no command output or flash completion was reported.
12. Keep board flash records separate: targetMCU,clock,bootloader arrangement/offset,transport,pins,bitrate,buildfile,deviceID,result. Do not confuse a generic STM32 DFU USB ID with proof of which attached board is targeted. Do not erase or flash hardware without identifying current device and intended build.
13. Older diagrams/notes are history. Preferred images are the selected files in this package's Diagrams directory, not the older combined three-board SVG that still used BED-OUT.
`);
write('NEW_CHAT_PROMPT.txt',`Continue my Flashforge AD5M electronics replacement in this same project. First read:
${path.join(pack,'START_HERE.txt')}
Then read AD5M_REBUILD_HANDOFF.txt, CURRENT_BUILD_STATE.json and DECISIONS_AND_CORRECTIONS.txt in that folder. The package contains the current diagrams, CAD and original photos.

We are preparing firmware flashing. EBB36V1.2.1 (noMAX31865) and Octopus ProV1.1H723 are the relevant boards; do not assume either flash succeeded. My latest questions were locating Octopus BOOT0 and VBUS. Establish the current USB/power/jumper state and actual lsusb result before choosing the next flashing step.

Keep our current HE0/PA0-controlled external bed MOSFET wiring; BED-POWER and BED-OUT are unused. EBB Hall X/Y usePB6/PB7. Respect the other confirmed decisions and identify untested items from the documents. Help me one concrete step at a time, and show the current annotated pictures inline when useful. Do not repeat questions about hardware and materials already documented.
`);

const latest='outputs/AD5M_HE0_wiring_R5';
copy(latest+'/Octopus_Pro_V11_AD5M_with_MOSFET.png','Diagrams/01_Octopus_and_MOSFET_HE0.png');
copy(latest+'/Octopus_Pro_V11_AD5M_with_MOSFET.svg','Diagrams/01_Octopus_and_MOSFET_HE0.svg');
copy(latest+'/EBB36.png','Diagrams/02_EBB36.png');
copy('outputs/AD5M_board_diagrams_R4/02_EBB36.svg','Diagrams/02_EBB36.svg');
copy(latest+'/AD5M_PSU_annotated.png','Diagrams/03_PSU_HE0.png');
copy(latest+'/AD5M_PSU_annotated.svg','Diagrams/03_PSU_HE0.svg');
copy(latest+'/HE0_revision.md','Diagrams/HE0_revision.md');
copyDir('reference/octopus_v11','Official_pinouts');
copy('work/BOOT0_reference_zoom.png','Flashing_reference/Octopus_BOOT0.png');
copy('work/VBUS_reference_zoom.png','Flashing_reference/Octopus_VBUS.png');
const old='C:/Users/PK800/Documents/Codex/2026-10-28/i-have-a-flashforge-ad5m-3d-6';
copyDir(old+'/outputs/AD5M_rear_tray_DRAFT_R10','CAD/rear_tray_R10');
const att='C:/Users/PK800/.codex/codex-remote-attachments/01a184a7-3af8-7512-9fb7-97742eb76ee0';
const dirs={'0F6E5719-5D1D-408F-A106-B493AD663FBD':'boards_and_carrier','818AA0C1-9474-480C-A624-1012ACB6251C':'toolhead_fans','6B8986EE-BB2B-4EA2-8661-F31C2EA57E64':'bed_breakout','DEF546A8-79B3-4113-92CB-FBFFEB679CBA':'mosfet_control','940EBD6C-E777-4AFA-8C15-3A0A32BCFEF4':'mosfet_rear','D6CB87E2-E776-48FC-BFEB-025547FBA544':'psu','93CC6146-4CA2-46E8-9595-C69775A5A033':'z_max_plug','3C188180-F639-431D-86A0-FA7CA034E0E4':'z_endstop_sensor'};
for(const [dir,label]of Object.entries(dirs))copyDir(att+'/'+dir,'Photos/'+label);
const tempPhoto='C:/Users/PK800/AppData/Local/Temp/codex-clipboard-5a3b90bc-e8bf-4439-b224-8faac380b7d1.png';if(fs.existsSync(tempPhoto))copy(tempPhoto,'Photos/filament_sensor_guide_S_V_G.png');
copy(old+'/work/chaotic/Mainboard/Photos/m8p-accessory-pinouts.jpg','Photos/reference_bed_and_sensor_pinout.jpg');
copy(old+'/work/sedmenti/IMG/fan_part.png','Photos/reference_four_wire_blower.png');
copy(old+'/work/sedmenti/IMG/endstop_wiring.png','Photos/reference_Hall_endstops.png');
for(const name of ['annotate_octopus_HE0.cjs','add_mosfet_HE0.cjs','annotate_psu_HE0.cjs','add_ebb36.cjs','revise_HE0.cjs'])copy('work/'+name,'Diagram_sources/'+name);
write('Diagram_sources/README.txt','Frozen source scripts for provenance. They contain original absolute photo paths and some historical output paths. Rebase paths to package Photos/ and the desired output directory before rerunning. The selected Diagrams files, not regeneration of all historical scripts in order, define current wiring. CAD source is separately portable and requires CadQuery/trimesh; Python dependencies are not bundled.\n');

const manifest=[];function walk(dir){for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const full=path.join(dir,ent.name);if(ent.isDirectory())walk(full);else if(ent.name!=='MANIFEST.json'){const data=fs.readFileSync(full);manifest.push({file:path.relative(pack,full).replaceAll('\\','/'),bytes:data.length,sha256:crypto.createHash('sha256').update(data).digest('hex')});}}}walk(pack);
write('MANIFEST.json',JSON.stringify({created:'2026-11-02',files:manifest},null,2));
fs.writeFileSync('START_HERE_AD5M.txt',summary,'utf8');
console.log(JSON.stringify({package:pack,files:manifest.length,totalBytes:manifest.reduce((s,x)=>s+x.bytes,0)}));
