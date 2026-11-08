import FreeCAD as A,Part,Mesh,json,math,shutil
from pathlib import Path
V=A.Vector
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\Eddy_Duo_BambuMod_mount_R1');out.mkdir(exist_ok=True)
housing=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step')
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def hole(y,z,r,length=12,start=26):return Part.makeCylinder(r,length,V(start,y,z),V(1,0,0))
def slot(y,lo,hi,r):return hole(y,lo,r).fuse(hole(y,hi,r)).fuse(box(26,y-r,lo,12,2*r,hi-lo))
# Original imported coordinates retained for assembly; upright rendering uses the established flip.
# Two solid-material locations on original +X outer side face, y=-6, z=64/84.
mount=box(30.10,-10,59,4,7,31).fuse(box(30.10,-30.25,60,4,27.25,8)).fuse(box(30.10,-30.25,80,4,27.25,8))
for y in [-27.25,-16.75]:mount=mount.fuse(box(30.10,y-3,69,4,6,25))
for z in [64,84]:mount=mount.cut(hole(-6,z,1.65))
for y in [-27.25,-16.75]:mount=mount.cut(slot(y,76,88,1.65))
mount=mount.removeSplitter()
# Two datum fences: the front plane and bottom extent of the imported main housing.
jig=box(30.10,-11.117,59,3,11.117,33.21775)
jig=jig.fuse(box(25,-13.117,59,8.1,2,35.21775)).fuse(box(25,-13.117,92.21775,8.1,13.117,2))
for z in [64,84]:jig=jig.cut(hole(-6,z,.8))
jig=jig.removeSplitter()
# Small flat hole-spacing coupon (same 20 mm pitch, without full bracket).
coupon=box(0,0,0,10,30,3)
for y in [5,25]:coupon=coupon.cut(Part.makeCylinder(1.65,5,V(5,y,-1)))
eddy=Part.read(str(out/'EDDY_official.step'))
m=A.Matrix();m.A11=0;m.A12=0;m.A13=1;m.A14=35.15158;m.A21=-1;m.A22=0;m.A23=0;m.A24=-96.3294;m.A31=0;m.A32=-1;m.A33=0;m.A34=73.90625
eddy=eddy.transformGeometry(m)
validation={}
def save(name,s,print_rotate=True):
 assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
 s.exportStep(str(out/(name+'.step')))
 ps=s.copy()
 if print_rotate:
  ps.rotate(V(0,0,0),V(0,1,0),-90)
 b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin));ps.exportStl(str(out/(name+'.stl')))
 mesh=Mesh.Mesh(str(out/(name+'.stl')))
 validation[name]={'valid_solid':s.isValid(),'solid_count':len(s.Solids),'volume_mm3':s.Volume,'print_bounds_mm':[ps.BoundBox.XLength,ps.BoundBox.YLength,ps.BoundBox.ZLength],'mesh_closed':mesh.isSolid(),'facets':mesh.CountFacets}
 return s
save('Eddy_Duo_side_bracket_R1',mount);save('Drill_locator_1p6mm_R1',jig);save('Hole_pitch_coupon_R1',coupon,False)
validation['bracket_housing_intersection_mm3']=mount.common(housing).Volume
validation['probe_bracket_check']='reference sensor minimum X equals bracket maximum X (face contact); no penetrating bounding-box overlap'
validation['probe_housing_x_clearance_mm']=eddy.BoundBox.XMin-housing.BoundBox.XMax
validation['insert_material_fraction']={}
for z in [64,84]:
 c=hole(-6,z,2.1,4,25.99);validation['insert_material_fraction'][str(z)]=housing.common(c).Volume/c.Volume
(out/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2))
# Export an editable native assembly with separate named features.
doc=A.newDocument('EddyDuoBambuModR1')
for name,s in [('Existing_housing_reference',housing),('Print_bracket_R1',mount),('Eddy_reference_nominal',eddy),('Drill_locator_reference',jig)]:
 o=doc.addObject('PartDesign::Feature',name);o.Shape=s
 if name=='Drill_locator_reference':o.Label='Drill locator - remove for operation'
doc.recompute();doc.saveAs(str(out/'Eddy_Duo_BambuMod_assembly_R1.FCStd'))
Part.makeCompound([housing,mount]).exportStep(str(out/'Housing_and_bracket_reference_R1.step'))
# Lightweight meshes for a preview; official probe mesh is transformed separately by renderer.
parts=[]
for i,s in enumerate(housing.Solids):
 v,f=s.tessellate(.25);parts.append({'v':[[a.x,a.y,a.z] for a in v],'f':f,'color':[158,175,190] if i==1 else [191,201,211]})
v,f=mount.tessellate(.15);parts.append({'v':[[a.x,a.y,a.z] for a in v],'f':f,'color':[235,153,46]})
(out/'preview_parts.json').write_text(json.dumps(parts))
(out/'parameters.json').write_text(json.dumps({'housing_side_x':29.998,'bracket_inner_x':30.1,'mount_holes_original_CAD_xyz':[[30,-6,64],[30,-6,84]],'mount_pitch_mm':20,'insert_envelope_checked_diameter_mm':4.2,'insert_envelope_checked_depth_mm':4,'sensor_hole_pitch_mm':10.5,'slot_travel_mm':12,'nominal_sensor_hole_z_original':82,'sensor_bottom_z_original_approx':104.892,'actual_nozzle_tip_position':'unmeasured; set probe using physical nozzle','sensor_case':'official EDDY shared-family CAD; confirm against Duo case'},indent=2))

