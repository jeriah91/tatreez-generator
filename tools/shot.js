const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('file://'+require('path').resolve(__dirname,'../dist/index.html'));await p.waitForTimeout(400);
const steps=JSON.parse(process.argv[2]||'[]');
for(const s of steps){await p.evaluate(s);await p.waitForTimeout(300);}
await p.screenshot({path:process.argv[3]||'shot.png'});
console.log('errors',JSON.stringify(errs));
console.log(await p.evaluate(()=>document.getElementById('status').innerText));
await b.close();})();
