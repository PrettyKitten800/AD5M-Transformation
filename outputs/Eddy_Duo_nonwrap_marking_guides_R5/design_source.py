import FreeCAD as A,Part,MeshPart,json
from pathlib import Path
V=A.Vector;r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');o=r/'outputs/Eddy_Duo_nonwrap_marking_guides_R5';o.mkdir(exist_ok=True)
# A short slip-fit button fits the existing plate hole and stops short of its back face.
head=Part.makeCylinder(4,2,V(0,0,0));shaft=Part.makeCylinder(1.55,3.5,V(0,0,2));lead=Part.makeCone(1.55,1.25,.3,V(0,0,5.5))
s=head.fuse(shaft).fuse(lead).removeSplitter()
# Soften only the exposed collar rim, before boring the sharp marking aperture.
for e in s.Edges:
 if e.BoundBox.ZLength<.001 and abs(e.CenterOfMass.z-2)<.001 and e.BoundBox.XLength>7.9:
  try:s=s.makeFillet(.35,[e]);break
  except:pass
s=s.cut(Part.makeCylinder(.8,8,V(0,0,-1))).removeSplitter();assert s.isValid() and len(s.Solids)==1
s.exportStep(str(o/'Centering_button_3p1_OD_1p6_bore.step'));m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.03,AngularDeflection=.15,Relative=False);m.write(str(o/'Centering_button_PRINT_TWO.stl'))
# Exact reference placement: buttons sit on the OUTSIDE face; no piece wraps the housing.
plate=Part.read(str(r/'outputs/Eddy_Duo_adjustable_side_mount_R4/Eddy_Duo_adjustable_mount_R4.step'));parts=[]
for sh,col in [(plate,[155,175,191])]:
 v,f=sh.tessellate(.12);parts.append({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':col})
for z in [64,84]:
 sh=s.copy();sh.rotate(V(),V(0,1,0),-90);sh.translate(V(36.1,-6,z));v,f=sh.tessellate(.05);parts.append({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':[239,153,49]})
for p in parts:p['v']=[[-x,y,92.21775-z] for x,y,z in p['v']]
(o/'preview_parts.json').write_text(json.dumps(parts))
v,f=s.tessellate(.05);(o/'button_mesh.json').write_text(json.dumps({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':[239,153,49]}))
(o/'validation.json').write_text(json.dumps({'valid_solid':s.isValid(),'closed_mesh':m.isSolid(),'sleeve_OD_mm':3.1,'nominal_mount_hole_diameter_mm':3.3,'marking_bore_mm':1.6,'shaft_length_mm':3.8,'mount_plate_thickness_mm':4,'shaft_clearance_from_housing_mm':.2,'collar_diameter_mm':8,'collar_thickness_mm':2,'quantity':2,'function':'center marking only; does not locate the plate or validate gantry clearance'},indent=2))
print('Created single button STL; print two copies.',m.isSolid(),flush=True)
