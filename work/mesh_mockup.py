import FreeCAD,Part,json
from pathlib import Path
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\ebb42_mockup')
paths=[Path(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step'),out/'EBB42_CAN_V1.1_reference.step']
for name,p in zip(['housing','board'],paths):
 s=Part.read(str(p));r=[]
 for solid in s.Solids:
  v,f=solid.tessellate(0.18);b=solid.BoundBox
  r.append({'v':[[a.x,a.y,a.z] for a in v],'f':f,'bounds':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
 (out/(name+'.json')).write_text(json.dumps(r));print(name,len(r),[a['bounds'] for a in r][:8])
