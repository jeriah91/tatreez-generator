import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA=lambda *p:_os.path.join(ROOT,'data',*p)
import json,sys
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
from fit import trim, reduce_height, reduce_width, recolour, shape_sym
C=json.load(open(DATA('charts.json'))); P10={o['i']:o for o in json.load(open(DATA('kawar','p10_grids.json')))}
T='https://tatreez.app/motifs/'
def crop(g,x0,y0,x1,y1): return [r[x0:x1+1] for r in g[y0:y1+1]]
B=[]
def add(id,name,arabic,area,city,kind,unit,gap,url=None,source=None,note=''):
    unit=recolour(trim(unit)) if kind=='pictorial' else recolour(unit)
    if kind=='pictorial':
        if len(unit)>13: unit=reduce_height(unit,13)
        if len(unit[0])>13: unit=reduce_width(unit,13)
    B.append(dict(id=id,name=name,arabic=arabic,area=area,city=city,kind=kind,unit=unit,gap=gap,url=url,source=source or url,note=note,symmetric=shape_sym(unit)))
# pictorial units: upright, repeated along the strip in either direction
add('b-galilee-cypress','Row of cypress trees','Sarw · سرو','Galilee','Galilee (al-Jalil)','pictorial',crop(C['d902bd23']['rows'],1,0,5,14),1,
    url=T+'d902bd23-27ff-46cf-b1ac-cd31c77fbd64/sarwa-cypress-tree-galilee-1-galilee',note='Small cypresses stitched in a row.')
add('b-gaza-wheat','Row of wheat stalks','Sanabel · سنابل','Gaza','Gaza','pictorial',crop(C['13f6a1af']['rows'],1,0,7,18),1,
    url=T+'13f6a1af-b9b2-44b9-ae2c-a040b956ab79/sanabel-crops-gaza',note='Wheat stalks standing in a row.')
add('b-jaffa-trees','Row of bald trees',"Shajar Aqra' · شجر اقرع",'Jaffa','Jaffa (Yafa)','pictorial',crop(C['1962ccc1']['rows'],1,0,5,21),1,
    url=T+'1962ccc1-e57a-4806-9202-38282977d7dd/shajar-aqra-bald-trees-jaffa',note='Trees in a row.')
add('b-ramallah-palms','Row of palm trees','Nakhla · نخلة','Ramallah','Ramallah','pictorial',crop(P10[0]['grid'],0,0,8,16),0,
    source='Kawar & Nasir, Palestinian Embroidery (2021), p.18',note='The book’s Ramallah palm, repeated as a band.')
add('b-ashdod-cypress','Row of cypress trees','Sarwat Isdud · سروة أسدود','Gaza','Isdud (Ashdod)','pictorial',C['74e78c47']['rows'],1,
    url=T+'74e78c47-cc55-468d-bc7f-cb20e26770e1/sarwa-cypress-tree-ashdod-2-ashdod',note='Small Isdud cypress in a row.')
# geometric bands: native vertical, 13 wide; they turn with the edge on horizontal sides
add('b-ramallah-nafnoof','Border','Nafnoof · نفنوف','Ramallah','Ramallah','geometric',crop(C['b1f09e24']['rows'],0,0,12,5),0,
    url=T+'b1f09e24-622d-4abd-bfde-335873e60dac/nafnoof-border-17-ramallah',note='Ramallah border unit.')
add('b-hebron-houses','Houses band','Beyout · بيوت','Hebron','Hebron (al-Khalil)','geometric',crop(C['2404bb07']['rows'],0,0,12,5),0,
    url=T+'2404bb07-0a50-49e8-a980-576677918655/beyout-houses-1-hebron',note='Houses repeated as a band.')
add('b-jaffa-feathers','Squares of feathers',"'Irq Reesh Tarbee' · عرق ريش تربيع",'Jaffa','Jaffa (Yafa)','geometric',crop(C['07c0c91e']['rows'],0,0,12,6),0,
    url=T+'07c0c91e-e748-439a-8299-0648eebdabbc/irq-reesh-tarbee-squares-of-feathers-jaffa',note='Feather squares repeated as a band.')
add('b-gaza-railway','Railway','Sikkat Hadeed · سكة حديد','Gaza','Gaza','geometric',crop(C['bdad9684']['rows'],0,0,12,7),0,
    url=T+'bdad9684-4dec-4f5c-9246-88d88bafe8bc/sikat-hadeed-railway-gaza',note='Railway carriages between rows of leaves.')
json.dump(B,open(DATA('borders.json'),'w'),ensure_ascii=False)
for b in B:
    print(b['id'],b['kind'],f"{len(b['unit'][0])}x{len(b['unit'])}",'sym' if b['symmetric'] else 'ASYM'); print('\n'.join(b['unit']))

# ---------- prebuilt strips: FILL RULE edge to edge, symmetric spacing ----------
from fit import expand_width, expand_height, rot90 as _rot90
def sym_gaps(n, base, extra):
    """n-1 gaps of `base`, plus `extra` spread symmetrically from the centre. None if impossible."""
    k=n-1
    if k<=0: return [] if extra==0 else None
    g=[base]*k; per=extra//k; g=[x+per for x in g]; rem=extra-per*k
    if rem%2 and k%2==0: return None
    if rem%2: g[k//2]+=1; rem-=1
    i=0
    while rem>0: g[k//2-1-i if k%2==0 else k//2-1-i]+=1; g[k-1-(k//2-1-i)]+=1; rem-=2; i+=1
    return g
def run(L,u,gap):
    """EQUAL SPACING: n repeats with identical gaps, first and last touching the ends (fill rule).
    The unit may widen by up to 4 stitches so the gaps divide evenly. Returns (n, gap, stretch)."""
    best=None
    lo,hi=(0,0) if gap==0 else (1,3)
    for st in range(0,5):
        uu=u+st
        if uu>L: break
        for n in range(1,L//uu+1):
            if n==1:
                if uu==L: cand=(st*2,1,0,st)
                else: continue
            else:
                extra=L-n*uu
                if extra<0 or extra%(n-1): continue
                g=extra//(n-1)
                if not lo<=g<=hi: continue
                cand=(st*2+abs(g-max(gap,0))+0.01*n, n, g, st)
            if best is None or cand<best: best=cand
    if best is None: return 1,0,L-u
    return best[1],best[2],best[3]
def strip(unit,gap,W,H):
    nx,gx,sx=run(W,len(unit[0]),gap)
    if sx: unit=expand_width(unit,len(unit[0])+sx)
    ny,gy,sy=run(H,len(unit),gap)
    if sy: unit=expand_height(unit,len(unit)+sy)
    uw,uh=len(unit[0]),len(unit)
    G=[['.']*W for _ in range(H)]
    for a in range(ny):
        for b in range(nx):
            x=b*(uw+gx); y=a*(uh+gy)
            for yy in range(uh):
                for xx in range(uw):
                    if unit[yy][xx]!='.': G[y+yy][x+xx]=unit[yy][xx]
    return [''.join(r) for r in G]
for b in B:
    u=b['unit']; S={}
    for L in (13,28):
        hu = _rot90(u) if b['kind']=='geometric' else u     # geometric bands turn with the edge; pictorial stay upright
        h=strip(hu,b['gap'],L,13)
        if not all(r==r[::-1] for r in h):            # directional band: mirror it at the module centre
            h=[r[:(L+1)//2]+r[:L//2][::-1] for r in h]
        S[f'h{L}']=h
        S[f'v{L}']=strip(u,b['gap'],13,L)
    b['strips']=S
json.dump(B,open(DATA('borders.json'),'w'),ensure_ascii=False)
bad=[]
for b in B:
    for k,g in b['strips'].items():
        t=trim(g); W=len(g[0]);H=len(g)
        full = len(t[0])==W and len(t)==H
        lr = all(r==r[::-1] for r in g)
        if not full or not lr: bad.append((b['id'],k,'full' if full else 'NOT FULL','LR' if lr else 'not LR'))
print('strip issues:',bad)
import re
def gaps_equal(g,axis):
    lines = g if axis=='y' else [''.join(r[j] for r in g) for j in range(len(g[0]))]
    occ=[any(c!='.' for c in l) for l in lines]
    runs=[];cur=0
    for o in occ:
        if not o: cur+=1
        elif cur: runs.append(cur); cur=0
    return len(set(runs))<=1, runs
for bb in B:
    for k,g in bb['strips'].items():
        for ax in ('x','y'):
            ok,r=gaps_equal(g,ax)
            if not ok: print('UNEQUAL',bb['id'],k,ax,r)
print('\n'.join(B[0]['strips']['v13'])); print(); print('\n'.join(B[5]['strips']['h28']))
