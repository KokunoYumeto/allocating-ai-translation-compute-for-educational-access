// Local, offline, book-specific browser build. No TeX or remote browser service.
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.A20_PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.A20_CHROMIUM_PATH ? { executablePath: process.env.A20_CHROMIUM_PATH } : {}),
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const missing = [];
    const remote = [];
    page.on('requestfailed', r => missing.push({url:r.url().startsWith('file:') ? r.url().split('/').slice(-3).join('/') : r.url(),error:r.failure().errorText}));
    await page.route(/https?:\/\//, r => { remote.push(r.request().url()); return r.abort(); });
    await page.goto(pathToFileURL(path.join(root, 'index.html')).href, {waitUntil:'networkidle'});
    await page.evaluate(() => document.fonts.ready);
    const results = [];
    for (const width of [360, 768, 1280]) {
      await page.setViewportSize({width, height:900});
      const result = await page.evaluate(() => ({
        viewport:innerWidth, scroll:document.documentElement.scrollWidth,
        direction:getComputedStyle(document.documentElement).direction,
        font_loaded:document.fonts.check('16px "A20 Naskh"'),
        images:[...document.images].map(i=>({file:i.getAttribute('src'),loaded:i.complete && i.naturalWidth>0,natural_width:i.naturalWidth,transform:getComputedStyle(i).transform})),
        duplicate_ids:[...new Set([...document.querySelectorAll('[id]')].map(e=>e.id))].filter(id=>document.querySelectorAll(`[id="${id}"]`).length>1),
        headings:[...document.querySelectorAll('h1,h2,h3,h4')].map(e=>({tag:e.tagName,text:e.innerText})),
      }));
      if (result.scroll > width || result.direction !== 'rtl' || !result.font_loaded || result.duplicate_ids.length || result.images.some(i=>!i.loaded||i.transform!=='none')) throw new Error('Viewport/font/asset QA failed: '+JSON.stringify(result));
      results.push(result);
      if (width === 360) await page.screenshot({path:path.join(root,'tmp/pdfs/mobile.png'),fullPage:false});
    }
    if (remote.length || missing.length) throw new Error(JSON.stringify({remote,missing}));
    await page.emulateMedia({media:'print'});
    const css = await page.evaluate(() => ({
      print_body_font:getComputedStyle(document.body).fontFamily,
      print_body_size:getComputedStyle(document.body).fontSize,
      source_owners:document.querySelectorAll('#a20-preface-source [data-source-key]').length,
    }));
    await page.pdf({path:path.join(root,'output/pdf/a20-preface-shahmukhi.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true,tagged:true,outline:true,displayHeaderFooter:true,
      headerTemplate:'<div></div>',
      footerTemplate:'<div style="font:9px Arial,sans-serif;color:#586763;width:100%;text-align:center;direction:ltr">A20 / m81357 - Shahmukhi Punjabi preface · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
    fs.writeFileSync(path.join(root,'qa/browser.json'),JSON.stringify({browser:browser.version(),offline:true,remote_requests:remote,failed_requests:missing,viewports:results,...css},null,2)+'\n');
    console.log(JSON.stringify({pdf:'output/pdf/a20-preface-shahmukhi.pdf',bytes:fs.statSync(path.join(root,'output/pdf/a20-preface-shahmukhi.pdf')).size,viewports:results.map(r=>r.viewport)}));
  } finally {
    await browser.close();
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
