# Update: Job B PUSHED - six commits on origin/main

**2026-08-06.** Explicit go-ahead given by Sleven. Pushed `0570426..8017efc`.
`git rev-list --left-right --count origin/main...main` now returns `0 0`.

```
8017efc Ignore the wrangler account cache by pattern, not by path
253b647 File the 2026-08-05/06 session record
0964c09 Record the rulings, findings and work orders from the 2026-08-05/06 dig
e204fb9 Stop uex_corp.py blaming a missing token for a missing library
5fe63ba Build the starmap route tables, and keep the bulk shards out of git
099d35b Add citizen-collector to the Go workspace
```

Checked before pushing: nothing matching `wrangler`, `.env`, `password`,
`token`, `secret` or `.dump` appears in the diff across all six.

## The wrangler ignore is by PATTERN, not by path

Sleven's instruction: ignore the pattern, not the path. The rules carry no
leading or embedded slash, so git matches them at **any depth**:

```
.wrangler/
wrangler-account.json
```

The file is also ignored by its own name, so it is caught even if it lands
outside a `.wrangler/` directory.

**Proven by behaviour, not by reading the rule** (hard rule 12). Confirmed
ignored at four locations - repo root, `testing/_deploy/.wrangler/cache/`, and
two arbitrary nested paths - while an unrelated `.json` at the same depth was
confirmed **not** ignored, so the pattern catches the subject rather than
swallowing everything near it.

Anchoring to `testing/_deploy/` or the root would only have covered the two
places it has already appeared, which is exactly how the second occurrence got
through after the first was fixed.

## Test artifacts moved aside, not deleted

Proving the pattern required planting a `wrangler-account.json` inside
`testing/_deploy/.wrangler/cache/` - the exact artifact that leaked. It has been
**moved out of `_deploy`** to `_to_delete/ignoretest_20260806/`, along with the
nested test tree. `testing/_deploy/` is confirmed clean of any `.wrangler` or
`wrangler-account.json`. Nothing was deleted (hard rule 1).

**Next:** two follow-ups from Sleven, both explicitly lower priority than
anything he asks for next - the `_deploy` build guard, and recording the four
orphaned scratch databases by name.
