import FreeCAD as A, Part, MeshPart, json, math
from pathlib import Path
V=A.Vector
root=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build')
out=root/'outputs/EBB42_uniform_posts_R7';out.mkdir(exist_ok=True)
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)): return Part.makeCylinder(r,h,V(x,y,z),V(*axis))
source=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step')
body=source.Solids[1].copy();body.rotate(V(),V(0,1,0),180);body.translate(V(0,0,92.21775))
angle=45.;sn=math.sin(math.radians(angle));cs=math.cos(math.radians(angle))
m=A.Matrix();m.A11=1;m.A12=0;m.A13=0;m.A14=-20
m.A21=0;m.A22=-sn;m.A23=-cs;m.A24=13.1
m.A31=0;m.A32=cs;m.A33=-sn;m.A34=86.0
def placed(shape):
 s=shape.copy();s.transformShape(m);return s
base=80.1515
# Rounded base, mounting positions unchanged.
s=box(-30,-11,base,60,8,4)
for x in [-30,14.35]:s=s.fuse(box(x,-11,base,15.65,29,4))
for x in [-20,11.5]:s=s.fuse(box(x,12,base,8.5,12,4))
for x in [-18,18]:s=s.fuse(cyl(x,-7.498,base,4,4))
s=s.removeSplitter()
for radius in [.8,.5,.3]:
 try:
  f=s.makeFillet(radius,s.Edges)
  if f.isValid() and len(f.Solids)==1:s=f;break
 except:pass
# One constant 6.6 mm extrusion per angled post, matching the previous contact width.
for x in [-18.8,12.2]:
 poly=[V(x,100.01924-base,base),V(x,24,base),V(x,24,98),V(x,12,98),V(x,8.01924,92),V(x,100.01924-base,base)]
 post=Part.Face(Part.makePolygon(poly)).extrude(V(6.6,0,0))
 post=post.removeSplitter()
 for radius in [.6,.4,.25]:
  try:
   f=post.makeFillet(radius,post.Edges)
   if f.isValid() and len(f.Solids)==1:post=f;break
  except:pass
 s=s.fuse(post)
# Sharp hole rims cut after rounding, M3 pilots per the user's latest specification.
for x in [-27,-18,18,27]:s=s.cut(cyl(x,-7.498,base-1,2.15,7))
for x in [4.5,35.5]:s=s.cut(placed(cyl(x,4.5,-20,1.25,24)))
s=s.removeSplitter()
print('SOLIDS',[(a.Volume,str(a.BoundBox)) for a in s.Solids],flush=True)
assert s.isValid() and len(s.Solids)==1, (s.isValid(),len(s.Solids))
s.exportStep(str(out/'EBB42_short_bridge_R7.step'))
ps=s.copy();b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
mesh=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.06,AngularDeflection=.18,Relative=False)
mesh.write(str(out/'EBB42_short_bridge_R7.stl'))
board_source=Part.read(str(root/'outputs/ebb42_mockup/EBB42_CAN_V1.1_reference.step'))
board=placed(Part.makeCompound([a for i,a in enumerate(board_source.Solids) if i not in [1667,1669,1671,1673]]))
def intersects(a,b):
 aa=a.BoundBox;bb=b.BoundBox
 return aa.XMax>bb.XMin and aa.XMin<bb.XMax and aa.YMax>bb.YMin and aa.YMin<bb.YMax and aa.ZMax>bb.ZMin and aa.ZMin<bb.ZMax
clashes=[];housing_clashes=[]
for i,a in enumerate(board_source.Solids):
 if i in [1667,1669,1671,1673]:continue
 a=placed(a)
 if intersects(s,a):
  v=s.common(a).Volume
  if v>.002:clashes.append([i,round(v,4)])
 if intersects(body,a):
  v=body.common(a).Volume
  if v>.002:housing_clashes.append([i,round(v,4)])
bb=board.BoundBox
validation={'valid_solid':s.isValid(),'solid_count':len(s.Solids),'closed_mesh':mesh.isSolid(),'volume_mm3':s.Volume,'print_envelope_mm':[ps.BoundBox.XLength,ps.BoundBox.YLength,ps.BoundBox.ZLength],'housing_overlap_mm3':s.common(body).Volume,'board_bracket_clashes':clashes,'board_housing_clashes':housing_clashes,'board_bounds':[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax],'board_extra_height_over_old_cover_mm':bb.ZMax-96.21775,'rear_extension_from_housing_reference_mm':-11.117-bb.YMin,'angle_from_vertical_deg':angle,'physical_fit':'unverified; original feeder/motor, stock bearing carriage and frame are absent from supplied housing CAD','strain_relief':'removed; no clip geometry or holes'}
(out/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2),flush=True)
doc=A.newDocument('EBB42SketchBridgeR7')
for name,shape in [('PRINT_ShortBridge',s),('REFERENCE_BambuMod',body),('REFERENCE_EBB42',board)]:
 o=doc.addObject('PartDesign::Feature',name);o.Shape=shape
doc.recompute();doc.saveAs(str(out/'EBB42_bridge_assembly_R7.FCStd'))
parts=[]
for shape,color in [(body,[155,175,191]),(s,[239,153,49])]:
 v,f=shape.tessellate(.14);parts.append({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':color})
(out/'preview_parts.json').write_text(json.dumps(parts))
(out/'placement.json').write_text(json.dumps({'angle':angle,'sin':sn,'cos':cs,'board_base_y':13.1,'board_base_z':86.0,'base_z':base},indent=2))
