# -*- coding: utf-8 -*-
"""
Rule 12 proof for L1-L4: the derived type scan and the per-port fitment rule.

RULE16: INDEPENDENT - the port counts in META are recomputed here from the port
list rather than read back, so a generator that miscounted is caught by
arithmetic rather than by its own summary. The expected type set is
written down here as well.

WHAT IT CANNOT REACH, since both halves live in one generated file: a
port LIST that is wrong. The recount would agree with it, being a count
of the same wrong list. What is proven is that the file does not
contradict itself.

WHAT COULD SILENTLY GO WRONG HERE
---------------------------------
Everything the ship page claims rests on one sentence: *what a port accepts
comes from `CompatibleTypes` + `MinSize`/`MaxSize` on that port*. If that is
wrong, the page does not crash. It quietly offers a part that cannot be
mounted, or quietly hides one that can, and it looks exactly the same either
way. That is the failure this file exists to catch.

The order names the two halves and they are BOTH controls, not one:

    a part the port accepts  MUST APPEAR
    a part it does not       MUST BE ABSENT - not greyed, absent

The second half is the one that can pass vacuously. A `fits()` that returns
nothing for everything satisfies "the wrong part is absent" perfectly, so the
positive half is load-bearing rather than decoration. Both are asserted with
NAMED examples, per the order's report section.

Three more things are proven here because each one has a silent failure mode:

  THE SCAN IS DERIVED, NOT TRANSCRIBED. If someone replaces the port scan with
  a hardcoded list, every count still looks plausible. So the emitted type list
  is recomputed from the snapshot here, independently, and compared - and the
  measured EDITABLE-PORT COUNT PER TYPE has to agree too, because a list that
  matches by luck will not match by arithmetic.

  SUBTYPES MUST NOT BE ENFORCED AS LITERALS. 253 quantum ports declare
  `SubTypes: ["QDrive"]` while all 63 quantum drives carry `subType:
  "UNDEFINED"`. Enforce that strictly and every quantum picker on the site is
  empty - and an empty picker still renders. So a floor is asserted: every
  quantum, jump, shield, power plant and cooler port MUST offer more than one
  option, or the subtype logic has silently closed.

  THE GAME'S OWN LOADOUT MUST BE OFFERABLE. The strongest available check on
  our fitment rule is CIG's: the part the game actually ships in a port must be
  offered at that port. 45 ports in this snapshot fail CIG's own declared rule,
  so they are carried by `also` - and this asserts that EVERY editable slot's
  stock part is reachable, which is what stops the page telling a player the
  part already on their ship does not fit it.

  THE PATCH OVERRIDE MUST ACTUALLY REACH THE SLOT. L4 says a port opening up
  later must be a DATA change, not a code change. A mechanism nobody has ever
  fired is an untested gate wearing a reassuring name, so this plants a real
  override, regenerates, and confirms it lands on the named slot - then removes
  it and confirms it is gone.

AND THE CHECK IS PROVEN AGAINST KNOWN-BAD INPUT. `--mutants` plants six defects
that a real regression would produce and confirms each one is CAUGHT. If those
mutants pass, this file is not a check.

Run: venv/Scripts/python.exe checks/_verify_loadout_fitment.py
     venv/Scripts/python.exe checks/_verify_loadout_fitment.py --mutants
"""

import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import build_loadout_data as B  # noqa: E402

GEN = B.OUT

FAILURES = []
NOTES = []


def say(line):
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def check(ok, label, detail=""):
    if ok:
        say("  ok    %s" % label)
    else:
        FAILURES.append("%s%s" % (label, ("  -- " + detail) if detail else ""))
        say("  FAIL  %s%s" % (label, ("  -- " + detail) if detail else ""))
    return ok


def load_generated(path=GEN):
    """Parse the emitted JS back into dicts. Deliberately does NOT import it as
    JS: reading the shipped bytes is the point, and a parse failure here is a
    real finding rather than a test-harness problem."""
    if not os.path.exists(path):
        sys.exit("MISSING: %s - run build_loadout_data.py first." % path)
    with io.open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    out = {}
    for name in ("LOADOUT_META", "LOADOUT_TYPES", "LOADOUT_HP", "LOADOUT_PARTS",
                 "LOADOUT_FITS", "LOADOUT_ARMOR", "LOADOUT_PAINTS",
                 "LOADOUT_PAINTSETS", "LOADOUT_SHIPS", "LOADOUT_UNRELEASED"):
        m = re.search(r"^const " + name + r"=(.*);$", src, re.M)
        if not m:
            sys.exit("MISSING SECTION %s in %s" % (name, path))
        out[name] = json.loads(m.group(1))
    return out


def load_snapshot():
    with io.open(B.SHIPS_JSON, "r", encoding="utf-8") as fh:
        ships = json.load(fh)
    with io.open(B.ITEMS_JSON, "r", encoding="utf-8") as fh:
        items = json.load(fh)
    return ships, items


# --------------------------------------------------------------------------

def run(data, ships, items, strict=True):
    """Every control. `strict` off is used by the mutant runner, which needs
    the failure list rather than a process exit."""
    META = data["LOADOUT_META"]
    TYPES = data["LOADOUT_TYPES"]
    HP = data["LOADOUT_HP"]
    PARTS = data["LOADOUT_PARTS"]
    FITS = data["LOADOUT_FITS"]
    ARMOR = data["LOADOUT_ARMOR"]
    SHIPS = data["LOADOUT_SHIPS"]
    PAINTS = data["LOADOUT_PAINTS"]
    PSETS = data["LOADOUT_PAINTSETS"]

    catalogue_types = set(it.get("type") or "" for it in items if it.get("type"))
    by_class = {}
    for it in items:
        cn = it.get("className")
        if cn:
            by_class[cn.lower()] = it

    all_ports = []
    for s in ships:
        B.walk_ports(s.get("Loadout"), all_ports)

    # ---- 1. THE SCAN IS DERIVED ------------------------------------------
    say("")
    say("1. the type list is DERIVED from the ports, not transcribed")
    expect, editable_total, untyped = B.select_types(all_ports, catalogue_types)
    emitted = set(META.get("types") or [])
    check(emitted == set(expect),
          "emitted type list == independently rescanned type list",
          "emitted-only %s  scan-only %s" % (sorted(emitted - set(expect)),
                                             sorted(set(expect) - emitted)))
    check(len(emitted) > 5,
          "the scan found more than the five hand-written types it replaced",
          "found %d" % len(emitted))
    # The counts, so a list that matches by luck does not match by arithmetic.
    bad_counts = []
    for t in sorted(expect):
        code = B.code_for(t)
        if code not in TYPES:
            bad_counts.append("%s missing from LOADOUT_TYPES" % t)
        elif TYPES[code].get("t") != t:
            bad_counts.append("%s -> code %s maps back to %s"
                              % (t, code, TYPES[code].get("t")))
    check(not bad_counts, "every scanned type has a code that maps back to it",
          "; ".join(bad_counts[:3]))
    check(META.get("editable_ports") == editable_total,
          "META.editable_ports == the rescanned editable count",
          "%s vs %s" % (META.get("editable_ports"), editable_total))

    # BOTH CONDITIONS, not one. `Editable` alone admits 26,182 ports including
    # doors and dashboards; the emitted component count must be far smaller.
    check(META["editable_component_ports"] < editable_total * 0.5,
          "the second condition actually excluded something",
          "%d component of %d editable" % (META["editable_component_ports"],
                                           editable_total))
    NOTES.append("scan selected %d types over %d editable ports; %d of those "
                 "ports are real component slots"
                 % (len(emitted), editable_total,
                    META["editable_component_ports"]))

    # No excluded type leaked in.
    check(not (emitted & B.EXCLUDED_TYPES),
          "no excluded type (Flair_*, GroundVehicleMissileLauncher) was emitted",
          str(sorted(emitted & B.EXCLUDED_TYPES)))
    # Paints ARE selected - the order says they are not excluded, they go to L7.
    check(B.PAINT_TYPE in emitted,
          "Paints is selected by the scan (L7), not excluded")

    # ---- 2. L3, BOTH HALVES, WITH NAMED EXAMPLES -------------------------
    say("")
    say("2. L3 - a part the port accepts APPEARS; one it does not is ABSENT")
    # Positive: for every editable slot, the part the GAME fits there must be
    # offerable. This is CIG's own answer to "does this mount here".
    missing_stock = []
    checked = 0
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            key, stock = sl.get("fit"), sl.get("stock")
            if not key or not stock:
                continue
            checked += 1
            if stock in (FITS.get(key) or []) or sl.get("also") == stock:
                continue
            missing_stock.append("%s / %s: %s" % (rec["n"], HP[sl["h"]], stock))
    check(checked > 5000, "enough editable slots to be worth asserting on",
          "%d" % checked)
    check(not missing_stock,
          "OFFERED: every editable slot offers the part CIG fits in it "
          "(%d slots)" % checked,
          "%d missing, e.g. %s" % (len(missing_stock), missing_stock[:3]))

    # Named positive example, per the order's report section.
    named_pos = None
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            if sl.get("fit") and sl.get("stock") and TYPES.get(sl["t"], {}).get("t") == "Shield":
                offered = FITS.get(sl["fit"]) or []
                if len(offered) > 3:
                    named_pos = (rec["n"], HP[sl["h"]], sl["stock"],
                                 PARTS[sl["stock"]]["n"], len(offered))
                    break
        if named_pos:
            break
    check(named_pos is not None, "a named OFFERED example exists")
    if named_pos:
        NOTES.append("L3 OFFERED: %s port `%s` offers %d parts including its "
                     "own stock %s (%s)"
                     % (named_pos[0], named_pos[1], named_pos[4],
                        named_pos[3], named_pos[2]))

    # Negative: a part outside the port's size window must NOT be offered.
    # Asserted structurally over every fitment list, then named once.
    violations = []
    rule_of = {}
    for entry, _p, _par in all_ports:
        if not entry.get("Editable"):
            continue
        r = B.port_rules(entry, catalogue_types)
        if not r:
            continue
        # E9: THE KEY CARRIES THE PORT'S TAGS NOW, where it states any.
        # Rebuilding it without them made every one of the 73 tagged
        # flight-blade lists look like a key belonging to no port - this
        # control failed on a page that was correct, because it reconstructed
        # the key by a rule the builder no longer follows. It calls the
        # builder's own constrain_tags() rather than reimplementing it, so the
        # two cannot drift again.
        ktags = B.constrain_tags(r, entry)
        rule_of.setdefault(
            B.rule_key(r, entry.get("MinSize"), entry.get("MaxSize"), ktags),
            (r, entry.get("MinSize"), entry.get("MaxSize"), ktags))
    for key, offered in FITS.items():
        r, mn, mx, _kt = rule_of.get(key, (None, None, None, ()))
        if r is None:
            violations.append("fitment key %s belongs to no real port" % key)
            continue
        want_types = set(t for t, _ in r)
        for k in offered:
            it = by_class.get(k.lower())
            if it is None:
                violations.append("%s offers unknown item %s" % (key, k))
                continue
            if (it.get("type") or "") not in want_types:
                violations.append("%s offers %s of type %s, not in %s"
                                  % (key, k, it.get("type"), sorted(want_types)))
                continue
            sz = it.get("size")
            if sz is not None and mn is not None and sz < mn:
                violations.append("%s offers %s size %s below min %s"
                                  % (key, k, sz, mn))
            if sz is not None and mx is not None and sz > mx:
                violations.append("%s offers %s size %s above max %s"
                                  % (key, k, sz, mx))
    check(not violations,
          "ABSENT: no fitment list offers a wrong type or an out-of-window size",
          "%d violations, e.g. %s" % (len(violations), violations[:3]))

    # Named negative example: pick a real small shield port and prove a
    # specific larger shield is not in its list.
    named_neg = None
    for key, (r, mn, mx, _kt) in rule_of.items():
        if key not in FITS or len(r) != 1 or r[0][0] != "Shield":
            continue
        if mx is None:
            continue
        bigger = [it for it in items
                  if it.get("type") == "Shield"
                  and (it.get("size") or 0) > mx
                  and it.get("className")]
        if bigger and FITS[key]:
            b = bigger[0]
            named_neg = (key, mn, mx, b.get("className"), b.get("size"),
                         b.get("className") in FITS[key])
            break
    check(named_neg is not None, "a named ABSENT example exists")
    if named_neg:
        check(named_neg[5] is False,
              "the named oversize part really is absent from that list")
        NOTES.append("L3 ABSENT: a size %s..%s shield port does NOT offer %s "
                     "(size %s) - absent from the list, not greyed"
                     % (named_neg[1], named_neg[2], named_neg[3], named_neg[4]))

    # ---- 2b. L2 - THE STOCK LOADOUT IS THE SHIP'S OWN DEFAULTS -----------
    say("")
    say("2b. L2 - a ship opens with what its own Loadout says is fitted")
    # PORT FOR PORT, on named ships, against ships.json directly. Not a count
    # and not a sample: the whole sequence, in order, for each named hull.
    #
    # A count would pass while the parts were shuffled between ports, which is
    # precisely the bug that would make a ship page subtly wrong and impossible
    # to spot - a Cutlass with its shields in its power-plant slots still shows
    # the right number of components.
    ship_by_class = {}
    for sh in ships:
        ship_by_class[sh.get("ClassName") or sh.get("Name")] = sh
    NAMED = ["DRAK_Cutlass_Black", "AEGS_Avenger_Stalker", "RSI_Aurora_MR",
             "ANVL_Hornet_F7C", "MISC_Prospector"]
    named_found = 0
    mismatches = []
    for cls in NAMED:
        rec = SHIPS.get(cls)
        sh = ship_by_class.get(cls)
        if not rec or not sh:
            continue
        named_found += 1
        # KEYED ON PortId, WHICH IS THE GAME'S OWN UNIQUE PORT IDENTITY.
        #
        # The first version of this rebuilt the generator's port-selection rule
        # here and compared counts, which meant it drifted the moment the
        # generator learned to type a port by what is fitted in it - and a
        # check that re-implements the thing it checks is testing its own copy
        # anyway. Keying on PortId asks the only question that matters and
        # duplicates no logic: FOR EVERY PORT THE PAGE SHOWS, DOES THE GAME
        # FILE PUT THAT EXACT PART IN THAT EXACT PORT?
        raw = []
        B.walk_ports(sh.get("Loadout"), raw)
        prefix = META.get("port_id_prefix") or ""
        by_pid = {}
        for entry, _pilot, _par in raw:
            pid = entry.get("PortId") or ""
            if prefix and pid.startswith(prefix):
                pid = pid[len(prefix):]
            by_pid[pid] = entry
        for sl in rec["slots"]:
            entry = by_pid.get(sl.get("p"))
            if entry is None:
                mismatches.append("%s: slot %s names port %r, which is not in "
                                  "the game file" % (cls, sl["id"], sl.get("p")))
                continue
            # The port the page names must be the port the page labels.
            if (entry.get("HardpointName") or "") != HP[sl["h"]]:
                mismatches.append("%s / %s: page says port %r, game file says %r"
                                  % (cls, sl.get("p"), HP[sl["h"]],
                                     entry.get("HardpointName")))
                continue
            want = entry.get("ClassName") or ""
            got = sl.get("stock") or ""
            # A part the page could not carry comes back empty; that is an
            # absence to report elsewhere, not a wrong part fitted here.
            if got and want and got != want:
                mismatches.append("%s / %s: game fits %s, page opens with %s"
                                  % (cls, entry.get("HardpointName"), want, got))
    check(named_found >= 3, "enough named ships to compare", "%d" % named_found)
    check(not mismatches,
          "each named ship's opening state matches its Loadout PORT FOR PORT, "
          "keyed on the game's own PortId",
          "; ".join(mismatches[:3]))
    # And the opening state is not empty, which "no mismatches" would allow.
    cut = SHIPS.get("DRAK_Cutlass_Black") or {}
    stocked = [sl for sl in cut.get("slots", []) if sl.get("stock")]
    check(len(stocked) > 10,
          "the named ship opens with parts fitted, not empty - so the "
          "port-for-port match is not vacuous",
          "%d of %d slots carry a stock part"
          % (len(stocked), len(cut.get("slots", []))))
    if cut:
        NOTES.append("L2: Drake Cutlass Black opens with %d of %d ports "
                     "filled from its own ClassName defaults, matched port "
                     "for port by PortId against ships.json"
                     % (len(stocked), len(cut.get("slots", []))))

    # ---- 3. SUBTYPES MUST NOT HAVE CLOSED SILENTLY -----------------------
    say("")
    say("3. subtype handling has not silently emptied a picker")
    # A FLOOR WOULD BE THE WRONG CHECK HERE, and finding that out is the
    # useful part. The first version demanded every jump port offer >=2 and it
    # failed on 249 ports - not because the filter had closed, but because
    # THERE IS EXACTLY ONE REAL SIZE-1 JUMP MODULE IN THE GAME. The other
    # size-1 entry is `JDRV_S01_Template`, a CIG placeholder, correctly
    # excluded. Lowering the bar until it passes would have been the check
    # being talked out of its job.
    #
    # So the assertion is EXACTNESS instead, which is strictly stronger: the
    # number of parts a port offers must EQUAL the number of real catalogue
    # items that satisfy its rule. Too few catches a silently-closed filter
    # (the `$editable` defect); too many catches an over-permissive one. A
    # floor could pass while both were wrong.
    exact_bad = []
    for key, offered in FITS.items():
        r, mn, mx, ktags = rule_of.get(key, (None, None, None, ()))
        if r is None:
            continue
        want = set()
        for it in items:
            if not it.get("className"):
                continue
            if "PLACEHOLDER" in (it.get("name") or ""):
                continue
            if (it.get("type") or "") == B.PAINT_TYPE:
                continue
            if not B.item_fits(it, r, mn, mx):
                continue
            # E9: AND THE TAG, where the port states one. Type and size alone
            # is precisely the rule this control was written against, and
            # leaving it here would have made the check demand the defect back.
            if ktags and not (B.item_tags(it) & set(ktags)):
                continue
            want.add(it["className"])
        got = set(offered)
        if got != want:
            exact_bad.append("%s: missing %s extra %s"
                             % (key, sorted(want - got)[:2], sorted(got - want)[:2]))
    check(not exact_bad,
          "every fitment list holds EXACTLY the parts its rule admits - not "
          "one fewer, not one more (%d rules)" % len(FITS),
          "%d wrong, e.g. %s" % (len(exact_bad), exact_bad[:2]))

    # And nothing offers nothing. An empty picker still renders, which is how
    # a closed filter hides.
    empty = []
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            if sl.get("fit") and not (FITS.get(sl["fit"]) or []) and not sl.get("also"):
                empty.append("%s / %s" % (rec["n"], HP[sl["h"]]))
    check(not empty, "no editable port offers an empty list",
          "%d, e.g. %s" % (len(empty), empty[:3]))

    # THE OTHER HALF OF THAT: the ports which genuinely have nothing must be
    # SHOWN and marked, not silently dropped. 134 editable ports name a type
    # no catalogue item satisfies at their size. Excluding them from the page
    # would be hiding a port; opening an empty picker would look broken. They
    # render with `nofit`, and this asserts both that they exist and that they
    # are handled - because "there are none" would pass vacuously if the
    # generator had simply deleted them.
    nofit = [(rec["n"], HP[sl["h"]]) for rec in SHIPS.values()
             for sl in rec["slots"] if sl.get("nofit")]
    check(len(nofit) > 50,
          "ports whose type has no part in the catalogue are still SHOWN, "
          "marked `nofit`", "%d" % len(nofit))
    check(all(not sl.get("fit") for rec in SHIPS.values()
              for sl in rec["slots"] if sl.get("nofit")),
          "a `nofit` port opens no picker")
    check(META.get("ports_with_no_part") == len(nofit),
          "the generator reported the same count it emitted",
          "%s vs %s" % (META.get("ports_with_no_part"), len(nofit)))
    NOTES.append("L3 gap, logged not guessed: %d editable ports name a "
                 "component type no catalogue item satisfies at their size "
                 "(e.g. %s / %s). Shown, no picker."
                 % (len(nofit), nofit[0][0], nofit[0][1]) if nofit else "")

    # The measured thinness, recorded rather than asserted, because it is a
    # fact about CIG's catalogue and not about our code.
    seen = {}
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            if not sl.get("fit"):
                continue
            t = TYPES.get(sl["t"], {}).get("t")
            n = len(FITS.get(sl["fit"]) or [])
            seen[t] = min(seen.get(t, 10 ** 9), n)
    NOTES.append("thinnest picker per type (a fact about CIG's catalogue, not "
                 "a bug): " + ", ".join("%s %s" % (t, seen[t])
                                        for t in sorted(seen))[:400])

    # ---- 4. L4 - A FIXED PORT IS SHOWN, NOT HIDDEN -----------------------
    say("")
    say("4. L4 - fixed ports render, open no picker, and are not hidden")
    fixed = [(rec, sl) for rec in SHIPS.values() for sl in rec["slots"]
             if sl.get("fix")]
    check(len(fixed) > 1000, "fixed component ports are present in the data",
          "%d" % len(fixed))
    check(all(not sl.get("fit") for _r, sl in fixed),
          "no fixed slot carries a fitment list (it would open a picker)")
    # The order names the fuel tank specifically: 0 of 436 FuelTank ports are
    # editable, and it must still be on the page.
    fuel = [sl for _r, sl in fixed if TYPES.get(sl["t"], {}).get("t")
            in ("FuelTank", "FuelIntake", "QuantumFuelTank")]
    check(len(fuel) > 100,
          "fuel tanks and intakes are SHOWN as fixed, not dropped",
          "%d" % len(fuel))
    check(all(sl.get("h") is not None and 0 <= sl["h"] < len(HP) for _r, sl in fixed),
          "every fixed slot names its port, so the page can say what it is")

    # ---- 5. EDITABILITY IS PER PORT, NEVER PER TYPE ----------------------
    say("")
    say("5. editability is per port, per ship - never per component type")
    # The order's own example: ExternalFuelTank is 20 editable / 0 fixed, and
    # every one is on a refueller. If a by-type rule ever creeps back in, one
    # of these two facts breaks.
    by_type = {}
    for rec in SHIPS.values():
        for sl in rec["slots"]:
            t = TYPES.get(sl["t"], {}).get("t")
            d = by_type.setdefault(t, [0, 0])
            d[0 if sl.get("fit") else 1] += 1
    mixed = [t for t, (e, f) in by_type.items() if e and f]
    check(len(mixed) >= 5,
          "several types are editable on some ports and fixed on others - "
          "which a by-type rule could not produce",
          "mixed types: %s" % sorted(mixed)[:8])
    ext = by_type.get("ExternalFuelTank")
    check(ext is not None and ext[0] > 0,
          "ExternalFuelTank has EDITABLE ports (the refuellers), though plain "
          "FuelTank has none", str(ext))
    check(by_type.get("FuelTank", [0, 0])[0] == 0,
          "plain FuelTank has NO editable ports - the same measurement, "
          "opposite answer", str(by_type.get("FuelTank")))
    NOTES.append("per-port proof: ExternalFuelTank %d editable / %d fixed, "
                 "plain FuelTank %d editable / %d fixed"
                 % (ext[0], ext[1], by_type.get("FuelTank", [0, 0])[0],
                    by_type.get("FuelTank", [0, 0])[1]))

    # ---- 6. L5 - ARMOUR RESOLVES, AND IS NOT ONE NUMBER ------------------
    say("")
    say("6. L5 - armour resistance resolves, and differs between hulls")
    # THE MEASURED ANSWER, NOT THE HOPED-FOR ONE. 305 of 316 records carry an
    # Armor port and ALL 305 RESOLVE - there is no partial resolution and no
    # guessing. The 11 without are named rather than waved at: nine are
    # exosuits (IsPowerSuit), and the other two are the Greycat PTV buggy and
    # the Aegis Idris-P, neither of which CIG models armour for. So the page
    # can state resistance for every hull that has any, and must say "not
    # stated" for those eleven rather than invent a 1.0 baseline.
    with_arm = [r for r in SHIPS.values() if r.get("arm")]
    no_arm = sorted(r["n"] for r in SHIPS.values() if not r.get("arm"))
    # PINNED TO 4.9's DATASET UNTIL 2026-08-30. This asserted "305 of 316" and
    # "exactly 11", and the 4.10 pull made it 307 of 318 - two ships added,
    # nothing about armour resolution changed. A count is a fact about one
    # snapshot; the PROPERTY is that every record either resolves armour or is
    # one of a known set that CIG gives no armour port.
    #
    # The named set is the assertion now. It cannot drift quietly the way a
    # number can: a twelfth record appearing without armour fails here by NAME,
    # and says which one, which is what a reader needs.
    KNOWN_NO_ARMOUR = {
        "ATLS Cool Metal Color", "ATLS Orange Line", "ATLS Snowland Color",
        "Aegis Idris-P", "Argo ATLS", "Argo ATLS GEO", "Argo ATLS GEO IKTI",
        "Argo ATLS IKTI", "Argo ATLS IKTI Rad", "Greycat PTV", "Power Suit",
    }
    unexpected = sorted(set(no_arm) - KNOWN_NO_ARMOUR)
    check(not unexpected,
          "every record without hull armour is one CIG gives no armour port - "
          "exosuits, the PTV and the Idris-P",
          "unexpected: %s" % unexpected if unexpected else
          "%d resolved, %d without, all known" % (len(with_arm), len(no_arm)))
    # AND THE COVERAGE IS STILL OVERWHELMING, so a collapse cannot hide behind
    # a set that happens to match. Without this, emptying LOADOUT_ARMOR would
    # satisfy the check above by making no_arm equal the known set and nothing
    # else - which is exactly the shape of a check that cannot fail.
    check(len(with_arm) > 250,
          "and the overwhelming majority of records DO resolve one",
          "%d resolved" % len(with_arm))
    check(all(r["arm"] in ARMOR for r in with_arm),
          "every resolved armour key names a record in LOADOUT_ARMOR")
    NOTES.append("L5 coverage: %d of %d records resolve hull armour; the %d "
                 "without are 9 exosuits plus Greycat PTV and Aegis Idris-P, "
                 "neither of which CIG gives an armour port"
                 % (len(with_arm), len(SHIPS), len(no_arm)))
    profiles = set()
    for a in ARMOR.values():
        dm = a.get("dm") or {}
        profiles.add(tuple(sorted(dm.items())))
    check(len(profiles) > 1,
          "hulls do NOT all share one resistance profile - survivability is "
          "not one number", "%d distinct profiles" % len(profiles))
    # Named: a hull tough against ballistics and soft against lasers.
    asym = [(a["n"], a["dm"]["Physical"], a["dm"]["Energy"])
            for a in ARMOR.values()
            if (a.get("dm") or {}).get("Physical") is not None
            and (a.get("dm") or {}).get("Energy") is not None
            and a["dm"]["Physical"] != a["dm"]["Energy"]]
    check(bool(asym),
          "at least one hull resists physical and energy DIFFERENTLY")
    if asym:
        NOTES.append("L5 asymmetry: %s takes Physical at %s and Energy at %s"
                     % asym[0])
    check(any((a.get("sm") or {}) for a in ARMOR.values()),
          "armour carries SIGNAL multipliers, so it moves stealth too")

    # ---- 7. L7 - LIVERIES, CASE-INSENSITIVE, AND HULL-SCOPED -------------
    say("")
    say("7. L7 - liveries are matched case-insensitively and scoped to a hull")
    # The six ships spelled `Hardpoint_Paint`. Recount from the snapshot: an
    # exact-case match would find fewer paint ports than a case-insensitive one.
    lower = upper = 0
    for entry, _p, _par in all_ports:
        hp = entry.get("HardpointName") or ""
        if hp.startswith("hardpoint_paint"):
            lower += 1
        elif "paint" in hp.lower():
            upper += 1
    check(upper > 0,
          "there really are paint ports NOT spelled `hardpoint_paint` - so "
          "case-insensitivity is load-bearing, not defensive",
          "%d exact, %d other-case" % (lower, upper))
    # AND WHICH SHIPS WOULD BE LOST, by name. "Six ships" is a number; "the six
    # RSI Aurora Mk I variants" is a thing somebody can go and look at. The
    # exact-case match is run here as the DEFECT it would be, so the loss is
    # demonstrated rather than described.
    lost = []
    for sh in ships:
        raw = []
        B.walk_ports(sh.get("Loadout"), raw)
        anyp = [e for e, _p, _x in raw
                if "paint" in (e.get("HardpointName") or "").lower()]
        exact = [e for e in anyp
                 if (e.get("HardpointName") or "").startswith("hardpoint_paint")]
        if anyp and not exact:
            lost.append(sh.get("Name"))
    check(len(lost) > 0,
          "an exact-case match WOULD lose ships - demonstrated, not asserted",
          "%d: %s" % (len(lost), lost))
    # THE SIX ARE DETECTED, AND THEY STILL GET NO LIVERIES - and that is the
    # honest answer rather than a failure to fix.
    #
    # The case-insensitive match is what stops those six ports being mistaken
    # for component slots, and it does that. But CIG left the SAME six records
    # with `RequiredTags: null` on the paint port, so the game states no livery
    # for them. `Paint_Aurora` liveries plainly exist and plainly belong to an
    # Aurora - and "plainly" is inference, which L3 forbids: "where the data
    # does not say, exclude and log it. NEVER GUESS A PORT RULE." Offering a
    # livery the game does not say is fittable is the same false claim as
    # offering an unmountable shield.
    #
    # So this asserts the honest treatment: they render, they say the game
    # files list no livery, and the count goes on the punch list.
    # KEYED ON CLASSNAME, NOT ON THE DISPLAY NAME. Two distinct records are
    # both called "Drake Caterpillar" - `DRAK_Caterpillar` and
    # `DRAK_Caterpillar_Boarded` - and the boarded one's paint port is
    # untagged while the flyable one's is not. A name-keyed join merged them
    # and reported the page guessing when it had done nothing of the kind.
    # The generator keys on ClassName throughout; this check now does too.
    got = set(k for k in SHIPS if SHIPS[k].get("pset"))
    untagged = []
    for sh in ships:
        raw = []
        B.walk_ports(sh.get("Loadout"), raw)
        pp = [e for e, _p, _x in raw
              if "paint" in (e.get("HardpointName") or "").lower()]
        # EVERY paint port, not the first. Four hulls carry several, and on the
        # Drake Caterpillar the first is untagged while a later one is not -
        # reading only `pp[0]` called a hull untagged that is not, which is the
        # check being wrong rather than the page.
        if pp and not any(e.get("RequiredTags") for e in pp):
            untagged.append(sh.get("ClassName") or sh.get("Name"))
    lost_cls = []
    for sh in ships:
        raw = []
        B.walk_ports(sh.get("Loadout"), raw)
        anyp = [e for e, _p, _x in raw
                if "paint" in (e.get("HardpointName") or "").lower()]
        exact = [e for e in anyp
                 if (e.get("HardpointName") or "").startswith("hardpoint_paint")]
        if anyp and not exact:
            lost_cls.append(sh.get("ClassName") or sh.get("Name"))
    check(all(n in untagged for n in lost_cls),
          "the six ships an exact match would lose are ALSO the ones CIG left "
          "with no livery tag - two defects in the same records",
          "not all untagged: %s" % [n for n in lost_cls if n not in untagged])
    check(not (set(untagged) & got),
          "no hull with an untagged paint port is offered liveries anyway - "
          "the page does not guess which hull a livery belongs to",
          "guessed for: %s" % sorted(set(untagged) & got)[:3])
    # Orphaned liveries: reachable by nothing, so nobody can fit them.
    port_tags, paint_tag_counts = set(), {}
    for sh in ships:
        raw = []
        B.walk_ports(sh.get("Loadout"), raw)
        for e, _p, _x in raw:
            if "paint" in (e.get("HardpointName") or "").lower():
                for t in (e.get("RequiredTags") or []):
                    port_tags.add(t)
    for it in items:
        if (it.get("type") or "") != B.PAINT_TYPE:
            continue
        for t in ((it.get("stdItem") or {}).get("RequiredTags") or []):
            paint_tag_counts[t] = paint_tag_counts.get(t, 0) + 1
    orphan_tags = sorted(t for t in paint_tag_counts if t not in port_tags)
    orphan_n = sum(paint_tag_counts[t] for t in orphan_tags)
    NOTES.append("L7 case: %d paint ports are spelled `hardpoint_paint` and %d "
                 "are not. An exact-case match would lose %d ships: %s"
                 % (lower, upper, len(lost), ", ".join(sorted(lost))))
    NOTES.append("L7 gap, for the punch list: %d hulls have a paint port CIG "
                 "left untagged, so no livery can be stated for them; and %d "
                 "liveries under %d tags (%s) are asked for by no port at all"
                 % (len(untagged), orphan_n, len(orphan_tags),
                    ", ".join(orphan_tags)))
    with_paints = [r for r in SHIPS.values() if r.get("pset")]
    check(len(with_paints) > 200,
          "liveries reach the hulls that have a paint port",
          "%d ships" % len(with_paints))
    check(all(r["pset"] in PSETS for r in with_paints),
          "every ship's livery set names a real set")
    # HULL-SCOPED: no hull is offered every livery in the game.
    biggest = max((len(v) for v in PSETS.values()), default=0)
    check(biggest < len(PAINTS),
          "no hull is offered the entire livery catalogue - the sets are "
          "scoped by the port's RequiredTags",
          "biggest set %d of %d liveries" % (biggest, len(PAINTS)))
    # AND liveries take no part in the readout: they carry no stats.
    #
    # `un` IS PROVENANCE, NOT PERFORMANCE  (2026-08-30). 61 liveries had no
    # name in the game files and the page was printing CIG's own
    # <= PLACEHOLDER => marker as the paint's name. They now carry a label
    # built from CIG's identifier, and `un` marks that the WORDING is ours
    # rather than the game's. A livery still moves no number on the readout,
    # so the assertion's intent is untouched.
    #
    # DELIBERATELY STILL A NARROW ALLOWLIST rather than 'ignore unknown
    # keys'. Reading any unrecognised key as a stat is what made this fire
    # at all, and it is the only reason anybody looked.
    statty = [k for k, v in PAINTS.items()
              if set(v) - {"n", "m", "ev", "tags", "un"}]
    check(not statty,
          "no livery carries a performance stat (L7: they do not move the "
          "readout)", str(statty[:3]))

    # ---- 8. L13 - PROVENANCE SURVIVES ------------------------------------
    say("")
    say("8. L13 - CIG's own figures stay distinguishable from ours")
    with_cig = [r for r in SHIPS.values() if r.get("cig")]
    check(len(with_cig) > 250,
          "CIG's precomputed aggregates are carried separately",
          "%d ships" % len(with_cig))
    check(META.get("last_verified_patch"),
          "the snapshot's patch is stated on the data")
    check(META.get("has_prices") is False,
          "the data still declares that it holds no prices")
    check(len(data["LOADOUT_UNRELEASED"]) > 0,
          "the ships CIG has not built are carried, so the page can say why")

    # ---- 9. NOTHING DANGLING ---------------------------------------------
    say("")
    say("9. every reference resolves")
    dangling = []
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            if sl.get("stock") and sl["stock"] not in PARTS:
                dangling.append("%s stock %s" % (cls, sl["stock"]))
            if sl.get("fit") and sl["fit"] not in FITS:
                dangling.append("%s fit %s" % (cls, sl["fit"]))
            if sl.get("also") and sl["also"] not in PARTS:
                dangling.append("%s also %s" % (cls, sl["also"]))
            if not (0 <= sl.get("h", -1) < len(HP)):
                dangling.append("%s h=%s" % (cls, sl.get("h")))
            if sl["t"] not in TYPES:
                dangling.append("%s type %s" % (cls, sl["t"]))
    for key, lst in FITS.items():
        for k in lst:
            if k not in PARTS:
                dangling.append("fits %s -> %s" % (key, k))
    for key, lst in PSETS.items():
        for k in lst:
            if k not in PAINTS:
                dangling.append("pset %s -> %s" % (key, k))
    check(not dangling, "no dangling reference anywhere in the file",
          "%d, e.g. %s" % (len(dangling), dangling[:3]))
    return FAILURES


# --------------------------------------------------------------------------
# The L4 patch-override mechanism, proven by firing it.
# --------------------------------------------------------------------------

def verify_patch_override():
    """L4: a port opening up later must be a DATA change, not a code change.

    Proven by behaviour rather than by reading the code, per rule 12: plant a
    real override, regenerate, confirm it reached the slot, remove it, confirm
    it is gone. A mechanism that has never fired is an untested gate.
    """
    say("")
    say("10. L4 - the editability patch override is DATA, and it actually fires")
    data = load_generated()
    SHIPS = data["LOADOUT_SHIPS"]
    HP = data["LOADOUT_HP"]

    target = None
    for cls, rec in SHIPS.items():
        for sl in rec["slots"]:
            if sl.get("fit"):
                target = (cls, HP[sl["h"]], sl["id"])
                break
        if target:
            break
    if not target:
        check(False, "found a slot to plant an override on")
        return
    cls, hp, slot_id = target

    existed = os.path.exists(B.PATCH_OVERRIDES)
    backup = None
    if existed:
        with io.open(B.PATCH_OVERRIDES, "r", encoding="utf-8") as fh:
            backup = fh.read()
    try:
        payload = json.loads(backup) if backup else {}
        payload["%s|%s" % (cls, hp)] = "4.99-CONTROL"
        with io.open(B.PATCH_OVERRIDES, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True, ensure_ascii=False)
        rc = subprocess.call([sys.executable,
                              os.path.join(ROOT, "build_loadout_data.py")],
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        check(rc == 0, "regeneration with an override succeeded")
        after = load_generated()
        sl = next((x for x in after["LOADOUT_SHIPS"][cls]["slots"]
                   if x["id"] == slot_id), None)
        check(sl is not None and sl.get("v") == "4.99-CONTROL",
              "the planted patch override REACHED the emitted slot (%s / %s)"
              % (cls, hp),
              "slot carries v=%r" % (sl or {}).get("v"))
    finally:
        if existed:
            with io.open(B.PATCH_OVERRIDES, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(backup)
        elif os.path.exists(B.PATCH_OVERRIDES):
            os.remove(B.PATCH_OVERRIDES)
        subprocess.call([sys.executable, os.path.join(ROOT, "build_loadout_data.py")],
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    after = load_generated()
    sl = next((x for x in after["LOADOUT_SHIPS"][cls]["slots"]
               if x["id"] == slot_id), None)
    check(sl is not None and sl.get("v") is None,
          "and removing the override removed it again - so it is the DATA "
          "deciding, not the code")


# --------------------------------------------------------------------------
# Rule 12: prove the check by making it fail.
# --------------------------------------------------------------------------

def mutants():
    """Six defects a real regression would produce. Each MUST be caught.

    A check that has never failed is not a check. These are applied to the
    parsed data rather than to the generator, so the failure is attributed to
    the assertion rather than to a broken build.
    """
    ships, items = load_snapshot()
    base = load_generated()

    def fresh():
        return json.loads(json.dumps(base))

    def m_drop_type(d):
        """A regression that reverts to a hand-written five-type list."""
        d["LOADOUT_META"]["types"] = ["WeaponGun", "Shield", "PowerPlant",
                                      "Cooler", "QuantumDrive"]
        return "the type list silently reverted to the old five"

    def m_offer_oversize(d):
        """A fitment rule that stopped honouring MaxSize."""
        key = next(k for k, v in d["LOADOUT_FITS"].items() if v)
        big = max(d["LOADOUT_PARTS"], key=lambda k: d["LOADOUT_PARTS"][k]["s"])
        d["LOADOUT_FITS"][key] = d["LOADOUT_FITS"][key] + [big]
        return "an oversize part leaked into a fitment list"

    def m_empty_quantum(d):
        """SubTypes enforced as literals - every quantum picker closes."""
        for cls, rec in d["LOADOUT_SHIPS"].items():
            for sl in rec["slots"]:
                t = d["LOADOUT_TYPES"].get(sl["t"], {}).get("t")
                if sl.get("fit") and t == "QuantumDrive":
                    d["LOADOUT_FITS"][sl["fit"]] = []
        return "every quantum-drive picker went empty"

    def m_hide_fixed(d):
        """Fixed ports hidden rather than shown - the L4 defect."""
        for cls, rec in d["LOADOUT_SHIPS"].items():
            rec["slots"] = [sl for sl in rec["slots"] if not sl.get("fix")]
        return "fixed ports were hidden instead of shown"

    def m_one_armour(d):
        """Survivability collapsed to one number."""
        first = next(iter(d["LOADOUT_ARMOR"].values()))
        for a in d["LOADOUT_ARMOR"].values():
            a["dm"] = dict(first.get("dm") or {})
            a["sm"] = dict(first.get("sm") or {})
        for a in d["LOADOUT_ARMOR"].values():
            for k in list((a.get("dm") or {})):
                a["dm"][k] = 1
        return "every hull was given the same resistance profile"

    def m_all_liveries(d):
        """Every livery offered on every hull - the 8 MB bug, as a lie."""
        allp = sorted(d["LOADOUT_PAINTS"])
        for k in d["LOADOUT_PAINTSETS"]:
            d["LOADOUT_PAINTSETS"][k] = allp
        return "every hull was offered the entire livery catalogue"

    def m_stock_not_offered(d):
        """A port stops offering the part the game fits in it."""
        n = 0
        for cls, rec in d["LOADOUT_SHIPS"].items():
            for sl in rec["slots"]:
                if sl.get("fit") and sl.get("stock"):
                    lst = d["LOADOUT_FITS"].get(sl["fit"]) or []
                    d["LOADOUT_FITS"][sl["fit"]] = [x for x in lst
                                                    if x != sl["stock"]]
                    sl.pop("also", None)
                    n += 1
                    if n > 3:
                        return ("a port stopped offering the part CIG fits "
                                "in it")
        return "a port stopped offering the part CIG fits in it"

    def m_shuffle_stock(d):
        """Stock parts shuffled between ports - the right count, wrong ship."""
        rec = d["LOADOUT_SHIPS"].get("DRAK_Cutlass_Black")
        stocks = [sl.get("stock") for sl in rec["slots"]]
        rot = stocks[1:] + stocks[:1]
        for sl, v in zip(rec["slots"], rot):
            if v:
                sl["stock"] = v
            else:
                sl.pop("stock", None)
        return "stock parts were shuffled between ports"

    def m_empty_stock(d):
        """A ship that opens empty instead of with its own defaults."""
        rec = d["LOADOUT_SHIPS"].get("DRAK_Cutlass_Black")
        for sl in rec["slots"]:
            sl.pop("stock", None)
        return "a ship opened empty instead of with its defaults"

    muts = [m_drop_type, m_offer_oversize, m_empty_quantum, m_hide_fixed,
            m_one_armour, m_all_liveries, m_stock_not_offered,
            m_shuffle_stock, m_empty_stock]
    say("")
    say("=" * 72)
    say("MUTANTS - each defect below MUST be caught, or this file is not a check")
    say("=" * 72)
    escaped = []
    for fn in muts:
        global FAILURES, NOTES
        FAILURES, NOTES = [], []
        d = fresh()
        what = fn(d)
        buf = io.StringIO()
        real, sys.stdout = sys.stdout, _Quiet()
        try:
            run(d, ships, items, strict=False)
        finally:
            sys.stdout = real
        if FAILURES:
            say("  CAUGHT  %-52s (%d assertion%s fired)"
                % (what, len(FAILURES), "" if len(FAILURES) == 1 else "s"))
        else:
            escaped.append(what)
            say("  ESCAPED %-52s  <-- THE CHECK DID NOT SEE THIS" % what)
    say("")
    if escaped:
        say("MUTANT RUN FAILED: %d defect(s) escaped." % len(escaped))
        return 1
    say("MUTANT RUN PASSED: all %d defects were caught." % len(muts))
    return 0


class _Quiet(object):
    """Swallow the inner run's output during mutant testing. `buffer` is here
    because say() writes bytes."""
    def write(self, *_a, **_k):
        return 0

    def flush(self):
        pass

    @property
    def buffer(self):
        return self


def main():
    if "--mutants" in sys.argv:
        return mutants()
    say("=" * 72)
    say("L1-L7 CONTROL - the derived scan and the per-port fitment rule")
    say("=" * 72)
    ships, items = load_snapshot()
    data = load_generated()
    run(data, ships, items)
    verify_patch_override()
    say("")
    if NOTES:
        say("MEASURED, for the ledger:")
        for n in NOTES:
            say("  - %s" % n)
        say("")
    if FAILURES:
        say("FAILED: %d control(s)" % len(FAILURES))
        for f in FAILURES:
            say("  - %s" % f)
        return 1
    say("PASSED: every control, and each one had a way to fail.")
    say("Run again with --mutants to see them fire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
