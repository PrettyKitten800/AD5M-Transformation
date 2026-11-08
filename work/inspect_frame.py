import FreeCAD,Part
p=r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\reference\AD5M_gantry_research\official_frame_model\AD5M_Frame.STEP'
s=Part.read(p)
print('SOLID BOUNDING BOX LENGTHS mm')
for i,a in enumerate(s.Solids):
 b=a.BoundBox
 print(i,round(b.XLength,2),round(b.YLength,2),round(b.ZLength,2))

