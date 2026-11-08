import FreeCAD as A,Part,Mesh,json
from pathlib import Path
out=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\outputs\Eddy_Duo_BambuMod_mount_R1')
jig=Part.read(str(out/'Drill_locator_1p6mm_R1.step'));jig.rotate(A.Vector(),A.Vector(0,1,0),90);b=jig.BoundBox;jig.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));jig.exportStl(str(out/'Drill_locator_1p6mm_R1.stl'))
for n in ['Eddy_Duo_side_bracket_R1','Drill_locator_1p6mm_R1','Hole_pitch_coupon_R1']:
 s=Part.read(str(out/(n+'.step')));m=Mesh.Mesh(str(out/(n+'.stl')));print(n,'STEP valid',s.isValid(),'solids',len(s.Solids),'closed STL',m.isSolid())
