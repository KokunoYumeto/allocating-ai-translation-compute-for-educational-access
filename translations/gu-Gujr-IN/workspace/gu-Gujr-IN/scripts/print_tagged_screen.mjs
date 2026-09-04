/** Isolated local-document PDF printer, not an interactive browser-control tool. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const input = path.resolve(process.argv[2]);
const output = path.resolve(process.argv[3]);
const receipt = path.resolve(process.argv[4]);
const bytes = await fs.readFile(input);
await fs.mkdir(path.dirname(output), {recursive:true});
const renderer = await chromium.launch({
  ...(process.env.PDF_CHROME_PATH ? {executablePath:process.env.PDF_CHROME_PATH} : {}),
  headless:true,
  args:['--disable-background-networking','--disable-component-update','--disable-default-apps','--no-first-run'],
});
try {
  const context = await renderer.newContext({viewport:{width:1280,height:900}, locale:'gu-IN', javaScriptEnabled:false});
  const blocked = [];
  await context.route('**/*', route => {
    const url = route.request().url();
    if (/^(file:|data:|about:)/.test(url)) return route.continue();
    blocked.push(url);
    return route.abort();
  });
  const page = await context.newPage();
  await page.goto(pathToFileURL(input).href, {waitUntil:'load'});
  await page.emulateMedia({media:'print'});
  await page.evaluate(async () => { await document.fonts.ready; await document.fonts.load('400 16px Gujarati'); await document.fonts.load('700 16px Gujarati'); });
  const dom = await page.evaluate(() => ({
    title:document.title,
    lang:document.documentElement.lang,
    headings:[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(e=>({level:e.tagName,text:e.textContent.trim(),id:e.id})),
    mathematics:[...document.querySelectorAll('math')].map(e=>({text:e.textContent,alt:e.getAttribute('aria-label'),role:e.getAttribute('role')})),
    fonts:[...document.fonts].map(f=>({family:f.family,status:f.status})),
    logicalText:document.body.innerText,
    images:[...document.images].map(i=>({src:i.getAttribute('src'),alt:i.alt,loaded:i.complete&&i.naturalWidth>0})),
  }));
  await page.pdf({path:output,format:'A4',preferCSSPageSize:true,printBackground:true,tagged:true,outline:true,
                 displayHeaderFooter:false});
  if (blocked.length) throw new Error('External runtime requests blocked: '+blocked.join(', '));
  if (dom.images.some(i=>!i.loaded)) throw new Error('Missing local image(s)');
  await fs.writeFile(receipt,JSON.stringify({
    input,output,input_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
    renderer:await renderer.version(),tagged_requested:true,outline_requested:true,
    network_requests_blocked:blocked,dom,
    limitations:['This receipt records printing inputs, not PDF/UA conformance. Inspect actual PDF structure and extraction separately.'],
  },null,2)+'\n','utf8');
  process.stdout.write(JSON.stringify({output,headings:dom.headings.length,math:dom.mathematics.length,fonts:dom.fonts})+'\n');
} finally {
  await renderer.close();
}
