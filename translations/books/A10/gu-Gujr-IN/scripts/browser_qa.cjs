/* Bounded offline visual/geometry check. Usage: node scripts/browser_qa.cjs
 * Playwright must resolve through normal NODE_PATH; uses installed Chrome.
 * This is not a native-speaker or assistive-technology certification.
 */
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage();
  const report={schema:'gu-a10-browser-qa-v1',browser:'installed Chrome via Playwright',networkRuntimeRequests:[],pages:[],screenshots:[]};
  page.on('request',r=>{if(/^https?:/.test(r.url()))report.networkRuntimeRequests.push(r.url());});
  const pkg=JSON.parse(fs.readFileSync(path.join(root,'PACKAGE.json'),'utf8'));
  fs.mkdirSync(path.join(root,'qa-visual'),{recursive:true});
  for(const width of [1100,390]){
    await page.setViewportSize({width,height:1000});
    for(const file of ['index.html','attribution.html','support/fractions.html',...pkg.coverage.map(x=>x.reader),...pkg.coverage.filter(x=>x.recovered_added_answers).map(x=>`reader/a10-${x.module}-answers.html`)]){
      await page.goto(pathToFileURL(path.join(root,file)).href,{waitUntil:'load'});
      await page.evaluate(async()=>{await document.fonts.ready;document.querySelectorAll('details').forEach(x=>x.open=true);document.querySelectorAll('img').forEach(x=>x.loading='eager');});
      await page.waitForFunction(()=>Array.from(document.images).every(x=>x.complete));
      const m=await page.evaluate(()=>({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,fontLoaded:document.fonts.check('18px Gujarati'),brokenImages:Array.from(document.images).filter(x=>!x.naturalWidth).map(x=>x.getAttribute('src')),mathCount:document.querySelectorAll('math').length,svgCount:document.querySelectorAll('svg').length,openDetails:document.querySelectorAll('details[open]').length}));
      report.pages.push({file,width,...m});
      if(file==='index.html'||file==='support/fractions.html'||file==='reader/a10-m82456.html'){
        const label=file==='index.html'?'index':file==='support/fractions.html'?'fraction-guide':'source-fractions';
        const dest=`qa-visual/${width}-${label}.png`;
        await page.screenshot({path:path.join(root,dest)});report.screenshots.push(dest);
      }
      if(file==='support/fractions.html'){
        const diagramGeometry=await page.evaluate(()=>Array.from(document.querySelectorAll('figure svg')).map(svg=>({
          title:svg.querySelector('title').textContent,
          rectangles:svg.querySelectorAll('rect').length,
          escapedText:Array.from(svg.querySelectorAll('text')).filter(t=>{const b=t.getBBox(),v=svg.viewBox.baseVal;return b.x<v.x-1||b.y<v.y-1||b.x+b.width>v.x+v.width+1||b.y+b.height>v.y+v.height+1;}).map(t=>t.textContent)
        })));
        report.pages[report.pages.length-1].diagramGeometry=diagramGeometry;
        for(const id of ['fs-id1170654189085','fs-id1170652648117','fs-id1170652648184','fs-id1170654047650']){
          const loc=page.locator(`#answer-${id} figure`);
          const dest=`qa-visual/${width}-${id}.png`;
          await loc.screenshot({path:path.join(root,dest)});report.screenshots.push(dest);
        }
      }
    }
  }
  report.status=report.pages.every(p=>p.fontLoaded&&!p.brokenImages.length&&p.scrollWidth<=p.viewport&&(!p.diagramGeometry||p.diagramGeometry.every(d=>!d.escapedText.length)))&&!report.networkRuntimeRequests.length?'pass':'needs-correction';
  fs.writeFileSync(path.join(root,'BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
  process.stdout.write(JSON.stringify({status:report.status,pages:report.pages.length,failures:report.pages.filter(p=>!p.fontLoaded||p.brokenImages.length||p.scrollWidth>p.viewport),screenshots:report.screenshots.length})+'\n');
})().catch(e=>{process.stderr.write(String(e)+'\n');process.exit(1);});
