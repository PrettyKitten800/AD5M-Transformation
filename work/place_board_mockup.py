from pathlib import Path
import sys,json,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from render_mockup import draw
from PIL import Image,ImageDraw,ImageFont
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\ebb42_mockup')
h=json.loads((out/'housing.json').read_text());b=json.loads((out/'board.json').read_text());parts=[]
for i,s in enumerate(h):s['color']=[135,157,178] if i==1 else [183,194,204];parts.append(s)
for i,s in enumerate(b):
 if i in [1667,1669,1671,1673]:continue
 bounds=s['bounds'];span=np.array(bounds[3:])-bounds[:3]
 if i>0 and max(span)<.8:continue
 v=np.array(s['v']);s['v']=np.column_stack([v[:,0]-20,v[:,2]+36.41,v[:,1]+42]).tolist();s['color']=[38,138,110] if i==0 else ([218,221,213] if max(span)>5 else [85,91,100]);parts.append(s)
# Mount pads are conceptual; fastening locations are not established.
def box(x,y,z,dx,dy,dz):
 v=[[x+a*dx,y+b*dy,z+c*dz] for a,b,c in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
 return {'v':v,'f':[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)],'color':[227,155,56]}
# Concept supports stop beneath the four board holes; no holes are claimed validated.
for x in [-18,13]:
 for z in [44,75]:parts.append(box(x,32.12,z,5,3.7,5))
(out/'placement.json').write_text(json.dumps({'reference':'EBB42 CAN V1.1; actual board revision unknown','board_transform':'x=X-20, y=Z+36.41, z=Y+42','removed_cad_solids':[1667,1669,1671,1673],'housing_max_y_mm':32.119,'minimum_reference_board_back_clearance_mm':0.5,'carriage_present':False,'case_present':False,'mount_pads':'concept only'}))
draw(parts,out/'mockup_views.png',[('OUTER FACE | connectors face outward',165,20),('SIDE | board back toward housing',82,12),('OUTER FACE | straight on',180,0),('TOP | close placement concept',135,75)])
im=Image.open(out/'mockup_views.png');canvas=Image.new('RGB',(1400,1200),'#edf1f5');canvas.paste(im,(0,120));d=ImageDraw.Draw(canvas);f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',31);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d.text((25,18),'BambuMod + close-mounted EBB42 | placement study 01',font=f,fill='#172b40')
d.text((25,65),'Blue: supplied housing   Green/white: official board CAD   Amber: provisional mounting pads',font=sm,fill='#263c50')
d.text((25,1140),'Reference V1.1 board; long CAD spacers removed. Carriage, motor, wiring and protective case not modeled.',font=sm,fill='#263c50');d.text((25,1170),'Approx. 0.5 mm minimum modeled back clearance. Placement and fasteners are not fit-verified.',font=sm,fill='#263c50');canvas.save(out/'EBB42_close_mount_mockup_01.png')
