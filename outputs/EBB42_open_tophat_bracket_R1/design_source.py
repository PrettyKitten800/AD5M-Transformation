import FreeCAD as A,Part,Mesh,MeshPart,json,math
from pathlib import Path
V=A.Vector
root=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');out=root/'outputs/EBB42_open_tophat_bracket_R1';out.mkdir(exist_ok=True)
source=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step')
body=source.Solids[1].copy();body.rotate(V(),V(0,1,0),180);body.translate(V(0,0,92.21775))
cap=source.Solids[0].copy();cap.rotate(V(),V(0,1,0),180);cap.translate(V(0,0,92.21775))
q=math.sqrt(.5);m=A.Matrix();m.A11=1;m.A12=0;m.A13=0;m.A14=-20;m.A21=0;m.A22=-q;m.A23=-q;m.A24=-17;m.A31=0;m.A32=q;m.A33=-q;m.A34=64
# This maps the board component normal outward/downward and its upper edge away from the filament inlet.
def placed(s):r=s.copy();r.transformShape(m);return r
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(x,y,z,r,L,axis):return Part.makeCylinder(r,L,V(x,y,z),V(*axis))
anchor_z=92.21775-31.215
s=box(-29,-15.217,anchor_z-5,58,4,10)
for x in [-24,24]:s=s.fuse(box(x-3,-15.217,anchor_z,6,4,92-anchor_z))
# Reuse stock clip above the open central volume, below the previous cap's maximum height.
s=s.fuse(box(-29,-17.0895,88,58,8,4))
carrier=box(1.5,1.5,-7.5,6,32.5,3).fuse(box(32.5,1.5,-7.5,6,32.5,3)).fuse(box(1.5,1.5,-7.5,37,6,3))
s=s.fuse(placed(carrier))
for x in [-15.5,15.5]:s=s.fuse(box(x-3,-20,62,6,8.65,16))
# Remove a conservative full component/backside envelope, then add corner-only mounting posts.
s=s.cut(placed(box(-.2,-.5,-4,40.4,42,18)))
for x in [4.5,35.5]:s=s.fuse(placed(cyl(x,4.5,-4.5,3,3.85,(0,0,1))))
for x in [-24,24]:s=s.cut(cyl(x,-18,anchor_z,2.2,10,(0,1,0)))
for x in [4.5,35.5]:s=s.cut(placed(cyl(x,4.5,-16,1.65,19,(0,0,1))))
for x in [-7.25,7.25]:s=s.cut(cyl(x,-13.0895,86,1.65,9,(0,0,1)))
s=s.removeSplitter();print('BRACKET',s.isValid(),len(s.Solids),s.BoundBox)
assert s.isValid() and len(s.Solids)==1
s.exportStep(str(out/'Open_EBB42_45deg_bracket_R1.step'))
ps=s.copy();b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=MeshPart.meshFromShape(Shape=ps,LinearDeflection=0.08,AngularDeflection=0.2,Relative=False);mesh.write(str(out/'Open_EBB42_45deg_bracket_R1.stl'))
# Flat six-hole fit coupon, unrelated to installed orientation.
c=box(-29,0,0,58,30,2)
for xs,y,r in [([-24,24],5,2.2),([-15.5,15.5],15,1.65),([-7.25,7.25],25,1.65)]:
 for x in xs:c=c.cut(cyl(x,y,-1,r,4,(0,0,1)))
c.exportStep(str(out/'Six_hole_spacing_coupon.step'));c.translate(V(29,0,0));c.exportStl(str(out/'Six_hole_spacing_coupon.stl'))
boardshape=Part.read(str(root/'outputs/ebb42_mockup/EBB42_CAN_V1.1_reference.step'));board=placed(Part.makeCompound([a for i,a in enumerate(boardshape.Solids) if i not in [1667,1669,1671,1673]]))
validation={'valid_solid':s.isValid(),'solid_count':len(s.Solids),'closed_mesh':mesh.isSolid(),'volume_mm3':s.Volume,'print_envelope_mm':[ps.BoundBox.XLength,ps.BoundBox.YLength,ps.BoundBox.ZLength],'housing_intersection_mm3':s.common(body).Volume,'board_to_housing_Y_envelope_gap_mm':'tilted assembly; visual and sampled checks separately','reference_old_cap_top_z_mm':cap.BoundBox.ZMax,'bracket_top_z_mm':s.BoundBox.ZMax,'board_top_z_mm':board.BoundBox.ZMax,'clip_top_z_mm':95,'physical_validation':'not performed'}
(out/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2))
params={'board_angle_from_vertical_deg':45,'lean_direction':'upper edge away from filament inlet, toward negative source Y','housing_pair_pitch_mm':48,'housing_clearance_diameter_mm':4.4,'housing_anchor_xyz_mm':[[-24,-11.117,anchor_z],[24,-11.117,anchor_z]],'EBB42_pair_pitch_mm':31,'board_hole_diameter_mm':3.3,'board_back_post_height_mm':3.85,'board_mount_selection':'two lower-row holes at local (4.5,4.5) and (35.5,4.5)','clip_pitch_mm':14.5,'clip_hole_diameter_mm':3.3,'clip_source':'cable-clip.stl in user-supplied BambuMod folder; two measured hole centers 14.501 mm apart, slight 0.061 mm fore-aft difference rounded to common centerline','stock_clip_fit':'verify actual stock clip matches supplied model','hardware_note':'M4 class carriage attachment; M3 board and clip clearance holes; match actual original housing fasteners','board_model':'official EBB42 V1.1 CAD reference for original V1.2.1 board; exact physical connector envelope must be checked'}
(out/'parameters.json').write_text(json.dumps(params,indent=2))
doc=A.newDocument('OpenEBB42Bracket45deg')
for n,shape in [('PRINT_OpenBracket',s),('Existing_BambuMod_body_reference',body),('EBB42_reference_no_long_spacers',board)]:o=doc.addObject('PartDesign::Feature',n);o.Shape=shape
doc.recompute();doc.saveAs(str(out/'Open_EBB42_bracket_assembly_R1.FCStd'))
Part.makeCompound([s,body]).exportStep(str(out/'Bracket_and_BambuMod_reference.step'))
parts=[]
for shape,color in [(body,[155,175,191]),(s,[233,151,45])]:
 v,f=shape.tessellate(.18);parts.append({'v':[[a.x,a.y,a.z] for a in v],'f':f,'color':color})
(out/'preview_parts.json').write_text(json.dumps(parts))
