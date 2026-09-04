// Focused, isolated local visual QA for the U022/U023 integration boundary.
// Generated receipts record browser checks only; root image inspection is separate.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const registry = JSON.parse(fs.readFileSync(path.join(root, 'units.json'), 'utf8'));
const digest = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const requested = process.argv.slice(2);
const units = requested.length ? requested : ['A30-U022', 'A30-U023'];
assert(units.every(unit => ['A30-U022', 'A30-U023'].includes(unit)));
const sourcePoints = {
  'A30-U022': ['fs-id1165134042316', 'fs-id1165137531241',
    'Example_01_02_11', 'Example_01_02_12',
    'fs-id1165135177567', 'Example_01_02_13', 'Figure_01_02_026',
    'ti_01_02_06', 'fs-id1165137810682'],
  'A30-U023': ['fs-id1165137591772', 'vi-review-notes'],
};

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
  });
  try {
    for (const unit of units) {
      const config = registry[unit];
      const reader = path.join(root, 'review', config.slug + '.vi.html');
      const readerHash = digest(reader);
      const out = path.resolve(root, '..', 'build', 'vi-visual-' + unit);
      fs.mkdirSync(out, {recursive: true});
      const page = await browser.newPage();
      const url = 'http://127.0.0.1:8765/' + config.slug + '.vi.html';
      const response = await page.goto(url, {waitUntil: 'networkidle'});
      assert.equal(response.status(), 200);
      const captures = [];
      const geometry = [];
      async function capture(name) {
        const file = path.join(out, name + '.png');
        await page.screenshot({path: file});
        captures.push({path: path.relative(path.dirname(root), file).replaceAll('\\', '/'),
          sha256: digest(file)});
      }
      for (const width of [1280, 390]) {
        await page.setViewportSize({width, height: 1100});
        geometry.push(await page.evaluate(() => ({
          viewport: innerWidth, document: document.documentElement.scrollWidth,
        })));
        assert(geometry.at(-1).document <= width);
        for (const id of sourcePoints[unit]) {
          const locator = page.locator('[id="' + id + '"]');
          assert.equal(await locator.count(), 1);
          await locator.evaluate(element => element.scrollIntoView({block: 'start'}));
          await capture('focus-' + width + '-' + id);
        }
      }
      let scrollCheck = null;
      let links = [];
      if (unit === 'A30-U022') {
        const region = page.locator('#vi-piecewise-definition-scroll');
        assert.equal(await region.getAttribute('role'), 'region');
        assert.equal(await region.getAttribute('tabindex'), '0');
        assert((await region.getAttribute('aria-label')).includes('cuộn ngang'));
        await region.evaluate(element => {
          element.scrollIntoView({block: 'start'});
          element.scrollLeft = 0;
        });
        await region.focus();
        await capture('focus-390-definition-left');
        const before = await region.evaluate(element => element.scrollLeft);
        await page.keyboard.press('ArrowRight');
        await page.waitForFunction(() =>
          document.getElementById('vi-piecewise-definition-scroll').scrollLeft > 0);
        const after = await region.evaluate(element => element.scrollLeft);
        assert(after > before);
        await region.evaluate(element => { element.scrollLeft = element.scrollWidth; });
        scrollCheck = await region.evaluate(element => {
          const math = element.querySelector('math');
          const end = math.querySelector('mtr:last-child mtext:last-child');
          return {
            viewport: innerWidth, document: document.documentElement.scrollWidth,
            client_width: element.clientWidth, scroll_width: element.scrollWidth,
            scroll_left: element.scrollLeft, focused: document.activeElement === element,
            math_client_width: math.clientWidth, math_scroll_width: math.scrollWidth,
            final_domain_index_visible: end.getBoundingClientRect().right <=
              element.getBoundingClientRect().right + 1,
            final_domain_text: end.textContent,
          };
        });
        assert(scrollCheck.focused);
        assert(scrollCheck.scroll_width > scrollCheck.client_width);
        assert(scrollCheck.math_scroll_width <= scrollCheck.math_client_width + 1);
        assert(scrollCheck.final_domain_index_visible);
        assert(scrollCheck.document <= scrollCheck.viewport);
        scrollCheck.keyboard_scroll_before = before;
        scrollCheck.keyboard_scroll_after = after;
        await capture('focus-390-definition-right');
        const mathKeys = await page.locator('math[data-source]').evaluateAll(
          elements => elements.map(element => element.getAttribute('data-source')));
        assert.equal(mathKeys.length, 38);
        assert.equal(new Set(mathKeys).size, 38);
      } else {
        const hrefs = await page.locator('#fs-id1165137591772 a').evaluateAll(
          elements => elements.map(element => element.getAttribute('href')));
        assert.equal(hrefs.length, 13);
        for (const href of hrefs) {
          await page.goto(url, {waitUntil: 'domcontentloaded'});
          const anchor = href.split('#')[1];
          await page.locator('a[href="' + href + '"]').click();
          await page.waitForURL('**/' + href);
          const target = page.locator('[id="' + anchor + '"]');
          assert.equal(await target.count(), 1);
          const heading = await target.innerText();
          assert(heading.includes('Ví dụ '));
          const filename = href.split('#')[0];
          links.push({href, target_anchor: anchor, heading,
            target_html_sha256: digest(path.join(root, 'review', filename)),
            actual_click: 'pass'});
        }
      }
      assert.equal(digest(reader), readerHash, 'Reader changed during visual capture');
      const receipt = {unit, result: 'automated_focus_checks_pass',
        html_sha256: readerHash, browser: 'isolated headless Microsoft Edge via Playwright',
        geometry, top_aligned_captures: captures, keyboard_scroll: scrollCheck,
        actual_example_link_clicks: links,
        source_external_links: 'not clicked or fetched',
        model_image_review: 'pending separate root inspection'};
      fs.writeFileSync(path.join(root, 'qa', 'focus-' + unit + '.json'),
        JSON.stringify(receipt, null, 2) + '\n');
      console.log(JSON.stringify({unit, result: receipt.result, html_sha256: readerHash,
        captures: captures.length, keyboard_scroll: scrollCheck,
        actual_example_link_clicks: links.length}));
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
