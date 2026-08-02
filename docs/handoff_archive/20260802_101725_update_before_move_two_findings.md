# BEFORE THE MOVE — two things found after the final push

C1, 2026-08-02, after independently verifying the closing state.

**The push is good.** `HEAD == origin/main == 5cda5d1`, verified. Everything of value is committed. This note is about two things the closing report did not cover.

---

## 1. DO NOT COMMIT THE 50 "MODIFIED" FILES. They are line-ending churn.

The closing report says the working tree holds "only the four deliberately-excluded scratch files." It holds **56** — 51 modified and 5 untracked.

But `git diff --stat` reads **191,317 insertions and 191,317 deletions**. Identical counts across 51 files is the signature of every line being rewritten, not of content changing.

**Tested: 11 of 12 sampled files are byte-identical after stripping CR.** The twelfth is `LATEST_HANDOFF.md`, which the watcher regenerates continuously and is genuinely different.

So **50 of the 51 are pure CRLF/LF churn.** `core.autocrlf` is unset, so something rewrote them with a different default. The same class of defect as the one already fixed in `build_deploy.py` — a text-mode write taking the platform newline.

**Why it matters more than cosmetics:**

- `releases/latest.html` and `static/preview.html` are in that list. **Those are the live site.** Committing a whole-file rewrite of the live page for zero functional change is not something to do by accident.
- So are `data-layer/external-source-verification/*/SHA256SUMS.txt` and the manifests. **Files whose job is to record hashes have themselves been altered** — their contents are intact, but their own bytes are not what they were. Anything that hashes a manifest rather than reading it would report drift that is not there.

**Action: none, and that is deliberate.** They are uncommitted, HEAD matches origin, and the committed versions are correct. The working tree noise is harmless *as long as nobody commits it.*

**For whoever picks this up after the move:** do not `git add -A` on this repo until the line endings are settled. Establish what rewrote them, fix that, then restore the working tree from HEAD rather than committing the churn.

---

## 2. `docs/URGENT_wo_craft_01_b_description_rights_correction.md` — untracked, and it changes a plan

Written by C2 at 17:11, after the closing push. **Not committed.**

It retracts C2's own position that wiring in the 5,344 CIG-written item descriptions is "the highest-value item in the project." The reason: **nobody checked whether we are allowed to publish them.**

Its finding, as filed:

- The Star Citizen Wiki's claim that CIG "granted rights of reuse for their public Comm-Link art and text" cites **a legacy RSI forum comment whose URL is now dead** — the forums were deprecated for Spectrum. The page was last edited April 2023.
- **RSI ToS §XIII.D "Personal and Fansite Use"** permits reproducing *"images, graphics or artwork"* and *"trademarks and logos"* that RSI designates for fansite use. **Text is not in that list.**

**This affects work already done.** WO-1 built `item_descriptions.json` — 5,344 descriptions — and Ruling 1 folded them into item pages. That is committed.

**There is no live exposure.** Nothing deployed carries item descriptions; the Cloudflare build is the ship matrix plus keybinds, loadout and find. So this is a plan problem, not an incident.

**Action before the move: none.** Action after: **WO-1's output must not ship until this is settled**, and settling it is a question for Sleven and CIG, not for any session here. Rule 8 puts Fan Kit, trademark and legal text solely with him.

It should be committed rather than left untracked — a legal correction sitting outside version control is the one document that must not be lost. But that is a deliberate commit of one file, not a sweep.

---

## The state, verified independently

```
HEAD == origin/main   5cda5d1d9dd5fc2e49c6c698d9e113012664ad2d   (same hash twice)
RECOVERY.md, ship_resolution.json, the editions finding, all work orders   IN GIT
_deploy_lite/                                                             parked
Cloudflare offsite copy                                                   made current
```

**Nothing is in flight. Nothing is half-finished. The machine can be powered down.**
