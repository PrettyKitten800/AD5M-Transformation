from pathlib import Path
import sys,json,numpy as np,math,shutil
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent));from render_mockup import draw
root=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');src=root/'outputs/Eddy_Duo_BambuMod_mount_R1';out=root/'outputs/Eddy_Duo_BambuMod_mount_R2';out.mkdir(exist_ok=True)
parts=json.loads((src/'preview_parts.json').read_text())[:2]
# 33.37 mm shift rearward from R1; nozzle-line alignment is a visual target, not measured geometry.
e=json.loads((src/'eddy_mesh.json').read_text());v=np.array(e['v']);e['v']=np.column_stack([v[:,2]+35.15158,-v[:,0]-62.9594,-v[:,1]+73.90625]).tolist();e['color']=[65,77,85];parts.append(e)
def cylinder_x(x,y,z,length,r):
 v=[];f=[];n=36
 for xx in [x,x+length]:
  for i in range(n):v.append([xx,y+r*math.cos(i*2*math.pi/n),z+r*math.sin(i*2*math.pi/n)])
 for i in range(n):
  j=(i+1)%n;f.extend([[i,j,n+j],[i,n+j,n+i]])
 for i in range(1,n-1):f.extend([[0,i+1,i],[n,n+i,n+i+1]])
 return {'v':v,'f':f,'color':[237,157,51]}
for y in [6.12,16.62]:parts.append(cylinder_x(30.1,y,82,4,2.8))
for p in parts:
 v=np.array(p['v']);p['v']=np.column_stack([-v[:,0],v[:,1],92.21775-v[:,2]]).tolist()
views=[('PROPOSED | Eddy moved back beside hotend',-45,22),('SIDE | left Duo hole is the proposed anchor',-90,0),('FRONT | reduced fore-aft offset',0,0),('TOP | carriage is not present in supplied CAD',-40,65)]
draw(parts,out/'placement_raw.png',views)
im=Image.open(out/'placement_raw.png');canvas=Image.new('RGB',(1400,1210),'#edf1f5');canvas.paste(im,(0,100));d=ImageDraw.Draw(canvas);ft=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d.text((25,15),'Eddy Duo R2 | direct-carriage attachment concept',font=ft,fill='#172b40');d.text((25,58),'Blue: existing housing   Dark gray: sensor   Amber: provisional spacers, not a finished mount',font=sm,fill='#263c50')
# Mark the left mounting hole in the straight side view using the same projection as renderer.
az=-math.pi/2;right=np.array([0,-1,0]);up=np.array([0,0,1]);dep=np.cross(right,up);R=np.array([right,up,dep]).T
allp=np.concatenate([np.array(p['v'])@R for p in parts]);mi=allp.min(0);ma=allp.max(0);sc=min(600/(ma[0]-mi[0]),410/(ma[1]-mi[1]));c=(mi+ma)/2
point=np.array([-52.4,16.62,92.21775-82])@R;xy=(700+350+(point[0]-c[0])*sc,100+290-(point[1]-c[1])*sc)
d.ellipse((xy[0]-9,xy[1]-9,xy[0]+9,xy[1]+9),outline='#c95425',width=3);end=(xy[0]-85,xy[1]-65);d.line((xy,end),fill='#c95425',width=3);d.text((end[0]-80,end[1]-26),'Carriage anchor',font=sm,fill='#a54120')
d.text((25,1150),'Position study only: actual carriage face, screw engagement and nozzle axis are not established.',font=sm,fill='#263c50');d.text((25,1178),'This position moves the sensor beside the vent; airflow and complete carriage clearance still need checking.',font=sm,fill='#263c50')
canvas.save(out/'Eddy_Duo_R2_placement_mockup.png')
(out/'PLACEMENT_STUDY.md').write_text('R2 placement-only mockup, November 8, 2026. Sensor shifted 33.37 mm rearward from R1. This is a provisional placement and does not establish nozzle axis or physical carriage attachment. Left Duo hole in straight side view is marked as proposed direct carriage anchor. Amber spacers are conceptual. Sensor is now adjacent to the honeycomb vent and may affect airflow; actual fan, carriage, fasteners, frame and nozzle remain absent. No R2 printable mount or drill template has been released. Do not use R1 drill layout.\n')
desk=Path(r'C:\Users\PK800\Desktop\AD5M_Eddy_Duo_Mount_R2');desk.mkdir(exist_ok=True)
for n in ['Eddy_Duo_R2_placement_mockup.png','PLACEMENT_STUDY.md']:shutil.copy2(out/n,desk/n)
