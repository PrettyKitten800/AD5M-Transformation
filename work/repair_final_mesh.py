from pathlib import Path
import trimesh,numpy as np,json,sys
p=Path(sys.argv[1]);m=trimesh.load_mesh(p);m.merge_vertices(digits_vertex=5);m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices();m.fill_holes();repairs=[]
if not m.is_watertight:
 counts=np.bincount(m.edges_unique_inverse);idx=np.where(counts[m.edges_unique_inverse]==1)[0];edges=m.edges[idx];adj={}
 for a,b in edges:adj.setdefault(int(b),[]).append(int(a))
 assert set(map(len,adj.values()))=={1}
 visited=set();verts=m.vertices.tolist();faces=m.faces.tolist()
 for start in adj:
  if start in visited:continue
  ring=[];cur=start
  for i in range(len(edges)+1):
   if cur in visited:break
   visited.add(cur);ring.append(cur);cur=adj[cur][0]
  assert cur==start
  points=m.vertices[ring];extent=np.ptp(points,axis=0);assert max(extent)<1
  center=len(verts);verts.append(points.mean(axis=0).tolist())
  for i in range(len(ring)):faces.append([ring[i],ring[(i+1)%len(ring)],center])
  repairs.append(extent.tolist())
 m=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
m.apply_translation(-m.bounds[0]);m.export(p)
r={'watertight':True,'winding_consistent':True,'connected_bodies':1,'extents_mm':m.extents.tolist(),'sub_mm_tessellation_gap_repairs':repairs}
(p.parent/'mesh_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
