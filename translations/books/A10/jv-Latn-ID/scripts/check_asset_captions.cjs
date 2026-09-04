// Targeted rendering check for the six inherited-asset captions only.
const {chromium}=require(process.argv[2]||'playwright');
const path=require('path'),fs=require('fs');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage();const results=[];
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  for(const track of ['jv-academic','jv-conversation','id-academic']){
   await page.goto(pathToFileURL(path.join(root,track+'.html')).href);
   await page.evaluate(()=>document.querySelectorAll('details').forEach(e=>e.open=true));
   for(const mid of ['fs-id1167836692989','fs-id1169149089480']){
    const fig=page.locator('#'+mid);await fig.scrollIntoViewIfNeeded();
    await fig.locator('img').evaluate(i=>{i.loading='eager'});
    await page.waitForFunction(id=>document.querySelector('#'+id+' img').complete,mid);
    const state=await fig.evaluate(e=>({captionCount:e.querySelectorAll('[data-provenance]').length,imageLoaded:!!e.querySelector('img').naturalWidth,pageOverflow:document.documentElement.scrollWidth>innerWidth+2,text:e.querySelector('figcaption').textContent}));
    if(state.captionCount!==1||!state.imageLoaded||state.pageOverflow)throw new Error(JSON.stringify(state));
    results.push({track,width,media_id:mid,...state});
    if(track==='jv-academic'&&((width===1280)||(width===390&&mid==='fs-id1169149089480'))){
     const row=fig.locator('xpath=ancestor::tr[1]');
     await row.screenshot({path:path.join(root,'provenance/visual',`asset-${mid}-${width}.png`)});
    }
   }
  }
 }
 await browser.close();
 fs.writeFileSync(path.join(root,'provenance/ASSET-OVERRIDE-VISUAL.json'),JSON.stringify({schema:'targeted-two-asset-caption-layout-v1',status:'pass',browser:'Edge Chromium headless',checks:results,scope:'Two affected figures in three readers at 1280px/390px; captions expanded, loaded images, no page overflow.',screenshots_inspection_record:'provenance/ASSET-OVERRIDE-VISUAL.md'},null,2)+'\n');
 console.log('Targeted caption checks passed:',results.length);
})().catch(e=>{console.error(e);process.exitCode=1});
