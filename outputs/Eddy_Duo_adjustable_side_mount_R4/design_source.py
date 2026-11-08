import FreeCAD as A,Part,MeshPart,json
from pathlib import Path
V=A.Vector;r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');o=r/'outputs/Eddy_Duo_adjustable_side_mount_R4';o.mkdir(exist_ok=True)
def box(y,z,dy,dz):return Part.makeBox(4,dy,dz,V(30.10,y,z))
def bore(y,z,radius,depth=10,start=27):return Part.makeCylinder(radius,depth,V(start,y,z),V(1,0,0))
# All bracket features are in one 4 mm-thick printable plane.
# The left strip uses solid material rather than the honeycomb at the sensor location.
s=box(-10,59,8,31)
s=s.fuse(box(-6,73,27.12,7))
s=s.fuse(box(-6,86,27.12,7))
for y in [6.12,16.62]:s=s.fuse(box(y-4.5,73,9,20))
s=s.removeSplitter()
# Radiused outline corners in the plate plane.
es=[e for e in s.Edges if e.BoundBox.XLength>3.99 and e.BoundBox.YLength<.001 and e.BoundBox.ZLength<.001]
used_radius=0
for radius in [1.2,.8,.5,.3]:
 try:
  f=s.makeFillet(radius,es)
  if f.isValid() and len(f.Solids)==1:s=f;used_radius=radius;break
 except:pass
for z in [64,84]:s=s.cut(bore(-6,z,1.65))
for y in [6.12,16.62]:
 cut=bore(y,78,1.65).fuse(bore(y,88,1.65)).fuse(box(y-1.65,78,3.3,10))
 # The slot connector is cut across the full plate thickness.
 cut=cut.fuse(Part.makeBox(10,3.3,10,V(27,y-1.65,78)))
 s=s.cut(cut)
# Recess ordinary M3 nuts behind the slots; channel flats prevent rotation.
for y in [6.12,16.62]:s=s.cut(Part.makeBox(2.5,5.8,16.6,V(30.10,y-2.9,74.7)))
s=s.removeSplitter();assert s.isValid() and len(s.Solids)==1
s.exportStep(str(o/'Eddy_Duo_adjustable_mount_R4.step'));ps=s.copy();ps.rotate(V(),V(0,1,0),90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin));m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.06,AngularDeflection=.18,Relative=False);m.write(str(o/'Eddy_Duo_adjustable_mount_R4.stl'))
h=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1]
check={'outline_radius_mm':used_radius,'valid_solid':s.isValid(),'closed_mesh_native':m.isSolid(),'housing_overlap_mm3':s.common(h).Volume,'housing_anchors_original_CAD_mm':[[30,-6,64],[30,-6,84]],'anchor_pitch_mm':20,'anchor_hole_diameter_mm':3.3,'sensor_slot_pitch_mm':10.5,'slot_travel_mm':10,'slot_width_mm':3.3,'plate_thickness_mm':4,'sensor_nut_channels_mm':[5.8,16.6,2.5],'nut_channel_side_wall_mm':1.6,'nut_channel_end_wall_mm':1.7,'nut_channel_front_skin_mm':1.5,'print_orientation':'sensor-contact face down, recessed nut channels up','sensor_nominal_mount_z_source_mm':82,'actual_nozzle_tip':'not established by supplied housing CAD; set physically','drilling':'two new holes in the housing solid edge; do not use the vent honeycomb','reference':'official Eddy shared-family case mesh; physical Duo should be checked'}
fractions=[]
for z in [64,84]:
 c=bore(-6,z,2.1,4,25.99);fractions.append(h.common(c).Volume/c.Volume)
check['diameter_4p2_by_4mm_insert_envelope_solid_fraction']=fractions
(o/'validation.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2),flush=True)
# Upright assembly, matching the existing EBB bracket coordinate frame.
parts=[]
for shape,col in [(h,[155,175,191]),(s,[239,153,49])]:
 sh=shape.copy();sh.rotate(V(),V(0,1,0),180);sh.translate(V(0,0,92.21775));v,f=sh.tessellate(.14);parts.append({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':col})
(o/'preview_parts.json').write_text(json.dumps(parts))
doc=A.newDocument('EddyAdjustableSideMountR4')
for name,shape in [('PRINT_AdjustableSideMount',s),('REFERENCE_BambuMod',h)]:ob=doc.addObject('PartDesign::Feature',name);ob.Shape=shape
doc.recompute();doc.saveAs(str(o/'Eddy_side_mount_assembly_R4.FCStd'))
