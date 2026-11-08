const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/PK800/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const out='outputs/Octopus_AD5M_labels_R2';fs.mkdirSync(out,{recursive:true});
let svg=fs.readFileSync('outputs/Octopus_AD5M_labels/Octopus_Pro_V11_AD5M_annotated.svg','utf8');
svg=svg.replace('width="2400" height="2680" viewBox="0 0 2400 2680"','width="3600" height="2680" viewBox="0 0 3600 2680"').replace('<rect width="2400" height="2680"','<rect width="3600" height="2680"');
let p=[];const red='#ff3535',gray='#d2d8e2',blue='#70bfff',white='#eee',amber='#ffc36b';
function t(x,y,s,size=28,color=white,bold=false){p.push(`<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" font-weight="${bold?700:400}" fill="${color}">${s.replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`);}
function wire(a,c,w=5){p.push(`<polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="#08090b" stroke-width="${w+5}" stroke-linejoin="round"/><polyline points="${a.map(x=>x.join(',')).join(' ')}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linejoin="round"/>`);const [x,y]=a.at(-1);p.push(`<circle cx="${x}" cy="${y}" r="6" fill="${c}"/>`);}
p.push('<path d="M2420 550 V2360" stroke="#454950" stroke-width="2"/>');
t(2500,245,'RELIABOT BED MOSFET',42,red,true);
t(2500,295,'Actual board photo / orientation shown below',28);
t(2500,335,'R2: added to the annotated Octopus reference',24,amber);
const file='C:/Users/PK800/.codex/codex-remote-attachments/01a184a7-3af8-7512-9fb7-97742eb76ee0/DEF546A8-79B3-4113-92CB-FBFFEB679CBA/1-Photo-1.jpg';
const b=fs.readFileSync(file).toString('base64');
p.push(`<svg x="2500" y="650" width="760" height="632" viewBox="200 840 950 790"><image width="1368" height="1824" href="data:image/jpeg;base64,${b}"/></svg>`);
// User-identified CONTROL positive; paths end beside the connector zone, not at inferred hidden contacts.
wire([[925,590],[925,430],[2350,430],[2350,500],[3300,500],[3300,754],[3055,754]],red);
wire([[830,590],[830,450],[2330,450],[2330,520],[3330,520],[3330,776],[3055,776]],gray);
t(2530,575,'BED-OUT + -> CONTROL + (wire beside +)',26,red,true);
t(2530,615,'BED-OUT - -> other CONTROL wire',26,gray,true);
t(2500,1360,'CONTROL / two-pin JST',34,red,true);
t(2500,1405,'Positive identification follows your instruction.',27);
t(2500,1450,'Gray CONTROL return goes to BED-OUT -.',27,gray);
t(2500,1490,'Do not substitute PSU ground for that return.',27,gray);
t(2500,1530,'Wire endpoints mark the connector zone; follow the wires.',24,amber);

t(3310,835,'HOT BED',30,blue,true);t(3310,875,'Output pair',25,blue);
wire([[3300,850],[3280,850],[2780,790]],blue,4);
wire([[3300,890],[3280,890],[2780,914]],blue,4);
t(3310,1040,'DC IN +',30,red,true);t(3310,1080,'From PSU +24 V',24);
wire([[3300,1095],[3250,1095],[2756,1074]],red,4);
t(3310,1170,'DC IN -',30,gray,true);t(3310,1210,'From PSU V-',24);
wire([[3300,1225],[3250,1225],[2756,1202]],gray,4);

t(2500,1640,'BED HEATER CONNECTIONS',34,blue,true);
t(2500,1690,'HOT BED + -> breakout pins 12-22 combined',28,blue);
t(2500,1735,'HOT BED - -> breakout pins 1-11 combined',28,blue);
t(2500,1790,'The two blue leaders identify the output pair only.',26);
t(2500,1830,'Individual output +/- contacts are not assigned by this photo.',24,amber);
t(2500,1920,'WIRE ALLOCATION',32,white,true);
t(2500,1970,'12 AWG: PSU -> DC IN, and heater output leads.',27);
t(2500,2015,'Supplied small two-wire cable: BED-OUT -> CONTROL.',27);
t(2500,2060,'Heater current comes from the MOSFET DC IN supply.',27);
t(2500,2105,'Octopus BED-OUT carries the control signal only.',27);
t(2500,2195,'Both original board photos are preserved.',26,amber);
t(2500,2235,'Sensor behavior and electrical checks remain pending.',26,amber);
svg=svg.replace('</svg>',()=>'</svg>'); // Preserve nested SVG elements; append only at root close.
const i=svg.lastIndexOf('</svg>');svg=svg.slice(0,i)+p.join('\n')+svg.slice(i);
fs.writeFileSync(path.join(out,'Octopus_Pro_V11_AD5M_with_MOSFET.svg'),svg);
fs.copyFileSync('outputs/Octopus_AD5M_labels/Assignments.md',path.join(out,'Assignments.md'));
fs.appendFileSync(path.join(out,'Assignments.md'),'\n\nR2 adds the actual ReliaBot photograph. CONTROL positive uses the user-identified wire beside the + mark; the other wire returns to Octopus BED-OUT negative. Blue output leaders identify the HOT BED pair without claiming its individual contact polarities.\n');
sharp(Buffer.from(svg)).png().toFile(path.join(out,'Octopus_Pro_V11_AD5M_with_MOSFET.png')).then(()=>console.log('MOSFET diagram rendered'));

