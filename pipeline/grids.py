import json,sys,collections
pts=json.load(open(sys.argv[1]))
pts=[p for p in pts if p[4]!='rgb(255, 255, 255)']
# group by stitch size class (round to 0.2) then connected components
def comps(items,link):
    n=len(items);parent=list(range(n))
    def f(i):
        while parent[i]!=i: parent[i]=parent[parent[i]];i=parent[i]
        return i
    cell={}
    for i,p in enumerate(items):
        cell.setdefault((int(p[0]//link),int(p[1]//link)),[]).append(i)
    for (cx,cy),ids in cell.items():
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                for j in cell.get((cx+dx,cy+dy),[]):
                    for i in ids:
                        if abs(items[i][0]-items[j][0])<=link and abs(items[i][1]-items[j][1])<=link:
                            a,b=f(i),f(j)
                            if a!=b: parent[a]=b
    g=collections.defaultdict(list)
    for i in range(n): g[f(i)].append(items[i])
    return list(g.values())
groups=comps(pts,7.5)
groups=[g for g in groups if len(g)>=20]
groups.sort(key=lambda g:(round(min(p[1] for p in g)/60),min(p[0] for p in g)))
out=[]
for gi,g in enumerate(groups):
    sizes=collections.Counter(round(max(p[2],p[3]),1) for p in g)
    pitch=sizes.most_common(1)[0][0]
    xs=[p[0] for p in g];ys=[p[1] for p in g]
    x0,y0=min(xs),min(ys)
    cols=collections.Counter(p[4] for p in g)
    cmap={c:str(i+1) for i,(c,_) in enumerate(cols.most_common())}
    W=round((max(xs)-x0)/pitch)+1;H=round((max(ys)-y0)/pitch)+1
    grid=[['.']*W for _ in range(H)]
    for p in g:
        cx=round((p[0]-x0)/pitch);cy=round((p[1]-y0)/pitch)
        if grid[cy][cx]=='.' or cmap[p[4]]<grid[cy][cx]: grid[cy][cx]=cmap[p[4]]
    rows=[''.join(r) for r in grid]
    out.append({'i':gi,'x':round(x0),'y':round(y0),'pitch':pitch,'w':W,'h':H,'n':len(g),'colors':cmap,'grid':rows})
json.dump(out,open(sys.argv[2],'w'))
for o in out:
    print(f"#{o['i']} at({o['x']},{o['y']}) pitch={o['pitch']} {o['w']}x{o['h']} n={o['n']} colors={list(o['colors'].keys())}")
    if '--show' in sys.argv: print('\n'.join(o['grid']))
