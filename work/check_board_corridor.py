import FreeCAD as A,Part,json
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');b=Part.read(str(r/'outputs/ebb42_mockup/EBB42_CAN_V1.1_reference.step'))
h=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1];h.rotate(A.Vector(),A.Vector(0,1,0),180);h.translate(A.Vector(0,0,92.21775))
for base in [53,60,70,80,81]:
 m=A.Matrix();m.A11=1;m.A12=0;m.A13=0;m.A14=-20;m.A21=0;m.A22=0;m.A23=-1;m.A24=.25;m.A31=0;m.A32=1;m.A33=0;m.A34=base
 pcb=b.Solids[0].copy();pcb.transformShape(m);print('base',base,'PCB overlap',pcb.common(h).Volume)
