import FreeCAD,Part,json
from pathlib import Path
src=Path(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files')
rows=[]
for p in src.glob('*.step'):
 s=Part.read(str(p));b=s.BoundBox
 r={'file':p.name,'valid':s.isValid(),'solids':len(s.Solids),'bounds_mm':[b.XLength,b.YLength,b.ZLength],'solid_details':[]}
 for solid in s.Solids:
  bb=solid.BoundBox;r['solid_details'].append({'bounds_mm':[bb.XLength,bb.YLength,bb.ZLength],'volume_mm3':solid.Volume})
 rows.append(r)
print(json.dumps(rows,indent=2))
Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\bambumod_inspection\cad_inspection.json').write_text(json.dumps(rows,indent=2))
