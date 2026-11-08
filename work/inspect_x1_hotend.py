import FreeCAD as A,Part,json
from pathlib import Path
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\reference\Bambu_X1_hotend_CAD');s=Part.read(str(out/'Bambu_X1_P1_original_hotend_Jorge.STEP'));b=s.BoundBox
r={'valid':s.isValid(),'solids':len(s.Solids),'bounds_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'size_mm':[b.XLength,b.YLength,b.ZLength],'cylinders':[]}
for face in s.Faces:
 t=face.Surface
 if isinstance(t,Part.Cylinder):
  if t.Radius<3:r['cylinders'].append({'r':t.Radius,'axis':[t.Axis.x,t.Axis.y,t.Axis.z],'center':[t.Center.x,t.Center.y,t.Center.z]})
parts=[]
for i,p in enumerate(s.Solids):
 bb=p.BoundBox;print('solid',i,'bounds',bb)
 v,f=p.tessellate(.12);parts.append({'v':[[a.x,a.y,a.z] for a in v],'f':f,'color':[[130,148,160],[80,87,94],[180,145,72]][i%3]})
(out/'inspection.json').write_text(json.dumps(r,indent=2));(out/'hotend_preview_mesh.json').write_text(json.dumps(parts));print(json.dumps(r,indent=2)[:6500])
