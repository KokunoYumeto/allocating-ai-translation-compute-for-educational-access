/** Read-only PDF.js compatibility receipt. Does not control an interactive browser. */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const pdfjs = await import(process.env.PDFJS_MODULE_PATH ? pathToFileURL(path.resolve(process.env.PDFJS_MODULE_PATH)).href : 'pdfjs-dist/legacy/build/pdf.mjs');
const bytes=await fs.readFile(process.argv[2]);
const doc=await pdfjs.getDocument({data:new Uint8Array(bytes),useSystemFonts:false}).promise;
const pages=[];
for(let i=1;i<=Math.min(doc.numPages,Number(process.argv[4]||1));i++) {
  const page=await doc.getPage(i);
  const text=(await page.getTextContent()).items.filter(x=>x.str).map(x=>x.str).join(' ');
  pages.push({page:i,text,nul_count:[...text].filter(x=>x==='\u0000').length,
             replacement_count:[...text].filter(x=>x==='\ufffd').length,structure:await page.getStructTree()});
}
await fs.writeFile(process.argv[3],JSON.stringify({
  pdf_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),version:pdfjs.version,
  document_pages:doc.numPages,pages_tested:pages.length,pages,
  extraction_pass:pages.every(p=>!p.nul_count&&!p.replacement_count),
  note:'This is an actual PDF.js text/structure extraction test, not an assistive-technology session.'
},null,2)+'\n','utf8');
process.stdout.write(JSON.stringify({version:pdfjs.version,pages_tested:pages.length,nul_counts:pages.map(p=>p.nul_count)})+'\n');
await doc.destroy();
