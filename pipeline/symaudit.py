import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA=lambda *p:_os.path.join(ROOT,'data',*p)
import json,sys
sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
from fit import trim
def score(g,axis):
    g=trim(g); H=len(g); W=len(g[0]); ok=tot=0
    for y in range(H):
        for x in range(W):
            a=g[y][x]; b=g[y][W-1-x] if axis=='lr' else g[H-1-y][x]
            if a!='.' or b!='.':
                tot+=1; ok+= (a!='.')==(b!='.')
    return ok/max(tot,1)
def colscore(g,axis):
    g=trim(g); H=len(g); W=len(g[0]); ok=tot=0
    for y in range(H):
        for x in range(W):
            a=g[y][x]; b=g[y][W-1-x] if axis=='lr' else g[H-1-y][x]
            if a!='.' or b!='.': tot+=1; ok+= a==b
    return ok/max(tot,1)
if __name__=='__main__':
    for f in ['motifs.json','supplied.json']:
        for m in json.load(open(DATA(f)))['motifs']:
            g=m['grid']; t=trim(g)
            lr,tb=score(g,'lr'),score(g,'tb')
            off_lr=(13-len(t[0]))%2; 
            flag=[]
            if 0.85<=lr<1: flag.append(f'near-LR {lr:.2f}')
            if 0.85<=tb<1 and m['size']=='square': flag.append(f'near-TB {tb:.2f}')
            if lr==1 and off_lr: flag.append('LR-sym but off-centre')
            if lr<0.85 and tb<0.85: flag.append('NO AXIS')
            if lr==1 and colscore(g,'lr')<1: flag.append(f'colour-LR {colscore(g,"lr"):.2f}')
            print(f"{m['id']:28s} {m['size']:6s} LR={lr:.2f} TB={tb:.2f} {' | '.join(flag)}")
