/**
 * I6 - a 404 sweep of the DEPLOYED testing site.

 *
 * RULE16: INDEPENDENT - it fetches the deployed origin and reads what a visitor
 * would actually receive. A link that is broken in the served bytes cannot
 * be argued out of by anything in this tree, and a build exiting 0 is not
 * accepted as evidence about it. The canary is the other half: the sweep
 * must be able to report a failure, and it is made to do so on every run.
 *
 * "Every internal link and every asset the pages reference, fetched from the
 *  served origin. NOT from disk. This is the last chance to find a dead link
 *  before it is on the public site."
 *
 * FROM THE ORIGIN, IN BOTH DIRECTIONS
 * ------------------------------------
 * The references are discovered by FETCHING THE DEPLOYED PAGES and reading what
 * they actually contain, not by reading testing/_deploy on this machine. That
 * matters more than it sounds: the local build is usually ahead of the deployed
 * one, so a disk-driven sweep reports "missing" for files that simply have not
 * been deployed yet, and reports nothing at all about a file that was deployed
 * and then removed. What is served is the subject, so what is served is what is
 * read.
 *
 * WHAT IS SWEPT
 * -------------
 *   - every internal href and src in every page reachable from /
 *   - every url(...) in inline CSS
 *   - every 3D model the page can load, read out of the page's own CC_EMBED map
 *   - every ship thumbnail, derived with the page's own CC_SAFE rule from the
 *     same map - because those paths are computed at runtime and appear
 *     nowhere in the markup for a link checker to find
 *   - external links, checked and reported SEPARATELY: a dead github.com link
 *     on the download page is worth knowing about, but somebody else's outage
 *     is not this project's failure
 *
 * THE CONTROL, WHICH IS NOT OPTIONAL (rule 12)
 * ---------------------------------------------
 * A URL that is KNOWN to be absent is injected into the sweep, and the sweep is
 * required to report it. A sweep that has never reported anything is not a
 * sweep - it is a green light with no bulb in it. If the canary comes back
 * clean, this exits non-zero and says the sweep cannot be trusted, whatever it
 * found or did not find about the real URLs.
 *
 * HEAD, not GET, for assets. 235 models are 341 MB and nobody needs to download
 * them to learn whether they are there. Pages are fetched with GET because
 * their content is what the discovery reads.
 *
 * Usage:  node checks/_verify_deployed_links.mjs [baseUrl] [--self-test]
 *
 * --self-test inverts the verdict: it makes the canary the ONLY absent URL and
 * requires the run to fail anyway, proving the canary alone can fail the sweep.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const BASE = (process.argv.find((a) => a.startsWith("http")) ||
  "https://citizencompasstesting.citizencompass-contact.workers.dev")
  .replace(/\/$/, "");
const SELFTEST_ARG = process.argv.includes("--self-test");
const SELFTEST = SELFTEST_ARG;

// Known to be absent. Deliberately specific, so it cannot collide with
// anything real, and deliberately shaped like a page so it exercises the same
// path a real page would.
//
// UNDER --self-test IT POINTS AT A PAGE THAT DEFINITELY EXISTS. That inverts
// the one expectation this sweep's trustworthiness rests on: the canary comes
// back 200, the canary assertion must therefore fire, and the run must fail
// BECAUSE OF IT. If it does not fire, the assertion is dead and the sweep has
// been reporting a green light with no bulb in it - and the run exits ZERO, so
// that run_all_controls.py's "every self-test must exit non-zero" is what
// catches it.
const CANARY = SELFTEST_ARG
  ? "/"
  : "/this-page-is-the-canary-and-must-404-8f3a91.html";

const CONCURRENCY = 12;
const TIMEOUT_MS = 30000;

let failures = 0;
function fail(msg) { failures++; console.log("  FAIL " + msg); }

async function fetchWithTimeout(url, opts = {}) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { ...opts, signal: ctl.signal, redirect: "follow" });
  } finally {
    clearTimeout(t);
  }
}

/** Absolute URL, or null for anything this sweep does not follow. */
function resolve(ref, from) {
  if (!ref) return null;
  const r = ref.trim();
  if (!r || r.startsWith("#") || r.startsWith("data:") ||
      r.startsWith("javascript:") || r.startsWith("mailto:") ||
      r.startsWith("blob:") || r.startsWith("about:")) return null;
  try { return new URL(r, from).href; } catch { return null; }
}

/** Everything one page points at.
 *
 * MARKUP ONLY, AND THAT IS NOT A SHORTCUT. The first version of this read the
 * whole page and reported thirteen dead links that were not links at all:
 * `src="${logo}"` inside a template literal, `URL.createObjectURL(new Blob(...))`
 * matched by the CSS `url(...)` pattern, `${esc(SUM.file)}` from an href being
 * built at runtime. Every one of them 404s when you ask a server for it, and
 * every one of them is fine.
 *
 * A checker that cries wolf gets switched off, which is worse than not having
 * one. So <script> blocks are removed before the markup patterns run - and the
 * one thing this sweep genuinely needs from a script, the CC_EMBED model map,
 * is taken from the RAW page below rather than from the stripped copy.
 *
 * <link rel="preconnect"> and dns-prefetch are dropped too: their href is an
 * ORIGIN, not a document, and asking https://fonts.gstatic.com/ for a page
 * correctly returns 404 while the preconnect works perfectly.
 */
// WHAT THE BUILD ACTUALLY PUBLISHES, read out of its own list.
//
// Parsed rather than imported: deploy_pages.py is Python, and parsed rather
// than restated because a copy of this list here is exactly the drift that
// made the floor stale. Commented-out entries are skipped - that is how a page
// is unpublished in that file, so treating one as published would defeat the
// point.
const PAGES_SRC = join(dirname(fileURLToPath(import.meta.url)), "..",
                       "testing", "_src", "deploy_pages.py");

function publishedOutputs() {
  let text;
  try {
    text = readFileSync(PAGES_SRC, "utf-8");
  } catch {
    return null;
  }
  const out = new Set();
  for (const line of text.split("\n")) {
    if (/^\s*#/.test(line)) continue;
    const m = line.match(/\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)/);
    if (m) out.add(m[2]);
  }
  return out.size ? out : null;
}


// THE FLOOR'S DECISION, as a pure function so it can be driven with input that
// must fail it. A branch that has only ever been reached by real, healthy data
// is a branch nobody has seen work.
//
//   published === null  ->  [{kind: "unreadable"}]
//   a floor entry the build no longer publishes  ->  {kind: "stale"}
//   a published floor entry missing from the swept set  ->  {kind: "blind"}
function floorProblems(must, published, swept) {
  if (published === null) return [{ kind: "unreadable", files: [...must] }];
  const stale = must.filter((f) => !published.has(f));
  const out = [];
  if (stale.length) out.push({ kind: "stale", files: stale });
  const expected = must.filter((f) => published.has(f));
  const missed = expected.filter((f) => !swept.some((u) => u.endsWith("/" + f)));
  if (missed.length) out.push({ kind: "blind", files: missed });
  return out;
}


// PROVEN AGAINST KNOWN-BAD INPUT, on every run, before the real one is trusted.
//
// This costs no network and takes no time, and without it the stale branch
// added on 2026-08-22 would be code that had never once executed - which is
// how the thing it replaced came to be wrong in the first place.
function proveFloorCanFail() {
  const cases = [
    ["a floor entry the build no longer publishes is called STALE",
     floorProblems(["gone.gen.js"], new Set(["kept.gen.js"]), []),
     "stale"],
    ["a published entry missing from the swept set is called BLIND",
     floorProblems(["kept.gen.js"], new Set(["kept.gen.js"]), []),
     "blind"],
    ["an unreadable PAGES list is called UNREADABLE, never clean",
     floorProblems(["kept.gen.js"], null, []),
     "unreadable"],
    ["and a healthy floor reports nothing",
     floorProblems(["kept.gen.js"], new Set(["kept.gen.js"]),
                   ["https://x/kept.gen.js"]),
     null],
  ];
  console.log("\n--- the floor can fail, and tells the two faults apart ---");
  for (const [label, got, want] of cases) {
    const kind = got.length ? got[0].kind : null;
    if (kind === want) console.log("  ok   " + label);
    else fail(`${label} - got ${kind === null ? "nothing" : kind}`);
  }
}


function refsIn(html, pageUrl) {
  const out = new Set();
  const add = (r) => { const u = resolve(r, pageUrl); if (u) out.add(u); };

  // THE TAGS SURVIVE; ONLY THE INLINE CODE GOES. Getting this wrong the first
  // time made the sweep blind to EVERY <script src="...">, which is every
  // .gen.js file on this site - find_data, hardpoint_data, kb_actions,
  // loadout_data, holo_data, sc_export and the published checksum. Those are
  // precisely the files whose absence breaks a page while the page still
  // serves 200, and the sweep was not looking at a single one of them.
  //
  // Found on 2026-08-21, and only because adding hardpoint_data.gen.js to
  // index.html did not move the swept count. A sweep that reports the same
  // number after you add a file is not reporting on that file.
  const markup = html
    .replace(/(<script\b[^>]*>)[\s\S]*?(<\/script>)/gi, "$1$2")
    .replace(/<link\b[^>]*\brel\s*=\s*["'](?:preconnect|dns-prefetch)["'][^>]*>/gi, " ");

  for (const m of markup.matchAll(/\b(?:href|src)\s*=\s*"([^"]*)"/gi)) add(m[1]);
  for (const m of markup.matchAll(/\b(?:href|src)\s*=\s*'([^']*)'/gi)) add(m[1]);
  for (const m of markup.matchAll(/url\(\s*['"]?([^'")]+)['"]?\s*\)/gi)) add(m[1]);

  // The 3D models. They are values in a JSON map the page carries, so no link
  // checker reading markup would ever see them - and a deploy that dropped the
  // models folder still serves a page that looks completely correct.
  const embed = html.match(/const CC_EMBED\s*=\s*(\{[\s\S]*?\});/);
  if (embed) {
    try {
      const map = JSON.parse(embed[1]);
      const safe = (n) => String(n).replace(/[^A-Za-z0-9._-]+/g, "_");
      for (const [folder, path] of Object.entries(map)) {
        add(path);
        // The thumbnail path the page computes at runtime: 'images/' +
        // CC_SAFE(dir) + '.webp'. Derived with the page's own rule, taken from
        // the page's own source above, so the two cannot drift.
        add("images/" + safe(folder) + ".webp");
      }
    } catch (e) {
      fail(`CC_EMBED on ${pageUrl} did not parse (${e.message}) - the models ` +
           `and thumbnails were NOT swept. Reported, never skipped quietly.`);
    }
  }
  return out;
}

async function mapLimit(items, limit, fn) {
  const results = [];
  let i = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (i < items.length) {
      const n = i++;
      results[n] = await fn(items[n], n);
    }
  });
  await Promise.all(workers);
  return results;
}

async function probe(url, method) {
  try {
    const res = await fetchWithTimeout(url, { method });
    return { url, status: res.status, redirected: res.redirected, final: res.url };
  } catch (e) {
    return { url, status: 0, error: String(e.message || e) };
  }
}

async function main() {
  console.log(`--- I6: 404 sweep of ${BASE} ---`);
  console.log("Fetched from the served origin. Nothing here reads the local "
    + "build.\n");

  // ---- 1. discover the pages ------------------------------------------
  // Every page the build ships, seeded by name. Crawling from / alone reached
  // only five of the seven: /holo, /download and /stick-test are standalone
  // URLs that nothing on the site links to. Leaving them out would mean the
  // sweep quietly did not look at three of the seven pages about to go public.
  //
  // Which of them are ORPHANED is reported below rather than glossed over - a
  // page nobody can reach from the site is a fact somebody should decide about
  // deliberately, not a fact a link checker should hide by seeding around it.
  const SHIPPED_PAGES = ["/", "/find", "/keybinds", "/loadout", "/holo",
                         "/download", "/stick-test"];
  const pages = new Set();
  const seen = new Set();
  const pageBodies = new Map();
  const linkedTo = new Set();
  const queue = SHIPPED_PAGES.map((p) => BASE + p);

  while (queue.length) {
    const url = queue.shift();
    if (seen.has(url)) continue;
    seen.add(url);
    const res = await fetchWithTimeout(url).catch((e) => ({ ok: false, status: 0, _e: e }));
    if (!res.ok) {
      fail(`page ${url} -> ${res.status || "no response"}`);
      continue;
    }
    const html = await res.text();
    pageBodies.set(url, html);
    pages.add(url);
    for (const ref of refsIn(html, url)) {
      if (!ref.startsWith(BASE + "/")) continue;
      const path = new URL(ref).pathname;
      // Follow HTML only. Assets are probed, not crawled.
      if (/\.(html?)$/i.test(path) || path === "/" || !/\.[a-z0-9]+$/i.test(path)) {
        linkedTo.add(path.replace(/\.html?$/i, "").replace(/^$/, "/"));
        if (!seen.has(ref)) queue.push(ref);
      }
    }
  }

  console.log(`pages fetched: ${pages.size}`);
  for (const p of [...pages].sort()) console.log("  " + new URL(p).pathname);

  // HOW EACH PAGE IS REACHED. The crawl above reads MARKUP, so a page whose
  // link is built by JavaScript - /loadout is opened from the ship view with
  // link.href='loadout.html#'+cls - would read as an orphan when it is nothing
  // of the kind. Calling that "unreachable" would be a checker stating
  // something false, so the raw bodies are searched too and the three cases
  // are named separately.
  const allBodies = [...pageBodies.values()].join("\n");
  console.log("\nhow each shipped page is reached:");
  const unreferenced = [];
  for (const p of SHIPPED_PAGES) {
    if (p === "/") { console.log("  /            the entry point"); continue; }
    const file = p.slice(1) + ".html";
    let how;
    if (linkedTo.has(p) || linkedTo.has(p + "/")) how = "linked in the markup";
    else if (allBodies.includes(file)) how = "linked from JAVASCRIPT only";
    else { how = "NOTHING references it - reachable by URL alone"; unreferenced.push(p); }
    console.log(`  ${p.padEnd(12)} ${how}`);
  }
  if (unreferenced.length) {
    console.log("\n  " + unreferenced.join(", ") + " are not referenced by any "
      + "page.\n  Not a failure - they serve. But a visitor cannot find them, "
      + "and that is\n  worth deciding about deliberately rather than "
      + "discovering later.");
  }

  // ---- 2. collect every reference -------------------------------------
  const internal = new Set();
  const external = new Set();
  for (const [pageUrl, html] of pageBodies) {
    for (const ref of refsIn(html, pageUrl)) {
      (ref.startsWith(BASE + "/") ? internal : external).add(ref);
    }
  }

  // THE CONTROL. A URL known to be absent, mixed in with the real ones so it
  // travels the same code path they do.
  const canaryUrl = BASE + CANARY;
  internal.add(canaryUrl);

  // A NAMED FLOOR, so the blind spot above cannot come back unnoticed. These
  // are loaded by <script src> and nothing else points at them; if the
  // extractor ever stops seeing script tags again, the swept set loses them
  // silently and the sweep goes on reporting clean.
  //
  // THE FLOOR IS CROSS-CHECKED AGAINST WHAT THE BUILD PUBLISHES, because a
  // hand-written list of filenames is a second writer for a fact that lives in
  // deploy_pages.py (rule 14) - and on 2026-08-22 the two drifted. N3
  // unpublished hardpoint_data.gen.js: index.html stopped loading it, the file
  // is still generated and still checked, it is simply no longer served. The
  // floor went on demanding it and this control reported "the reference
  // extractor has stopped seeing script tags" - a real failure with entirely
  // the wrong diagnosis, pointing at working code.
  //
  // So the two failure modes are now told apart and named separately:
  //
  //   floor is STALE      it demands a file the build no longer publishes.
  //                       Fix the list, not the extractor.
  //   extractor is BLIND  it demands a published file that the swept set does
  //                       not contain. Fix the extractor.
  //
  // The floor is NOT derived from the swept set - that would be circular, and
  // an extractor that went blind would empty both sides and pass. It is named
  // here and validated against an independent source: the build's own PAGES.
  const MUST_BE_SWEPT = ["find_data.gen.js", "kb_actions.gen.js",
                         "loadout_data.gen.js"],
        swept = [...internal];

  proveFloorCanFail();

  const published = publishedOutputs();
  const problems = floorProblems(MUST_BE_SWEPT, published, swept);
  for (const pr of problems) {
    if (pr.kind === "unreadable") {
      fail(`NOT PERFORMED - ${PAGES_SRC} could not be read, so whether the `
        + `floor still matches what the build publishes is unknown. `
        + `Reported, never assumed.`);
    } else if (pr.kind === "stale") {
      fail(`the floor is STALE: ${pr.files.join(", ")} is named in this `
        + `control but the build no longer publishes it (see `
        + `deploy_pages.py). This is NOT an extractor fault - update the `
        + `floor.`);
    } else {
      fail(`these files are loaded by <script src> and were NOT in the swept `
        + `set: ${pr.files.join(", ")}. The reference extractor has stopped `
        + `seeing script tags, so a missing data file would not be reported.`);
    }
  }
  if (!problems.length) {
    console.log(`\nfloor: every <script src> data file the build publishes is `
      + `in the swept set (${MUST_BE_SWEPT.join(", ")})`);
  }

  const list = [...internal].sort();
  console.log(`\ninternal references to check: ${list.length} `
    + `(including 1 canary that MUST come back absent)`);

  const results = await mapLimit(list, CONCURRENCY, (u) =>
    probe(u, /\.(html?)$/i.test(new URL(u).pathname) || !/\.[a-z0-9]+$/i.test(new URL(u).pathname)
      ? "GET" : "HEAD"));

  const canary = results.find((r) => r.url === canaryUrl);
  const bad = results.filter((r) => r.url !== canaryUrl && r.status !== 200);
  const redirected = results.filter((r) => r.url !== canaryUrl && r.redirected);

  console.log("\n--- THE CONTROL: a URL known to be absent ---");
  console.log(`  ${CANARY} -> ${canary ? canary.status : "not probed"}`);
  const canaryReported = canary && canary.status !== 200;
  if (canaryReported) {
    console.log("  ok   the sweep REPORTS an absent URL, so a clean result "
      + "below means something");
  } else {
    fail("THE CANARY CAME BACK 200. This sweep cannot report an absent URL, "
      + "so nothing it says about the real ones can be trusted. Reported as "
      + "NOT PERFORMED, never as clean.");
  }

  console.log("\n--- internal references that did not return 200 ---");
  if (!bad.length) {
    console.log("  none");
  } else {
    for (const r of bad) {
      fail(`${new URL(r.url).pathname} -> ${r.error ? "ERROR " + r.error : r.status}`);
    }
  }

  if (redirected.length) {
    console.log(`\n--- ${redirected.length} reference(s) reached 200 VIA A `
      + `REDIRECT (not a failure, but worth knowing) ---`);
    for (const r of redirected.slice(0, 12)) {
      console.log(`  ${new URL(r.url).pathname} -> ${new URL(r.final).pathname}`);
    }
    if (redirected.length > 12) console.log(`  ... and ${redirected.length - 12} more`);
  }

  // ---- 3. external links, reported separately -------------------------
  console.log(`\n--- external links (${external.size}), reported separately: `
    + `somebody else's outage is not this project's failure ---`);
  if (external.size) {
    const ext = await mapLimit([...external].sort(), 6, (u) => probe(u, "GET"));
    for (const r of ext) {
      const okish = r.status >= 200 && r.status < 400;
      console.log(`  ${okish ? "ok  " : "DEAD"} ${r.status || r.error} ${r.url}`);
      if (!okish) {
        console.log("       ^ not counted as a failure of this sweep, but it "
          + "is a dead link on a page about to go public");
      }
    }
  } else {
    console.log("  none");
  }

  // ---- verdict --------------------------------------------------------
  console.log("");
  console.log(`swept ${list.length - 1} internal references across `
    + `${pages.size} pages, plus ${external.size} external`);

  if (SELFTEST) {
    // The canary pointed at a page that exists, so the canary assertion had to
    // fire. If it did not, the assertion is dead and every clean run this
    // sweep has ever reported was meaningless.
    if (canaryReported) {
      console.log("--self-test NOT PROVEN: the canary pointed at a page that "
        + "EXISTS and the assertion still passed it. The canary check is dead, "
        + "so a clean sweep means nothing.");
      // Exit ZERO deliberately. run_all_controls.py requires every --self-test
      // to exit NON-zero, so a zero here is exactly what makes the sweep report
      // this control's inverted mode as broken. Inventing a distinct exit code
      // would have hidden it from the one thing that checks.
      process.exit(0);
    }
    console.log(`--self-test: the canary assertion fired as required `
      + `(${failures} failure(s) in total). A non-zero exit is the correct `
      + `outcome.`);
    process.exit(1);
  }

  if (failures) {
    console.log(`SWEEP FAILED: ${failures} problem(s) above.`);
    process.exit(1);
  }
  console.log("SWEEP CLEAN - and the canary proves the sweep can report.");
}

main().catch((e) => { console.log("SWEEP NOT PERFORMED:", e); process.exit(1); });
