from pathlib import Path
import sys,json,numpy as np,struct,math
from PIL import Image,ImageDraw,ImageFont
root=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');sys.path.insert(0,str(root/'work'));from render_mockup import draw
out=root/'outputs/EBB42_open_tophat_bracket_R1';parts=json.loads((out/'preview_parts.json').read_text());q=math.sqrt(.5)
board=json.loads((root/'outputs/ebb42_mockup/board.json').read_text())
for i,p in enumerate(board):
 if i in [1667,1669,1671,1673]:continue
 span=np.array(p['bounds'][3:])-p['bounds'][:3]
 if i and max(span)<.8:continue
 v=np.array(p['v']);p['v']=np.column_stack([v[:,0]-20,-17-q*v[:,1]-q*v[:,2],64+q*v[:,1]-q*v[:,2]]).tolist();p['color']=[37,139,109] if not i else ([213,219,218] if max(span)>5 else [83,92,104]);parts.append(p)
p=Path(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\cable-clip.stl');data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);v=np.frombuffer(data,dt,n,84)['v'].reshape(-1,3).copy();v+=np.array([-11.74833,-10.21836,98.165023]);parts.append({'v':v.tolist(),'f':np.arange(len(v)).reshape(-1,3).tolist(),'color':[191,199,208]})
def tube():
 v=[];f=[];n=32
 for z in [78,103]:
  for i in range(n):v.append([2*math.cos(2*math.pi*i/n),12.12+2*math.sin(2*math.pi*i/n),z])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,j+n],[i,j+n,i+n]])
 return {'v':v,'f':f,'color':[66,183,198]}
parts.append(tube())
draw(parts,out/'assembly_views_raw.png',[('ASSEMBLY | 45 degree outward tilt',-35,20),('SIDE | filament tube stays clear',-90,0),('FRONT | two board mounting screws',0,8),('TOP | reused strain-relief clip',-30,70)])
im=Image.open(out/'assembly_views_raw.png');canvas=Image.new('RGB',(1400,1210),'#edf1f5');canvas.paste(im,(0,100));d=ImageDraw.Draw(canvas);ft=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',29);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d.text((25,15),'Open EBB42 bracket | six mounting holes | R1 prototype',font=ft,fill='#172b40');d.text((25,58),'Orange: new bracket   Blue: existing BambuMod body   Cyan: filament-tube reference',font=sm,fill='#263c50');d.text((25,1152),'48 mm body pair | 31 mm EBB42 pair | 14.5 mm clip pair from supplied clip model',font=sm,fill='#263c50');d.text((25,1180),'Old top cover removed. Exact stock clip fit, connectors, internal parts and frame sweep need physical checks.',font=sm,fill='#263c50');canvas.save(out/'Open_EBB42_45deg_bracket_preview.png')
draw([json.loads((out/'preview_parts.json').read_text())[1]],out/'Bracket_only_views.png',[('BRACKET ONLY | six functional holes',-35,20),('SIDE | 45 degree board supports',-90,0),('FRONT | body pair 48 mm',0,0),('TOP | strain-relief pair 14.5 mm',-30,70)])
