import FreeCAD as A,Part,json
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');s=Part.read(str(r/'work/rounded_all.step'));v,f=s.tessellate(.12);(r/'work/rounded_preview.json').write_text(json.dumps({'v':[[p.x,p.y,p.z] for p in v],'f':f,'color':[239,153,49]}))
