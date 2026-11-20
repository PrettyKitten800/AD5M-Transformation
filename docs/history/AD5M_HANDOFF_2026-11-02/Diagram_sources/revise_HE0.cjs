const fs=require('fs');
const out='outputs/AD5M_HE0_wiring_R5';fs.mkdirSync(out,{recursive:true});
function change(s,a,b){if(!s.includes(a))throw new Error('Missing revision target: '+a.slice(0,90));return s.replace(a,b);}
let base=fs.readFileSync('work/annotate_octopus.cjs','utf8');
base=change(base,"const out='outputs/Octopus_AD5M_labels'","const out='outputs/AD5M_HE0_wiring_R5'");
base=change(base,"label(60,245,'BED MOSFET CONTROL',['BED-OUT + -> CONTROL +','BED-OUT - -> CONTROL -'],[[510,305],[590,305],[830,590]]);","label(60,245,'BED-OUT — unused',['No control cable used here.','HE0 drives the external MOSFET.'],[[510,305],[590,305],[830,590]],true);");
base=change(base,'lead([[510,275],[620,275],[925,590]]);','');
base=change(base,"label(750,245,'BED-POWER',['From PSU: +24 V / GND','Input for BED-OUT control'],[[1040,335],[1040,430],[1075,590]]);","label(750,245,'BED-POWER — unused',['No PSU feed required.','Bed control uses HE0 / PA0.'],[[1040,335],[1040,430],[1075,590]],true);");
base=change(base,"t(795,470,'BED-OUT: -  +'","t(795,470,'BED-OUT: unused'");
base=change(base,"t(1000,470,'BED-POWER: +  -'","t(1000,470,'BED-POWER: unused'");
base=change(base,"label(65,740,'LEDs — optional',['HE0: VIN (+) / PA0 (switched -)','24 V strip only; rating pending'],[[555,780],[620,780],[780,745]],true);","label(65,740,'BED MOSFET CONTROL',['HE0 + -> MOSFET CONTROL +','HE0 - -> MOSFET CONTROL -','Bed heater_pin: PA0'],[[555,780],[620,780],[780,745]]);\nlabel(65,930,'LEDs — optional',['HE1: VIN (+) / PA3 (switched -)','24 V strip only; rating pending'],[[555,970],[620,970],[780,850]],true);");
fs.writeFileSync('work/annotate_octopus_HE0.cjs',base);
let mos=fs.readFileSync('work/add_mosfet.cjs','utf8');
mos=change(mos,"outputs/Octopus_AD5M_labels_R2","outputs/AD5M_HE0_wiring_R5");
mos=change(mos,"outputs/Octopus_AD5M_labels/Octopus_Pro_V11_AD5M_annotated.svg","outputs/AD5M_HE0_wiring_R5/Octopus_Pro_V11_AD5M_annotated.svg");
mos=change(mos,"'R2: added to the annotated Octopus reference'","'R5: MOSFET control connected to Octopus HE0'");
mos=change(mos,'[[925,590],[925,430],[2350,430],[2350,500],[3300,500],[3300,754],[3055,754]]','[[780,725],[680,725],[680,400],[2350,400],[2350,500],[3300,500],[3300,754],[3055,754]]');
mos=change(mos,'[[830,590],[830,450],[2330,450],[2330,520],[3330,520],[3330,776],[3055,776]]','[[780,777],[655,777],[655,420],[2330,420],[2330,520],[3330,520],[3330,776],[3055,776]]');
mos=mos.replaceAll('BED-OUT + -> CONTROL +','HE0 + -> CONTROL +').replaceAll('BED-OUT - -> other CONTROL wire','HE0 - -> other CONTROL wire').replaceAll('return goes to BED-OUT -','return goes to HE0 -').replaceAll('BED-OUT -> CONTROL','HE0 -> CONTROL').replaceAll('Octopus BED-OUT carries the control signal only.','Octopus HE0 carries the bed-control signal only.');
// Copy a new authoritative notes file below instead of inheriting old BED-OUT assignments.
mos=mos.replace("fs.copyFileSync('outputs/Octopus_AD5M_labels/Assignments.md',path.join(out,'Assignments.md'));",'');
mos=mos.replace(/fs\.appendFileSync\(path\.join\(out,'Assignments\.md'\),[^\n]+\);/,'');
fs.writeFileSync('work/add_mosfet_HE0.cjs',mos);

let psu=fs.readFileSync('work/annotate_psu_R2.cjs','utf8');
psu=change(psu,"outputs/AD5M_PSU_annotated_R2","outputs/AD5M_HE0_wiring_R5");
psu=change(psu,"['Octopus BED-POWER + / -','16 AWG'],",'');
psu=change(psu,"t(1300,1905,'PSU rating is 14.6 A total, shared by all loads.'","t(1300,1840,'BED-POWER / BED-OUT unused with HE0 control.',25,A);\nt(1300,1905,'PSU rating is 14.6 A total, shared by all loads.'");
fs.writeFileSync('work/annotate_psu_HE0.cjs',psu);
fs.writeFileSync(out+'/HE0_revision.md',`# R5: external bed MOSFET controlled from HE0

This revision supersedes the earlier BED-OUT control drawings. The user has connected the ReliaBot CONTROL plug to Octopus HE0.

- PSU 24 V still supplies Octopus POWER and MOTOR-POWER, ReliaBot DC IN and a protected EBB power branch.
- Octopus BED-POWER and BED-OUT are unused and do not need supply wiring for this arrangement.
- HE0 positive (VIN) -> MOSFET CONTROL positive, using the user's identified positive CONTROL wire.
- HE0 negative (PA0 switched output) -> MOSFET CONTROL negative. Do not substitute PSU ground.
- The external MOSFET DC IN supplies bed-heater current. Its HOT BED output feeds the breakout's heater groups as previously mapped.
- Bed thermistor remains on TB / PF3; the probe connections remain unchanged.
- In the existing Klipper [heater_bed] section, set heater_pin: PA0 (Octopus HE0), replacing PA1 / BED-OUT. Keep the correct bed sensor configuration and tune bed control for the completed system.
- No other Octopus configuration section may own PA0. The hotend heater is controlled by the separate EBB36 MCU (PB13).
- Optional LEDs are now reserved on Octopus HE1 / PA3, subject to electrical-rating confirmation. HE0 is no longer available for LEDs.

The EBB hotend fan uses its own PA0, e.g. head:PA0 or EBBCan:PA0. That is a different physical MCU pin from Octopus PA0, so there is no conflict when the configuration correctly names the MCUs.

Reference: https://github.com/Klipper3d/klipper/blob/master/config/generic-bigtreetech-octopus-pro-v1.1.cfg (HE0=PA0; HE1=PA3; TB=PF3).
`);
console.log('HE0 render scripts prepared');
