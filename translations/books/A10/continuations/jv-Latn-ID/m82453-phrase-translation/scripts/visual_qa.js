'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const browserPath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const pages = ['index.html', 'jv-academic.html', 'jv-conversation.html', 'id-academic.html', 'en.html'];
const viewports = {
  wide: { width: 1440, height: 900 },
  narrow: { width: 500, height: 844 },
};
const screenshotPages = new Set(['jv-academic.html', 'jv-conversation.html']);
const screenshotDir = path.join(root, 'qa', 'screenshots');
fs.mkdirSync(screenshotDir, { recursive: true });

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

(async () => {
  const browser = await chromium.launch({ executablePath: browserPath, headless: true });
  const checks = [];
  const screenshots = [];
  try {
    for (const [viewportName, viewport] of Object.entries(viewports)) {
      const context = await browser.newContext({ viewport });
      for (const file of pages) {
        const page = await context.newPage();
        const browserErrors = [];
        page.on('pageerror', error => browserErrors.push(String(error)));
        await page.goto(pathToFileURL(path.join(root, file)).href, { waitUntil: 'load' });
        const metric = await page.evaluate(() => {
          const main = document.querySelector('main');
          const images = [...document.images];
          return {
            title: document.title,
            document_language: document.documentElement.lang,
            viewport_width: innerWidth,
            document_scroll_width: document.documentElement.scrollWidth,
            main_width: Math.round(main.getBoundingClientRect().width),
            mathml: document.querySelectorAll('math').length,
            tables: document.querySelectorAll('table').length,
            figures: document.querySelectorAll('figure').length,
            details: document.querySelectorAll('details').length,
            source_links: document.querySelectorAll('a.source-link, .source-link a').length,
            audio: document.querySelectorAll('audio').length,
            missing_images: images.filter(image => !image.complete || image.naturalWidth === 0).length,
          };
        });
        const expectedReader = file !== 'index.html';
        const translated = ['jv-academic.html', 'jv-conversation.html', 'id-academic.html'].includes(file);
        const passed = browserErrors.length === 0 &&
          metric.document_scroll_width <= metric.viewport_width + 1 &&
          metric.main_width >= metric.viewport_width - 1 &&
          metric.missing_images === 0 &&
          (!expectedReader || (metric.mathml === 63 && metric.tables === 3 && metric.figures === 3)) &&
          (!translated || metric.source_links === 15) &&
          (!['jv-academic.html', 'jv-conversation.html'].includes(file) || metric.audio === 1);
        checks.push({ file, viewport: viewportName, ...metric, browser_errors: browserErrors, passed });
        if (screenshotPages.has(file)) {
          const name = `${path.basename(file, '.html')}-${viewportName}.png`;
          const destination = path.join(screenshotDir, name);
          await page.screenshot({ path: destination, fullPage: true });
          screenshots.push({
            file: path.relative(root, destination).split(path.sep).join('/'),
            page: file,
            viewport: viewportName,
            bytes: fs.statSync(destination).size,
            sha256: sha256(destination),
          });
        }
        await page.close();
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  const result = {
    schema: 'a10.browser-qa.v1',
    date: '2026-09-04',
    browser: 'Microsoft Edge via Playwright',
    viewports,
    status: checks.every(check => check.passed) ? 'pass' : 'fail',
    checks,
    screenshots,
  };
  fs.writeFileSync(path.join(root, 'BROWSER_QA.json'), JSON.stringify(result, null, 2) + '\n', 'utf8');
  if (result.status !== 'pass') {
    console.error(JSON.stringify(checks.filter(check => !check.passed), null, 2));
    process.exit(1);
  }
  console.log(`Browser QA passed for ${checks.length} page/viewport combinations; ${screenshots.length} screenshots saved.`);
})().catch(error => {
  console.error(error.stack || String(error));
  process.exit(1);
});
