const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/PK800/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const out='outputs/AD5M_HE0_wiring_R5';fs.mkdirSync(out,{recursive:true});
const file='C:/Users/PK800/.codex/codex-remote-attachments/01a184a7-3af8-7512-9fb7-97742eb76ee0/D6CB87E2-E776-48FC-BFEB-025547FBA544/1-Photo-1.jpg';
const b=fs.readFileSync(file).toString('base64');
let p=['<svg xmlns="http://www.w3.org/2000/svg" width="2500" height="2400" viewBox="0 0 2500 2400"><rect width="2500" height="2400" fill="#08090b"/>'];
const R='#ff3535',W='#eee',A='#ffc36b',G='#83e599',B='#70bfff';
function t(x,y,s,size=30,c=W,bold=false){p.push(`<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" fill="${c}" font-weight="${bold?700:400}">${String(s).replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`);}
function lead(a,c=R){p.push(`<polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="#08090b" stroke-width="10" stroke-linejoin="round"/><polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="${c}" stroke-width="4" stroke-linejoin="round"/>`);let [x,y]=a.at(-1);p.push(`<circle cx="${x}" cy="${y}" r="6" fill="${c}"/>`);}
t(60,65,'AD5M / PSU TERMINALS AND POWER DISTRIBUTION',43,W,true);
t(60,115,'A-350GF-24-CX | label rating: 24 V DC, 14.6 A | your actual PSU photo',29);
t(60,160,'Terminal numbering below is added for this drawing; read left to right in the photo.',26,A);
p.push(`<svg x="700" y="200" width="1005" height="1125" viewBox="70 0 670 750"><image width="960" height="1280" href="data:image/jpeg;base64,${b}"/></svg>`);
const pins=[[1186,1206],[1253,1200],[1318,1192],[1383,1183],[1447,1172],[1510,1161],[1570,1151]];
pins.forEach(([x,y],i)=>{const c=i<4?R:(i===4?G:A);p.push(`<path d="M${x} ${y+9} V1260" stroke="${c}" stroke-width="3"/><circle cx="${x}" cy="1285" r="23" fill="#08090b" stroke="${c}" stroke-width="2"/>`);t(x-8,1294,i+1,25,c,true);});

t(65,930,'1 and 2: +V',39,R,true);
t(65,980,'+24 V DC positive output',29);
t(65,1020,'Both screws share the same output.',26);
lead([[575,990],[630,990],[1186,1206]]);
lead([[575,1030],[650,1030],[1253,1200]]);
t(65,1350,'3 and 4: -V',39,R,true);
t(65,1400,'DC negative / return',29);
t(65,1440,'Both screws share the same return.',26);
lead([[575,1370],[640,1370],[1318,1192]]);
lead([[575,1410],[660,1410],[1383,1183]]);

t(1810,780,'5: PROTECTIVE EARTH',32,G,true);
t(1810,825,'Original mains earth conductor.',26);
t(1810,865,'Preserve chassis earth bonding.',26);
lead([[1790,850],[1750,850],[1447,1172]],G);
t(1810,970,'6: N / NEUTRAL',34,A,true);
t(1810,1015,'Original AC neutral conductor.',26);
lead([[1790,1040],[1730,1040],[1510,1161]],A);
t(1810,1150,'7: L / LIVE',34,A,true);
t(1810,1195,'From original switch / fuse harness.',26);
lead([[1790,1220],[1740,1220],[1570,1151]],A);
t(1790,1340,'AC INPUT: mains voltage',30,A,true);
t(1790,1380,'Identify conductors from the harness;',25);
t(1790,1420,'do not infer them from wire colors.',25);

p.push('<path d="M60 1520 H2440" stroke="#4b4f57" stroke-width="2"/>');
t(65,1590,'PROPOSED DC OUTPUT ALLOCATION',36,R,true);
t(65,1640,'Terminal 1 (+V) + terminal 3 (-V)',31,R,true);
t(65,1685,'-> ReliaBot DC IN + / - using 12 AWG copper',29);
t(65,1760,'Terminal 2 (+V) + terminal 4 (-V)',31,R,true);
t(65,1805,'-> Positive / negative DC distribution blocks using 12 AWG',29);
t(65,1850,'Use suitably rated terminals, branch protection and covered connections.',26,A);

t(65,1900,'30-PIN BED ADAPTER / DOWNSTREAM POWER',30,B,true);
t(65,1945,'MOSFET HOT BED + -> FPC pins 12-22 combined',27);
t(65,1985,'MOSFET HOT BED - -> FPC pins 1-11 combined',27);
t(65,2025,'FPC 23 -> Octopus PROBE DC (5 V); FPC 28 -> GND',26,A);

t(1300,1590,'FROM THE DISTRIBUTION BLOCKS',33,B,true);
const rows=[['Octopus POWER + / -','16 AWG'],['Octopus MOTOR-POWER + / -','16 AWG'],['Protected EBB36 VIN / GND branch','18 AWG cable power pair']];
rows.forEach(([a,b],i)=>{t(1300,1650+i*55,a,27);t(2100,1650+i*55,b,24,B);});
t(1300,1840,'BED-POWER / BED-OUT unused with HE0 control.',25,A);
t(1300,1905,'PSU rating is 14.6 A total, shared by all loads.',27,A,true);
t(1300,1950,'Distribution hardware: rated for at least 14.6 A.',26);
t(1300,1995,'Branch fuse sizes remain to be selected.',26,A);

t(65,2075,'FPC 23 requires 5 V, never PSU 24 V. FPC 26 -> probe signal PC5. Pi uses kit adapter.',29,W,true);
t(65,2130,'-V is the DC return; it does not replace protective earth. Do not add an earth-to--V bond based on this drawing.',25,A);
t(65,2180,'Set the input-voltage selector for your mains while unplugged: 115 V for 120 V supply; 230 V for 230 V supply.',25,A);
t(65,2230,'Preserve the stock AC switch / fuse / protective-earth arrangement. Refit the terminal cover before operation.',25);
t(65,2280,'Annotations identify terminal functions; leader-line colors are not a mains-wire color code.',26,W,true);
t(65,2330,'Terminal order is read from the photographed label. Electrical checks and first power-up remain pending.',25,A);
p.push('</svg>');
const svg=p.join('\n');fs.writeFileSync(path.join(out,'AD5M_PSU_annotated.svg'),svg);
sharp(Buffer.from(svg)).png().toFile(path.join(out,'AD5M_PSU_annotated.png')).then(()=>console.log('PSU diagram rendered'));

