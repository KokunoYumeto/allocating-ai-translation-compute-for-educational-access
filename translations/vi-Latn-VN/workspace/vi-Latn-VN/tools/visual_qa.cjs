// Isolated local headless rendering fallback when the in-app runtime is unavailable.
// No user browser profile or authenticated session is accessed.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

(async () => {
  const root = path.resolve(__dirname, '..');
  const unit = process.argv[2] || 'A30-U001';
  const config = JSON.parse(fs.readFileSync(path.join(root, 'units.json'), 'utf8'))[unit];
  if (!config) throw new Error(`Unknown unit: ${unit}`);
  const out = path.resolve(root, '..', 'build', unit === 'A30-U001' ? 'vi-visual-qa' : `vi-visual-${unit}`);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await page.goto(`http://127.0.0.1:8765/${config.slug}.vi.html`, {waitUntil:'networkidle'});
  const widths = [];
  const figures = await page.locator('img').evaluateAll(images => images.map(i => ({loaded:i.complete && i.naturalWidth > 0, alt:i.alt})));
  if (figures.some(i => !i.loaded || !i.alt)) throw new Error('Unloaded/undescribed figure');
  const anchors = config.visual?.anchors || (unit === 'A30-U001'
    ? ['fs-id1165133394710', 'Figure_01_01_001', 'Example_01_01_01', 'Table_01_01_01', 'vi-exercises', 'vi-answers', 'vi-computing']
    : ['fs-id1165134474160', 'fs-id1165135332760', 'fs-id1165137444349', 'Example_01_01_03', 'Image_01_01_005', 'Example_01_01_04', 'fs-id1165134257606', 'fs-id1165137740780', 'vi-attribution']);
  for (const id of anchors) {
    await page.locator(`[id="${id}"]`).scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out, `desktop-${id}.png`)});
  }
  for (const width of [1280, 390]) {
    await page.setViewportSize({width,height:1000});
    const geometry = await page.evaluate(() => ({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    if (geometry.scroll > geometry.width) throw new Error(`Horizontal overflow at ${width}: ${JSON.stringify(geometry)}`);
    widths.push(geometry);
    await page.locator(config.visual?.primary ? `#${config.visual.primary}` : unit === 'A30-U001' ? '#Table_01_01_01' : '#Image_01_01_005').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out, `table-${width}.png`)});
    await page.locator(config.visual?.secondary ? `#${config.visual.secondary}` : unit === 'A30-U001' ? '#vi-exercises' : '#fs-id1165134257606').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out, `exercises-${width}.png`)});
  }
  const answer = config.visual?.answer || (unit === 'A30-U001' ? 'fs-id1165137724415' : 'fs-id1165137871618');
  await page.locator(`a[href="#${answer}"]`).first().click();
  if (!page.url().endsWith(`#${answer}`)) throw new Error('Answer link failed');
  const htmlPath = path.join(root,'review',`${config.slug}.vi.html`);
  const receipt = {unit, result:'automated_layout_pass', browser:'isolated headless Microsoft Edge via Playwright',
    fallback_reason:'in-app runtime failed before connection: kernel assets path not found; U002 retry after storage recovery also failed', figures:figures.length, widths,
    answer_link:'pass', html_sha256:crypto.createHash('sha256').update(fs.readFileSync(htmlPath)).digest('hex'),
    screenshots:path.relative(path.dirname(root),out).replaceAll('\\','/'), visual_inspection:'pending model image review'};
  fs.writeFileSync(path.join(root,config.visual_receipt),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify(receipt));
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
