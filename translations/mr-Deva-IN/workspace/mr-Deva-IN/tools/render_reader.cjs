// Isolated fallback after in-app browser bootstrap failed; no user browser profile.
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const playwrightRoot = process.argv[2];
const executablePath = process.argv[3];
const unit = process.argv[4] || 'MR-BRIDGE-001';
if (!playwrightRoot || !executablePath || !/^MR-BRIDGE-\d{3}$/.test(unit)) throw new Error('Usage: node render_reader.cjs PLAYWRIGHT_MODULE_PATH BROWSER_EXECUTABLE [MR-BRIDGE-002]');
const { chromium } = require(playwrightRoot);
const language = path.resolve(__dirname, '..');
const scratch = path.resolve(language, '../downloads/mr-Deva-IN/reader-qa', unit);
fs.mkdirSync(scratch, { recursive:true });
(async () => {
  const browser = await chromium.launch({ executablePath, headless:true });
  try {
  const page = await browser.newPage({ viewport:{width:1100,height:900} });
  const errors = [];
  const networkRequests = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('request', request => { if (/^https?:/.test(request.url())) networkRequests.push(request.url()); });
  await page.route(/^https?:/, route => route.abort());
  const readerPath = path.join(language,'output',unit+'.html');
  await page.goto(pathToFileURL(readerPath).href);
  await page.evaluate(() => document.fonts.ready);
  const imageDecoding = await page.locator('img').evaluateAll(async nodes => {
    await Promise.all(nodes.map(node => node.decode()));
    return nodes.map(node => ({figure:node.closest('figure')?.id, naturalWidth:node.naturalWidth,
      naturalHeight:node.naturalHeight, complete:node.complete, alt:node.alt,
      embedded:/^data:image\/(jpeg|png);base64,/.test(node.src)}));
  });
  if (imageDecoding.some(item => !item.complete || !item.embedded || !item.figure || !item.alt.trim()
    || item.naturalWidth <= 0 || item.naturalHeight <= 0)) throw new Error('Invalid rendered source image');
  const results = [];
  const sections = await page.locator('article > section[id], article > aside[id]').evaluateAll(nodes => nodes.map(node => node.id));
  if (await page.locator('article > header').count()) sections.unshift('header');
  const screenshots = [];
  for (const width of [1100,420]) {
    await page.setViewportSize({width,height:900});
    const layout = await page.evaluate(() => ({width:innerWidth, documentWidth:document.documentElement.scrollWidth, ids:document.querySelectorAll('[id]').length, language:document.documentElement.lang, font:getComputedStyle(document.body).fontFamily}));
    if (layout.documentWidth > width) throw new Error('Horizontal overflow: '+JSON.stringify(layout));
    results.push(layout);
    for (const id of sections) {
      const screenshotPath = path.join(scratch,`${width}-${id}.png`);
      await page.locator(id === 'header' ? 'article > header' : '#'+id).screenshot({path:screenshotPath});
      screenshots.push({width, section:id, path:path.relative(language,screenshotPath).replaceAll('\\','/')});
    }
  }
  const configPath = path.join(language,'units',unit+'.json');
  const questionIds = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath,'utf8')).question_ids : ['D1'];
  for (const id of questionIds) {
    await page.locator(`a[href="#S-${id}"]`).first().click();
    if (new URL(page.url()).hash !== '#S-'+id) throw new Error('Answer link did not navigate: '+id);
    await page.locator(`#S-${id} a[href="#${id}"]`).click();
    if (new URL(page.url()).hash !== '#'+id) throw new Error('Return link did not navigate: '+id);
  }
  const sourceAnswerPairs = await page.locator('.problem[id]').evaluateAll(problems => problems.map(problem => {
    const targets = Array.from(problem.querySelectorAll('a[href^="#"]')).map(anchor => {
      const answer = document.getElementById(anchor.getAttribute('href').slice(1));
      return answer?.classList.contains('solution') ? answer : null;
    }).filter(Boolean);
    if (targets.length !== 1) throw new Error('Expected one source answer target for '+problem.id);
    const answer = targets[0];
    if (!Array.from(answer.querySelectorAll('a')).some(anchor => anchor.getAttribute('href') === '#'+problem.id))
      throw new Error('Missing source answer return link for '+problem.id);
    return {problem:problem.id, answer:answer.id};
  }));
  for (const pair of sourceAnswerPairs) {
    await page.locator(`[id="${pair.problem}"] a[href="#${pair.answer}"]`).click();
    if (new URL(page.url()).hash !== '#'+pair.answer) throw new Error('Source answer link did not navigate: '+pair.problem);
    await page.locator(`[id="${pair.answer}"] a[href="#${pair.problem}"]`).click();
    if (new URL(page.url()).hash !== '#'+pair.problem) throw new Error('Source return link did not navigate: '+pair.problem);
  }
  if (errors.length) throw new Error(errors.join('\n'));
  if (networkRequests.length) throw new Error('Unexpected network dependency: '+networkRequests.join(', '));
  const htmlSha256 = require('node:crypto').createHash('sha256').update(fs.readFileSync(readerPath)).digest('hex');
  const receipt = {unit,result:'PASS',htmlSha256,browserVersion:browser.version(),isolatedHeadless:true,viewports:results,answerNavigation:questionIds.length || sourceAnswerPairs.length ? 'bidirectional pass' : 'no question pairs in unit',questionIdsChecked:questionIds,sourceAnswerPairsChecked:sourceAnswerPairs,imageDecoding,pageErrors:errors,networkRequests,screenshots,manualVisualReview:'recorded separately after actual inspection'};
  const receiptName = unit === 'MR-BRIDGE-001' ? 'browser-receipt.json' : unit+'-browser-receipt.json';
  const receiptPath = path.join(language,'qa',receiptName);
  fs.writeFileSync(receiptPath+'.tmp',JSON.stringify(receipt,null,2)+'\n');
  fs.renameSync(receiptPath+'.tmp',receiptPath);
  console.log(JSON.stringify(receipt,null,2));
  } finally {
  await browser.close();
  }
})().catch(error => {console.error(error);process.exitCode=1;});
