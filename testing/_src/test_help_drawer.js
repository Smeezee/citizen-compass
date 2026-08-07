/* test_help_drawer.js - HELP drawer on the keybind screen.
 *
 * Rule 12: a check that cannot fail is not a check. Every assertion here that
 * could plausibly pass for the wrong reason carries a NEGATIVE CONTROL that
 * proves it fails on known-bad input, run in the same pass.
 *
 *   run:  node testing/_src/test_help_drawer.js                 (built file://)
 *         node testing/_src/test_help_drawer.js <https-url>     (deployed)
 *
 * Needs playwright:  npx playwright install chromium
 */
'use strict';
const path = require('path');
const { chromium } = require('playwright');

const REPO = path.resolve(__dirname, '..', '..');
const TARGET = process.argv[2] ||
  ('file:///' + path.join(REPO, 'testing', '_deploy', 'index.html').replace(/\\/g, '/'));

const DRAWER_W = 420;         // must match --cc-help-w in the layer
let pass = 0; const fail = [];
function ck(cond, msg) { if (cond) { pass++; console.log('  ok   ' + msg); }
                         else { fail.push(msg); console.log('  FAIL ' + msg); } }

/* ---------------------------------------------------------------------------
 * The link validator. Kept as a pure function so it can be run against the
 * real graph AND against a deliberately corrupted copy in the same pass.
 * ------------------------------------------------------------------------- */
function validateGraph(G) {
  const problems = [];
  const nodes = G.nodes || {};
  const targetsOf = (n) => {
    if (n.type === 'question') return [n.yes, n.no];
    if (n.type === 'choice') return (n.options || []).map(o => o.goto);
    return n.then === null ? [] : [n.then];
  };
  // 1. every link resolves
  for (const [id, n] of Object.entries(nodes))
    for (const t of targetsOf(n))
      if (!t || !nodes[t]) problems.push(`${id} -> ${t} does not exist`);
  // 2. every node reachable from start
  const seen = new Set(); const q = [G.start];
  if (!nodes[G.start]) problems.push(`start node "${G.start}" does not exist`);
  while (q.length) {
    const id = q.shift();
    if (!id || seen.has(id) || !nodes[id]) continue;
    seen.add(id);
    for (const t of targetsOf(nodes[id])) q.push(t);
  }
  for (const id of Object.keys(nodes))
    if (!seen.has(id)) problems.push(`${id} is unreachable from start`);
  return problems;
}

(async () => {
  console.log('TARGET: ' + TARGET + '\n');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  /* Over the network the page is 1.5MB and the drawer's script is near the end
     of it. A fixed sleep here is a flaky gate - wait for the drawer to actually
     announce itself instead. */
  async function ready() {
    if (await page.locator('#cc-pw').count()) {
      await page.fill('#cc-pw', 'apples');
      await page.click('#cc-go');
    }
    await page.waitForFunction(() => typeof window.ccHelpGraph === 'function' &&
                                     !!document.getElementById('cc-help-tab'),
                               null, { timeout: 60000 });
  }

  await page.goto(TARGET, { waitUntil: 'load' });
  await ready();
  ck(await page.locator('#cc-help-tab').count() === 1, 'HELP tab exists on the page');
  ck(await page.locator('#cc-help-tab').isVisible(), 'HELP tab is visible without opening anything');
  ck(!(await page.locator('#cc-help').evaluate(e => e.classList.contains('open'))),
     'HELP drawer does NOT auto-open');

  /* ---------------- 1. THE SHRINK ---------------------------------------- */
  console.log('\n1. content region must SHRINK, not be overlaid');
  await page.click('#cc-kb-tab');                       // open the keybind screen
  await page.waitForTimeout(400);
  const wClosed = await page.locator('#cc-kb').evaluate(e => e.getBoundingClientRect().width);
  await page.click('#cc-help-tab');
  await page.waitForTimeout(500);                       // 280ms transition
  const wOpen = await page.locator('#cc-kb').evaluate(e => e.getBoundingClientRect().width);
  console.log(`     #cc-kb width  closed=${wClosed}px  open=${wOpen}px  delta=${wClosed - wOpen}px`);

  /* This is the assertion the whole drawer exists to satisfy. A drawer that
     merely slid over the top would leave wOpen === wClosed. */
  const shrank = (wClosed - wOpen) >= DRAWER_W - 2 && (wClosed - wOpen) <= DRAWER_W + 2;
  ck(shrank, `content region narrows by the drawer width (${DRAWER_W}px), it does not overlay`);
  ck(await page.locator('#cc-help').isVisible(), 'drawer is on screen');

  /* NEGATIVE CONTROL. Neutralise ONLY the reflow rules and leave the drawer
     working exactly as before: it still opens, still animates, still visible.
     That is precisely an overlay drawer. The width test must now FAIL - if it
     still passes, it was never measuring reflow. */
  await page.addStyleTag({ content:
    'body.cc-help-open #cc-kb{right:0 !important}body.cc-help-open{padding-right:0 !important}' });
  await page.waitForTimeout(400);
  const wOverlay = await page.locator('#cc-kb').evaluate(e => e.getBoundingClientRect().width);
  const stillVisible = await page.locator('#cc-help').isVisible();
  console.log(`     [negative control] overlay-mode width=${wOverlay}px, drawer visible=${stillVisible}`);
  ck(stillVisible && wOverlay === wClosed,
     '[NEG] with reflow disabled the drawer still shows but the width does NOT change');
  ck(!((wClosed - wOverlay) >= DRAWER_W - 2),
     '[NEG] the shrink assertion FAILS on an overlay drawer (so it can catch one)');

  await page.reload({ waitUntil: 'load' });
  await ready();

  /* ---------------- 2. THE GRAPH ----------------------------------------- */
  console.log('\n2. every node reachable, every link resolves');
  const G = await page.evaluate(() => window.ccHelpGraph());
  ck(G && G.nodes && Object.keys(G.nodes).length === 17,
     `graph loaded from the page with 17 nodes (got ${G && G.nodes ? Object.keys(G.nodes).length : 'none'})`);
  const problems = validateGraph(G);
  if (problems.length) problems.forEach(p => console.log('       - ' + p));
  ck(problems.length === 0, 'no unreachable nodes and no dangling links');

  /* NEGATIVE CONTROL: plant a broken link and an orphan, confirm both caught. */
  const broken = JSON.parse(JSON.stringify(G));
  broken.nodes.q_selector_setting.no = 'fix_that_does_not_exist';
  const bp = validateGraph(broken);
  ck(bp.some(p => p.includes('fix_that_does_not_exist')),
     '[NEG] a planted dangling link IS caught by the validator');
  ck(bp.some(p => p.includes('unreachable')),
     '[NEG] the node orphaned by that break is reported unreachable');
  const clean = validateGraph(G);
  ck(clean.length === 0, '[NEG] removing the planted break returns the validator to clean');

  /* end_not_covered is the honest dead end and must stay one */
  const nulls = Object.entries(G.nodes).filter(([, n]) => n.then === null).map(([k]) => k);
  ck(nulls.length === 1 && nulls[0] === 'end_not_covered',
     'end_not_covered is the only node with then:null');

  /* ---------------- 3. FIXES ROUTE BACK TO A RETEST ---------------------- */
  console.log('\n3. a fix node\'s "then" actually navigates');
  const fixes = Object.entries(G.nodes)
    .filter(([, n]) => n.type === 'fix' && n.then !== null).map(([k]) => k);
  ck(fixes.length === 11, `11 fix nodes carry a "then" (got ${fixes.length})`);
  let routed = 0; const stuck = [];
  for (const id of fixes) {
    await page.evaluate(f => window.ccHelpOpen(f), id);
    const btn = page.locator('#cc-help .then');
    if (!(await btn.count())) { stuck.push(id + ' (no continue button rendered)'); continue; }
    await btn.click();
    const now = await page.evaluate(() => window.ccHelpNode());
    if (now === G.nodes[id].then) routed++;
    else stuck.push(`${id} -> expected ${G.nodes[id].then}, landed on ${now}`);
  }
  if (stuck.length) stuck.forEach(s => console.log('       - ' + s));
  ck(routed === fixes.length, `every fix routes the user back to its retest node (${routed}/${fixes.length})`);

  /* the dead end must NOT offer a route out */
  await page.evaluate(() => window.ccHelpOpen('end_not_covered'));
  ck(await page.locator('#cc-help .then').count() === 0,
     'end_not_covered offers no invented way onward');

  /* back a step costs one click, not a restart */
  await page.evaluate(() => window.ccHelpOpen('q_stick_listed'));
  await page.locator('#cc-help .ans button').first().click();     // Yes
  const afterYes = await page.evaluate(() => window.ccHelpNode());
  await page.click('#cc-help-back');
  const afterBack = await page.evaluate(() => window.ccHelpNode());
  ck(afterYes === 'q_selector_setting' && afterBack === 'q_stick_listed',
     'answering wrong costs one click back, not a restart');

  /* how_to_check is rendered, not dropped */
  await page.evaluate(() => window.ccHelpOpen('q_selector_setting'));
  const chk = await page.locator('#cc-help .chk').innerText();
  ck(chk.includes('Look at what it currently says'),
     'how_to_check text is rendered under the question');

  /* ---------------- 4. VENDOR MATCHING ----------------------------------- */
  console.log('\n4. vendor matched on usb_vid ALONE');
  const vm = await page.evaluate(() => {
    const r = {};
    r.vkb        = window.ccHelpVendor(window.ccHelpVid('VKBsim Gladiator NXT R (Vendor: 231d Product: 0200)'));
    r.virpil     = window.ccHelpVendor(window.ccHelpVid('VPC Stick (Vendor: 3344 Product: 412f)'));
    r.firefox    = window.ccHelpVendor(window.ccHelpVid('231d-0200-VKBsim Gladiator NXT R'));
    r.unknownVid = window.ccHelpVendor(window.ccHelpVid('Wobble Stick 9000 (Vendor: dead Product: beef)'));
    r.noVid      = window.ccHelpVendor(window.ccHelpVid('Some Unnamed Controller'));
    /* a product id that collides with another vendor's VID must NOT match */
    r.productOnly = window.ccHelpVendor(window.ccHelpVid('Fake (Vendor: 9999 Product: 231d)'));
    return {
      vkb: r.vkb && r.vkb.key, virpil: r.virpil && r.virpil.key,
      firefox: r.firefox && r.firefox.key,
      unknownVid: r.unknownVid, noVid: r.noVid, productOnly: r.productOnly,
    };
  });
  ck(vm.vkb === 'vkb', 'Chrome-style id with vendor 231d matches VKB');
  ck(vm.virpil === 'virpil', 'vendor 3344 matches VIRPIL');
  ck(vm.firefox === 'vkb', 'Firefox-style id string also resolves the vendor');
  ck(vm.unknownVid === null, 'an unknown VID matches NO vendor (falls through)');
  ck(vm.noVid === null, 'an id string with no VID in it matches no vendor');
  ck(vm.productOnly === null,
     '[NEG] a VKB vendor id appearing as a PRODUCT id does not match VKB');

  /* turtle_beach has usb_vid null on purpose - it must be unmatchable */
  const tb = await page.evaluate(() => {
    const V = JSON.parse(document.getElementById('cc-vendor-data').textContent);
    return { vid: V.vendors.turtle_beach.usb_vid,
             byNull: window.ccHelpVendor(null),
             byEmpty: window.ccHelpVendor('') };
  });
  ck(tb.vid === null && tb.byNull === null && tb.byEmpty === null,
     'turtle_beach (usb_vid null) can never be auto-matched');

  /* now the rendering, on the dead end where the links are surfaced */
  await page.evaluate(() => { window.__ccHelpFakeId = 'VKBsim Gladiator NXT R (Vendor: 231d Product: 0200)'; });
  await page.evaluate(() => window.ccHelpOpen('end_not_covered'));
  const vkbText = await page.locator('#cc-help .vend').innerText();
  ck(vkbText.includes('VKB-Sim'), 'matched vendor name renders on the dead end');
  ck(vkbText.includes('VKBDevCfg'), 'the VKB known_gotcha renders prominently');
  ck(await page.locator('#cc-help .gotcha').isVisible(), 'known_gotcha has its own callout, not buried in a list');
  ck((await page.locator('#cc-help .vend a').count()) === 5, 'all 5 VKB links render');

  await page.evaluate(() => { window.__ccHelpFakeId = 'Wobble Stick 9000 (Vendor: dead Product: beef)'; });
  await page.evaluate(() => window.ccHelpOpen('end_not_covered'));
  const fbText = await page.locator('#cc-help .vend').innerText();
  ck(fbText.includes("don't recognise your device yet"), 'unknown VID falls through to the generic fallback');
  ck(!/VKB-Sim|VIRPIL|Thrustmaster|WinWing|Turtle Beach/.test(fbText),
     '[NEG] unknown VID does NOT route to any wrong manufacturer');

  /* ---------------- 5. THE LINE ON THE BINDING SCREEN -------------------- */
  console.log('\n5. the one line on the binding screen');
  await page.evaluate(() => window.ccHelpClose());
  /* the hint lives ON the binding screen, so that screen has to be open */
  await page.click('#cc-kb-tab');
  await page.waitForTimeout(300);
  const hint = page.locator('#cc-kb-hinthelp');
  ck(await hint.count() === 1, 'the hint line exists on the binding screen');
  ck(await hint.isVisible(), 'the hint line is visible on the binding screen');
  ck((await hint.innerText()).trim() === 'Not detecting your stick? Check the device selector first.',
     'hint reads exactly as specified');
  await hint.click();
  const at = await page.evaluate(() => window.ccHelpNode());
  ck(at === 'q_selector_setting', 'the hint opens the drawer AT q_selector_setting');
  ck(await page.evaluate(() => document.body.classList.contains('cc-help-open')),
     'clicking the hint opens the drawer (and so shrinks the page)');

  /* ---------------- 6. THE TRAP ------------------------------------------ */
  console.log('\n6. build substitution actually happened in the shipped page');
  const subbed = await page.evaluate(() => {
    const a = document.getElementById('cc-help-data').textContent;
    const b = document.getElementById('cc-vendor-data').textContent;
    return { a: a.indexOf('__BUILD_INJECTS__') === -1 && a.length > 5000,
             b: b.indexOf('__BUILD_INJECTS__') === -1 && b.length > 3000 };
  });
  ck(subbed.a, 'keybind_troubleshooting.json was substituted into the shipped page');
  ck(subbed.b, 'vendor_support.json was substituted into the shipped page');

  await page.screenshot({ path: path.join(REPO, 'testing', '_src', '_help_drawer_1920.png') });
  console.log('\n     screenshot: testing/_src/_help_drawer_1920.png');

  await browser.close();
  console.log(`\n${pass} passed, ${fail.length} failed`);
  if (fail.length) { fail.forEach(f => console.log('  FAILED: ' + f)); process.exit(1); }
})().catch(e => { console.error(e); process.exit(1); });
