const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+require('path').resolve(__dirname,'../dist/index.html'));await p.waitForTimeout(300);
const r=await p.evaluate(()=>{const out=[];
for(const [c,r] of [[1,1],[2,2],[3,3],[4,3],[5,7],[8,2],[10,10]]){let worst=0,avg=0,nbClash=0,n=0;
 for(let s=0;s<20;s++){S.cols=c;S.rows=r;S.seed='t'+s;S.overrides={};generate();const t=LAST;
  const sum=Object.values(t.totals).reduce((a,b)=>a+b,0);const dev=Math.max(...Object.values(t.totals).map(v=>Math.abs(v/sum-.25)));
  worst=Math.max(worst,dev);avg+=dev;n++;
  t.mods.forEach(m=>m.nb.forEach(j=>{if(t.mods[j].cw.bg===m.cw.bg)nbClash++}));}
 out.push(`${c}x${r} avgMaxDev=${(avg/n*100).toFixed(1)}% worst=${(worst*100).toFixed(1)}% bgClashes=${nbClash}`);}
return out.join('\n')});console.log(r);await b.close();})();
