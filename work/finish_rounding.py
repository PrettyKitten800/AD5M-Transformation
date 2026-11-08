from pathlib import Path
import subprocess,json,shutil,time
r=Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build');skip=[];start=time.monotonic();ok=0
for i in range(90):
 if time.monotonic()-start>105:break
 try:
  p=subprocess.run([r'C:\Program Files\FreeCAD 1.1\bin\python.exe',str(r/'work/round_one_edge.py')],cwd=r,capture_output=True,text=True,timeout=3)
  msg=p.stdout.strip()
 except subprocess.TimeoutExpired:msg='timeout'
 if 'finished' in msg:print('finished',flush=True);break
 key=r/'work/current_round_edge.json'
 if key.exists():skip.append(json.loads(key.read_text()))
 (r/'work/round_skip.json').write_text(json.dumps(skip))
 if 'ok' in msg:
  shutil.copy2(r/'work/rounded_next.step',r/'work/rounded_all.step');ok+=1
 if i%5==0:print(i,msg,'new_rounds',ok,flush=True)
print('complete',ok,'elapsed',round(time.monotonic()-start),flush=True)
