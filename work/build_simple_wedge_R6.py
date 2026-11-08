import FreeCAD as A,Part,MeshPart,json,math
from pathlib import Path
V=A.Vector;r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');o=r/'outputs/EBB42_simple_wedge_R6';o.mkdir(exist_ok=True);base=80.1515;q=math.sqrt(.5)
# Full rectangular base and ONE solid triangular prism, as drawn.
p=Part.makeBox(60,21,4,V(-30,-12,base));p=p.makeFillet(1.0,p.Edges)
vs=[V(-20,-1,base+3.9),V(-20,7,base+3.9),V(-20,-1,base+11.9),V(-20,-1,base+3.9)]
w=Part.Face(Part.makePolygon(vs)).extrude(V(40,0,0));w=w.makeFillet(.8,w.Edges)
s=p.fuse(w).removeSplitter()
# Round the root transition where possible; exterior shapes are already rounded.
for radius in [.5,.25]:
 try:
  es=[e for e in s.Edges if abs(e.CenterOfMass.z-(base+4))<.03 and abs(e.CenterOfMass.x)<21 and e.CenterOfMass.y>-2]
  f=s.makeFillet(radius,es)
  if f.isValid() and len(f.Solids)==1:s=f;break
 except:pass
for x in [-27,-18,18,27]:s=s.cut(Part.makeCylinder(2.15,6,V(x,-7.498,base-1)))
# Sloped-face holes, 31 mm apart. Cut AFTER rounding to retain sharp rims.
face_z=base+7.9
for x in [-15.5,15.5]:s=s.cut(Part.makeCylinder(1.25,16,V(x,3+q,face_z+q),V(0,-q,-q)))
s=s.removeSplitter();assert s.isValid() and len(s.Solids)==1
s.exportStep(str(o/'EBB42_simple_wedge_R6.step'));ps=s.copy();ps.translate(V(30,12,-base));mesh=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.15,Relative=False);mesh.write(str(o/'EBB42_simple_wedge_R6.stl'))
source=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step');body=source.Solids[1].copy();body.rotate(V(),V(0,1,0),180);body.translate(V(0,0,92.21775))
parts=[]
for shape,color in [(body,[155,175,191]),(s,[239,153,49])]:
 v,f=shape.tessellate(.12);parts.append({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':color})
(o/'preview_parts.json').write_text(json.dumps(parts))
params={'shape':'one rectangular plate plus one central triangular wedge','base_mm':[60,21,4],'wedge_nominal_mm':[40,8,8],'main_round_radius_mm':1,'wedge_round_radius_mm':.8,'housing_holes_mm':{'x':[-27,-18,18,27],'y':-7.498,'diameter':4.3},'board_holes_mm':{'pitch':31,'diameter':2.5,'sloped_face_center_y':3,'sloped_face_center_z':face_z},'board_back_clearance':'Use separate 4 mm M3 spacers between the wedge face and PCB; screws thread into the printed wedge. Select length for approximately 5 mm plastic engagement.','valid_solid':s.isValid(),'mesh_closed_native':mesh.isSolid(),'housing_overlap_mm3':s.common(body).Volume,'print':'flat base down, supports off','tube_reference_y':12.12,'base_max_y':9,'fit':'physical motor/frame/carriage and plugged board not verified'}
(o/'parameters.json').write_text(json.dumps(params,indent=2));print(json.dumps(params,indent=2),flush=True)
doc=A.newDocument('SimpleWedgeR6')
for n,shape in [('PRINT_SimpleWedge',s),('REFERENCE_BambuMod',body)]:ob=doc.addObject('PartDesign::Feature',n);ob.Shape=shape
doc.recompute();doc.saveAs(str(o/'EBB42_simple_wedge_assembly_R6.FCStd'))
