#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE PAGE SPELLS WORDS THE WAY THE GAME SPELLS THEM, AND EVERY SHORTHAND IT
SHOWS HAS A DEFINITION BEHIND IT.

RULE16: INDEPENDENT - the spelling this control judges by is read from CIG's own
localisation table, `labels.json`, in the snapshot the page itself is pinned to.
The pages under test do not contribute a single word to the standard they are
measured against, and no word list is written into this file.

    owner    C1
    rule 16  the truth this control judges by comes from CIG's own
             localisation table, `labels.json`, NOT from a list of words C1
             thinks are correct. If CIG changes how the game spells something,
             this control changes with it and nobody edits anything.
    rule 12  `--self-test` plants five defects and EXITS NON-ZERO when it
             catches them. A control whose test cannot fail is not a control.
    rule 15  encoding: every file is read as utf-8; `labels.json` is read as
             utf-8-sig because CIG ships it with a BOM.

WHY THIS EXISTS. Sleven, 2026-08-29: *"Fix the vocabulary towards more US based
English instead of British."* That was done by hand, in one pass, across five
page sources - and a hand pass protects nothing the day after it is made. Two
of the files it had to touch hold the SAME joystick code by copy, so the same
correction had to be typed twice. **The second copy is exactly where a hand
pass fails.**

AND IT IS NOT A STYLE PREFERENCE. Measured in the pinned snapshot's
`labels.json`, the game itself is decisively American:

    defense 404 / defence 3      center 444 / centre 12
    maneuver 166 / manoeuv 12    color  141 / colour 0

**So a page that says `Point Defence Cannon` is not writing in a different
dialect - it is naming a thing the game does not call that.** Sleven's rule
governs: *"The words we use need to match the ones that the players would see
in game."*

ONE PAIR IS DELIBERATELY NOT ENFORCED, AND IT IS THE INTERESTING ONE.
`grey`/`gray` does not resolve to American, and the reason is not sloppiness on
CIG's part - **the game uses both, in different departments.** Counted over the
strings a player reads as a LABEL rather than as lore:

    ship liveries      Grey  141   "Arrow Metallic Grey Livery"
    clothing items     Gray   14   "Cumulus Jacket Gray"

**This site is about ships, so the ship spelling wins.** `grey` was "corrected"
to `gray` on this page on 2026-08-30 and then put back, because Sleven's rule is
not "write American" - it is *"the words we use need to match the ones that the
players would see in game."* The two rules agree almost everywhere and this is
where they part. **The measurement decides, not the dialect.**

WHAT IT CANNOT SEE, SAID PLAINLY. It reads `testing/_src/*.src.html` - the
files that carry page copy - and nothing else. Strings that reach a reader from
`cc_viewer.js` or from generated data are outside it. It strips block comments
and HTML comments before judging, so a British spelling in a comment is not a
defect; the deploy strips those anyway. **It is a control over page copy, not
over the repository.**
"""

import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "testing", "_src")
SELF = "--self-test" in sys.argv

# ---------------------------------------------------------------- the pairs
# British form -> American form. Each is CONFIRMED against labels.json below;
# a pair the game does not decide is not enforced, and says so.
PAIRS = [
    ("colour","color"), ("behaviour","behavior"), ("centre","center"),
    ("metre","meter"), ("defence","defense"), ("licence","license"),
    ("catalogue","catalog"), ("analyse","analyze"), ("organise","organize"),
    ("recognise","recognize"), ("prioritise","prioritize"),
    ("armour","armor"), ("neighbour","neighbor"), ("favour","favor"),
    ("travelling","traveling"), ("labelled","labeled"),
    ("modelling","modeling"), ("grey","gray"), ("fibre","fiber"),
    ("litre","liter"), ("manoeuvre","maneuver"), ("programme","program"),
    ("sceptic","skeptic"), ("storey","story"), ("jewellery","jewelry"),
    ("mould","mold"), ("smoulder","smolder"), ("whilst","while"),
    ("amongst","among"),
]

def labels_path():
    """The snapshot the PAGE is pinned to, read out of the page's own data
       layer - not the newest one on disk. Reading the newest is how a control
       ends up judging today's page against tomorrow's game."""
    gen = os.path.join(SRC, "loadout_data.gen.js")
    with open(gen, encoding="utf-8") as f:
        head = f.read(20000)
    m = re.search(r'"snapshot":\s*"([^"]+)"', head)
    if not m:
        return None, None
    snap = m.group(1)
    p = os.path.join(ROOT, "data-layer", "external-sources", "scunpacked-data",
                     "snapshots", snap, "labels.json")
    return (p if os.path.exists(p) else None), snap

# ------------------------------------------------------- what counts as code
# A match inside an identifier, an attribute name, an element id or a settings
# key is NOT page copy. Each of these was a real occurrence in this repository
# on 2026-08-30, and each is named so the exclusion is auditable rather than a
# blanket "looks like code".
CODE_BEFORE = re.compile(r"[A-Za-z0-9_.\-]$")     # CC_COLOUR_NAMES, data-colour, _view.colour
CODE_AFTER  = re.compile(r"^[A-Za-z0-9_(]")       # setColour(, HAT_CENTRE
ATTR_VALUE  = re.compile(r"""(?:id|class|data-[\w-]+|name|for)\s*=\s*["']$""")
DOLLAR_ID   = re.compile(r"""\$\(\s*["']$""")     # $('armour')
# A BARE TOKEN WEDGED BETWEEN CODE PUNCTUATION IS A NAME, NOT A SENTENCE:
# `markerMesh(colour)`, `{color:colour,`. Both sides must match, which is what
# keeps it off real copy - "not returning to centre." ends with a period but
# does not START after a bracket.
IDENT_OPEN  = re.compile(r"[(\[{,:=]\s*$")
IDENT_CLOSE = re.compile(r"^\s*[)\]},;:=.]")

def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    out = []
    for line in s.split("\n"):
        out.append("" if line.strip().startswith("//") else line)
    return "\n".join(out)

def scan(text, british):
    """Lowercase-only, whole word. `Grey's Market` and `Greycat` are the game's
       own proper nouns and are not misspellings of anything."""
    rx = re.compile(r"\b" + british + r"\b")
    hits = []
    for m in rx.finditer(text):
        a, b = m.start(), m.end()
        before, after = text[max(0, a-24):a], text[b:b+2]
        if CODE_BEFORE.search(before[-1:]): continue
        if CODE_AFTER.search(after):        continue
        if ATTR_VALUE.search(before):       continue
        if DOLLAR_ID.search(before):        continue
        if IDENT_OPEN.search(before) and IDENT_CLOSE.search(text[b:b+3]): continue
        line = text.count("\n", 0, a) + 1
        hits.append((line, text[max(0,a-40):b+40].replace("\n"," ").strip()))
    return hits

# ----------------------------------------------------------- the glossary
GLOSS_RX = re.compile(r"window\.CC_GLOSSARY\s*=\s*\{(.*?)\n\};", re.S)
TERMS_RX = re.compile(r"GLOSS_ON_PARTS\s*=\s*\[(.*?)\]", re.S)

def glossary_entries(layer_text):
    m = GLOSS_RX.search(layer_text)
    if not m: return None
    body = m.group(1)
    out = {}
    for em in re.finditer(r'"([^"]+)"\s*:\s*\[(.*?)\]\s*,?\s*\n', body, re.S):
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', em.group(2))
        out[em.group(1)] = parts
    return out

# =========================================================== run
def main():
    fails, notes = [], []

    lp, snap = labels_path()
    if lp is None:
        print("UNPROVEN - the pinned snapshot's labels.json is not on disk; "
              "the game's own spelling could not be read. Nothing is asserted.")
        return 2
    labels = json.load(open(lp, encoding="utf-8-sig"))
    blob = "\n".join(str(v) for v in labels.values()).lower()

    enforced, undecided = [], []
    for b, a in PAIRS:
        nb = len(re.findall(r"\b"+b+r"\b", blob))
        na = len(re.findall(r"\b"+a+r"\b", blob))
        (enforced if na > nb else undecided).append((b, a, nb, na))
    notes.append("%d pair(s) the game decides for American, %d it does not decide"
                 % (len(enforced), len(undecided)))
    if undecided:
        notes.append("not enforced, the game does not settle them: "
                     + ", ".join("%s/%s %d-%d" % (b, a, nb, na)
                                 for b, a, nb, na in undecided))

    files = sorted(glob.glob(os.path.join(SRC, "*.src.html")))
    if not files: fails.append("no page sources found to check")

    planted = {}
    for path in files:
        raw = open(path, encoding="utf-8").read()
        if SELF and path.endswith("loadout.src.html"):
            raw = raw.replace("<h1 id=\"shipname\">Ship</h1>",
                              "<h1 id=\"shipname\">Ship</h1><p>the armour colour "
                              "is grey and we recognise it whilst travelling</p>", 1)
            planted[path] = 6
        text = strip_comments(raw)
        for b, a, nb, na in enforced:
            for line, ctx in scan(text, b):
                fails.append("%s:%d says %r where the game says %r (%d/%d) - %s"
                             % (os.path.basename(path), line, b, a, na, nb, ctx[:90]))

    # --- the glossary itself -------------------------------------------
    layer = os.path.join(SRC, "_layer.src.html")
    lt = open(layer, encoding="utf-8").read()
    if SELF:
        lt = lt.replace('"VLM":      ["Vehicle Loadout Manager"',
                        '"VLM":      ["Vehicle Loadout Manager (broken)"' , 1)
        lt = lt.replace('  "livery":   ["Livery",',
                        '  "ZZ_ONE":   ["only one part"],\n'
                        '  "ZZ_THREE": ["a", "b", "c"],\n'
                        '  "livery":   ["Livery",', 1)
    g = glossary_entries(lt)
    if g is None:
        fails.append("_layer.src.html: no CC_GLOSSARY table found at all")
        g = {}
    else:
        notes.append("%d glossary term(s)" % len(g))
    for k, v in sorted(g.items()):
        if len(v) != 2:
            fails.append("glossary %r has %d part(s); every term is exactly "
                         "[short name, plain-English meaning]" % (k, len(v)))

    # every term the ship page turns loose on part rows must HAVE a definition
    lo = open(os.path.join(SRC, "loadout.src.html"), encoding="utf-8").read()
    if SELF:
        lo = lo.replace('const GLOSS_ON_PARTS = ["DPS"',
                        'const GLOSS_ON_PARTS = ["NOSUCHTERM","DPS"', 1)
    tm = TERMS_RX.search(lo)
    if not tm:
        fails.append("loadout.src.html: GLOSS_ON_PARTS is gone; the ship page "
                     "decorates nothing and the tooltip is dead copy")
    else:
        terms = re.findall(r'"([^"]+)"', tm.group(1))
        notes.append("%d term(s) applied to part rows" % len(terms))
        for t in terms:
            if t not in g:
                fails.append("GLOSS_ON_PARTS names %r and CC_GLOSSARY does not "
                             "define it - the page would underline a word and "
                             "then show nothing" % t)

    # the definitions are page copy too, and obey the same spelling rule
    for k, v in sorted(g.items()):
        for part in v:
            for b, a, nb, na in enforced:
                if re.search(r"\b"+b+r"\b", part):
                    fails.append("glossary %r spells %r where the game says %r"
                                 % (k, b, a))

    # ------------------------------------------------------------- report
    print("US spelling: %d page source(s), snapshot %s" % (len(files), snap))
    for n in notes: print("   " + n)
    print()
    if SELF:
        print("SELF-TEST. Planted: five enforceable British spellings in the "
              "ship page - plus `grey`, which MUST NOT be caught, because the "
              "game spells ship liveries that way - a glossary term with one "
              "part, a term with three, and a GLOSS_ON_PARTS entry with no "
              "definition. Eight catches expected: five spellings, two malformed terms, one undefined.")
        if any("'grey'" in f for f in fails):
            print("SELF-TEST FAILED - it caught `grey`, which the game itself "
                  "uses for ship liveries. A control that enforces a dialect "
                  "over the game's own strings is worse than no control.")
            return 1
        if len(fails) != 8:
            print("SELF-TEST FAILED - expected 8 catches, got %d:" % len(fails))
            for f in fails: print("     " + f)
            return 1
        if fails:
            print("   caught %d - the control is decisive:" % len(fails))
            for f in fails[:12]: print("     " + f)
            print("\nEXIT 9 - the control caught what was planted. This is the "
                  "GOOD outcome and it is deliberately non-zero.")
            return 9
        print("SELF-TEST FAILED - the planted defects were not caught.")
        return 1

    if fails:
        print("FAIL - %d defect(s):" % len(fails))
        for f in fails: print("   " + f)
        return 1
    print("PASS - the pages spell words the way the game spells them, and every "
          "shorthand shown on a part row has a definition behind it.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
