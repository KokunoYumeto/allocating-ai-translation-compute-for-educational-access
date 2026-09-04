// Author-only local render after Browser skill connection and discovery returned
// no browser. No browser was user-specified; isolated Edge has no signed-in profile.
const {chromium}=require(process.env.TE_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
(async()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8'));
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  const receipts=[];
  try{
    const page=await browser.newPage({viewport:{width:1320,height:400},deviceScaleFactor:1});
    const dir=path.join(__dirname,'author-render');fs.mkdirSync(dir,{recursive:true});
    for(const asset of manifest.assets){
      const name=path.basename(asset.localized_path);
      await page.goto(pathToFileURL(path.join(__dirname,name)).href);
      await page.evaluate(()=>document.fonts.ready);
      const data=await page.evaluate(()=>{
        const svg=document.querySelector('svg'),v=svg.viewBox.baseVal;
        const texts=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return{text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
        return{width:v.width,height:v.height,texts,outside:texts.filter(b=>b.x<0||b.y<0||b.x+b.w>v.width||b.y+b.h>v.height)};
      });
      if(data.outside.length)throw Error(name+JSON.stringify(data.outside));
      await page.locator('svg').screenshot({path:path.join(dir,name+'.png')});
      receipts.push({name,localized_sha256:asset.localized_sha256,...data});
    }
    fs.writeFileSync(path.join(dir,'bounds.json'),JSON.stringify({scope:'Author render only, not independent review',renderer:'Isolated headless Edge',receipts},null,2)+'\n');
    console.log(JSON.stringify({rendered:receipts.length,text_bounds:'PASS',scope:'Author review only'}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
