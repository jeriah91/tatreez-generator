const { chromium } = require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const f of process.argv.slice(2)){const s=fs.readFileSync(f,'utf8').replace(/<\?xml[^>]*>/,'');await p.setContent(s);
const r=await p.evaluate(()=>{const out={rects:[],paths:[],classes:{}};document.querySelectorAll('rect').forEach(e=>{const bb=e.getBBox();out.rects.push([e.getAttribute('class'),bb.x,bb.y,bb.width,bb.height].join(' '))});
const ps=[...document.querySelectorAll('path,polygon,circle')];out.n=ps.length;const ws={};ps.forEach(e=>{const bb=e.getBBox();const k=bb.width.toFixed(1)+'x'+bb.height.toFixed(1);ws[k]=(ws[k]||0)+1;});out.sizes=ws;out.sample=ps.slice(0,6).map(e=>{const bb=e.getBBox();return [e.tagName,e.getAttribute('class'),bb.x.toFixed(2),bb.y.toFixed(2)].join(' ')});out.tags=[...new Set(ps.map(e=>e.tagName))];return out});
console.log(f,JSON.stringify(r));}
await b.close();})();
