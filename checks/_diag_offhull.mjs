/* DIAGNOSTIC, not a gate. How far is each hardpoint dot from its own hull?
 *
 * Q26. C1 measured this fleet-wide with `offhull.py` and found ten dots in
 * empty space. THAT SCRIPT IS NOT IN THIS REPOSITORY - it ran on the Cowork
 * mount - so the method is rebuilt here rather than re-run. Three hulls, not
 * 259, so the fifty minutes does not apply.
 *
 * THE METHOD IS C1'S AND I AM NOT IMPROVING ON IT. A dot cannot be measured
 * against a picture that contains it, so every hull is photographed TWICE: once
 * to read the marker positions out of the DOM, and once with `#cc-marks` hidden
 * to get a clean silhouette. The distance is from the marker's centre to the
 * nearest pixel of its own ship.
 *
 * TWO THINGS THAT WOULD SILENTLY WRECK THE MEASUREMENT, BOTH HANDLED:
 *   the grid    `_view.setGrid(false)` first. The holo table is drawn in the
 *               same frame and is not the hull; leaving it on makes every dot
 *               look like it landed on something.
 *   decoding    the screenshot is handed BACK to the browser as a data URL and
 *               read with getImageData. Node has no PNG decoder here and rule 7
 *               says downloaded code is data - so nothing is installed to get
 *               one, and the browser decodes its own picture.
 *
 * The canvas cannot be read with toDataURL: the renderer is constructed without
 * preserveDrawingBuffer (cc_viewer.js:540), so a readback outside the frame
 * comes back blank. Playwright's screenshot goes through the compositor and
 * does not have that problem.
 *
 *   node checks/_diag_offhull.mjs DRAK_Corsair TMBL_Storm_AA VNCL_Glaive
 */
const BASE = "https://citizencompasstesting.citizencompass-contact.workers.dev";
const KEYS = process.argv.slice(2);
if (!KEYS.length) { console.log("usage: node _diag_offhull.mjs <shipKey> ..."); process.exit(2); }

/* The field colour the viewer paints behind the hull, cc_viewer.js:156. A
 * pixel is HULL when it is far enough from that. The threshold is reported per
 * hull along with the coverage it produced, so a silhouette that captured
 * nothing - or everything - is visible rather than assumed. */
const FIELD = [5, 10, 18];
/* SENSITIVITY IS THE WHOLE QUESTION FOR THIS INSTRUMENT. Too high a
 * threshold and the hull's dim edge stops counting as hull, which INFLATES
 * every distance and invents off-hull dots. Settable so the answer can be
 * shown to be stable rather than asserted. */
const THRESH = Number(process.env.CC_OFFHULL_THRESH || 18);
const CAP = 240;

process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH ||
  "C:/Users/david/citizen-compass/checks/.playwright-browsers";
const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 },
                                     deviceScaleFactor: 1 });
page.on("pageerror", e => console.log("  pageerror:", String(e).slice(0, 120)));

await page.goto(BASE + "/loadout", { waitUntil: "domcontentloaded" });
await page.evaluate(() => { try { localStorage.setItem("ccGate", "1"); } catch (e) {} });

let worst = 0;
for (const key of KEYS) {
  console.log("\n=== " + key + " ===");
  await page.goto(`${BASE}/loadout#${encodeURIComponent(key)}`, { waitUntil: "networkidle" });
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(6000);

  const setup = await page.evaluate(() => {
    if (typeof SHIPS === "undefined" || typeof shipId === "undefined")
      return { err: "SHIPS/shipId not defined" };
    if (!SHIPS[shipId]) return { err: "no ship row for " + shipId };
    if (typeof _view === "undefined" || !_view || !_view.current)
      return { err: "no model loaded" };
    _view.setGrid(false);
    const cv = document.querySelector("#cc-holo canvas") ||
               document.querySelector("canvas");
    if (!cv) return { err: "no canvas" };
    const cr = cv.getBoundingClientRect();
    const dots = [...document.querySelectorAll('#cc-marks button[data-mount]')]
      .map(b => { const r = b.getBoundingClientRect();
                  return { port: b.getAttribute("data-mount"),
                           x: r.left + r.width / 2 - cr.left,
                           y: r.top + r.height / 2 - cr.top,
                           on: r.width > 0 && r.height > 0 }; })
      .filter(d => d.on);
    return { name: SHIPS[shipId].n, shown: shipId,
             rect: { x: cr.left, y: cr.top, width: cr.width, height: cr.height },
             dots };
  });
  if (setup.err) { console.log("  NOT MEASURED:", setup.err); continue; }
  console.log(`  ${setup.name}  (${setup.shown})  ${setup.dots.length} dot(s) drawn`);

  /* MARKERS HIDDEN - a dot cannot be measured against a picture containing it.
   *
   * AND SO IS EVERY OTHER THING DRAWN OVER THE CANVAS, which is not a detail.
   * The first version of this measured "any pixel that is not the field
   * colour", and the viewer's own chrome - the Display button, Start spin, the
   * mounts pill, the drag-to-rotate hint - is not the field colour either. The
   * hull's bounding box came back 788px wide on all three hulls, which is the
   * frame rather than the ship, and a dot sitting over the Display button
   * would have measured as ON THE HULL. Caught by the span looking impossible,
   * then confirmed by looking at the picture.
   *
   * Hidden GENERICALLY rather than by a list of selectors: anything that
   * overlaps the canvas and is not the canvas or one of its ancestors. A list
   * would go stale the first time the viewer gains a button. */
  await page.evaluate(() => {
    const cv = document.querySelector("#cc-holo canvas") || document.querySelector("canvas");
    const cr = cv.getBoundingClientRect();
    const anc = new Set(); for (let e = cv; e; e = e.parentElement) anc.add(e);
    window.__offhullHidden = [];
    for (const el of document.body.querySelectorAll("*")) {
      if (el === cv || anc.has(el) || el.contains(cv)) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) continue;
      if (r.right <= cr.left || r.left >= cr.right ||
          r.bottom <= cr.top || r.top >= cr.bottom) continue;
      window.__offhullHidden.push([el, el.style.visibility]);
      el.style.visibility = "hidden";
    }
    return window.__offhullHidden.length;
  });
  await page.waitForTimeout(400);
  const shot = await page.screenshot({ clip: setup.rect });
  await page.evaluate(() => {
    for (const [el, v] of (window.__offhullHidden || [])) el.style.visibility = v;
    window.__offhullHidden = [];
  });

  const res = await page.evaluate(async ({ b64, dots, field, thresh, cap }) => {
    const img = new Image();
    await new Promise((ok, no) => { img.onload = ok; img.onerror = no;
                                    img.src = "data:image/png;base64," + b64; });
    const c = document.createElement("canvas");
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext("2d").drawImage(img, 0, 0);
    const { data, width: W, height: H } = c.getContext("2d")
      .getImageData(0, 0, c.width, c.height);
    const hull = new Uint8Array(W * H);
    let n = 0;
    for (let i = 0, p = 0; i < data.length; i += 4, p++) {
      const d = Math.max(Math.abs(data[i] - field[0]),
                         Math.abs(data[i + 1] - field[1]),
                         Math.abs(data[i + 2] - field[2]));
      if (d > thresh) { hull[p] = 1; n++; }
    }
    /* THE SHIP IS THE LARGEST CONNECTED BLOB, AND NOTHING ELSE IS THE SHIP.
     * With the chrome hidden there is still a faint ring on the canvas's own
     * rounded border - about ten pixels in the outermost column - and it was
     * enough to keep the hull's bounding box at the full frame width. Worse, a
     * dot near the edge would have found the border as its "nearest hull" and
     * been reported closer to the ship than it is. Keeping only the largest
     * component drops it without a magic margin to tune. */
    {
      const lab = new Int32Array(W * H), stack = [];
      let best = 0, bestN = 0, cur = 0;
      for (let s = 0; s < W * H; s++) {
        if (!hull[s] || lab[s]) continue;
        cur++; let cnt = 0; stack.push(s); lab[s] = cur;
        while (stack.length) {
          const q = stack.pop(); cnt++;
          const qx = q % W, qy = (q / W) | 0;
          for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
            const nx = qx + dx, ny = qy + dy;
            if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
            const ni = ny * W + nx;
            if (hull[ni] && !lab[ni]) { lab[ni] = cur; stack.push(ni); }
          }
        }
        if (cnt > bestN) { bestN = cnt; best = cur; }
      }
      for (let s = 0; s < W * H; s++) if (lab[s] !== best) hull[s] = 0;
      n = bestN;
    }

    const at = (x, y) => (x >= 0 && y >= 0 && x < W && y < H) && hull[y * W + x];

    /* A PIXEL DISTANCE IS NOT A PROPERTY OF THE SHIP. It is a property of how
     * big the ship happens to be drawn, so the same dot on the same hull gives
     * a different number at a different zoom - which is exactly why C1's
     * numbers and these do not line up. The hull's own on-screen span is
     * measured here so the distance can also be given as a FRACTION OF THE
     * HULL, which is comparable between runs, machines and framings. */
    let x0h = W, y0h = H, x1h = -1, y1h = -1;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (hull[y * W + x]) {
      if (x < x0h) x0h = x; if (x > x1h) x1h = x;
      if (y < y0h) y0h = y; if (y > y1h) y1h = y;
    }
    const span = Math.max(x1h - x0h, y1h - y0h) || 1;
    const out = dots.map(dt => {
      const x0 = Math.round(dt.x), y0 = Math.round(dt.y);
      if (at(x0, y0)) return { port: dt.port, px: 0 };
      for (let r = 1; r <= cap; r++) {           /* expanding ring */
        for (let dx = -r; dx <= r; dx++) {
          if (at(x0 + dx, y0 - r) || at(x0 + dx, y0 + r)) return { port: dt.port, px: r };
        }
        for (let dy = -r + 1; dy <= r - 1; dy++) {
          if (at(x0 - r, y0 + dy) || at(x0 + r, y0 + dy)) return { port: dt.port, px: r };
        }
      }
      return { port: dt.port, px: null };        /* further than the cap */
    });
    for (const o of out) o.pct = o.px === null ? null : +(100 * o.px / span).toFixed(2);
    return { W, H, hullPx: n, coverage: +(100 * n / (W * H)).toFixed(1),
             span, out };
  }, { b64: shot.toString("base64"), dots: setup.dots,
       field: FIELD, thresh: THRESH, cap: CAP });

  console.log(`  silhouette ${res.W}x${res.H}, ${res.hullPx} hull px (${res.coverage}% of frame), hull span ${res.span}px, threshold ${THRESH}`);
  const off = res.out.filter(r => r.px === null || r.px > 0)
                     .sort((a, b) => (b.px ?? 1e9) - (a.px ?? 1e9));
  console.log(`  on the hull exactly: ${res.out.length - off.length} of ${res.out.length}`);
  for (const o of off.slice(0, 12))
    console.log(`     port ${String(o.port).padEnd(5)} ${o.px === null ? ">" + CAP + "px" : String(o.px) + "px"}`
                 + `  ${o.pct === null ? "" : o.pct + "% of hull span"}`);
  for (const o of off) if (o.px !== null && o.px > worst) worst = o.px;
}
console.log("\nworst measured distance across all hulls: " + worst + "px");
await browser.close();
