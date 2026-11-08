from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from render_mockup import draw
out=root/'outputs/EBB42_uniform_posts_R7'
parts=json.loads((out/'preview_parts.json').read_text());p=json.loads((out/'placement.json').read_text());s=p['sin'];c=p['cos']
draw([parts[1]],out/'Bracket_preview.png',[('R7 | uniform-width angled posts',-35,32),('SIDE | ramps grow from the base',-90,12),('TOP | two original holes per foot',0,90),('UNDERSIDE | print this face on the bed',145,-35)])
for i,b in enumerate(json.loads((root/'outputs/ebb42_mockup/board.json').read_text())):
 if i in [1667,1669,1671,1673]:continue
 span=np.array(b['bounds'][3:])-b['bounds'][:3]
 if i and max(span)<.9:continue
 v=np.array(b['v']);b['v']=np.column_stack([v[:,0]-20,p['board_base_y']-s*v[:,1]-c*v[:,2],p['board_base_z']+c*v[:,1]-s*v[:,2]]).tolist()
 b['color']=[31,141,110] if not i else ([215,222,220] if max(span)>5 else [72,83,91]);parts.append(b)

draw(parts,out/'Assembly_preview.png',[('ASSEMBLY | supplied BambuMod reference',-35,24),('SIDE | 45 degree prototype',-90,0),('TOP | board and open extruder space',-35,80),('REVERSE | board mounting points',180,12)])
# Large standalone isometric for inline review.
im=Image.open(out/'Bracket_preview.png');im.crop((0,0,700,525)).resize((1120,840)).save(out/'Bracket_isometric.png')
