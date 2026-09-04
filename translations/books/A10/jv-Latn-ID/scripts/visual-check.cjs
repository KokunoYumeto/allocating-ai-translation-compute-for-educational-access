// Usage: node scripts/visual-check.cjs PATH_TO_PLAYWRIGHT_PACKAGE
// Opens only this generated package in headless Edge; no remote requests needed.
const {chromium}=require(process.argv[2] || 'playwright');
const path=require('path');
const fs=require('fs');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 const records=[];const errors=[];
 fs.mkdirSync(path.join(root,'provenance','visual'),{recursive:true});
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  for(const name of ['index.html','jv-academic.html','jv-conversation.html','id-academic.html']){
   await page.goto(pathToFileURL(path.join(root,name)).href);
   await page.evaluate(()=>{document.querySelectorAll('details').forEach(e=>e.open=true);document.querySelectorAll('img').forEach(e=>e.loading='eager')});
   await page.waitForFunction(()=>[...document.images].every(i=>i.complete));
   const state=await page.evaluate(()=>({
    width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    brokenImages:[...document.images].filter(i=>!i.naturalWidth).length,
    images:document.images.length,math:document.querySelectorAll('math').length,
    sourceIDs:document.querySelectorAll('[data-source-id]').length,
    font: getComputedStyle(document.querySelector('h1')).fontFamily,
    h1:document.querySelector('h1').textContent,
    clippedText:[...document.querySelectorAll('p,h1,h2,h3,.para')].filter(e=>{
      const r=e.getBoundingClientRect(); return r.width>innerWidth && !e.closest('.table-scroll,.equation');
    }).length
   }));
   if(state.brokenImages||state.scrollWidth>width+2||state.clippedText) errors.push({name,width,...state});
   records.push({file:name,...state});
   if(name==='index.html'&&width===1280)await page.screenshot({path:path.join(root,'provenance/visual/desktop-index.png')});
   if(name==='jv-academic.html'&&width===390)await page.screenshot({path:path.join(root,'provenance/visual/mobile-opening.png')});
   if(name==='jv-academic.html'&&width===1280){
    await page.locator('#fs-id1170654940588').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(root,'provenance/visual/desktop-like-terms.png')});
   }
  }
 }
 await browser.close();
 fs.writeFileSync(path.join(root,'provenance/VISUAL-QA.json'),JSON.stringify({
  schema:'headless-browser-layout-v1',browser:'Microsoft Edge / Chromium',status:errors.length?'fail':'automated_pass',
  modes:'1280px desktop and 390px mobile; all source answer and description disclosures expanded for geometry checks',
  records,errors,visual_inspection:'Screenshots produced; agent inspection recorded separately before final package checks.',
  limits:'DOM geometry and image loading are deterministic checks, not a human or screen-reader usability study.'
 },null,2)+'\n');
 console.log(JSON.stringify({records:records.length,errors},null,2));
 if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
