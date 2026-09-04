// Standalone local-render fallback: in-app browser runtime failed before bootstrap.
// No signed-in profiles, external websites, uploads, or user browser sessions.
// portable-export-transform-v1
let chromium;
try {
  ({chromium} = require(process.env.TE_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright'));
} catch (error) {
  throw new Error('Playwright is unavailable. Configure TE_PLAYWRIGHT_MODULE or PLAYWRIGHT_MODULE_PATH for this PC, or install it through your normal dependency workflow. No automatic acquisition is performed.');
}
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const base = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch({headless:true, ...(process.env.TE_BROWSER_PATH ? {executablePath:process.env.TE_BROWSER_PATH} : {channel:process.env.TE_BROWSER_CHANNEL || 'msedge'})});
  const page = await browser.newPage({viewport:{width:1280,height:1000},deviceScaleFactor:1});
  const errors=[]; const badResponses=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)badResponses.push([r.url(),r.status()]);});
  await page.goto('http://127.0.0.1:8763/reader/TE-B001.html',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  const dir=path.join(base,'qa','screenshots'); fs.mkdirSync(dir,{recursive:true});
  await page.screenshot({path:path.join(dir,'desktop-top.png')});
  await page.locator('#source-te').screenshot({path:path.join(dir,'telugu-source.png')});
  await page.locator('#entry-solutions').screenshot({path:path.join(dir,'entry-solutions.png')});
  await page.locator('#recheck-solutions').screenshot({path:path.join(dir,'recheck-solutions.png')});
  const desktop=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,math:document.querySelectorAll('math').length,images:[...document.images].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,complete:i.complete})),font:getComputedStyle(document.body).fontFamily}));
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:8763/reader/TE-B001.html',{waitUntil:'networkidle'});
  await page.screenshot({path:path.join(dir,'mobile-top.png')});
  await page.locator('#source-te').screenshot({path:path.join(dir,'mobile-source.png')});
  const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
  if(errors.length||badResponses.length||desktop.scrollWidth>desktop.width||mobile.scrollWidth>mobile.width||desktop.images.some(i=>!i.complete||!i.width))throw Error(JSON.stringify({errors,badResponses,desktop,mobile}));
  const hashes={}; for(const file of fs.readdirSync(dir)) hashes[file]=crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,file))).digest('hex');
  fs.writeFileSync(path.join(base,'qa','visual-render-receipt.json'),JSON.stringify({renderer:'Configured headless Chromium-family browser via Playwright; isolated local-render fallback',reason:'Portable configured runtime; originating in-app bootstrap failure is historical',desktop,mobile,errors,badResponses,screenshots:hashes,manual_inspection:'Separate status receipt; these metrics do not claim manual review'},null,2)+'\n');
  console.log(JSON.stringify({desktop,mobile,errors,badResponses})); await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
