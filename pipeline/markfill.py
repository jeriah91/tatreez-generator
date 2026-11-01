# PCF MARK MODULE: a square module whose 13×13 field is stitched on a half-scale grid (26×26 half-stitches).
# The centre 14×14 half-stitches hold the PCF mark (6.5 stitches = half the field); the ring around it is a real
# disc/medallion chart from Tatreez.app, fitted to 26×26, with its centre medallion replaced by the mark.
import os as _os, json, sys
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA=lambda *p:_os.path.join(ROOT,'data',*p)
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
from fit import fit
from spec import SPEC
C=json.load(open(DATA('charts.json')))
SP={s['id']:s for s in SPEC if 'chart' not in s and 'kawar' not in s and 'supplied' not in s}
HOLE=(6,19)            # half-stitch rows/cols cleared for the mark (14 wide; the mark is 13 wide, centred)
CHARTS=['1d674d15','5399f5a7','ebf4fd94','16503779','caf13f92','5c7713a3','abf960f1','8eb97ae3','fa85da31','341b229b']
out=[]
for cid in CHARTS:
    s=SP[cid]; src=C[cid]['rows']; h,w=len(src),max(len(r) for r in src)
    g=fit(src,'half')
    g=[''.join('.' if HOLE[0]<=x<=HOLE[1] and HOLE[0]<=y<=HOLE[1] else c for x,c in enumerate(r)) for y,r in enumerate(g)]
    lr=all([c=='.' for c in r]==[c=='.' for c in r[::-1]] for r in g); tb=all([c=='.' for c in g[i]]==[c=='.' for c in g[-1-i]] for i in range(26))
    edges=any(c!='.' for c in g[0]) and any(c!='.' for c in g[-1]) and any(r[0]!='.' for r in g) and any(r[-1]!='.' for r in g)
    if not(lr and tb and edges): print('SKIP',cid,lr,tb,edges); continue
    out.append(dict(id='mark-'+cid,name=s['name'],arabic=s.get('arabic'),area=s['area'],city=s.get('city'),region=s['area'],type='mark',size='mark',
        url=s['url'],source=s['url'],grid=g,axes=['lr','tb'],symmetric=True,
        derivation=f'Source chart {w}×{h} fitted to 26×26 half-stitches by repeating or dropping whole stitch lines (fit.py), symmetry made exact; '
                   f'the centre {HOLE[1]-HOLE[0]+1}×{HOLE[1]-HOLE[0]+1} half-stitches (its centre medallion) cleared for the PCF mark.'))
json.dump({'fills':out},open(DATA('markfills.json'),'w'),ensure_ascii=False,indent=0)
print(len(out),'mark fills')
