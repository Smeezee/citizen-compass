/**
 * E9 - THE HULL CONSTRAINT ON FLIGHT BLADES EXISTS, IT IS CALLED RequiredTags,
 * AND IT WAS IN THE SNAPSHOT ALL ALONG.

 *
 * RULE16: INDEPENDENT - the constraint is read out of CIG's own snapshot and the
 * page is then required to honour it. The snapshot is not something this
 * site produced, so a page that fitted a blade to the wrong hull cannot
 * make itself right by being consistent about it.
 *
 * Sleven, 2026-08-23: "an Anvil C8R Pisces able to put an Avenger Stalker
 * flight blade? I don't know what that is or why it's even on there... I could
 * be wrong, so please do the research."
 *
 * THE ORDER ASKS THIS CONTROL TO REPORT WHETHER THE FIELD EXISTS, BY NAME,
 * BEFORE ASSERTING ANYTHING ABOUT THE LIST. It does. Section 1 finds it in the
 * raw snapshot rather than in the built data, because the built data is the
 * thing under test and a constraint read out of the output would only prove
 * the output agrees with itself.
 *
 *   ports: 123 of the 136 editable FlightController ports carry RequiredTags
 *          naming a hull-specific kit - ANVL_Pisces_C8R_Blade,
 *          AEGS_Avenger_Stalker_Blade
 *   items: ALL 238 blades carry the matching tag on their own side
 *
 * So the order's second branch - "if no such field exists, assert the list is
 * GROUPED" - does not apply, and this file says so rather than quietly
 * implementing the fallback for a case that did not arise.
 *
 * WHAT IS NOT SETTLED, AND IS NOT CLAIMED. The order is explicit that no
 * source we hold says whether a blade made for one hull PHYSICALLY fits
 * another. This control does not answer that and does not try to. What it
 * asserts is narrower and is a fact about the game files: CIG's own data ties
 * these parts to these hulls, and the page had been ignoring it.
 *
 * MUTATORS
 *   --mutate-untagged  the tag join is removed from the built rule key, which
 *                      is the behaviour this replaces. The Pisces goes back to
 *                      238 and section 3 must fail.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { loadPage, reporter } from "./_loadout_harness.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const SNAP = join(ROOT, "data-layer", "external-sources", "scunpacked-data",
                  "snapshots", "20260801T204744Z");
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
const KNOWN = ["--mutate-untagged"];
if (MUT && KNOWN.indexOf(MUT) < 0) {
  console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2);
}

/* --mutate-untagged UNDOES THE JOIN IN THE PAGE'S OWN DATA rather than in the
   builder. Re-running the builder inside a control would make the control a
   second writer of the generated files (rule 14) and would take four minutes;
   collapsing every flight-controller port back onto one shared list is the
   same observable state, and it is the state that shipped. */
const mutate = [];
const H = loadPage({
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null });
if (MUT === "--mutate-untagged") {
  const n = H.g(`(function(){
    var all={}, hit=0;
    Object.keys(FITS).forEach(function(k){
      if(k.indexOf('FlightController|')!==0) return;
      (FITS[k]||[]).forEach(function(i){ all[i]=1; });
    });
    var every=Object.keys(all).sort();
    Object.keys(FITS).forEach(function(k){
      if(k.indexOf('FlightController|')!==0) return;
      FITS[k]=every.slice(); hit++;
    });
    return {lists:hit, size:every.length};
  })()`);
  if (!n.lists || n.size < 200) {
    console.log(`MUTATION DID NOT APPLY - collapsed ${n.lists} lists to `
      + `${n.size} parts, which is not the pre-E9 state. This run proves `
      + `nothing.`);
    process.exit(1);
  }
  console.log(`*** MUTATED: every flight-controller port shares one list of `
    + `${n.size} again ***`);
}
const { record, finish } = reporter(false);
const { g, openShip, SHIPS, META } = H;

console.log("==========================================================");
console.log("E9 - flight blades: does anything tie one to a hull");
console.log(MUT ? `MUTATED: ${MUT}` : "clean");
console.log("==========================================================");

/* =====================================================================
   1. THE FIELD, FOUND IN THE RAW SNAPSHOT AND NAMED.
   ===================================================================== */
console.log("\n--- 1. the constraining field, by name, from the source data ---");
let piscesAdmits = 0;
{
  let ships, items;
  try {
    ships = JSON.parse(readFileSync(join(SNAP, "ships.json"), "utf-8"));
    items = JSON.parse(readFileSync(join(SNAP, "ship-items.json"), "utf-8"));
  } catch (e) {
    console.log("NOT PERFORMED - the scunpacked snapshot is not on this "
      + "machine, so the question the order asks cannot be answered from the "
      + "source. Reported as not performed rather than as passed.\n  " + e.message);
    process.exit(2);
  }
  const seq = Array.isArray(items) ? items : Object.values(items);
  const itemTags = (it) => {
    const st = it.stdItem || {};
    let t = it.requiredTags || st.RequiredTags || it.entity_tags;
    if (typeof t === "string") t = t.split(/\s+/);
    return new Set((t || []).filter(Boolean));
  };
  const blades = seq.filter((it) =>
    String(it.type || (it.stdItem || {}).Type || "").split(".")[0]
      === "FlightController");
  record(blades.length > 200,
    `the catalogue carries ${blades.length} flight blades`);
  const bladeTagged = blades.filter((b) => itemTags(b).size > 0);
  record(bladeTagged.length === blades.length,
    "and EVERY ONE of them carries a tag on its own side of the join",
    `${bladeTagged.length} of ${blades.length}`);

  function* walk(n) {
    if (n && typeof n === "object" && !Array.isArray(n)) {
      yield n;
      for (const v of Object.values(n)) yield* walk(v);
    } else if (Array.isArray(n)) {
      for (const v of n) yield* walk(v);
    }
  }
  let ports = 0, tagged = 0, starved = 0;
  const perPort = [];
  const shipSeq = Array.isArray(ships) ? ships : Object.values(ships);
  for (const sh of shipSeq) {
    const name = sh.Name || sh.ClassName;
    for (const node of walk(sh)) {
      const ct = node.CompatibleTypes;
      if (!Array.isArray(ct) || !node.Editable) continue;
      if (!ct.some((c) => c && c.Type === "FlightController")) continue;
      ports++;
      let rt = node.RequiredTags;
      if (typeof rt === "string") rt = rt.split(/\s+/);
      const want = new Set((rt || []).filter(Boolean));
      if (!want.size) continue;
      tagged++;
      const hits = blades.filter((b) =>
        [...itemTags(b)].some((t) => want.has(t)));
      if (!hits.length) starved++;
      perPort.push({ name, tags: [...want], n: hits.length });
      if (/C8R Pisces/i.test(name || "")) piscesAdmits = hits.length;
    }
  }
  record(tagged > 0,
    "THE FIELD IS `RequiredTags`, on the port, in ships.json",
    `${tagged} of ${ports} editable FlightController ports carry it`);
  record(starved === 0,
    "and no tagged port is left with nothing - the join is complete on both "
    + "sides", `${starved} starved`);
  const spread = perPort.map((p) => p.n);
  console.log(`    tagged ports admit between ${Math.min(...spread)} and `
    + `${Math.max(...spread)} blades each`);
  record(Math.max(...spread) <= 8,
    "a tagged port admits a handful, not a catalogue",
    `max ${Math.max(...spread)}`);
  record(piscesAdmits > 0,
    "and the C8R Pisces - the hull Sleven asked about - is tagged",
    `${piscesAdmits} blades admitted by ANVL_Pisces_C8R_Blade`);
  /* THE ORDER'S SECOND BRANCH, EXPLICITLY DECLINED RATHER THAN FORGOTTEN. */
  console.log("    the order's fallback ('if no such field exists, assert the "
    + "list is GROUPED') does not apply - the field exists");
}

/* =====================================================================
   2. WHAT THE BUILT DATA NOW OFFERS.
   ===================================================================== */
console.log("\n--- 2. the fitment table carries the constraint ---");
{
  const stat = g(`(function(){
    var per={}, groups={};
    Object.keys(SHIPS).forEach(function(k){
      (SHIPS[k].slots||[]).forEach(function(s){
        if(s.t!=='flc'||!s.fit) return;
        groups[s.fit]=1;
        per[k]=(FITS[s.fit]||[]).length;
      });
    });
    var counts={};
    Object.keys(per).forEach(function(k){counts[per[k]]=(counts[per[k]]||0)+1;});
    return {hulls:Object.keys(per).length, groups:Object.keys(groups).length,
            counts:counts,
            wide:Object.keys(per).filter(function(k){return per[k]>5;}).length};
  })()`);
  record(stat.groups > 1,
    "flight-controller ports no longer share ONE fitment list",
    `${stat.groups} distinct lists across ${stat.hulls} hulls`);
  console.log(`    blades offered per hull: `
    + `${JSON.stringify(stat.counts)}`);
  record(META.blade_ports_starved === 0,
    "the build reports no port emptied by the constraint",
    String(META.blade_ports_starved));
  /* PORTS AND RULES ARE DIFFERENT FACTS and the build reports both. The first
     version of this line read a 73-RULE figure and asserted it as a port
     count, which is the same class of error as the sort's five-entry type
     table: a number that looked plausible for the wrong quantity. */
  record(META.blade_ports_constrained + META.blade_ports_unconstrained
    === stat.hulls,
    "the build's port counts add up to the hulls with such a port",
    `${META.blade_ports_constrained} + ${META.blade_ports_unconstrained} `
    + `vs ${stat.hulls}`);
  record(META.blade_ports_constrained > META.blade_ports_unconstrained * 5,
    "and the great majority of them ARE constrained",
    `${META.blade_ports_constrained} constrained, `
    + `${META.blade_ports_unconstrained} not`);
  record(META.blade_rules_constrained > 1
    && META.blade_rules_constrained < META.blade_ports_constrained,
    "with the rules deduplicated below the port count, as every other rule is",
    `${META.blade_rules_constrained} rules for `
    + `${META.blade_ports_constrained} ports`);
  /* THE ONES THAT ARE NOT CONSTRAINED ARE NOT A FAILURE AND ARE NOT HIDDEN.
     They state no kit, and inventing one from their silence is the opposite of
     what the data says. NAMED, because "13 hulls" is a number and these are
     ships somebody can go and look at. */
  const wideNames = g(`(function(){var out=[];Object.keys(SHIPS).forEach(
    function(k){(SHIPS[k].slots||[]).forEach(function(s){
      if(s.t==='flc'&&s.fit&&(FITS[s.fit]||[]).length>5) out.push(SHIPS[k].n);
    });});return out;})()`);
  console.log(`    ${wideNames.length} port(s) still offer the full list, on: `
    + `${[...new Set(wideNames)].join(", ")}`);
  record(wideNames.length === META.blade_ports_unconstrained,
    "and they are exactly the ports the build counted as unconstrained",
    `${wideNames.length} vs ${META.blade_ports_unconstrained}`);
}

/* =====================================================================
   3. THE PAGE, ON SLEVEN'S OWN SHIP.
   ===================================================================== */
console.log("\n--- 3. the C8R Pisces picker ---");
{
  const key = g(`Object.keys(SHIPS).find(function(k){
    return /C8R Pisces/i.test(SHIPS[k].n||""); })`);
  record(!!key, "the Anvil C8R Pisces Rescue is in the data", String(key));
  openShip(key);
  const slot = g(`(ship().slots||[]).find(function(s){return s.t==='flc';})`);
  record(!!slot, "and it has a flight-controller port", slot && slot.id);
  const html = g(`pickerHTML(ship().slots.find(function(s){
    return s.id===${JSON.stringify(slot.id)};}))`);
  const rows = [...html.matchAll(/data-part="([^"]+)"/g)].map((m) => m[1]);
  /* THE ASSERTION THE ORDER ASKS FOR: the rendered list length matches the
     count the constraining field admits. */
  record(rows.length === piscesAdmits,
    `the rendered list is exactly the ${piscesAdmits} blades RequiredTags `
    + `admits`, `${rows.length} rendered`);
  const names = g(`${JSON.stringify(rows)}.map(function(k){return (P[k]||{}).n;})`);
  console.log(`    ${JSON.stringify(names)}`);
  record(names.every((n) => /Pisces/i.test(n || "")),
    "and every one of them is a Pisces blade - no Avenger Stalker among them",
    /* CAPPED. Under --mutate-untagged this is 235 names and the failure line
       scrolls the terminal - a detail nobody can read is not a detail. */
    (() => {
      const bad = names.filter((n) => !/Pisces/i.test(n || ""));
      return bad.length > 6
        ? `${bad.length} not Pisces, e.g. ${bad.slice(0, 4).join(", ")}`
        : bad.join(", ");
    })());
  record(names.some((n) => /PHB/.test(n)) && names.some((n) => /TSB/.test(n)),
    "both tunings are offered, PHB and TSB");

  /* AND THE PAGE ANSWERS THE QUESTION HE ACTUALLY ASKED. */
  record(/flight blade/i.test(html),
    "the picker says what a flight blade IS, where somebody is choosing one");
  record(/manoeuvrability/i.test(html) && /top speed/i.test(html),
    "and what the two tunings do");
  record(/tie to this hull/i.test(html),
    "and states that these are the blades the files tie to this hull",
    "");
}

/* =====================================================================
   4. AND THE UNCONSTRAINED CASE SAYS SO.
   ===================================================================== */
console.log("\n--- 4. a port that names no kit says that, rather than implying one ---");
{
  const wide = g(`(function(){
    var out=null;
    Object.keys(SHIPS).forEach(function(k){
      if(out) return;
      (SHIPS[k].slots||[]).forEach(function(s){
        if(out||s.t!=='flc'||!s.fit) return;
        if((FITS[s.fit]||[]).length>5) out={ship:k, slot:s.id,
          n:(FITS[s.fit]||[]).length};
      });
    });
    return out;
  })()`);
  if (!wide) {
    console.log("    every flight-controller port is constrained - nothing to "
      + "check here, and that is reported rather than passed silently");
  } else {
    openShip(wide.ship);
    const html = g(`pickerHTML(ship().slots.find(function(s){
      return s.id===${JSON.stringify(wide.slot)};}))`);
    record(/names no blade kit/i.test(html),
      `${g(`SHIPS[${JSON.stringify(wide.ship)}].n`)} offers ${wide.n} and SAYS `
      + `the port names no kit, rather than implying all of them were made for `
      + `it`);
    record(!/tie to this hull/i.test(html),
      "and does NOT claim the files tie them to this hull");
  }
}

/* =====================================================================
   5. THE THING THE ORDER SAYS IS NOT SETTLED IS NOT CLAIMED.
   ===================================================================== */
console.log("\n--- 5. what is not claimed ---");
{
  const key = g(`Object.keys(SHIPS).find(function(k){
    return /C8R Pisces/i.test(SHIPS[k].n||""); })`);
  openShip(key);
  const slot = g(`(ship().slots||[]).find(function(s){return s.t==='flc';})`);
  const html = g(`pickerHTML(ship().slots.find(function(s){
    return s.id===${JSON.stringify(slot.id)};}))`);
  record(!/cannot fit|will not fit|incompatible/i.test(html),
    "the page does not claim another hull's blade would not physically fit - "
    + "no source we hold settles that, and the order says so explicitly");
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : `the constraining field is RequiredTags; the C8R Pisces admits `
    + `${piscesAdmits}`);
void mutate;
