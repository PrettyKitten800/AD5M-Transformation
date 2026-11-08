import FreeCAD,Part
s=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1]
for y in [0,24,26]:
 for z in [86,87,88]:
  c=Part.makeCylinder(2.1,4,FreeCAD.Vector(25.99,y,z),FreeCAD.Vector(1,0,0));print(y,z,round(s.common(c).Volume/c.Volume,3))
