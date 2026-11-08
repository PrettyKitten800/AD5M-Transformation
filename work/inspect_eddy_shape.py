import FreeCAD,Part,json
from pathlib import Path
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\Eddy_Duo_BambuMod_mount_R1');s=Part.read(str(out/'EDDY_official.step'));print('shells',len(s.Shells),'faces',len(s.Faces))
for face in s.Faces:
 t=face.Surface
 if isinstance(t,Part.Cylinder) and 1.4<t.Radius<1.8:print(t.Radius,t.Center,t.Axis,face.BoundBox)
v,f=s.tessellate(.2);(out/'eddy_mesh.json').write_text(json.dumps({'v':[[a.x,a.y,a.z] for a in v],'f':f}))
