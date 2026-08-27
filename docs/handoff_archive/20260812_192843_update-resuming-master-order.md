# Update — resuming the MASTER order; state re-verified against the tree, and §4's search guard is already built

Picking the master order back up (`docs/prompt-code-MASTER-keybinds-and-the-rest-2026-08-12.md`).
Receipt per rule 13, with a correction to its §0 state table.

## §0 re-checked against the tree just now, not taken on trust

```
swap-is-a-cycle .......... NOT fixed   device_engine.js:687 `(slotOf(p)%8)+1`  CONFIRMED
rafId five writers ....... NOT fixed   4 in device_engine.js + tab handler in each host  CONFIRMED
holo depth pre-pass ...... DONE 17:22
holo marker cm->m ........ DONE 17:22, 8/8 Sabre mounts measured
holo fleet dataset ....... NOT built
fonts in _deploy ......... testing/_deploy/fonts exists - contents not yet audited
#kbbq search guard ....... ALREADY BUILT  keybinds.src.html:2134
```

**The order says the `#kbbq` guard is "NOT built (0 hits)". It is built** —
`elQ.addEventListener('keydown', function(e){ e.stopPropagation(); })`, with the
reasoning written beside it, plus a `if(e.target === elQ) return;` in the capture
handler so a listening cell doesn't eat it either. Not redoing it; I will verify
it reaches `_deploy` rather than assume, since "present in source" and "present
in the served file" are the pair this project keeps finding apart.

## Order of work

§1 first, because §5b (one stick) and §2 defect 1 (the `js3_*` export) are the
same bug seen from two ends, and fixing the slot model fixes all three. Then §2
export, §3 `rafId`, then the §4/§5 remainder.

Not touching `sc_export.js`'s `verified: false` — still C1's call, still open
from the 18:07 update.
