# Update — M1 done. Five bars on the loadout page, zero explanation blocks left.

**C1, 2026-08-27 14:18 local.** `node --check` passes.

Sleven's ruling: *"I want whatever's next. It all has to be done."* **The
decision gates are gone from `NEXT.md`** — no item waits on him any more, and
going live is off the queue entirely until he raises it himself.

## What changed in `testing/_src/loadout.src.html`

The three `.trip` blocks named in the order's table are now bars. **There is no
`.trip` explanation block left on the page.**

    MATCHUP        not a rating - no gun here is "better"
    COUNTS ONLY    fuse ratings and failure behaviour are not in the game files
    NO PRICE JOIN  shop data is real, the link to these parts is not proven

**Each stamp carries the block's own warning, not a label.** That is the whole
test for whether a bar earns its collapse: a reader who never opens
`NO PRICE JOIN` still leaves knowing this page will not put a price beside a
part. A bar reading "More info" would have been a worse version of what was
there before.

With the provenance bar and the inline `why ›` over the 3D stage, that is
**five** on this page.

## What I want from you

Rebuild and re-run `_verify_disclosure.mjs`. **D2's subject set goes from 2 to
5**, so it is a materially stronger assertion than the one that went green an
hour ago — and if any of the three new stamps is hollow, D2 is the thing that
should say so, not me.

**D1 matters more on this pass.** I collapsed three blocks in one go. If any of
them warns rather than explains, D1 is the only thing standing between that and
a shipped page. I read each against the rule before touching it and I still
want the check's opinion rather than my own.

## Your queue moved

`NEXT.md` Q1 is now **the disclosure bar on the other three pages** — eleven
amber blocks, keybinds x5, index x4, find x2. The loadout page is the reference
implementation and it is done.

**Audit each one before touching it.** The download page's antivirus notice,
find's error and empty states, and the keybinds capture warnings are all NEVER.
A block collapsed that should not have been is a warning nobody reads.

Q2 is the roadmap watcher past R0. Q3 is the collector selftest — **~190 checks
that have never run once**, and the reason they could not is stale for you.
Q4 is labelling every check that cannot meet rule 16, which Sleven has adopted.

*C1*
