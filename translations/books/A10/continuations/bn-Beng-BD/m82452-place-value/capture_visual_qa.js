const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const ROOT = __dirname;
const QA = path.join(ROOT, 'qa');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
fs.mkdirSync(QA, { recursive: true });

const sha256 = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const pages = [
  {
    id: 'reader',
    file: 'index.html',
    shots: [
      { id: 'top', selector: null },
      { id: 'rounding-table', selector: '#fs-id1167832055010' },
      { id: 'edition-notes', selector: '#edition-notes' },
    ],
  },
  {
    id: 'companion',
    file: 'companion.html',
    shots: [
      { id: 'top', selector: null },
      { id: 'support-table', selector: '#same-number table' },
      { id: 'recheck', selector: '#bd-pv-r3' },
    ],
  },
];
const viewports = [
  { id: 'wide', width: 1440, height: 900 },
  { id: 'narrow', width: 500, height: 844 },
];

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME,
    args: ['--disable-gpu', '--disable-background-networking', '--disable-component-update'],
  });
  const records = [];
  try {
    for (const viewport of viewports) {
      for (const pageSpec of pages) {
        const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
        const url = pathToFileURL(path.join(ROOT, pageSpec.file)).href;
        await page.goto(url, { waitUntil: 'load' });
        await page.evaluate(() => document.fonts.ready);
        const layout = await page.evaluate(() => {
          const doc = document.documentElement;
          const body = document.body;
          const main = document.querySelector('main').getBoundingClientRect();
          const offscreen = [...document.querySelectorAll('body *')].filter((element) => {
            const r = element.getBoundingClientRect();
            return r.width > 0 && (r.right > window.innerWidth + 1 || r.left < -1);
          }).map((element) => ({ tag: element.tagName, id: element.id || null, class: element.className || null })).slice(0, 20);
          const tables = [...document.querySelectorAll('table')].map((table) => ({
            id: table.id || null,
            width: Math.round(table.getBoundingClientRect().width),
            scrollWidth: table.scrollWidth,
            clientWidth: table.clientWidth,
            wrapperScrollWidth: table.parentElement ? table.parentElement.scrollWidth : null,
            wrapperClientWidth: table.parentElement ? table.parentElement.clientWidth : null,
          }));
          const text = body.innerText;
          return {
            language: doc.lang,
            viewport: { width: window.innerWidth, height: window.innerHeight },
            documentScrollWidth: doc.scrollWidth,
            bodyScrollWidth: body.scrollWidth,
            horizontalOverflowPx: Math.max(doc.scrollWidth, body.scrollWidth) - window.innerWidth,
            main: { left: Math.round(main.left), right: Math.round(main.right), width: Math.round(main.width), fillRatio: Number((main.width / window.innerWidth).toFixed(4)) },
            bodyFontFamily: getComputedStyle(body).fontFamily,
            banglaFontLoaded: document.fonts.check('18px Bangla'),
            bengaliCodepoints: [...text].filter((c) => c >= '\u0980' && c <= '\u09ff').length,
            replacementCharacters: (text.match(/\ufffd/g) || []).length,
            offscreen,
            tables,
          };
        });
        if (layout.language !== 'bn-BD' || !layout.banglaFontLoaded || layout.replacementCharacters !== 0 || layout.horizontalOverflowPx > 1 || layout.offscreen.length !== 0) {
          throw new Error(`layout invariant failed for ${pageSpec.id}/${viewport.id}: ${JSON.stringify(layout)}`);
        }
        for (const shot of pageSpec.shots) {
          if (shot.selector) {
            const locator = page.locator(shot.selector).first();
            if (await locator.count() !== 1) throw new Error(`missing visual target ${shot.selector}`);
            await locator.scrollIntoViewIfNeeded();
            await page.waitForTimeout(100);
          } else {
            await page.evaluate(() => window.scrollTo(0, 0));
          }
          const name = `${pageSpec.id}-${viewport.id}-${shot.id}-${viewport.width}x${viewport.height}.png`;
          const output = path.join(QA, name);
          await page.screenshot({ path: output, fullPage: false });
          records.push({
            page: pageSpec.file,
            viewport,
            target: shot.selector || 'top',
            path: `qa/${name}`,
            bytes: fs.statSync(output).size,
            sha256: sha256(output),
            layout,
          });
        }
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  const result = {
    schema: 'a10.browser-metrics.v1',
    engine: 'Google Chrome via Playwright',
    offline_file_urls_only: true,
    records,
  };
  fs.writeFileSync(path.join(QA, 'BROWSER_METRICS.json'), JSON.stringify(result, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ screenshots: records.length, metrics: 'qa/BROWSER_METRICS.json' }) + '\n');
})().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
