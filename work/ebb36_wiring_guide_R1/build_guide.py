from pathlib import Path
from math import cos, pi
import hashlib
import json

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/ebb36_wiring_guide_R1'
OUT = ROOT / 'outputs/EBB36_wiring_guide_R1'
PDFDIR = ROOT / 'output/pdf'
REF = ROOT / 'reference/ebb36_btt'
OUT.mkdir(parents=True, exist_ok=True)
PDFDIR.mkdir(parents=True, exist_ok=True)

W, H = 792, 612
INK = HexColor('#172C3F')
MUTED = HexColor('#4D6272')
RULE = HexColor('#CCD6DE')
PALE = HexColor('#F1F5F8')
BLUE = HexColor('#1764A0')
TEAL = HexColor('#007D80')
RED = HexColor('#B52730')
PURPLE = HexColor('#71549A')
AMBER = HexColor('#966112')
AMBER_BG = HexColor('#FFF5DF')
GREEN = HexColor('#23724F')

for name, path in [('Guide', 'C:/Windows/Fonts/segoeui.ttf'), ('GuideBold', 'C:/Windows/Fonts/segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(name, path))

PDF = PDFDIR / 'EBB36_toolhead_wiring_R1.pdf'
C = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
C.setTitle('AD5M - EBB36 Toolhead Wiring Guide R1')
C.setAuthor('AD5M Build')
C.setSubject('BTT EBB36 CAN V1.2.1 without MAX31865 - project-specific wiring preparation')

def txt(x, y, s, size=11.5, color=INK, bold=False):
    C.setFillColor(color)
    C.setFont('GuideBold' if bold else 'Guide', size)
    C.drawString(x, H-y-size*.82, s)

def para(x, y, width, s, size=11.2, color=INK, leading=None):
    st = ParagraphStyle('p', fontName='Guide', fontSize=size, leading=leading or size*1.34,
                        textColor=color, spaceAfter=0)
    # Registering a family makes Paragraph bold use the correct font.
    pr = Paragraph(s, st)
    _, height = pr.wrap(width, 1000)
    assert y+height < H-24, (s[:60], y, height)
    pr.drawOn(C, x, H-y-height)
    return height

pdfmetrics.registerFontFamily('Guide', normal='Guide', bold='GuideBold', italic='Guide', boldItalic='GuideBold')

def rect(x, y, w, h, fill=PALE, stroke=None, radius=5):
    C.setFillColor(fill or white)
    C.setStrokeColor(stroke or fill or white)
    C.setLineWidth(.8)
    C.roundRect(x, H-y-h, w, h, radius, fill=bool(fill), stroke=bool(stroke))

def line(points, color=INK, width=1.5, dash=None):
    C.saveState()
    C.setStrokeColor(color)
    C.setLineWidth(width)
    if dash:
        C.setDash(dash)
    p = C.beginPath()
    p.moveTo(points[0][0], H-points[0][1])
    for x,y in points[1:]:
        p.lineTo(x, H-y)
    C.drawPath(p)
    C.restoreState()

def dot(x, y, color=INK, r=2.5):
    C.setFillColor(color)
    C.circle(x, H-y, r, stroke=0, fill=1)

def badge(x, y, s, color=BLUE, r=11):
    C.setFillColor(color)
    C.circle(x, H-y, r, stroke=0, fill=1)
    C.setFont('GuideBold', 11)
    C.setFillColor(white)
    C.drawCentredString(x, H-y-3.7, s)

def image(path, x, y, w, h=None, crop=None):
    im = Image.open(path).convert('RGB')
    if crop:
        im = im.crop(crop)
    h = h or w*im.height/im.width
    C.drawImage(ImageReader(im), x, H-y-h, w, h, mask='auto')
    return w,h

def heading(n, title, subtitle):
    C.setFillColor(white)
    C.rect(0,0,W,H,fill=1,stroke=0)
    txt(34, 21, 'AD5M / TOOLHEAD WIRING', 9.5, BLUE, True)
    txt(34, 44, title, 24, INK, True)
    txt(34, 79, subtitle, 11, MUTED)
    line([(34,105),(758,105)], RULE, .8)

def note(x, y, w, s, amber=False, height=36):
    rect(x,y,w,height,AMBER_BG if amber else PALE)
    para(x+12,y+9,w-24,s,10.5,AMBER if amber else INK,13.2)

def footer(n, refs):
    line([(34,573),(758,573)], RULE, .65)
    txt(34,582,'R1 / Nov 3, 2026 / EBB36 CAN V1.2.1 / assembly preparation',8.5,MUTED)
    C.setFont('Guide',8.5)
    C.drawRightString(758,H-589,f'{refs}   |   {n} / 7')
    C.showPage()

def checklist(x,y,width,items,size=11.2,gap=33):
    for i,s in enumerate(items):
        yy=y+i*gap
        C.setStrokeColor(MUTED)
        C.setLineWidth(.9)
        C.rect(x,H-yy-10,9,9,fill=0,stroke=1)
        para(x+18,yy-1,width-18,s,size)

def source_link(x,y,label,url,size=9.5):
    txt(x,y,label,size,BLUE)
    width=pdfmetrics.stringWidth(label,'Guide',size)
    C.linkURL(url,(x,H-y-size-1,x+width,H-y+2),relative=0,thickness=0)

PHOTO = WORK / 'actual_board_front.png'
orig = Image.open(ROOT/'AD5M_HANDOFF_2026-11-02/Photos/boards_and_carrier/5-Photo-5.jpg')
scale=orig.width/1368
orig.crop(tuple(round(v*scale) for v in (380,695,1130,1225))).save(PHOTO)

# 1. The real board, with indexed locations rather than a generated PCB picture.
heading(1,'Your EBB36 toolhead map','Your photographed board / first-generation V1.1-V1.2 documentation / no MAX31865')
note(34,117,724,'Before assembly: unplug printer power and USB. Change plugs and jumpers only with both removed.',height=34)
px,py,pw,ph=34,168,438,310
image(PHOTO,px,py,pw,ph)
points=[('1',.54,.22,.63,.10,BLUE),('2',.16,.14,.07,.06,BLUE),
        ('3',.74,.79,.89,.81,BLUE),('4',.35,.77,.27,.91,BLUE),
        ('5',.45,.86,.43,.97,BLUE),('6',.57,.86,.64,.97,AMBER),
        ('7',.16,.71,.05,.78,BLUE)]
for num,tx,ty,bx,by,col in points:
    target=(px+pw*tx,py+ph*ty)
    bpos=(px+pw*bx,py+ph*by)
    line([bpos,target],white,3.5)
    line([bpos,target],col,1.6)
    dot(*target,col,2.6)
    badge(*bpos,num,col,10)
entries=[('1','Power + CAN','24 V, GND, CAN H, CAN L / page 5'),
         ('2','Extruder motor','E0 / EM four-contact plug / page 3'),
         ('3','X1C heater','Green E0 / HE0 screw pair / page 2'),
         ('4','X1C thermistor','TH0 / PA3 / page 2'),
         ('5','Two-wire hotend fan','PA0 / BTT FAN1 / page 2'),
         ('6','Four-wire blower','PA1 reserved; hold connection / page 6'),
         ('7','X + Y Hall sensors','Five-contact ENDSTOP / page 4')]
for i,(n,title,body) in enumerate(entries):
    yy=169+i*43
    badge(502,yy+10,n,AMBER if n=='6' else BLUE,9)
    txt(520,yy,title,12,INK,True)
    para(520,yy+18,236,body,10.1,MUTED,12.5)
txt(34,499,'Assembly order',11,BLUE,True)
for i,(a,b) in enumerate([('1 / Hotend leads','Heater, thermistor, hotend fan'),('2 / Motor + sensors','Measure coils; label Hall leads'),('3 / Main harness','24 V, GND and twisted CAN pair'),('4 / Inspect + test','Jumpers, continuity, staged power')]):
    x=34+i*184
    txt(x,520,a,11.5,INK,True)
    para(x,538,171,b,9.7,MUTED,12)
footer(1,'B1-B3 + project photo')

# 2. Show the physical lower connectors, then provide each exact assignment.
heading(2,'Wire the three hotend circuits','Bambu X1C heater + thermistor / Peerless DF3010B24H hotend fan, 24 V, 0.09 A')
txt(34,120,'Board front, same orientation as page 1. Upper contacts point toward the MCU.',10.8,MUTED)
cx,cy,cw,ch=97,146,580,220
crop=(380,720,1260,1054)
image(PHOTO,cx,cy,cw,ch,crop=crop)
def bottom_point(x,y):
    return (cx+(x-crop[0])*cw/(crop[2]-crop[0]),cy+(y-crop[1])*ch/(crop[3]-crop[1]))
for lab,coord,bpos,col in [('TH0',(530,875),(123,359),BLUE),('PA0',(715,951),(318,359),BLUE),
                           ('PA1',(905,951),(485,359),AMBER),('HE0',(1178,883),(672,359),BLUE)]:
    target=bottom_point(*coord)
    line([bpos,target],white,3.5)
    line([bpos,target],col,1.5)
    rect(bpos[0]-24,bpos[1]-10,48,20,col,radius=3)
    txt(bpos[0]-18,bpos[1]-6,lab,10,white,True)

colw=232
for x,title in [(34,'X1C heater'),(280,'X1C thermistor'),(526,'Hotend fan')]:
    txt(x,391,title,14,INK,True)
    line([(x,414),(x+colw,414)],RULE,.8)
para(34,425,232,'<b>Green E0 / HE0 terminal</b><br/>One heater lead in each clamp.<br/>The heater pair has no polarity.',11.2)
para(34,488,232,'Control: <b>EBBCan:PB13</b><br/>Use a sound wire/ferrule termination; no solder-tinned strands in the clamp.',10.8)
para(280,425,232,'<b>TH0, two-contact plug</b><br/>Upper contact: <b>PA3</b><br/>Lower contact: <b>GND</b>',11.2)
para(280,488,232,'One thermistor lead per contact; no polarity. PT1000 jumper stays <b>open</b> for the planned NTC connection.',10.8)
para(526,425,232,'<b>PA0 / FAN1, two-contact plug</b><br/>Upper: <b>PA0 / black fan negative</b><br/>Lower: <b>VIN / red fan positive</b>',11.2)
para(526,488,232,'This build uses PA0 for hotend cooling. Configure it as the hotend fan; BTT\'s example assigns it differently.',10.8)
footer(2,'B1-B3; X1C sensor curve still pending')

# 3. Motor schematic numbers must not be misrepresented as known cavity orientation.
heading(3,'Identify the extruder motor coils','Use the EBB36 onboard driver / measure with the motor unplugged from the board')
image(PHOTO,34,135,252,231,crop=(20,0,520,458))
txt(34,379,'E0 / EM motor connector',13,INK,True)
para(34,403,252,'Use the angled four-contact socket at the upper left. Keep the existing motor lead if it is suitable.',11.2)
note(34,471,252,'Plug orientation and wire colors still need a continuity record. Do not guess from color.',True,72)

txt(319,132,'BTT V1.2 schematic: P11 / E0',14,INK,True)
txt(319,156,'These are schematic pin numbers, not a cable-entry drawing.',10.4,MUTED)
tablex=319
for i,(pin,net,coil) in enumerate([('1','A2','Coil A'),('2','A1','Coil A'),('3','B1','Coil B'),('4','B2','Coil B')]):
    yy=181+i*33
    rect(tablex,yy,439,30,PALE if i%2==0 else white,radius=2)
    txt(tablex+12,yy+7,f'P11 pin {pin}',11,INK,True)
    txt(tablex+123,yy+7,net,11,BLUE if i<2 else TEAL,True)
    txt(tablex+201,yy+7,coil,11,INK)
    txt(tablex+299,yy+7,'Wire: __________',10.5,MUTED)

txt(319,334,'Measure, label, then crimp',14,INK,True)
for i,s in enumerate([
    'Set the meter to resistance. Find two pairs with low, finite resistance; wires from different coils should read open.',
    'Label one measured pair A and the other B. Each complete pair goes to its matching A or B contacts.',
    'Identify actual connector pin 1 before repinning; then verify each wire through the finished lead. Never move a motor plug while powered.'
]):
    yy=361+i*62
    badge(329,yy+9,str(i+1),BLUE,9)
    para(347,yy,411,s,11.2)
txt(319,551,'Motor current, direction and rotation distance remain commissioning settings.',9.8,MUTED)
footer(3,'B2; coil colors and cavity orientation not recorded')

# 4. Hall sensor wiring: two shared rails, two individual outputs, real pull-ups.
heading(4,'Connect X and Y Hall endstops','Five-contact ENDSTOP header / X signal = PB6 / Y signal = PB7 / PB5 unused')
image(PHOTO,34,137,237,182,crop=(0,580,648,1078))
rect(41,196,115,29,None,BLUE,radius=2)
txt(34,333,'ENDSTOP is the middle row.',11,INK,True)
para(34,353,238,'The four-contact I2C row is above it. Match the board-front orientation before inserting contacts.',10.7)

txt(302,132,'Left to right in BTT\'s front view',12,INK,True)
endpins=[('+5 V','Both VCC'),('GND','Both GND'),('PB6','X output'),('PB5','Unused'),('PB7','Y output')]
for i,(pin,use) in enumerate(endpins):
    x=302+i*91
    rect(x,158,85,65,PALE,radius=3)
    txt(x+10,169,pin,13,INK,True)
    txt(x+10,196,use,9.5,MUTED)
para(302,242,452,'<b>The board already provides 10 kOhm pull-ups to 3.3 V</b> on these inputs (BTT schematic R35-R37). The sensors use a 5 V supply while their open-collector outputs use 3.3 V signal pull-ups.',11.2)

for x,title,out in [(34,'X sensor','PB6'),(282,'Y sensor','PB7')]:
    txt(x,411,title,14,INK,True)
    labels=[('VCC','+5 V',RED),('GND','GND',INK),('OUT',out,BLUE)]
    for i,(a,b,col) in enumerate(labels):
        yy=443+i*30
        txt(x,yy,a,11,col,True)
        line([(x+46,yy+7),(x+126,yy+7)],col,2)
        txt(x+139,yy,b,11,INK,True)
para(538,411,220,'<b>Sensor leg reference</b><br/>Original Allegro -UA package, branded face toward you, leads down:<br/><b>1 = VCC, 2 = GND, 3 = OUT.</b>',10.8)
para(538,490,220,'Confirm the actual part and orientation before soldering. Insulate each leg and support the lead bundle.',10.5,AMBER)
footer(4,'B1/B2 + A1; test both states before homing (K2)')

# 5. The four contacts are explicitly the board-front view, not a mirrored cable.
heading(5,'Build the power + CAN harness','Planned link: Raspberry Pi USB > Octopus Pro USB-to-CAN bridge > EBB36 CAN')
image(PHOTO,34,135,275,204,crop=(600,0,1100,371))
txt(352,132,'Looking at the board front',14,INK,True)
gridx,gridy=352,162
for col,row,title,body,color in [(0,0,'GND','PSU V- / common ground',INK),
                                (1,0,'VIN','Protected +24 V',RED),
                                (0,1,'CAN L','Octopus CAN L',TEAL),
                                (1,1,'CAN H','Octopus CAN H',BLUE)]:
    x,y=gridx+col*203,gridy+row*75
    rect(x,y,195,68,PALE,radius=4)
    txt(x+14,y+11,title,17,color,True)
    txt(x+14,y+40,body,10.2,INK)
para(352,324,401,'USB-C is at the upper right, as photographed. A plug\'s wire-entry view can be mirrored: verify every contact end to end instead of copying a left/right view.',10.6,AMBER)

txt(34,374,'Rear of printer',11.5,INK,True)
txt(622,374,'EBB36 functions',11.5,INK,True)
for y,left,right,col in [(408,'Fused +24 V branch','VIN',RED),(444,'PSU V- / ground','GND',INK)]:
    txt(34,y-7,left,11,col,True)
    line([(211,y),(607,y)],col,2.4)
    dot(211,y,col);dot(607,y,col)
    txt(622,y-7,right,11,col,True)
txt(34,477,'Octopus CAN H',11,BLUE,True)
txt(34,514,'Octopus CAN L',11,TEAL,True)
txt(622,477,'CAN H',11,BLUE,True)
txt(622,514,'CAN L',11,TEAL,True)
for offset,col in [(0,BLUE),(pi,TEAL)]:
    pts=[]
    for i in range(241):
        x=211+396*i/240
        # Whole turns preserve each conductor's identity at both labeled ends.
        y=502-18*cos(6*pi*i/240+offset)
        pts.append((x,y))
    line(pts,col,1.8)
txt(330,455,'H and L travel as one twisted pair',10.4,MUTED)
para(34,540,724,'Fit one 120 Ohm termination at each CAN end (Octopus and EBB). With all power removed and the bus connected, H-to-L should measure about 60 Ohm. Record cable colors and the selected branch fuse.',10.2)
footer(5,'B1/B2 + K1; line colors show functions, not your cable colors')

# 6. An explicit unconnected control gap prevents making up a four-wire fan interface.
heading(6,'Prepare the four-wire blower separately','HXH HBB0524VD / 24 V / 0.25 A / control connection is not yet validated')
note(34,119,724,'Planning only: keep the blower unplugged while its PWM interface is checked. PA1 remains reserved.',True,35)
rect(34,186,191,244,PALE)
txt(53,205,'STOCK BLOWER',13,INK,True)
para(53,233,152,'Four leads have different jobs. Wire colors below come from the conversion reference, not an HXH datasheet.',11.1)
para(53,354,152,'Confirm the supplied fan\'s actual leads before terminating.',10.8,AMBER)

specs=[(211,'Red','+24 V supply',RED),(268,'Black','Permanent GND',INK),
       (325,'Blue','PWM control input',BLUE),(382,'Yellow','Speed feedback / tach',AMBER)]
for y,colorname,desc,col in specs:
    line([(225,y),(464,y)],col,2.3,dash=[4,3] if colorname=='Blue' else None)
    txt(248,y-19,colorname,10.5,col,True)
    txt(479,y-8,desc,12,INK,True)
    if colorname=='Blue':
        # Deliberately show an open gap rather than an invented adapter circuit.
        C.setFillColor(white);C.rect(379,H-y-8,34,16,fill=1,stroke=0)
        dot(378,y,BLUE,2);dot(415,y,BLUE,2)
        txt(383,y-6,'?',13,AMBER,True)

para(479,227,279,'Supply function only. Final branch and fan lead identification still need checking.',10.5,MUTED)
para(479,284,279,'Ground stays connected for the fan\'s separate logic control.',10.5,MUTED)
para(479,341,279,'Logic voltage, drive circuit and control behavior need a verified specification or measurement.',10.5,AMBER)
para(479,398,279,'Leave unconnected and individually insulated if feedback is not used.',10.5,MUTED)
line([(34,455),(758,455)],RULE,.8)
para(34,473,347,'<b>What BTT establishes</b><br/>PA1 / FAN2 is a switched fan-power return. It is not a raw MCU logic pin. The fan header also carries VIN.',11.2)
para(407,473,351,'<b>What is still needed</b><br/>Establish a compatible PWM interface for this fan. Do not attach its PWM lead to 24 V or copy a control frequency without confirming it.',11.2)
footer(6,'B2 + saved fan label; color roles are secondary reference only')

# 7. Jumper states and staged commissioning, with live clickable primary sources.
heading(7,'Set jumpers, inspect, then power in stages','Assembly is separate from flashing and heating / successful firmware flashes are not yet recorded')
image(REF/'BTT_USB_power.png',34,137,330,248)
for n,x,y,bx,by in [('A',590,282,683,257),('B',187,388,110,500),('C',430,178,423,83)]:
    tx,ty=34+x*330/718,137+y*248/540
    xx,yy=34+bx*330/718,137+by*248/540
    line([(xx,yy),(tx,ty)],BLUE,1.3)
    badge(xx,yy,n,BLUE,9)

txt(390,134,'Normal 24 V + CAN operation',14,INK,True)
jumper_rows=[('A','VUSB','OPEN','Fit only for isolated USB-only electronics power.'),
             ('B','PT1000','OPEN','Planned NTC on TH0 uses the 4.7 kOhm pull-up.'),
             ('C','120R','FIT','EBB is the CAN bus end. Octopus needs the other 120 Ohm termination.')]
for i,(n,name,state,body) in enumerate(jumper_rows):
    yy=165+i*71
    badge(400,yy+10,n,BLUE,9)
    txt(419,yy,f'{name}: {state}',12,INK,True)
    para(419,yy+23,338,body,10.6)
para(390,387,368,'Keep the PCB underside clear of the motor case and screws. Support the harness at the mount; leave a service loop clear of belts, fan blades and the nozzle.',10.6)

for i,(title,body) in enumerate([
    ('1 / Check unpowered','Tug crimps; verify contact mapping, polarity, shorts and CAN termination. Select the fuse for the actual branch wiring and load.'),
    ('2 / Bring up electronics','Disconnect heater and motor for flashing. Confirm both MCUs, CAN, room-temperature sensor reading, hotend fan and Hall states.'),
    ('3 / Enable heat last','Power off before reconnecting loads. Confirm X1C sensor curve and heater checks, then test under supervision; finish blower and motion tests.')
]):
    x=34+i*246
    txt(x,435,title,11.5,INK,True)
    para(x,457,231,body,10.1,INK,12.6)

txt(34,526,'Primary sources (click labels; full source list accompanies this guide)',9.3,MUTED,True)
source_link(34,546,'B1 BTT hardware', 'https://neo.bttwiki.com/en/docs/board-docs/ebb-series/ebb-36/ebb-36-hardware',9)
source_link(155,546,'B2 V1.2 schematic','https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/EBB36%20CAN%20V1.1%20and%20V1.2/Hardware/BIGTREETECH%20EBB36%20CAN%20V1.2-SCH.pdf',9)
source_link(282,546,'B3 V1.2 example','https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/sample-bigtreetech-ebb-canbus-v1.2.cfg',9)
source_link(397,546,'K1 CAN bus','https://www.klipper3d.org/CANBUS.html',9)
source_link(488,546,'K2 Multi-MCU homing','https://www.klipper3d.org/Multi_MCU_Homing.html',9)
source_link(638,546,'A1 Hall datasheet','https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx',9)
footer(7,'B1-B3 + K1/K2/A1; BTT illustration reproduced as reference')

C.save()

sources={
    'B1': {'title':'BTT EBB36 hardware wiki','url':'https://neo.bttwiki.com/en/docs/board-docs/ebb-series/ebb-36/ebb-36-hardware'},
    'B2': {'title':'BTT EBB36 V1.2 schematic','url':'https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/EBB36%20CAN%20V1.1%20and%20V1.2/Hardware/BIGTREETECH%20EBB36%20CAN%20V1.2-SCH.pdf'},
    'B3': {'title':'BTT V1.2 sample configuration','url':'https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/sample-bigtreetech-ebb-canbus-v1.2.cfg'},
    'B4': {'title':'BTT V1.1/V1.2 pinout','url':'https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20(STM32G0B1)/EBB36%20CAN%20V1.1%20and%20V1.2/Hardware/EBB36%20CAN%20V1.1%26V1.2-PIN.png'},
    'K1': {'title':'Klipper CAN bus','url':'https://www.klipper3d.org/CANBUS.html'},
    'K2': {'title':'Klipper multiple-MCU homing','url':'https://www.klipper3d.org/Multi_MCU_Homing.html'},
    'A1': {'title':'Allegro A3141-A3144 datasheet','url':'https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx'},
    'S1': {'title':'Sedmenti conversion - secondary build-specific context','url':'https://github.com/sedmenti/FlashForge_A5M_raspberry'}
}
manifest={'checked':'2026-11-03','board':'EBB36 CAN V1.2.1 without MAX31865','sources':sources,
          'reference_files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(REF.iterdir()) if p.is_file() and p.name != 'SOURCES.json']}
(REF/'SOURCES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(f'Created {PDF} ({PDF.stat().st_size:,} bytes)')
