const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root='AD5M_HANDOFF_2026-11-02';const manifest=JSON.parse(fs.readFileSync(root+'/MANIFEST.json','utf8'));
for(const f of manifest.files){const bytes=fs.readFileSync(path.join(root,f.file));const hash=crypto.createHash('sha256').update(bytes).digest('hex');if(bytes.length!==f.bytes||hash!==f.sha256)throw Error('Manifest mismatch: '+f.file);}
const state=JSON.parse(fs.readFileSync(root+'/CURRENT_BUILD_STATE.json','utf8'));
if(state.decisions.bedControl.connector!=='HE0'||state.decisions.bedControl.pin!=='PA0'||state.decisions.ebb.xEndstop!=='PB6'||state.decisions.ebb.yEndstop!=='PB7'||state.cad.revision!=='R10')throw Error('Critical decision mismatch');
console.log(JSON.stringify({verifiedFiles:manifest.files.length,criticalDecisions:'pass',cad:'R10',bedControl:'Octopus HE0 / PA0'}));
