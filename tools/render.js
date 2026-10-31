const { chromium } = require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{const dir=process.argv[2];const files=fs.readdirSync(dir).filter(f=>f.endsWith('.svg')).sort((a,b)=>parseInt(a.match(/\d+/))-parseInt(b.match(/\d+/)));
let html='<body style="margin:0;background:#888;display:flex;flex-wrap:wrap;gap:10px;padding:10px;width:1400px">';
for(const f of files){const s=fs.readFileSync(path.join(dir,f),'utf8').replace(/<\?xml[^>]*>/,'');html+=`<div style="color:#fff;font:12px sans-serif"><div style="height:${f.includes('27')?320:200}px">${s.replace('<svg','<svg style="height:100%;width:auto"')}</div>${f}</div>`}
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1420,height:800}});await p.setContent(html);await p.screenshot({path:process.argv[3],fullPage:true});await b.close();})();
