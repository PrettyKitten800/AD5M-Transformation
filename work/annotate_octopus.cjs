const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/PK800/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const f='C:/Users/PK800/.codex/codex-remote-attachments/01a184a7-3af8-7512-9fb7-97742eb76ee0/0F6E5719-5D1D-408F-A106-B493AD663FBD/3-Photo-3.jpg';
const b=fs.readFileSync(f).toString('base64');
const photo=`<g transform="translate(1100 1765) rotate(180)"><image width="1368" height="1824" href="data:image/jpeg;base64,${b}"/></g>`;
const base=`<svg xmlns="http://www.w3.org/2000/svg" width="1010" height="1645" viewBox="0 0 1010 1645">${photo}</svg>`;
fs.writeFileSync('work/octopus_base.svg',base);
sharp(Buffer.from(base)).png().toFile('work/octopus_base.png');

const out='outputs/Octopus_AD5M_labels';
const R='#ff3535',A='#ffc36b',W='#eeeeee';
let p=[`<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="2680" viewBox="0 0 2400 2680"><rect width="2400" height="2680" fill="#08090b"/><defs><clipPath id="board"><rect width="1010" height="1645"/></clipPath></defs>`];
function t(x,y,s,size=30,color=R,bold=false){p.push(`<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" fill="${color}" font-weight="${bold?700:400}">${s.replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`);}
function lead(points,color=R){p.push(`<polyline points="${points.map(a=>a.join(',')).join(' ')}" fill="none" stroke="#08090b" stroke-width="10" stroke-linejoin="round"/><polyline points="${points.map(a=>a.join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="4" stroke-linejoin="round"/>`);let [x,y]=points.at(-1);p.push(`<circle cx="${x}" cy="${y}" r="6" fill="${color}" stroke="#111" stroke-width="2"/>`);}
function label(x,y,title,lines,points,optional=false){t(x,y,title,38,optional?A:R,true);lines.forEach((s,i)=>t(x,y+40+i*31,s,26,optional?A:W));if(points)lead(points,optional?A:R);}
t(70,70,'AD5M / OCTOPUS PRO V1.1 H723',46,W,true);
t(70,115,'Your board photo, rotated 180 degrees. Printer connections adapted from the Manta guide.',25,W);
t(70,155,'Port assignments shown are the proposed build configuration; match Klipper to these choices.',24,A);
p.push(`<g transform="translate(700 500)"><g clip-path="url(#board)">${photo}</g></g>`);
label(60,245,'BED MOSFET CONTROL',['BED-OUT + -> CONTROL +','BED-OUT - -> CONTROL -'],[[510,305],[590,305],[830,590]]);
lead([[510,275],[620,275],[925,590]]);
label(750,245,'BED-POWER',['From PSU: +24 V / GND','Input for BED-OUT control'],[[1040,335],[1040,430],[1075,590]]);
label(1250,245,'POWER',['From PSU: +24 V / GND','Main board supply'],[[1435,335],[1435,405],[1265,590]]);
label(1760,245,'MOTOR-POWER',['From PSU: +24 V / GND','24 V for your TMC2209s'],[[1910,335],[1910,420],[1465,590]]);
t(795,470,'BED-OUT: -  +',20,R,true);t(1000,470,'BED-POWER: +  -',20,R,true);t(1220,470,'POWER: +  -',20,R,true);t(1410,470,'MOTOR: +  -',20,R,true);

label(65,740,'LEDs — optional',['HE0: VIN (+) / PA0 (switched -)','24 V strip only; rating pending'],[[555,780],[620,780],[780,745]],true);
label(1820,765,'X / CoreXY A motor',['MOTOR0 + driver 0'],[[1800,790],[1655,790],[1655,770]]);
label(1820,970,'Y / CoreXY B motor',['MOTOR1 + driver 1'],[[1800,995],[1655,995],[1655,940]]);
label(1820,1175,'Z motor',['MOTOR2 + driver 2'],[[1800,1200],[1660,1200],[1660,1080]]);
label(1820,1380,'Spare driver',['Fourth TMC2209 is not required','for the EBB-driven extruder.'],[[1800,1425],[1600,1425],[1600,1230]]);

label(65,1090,'Chamber fan 1 — optional',['FAN0 / PA8','Set its supply to the fan rating.'],[[560,1135],[625,1135],[760,1170]],true);
label(65,1240,'Chamber fan 2 — optional',['FAN1 / PE5','Set its supply to the fan rating.'],[[560,1285],[625,1285],[760,1230]],true);
label(65,1390,'Mainboard fan',['Proposed: FAN2 / PD12','Fan voltage/current to be confirmed.'],[[560,1435],[625,1435],[760,1290]],true);
label(65,1540,'Stepper cooling fan(s)',['Proposed: FAN3 / PD13','Check combined current and voltage.'],[[560,1585],[625,1585],[760,1350]],true);

label(65,1750,'BED PROBE — 3-pin PROBE',['FPC 23 -> DC supply set to 5 V','FPC 28 -> GND; FPC 26 -> PC5','Header top -> bottom: DC / GND / PC5'],[[595,1800],[645,1800],[980,1555]]);
label(65,1940,'Z-ENDSTOP',['Proposed: STOP2 / PG10','Signal PG10 / GND / 5 V','Distinct from the bed probe.'],[[560,1990],[640,1990],[895,1785]]);
label(1820,1590,'Bed thermistor',['TB / PF3','FPC 29 and 30; no polarity'],[[1800,1640],[1685,1640],[1060,1595]]);
label(1820,1830,'Filament runout',['Proposed: STOP3 / PG11','Signal PG11 / GND / 5 V','Verify sensor contact order.'],[[1800,1885],[1600,1885],[895,1845]]);
label(65,2250,'CAN -> EBB36',['CAN L -> L; CAN H -> H','Separate 24 V / GND feeds EBB.','Use the connector markings.'],[[560,2300],[640,2300],[900,2070]]);
label(1820,2210,'Pi USB data',['Pi USB-A -> Octopus USB-C','Octopus runs USB-to-CAN bridge.'],[[1800,2260],[1730,2260],[1520,2100]]);

t(70,2450,'RED = mapped connection / proposed assignment     AMBER = optional hardware or ratings still unconfirmed',27,W,true);
t(70,2495,'Probe power must be 5 V. Do not copy the Manta connector positions or its five-pin probe order.',27,R,true);
t(70,2535,'FAN6 and FAN7 are always-on outputs; FAN0-FAN5 are controllable. Fan negative is a switched return.',25,W);
t(70,2575,'X Hall -> EBB36 PB6; Y Hall -> EBB36 PB7. Extruder, hotend and toolhead fans also connect to EBB36.',25,W);
t(70,2620,'Source: BTT Octopus Pro V1.1 pinout + your actual board photo. Electrical checks and sensor behavior remain pending.',23,A);
p.push('</svg>');
const svg=p.join('\n');fs.writeFileSync(path.join(out,'Octopus_Pro_V11_AD5M_annotated.svg'),svg);
sharp(Buffer.from(svg)).png().toFile(path.join(out,'Octopus_Pro_V11_AD5M_annotated.png')).then(()=>console.log('Annotated diagram rendered'));
