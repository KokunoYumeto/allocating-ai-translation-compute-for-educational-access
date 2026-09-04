/* Local offline reader rendering only. One bounded browser tree, always closed. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = path.resolve(__dirname, '..');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const mime = {'.html':'text/html; charset=utf-8','.ttf':'font/ttf','.png':'image/png','.svg':'image/svg+xml','.css':'text/css','.pdf':'application/pdf','.json':'application/json','.md':'text/plain; charset=utf-8'};
const server = http.createServer((req,res) => {
  const rel = decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/+/, '');
  const file = path.resolve(base, rel);
  if (!file.startsWith(base + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {res.writeHead(404);res.end();return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(file)] || 'application/octet-stream'});fs.createReadStream(file).pipe(res);
});
(async()=>{
 let browser;
 const qa = path.join(base,'qa'); fs.mkdirSync(qa,{recursive:true});
 const shots = path.join(qa,'visual'); fs.mkdirSync(shots,{recursive:true});
 const pdfdir = path.join(base,'output/pdf'); fs.mkdirSync(pdfdir,{recursive:true});
 try {
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const url = `http://127.0.0.1:${server.address().port}/reader/opening.html`;
  browser = await chromium.launch({headless:true,executablePath:process.env.BROWSER_EXECUTABLE || undefined});
  const context = await browser.newContext({viewport:{width:1280,height:1000},deviceScaleFactor:1});
  const blocked=[]; const errors=[];
  await context.route('**/*', route=>{if(route.request().url().startsWith(`http://127.0.0.1:${server.address().port}/`))return route.continue();blocked.push(route.request().url());return route.abort();});
  const page = await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url,{waitUntil:'networkidle',timeout:30000});await page.evaluate(()=>document.fonts.ready);
  const fontLoaded = await page.evaluate(()=>document.fonts.check('19px Shahmukhi'));
  if(!fontLoaded)throw Error('Offline Nastaliq font not loaded');
  const samples=[];
  for(const width of [1280,375]){
   await page.setViewportSize({width,height:1000});
   for(const [name,selector] of [['top','header'],['notation','.source-notation'],['contents','#b40-contents'],['bridge','#bridge-example-2'],['matrix','#bridge-example-4'],['glossary','#bridge-glossary']]){
    await page.locator(selector).scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(shots,`${name}-${width}.png`)});
    const metrics=await page.evaluate(()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
    if(metrics.scroll>metrics.client+1)throw Error('Page-level horizontal overflow '+JSON.stringify({name,width,...metrics}));
    samples.push({name,width,...metrics,screenshot:`qa/visual/${name}-${width}.png`});
   }
  }
  await page.locator('#bridge-a8 summary').click();
  if(!await page.locator('#bridge-a8').getAttribute('open') && !await page.locator('#bridge-a8').evaluate(e=>e.open))throw Error('Answer disclosure failed');
  const bidi=await page.evaluate(()=>({root:getComputedStyle(document.documentElement).direction,math:[...document.querySelectorAll('math')].every(e=>getComputedStyle(e).direction==='ltr'),optional:document.querySelectorAll('sup.optional-star').length,images:[...document.images].every(e=>e.complete&&e.naturalWidth>0)}));
  if(bidi.root!=='rtl'||!bidi.math||bidi.optional!==14||!bidi.images)throw Error('Bidi/image check');
  await page.setViewportSize({width:1280,height:1000});
  await page.evaluate(()=>document.querySelectorAll('#bridge-answers details').forEach(e=>e.open=true));
  await page.emulateMedia({media:'print'});
  await page.evaluate(()=>document.fonts.ready);
  const publicPackageBase='https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/blob/codex/additional-translations-review/translations/recovered-books/hefferon-pnb-20260904';
  // Relative companion-file links must not leak the ephemeral local server
  // address into the PDF. In-document anchors remain native PDF destinations.
  const publicLinks=await page.evaluate(base=>{
   let changed=0;
   for(const a of document.querySelectorAll('a[href]')){
    const raw=a.getAttribute('href');if(raw.startsWith('#'))continue;
    const link=new URL(raw,document.baseURI);
    if(link.origin===location.origin){a.href=base+link.pathname+link.hash;changed++;}
   }
   return changed;
  },publicPackageBase);
  const pdf = path.join(pdfdir,'hefferon-shahmukhi-opening.pdf');
  await page.pdf({path:pdf,format:'A4',preferCSSPageSize:true,printBackground:true,tagged:true,outline:true,displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:'<div style="font-size:9px;width:100%;text-align:center;color:#465550;font-family:Arial">Hefferon · Shahmukhi opening <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
  // Fixed-width date normalization preserves every xref offset and makes the
  // release-date metadata deterministic without touching text or structure.
  const pdfBytes=fs.readFileSync(pdf); let normalizedDates=0;
  let normalized=pdfBytes.toString('latin1').replace(/\/(CreationDate|ModDate) \(D:\d{14}\+00'00'\)/g,(_,key)=>{normalizedDates++;return `/${key} (D:20260904000000+00'00')`;});
  // Chromium gives tagged-table structure IDs process-local node numbers.
  // Canonicalize those strings bijectively, including every IDTree/reference
  // occurrence. Fixed width preserves xrefs and all content/font streams.
  const originalIds=[...new Set(normalized.match(/\(node\d{8}\)/g)||[])].sort();
  const structureIds=new Map(originalIds.map((original,i)=>[original,`(node${String(i+1).padStart(8,'0')})`]));let structureIdOccurrences=0;
  normalized=normalized.replace(/\(node\d{8}\)/g,original=>{
   structureIdOccurrences++;return structureIds.get(original);
  });
  if(structureIds.size===0||structureIdOccurrences<structureIds.size*2)throw Error('Unexpected PDF structure ID references');
  if(normalizedDates!==2 || Buffer.byteLength(normalized,'latin1')!==pdfBytes.length)throw Error('Unexpected PDF metadata layout');
  fs.writeFileSync(pdf,Buffer.from(normalized,'latin1'));
  const receipt={status:'PASS',browser:browser.version(),html_sha256:sha(path.join(base,'reader/opening.html')),font_loaded:fontLoaded,offline_external_requests:blocked,script_errors:errors,samples,bidi,answers_expanded_in_pdf:8,raw_tex_appendix_printed:false,pdf_companion_link_base:publicPackageBase,pdf_companion_links_rebound:publicLinks,pdf_deterministic_normalizations:{fixed_release_dates:normalizedDates,bijective_tagged_structure_ids:structureIds.size,structure_id_occurrences:structureIdOccurrences,method:'Same-width replacement; content streams, fonts, xref offsets and ID reference relationships preserved.'},pdf:{path:'output/pdf/hefferon-shahmukhi-opening.pdf',bytes:fs.statSync(pdf).size,sha256:sha(pdf)},limits:'Browser/structural checks and requested tagged/outline metadata do not imply PDF/UA or universal assistive-technology certification.'};
  if(blocked.length||errors.length)throw Error('Unexpected external requests/errors');
  fs.writeFileSync(path.join(qa,'browser.json'),JSON.stringify(receipt,null,2)+'\n');
  process.stdout.write(JSON.stringify({status:receipt.status,pdf:receipt.pdf,browser:receipt.browser})+'\n');
 } finally {if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1});
