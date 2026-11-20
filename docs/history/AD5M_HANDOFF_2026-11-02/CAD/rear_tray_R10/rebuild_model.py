import sys, json, math, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for ancestor in [ROOT,*ROOT.parents]:
    if (ancestor/'work/pythonlibs').exists():
        sys.path.insert(0,str(ancestor/'work/pythonlibs'));break
import cadquery as cq
import trimesh
OUT=ROOT; OUT.mkdir(parents=True,exist_ok=True)
P={
 'width':167.0,'bottom':-30.0,'top':142.0,'plate_thickness':2.0,'standoff_height':3.0,
 'chassis_holes':[[128,6],[16,6],[153.5,15],[128,138],[16,138],[153.5,93]],
 'chassis_hole_diameter':3.3,
 'octopus_origin':[2,-24],'octopus_size':[100,160],
 'octopus_holes':[[9,-19],[99,-19],[9,131],[99,131]],'octopus_pilot':2.5,
 'pi_origin':[107,47],'pi_size':[56,85],
 'pi_holes':[[117.5,50.5],[166.5,50.5],[117.5,108.5],[166.5,108.5]],'pi_pilot':2.0,
 'mosfet_origin':[105,-21],'mosfet_size_assumed':[60,50],
 'mosfet_holes':[[114.5,-17.5],[167.5,-17.5],[114.5,25.5],[167.5,25.5]],'mosfet_pilot':2.5,
 'depth_ESTIMATED':35.0,'preferred_total_installed_height':30.0
}
# Pi orientation: 85x56 drawing rotated CCW; USB/Ethernet at top (+Y).
# Mount pattern is 58 along Y and 49 along X; holes are 3.5 mm from long edges,
# and 3.5/61.5 mm from bottom of this 85 mm oriented board.
pfile=OUT/'parameters.json'
if pfile.exists(): P.update(json.loads(pfile.read_text()))
else:pfile.write_text(json.dumps(P,indent=2))
# Recompute board mounting positions when their origins are edited.
ox,oy=P['octopus_origin']
P['octopus_holes']=[[ox+dx,oy+dy] for dx,dy in [(5,5),(95,5),(5,155),(95,155)]]
px,py=P['pi_origin']
P['pi_holes']=[[px+dx,py+dy] for dx,dy in [(3.5,3.5),(52.5,3.5),(3.5,61.5),(52.5,61.5)]]
P.setdefault('mosfet_mounting_pitch',[52.5,42.5])
mx,my=P['mosfet_origin'];mw,mh=P['mosfet_size_assumed'];sx,sy=P['mosfet_mounting_pitch']
P['mosfet_holes']=[[mx+mw/2+dx*sx/2,my+mh/2+dy*sy/2] for dy in [-1,1] for dx in [-1,1]]
pfile.write_text(json.dumps(P,indent=2))
w=P['width']; y0=P['bottom']; yt=P['top']; h=yt-y0; t=P['plate_thickness']; st=P['standoff_height']; ch=P['chassis_holes']
groups=[('Octopus',P['octopus_holes'],P['octopus_pilot']),('Pi',P['pi_holes'],P['pi_pilot']),('MOSFET_USER_DIMENSIONS',P['mosfet_holes'],P['mosfet_pilot'])]
allholes=ch+[p for _,hs,_ in groups for p in hs]
def box(x,y,dx,dy,dz,z=0):return cq.Workplane('XY').transformed(offset=(x,y,z)).box(dx,dy,dz,centered=(False,False,False))
def disk(x,y,r,z,height):return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(height)
def slab(thick):return box(0,y0,w,h,thick).edges('|Z').fillet(3)
# Skeletal plate: perimeter, rails, diagonal braces and local mounting pads.
P.setdefault('root_fillet_radius',1.5)
P.setdefault('frame_rail_width',4.0)
P.setdefault('brace_width',3.5)
P.setdefault('tie_pad_corner_radius',2.0)
rw=P['frame_rail_width'];bw=P['brace_width']
tray=slab(t).cut(box(rw,y0+rw,w-2*rw,h-2*rw,t+2,z=-1))
rails=[]
def rib(x1,y1,x2,y2,width):
 length=math.hypot(x2-x1,y2-y1)
 return cq.Workplane('XY').center((x1+x2)/2,(y1+y2)/2).slot2D(length+width,width,math.degrees(math.atan2(y2-y1,x2-x1))).extrude(t)
def add_rib(x1,y1,x2,y2,width=rw):
 global tray
 tray=tray.union(rib(x1,y1,x2,y2,width));rails.append([x1,y1,x2,y2,width])
for x in [ox+5,ox+95,px+2.5,px+53.5]:add_rib(x,y0+2,x,yt-2)
for y in [oy+5,6,py+3.5,py+61.5,oy+155,138]:add_rib(2,y,w-2,y)
# Crossbeam at the upper MOSFET mounting row.
my_top=my+mh/2+sy/2
add_rib(ox+95,my_top,w-2,my_top)
# Chassis holes on the right connect to the nearest horizontal rail.
for x,y in ch:
 tray=tray.union(disk(x,y,4.5,0,t))
 nearest=min([oy+5,6,py+3.5,py+61.5,oy+155,138,my_top],key=lambda yy:abs(yy-y))
 if abs(nearest-y)>0.01:add_rib(x,y,x,nearest)
# Triangulate the large open bays.
for x1,y1,x2,y2 in [(ox+5,oy+5,ox+95,py+3.5),(ox+95,py+3.5,ox+5,py+61.5),(ox+5,py+61.5,ox+95,oy+155),(px+3.5,py+3.5,px+52.5,py+61.5),(px+52.5,py+61.5,px+3.5,oy+155),(mx+mw/2-sx/2,my+mh/2-sy/2,mx+mw/2+sx/2,my_top)]:
 add_rib(x1,y1,x2,y2,bw)
for _,hs,_ in groups:
 for x,y in hs:tray=tray.union(disk(x,y,6,0,t))
# Tie pads are local rather than leaving a solid column of plate.
for y in [38,80,121]:tray=tray.union(box(100.25,y-9,8,18,t).edges('|Z').fillet(P['tie_pad_corner_radius']))
# Clip pads and rib end caps to the exact outer footprint.
tray=tray.intersect(slab(t)).clean()
for _,hs,_ in groups:
 for x,y in hs:tray=tray.union(disk(x,y,4,t,st))
tray=tray.clean()
roots=[e for e in tray.edges().vals() if e.geomType()=='CIRCLE' and abs(e.radius()-4)<1e-6 and abs(e.Center().z-t)<1e-6]
assert len(roots)==12,('expected twelve full standoff roots',len(roots))
tray=tray.newObject(roots).fillet(P['root_fillet_radius']).clean()
for _,hs,pilot in groups:
 for x,y in hs:tray=tray.cut(disk(x,y,pilot/2,-1,t+st+2))
for x,y in ch:tray=tray.cut(disk(x,y,P['chassis_hole_diameter']/2,-1,t+2))
ties=[]
for y in [38,80,121]:
 for yy in [y-5,y+5]:
  tray=tray.cut(box(102.75,yy-1.25,3,2.5,t+2,z=-1));ties.append([102.75,yy-1.25,3,2.5])
tray=tray.clean()
vent_rects=[] # Open bays are now formed by the rib network.
# Footprint and six chassis-hole test, printed before the full carrier.
template=slab(1.2).cut(box(5,y0+5,w-10,h-10,4,z=-1))
for x,y in ch:
 template=template.union(box(3,y-3,w-6,6,1.2)).union(disk(x,y,4,0,1.2))
for x,y in ch:template=template.cut(disk(x,y,1.65,-1,4))
template=template.clean()
# MOSFET pattern coupon for testing against the loose module, no printer disassembly.
coupon=box(0,0,60,50,1.2).edges('|Z').fillet(2)
coupon=coupon.cut(box(10,10,40,30,4,z=-1))
for x in [(60-sx)/2,(60+sx)/2]:
 for y in [(50-sy)/2,(50+sy)/2]:coupon=coupon.cut(disk(x,y,1.65,-1,4))
parts={'rear_tray_DRAFT_R10':tray,'expanded_footprint_fit_check':template,'MOSFET_52p5x42p5_pattern_check':coupon}
checks={}
for n,obj in parts.items():
 assert obj.val().isValid(),n
 assert len(obj.solids().vals())==1,n
 cq.exporters.export(obj,str(OUT/(n+'.stl')),tolerance=0.025,angularTolerance=0.12)
 cq.exporters.export(obj,str(OUT/(n+'.step')))
 m=trimesh.load(OUT/(n+'.stl'))
 assert m.is_watertight and m.is_winding_consistent and m.volume>0,n
 assert len(m.split())==1,n
 checks[n]={'valid_solid':True,'watertight':True,'single_connected_mesh':True,'bounds_mm':m.extents.tolist(),'volume_mm3':m.volume}
# Explicit hole/pitch assertions independent of solid validity.
assert math.dist(ch[0],ch[1])==112 and math.dist(ch[0],ch[3])==132
assert math.dist(P['octopus_holes'][0],P['octopus_holes'][1])==90
assert math.dist(P['octopus_holes'][0],P['octopus_holes'][2])==150
assert math.dist(P['pi_holes'][0],P['pi_holes'][1])==49
assert math.dist(P['pi_holes'][0],P['pi_holes'][2])==58
assert math.dist(P['mosfet_holes'][0],P['mosfet_holes'][1])==52.5
assert math.dist(P['mosfet_holes'][0],P['mosfet_holes'][2])==42.5
# Point-in-solid checks for all holes at their top, and support annuli.
for _,hs,pilot in groups:
 for x,y in hs:
  assert not tray.val().isInside(cq.Vector(x,y,t+st-0.5))
  assert tray.val().isInside(cq.Vector(x+3,y,t+st-0.5))
for x,y in ch:assert not tray.val().isInside(cq.Vector(x,y,t/2))
# Bounds and board-footprint checks for the narrower carrier.
# Use analytical surfaces, not the display-mesh bounding approximation.
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
exact_box=Bnd_Box()
BRepBndLib.AddOptimal_s(tray.val().wrapped,exact_box,False,False)
xb,yb,zb,xt,yy,zt=exact_box.Get()
assert abs((xt-xb)-w)<1e-6
assert abs((yy-yb)-h)<1e-6
assert abs((zt-zb)-5.0)<1e-6
# Check deck material ends at 2 mm away from mounting posts.
assert tray.val().isInside(cq.Vector(5,20,1.9))
assert not tray.val().isInside(cq.Vector(5,20,2.1))
# Verify an open passage across the entire height of every board mount.
for _,hs,_ in groups:
 for x,y in hs:
  assert not tray.val().isInside(cq.Vector(x,y,0.1))
  assert not tray.val().isInside(cq.Vector(x,y,t+st-0.1))
for _,hs,_ in groups:
 for x,y in hs:
  assert 4 <= x <= w-4 and y0+4 <= y <= yt-4
for origin,size in [(P['octopus_origin'],P['octopus_size']),(P['pi_origin'],P['pi_size']),(P['mosfet_origin'],P['mosfet_size_assumed'])]:
 assert origin[0]>=0 and origin[0]+size[0]<=w
assert P['pi_origin'][0]-(P['octopus_origin'][0]+P['octopus_size'][0])==5
assert P['mosfet_origin'][0]-(P['octopus_origin'][0]+P['octopus_size'][0])==3
checks['layout']={'width_mm':w,'height_mm':h,'plate_thickness_mm':t,'standoff_height_above_plate_mm':st,'overall_plastic_height_mm':zt-zb,'board_mount_through_hole_length_mm':t+st,'pi_to_octopus_PCB_gap_mm':5,'mosfet_to_octopus_PCB_gap_mm':3,'cable_and_connector_clearances':'unverified'}
checks['rounded_standoff_roots']={'count':len(roots),'fillet_radius_mm':P['root_fillet_radius']}
for _,hs,diameter in groups:
 for x,y in hs:
  probe=disk(x,y,diameter*0.45,-0.1,t+st+0.2)
  assert tray.intersect(probe).val().Volume()<1e-7
checks['all_board_holes_open_through']=True
checks['tie_pads']={'count':3,'outer_corner_radius_mm':P['tie_pad_corner_radius']}
checks['status']='DRAFT: printer envelope, MOSFET footprint/height, cables, cooling and fastener fit not physically validated'
(OUT/'validation.json').write_text(json.dumps(checks,indent=2))
# Visualization data, from the same CAD parameters.
(OUT/'layout_data.json').write_text(json.dumps({'parameters':P,'vents':vent_rects,'ties':ties,'rails':rails},indent=2))
print(json.dumps(checks,indent=2))
