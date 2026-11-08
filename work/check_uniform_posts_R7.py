from pathlib import Path
import trimesh,numpy as np,json
from shapely.geometry import Polygon
p=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\EBB42_uniform_posts_R7');m=trimesh.load_mesh(p/'EBB42_short_bridge_R7.stl')
prev=None;rows=[]
for z in np.arange(.1,m.bounds[1,2],.2):
 lines=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,z]);adj={};pts={}
 for seg in lines:
  a,b=[tuple(np.round(v[:2],5)) for v in seg]
  if a==b:continue
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 visited=set();geom=None
 for start in adj:
  for nxt in adj[start]:
   if (start,nxt) in visited:continue
   ring=[start];a,b=start,nxt
   for it in range(len(lines)+1):
    visited.add((a,b));visited.add((b,a));ring.append(b)
    if b==start:break
    ns=[c for c in adj[b] if c!=a and (b,c) not in visited]
    if not ns:break
    a,b=b,ns[0]
   if ring[-1]!=start or len(ring)<4:continue
   poly=Polygon(ring).buffer(0)
   geom=poly if geom is None else geom.symmetric_difference(poly)
 if geom is None:continue
 if prev is not None:
  excess=geom.difference(prev.buffer(.205,quad_segs=2))
  if excess.area>.01:rows.append({'z_mm':round(float(z),2),'area_mm2':round(excess.area,3),'bounds':list(excess.bounds)})
 prev=geom
r={'watertight':bool(m.is_watertight),'connected_bodies':len(m.split()),'extents_mm':m.extents.tolist(),'layer_height_mm':.2,'overhang_test':'each section compared with previous section expanded by 0.205 mm (about 45 degrees)','unsupported_sections':rows}
(p/'printability.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
