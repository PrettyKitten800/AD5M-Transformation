import FreeCAD,Part,math
s=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1]
for z in range(40,89,4):
 good=[]
 for y in range(-8,31,2):
  if all(s.isInside(FreeCAD.Vector(x,y+2.1*math.cos(a),z+2.1*math.sin(a)),.001,True) for x in [26.1,28,29.9] for a in [0,math.pi/2,math.pi,math.pi*1.5]):good.append(y)
 print(z,good)
