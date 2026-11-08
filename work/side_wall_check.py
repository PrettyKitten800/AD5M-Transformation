import FreeCAD,Part
s=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1]
for z in [65,68,70,72,74,78,82,86]:
 print('z',z,[(y,[x for x in [25,26,27,28,29,29.5] if s.isInside(FreeCAD.Vector(x,y,z),.001,True)]) for y in [0,3,5,10,15,20,25,28]])
