// Isolated local-render fallback; in-app setup fails before browser connection.
const {chromium}=require(process.env.TE_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const unit=process.argv[2];
if(!/^TE-B\d{3}$/.test(unit||''))throw Error('Pass one unit ID');
const base=path.resolve(__dirname,'..');
(async()=>{
  const edge=process.env.TE_BROWSER_PATH || path.join(process.env.LOCALAPPDATA || '', 'Microsoft/Edge/Application/msedge.exe');
  const chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
  const usingEdge=fs.existsSync(edge);
  if(!usingEdge&&!fs.existsSync(chrome))throw Error('No isolated local Chromium-family executable found');
  const browser=await chromium.launch(usingEdge?{headless:true,executablePath:edge}:{headless:true,executablePath:chrome});
  try{
    const page=await browser.newPage({viewport:{width:1280,height:1000},deviceScaleFactor:1});
    const errors=[],badResponses=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.status()>=400)badResponses.push([r.url(),r.status()]);});
    await page.goto(`http://127.0.0.1:8763/reader/${unit}.html`,{waitUntil:'networkidle'});
    // A large reader can make the isolated browser cancel an otherwise valid
    // image decode while dozens of assets arrive together. Retry only images
    // that actually completed with no intrinsic width, then require decode.
    await page.locator('img').evaluateAll(async images=>{
      for(const image of images){
        for(let attempt=0;attempt<2&&(!image.complete||!image.naturalWidth);attempt++){
          const src=image.getAttribute('src');
          image.removeAttribute('src');
          await new Promise(resolve=>requestAnimationFrame(()=>resolve()));
          image.setAttribute('src',src);
          try{await image.decode();}catch{}
        }
      }
    });
    const dir=path.join(base,'qa','screenshots',unit);fs.mkdirSync(dir,{recursive:true});
    const initialState=await page.evaluate(()=>({sourceAnswers:[...document.querySelectorAll('#source-te details.cn-solution')].map(d=>({id:d.id,open:d.open}))}));
    const expectedAnswers={'TE-B008':29,'TE-B011':1,'TE-B012':1,'TE-B019':42};
    if(unit in expectedAnswers&&(initialState.sourceAnswers.length!==expectedAnswers[unit]||initialState.sourceAnswers.some(d=>d.open)))throw Error('Practice/readiness source answers must begin closed');
    const keyboard={};
    // Bind the node once: opening it changes :not([open]) membership.
    const firstSummary=await page.locator('details:not([open]) > summary').first().elementHandle();
    if(firstSummary){
      await firstSummary.focus();
      await firstSummary.press('Enter');
      if(!await firstSummary.evaluate(s=>s.parentElement.open))throw Error('Enter did not open answer');
      await firstSummary.press('Space');
      if(await firstSummary.evaluate(s=>s.parentElement.open))throw Error('Space did not close answer');
      keyboard.answer_enter_space=true;
    }
    if(initialState.sourceAnswers.length)await page.locator('#source-te .cn-exercise').first().screenshot({path:path.join(dir,'source-first-answer-closed.png')});
    await page.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
    if(initialState.sourceAnswers.length)await page.locator('#source-te .cn-exercise').first().screenshot({path:path.join(dir,'source-first-answer-open.png')});
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:path.join(dir,'desktop-top.png')});
    if(['TE-B009','TE-B010','TE-B011','TE-B012','TE-B013'].includes(unit))await page.locator('#source-te').screenshot({path:path.join(dir,'source-complete.png')});
    const media=page.locator('#source-te .cn-media');
    for(let i=0;i<await media.count();i++){
      const figure=media.nth(i),img=figure.locator('img');
      await img.screenshot({path:path.join(dir,`diagram-${String(i+1).padStart(2,'0')}.png`)});
      const src=await img.getAttribute('src');
      // A chart inside a wide table may be clipped by an ancestor, even when
      // its own wrapper is not overflowing. Capture every SVG independently.
      if(src.endsWith('.svg')){
        const native=await browser.newPage({viewport:{width:2400,height:900},deviceScaleFactor:1});
        try{
          await native.goto(new URL(src,`http://127.0.0.1:8763/reader/${unit}.html`).href,{waitUntil:'networkidle'});
          await native.locator('svg').screenshot({path:path.join(dir,`diagram-${String(i+1).padStart(2,'0')}-full.png`)});
        }finally{await native.close();}
      }
    }
    if(unit==='TE-B019'){
      const originals=page.locator('#source-en .cn-media img');
      for(let i=0;i<await originals.count();i++)await originals.nth(i).screenshot({path:path.join(dir,`original-${String(i+1).padStart(2,'0')}.png`)});
    }
    const tables=page.locator('#source-te .table-scroll');
    for(let i=0;i<await tables.count();i++){
      const table=tables.nth(i);
      // Element screenshots may have scrolled an ancestor to reveal a diagram.
      // Record the instruction side explicitly before the optional right side.
      await table.evaluate(t=>t.scrollLeft=0);
      await table.screenshot({path:path.join(dir,`table-${i+1}.png`)});
      if(await table.evaluate(t=>t.scrollWidth>t.clientWidth)){
        await table.evaluate(t=>t.scrollLeft=t.scrollWidth);
        await table.screenshot({path:path.join(dir,`table-${i+1}-right.png`)});
        await table.evaluate(t=>t.scrollLeft=0);
      }
    }
    const bridge=page.locator(`[id="${unit.replace('TE-','')}-bridge"]`);
    // B019 has 82 fully worked cards and exceeds practical single-image height.
    if(await bridge.count()&&unit!=='TE-B019')await bridge.screenshot({path:path.join(dir,'bridge.png')});
    if(await bridge.count()){
      const cards=bridge.locator('aside,details');
      for(let i=0;i<await cards.count();i++)await cards.nth(i).screenshot({path:path.join(dir,`bridge-card-${i+1}.png`)});
      const routing=bridge.locator('[id$="-routing"], [id$="-self-check-support"]');
      for(let i=0;i<await routing.count();i++)await routing.nth(i).screenshot({path:path.join(dir,`bridge-section-${i+1}.png`)});
      const extraSections={
        'TE-B013':['B013-entry','B013-K1','B013-K2','B013-recheck'],
        'TE-B014':['B014-entry','B014-K1','B014-K2','B014-K3','B014-recheck','B014-activity-boundary'],
        'TE-B015':['B015-conventions','B015-K1','B015-K2','B015-K3','B015-final-check'],
        'TE-B016':['B016-K1','B016-K2','B016-K3'],
        'TE-B017':['B017-K1','B017-K2','B017-K3','B017-resource-boundary'],
        'TE-B018':['B018-K1','B018-K2','B018-K3','B018-K4','B018-boundary'],
        'TE-B019':['B019-writing','B019-selfcheck-rubric']
      };
      for(const id of extraSections[unit]||[])await page.locator('#'+id).screenshot({path:path.join(dir,id+'.png')});
    }
    const desktop=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,math:document.querySelectorAll('math').length,tables:document.querySelectorAll('table').length,images:[...document.images].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,complete:i.complete})),font:getComputedStyle(document.body).fontFamily}));
    await page.setViewportSize({width:390,height:844});
    await page.goto(`http://127.0.0.1:8763/reader/${unit}.html`,{waitUntil:'networkidle'});
    await page.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
    await page.screenshot({path:path.join(dir,'mobile-top.png')});
    if(['TE-B009','TE-B010','TE-B011','TE-B012','TE-B013'].includes(unit))await page.locator('#source-te').screenshot({path:path.join(dir,'mobile-source-complete.png')});
    // Prefer source tables; practice-only units still need an actual bridge-table pan.
    const mobileTables=await tables.count()?tables:page.locator('.table-scroll');
    if(await mobileTables.count())await mobileTables.first().screenshot({path:path.join(dir,'mobile-table.png')});
    if(await mobileTables.count()){
      await mobileTables.first().evaluate(t=>t.scrollLeft=t.scrollWidth);
      await mobileTables.first().screenshot({path:path.join(dir,'mobile-table-right.png')});
    }
    const wideMedia=page.locator('#source-te .media-scroll');
    if(await wideMedia.count()){
      await wideMedia.first().screenshot({path:path.join(dir,'mobile-chart-left.png')});
      await wideMedia.first().evaluate(t=>t.scrollLeft=t.scrollWidth);
      await wideMedia.first().screenshot({path:path.join(dir,'mobile-chart-right.png')});
    }
    const scrollable=await mobileTables.count()?mobileTables.first():wideMedia.first();
    if(await scrollable.count()&&await scrollable.evaluate(t=>t.scrollWidth>t.clientWidth)){
      await scrollable.evaluate(t=>t.scrollLeft=0);
      await scrollable.focus();
      await scrollable.press('ArrowRight');
      await page.waitForFunction(()=>document.activeElement.scrollLeft>0);
      keyboard.mobile_region_arrow_pan=true;
      await scrollable.evaluate(t=>t.scrollLeft=t.scrollWidth);
    }
    const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,all_details_open:[...document.querySelectorAll('details')].every(d=>d.open),tables:[...document.querySelectorAll('.table-scroll')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth,scrollLeft:t.scrollLeft,overflow:getComputedStyle(t).overflowX})),charts:[...document.querySelectorAll('#source-te .media-scroll')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth,scrollLeft:t.scrollLeft,overflow:getComputedStyle(t).overflowX}))}));
    if(errors.length||badResponses.length||desktop.scrollWidth>desktop.width||mobile.scrollWidth>mobile.width||desktop.images.some(i=>!i.complete||!i.width))throw Error(JSON.stringify({errors,badResponses,desktop,mobile}));
    const screenshots={};for(const file of fs.readdirSync(dir))screenshots[file]=crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,file))).digest('hex');
    fs.writeFileSync(path.join(base,'qa',`${unit}.visual.json`),JSON.stringify({unit,renderer:(usingEdge?'Headless Edge':'Headless Chrome')+' via Playwright; isolated local fallback',reader_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(base,'reader',unit+'.html'))).digest('hex'),initialState,keyboard,desktop,mobile,errors,badResponses,screenshots,manual_review:'Recorded separately; metrics do not claim human/native review'},null,2)+'\n');
    console.log(JSON.stringify({unit,desktop,mobile,errors,badResponses}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
