// Local-only fallback: in-app browser runtime failed before setup (os error 3).
// Never attaches to the user's browser, profiles, sessions or external sites.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium}=require(process.env.BN_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const lang = path.resolve(__dirname, '..');
const shots = path.resolve(lang, '../../tmp/bn-Beng-IN-visual');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const requested=process.argv.slice(2);
const names=requested.length?requested:['U01-companion','U01-source-faithful'];
const browserPath=process.env.BN_BROWSER_PATH || [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
].find(p=>fs.existsSync(p));
assert(browserPath,'No isolated Chromium-family browser executable is available');
const browserLabel=path.basename(browserPath).toLowerCase().startsWith('msedge')?'Edge':'Chrome';
let browser;
(async () => {
  fs.mkdirSync(shots, {recursive:true});
  browser = await chromium.launch({headless:true, executablePath:browserPath});
  const context = await browser.newContext({viewport:{width:1200,height:1000}});
  await context.route('**/*', route => /^(file:|data:)/.test(route.request().url()) ? route.continue() : route.abort());
  const results=[];
  for (const name of names) {
    const page=await context.newPage();
    const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.join(lang,'reader',name+'.html')).href);
    await page.evaluate(()=>document.fonts.ready);
    for (const width of [1200,390]) {
      await page.setViewportSize({width,height:1000});
      const info=await page.evaluate(()=>({
        width:document.documentElement.clientWidth,
        scrollWidth:document.documentElement.scrollWidth,
        height:document.documentElement.scrollHeight,
        images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0,alt:!!i.alt})),
        headings:[...document.querySelectorAll('h1,h2')].map(e=>({text:e.textContent,height:e.getBoundingClientRect().height})),
        math:[...document.querySelectorAll('math')].map(e=>({width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,text:e.textContent.trim(),spacingOnly:[...e.querySelectorAll('*')].every(c=>['mrow','mspace'].includes(c.localName)),parent:e.closest('[id]')?.id})),
        bengaliFont:document.fonts.check('19px "Nirmala UI"','ভগ্নাংশ সমীকরণ'),
        longDivision:[...document.querySelectorAll('menclose[notation~="longdiv"]')].map(e=>({top:parseFloat(getComputedStyle(e).borderTopWidth),left:parseFloat(getComputedStyle(e).borderLeftWidth),width:e.getBoundingClientRect().width})),
        cancellationStrokes:[...document.querySelectorAll('menclose[notation~="updiagonalstrike"]')].map(e=>({background:getComputedStyle(e).backgroundImage,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})),
        scrollRegions:[...document.querySelectorAll('.math-scroll')].map(e=>({focusable:e.tabIndex===0,label:e.getAttribute('aria-label'),width:e.clientWidth,scrollWidth:e.scrollWidth,overflowX:getComputedStyle(e).overflowX})),
        overflow:[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.parentElement?.closest('.math-scroll')).map(e=>({id:e.id,tag:e.tagName,x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,text:e.textContent.slice(0,180)}))
      }));
      if(info.scrollWidth!==info.width || info.overflow.length){
        const failure=`${name.replaceAll('/','_')}-${width}-failure.png`;
        const y=await page.evaluate(()=>{const e=[...document.querySelectorAll('main *')].find(e=>e.getBoundingClientRect().right>innerWidth+1);return e?e.getBoundingClientRect().top+scrollY:0});
        await page.evaluate(y=>scrollTo(0,Math.max(0,y-100)),y);
        await page.screenshot({path:path.join(shots,failure)});
        console.error(JSON.stringify({page:name,width,scrollWidth:info.scrollWidth,overflow:info.overflow,failure},null,2));
      }
      assert.equal(info.scrollWidth,info.width,`Horizontal page overflow: ${name} at ${width}px`);
      assert.deepEqual(info.overflow,[],'Overflowing content');
      assert(info.scrollRegions.every(r=>r.focusable&&r.label&&r.width>0&&r.overflowX==='auto'),'Long math must remain accessible in an explicitly labelled scroll region');
      for(const region of await page.locator('.math-scroll').all()) {
        await region.evaluate(e=>e.scrollLeft=e.scrollWidth);
        assert(await region.evaluate(e=>Math.abs(e.scrollLeft-(e.scrollWidth-e.clientWidth))<=1),'Long math cannot be reached by scrolling');
        await region.evaluate(e=>e.scrollLeft=0);
      }
      assert(info.images.every(i=>i.loaded&&i.alt),'Image missing');
      assert(info.math.every(m=>m.spacingOnly || (m.width>0&&m.height>0)),`MathML not rendered: ${name} at ${width}px: ${JSON.stringify(info.math.filter(m=>!m.spacingOnly&&(m.width<=0||m.height<=0)))}`);
      assert(info.bengaliFont,'Bengali font unavailable');
      assert(info.longDivision.every(e=>e.top>0&&e.left>0&&e.width>0),'Long-division enclosure must be visible');
      assert(info.cancellationStrokes.every(e=>e.width>0&&e.height>0&&e.background.includes('linear-gradient')),'Source cancellation strokes must remain visible');
      const screenshotFiles=[];
      // All desktop content is reviewed in overlapping viewport tiles; narrow top tests wrapping.
      const positions=width===1200?Array.from({length:Math.ceil(info.height/900)},(_,i)=>i*900):[0,Math.max(0,info.height-1000)];
      for (let i=0;i<positions.length;i++) {
        await page.evaluate(y=>scrollTo(0,y),positions[i]);
        const filename=`${name.replaceAll('/','_')}-${width}-${i+1}.png`;
        await page.screenshot({path:path.join(shots,filename)});
        screenshotFiles.push(filename);
      }
      results.push({page:name,width,...info,errors,screenshotFiles});
    }
    assert.deepEqual(errors,[]);
    const digest=crypto.createHash('sha256').update(fs.readFileSync(path.join(lang,'reader',name+'.html'))).digest('hex');
    fs.mkdirSync(path.join(lang,'qa','browser'),{recursive:true});
    fs.writeFileSync(path.join(lang,'qa','browser',name.replaceAll('/','_')+'.json'),JSON.stringify({method:`isolated ${browserLabel} headless via bundled Playwright; no external requests`,browser_executable:browserPath,page:name,input_sha256:digest,results:results.filter(r=>r.page===name)},null,2)+'\n');
    await page.close();
  }
  await browser.close();
  const inputs=Object.fromEntries(names.map(n=>[n+'.html',crypto.createHash('sha256').update(fs.readFileSync(path.join(lang,'reader',n+'.html'))).digest('hex')]));
  fs.writeFileSync(path.join(lang,'qa',requested.length?'browser-sections-check.json':'browser-check.json'),JSON.stringify({method:`isolated ${browserLabel} headless via bundled Playwright; in-app runtime unavailable`,browser_executable:browserPath,screenshots:path.relative(lang,shots),inputs,results},null,2)+'\n');
  console.log(JSON.stringify(results.map(r=>({page:r.page,width:r.width,height:r.height,images:r.images.length,math:r.math.length,screenshots:r.screenshotFiles})),null,2));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>{if(browser)await browser.close()});
