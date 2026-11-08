from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
out=Path(__file__).resolve().parents[2]/'outputs/ebb42_mockup'
try:
 font=ImageFont.truetype('DejaVuSans.ttf',22)
except OSError:
 font=ImageFont.load_default(size=22)
def draw(parts,path,views):
 im=Image.new('RGB',(1400,1050),'#edf1f5');d=ImageDraw.Draw(im)
 for j,(label,az,el) in enumerate(views):
  x0=(j%2)*700;y0=(j//2)*525
  az=np.radians(az);el=np.radians(el);right=np.array([np.cos(az),np.sin(az),0]);up=np.array([-np.sin(az)*np.sin(el),np.cos(az)*np.sin(el),np.cos(el)]);dep=np.cross(right,up);R=np.array([right,up,dep]).T
  allp=np.concatenate([np.array(p['v'])@R for p in parts]);mi=allp.min(0);ma=allp.max(0);sc=min(600/(ma[0]-mi[0]),410/(ma[1]-mi[1]));c=(mi+ma)/2;faces=[]
  for part in parts:
   v=np.array(part['v']);pr=v@R;f=np.array(part['f']);norm=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-10)
   light=np.abs(norm@np.array([.3,-.5,.8]));base=part.get('color',[175,185,195])
   for k,tri in enumerate(f):
    pts=pr[tri];xy=[(x0+350+(a[0]-c[0])*sc,y0+290-(a[1]-c[1])*sc) for a in pts];col=tuple(int(v*(.55+.45*light[k])) for v in base);faces.append((pts[:,2].mean(),xy,col))
  for z,xy,col in sorted(faces,key=lambda t:t[0]):d.polygon(xy,fill=col)
  d.text((x0+25,y0+20),label,font=font,fill='#172b40')
 im.save(path)
if __name__=='__main__':
 parts=json.loads((out/'housing.json').read_text());draw(parts,out/'housing_views.png',[('+Y view',0,0),('-Y view',180,0),('Isometric A',-35,25),('Isometric B',145,25)])
