import json,sys,os
here=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(here); sys.path.insert(0,here)
from fit import SIZES
DATA=lambda f: os.path.join(ROOT,'data',f)
ms=[]
for f in ['motifs.json','supplied.json']:
    p=DATA(f)
    if os.path.exists(p): ms+=json.load(open(p))['motifs']
ok=[]
for m in ms:
    g=m['grid']; w,h=SIZES[m['size']]
    if len(g)!=h or any(len(r)!=w or set(r)-set('.123') for r in g): print('BAD',m['id'],len(g),[len(r) for r in g]); continue
    shape_sym=all([c=='.' for c in r]==[c=='.' for c in r[::-1]] for r in g)
    if m['size'] in('tall','largetall') and not shape_sym: print('ASYM-TALL rejected',m['id']); continue
    if m['id'] in {x['id'] for x in ok}: print('DUP',m['id']); continue
    ok.append(m)
rest=json.load(open(DATA('stitch.json')))['rest']
import importlib.util
spec=importlib.util.spec_from_file_location('inv',os.path.join(here,'inventory_src.py'));inv=importlib.util.module_from_spec(spec);spec.loader.exec_module(inv)
s=open(os.path.join(ROOT,'src','app.html')).read().replace('__MOTIFS__',json.dumps(ok,ensure_ascii=False)).replace('__STITCH_REST__',json.dumps(rest)).replace('__INVENTORY__',json.dumps(inv.INV,ensure_ascii=False)).replace('__KAWAR_INV__',json.dumps(inv.KAWAR_INV,ensure_ascii=False)).replace('__BORDERS__',open(DATA('borders.json')).read())
(os.makedirs(os.path.join(ROOT,'dist'),exist_ok=True) or open(os.path.join(ROOT,'dist','index.html'),'w')).write(s)
print(len(ok),'motifs;',sum(m['size']=='tall' for m in ok),'tall;',sum(m['size'] in('large','largetall') for m in ok),'large')
