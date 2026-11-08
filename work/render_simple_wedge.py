from pathlib import Path
import sys,json,trimesh
from PIL import Image
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');sys.path.insert(0,str(r/'work'));from render_mockup import draw
p=r/'outputs/EBB42_simple_wedge_R6';a=json.loads((p/'preview_parts.json').read_text())
draw([a[1]],p/'Bracket_preview.png',[('R6 | single central wedge',145,32),('SIDE | triangular cross section',90,0),('TOP | four carriage holes, two EBB pilots',0,90),('UNDERSIDE | flat print base',145,-35)])
im=Image.open(p/'Bracket_preview.png');im.crop((0,0,700,525)).resize((1120,840)).save(p/'Bracket_isometric.png')
draw(a,p/'Housing_preview.png',[('ASSEMBLY | housing reference',-35,25),('SIDE | original housing',90,0),('TOP | wedge on rectangular base',0,90),('REVERSE',145,25)])
m=trimesh.load_mesh(p/'EBB42_simple_wedge_R6.stl');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
(p/'mesh_validation.json').write_text(json.dumps({'watertight':True,'connected_bodies':1,'winding_consistent':True,'extents_mm':m.extents.tolist()},indent=2))
s=(r/'work/check_bridge_overhangs.py').read_text().replace('EBB42_sketch_bridge_R4','EBB42_simple_wedge_R6').replace('EBB42_short_bridge_R4','EBB42_simple_wedge_R6');(r/'work/check_simple_wedge.py').write_text(s)
