const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = 'C:/Users/PK800/Documents/ChatGPT/AD5M Build/reference/Voron_Trident/BOM_and_sourcing';
for (const size of [250,300,350]) {
  const values = {'#build-x':size,'#build-y':size,'#build-z':250,'#frame-x':size+160,'#frame-y':size+160,'#frame-z':500,
    'input[name=joint-options]:checked':'blind','input[name=upgrade-options]:checked':'new','input[name=feed-options]:checked':'direct'};
  const jq = selector => ({val:()=>values[selector], ready:()=>{}, attr:()=>{}});
  jq.each=(obj,fn)=>{for(const key of Object.keys(obj)) if(fn(key,obj[key])===false)break;};
  const ctx=vm.createContext({$:jq,document:{},model_name:'VT'});
  for(const file of ['bom_trident.js','common.js','configurator_trident.js'])
    vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),ctx,{timeout:1000});
  vm.runInContext('populate_bom()',ctx,{timeout:1000});
  const bom=ctx.bom;
  if(bom.Motion[`Linear Rail MGN12H ${size+50}mm`]!==1 || bom.Electronics['NEMA17 TR8x4 300mm Linear Stepper']!==3)
    throw Error('Unexpected generated geometry');
  let out=`# Trident ${size} x ${size} x 250 mm reference BOM\n\nGenerated November 3, 2026 from the archived official Voron configurator scripts.\n\nOptions: new build, blind-joint frame, direct-drive feed. This is a stock Trident reference, not the AD5M shopping list. Source scripts are preserved alongside this file; no source quantities were manually corrected. Confirm revision and component choices against the assembly manual before purchasing.\n\n`;
  for(const [category,items] of Object.entries(bom)) {
    out+=`## ${category}\n\n| Part | Quantity |\n|---|---:|\n`;
    for(const [item,count] of Object.entries(items)) out+=`| ${item.replaceAll('|','\\|')} | ${count} |\n`;
    out+='\n';
  }
  fs.writeFileSync(path.join(root,`REFERENCE_BOM_${size}.md`),out);
  console.log(`Generated ${size}: ${Object.values(bom).reduce((n,x)=>n+Object.keys(x).length,0)} entries`);
}
