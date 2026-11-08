import FreeCAD as A,Part,math,json,time
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');s=Part.read(str(r/'work/rounded_all.step'));q=math.sqrt(.5)
def hole(e):
 pts=[e.valueAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*t) for t in [0,.25,.5,.75,1]]
 for x in [-27,-18,18,27]:
  if all(abs(math.hypot(p.x-x,p.y+7.498)-2.15)<.025 for p in pts):return True
 for x in [-15.5,15.5]:
  if all(abs(p.x-x)<2.95 and abs(q*((p.z-86)-(p.y-13.1))-4.5)<2.95 for p in pts):return True
 return False

def sharp(shape):
 rows=[]
 for e in shape.Edges:
  if e.Length<.08 or hole(e):continue
  fs=shape.ancestorsOfType(e,Part.Face)
  if len(fs)!=2:continue
  p=e.valueAt((e.FirstParameter+e.LastParameter)/2)
  try:
   ns=[]
   for f in fs:
    u,v=f.Surface.parameter(p);ns.append(f.normalAt(u,v))
   if ns[0].dot(ns[1])>.999:continue
  except:continue
  rows.append(e)
 return sorted(rows,key=lambda e:-e.Length)

skipfile=r/'work/round_skip.json'
skips=json.loads(skipfile.read_text()) if skipfile.exists() else []
for e in sharp(s):
 c=e.CenterOfMass;k=[round(v,4) for v in [c.x,c.y,c.z,e.Length]]
 if k in skips:continue
 (r/'work/current_round_edge.json').write_text(json.dumps(k))
 for radius in [.3,.15,.075]:
  try:
   f=s.makeFillet(radius,[e])
   if f.isValid() and len(f.Solids)==1:
    f.exportStep(str(r/'work/rounded_next.step'));print('ok',radius,flush=True);break
  except:pass
 else:print('failed',flush=True)
 break
else:print('finished',flush=True)
