import FreeCAD as A,Part,json
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');s=Part.read(str(r/'outputs/EBB42_sketch_bridge_R4/EBB42_short_bridge_R4.step'))
print('edges',len(s.Edges),flush=True)
rows=[]
for i,e in enumerate(s.Edges):
 b=e.BoundBox;vs=[v.Point for v in e.Vertexes]
 rows.append({'i':i,'length':e.Length,'type':type(e.Curve).__name__,'box':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
(r/'work/R4_edges.json').write_text(json.dumps(rows,indent=2))
vertical=[e for e in s.Edges if type(e.Curve).__name__=='Line' and e.Length>2 and e.BoundBox.XLength<.001 and e.BoundBox.YLength<.001]
print('vertical',len(vertical),flush=True)
for rad in [1.2,.8,.5]:
 try:
  f=s.makeFillet(rad,vertical)
  print('radius',rad,'valid',f.isValid(),len(f.Solids),flush=True)
  if f.isValid() and len(f.Solids)==1:
   f.exportStep(str(r/'work/rounded_vertical.step'));break
 except Exception as ex:print('failed',rad,str(ex)[:80],flush=True)
