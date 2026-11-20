"""Build the AD5M side-interface housing and packaging assembly with native FreeCAD Python."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import FreeCAD as App
import Mesh
import MeshPart
import Part
from cradle import build as build_cradle, FRONT

V = App.Vector
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('duct', type=Path, help='Original part-fan-short-mk2.stl, desktop X1C Hotend archive')
args = parser.parse_args()

def matrix(rows):
    result = App.Matrix()
    for i, row in enumerate(rows, 1):
        for j, value in enumerate(row, 1):
            setattr(result, f'A{i}{j}', value)
    return result

def upright(shape):
    result = shape.copy()
    result.rotate(V(), V(0, 1, 0), 180)
    result.translate(V(0, 0, 92.21775))
    return result

def load_step(path):
    return Part.read(str(ROOT / path))

def pilot(radius, length, z):
    return Part.makeCylinder(radius, length, V(-30.01, -6, z), V(1, 0, 0))

def intersects_bounds(a, b):
    return a.BoundBox.intersect(b.BoundBox)

def volume(a, b):
    return round(sum(a.common(s).Volume for s in b.Solids if intersects_bounds(a, s)), 5)

stock = upright(load_step('reference/BambuMod/bambumod_remix_and_vent_cover.step').Solids[1])
hotend = load_step('reference/Bambu_X1_hotend_CAD/Bambu_X1_P1_original_hotend_Jorge.STEP')
hotend.rotate(V(), V(1, 0, 0), 90)
hotend.rotate(V(), V(0, 0, 1), 90)
hotend.translate(V(0, 12.08, -9.58))
# Use the prior nozzle seating datum. Clear only measured material intersecting the reference fins.
body = stock.cut(hotend.Solids[2])
# Local tessellation relief at a zero-thickness upstream edge.
body = body.cut(Part.makeBox(.4, 4, .4, V(-27.4, 26.5, 30.69)))
pilot_z = (8.21775, 28.21775)
wall = []
for z in pilot_z:
    # Check the entire cylinder within the wall before removing a smaller blind pilot.
    sample = Part.makeCylinder(2.1, 4.0, V(-29.99, -6, z), V(1, 0, 0))
    wall.append(round(stock.common(sample).Volume / sample.Volume, 5))
    body = body.cut(pilot(1.25, 4.03, z))
    sample = Part.makeCylinder(2.1, 4.0, V(29.98, -6, z), V(-1, 0, 0))
    wall.append(round(stock.common(sample).Volume / sample.Volume, 5))
    body = body.cut(Part.makeCylinder(1.25,4.03,V(30.01,-6,z),V(-1,0,0)))
assert body.isValid() and len(body.Solids) == 1 and min(wall) > .995
body.exportStep(str(OUT / 'Side_interface_housing_R2.step'))

plate = build_cradle()
plate.exportStep(str(OUT / 'Front_cradle_R2.step'))


eddy_mesh = Mesh.Mesh()
model = json.loads((ROOT / 'outputs/Eddy_Duo_BambuMod_mount_R1/eddy_mesh.json').read_text())
vertices = [V(-p[0]-74.3294, p[2]+FRONT+1.05158, p[1]+19.9056) for p in model['v']]
eddy_mesh.addFacets([tuple(vertices[i] for i in face) for face in model['f']])

duct_mesh = Mesh.Mesh(str(args.duct))
# Housing magnet seats at X +/-24.5, Y30.119, Z18.00. Candidate pocket axes at X +/-24.5, Y18.3.
duct_mesh.transform(matrix([[-1, 0, 0, 0], [0, 0, -1, 49.759], [0, -1, 0, 36.30]]))
# Rectangular exclusion for the installed HXH blower. Sized from the candidate pocket and screw bosses.
blower = Part.makeBox(52, 15, 52, V(-24.4, 31.0, 25.4))
fan = Part.makeBox(10, 30, 30, V(19.502, -3.63, 7.248))
fan = fan.cut(Part.makeCylinder(13.7, 11, V(19.1,11.37,22.248),V(1,0,0)))
for y in (-.63,23.37):
    for z in (10.248,34.248):
        fan = fan.cut(Part.makeCylinder(1.65, 11, V(19.1,y,z), V(1,0,0)))

doc = App.newDocument('AD5M_R2')
preview = []
def mesh_object(label, mesh, color):
    obj = doc.addObject('Mesh::Feature', 'ReferenceMesh')
    obj.Label = label
    obj.Mesh = mesh
    points, triangles = mesh.Topology
    preview.append(dict(v=[[p.x,p.y,p.z] for p in points], f=triangles, color=color, label=label))
    return obj

def cad_object(label, shape, color, display=True):
    obj = doc.addObject('Part::Feature', 'Component')
    obj.Label = label
    obj.Shape = shape
    if display:
        points, triangles = shape.tessellate(.18)
        preview.append(dict(v=[[p.x,p.y,p.z] for p in points], f=triangles, color=color, label=label))
    return obj

cad_object('R2 housing - blind accessory pilots', body, [164,181,189])
cad_object('R2 removable inline cradle', plate, [232,151,51])
cad_object('X1C hotend - nozzle reference', hotend, [158,149,127])
eddy_step = load_step('outputs/Eddy_Duo_BambuMod_mount_R1/EDDY_official.step')
eddy_step.transformShape(matrix([[-1,0,0,-74.3294],[0,0,1,FRONT+1.05158],[0,1,0,19.9056]]))
cad_object('Eddy Duo - BTT shared-family STEP',eddy_step,[62,74,86],display=False)
points, triangles = eddy_mesh.Topology
preview.append(dict(v=[[p.x,p.y,p.z] for p in points], f=triangles, color=[62,74,86],label='BTT Eddy'))
mesh_object('Part cooling duct - candidate short mk2', duct_mesh, [71,148,151])
cad_object('HXH HBB0524VD - approximate envelope', blower, [97,108,111])
cad_object('Peerless DF3010 - frame envelope', fan, [88,97,103])
# Use the existing CAD arrangement solely to illustrate the top interface.
topdoc = App.openDocument(str(ROOT/'outputs/EBB42_uniform_posts_R7/EBB42_bridge_assembly_R7.FCStd'))
for name, label, color in [('PRINT_ShortBridge','R7 example carrier - installed mount unresolved',[104,120,135]),
                           ('REFERENCE_EBB42','EBB42 V1.1 reference for V1.2.1 - example pose',[71,103,85])]:
    cad_object(label, topdoc.getObject(name).Shape.copy(), color)
App.closeDocument(topdoc.Name)
doc.recompute()
doc.saveAs(str(OUT/'Toolhead_layout_R2.FCStd'))
with open(Path(tempfile.gettempdir())/'ad5m_r2_preview.json','w') as target:
    json.dump(preview,target)
# Tessellate the exported STEP geometry in print orientation and verify using check_layout.py.
for filename, source, rotation in [('Housing_R2',OUT/'Side_interface_housing_R2.step',90),
                                   ('Front_cradle_R2',OUT/'Front_cradle_R2.step',0)]:
    printable = Part.read(str(source))
    if rotation:
        printable.rotate(V(),V(1,0,0),rotation)
    points, faces = printable.tessellate(.05)
    mesh = Mesh.Mesh([tuple(points[i] for i in tri) for tri in faces])
    mesh.translate(0,0,-mesh.BoundBox.ZMin)
    mesh.write(str(OUT / (filename+'.stl')))

def axis_interval(a, b, axis):
    return round(getattr(b,axis+'Min') - getattr(a,axis+'Max'), 3)
# A positive projected gap lower-bounds the actual part-to-part distance.
eddy_box = eddy_mesh.BoundBox
duct_box = duct_mesh.BoundBox
report = {
    'valid_housing_solids': len(body.Solids), 'housing_valid': body.isValid(),
    'pilot_solid_envelope_fractions': wall, 'anchor_z_mm': pilot_z,
    'pilot_diameter_mm': 2.5, 'nominal_pilot_depth_mm': 4.02,
    'removed_material_mm3': round(stock.Volume-body.Volume,2),
    'material_added_mm3': 0, 'housing_cradle_intersection_mm3': volume(body,plate),
    'housing_hotend_intersection_mm3': volume(body,hotend),
    'housing_3010_frame_envelope_overlap_mm3': volume(body,fan),
    'blower_envelope_cradle_overlap_mm3':volume(plate,blower),
    '3010_envelope_cradle_overlap_mm3':volume(plate,fan),
    'eddy_case_to_duct_y_gap_mm':axis_interval(duct_box,eddy_box,'Y'),
    'coil_case_midpoint_offset_magnitude_y_mm':round((eddy_box.YMin+eddy_box.YMax)/2-12.08,2),
    'frontmost_case_relative_to_nozzle_y_mm':round(eddy_box.YMax-12.08,2),
    'duct_lowest_relative_to_nozzle_mm': round(duct_box.ZMin+13.58,2),
    'eddy_lowest_relative_to_nozzle_mm':round(eddy_box.ZMin+13.58,2),
    'candidate_duct_sha256':hashlib.sha256(args.duct.read_bytes()).hexdigest(),
    'note':'See front cradle / candidate duct triangle contact and section separation checks. Duct and blower are provisional. Stock feeder/carriage and frame travel are unmeasured.'
}
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(report,flush=True)
