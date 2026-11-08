const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/PK800/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const out='outputs/Octopus_AD5M_labels_R3';fs.mkdirSync(out,{recursive:true});
let svg=fs.readFileSync('outputs/Octopus_AD5M_labels_R2/Octopus_Pro_V11_AD5M_with_MOSFET.svg','utf8');
svg=svg.replace('width="3600" height="2680" viewBox="0 0 3600 2680"','width="5700" height="2680" viewBox="0 0 5700 2680"').replace('<rect width="3600" height="2680"','<rect width="5700" height="2680"');
const R='#ff3535',A='#ffc36b',W='#eee',C='#70bfff';let p=[];
function t(x,y,s,size=28,color=W,bold=false){p.push(`<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" font-weight="${bold?700:400}" fill="${color}">${s.replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`);}
function lead(a,c=R){p.push(`<polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="#08090b" stroke-width="9" stroke-linejoin="round"/><polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="${c}" stroke-width="4" stroke-linejoin="round"/>`);const [x,y]=a.at(-1);p.push(`<circle cx="${x}" cy="${y}" r="6" fill="${c}"/>`);}
function label(x,y,title,lines,a,color=R){t(x,y,title,34,color,true);lines.forEach((s,i)=>t(x,y+42+i*34,s,26,W));if(a)lead(a,color);}
p.push('<path d="M3640 200 V2390" stroke="#454950" stroke-width="2"/>');
t(3750,245,'EBB36 CAN V1.2.1 / WITHOUT MAX31865',42,R,true);
t(3750,295,'Your actual toolhead-board photo / front side shown',28);
t(3750,335,'R3: Octopus, bed MOSFET and EBB36 in one reference',24,A);
const file='C:/Users/PK800/.codex/codex-remote-attachments/01a184a7-3af8-7512-9fb7-97742eb76ee0/0F6E5719-5D1D-408F-A106-B493AD663FBD/5-Photo-5.jpg';
const b=fs.readFileSync(file).toString('base64');
p.push(`<svg x="3980" y="650" width="1125" height="795" viewBox="380 695 750 530"><image width="1368" height="1824" href="data:image/jpeg;base64,${b}"/></svg>`);

label(3750,465,'EXTRUDER MOTOR',['Angled four-pin motor connector.','Identify both coil pairs before repinning.'],[[3910,560],[3910,610],[4160,748]]);
t(4530,410,'POWER / CAN: connector as photographed',27,R,true);
p.push('<rect x="4530" y="435" width="520" height="135" fill="#17191e" stroke="#70bfff" stroke-width="2"/><path d="M4790 435 V570 M4530 502 H5050" stroke="#70bfff" stroke-width="2"/>');
t(4570,478,'GND',27,W,true);t(4820,478,'VIN / +24 V',27,R,true);
t(4570,545,'CAN L',27,C,true);t(4820,545,'CAN H',27,C,true);
t(4530,605,'Four-contact connector; this is the front mating view.',22,A);
// Leaders identify the connector zone; mini-grid records official contact order.
lead([[5030,580],[5135,580],[5135,720],[4560,720],[4560,830]],C);

label(3690,1010,'HALL ENDSTOPS',['X signal -> PB6','Y signal -> PB7','Shared +5 V and GND.'],[[3910,1150],[3945,1150],[4130,1180]]);
label(5170,1110,'X1C HEATER',['Green HE0 / E0 terminal.','Two heater wires; no polarity.','Software pin: PB13'],[[5150,1190],[5115,1190],[4800,1294]]);
label(5170,1430,'4-WIRE BLOWER',['PA1 channel reserved.','Control interface still unresolved.','Do not connect PWM to 24 V.'],[[5150,1470],[5070,1470],[4665,1470],[4665,1325]],A);

label(3750,1535,'X1C THERMISTOR',['TH0 / PA3; two wires, no polarity.','PT1000 jumper removed for NTC.'],[[4050,1485],[4050,1435],[4360,1240]]);
label(4400,1570,'HOTEND FAN',['Fan channel PA0 (FAN1 in BTT diagram).','Red fan lead -> VIN / +24 V.','Black fan lead -> PA0 switched negative.'],[[4460,1500],[4460,1435],[4510,1325]]);

t(3750,1750,'ENDSTOP HEADER: left -> right in the BTT diagram',30,R,true);
const cells=[['+5 V','Both VCC'],['GND','Both GND'],['PB6','X output'],['PB5','Unused'],['PB7','Y output']];
cells.forEach(([pin,use],i)=>{const x=3750+i*260;p.push(`<rect x="${x}" y="1780" width="260" height="120" fill="#17191e" stroke="${R}" stroke-width="2"/>`);t(x+25,1825,pin,29,R,true);t(x+25,1870,use,25,W);});
t(3750,1945,'Use the five-pin ENDSTOP header, not the four-pin I2C header above it.',27,A);
t(3750,1985,'Hall outputs need 3.3 V pull-ups. Confirm actual sensor leg orientation before soldering.',25);

t(3750,2080,'FOUR-WIRE HARNESS TO THE REAR',32,C,true);
t(3750,2130,'Octopus CAN H -> EBB CAN H; Octopus CAN L -> EBB CAN L.',28,C);
t(3750,2175,'Protected PSU +24 V -> EBB VIN; PSU V- -> EBB GND.',28);
t(3750,2220,'Keep CAN H/L twisted together. Terminate both physical ends of the bus.',26);
t(3750,2265,'Leave VUSB removed for normal 24 V operation. USB alone does not power the heater.',26,A);
t(3750,2360,'Actual cable colors have not been assigned to the four harness contacts.',26,A);
t(3750,2410,'The onboard driver runs the extruder; no plug-in TMC2209 is required on EBB36.',26);
t(3750,2460,'Pin references checked against BTT EBB36 V1.1/V1.2 diagram; actual photo is V1.2.1.',24,A);
t(3750,2510,'Blower control, X1C thermistor curve and electrical checks remain pending.',26,A);

const i=svg.lastIndexOf('</svg>');svg=svg.slice(0,i)+p.join('\n')+svg.slice(i);
fs.writeFileSync(path.join(out,'Octopus_MOSFET_EBB36_annotated.svg'),svg);
let notes=fs.readFileSync('outputs/Octopus_AD5M_labels_R2/Assignments.md','utf8');
notes+='\n\n## R3: EBB36 photo added\n\nThe original EBB36 V1.2.1 front photograph is preserved. The power/CAN mini-grid follows BTT front-view order: upper left GND, upper right VIN; lower left CAN L, lower right CAN H. The five-pin Endstop header reads +5 V, GND, PB6, PB5, PB7 left-to-right in BTT\'s drawing. X=PB6; Y=PB7; PB5 unused. The adjacent I2C header is distinct. TH0=PA3; heater=PB13; this project assigns PA0 to the two-wire hotend fan. PA1 remains reserved for the blower subject to resolving its control interface. Physical A3144 package-leg identification and the X1C thermistor curve remain unfinished.\n';
fs.writeFileSync(path.join(out,'Assignments.md'),notes);
sharp(Buffer.from(svg)).png().toFile(path.join(out,'Octopus_MOSFET_EBB36_annotated.png')).then(()=>console.log('Combined diagram rendered'));

