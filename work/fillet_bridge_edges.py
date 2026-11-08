import FreeCAD as A,Part,math
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');s=Part.read(str(r/'work/rounded_vertical.step'))
q=math.sqrt(.5)
def hole(e):
 pts=[e.valueAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*t) for t in [0,.25,.5,.75,1]]
 for x in [-27,-18,18,27]:
  if all(abs(math.hypot(p.x-x,p.y+7.498)-2.15)<.025 for p in pts):return True
 for x in [-15.5,15.5]:
  if all(abs(p.x-x)<2.95 and abs(q*((p.z-86)-(p.y-13.1))-4.5)<2.95 for p in pts):return True
 return False
edges=[e for e in s.Edges if e.Length>.5 and not hole(e)]
print('selected',len(edges),'of',len(s.Edges),flush=True)
for rad in [.5,.35,.25]:
 try:
  f=s.makeFillet(rad,edges)
  print('radius',rad,'valid',f.isValid(),len(f.Solids),flush=True)
  if f.isValid() and len(f.Solids)==1:
   f.exportStep(str(r/'work/rounded_all.step'));break
 except Exception as ex:print('failed',rad,str(ex)[:100],flush=True)
