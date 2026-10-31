import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA=lambda *p:_os.path.join(ROOT,'data',*p)
import json,sys
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
from fit import fit, shape_sym
from spec import SPEC
from PIL import Image, ImageDraw
C=json.load(open(DATA('charts.json')))
P10={o['i']:o for o in json.load(open(DATA('kawar','p10_grids.json')))}
out=[]
for s in SPEC:
    if 'rows' in s: src=s['rows']
    elif 'kawar' in s:
        i,crop=s['kawar']; src=P10[i]['grid']; s=dict(s,crop=crop)
    else: src=C[s['id']]['rows']
    g=fit(src,s['size'],crop=s.get('crop'),tile=s.get('tile'))
    m={k:v for k,v in s.items() if k not in('rows','kawar','crop','tile')}
    m['id']=('tz-' if not s['id'].startswith('kawar') else '')+s['id']
    m['source']=s.get('source') or m.get('url')
    m['inventory_status']='seen'
    m['grid']=g; m['region']=s['area']; m['symmetric']=shape_sym(g); m['axes']=fit.axes
    out.append(m)
# STAR SIDE-ORNAMENT RULE: extra stitches beside a star run vertically and join the star's arms
def _set(g,y,x,ch): g[y]=g[y][:x]+ch+g[y][x+1:]
def star_sides(m):
    g=list(m['grid'])
    if m['id']=='tz-76f399ae':          # Ramallah Najma: bar from upper arm tip to lower arm tip, drop the sideways pair
        for y in range(4,9): _set(g,y,0,'2'); _set(g,y,12,'2')
        _set(g,6,1,'.'); _set(g,6,11,'.')
    if m['id']=='tz-ebf4fd94':          # Beersheba disc of stars: join the two side clusters into one vertical bar
        _set(g,6,0,g[5][0]); _set(g,6,12,g[5][12])
    m['grid']=g
FACES={'tz-caf919e0':'left','tz-f12ff0d4':'right'}  # direction of asymmetric motifs used as facing pairs
for m in out:
    star_sides(m)
    if m['id'] in FACES: m['faces']=FACES[m['id']]
json.dump({'motifs':out},open(DATA('motifs.json'),'w'),ensure_ascii=False,indent=0)
# review sheet
cell=8; cols=10
cards=[]
for m in out:
    g=m['grid'];h=len(g)
    im=Image.new('RGB',(13*cell+4,28*cell+30),'white');d=ImageDraw.Draw(im)
    d.rectangle([0,12,13*cell+3,h*cell+15],fill=(35,31,32))
    pal={'1':(246,238,233),'2':(200,32,38),'3':(0,104,60)}
    for y,r in enumerate(g):
        for x,ch in enumerate(r):
            if ch!='.': d.rectangle([x*cell+2,y*cell+14,x*cell+cell,y*cell+cell+12],fill=pal[ch])
    d.text((1,0),m['id'][:18],fill=(0,0,0)); d.text((1,h*cell+16),('SYM ' if m['symmetric'] else '')+m['size'][0],fill=(0,0,0))
    cards.append(im)
W=cols*(13*cell+10); rowsN=(len(cards)+cols-1)//cols
sheet=Image.new('RGB',(W,rowsN*(28*cell+34)),'white')
for i,c in enumerate(cards): sheet.paste(c,((i%cols)*(13*cell+10),(i//cols)*(28*cell+34)))
sheet.save(_os.path.join(ROOT,'out','fit_sheet.png')); print(len(out),'motifs', sheet.size)
