import FreeCAD,Part,json
from pathlib import Path
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\Eddy_Duo_BambuMod_mount_R1')
for name,p in [('housing',r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step'),('eddy',str(out/'EDDY_official.step'))]:
 s=Part.read(p);print(name,'solids',len(s.Solids),'bounds',s.BoundBox)
 cylinders=[]
 for i,solid in enumerate(s.Solids):
  if name=='eddy':print('solid',i,solid.BoundBox)
  for face in solid.Faces:
   surf=face.Surface
   if isinstance(surf,Part.Cylinder):
    ax=surf.Axis;c=surf.Center;b=face.BoundBox
    cylinders.append({'solid':i,'r':round(surf.Radius,4),'axis':[round(ax.x,4),round(ax.y,4),round(ax.z,4)],'center':[round(c.x,4),round(c.y,4),round(c.z,4)],'bounds':[round(v,3) for v in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]]})
 (out/(name+'_cylinders.json')).write_text(json.dumps(cylinders,indent=2))
 if name=='housing':
  for c in cylinders:
   if c['solid']==1 and (abs(c['axis'][0])>.99 or abs(c['axis'][1])>.99) and c['r']<3:print(c)
 else:
  for c in cylinders:
   if 1.4<c['r']<1.9:print(c)
