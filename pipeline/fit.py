"""Fit source charts onto the generator's stitch fields.

Square field: 13 x 13.  Tall field: 13 x 28.
Steps per motif (from SPEC):  crop -> optional repeat-tile -> width reduction -> height reduction -> centre pad.
Reduction removes the line (column / row) that is most similar to its neighbour, so repeated
structure (duplicate columns of a thick trunk, doubled stepping rows) is merged first and the
motif's silhouette is kept. Left-right symmetric motifs lose columns in mirrored pairs so they stay symmetric.
Colours are re-indexed by frequency: 1 = main thread, 2 = first accent, 3 = everything else.
"""
import json

def trim(g):
    rows=[i for i,r in enumerate(g) if set(r)!={'.'}]
    if not rows: return g
    g=g[rows[0]:rows[-1]+1]
    cols=[j for j in range(len(g[0])) if any(r[j]!='.' for r in g)]
    return [r[cols[0]:cols[-1]+1] for r in g]

def shape_sym(g): return all([c=='.' for c in r]==[c=='.' for c in r[::-1]] for r in g)

def col(g,j): return ''.join(r[j] for r in g)
def diff(a,b): return sum((x=='.')!=(y=='.') for x,y in zip(a,b))*3 + sum(x!=y for x,y in zip(a,b))

def drop_cols(g, js): return [''.join(c for j,c in enumerate(r) if j not in js) for r in g]

def reduce_width(g, target):
    while len(g[0])>target:
        W=len(g[0]); sym=shape_sym(g); best=None
        excess=W-target
        for j in range(W):
            m=W-1-j
            if sym and excess>=2 and j==m: continue
            if sym and excess>=2 and j>m: continue
            cost=min(diff(col(g,j),col(g,j-1)) if j>0 else 99, diff(col(g,j),col(g,j+1)) if j<W-1 else 99)
            if sym and excess>=2:
                cost+=min(diff(col(g,m),col(g,m-1)) if m>0 else 99, diff(col(g,m),col(g,m+1)) if m<W-1 else 99)
                js={j,m}
            elif sym and excess==1:
                if j!=W//2: continue      # odd excess on a symmetric motif: drop the centre column
                js={j}
            else: js={j}
            # prefer interior lines (keep silhouettes)
            cost+= (0.5 if j==0 or j==W-1 else 0)
            if best is None or cost<best[0]: best=(cost,js)
        g=drop_cols(g,best[1])
    return g

def tb_sym(g): return all([c=='.' for c in g[i]]==[c=='.' for c in g[len(g)-1-i]] for i in range(len(g)))

def reduce_height(g, target):
    # rows are removed in mirrored pairs when the motif is top-bottom symmetric, so it stays symmetric
    while len(g)>target:
        H=len(g); best=None; sym=tb_sym(g); excess=H-target
        for i in range(H):
            m=H-1-i
            if sym and excess>=2 and i>=m: continue
            if sym and excess==1 and i!=H//2: continue
            cost=min(diff(g[i],g[i-1]) if i>0 else 99, diff(g[i],g[i+1]) if i<H-1 else 99)+(0.5 if i in (0,H-1) else 0)
            if sym and excess>=2: cost+=min(diff(g[m],g[m-1]) if m>0 else 99, diff(g[m],g[m+1]) if m<H-1 else 99); rm={i,m}
            else: rm={i}
            if best is None or cost<best[0]: best=(cost,rm)
        g=[r for k,r in enumerate(g) if k not in best[1]]
    return g

def pad(g, W, H):
    h=len(g); w=len(g[0])
    l=(W-w)//2; r=W-w-l; t=(H-h)//2; b=H-h-t
    row='.'*W
    return [row]*t+['.'*l+x+'.'*r for x in g]+[row]*b

def recolour(g):
    from collections import Counter
    c=Counter(ch for r in g for ch in r if ch!='.')
    order=[k for k,_ in c.most_common()]
    m={k:('1' if i==0 else '2' if i==1 else '3') for i,k in enumerate(order)}
    return [''.join(m.get(ch,'.') for ch in r) for r in g]

def fit(rows, size, crop=None, tile=None, keep_colours=False, max_rows=None):
    g=list(rows)
    if crop:
        x0,y0,x1,y1=crop; g=[r[x0:x1+1] for r in g[y0:y1+1]]
    g=trim(g)
    W=13; H=13 if size=='square' else 28
    if tile:   # repeat rows [a..b] until height reaches limit
        a,b,limit=tile; unit=g[a:b+1]; head=g[:a]; out=head[:]
        while len(out)+len(unit)<=limit: out+=unit
        g=out
    src=trim(g)
    g=reduce_width(g,W)
    g=reduce_height(g,H)
    g,axes=enforce_symmetry(g,src)
    if size=='square' and 'tb' not in axes and len(g)<H and len(g)%2==0: pass  # pictorial: keep natural height
    g=fill_field(g,W,H)          # FILL RULE: the motif touches all four sides of the stitch field
    if not keep_colours: g=recolour(g)
    fit.axes=axes
    return g


# ---------------- symmetry enforcement ----------------
def axis_score(g,axis):
    H=len(g); W=len(g[0]); ok=tot=0
    for y in range(H):
        for x in range(W):
            a=g[y][x]; b=g[y][W-1-x] if axis=='lr' else g[H-1-y][x]
            if a!='.' or b!='.': tot+=1; ok+=(a!='.')==(b!='.')
    return ok/max(tot,1)

def make_odd(g,axis):
    """A symmetric motif needs an odd extent to sit exactly centred on the 13-stitch field."""
    if axis=='lr' and len(g[0])%2==0:
        c=len(g[0])//2; g=[r[:c]+r[c+1:] for r in g]
    if axis=='tb' and len(g)%2==0:
        c=len(g)//2; g=g[:c]+g[c+1:]
    return g

def mirror(g,axis):
    """Copy the fuller half onto the other half (shape and colour)."""
    H=len(g); W=len(g[0])
    if axis=='lr':
        h=W//2; left=sum(c!='.' for r in g for c in r[:h]); right=sum(c!='.' for r in g for c in r[W-h:])
        if left>=right: return [r[:W-h]+r[:h][::-1] for r in g]
        return [r[W-h:][::-1]+r[h:] for r in g]
    h=H//2; top=sum(c!='.' for r in g[:h] for c in r); bot=sum(c!='.' for r in g[H-h:] for c in r)
    if top>=bot: return g[:H-h]+g[:h][::-1]
    return g[H-h:][::-1]+g[h:]

def rot90(g): return [''.join(g[len(g)-1-y][x] for y in range(len(g))) for x in range(len(g[0]))]

def colour_balanced(g):
    lr=all(r==r[::-1] for r in g)
    c4=len(g)==len(g[0]) and rot90(g)==g
    return lr or c4

def enforce_symmetry(g, src, tol=0.9):
    """Keep every axis the source has. Returns (grid, axes)."""
    g=trim(g); src=trim(src); axes=[]
    for axis in ('lr','tb'):
        if axis_score(src,axis)>=tol or axis_score(g,axis)>=tol:
            g=make_odd(g,axis); g=mirror(g,axis); axes.append(axis)
    if 'lr' in axes and not colour_balanced(g):
        g=[r[:(len(r)+1)//2]+r[:len(r)//2][::-1] for r in g]
    return g, axes


# ---------------- fill rule: every motif spans the full stitch field ----------------
def _dup_cols(g, js): return [''.join(c*2 if j in js else c for j,c in enumerate(r)) for r in g]

def _line_cost(lines, j):
    a=lines[j]; c=[]
    if j>0: c.append(diff(a,lines[j-1]))
    if j<len(lines)-1: c.append(diff(a,lines[j+1]))
    # prefer thick interior lines; never duplicate an empty line (that only adds space)
    empty = all(ch=='.' for ch in a)
    return (min(c) if c else 99) + (50 if empty else 0) - 0.1*sum(ch!='.' for ch in a)

def expand_width(g, target):
    while len(g[0])<target:
        W=len(g[0]); sym=shape_sym(g) and all(r==r[::-1] for r in g); need=target-W
        cols=[col(g,j) for j in range(W)]; best=None
        for j in range(W):
            m=W-1-j
            if sym and need>=2 and j>=m: continue
            if sym and need==1 and j!=W//2: continue
            cost=_line_cost(cols,j) + (_line_cost(cols,m) if sym and need>=2 else 0)
            js={j,m} if sym and need>=2 else {j}
            if best is None or cost<best[0]: best=(cost,js)
        g=_dup_cols(g,best[1])
    return g

def expand_height(g, target):
    while len(g)<target:
        H=len(g); sym=all(g[i]==g[H-1-i] for i in range(H)); need=target-H; best=None
        for i in range(H):
            m=H-1-i
            if sym and need>=2 and i>=m: continue
            if sym and need==1 and i!=H//2: continue
            cost=_line_cost(g,i)+(_line_cost(g,m) if sym and need>=2 else 0)
            rs={i,m} if sym and need>=2 else {i}
            if best is None or cost<best[0]: best=(cost,rs)
        out=[]
        for k,r in enumerate(g):
            out.append(r)
            if k in best[1]: out.append(r)
        g=out
    return g

def fill_field(g, W, H):
    g=trim(g)
    if len(g[0])>W: g=reduce_width(g,W)
    if len(g)>H: g=reduce_height(g,H)
    g=expand_width(g,W); g=expand_height(g,H)
    return g
