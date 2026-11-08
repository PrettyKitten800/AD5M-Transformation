import FreeCAD as A,Part
from pathlib import Path
V=A.Vector;r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');b=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1]
for y in [6.12,16.62,-6]:
 for z in [76,80,82,84,88]:
  c=Part.makeCylinder(2.1,4,V(25.99,y,z),V(1,0,0));print(y,z,round(b.common(c).Volume/c.Volume,3),flush=True)
