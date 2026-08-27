"""M1 — editions inherit their base ship's model.

GENERATES data-layer/derived/model-inheritance/. Re-runnable every patch, which
is the point: a hand-delivered mapping is stale the moment CIG adds an edition.

WHY THIS EXISTS. 113 of the ships that have a loadout say "no 3D model
available". Most of them are not missing a model - they are an EDITION of a
ship whose model we already hold. Sleven ruled on this on 2026-08-14
(docs/DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md):
a shared hull is correct unless the ships differ in external shape. An edition
is paint and fitted parts. The ruling existed; the join was never built.

THE SUFFIX LIST IS ENUMERATED, NOT INFERRED. Every entry below is an exact,
end-anchored pattern on the ClassName, and each one means "same airframe,
different paint and/or fitted parts". NO FUZZY MATCHING - standing rule. A
ClassName that does not match one of these is NOT touched; it goes to the
residue file for a human.

AND THE RESIDUE IS THE IMPORTANT HALF. Several of those would be WRONG to
inherit automatically and that is exactly why they are excluded: the Idris-P
and Idris-M differ at the nose, the Sabre and the Sabre Firebird are different
airframes, the Hornet Mk I and Mk II are different shapes. A rule that caught
those would be a rule that guesses.
"""
import json, os, re, sys

DEPLOY = os.path.join("testing", "_deploy")
OUT = os.path.join("data-layer", "derived", "model-inheritance")

# (pattern, what the suffix means). Pattern is anchored at end of ClassName.
SUFFIXES = [
    (r"_BIS\d{4}",              "Best In Show edition"),
    (r"_Showdown",              "Ship Showdown edition"),
    (r"_Teach",                 "Teach's Special"),
    (r"_BTALA",                 "Alliance edition"),
    (r"_Collector_[A-Za-z0-9]+","Wikelo collector variant"),
    (r"_Exec_[A-Za-z]+",        "PYAM Exec edition"),
    (r"_CitizenCon\d+",         "CitizenCon edition"),
    (r"_Tier_\d",               "service tier"),
    (r"_TEMP[A-Za-z_]*",        "temporary CIG placeholder suffix"),
    (r"_Pirate",                "pirate paint variant"),
    (r"_Boarded",               "boarded-state variant"),
]

def _extract(path, const):
    src = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"const %s\s*=\s*(\{.*?\});" % const, src, re.S)
    if not m:
        sys.exit("could not find %s in %s" % (const, path))
    return json.loads(m.group(1))

def main():
    models = _extract(os.path.join(DEPLOY, "loadout_model.gen.js"), "LOADOUT_MODEL")
    src = open(os.path.join(DEPLOY, "loadout_data.gen.js"), encoding="utf-8",
               errors="replace").read()
    ships = json.loads(re.search(r"const LOADOUT_SHIPS\s*=\s*(\{.*?\});\s*\n",
                                 src, re.S).group(1))

    no_model = [k for k, v in ships.items() if v.get("slots") and k not in models]
    rows, residue = [], []
    for k in no_model:
        hit = None
        for pat, why in SUFFIXES:
            base = re.sub(pat + r"$", "", k)
            if base != k and base in ships and base in models:
                hit = (base, models[base], pat, why)
                break
        if hit:
            rows.append({"class_name": k, "display_name": ships[k].get("n"),
                         "inherits_from": hit[0], "model_file": hit[1],
                         "matched_suffix": hit[2], "suffix_means": hit[3]})
        else:
            residue.append({"class_name": k, "display_name": ships[k].get("n")})

    # ---- ASSERTIONS. Rule 12: each of these can actually fail. ----
    assert all(r["inherits_from"] != r["class_name"] for r in rows), \
        "a ship was mapped to itself"
    assert all(r["inherits_from"] in models for r in rows), \
        "a ship was mapped to a base that has no model"
    assert not (set(r["class_name"] for r in rows) & set(models)), \
        "a ship that already has a model was included"
    assert len(rows) + len(residue) == len(no_model), "rows lost between the two files"

    rows.sort(key=lambda r: r["class_name"])
    residue.sort(key=lambda r: r["class_name"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(os.path.join(OUT, "model_inheritance.json"), "w",
                         encoding="utf-8"), indent=1)
    json.dump(residue, open(os.path.join(OUT, "needs_human_review.json"), "w",
                            encoding="utf-8"), indent=1)
    json.dump({
        "generated_by": "build_model_inheritance.py",
        "ruling": "docs/DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md",
        "order": "docs/RULING_the-asgard-is-in-centimetres-2026-08-26.md (appendix, M1-M3)",
        "ships_with_a_loadout": sum(1 for v in ships.values() if v.get("slots")),
        "ships_with_a_model": len(models),
        "ships_saying_no_model": len(no_model),
        "inheritable_exact": len(rows),
        "distinct_base_hulls_used": len(set(r["inherits_from"] for r in rows)),
        "residue_needing_human_review": len(residue),
        "join": "exact ClassName suffix strip. No fuzzy matching, no name similarity.",
        "suffixes": [{"pattern": p, "means": w} for p, w in SUFFIXES],
        "not_claimed": ("This says the edition shares its base hull's external "
                        "shape. It does NOT claim the models are good, correctly "
                        "scaled, or that the residue has no model anywhere."),
    }, open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8"), indent=1)

    print("ships saying 'no model' : %d" % len(no_model))
    print("  inheritable, exact    : %d  (across %d base hulls)"
          % (len(rows), len(set(r["inherits_from"] for r in rows))))
    print("  needs a human         : %d" % len(residue))
    print("wrote %s" % OUT)

if __name__ == "__main__":
    main()
