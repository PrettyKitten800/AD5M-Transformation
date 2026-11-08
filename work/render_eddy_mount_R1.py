from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent));from render_mockup import draw
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\Eddy_Duo_BambuMod_mount_R1')
parts=json.loads((out/'preview_parts.json').read_text());e=json.loads((out/'eddy_mesh.json').read_text());v=np.array(e['v']);e['v']=np.column_stack([v[:,2]+35.15158,-v[:,0]-96.3294,-v[:,1]+73.90625]).tolist();e['color']=[65,77,85];parts.append(e)
for p in parts:
 v=np.array(p['v']);p['v']=np.column_stack([-v[:,0],v[:,1],92.21775-v[:,2]]).tolist()
draw(parts,out/'preview_raw.png',[('PROBE SIDE | bolt-on bracket',-45,22),('SIDE | 12 mm height adjustment',-90,0),('FRONT | nozzle position not modeled',0,0),('TOP | honeycomb vent remains uncovered',-40,65)])
im=Image.open(out/'preview_raw.png');canvas=Image.new('RGB',(1400,1190),'#edf1f5');canvas.paste(im,(0,100));d=ImageDraw.Draw(canvas);ft=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d.text((25,16),'Eddy Duo mount R1 | existing BambuMod housing',font=ft,fill='#172b40');d.text((25,60),'Blue: supplied housing   Orange: printable bracket   Dark gray: official Eddy family reference',font=sm,fill='#263c50')
d.text((25,1148),'Prototype: two new mounting holes / M3 inserts. Probe height, fan and full-travel clearance need physical checks.',font=sm,fill='#263c50');canvas.save(out/'Eddy_Duo_mount_R1_preview.png')
