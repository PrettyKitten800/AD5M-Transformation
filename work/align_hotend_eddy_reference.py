import FreeCAD as A,Part,json
from pathlib import Path
root=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');out=root/'outputs/Custom_toolhead_reference_R1';out.mkdir(exist_ok=True)
h=Part.read(str(root/'reference/Bambu_X1_hotend_CAD/Bambu_X1_P1_original_hotend_Jorge.STEP'))
m=A.Matrix();m.A11=1;m.A12=0;m.A13=0;m.A21=0;m.A22=0;m.A23=-1;m.A31=0;m.A32=1;m.A33=0;m.A34=4;h.transformShape(m)
e=Part.read(str(root/'outputs/Eddy_Duo_BambuMod_mount_R1/EDDY_official.step'))
m=A.Matrix();m.A11=0;m.A12=0;m.A13=1;m.A14=18;m.A21=1;m.A22=0;m.A23=0;m.A24=74.3294;m.A31=0;m.A32=1;m.A33=0;m.A34=33.4856;e.transformShape(m)
d=A.newDocument('Nozzle_Eddy_Nominal_Reference')
for n,s in [('Bambu_hotend_unmodified_reference',h),('Eddy_unmodified_reference',e)]:o=d.addObject('PartDesign::Feature',n);o.Shape=s
# Preserve these as independent reference parts, not modified/distributed replacement hotend geometry.
d.recompute();d.saveAs(str(out/'Nozzle_Eddy_nominal_alignment.FCStd'))
r={'nozzle_tip_nominal_xyz_mm':[0,0,0],'nozzle_tip_derivation':'0.4 mm nozzle orifice at end of creator model; original Y=-4','eddy_case_sensing_bottom_z_mm':e.BoundBox.ZMin,'nominal_target_height_mm':2.5,'eddy_width_midline_y_mm':(e.BoundBox.YMin+e.BoundBox.YMax)/2,'hotend_to_sensor_X_envelope_gap_mm':e.BoundBox.XMin-h.BoundBox.XMax,'hotend_valid':h.isValid(),'hotend_solids':len(h.Solids),'status':'component alignment reference only, no carriage or fan included; coil-center XYZ to confirm from official drawing'}
(out/'alignment.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
parts=json.loads((root/'reference/Bambu_X1_hotend_CAD/hotend_preview_mesh.json').read_text())
for p in parts:
 p['v']=[[v[0],-v[2],v[1]+4] for v in p['v']]
ep=json.loads((root/'outputs/Eddy_Duo_BambuMod_mount_R1/eddy_mesh.json').read_text());ep['v']=[[v[2]+18,v[0]+74.3294,v[1]+33.4856] for v in ep['v']];ep['color']=[65,77,85];parts.append(ep)
(out/'preview_mesh.json').write_text(json.dumps(parts))
