// Author-only check. Browser skill discovery earlier returned no connected
// browsers; isolated headless Edge uses no signed-in browser profile.
// portable-export-transform-v1
let chromium;
try {
  ({chromium} = require(process.env.TE_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright'));
} catch (error) {
  throw new Error('Playwright is unavailable. Configure TE_PLAYWRIGHT_MODULE or PLAYWRIGHT_MODULE_PATH for this PC, or install it through your normal dependency workflow. No automatic acquisition is performed.');
}
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
(async()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8'));
  const asset=manifest.assets[0],name=path.basename(asset.localized_path);
  const browser=await chromium.launch({headless:true,...(process.env.TE_BROWSER_PATH ? {executablePath:process.env.TE_BROWSER_PATH} : {channel:process.env.TE_BROWSER_CHANNEL || 'msedge'})});
  try{
    const page=await browser.newPage({viewport:{width:1040,height:480},deviceScaleFactor:1});
    await page.goto(pathToFileURL(path.join(__dirname,name)).href);await page.evaluate(()=>document.fonts.ready);
    const data=await page.evaluate(()=>{
      const svg=document.querySelector('svg'),v=svg.viewBox.baseVal;
      const texts=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return{text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
      return{width:v.width,height:v.height,texts,outside:texts.filter(b=>b.x<0||b.y<0||b.x+b.w>v.width||b.y+b.h>v.height)};
    });
    if(data.outside.length)throw Error(JSON.stringify(data.outside));
    const dir=path.join(__dirname,'author-render');fs.mkdirSync(dir,{recursive:true});
    await page.locator('svg').screenshot({path:path.join(dir,name+'.png')});
    fs.writeFileSync(path.join(dir,'bounds.json'),JSON.stringify({scope:'Author render only,not independent review',renderer:'Configured headless Chromium-family browser via Playwright',localized_sha256:asset.localized_sha256,...data},null,2)+'\n');
    console.log(JSON.stringify({rendered:1,text_bounds:'PASS',scope:'Author review only'}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
