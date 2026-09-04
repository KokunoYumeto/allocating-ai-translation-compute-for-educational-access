// Isolated, offline headless browser QA; no user browser profile is opened.
const fs=require('fs'),path=require('path');
const {chromium}=require(process.argv[2]);
const base=__dirname;
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.argv[3]});
 const results=[], screenshots=[];
 try{
  const context=await browser.newContext();
  await context.route('https://**/*',route=>route.abort());
  await context.route('http://**/*',route=>route.abort());
  const page=await context.newPage();
  const files=['index.html',...fs.readdirSync(path.join(base,'reader')).filter(n=>/^a10.*\.html$/.test(n)).map(n=>'reader/'+n)];
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:900});
   for(const file of files){
    await page.goto('file:///'+path.join(base,file).replaceAll('\\','/'));
    await page.evaluate(()=>document.fonts.ready);
    const r=await page.evaluate(()=>({
      width:innerWidth,documentWidth:document.documentElement.scrollWidth,bodyDirection:getComputedStyle(document.body).direction,
      brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),
      mathCount:document.querySelectorAll('math').length,
      nonLtrMath:[...document.querySelectorAll('math')].filter(x=>getComputedStyle(x).direction!=='ltr').length,
      emptyParagraphs:[...document.querySelectorAll('p')].filter(x=>!x.textContent.trim()&&!x.querySelector('*')).length,
      clippedSourceBoxes:[...document.querySelectorAll('[data-source-key]')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&(b.left< -1||b.right>innerWidth+1)&&!e.closest('.table-scroll,.figure-scroll,.source-table-scroll')}).map(e=>e.getAttribute('data-source-key')),
      localScrollers:[...document.querySelectorAll('.source-table-scroll,.table-scroll,.figure-scroll')].filter(x=>x.scrollWidth>x.clientWidth+1).length
    }));
    results.push({file,...r});
    if(file==='index.html'||file==='reader/a10-unit-008.html'||(width===1280&&['reader/a10-preface.html','reader/a10-introduction.html','reader/a10-unit-005.html'].includes(file))){
     const name='visual/'+file.replace('reader/','').replace('.html','')+'-'+width+'.png';
     fs.mkdirSync(path.join(base,'visual'),{recursive:true});
     await page.screenshot({path:path.join(base,name),fullPage:false});screenshots.push(name);
    }
    if(file==='reader/a10-unit-008.html'){
      await page.locator('#fs-id1167836504155').scrollIntoViewIfNeeded();
      const name='visual/evaluation-table-'+width+'.png';await page.screenshot({path:path.join(base,name)});screenshots.push(name);
      if(width===390){
       await page.locator('#fs-id1167836504155 .source-table-scroll').evaluate(e=>{e.scrollLeft=e.scrollWidth});
       const last='visual/evaluation-table-390-scrolled.png';await page.screenshot({path:path.join(base,last)});screenshots.push(last);
      }
    }
   }
  }
  fs.writeFileSync(path.join(base,'visual/browser-results.json'),JSON.stringify({engine:'Chromium / Microsoft Edge, isolated headless context',network:'All HTTP/HTTPS requests blocked; file URLs only',results,screenshots},null,2));
  console.log(JSON.stringify({pages:results.length,screenshots:screenshots.length,failures:results.filter(r=>r.documentWidth>r.width+1||r.brokenImages.length||r.nonLtrMath||r.clippedSourceBoxes.length)}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
