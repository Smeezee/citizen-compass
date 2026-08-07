/* shot_help_drawer.js - read the drawer on screen at 1920x1080.
 * Captures the keybind screen with the HELP drawer open at several nodes, so
 * the walkthrough can be read rather than merely asserted about.
 *   node testing/_src/shot_help_drawer.js [url]
 */
'use strict';
const path = require('path');
const { chromium } = require('playwright');

const REPO = path.resolve(__dirname, '..', '..');
const TARGET = process.argv[2] ||
  ('file:///' + path.join(REPO, 'testing', '_deploy', 'index.html').replace(/\\/g, '/'));
const OUT = path.join(REPO, 'testing', '_src');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(TARGET, { waitUntil: 'load' });
  if (await page.locator('#cc-pw').count()) {
    await page.fill('#cc-pw', 'apples'); await page.click('#cc-go'); await page.waitForTimeout(400);
  }
  await page.click('#cc-kb-tab');
  await page.waitForTimeout(500);

  const shots = [
    ['q_stick_listed',            'shot_1_question'],
    ['fix_wrong_device_selected', 'shot_2_fix'],
    ['c_flying_problem',          'shot_3_choice'],
    ['end_not_covered',           'shot_4_deadend_vendor'],
  ];
  /* a VKB stick, so the vendor block has something real to match */
  await page.evaluate(() => { window.__ccHelpFakeId =
    'VKBsim Gladiator NXT R (Vendor: 231d Product: 0200)'; });

  for (const [node, name] of shots) {
    await page.evaluate(n => window.ccHelpOpen(n), node);
    await page.waitForTimeout(450);
    const w = await page.locator('#cc-kb').evaluate(e => e.getBoundingClientRect().width);
    const open = await page.evaluate(() => document.body.classList.contains('cc-help-open'));
    console.log(`${name.padEnd(24)} node=${node.padEnd(26)} #cc-kb width=${w}px  cc-help-open=${open}`);
    await page.screenshot({ path: path.join(OUT, '_' + name + '.png') });
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
