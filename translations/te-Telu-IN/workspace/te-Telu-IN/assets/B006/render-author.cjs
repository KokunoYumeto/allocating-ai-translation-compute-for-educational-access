// Author-only layout checks. No independent-review or native-approval claim.
// The browser skill was followed; runtime discovery reported no browsers.
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
  const browser=await chromium.launch({headless:true,...(process.env.TE_BROWSER_PATH ? {executablePath:process.env.TE_BROWSER_PATH} : {channel:process.env.TE_BROWSER_CHANNEL || 'msedge'})});
  try{
    const page=await browser.newPage({viewport:{width:1200,height:620},deviceScaleFactor:1});
    const dir=path.join(__dirname,'author-render');fs.mkdirSync(dir,{recursive:true});
    const checks=[];
    for(const asset of manifest.assets){
      const name=path.basename(asset.localized_path);
      await page.goto(pathToFileURL(path.join(__dirname,name)).href);
      await page.evaluate(()=>document.fonts.ready);
      const data=await page.evaluate(()=>{
        const svg=document.querySelector('svg'),view=svg.viewBox.baseVal;
        const texts=[...svg.querySelectorAll('text')].map(t=>{
          const b=t.getBBox();return{text:t.textContent,role:t.dataset.role,x:b.x,y:b.y,w:b.width,h:b.height};
        });
        return{width:view.width,height:view.height,texts,outside:texts.filter(b=>b.x<0||b.y<0||b.x+b.w>view.width||b.y+b.h>view.height)};
      });
      if(data.outside.length)throw Error(name+' clipping: '+JSON.stringify(data.outside));
      await page.locator('svg').screenshot({path:path.join(dir,name+'.png')});
      checks.push({name,...data});
    }
    fs.writeFileSync(path.join(dir,'bounds.json'),JSON.stringify({scope:'Author render only, not independent review',renderer:'Configured headless Chromium-family browser via Playwright',checks},null,2)+'\n');
    console.log(JSON.stringify({rendered:checks.length,text_bounds:'PASS',scope:'Author review only'}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
