import FreeCAD as A,Part,json
from pathlib import Path
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');o=r/'outputs/Eddy_Duo_adjustable_side_mount_R3';j=Part.read(str(r/'outputs/Eddy_Duo_BambuMod_mount_R1/Drill_locator_1p6mm_R1.step'));b=Part.read(r'C:\Users\PK800\Desktop\bambumod-for-ff-adventurer-5m-model_files\bambumod_remix_and_vent_cover.step').Solids[1];print('locator housing overlap',j.common(b).Volume,flush=True)
