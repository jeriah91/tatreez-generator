// Full rules check: runs the generator across many seeds/settings and reports violations of the
// CLAUDE.md design rules, measured on the rendered grid (after dense/negative handling).
// Usage: node tools/rules.js [runs=3000]
const { chromium } = require('playwright');
(async()=>{
const RUNS=+(process.argv[2]||3000);
const b=await chromium.launch();const p=await b.newPage();
const warns=[];p.on('console',m=>{if(m.type()==='warning'||m.type()==='error')warns.push(m.text())});p.on('pageerror',e=>warns.push(e.message));
await p.goto('file://'+require('path').resolve(__dirname,'../dist/index.html'));await p.waitForTimeout(300);
const res=await p.evaluate((RUNS)=>{
 const V={}, EX={}; const bump=(k,ex)=>{V[k]=(V[k]||0)+1; if(!EX[k])EX[k]=ex};
 const rnd=rngFrom('rules-check');const pick=a=>a[rnd()*a.length|0];
 const SIZES=[[1,1],[1,2],[2,1],[2,2],[3,3],[4,3],[5,7],[8,2],[2,8],[6,1],[1,6],[10,10],[12,8]];
 const BAD=new Set(['red|green','green|red','red|black','black|red','green|black','black|green']);
 const hex=k=>PALETTE.find(p=>p.key===k).hex;
 const devs=[]; let n=0;
 for(let run=0;run<RUNS;run++){
  const [c,r]=pick(SIZES);
  Object.assign(S,{cols:c,rows:r,seed:'s'+run,share:pick([0,25,50,75,100]),large:pick([0,0,25,50,100]),orient:pick(['tall','wide','mixed']),
   doubleMode:pick(['mix','tall','pair']),stagger:rnd()<.7,stitch:pick(Object.keys(STITCHES)),accents:rnd()<.8,
   rotate:rnd()<.5,overrides:{},locks:{}});
  const bon=rnd()<.5; S.border.on=bon;
  const sides=['top','right','bottom','left']; let any=false;
  sides.forEach(s=>{S.border.sides[s]=rnd()<(rnd()<.5?1:.6);any=any||S.border.sides[s]}); if(!any)S.border.sides.top=true;
  const cfg=`${c}x${r} seed=s${run} share=${S.share} orient=${S.orient} mode=${S.doubleMode} large=${S.large} stagger=${S.stagger} rotate=${S.rotate} stitch=${S.stitch} accents=${S.accents} border=${bon?sides.filter(s=>S.border.sides[s]).join('+'):'off'}`;
  try{generate()}catch(e){bump('generate threw',cfg+' '+e.message);continue}
  let t=LAST; n++;
  // LOCKS: lock a few modules, change seed and settings, regenerate — locked modules must keep slot and pattern
  if(rnd()<.35){
   const field=t.mods.filter(m=>!m.border); const k=1+(rnd()*3|0); const chosen=[];
   for(let q=0;q<k&&field.length;q++){const m=field.splice(rnd()*field.length|0,1)[0]; lockModule(m); chosen.push({key:m.key,w:m.w,h:m.h,choice:JSON.stringify(m.choice)})}
   Object.assign(S,{seed:'s'+run+'b',share:pick([0,25,50,75,100]),large:pick([0,25,50]),orient:pick(['tall','wide','mixed']),overrides:{}});
   try{generate()}catch(e){bump('generate threw (locked)',cfg+' '+e.message);continue}
   t=LAST;
   for(const L of chosen){ const m=t.mods.find(x=>!x.border&&x.key===L.key);
     if(!m||m.w!==L.w||m.h!==L.h) bump('lock: locked module lost its slot',cfg+' '+L.key);
     else if(JSON.stringify(m.choice)!==L.choice) bump('lock: locked module changed pattern',cfg+' '+L.key);
     else if(!m.lock) bump('lock: lock flag missing',cfg+' '+L.key); }
  }
  // --- tiling: full cover, no overlap
  const cov=Array.from({length:t.rows},()=>Array(t.cols).fill(0));
  t.mods.forEach(m=>{for(let y=m.r;y<m.r+m.h;y++)for(let x=m.c;x<m.c+m.w;x++){if(y<0||x<0||y>=t.rows||x>=t.cols)bump('tiling: out of bounds',cfg);else cov[y][x]++}});
  if(cov.flat().some(v=>v!==1)) bump('tiling: gap or overlap',cfg);
  t.mods.forEach((m,i)=>{
   const id=`${cfg} mod#${i+1} ${m.border?'border-'+m.border:''} ${m.kind} ${m.motifIds}`;
   const SHAPE={S:[1,1],T:[1,2],W:[2,1],L:[2,2],LT:[2,4]};
   if(!SHAPE[m.kind]||SHAPE[m.kind][0]!==m.w||SHAPE[m.kind][1]!==m.h) bump('tiling: bad module shape',id);
   if(m.kind[0]==='L'&&m.border) bump('tiling: large module in border',id);
   // rendered colour grid
   const neg=S.accents&&m.dense, col={'1':m.cw.p,'2':m.cw.s,'3':m.cw.t};
   const R=m.grid.map(row=>[...row].map(ch=>{if(ch==='.'||!(ch in col))return '.'; if(neg&&ch!=='1')return '.'; return S.accents?col[ch]:m.cw.p}));
   const H=R.length,W=R[0].length;
   const span=n=>13*n+2*(n-1), eH=span(m.h), eW=span(m.w);
   if(H!==eH||W!==eW) bump('grid: wrong stitch-field size',id+` ${H}x${W}`);
   // fill: stitches reach all four field edges (exactly 1-stitch margin)
   const st=(y,x)=>R[y][x]!=='.';
   const top=R[0].some(v=>v!=='.'),bot=R[H-1].some(v=>v!=='.'),lef=R.some(r=>r[0]!=='.'),rig=R.some(r=>r[W-1]!=='.');
   if(!(top&&bot&&lef&&rig)) bump('fill: margin >1 stitch on rendered grid',id+` T${+top}B${+bot}L${+lef}R${+rig}`);
   // symmetry per stitch & colour
   const key=R.map(r=>r.join(','));
   const LR=R.every(r=>r.join()===[...r].reverse().join()), TB=key.every((r,y)=>r===key[H-1-y]);
   if(m.border==='corner'){ if(!(H===W&&R.every((row,y)=>row.every((v,x)=>v===R[W-1-x][y])))) bump('border: corner not C4-symmetric',id); }
   else if(m.border){ if(!(LR||TB)) bump('symmetry: border strip has no mirror axis',id); }
   else if(m.kind==='S'||m.kind==='L'){ if(!(LR||TB)) bump(`symmetry: ${m.kind==='S'?'square':'large'} has no exact axis`,id); }
   else if(m.kind==='LT'){ if(!LR) bump('symmetry: large tall not left-right symmetric',id); }
   else { if(!LR) bump('symmetry: double not mirror-symmetric across long axis',id); }
   // asymmetric motifs only as wide pairs
   if(!m.border&&m.kind!=='W'&&m.motifs.some(mo=>mo.axes&&!mo.axes.length)) bump('symmetry: asymmetric motif outside wide pair',id);
   // stacked/facing: 2-stitch gap with a centre-line connector only
   if(!m.border&&(m.how==='stacked'||m.how==='facing')){
    const vert=m.how==='stacked';
    const at=(a,bb)=>vert?R[a][bb]:R[bb][a]; // a along long axis, bb across
    let stray=0,conn=true;
    for(const a of [13,14])for(let bb=0;bb<13;bb++){const s=at(a,bb)!=='.'; if(s&&(bb<5||bb>7))stray++; if(!s&&bb>=5&&bb<=7)conn=false}
    const bird=m.motifs[0].faces;
    if(bird){ let any=false; for(const a of [13,14])for(let bb=0;bb<13;bb++) if(at(a,bb)!=='.')any=true;
      if(any) bump('spacing: facing birds joined across the gap',id); }
    else {
    if(stray) bump('spacing: stitches in the 2-stitch gap outside the connector',id);
    if(!conn) bump('connector: repeats not joined through the gap',id);
    }
    // repeat identical (stacked: same top, never flipped)
    if(vert){ for(let y=0;y<13;y++) if(R[y].some((v,x)=>x!==6&&v!==R[y+15][x])){bump('orientation: stacked repeat differs from top (flipped?)',id);break} }
   }
   // directional motifs never upside down: squares/stacked are never flipped by construction; check source vs render
   if(!m.border&&(m.how==='single'||m.how==='large')){ const g=m.motifs[0].grid; if(g.join()!==m.grid.join()&&!m.dense) bump('orientation: square motif transformed',id); }
   // contrast: every stitch colour vs background
   const used=new Set(R.flat().filter(v=>v!=='.'));
   used.forEach(k=>{ if(k===m.cw.bg) bump('colour: stitch same as background',id);
     if(BAD.has(k+'|'+m.cw.bg)) bump(`colour: forbidden pair ${k} on ${m.cw.bg}`,id);
     if(contrastRatio(hex(k),hex(m.cw.bg))<3) bump('colour: contrast < 3:1',id+` ${k} on ${m.cw.bg}`); });
   if(!used.size) bump('fill: empty module',id);
   // neighbour background clash
   m.nb.forEach(j=>{ if(j>i&&t.mods[j].cw.bg===m.cw.bg) bump('colour: adjacent modules share background',id+` & mod#${j+1}`); });
  });
  // border runs symmetric from their own centre
  if(bon){
   const bm=t.mods.filter(m=>m.border&&m.border!=='corner');
   for(const side of ['top','bottom','left','right']){
    const run=bm.filter(m=>m.border===side).map(m=>side==='top'||side==='bottom'?m.w:m.h);
    if(run.join()!==[...run].reverse().join()) bump('border: run segmentation not symmetric',cfg+' '+side+' '+run);
    const ws=bm.filter(m=>m.border===side).map(m=>m.cw.bg+'/'+m.cw.p);
    if(ws.join()!==[...ws].reverse().join()) bump('border: colours not mirrored along run',cfg+' '+side);
   }
  }
  // balance
  const sum=Object.values(t.totals).reduce((a,b)=>a+b,0);
  devs.push({sz:c*r+(bon?1e4:0),cfg,dev:Math.max(...Object.values(t.totals).map(v=>Math.abs(v/sum-.25)))});
  // SVG export structure
  const svg=new DOMParser().parseFromString(buildSVG(t,true),'image/svg+xml');
  const comp=svg.querySelector('svg > #composition');
  if(!comp||!comp.querySelector(':scope > #field')||(bon&&!comp.querySelector(':scope > #border'))) bump('svg: missing #composition/#field/#border',cfg);
  const groups=svg.querySelectorAll('#field > g, #border > g');
  if(groups.length!==t.mods.length) bump('svg: module group count mismatch',cfg+` ${groups.length}/${t.mods.length}`);
  groups.forEach(g=>{ if(!/^\d{2,}-(border-(top|bottom|left|right|corner)-)?(square|tall|wide|large|large-tall)-.+/.test(g.id)||!g.hasAttribute('data-motif')) bump('svg: bad module id/data',cfg+' '+g.id) });
 }
 // balance summary by size
 const bySize={};devs.forEach(d=>{const k=d.sz;(bySize[k]=bySize[k]||[]).push(d)});
 const bal=Object.entries(bySize).sort((a,b)=>a[0]-b[0]).map(([k,a])=>{const w=a.reduce((x,y)=>y.dev>x.dev?y:x);return `${k>=1e4?'border ':''}area=${k%1e4} runs=${a.length} avgMaxDev=${(a.reduce((s,d)=>s+d.dev,0)/a.length*100).toFixed(1)}% worst=${(w.dev*100).toFixed(1)}%`});
 return {n,V,EX,bal};
},RUNS);
console.log(`runs: ${res.n}`);
console.log('\nVIOLATIONS'); const ks=Object.keys(res.V).sort((a,b)=>res.V[b]-res.V[a]);
if(!ks.length) console.log('  none');
ks.forEach(k=>console.log(`  ${res.V[k]}× ${k}\n      e.g. ${res.EX[k]}`));
console.log('\nCOLOUR BALANCE (max deviation from 25%)'); res.bal.forEach(l=>console.log('  '+l));
const w=[...new Set(warns)];console.log(`\nconsole warnings/errors: ${warns.length}`);w.slice(0,15).forEach(x=>console.log('  '+x));
await b.close();})();
