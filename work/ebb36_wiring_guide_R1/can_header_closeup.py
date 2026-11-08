from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[2]
out=root/'outputs/EBB36_wiring_guide_R1'
out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1500,1120),'white')
d=ImageDraw.Draw(im)
navy='#172C3F'; blue='#1764A0'; teal='#007D80'; red='#B52730'; amber='#966112'; muted='#4D6272'; pale='#F1F5F8'
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
def t(x,y,s,n=25,col=navy,b=False):d.text((x,y),s,font=font(n,b),fill=col)
def leader(points,col):
    d.line(points,fill='white',width=11,joint='curve')
    d.line(points,fill=col,width=5,joint='curve')
    x,y=points[-1];d.ellipse((x-6,y-6,x+6,y+6),fill=col)

t(42,25,'EBB36 TO OCTOPUS PRO V1.1',37,navy,True)
t(42,80,'Four cable conductors split into CAN data and a separate 24 V power branch.',26,muted)
d.line((42,130,1458,130),fill='#CCD6DE',width=2)

t(42,158,'EBB36: board-front contact order',29,navy,True)
t(42,203,'USB-C at upper right, as in your board photo.',23,muted)
for col,row,label,desc,c in [(0,0,'GND','Common PSU V-',navy),(1,0,'VIN','Protected +24 V',red),
                             (0,1,'CAN L','To Octopus upper CAN contact',teal),(1,1,'CAN H','To Octopus lower CAN contact',blue)]:
    x=42+col*327;y=258+row*140
    d.rounded_rectangle((x,y,x+313,y+126),radius=8,fill=pale)
    t(x+18,y+14,label,34,c,True)
    if label.startswith('CAN'):
        t(x+18,y+65,'To Octopus '+('upper' if label=='CAN L' else 'lower'),22)
        t(x+18,y+92,'CAN contact',22)
    else:t(x+18,y+72,desc,23)
t(42,548,'This is the board view. Verify the mating plug',23,amber)
t(42,580,'with continuity; its wire-entry view can be mirrored.',23,amber)

t(757,158,'Octopus Pro V1.1: lower-right corner',29,navy,True)
t(757,203,'Orient the board: motor sockets across the top,',23,muted)
t(757,232,'power screw terminals on the left.',23,muted)
src=Image.open(root/'reference/octopus_v11/official_pinout.jpg').convert('RGB')
crop=src.crop((1430,815,1660,1115)).resize((345,450),Image.Resampling.LANCZOS)
ix,iy=815,282
im.paste(crop,(ix,iy))

# Verified against BTT's V1.1 pinout: vertical CAN socket, L above H.
upper=(ix+(1607-1430)*1.5,iy+(912-815)*1.5)
lower=(ix+(1607-1430)*1.5,iy+(935-815)*1.5)
jump=(ix+(1507-1430)*1.5,iy+(915-815)*1.5)
leader([(1192,387),(1158,387),upper],teal)
t(1192,349,'UPPER',23,teal,True);t(1192,381,'CAN L',31,teal,True)
leader([(1192,508),(1158,508),lower],blue)
t(1192,473,'LOWER',23,blue,True);t(1192,505,'CAN H',31,blue,True)
leader([(1180,657),(1110,657),(1020,600),jump],amber)
t(1192,615,'120R',28,amber,True)
t(1192,650,'jumper',25,amber)
t(1192,690,'Fit at this',22,amber)
t(1192,720,'CAN bus end.',22,amber)

t(42,666,'Rear cable split',29,navy,True)
rows=[('EBB VIN','Fused +24 V branch at the distribution junction',red),
      ('EBB GND','PSU V- / shared ground at that junction',navy),
      ('EBB CAN H','Octopus CAN H (lower contact in this view)',blue),
      ('EBB CAN L','Octopus CAN L (upper contact in this view)',teal)]
for i,(a,b,c) in enumerate(rows):
    y=721+i*55
    t(42,y,a,24,c,True)
    d.line((231,y+19,291,y+19),fill=c,width=4)
    t(309,y,b,23)

d.line((42,965,1458,965),fill='#CCD6DE',width=2)
t(42,986,'Unplug printer power and USB before wiring. Keep CAN H/L twisted together.',24,navy,True)
t(42,1024,'Fit one 120 Ohm termination at each end: Octopus and EBB. Unpowered bus: about 60 Ohm across H/L.',23,navy)
t(42,1070,'BTT V1.1 Octopus / V1.1-V1.2 EBB pinouts | Nov 3, 2026 | Colors identify functions, not your cable colors.',20,muted)
target=out/'CAN_harness_to_Octopus_Pro_V11.png'
im.save(target)
print(target)
