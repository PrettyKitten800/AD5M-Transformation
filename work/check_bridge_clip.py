import FreeCAD as A,Part,Mesh,json
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');o=r/'outputs/EBB42_sketch_bridge_R3'
m=Mesh.Mesh(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\cable-clip.stl')
s=Part.Shape();s.makeShapeFromMesh(m.Topology,.03);s=Part.makeSolid(Part.Shell(s.Faces));s.translate(A.Vector(-11.74833,-4.12886,90.316523));print('clipvalid',s.isValid(),flush=True)
d=A.openDocument(str(o/'EBB42_bridge_assembly_R3.FCStd'));b=d.getObject('REFERENCE_EBB42').Shape
hits=[]
for i,a in enumerate(b.Solids):
 if a.BoundBox.intersect(s.BoundBox):
  v=s.common(a).Volume
  if v>.002:hits.append([i,v])
print('clip clashes',hits,flush=True)
x=d.addObject('PartDesign::Feature','REFERENCE_Supplied_Clip');x.Shape=s;d.recompute();d.save()
v,f=s.tessellate(.15);(o/'clip_mesh.json').write_text(json.dumps({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':[192,198,205]}))
p=json.loads((o/'validation.json').read_text());p['supplied_clip_board_clashes']=hits;(o/'validation.json').write_text(json.dumps(p,indent=2))
