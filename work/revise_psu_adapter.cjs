const fs=require('fs');
let s=fs.readFileSync('work/annotate_psu.cjs','utf8');
s=s.replace("outputs/AD5M_PSU_annotated'","outputs/AD5M_PSU_annotated_R2'");
s=s.replace("t(1300,1590,'FROM THE DISTRIBUTION BLOCKS'",`t(65,1900,'30-PIN BED ADAPTER / DOWNSTREAM POWER',30,B,true);
t(65,1945,'MOSFET HOT BED + -> FPC pins 12-22 combined',27);
t(65,1985,'MOSFET HOT BED - -> FPC pins 1-11 combined',27);
t(65,2025,'FPC 23 -> Octopus PROBE DC (5 V); FPC 28 -> GND',26,A);

t(1300,1590,'FROM THE DISTRIBUTION BLOCKS'`);
s=s.replace("Bed heater -> MOSFET HOT BED output. Pi -> kit adapter for now.","FPC 23 requires 5 V, never PSU 24 V. FPC 26 -> probe signal PC5. Pi uses kit adapter.");
fs.writeFileSync('work/annotate_psu_R2.cjs',s);
require('./annotate_psu_R2.cjs');
