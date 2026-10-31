const { chromium } = require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const f of process.argv.slice(2)){const s=fs.readFileSync(f,'utf8').replace(/<\?xml[^>]*>/,'');await p.setContent(s);
const r=await p.evaluate(()=>{const svg=document.querySelector('svg');const vb=svg.viewBox.baseVal;const ps=[...document.querySelectorAll('path')];const bb0=ps[0].getBBox();const cell=bb0.width;
const cols=Math.round(vb.width/cell),rows=Math.round(vb.height/cell);const g=[...Array(rows)].map(()=>Array(cols).fill('.'));
const cls={};let k=0;const sym='abcdefg';
ps.forEach(e=>{const bb=e.getBBox();const c=Math.round(bb.x/cell),r=Math.round(bb.y/cell);const cl=getComputedStyle(e).fill;if(!(cl in cls))cls[cl]=sym[k++];if(g[r])g[r][c]=cls[cl];});
return {cell,cols,rows,cls,bg:(document.querySelector('rect')?getComputedStyle(document.querySelector('rect')).fill:'none'),g:g.map(x=>x.join('')).join('\n')}});
console.log('== '+f,r.cell,r.cols+'x'+r.rows,JSON.stringify(r.cls),'bg',r.bg);console.log(r.g);}
await b.close();})();
