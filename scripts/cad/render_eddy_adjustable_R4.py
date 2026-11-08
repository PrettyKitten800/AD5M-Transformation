from pathlib import Path
import sys,json,numpy as np,trimesh
from PIL import Image
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from render_mockup import draw
p=r/'outputs/Eddy_Duo_adjustable_side_mount_R4';parts=json.loads((p/'preview_parts.json').read_text())
draw([parts[1]],p/'Bracket_preview.png',[('EDDY DUO | reinforced nut-channel walls',-35,25),('FACE | two 10 mm height slots',-90,0),('EDGE | flat 4 mm plate',0,0),('REVERSE | print broad face on bed',145,30)])
e=json.loads((r/'outputs/Eddy_Duo_BambuMod_mount_R1/eddy_mesh.json').read_text());v=np.array(e['v']);v=np.column_stack([v[:,2]+35.15158,-v[:,0]-62.9594,-v[:,1]+73.90625]);e['v']=np.column_stack([-v[:,0],v[:,1],92.21775-v[:,2]]).tolist();e['color']=[65,77,85];parts.append(e)
# Include the new simple EBB mount as a reference at its separate upper location.
t=json.loads((r/'outputs/EBB42_simple_wedge_R6/preview_parts.json').read_text())[1];t['color']=[111,153,165];parts.append(t)
draw(parts,p/'Assembly_preview.png',[('PROPOSED | Eddy beside the lower vent',-45,22),('SIDE | sensor close to nozzle fore-aft line',-90,0),('FRONT | EBB mount is above, independent',0,0),('TOP | compact side-mounted sensor',-40,65)])
im=Image.open(p/'Assembly_preview.png');im.crop((0,0,700,525)).resize((1120,840)).save(p/'Assembly_isometric.png')
m=trimesh.load_mesh(p/'Eddy_Duo_adjustable_mount_R4.stl');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
v=json.loads((p/'validation.json').read_text());v['mesh_watertight']=True;v['mesh_connected_bodies']=1;v['print_extents_mm']=m.extents.tolist();(p/'validation.json').write_text(json.dumps(v,indent=2));print(json.dumps({'extents':m.extents.tolist(),'watertight':True}))
