from pathlib import Path
import numpy as np,json,math,sys
from PIL import Image,ImageDraw,ImageFont
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');sys.path.insert(0,str(r/'work'));from render_mockup import draw
out=r/'outputs/EBB42_rear_corridor_study_R2';out.mkdir(exist_ok=True)
h=json.loads((r/'outputs/EBB42_open_tophat_bracket_R1/preview_parts.json').read_text())[0];parts=[h];vs=[];s=math.sin(math.radians(3));c=math.cos(math.radians(3))
for i,p in enumerate(json.loads((r/'outputs/ebb42_mockup/board.json').read_text())):
 if i in [1667,1669,1671,1673]:continue
 span=np.array(p['bounds'][3:])-p['bounds'][:3]
 v=np.array(p['v']);v=np.column_stack([v[:,0]-20,2.4-s*v[:,1]-c*v[:,2],81+c*v[:,1]-s*v[:,2]]);vs.append(v)
 if i and max(span)<.8:continue
 p['v']=v.tolist();p['color']=[37,139,109] if i==0 else ([216,222,220] if max(span)>5 else [85,95,105]);parts.append(p)
v=np.concatenate(vs);bounds=[v.min(0).tolist(),v.max(0).tolist()]
def tube():
 v=[];f=[];n=32
 for z in [78,131]:
  for i in range(n):v.append([2*math.cos(2*math.pi*i/n),12.12+2*math.sin(2*math.pi*i/n),z])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,j+n],[i,j+n,i+n]])
 return {'v':v,'f':f,'color':[65,183,198]}
parts.append(tube())
draw(parts,out/'raw.png',[('CORRECTED SIDE | board in the rear gap',-90,0),('TOP | rear face to filament path',-90,85),('ISOMETRIC | 3 degrees from vertical',-35,20),('FRONT | height tradeoff',0,0)])
im=Image.open(out/'raw.png');can=Image.new('RGB',(1400,1205),'#edf1f5');can.paste(im,(0,100));d=ImageDraw.Draw(can);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
d.text((25,12),'Rear-gap placement study | angle flexible, location fixed',font=font,fill='#172b40');d.text((25,55),'Green/white: EBB42 reference   Cyan: filament-tube reference   No printable bracket released',font=sm,fill='#263c50')
# Same side-view projection as renderer; annotate old cover height and opposing boundaries.
R=np.array([[0,0,-1],[-1,0,0],[0,1,0]])
a=np.concatenate([np.array(p['v'])@R for p in parts]);lo=a.min(0);hi=a.max(0);sc=min(600/(hi[0]-lo[0]),410/(hi[1]-lo[1]));mid=(lo+hi)/2
oldy=100+290-(96.21775-mid[1])*sc
for x in range(90,610,16):d.line((x,oldy,x+8,oldy),fill='#b85c35',width=2)
d.text((25,oldy-25),'Old cover height',font=sm,fill='#a34e29')
for physical_y,label in [(-11.117,'Carriage back'),(12.12,'Filament path')]:
 x=350+(-physical_y-mid[0])*sc
d.text((25,1150),f'Board inside rear gap, above the supplied housing: top is {bounds[1][2]-96.21775:.1f} mm higher than old cover.',font=sm,fill='#a34e29');d.text((25,1178),'A lower placement intersects housing features. Actual extruder/motor and frame clearance remain unverified.',font=sm,fill='#263c50');can.save(out/'Rear_gap_angle_and_height_study.png')
(out/'placement.json').write_text(json.dumps({'angle_from_vertical':3,'board_y_base':2.4,'board_z_base':81,'board_bounds':bounds,'reference_back_plane_y':-11.117,'filament_axis_y':12.12,'board_min_z_above_main_housing_mm':bounds[0][2]-80.001502,'extra_top_height_vs_previous_cover_mm':bounds[1][2]-96.21775,'status':'placement study, no final bracket; previous R1 wrong-side arrangement superseded','caution':'not an installed motor/gear assembly clearance check'},indent=2))
print(json.dumps({'board_bounds':bounds,'extra_height_mm':bounds[1][2]-96.21775},indent=2))
p=r/'CURRENT_TOOLHEAD_SPEC.md';t=p.read_text(encoding='utf8');t+='\n## EBB42 placement correction — November 8, 2026\n\nUser requires the EBB42 between the back of the carriage and the filament path. The prior open-bracket R1 put it outside the rear face and is superseded. User explicitly permits changing the angle; 45 degrees was only a starting point. Corridor study in outputs/EBB42_rear_corridor_study_R2 demonstrates a near-upright placement above the existing housing but adds approximately 26 mm above the old cover. Lower placements were found to intersect modeled housing features with multiple board components. No revised printable bracket is released from this study. Need reconcile compact rear-gap placement, real motor/gear clearances, and height before printing.\n';p.write_text(t,encoding='utf8')
