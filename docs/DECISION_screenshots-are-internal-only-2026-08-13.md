# DECISION — collector screenshots are internal working material. They are never published, shared, or posted.

    decided by  Sleven, 2026-08-13, in session with C1. Standing decision.
    status      SETTLED. Do not re-litigate. This scopes §5/§6 of the collector
                  order and every future question about frame handling.
    filed       Late. This existed only in the claude.ai project, which Code
                  cannot read. Code flagged the gap; he was right. Repo is the
                  source of truth for anything Code must act on.

---

## The decision, in Sleven's words

> "We will not be posting any of the screenshots that we pull. Therefore,
> informational gathering purposes only. So the screenshots are to gather static
> information, like the screenshots of the actual commodity terminals and stuff
> like that. So we have a visual inspection of those. They are not for being
> posted or shared or anything like that."

## What this means concretely

**Screenshots are input, not output.** They exist so a human or a parser can read
a commodity board and extract the numbers. The numbers get published. The frame
does not.

- Frames are never posted to Citizen Compass.
- Frames are never shared publicly or with third parties.
- Frames are never included in any published dataset or export bundle intended
  for the site.
- What ships is the *extracted* data: prices, stock, shop names, item names.

## THE GOVERNING RULE — no name survives extraction

Added by Sleven the same day, and it is the stronger half of the decision:

> "If we do utilize information, the information we use will not have anybody's
> personal name involved."

**A frame may contain a name. Nothing derived from that frame ever may.**

This is the line that actually matters, because it holds regardless of what
happens to the frames. Reading a price off a screenshot is fine. Carrying the
handle that was standing next to that price into a row, a note, a filename, a
field, or a published table is not — no exceptions, no "we'll strip it later."

It applies to every path out of a frame: hand transcription, OCR, a parser
somebody writes in a year, a debugging dump, a support ticket. If the output of
reading a screenshot contains a person's name, the rule has been broken, and the
fact that the frame itself was never published does not cure it.

Practically: **anything extracted from a frame goes through the same allow-list
discipline as `mineTxnKeep` / `mineForbidden` in `gamelog_mine.go`** — name the
fields that may exist, drop everything else. That mechanism has 308 rows and zero
leaks behind it. Do not invent a second, weaker one for frame-derived data.

**Nothing derives data from frames today** — Code confirmed the collector is
explicitly scoped "NO OCR. No atlas. No vocabulary." So this is a constraint on
future work, recorded now while the reasoning is fresh rather than after somebody
has already written the parser.

## Why the no-publish decision was needed

`export.go` states plainly:

> `Screenshots are NOT scrubbed. A frame can show your handle`

In Star Citizen, player handles appear on screen constantly — chat, contacts,
party lists, names over other players — and `r_displayinfo`, which Sleven runs,
stamps location, shard and server onto every frame. **There is no reliable way to
scrub a screenshot**, and the alternatives (blanking fixed UI regions, manual
review) are respectively brittle and unscalable.

So rather than solve an unsolvable scrubbing problem, the frames simply never
become public. Cheaper than any technical mitigation, and it cannot silently fail
the way a scrubber can.

## Consent — approved, and it is a change to the promise

Sleven approved the disclaimer, 2026-08-13: *"Adding the disclaimer... yes, add
it. That way it's known."*

**Frames still leave other people's machines.** Not publishing is not the same as
not collecting. When the collector runs on a contributor's computer and uploads,
their screenshots — potentially containing their handle and the handles of
players around them — travel to the project's storage.

`collector-consent.txt` must therefore say, in ordinary words:

- screenshots of their game are uploaded
- a frame can contain their handle and the handles of players near them
- the frames are used internally to read prices and are **never published**
- nothing extracted from them will carry anybody's name

**Code is right that this is a change to the promise**, and that the consent
file's own rule requires re-asking anyone who agreed to the previous wording.
Follow that rule — it exists for exactly this case. Sleven's view is that nobody
reads disclaimers; that is probably true and it changes nothing. It is stated so
it is known, and so the project can say plainly what it does.

## Consequences for the collector order

- **§5 and §6 remain scoped to the SIDECARS.** The JSON is what becomes published
  data, so it must be provably clean. The frames are internal.
- **§6's export guard still refuses unscrubbed sidecars**, unchanged.
- **Build NO screenshot scrubbing.** If a future session proposes blanking chat
  regions or OCR-based handle removal, this decision is the answer: the frames
  are not published, so the mitigation is unnecessary.
- **Any future frame-reading feature inherits the governing rule** — the
  allow-list applies to whatever comes out of a picture, not just to log lines.
- Storage still matters — frames were 1 GB of 1.9 GB in one session — but that is
  a cost question, not a privacy one.

## §5c — the 364 existing sidecars: REWRITE IN PLACE

Still open at time of writing. The direction, decided with Sleven:

**Rewrite them in place**, stripping `location_candidates` and keeping every
other field. Not deleted — `export.go` refuses a PNG with no sidecar, so deleting
them bins 364 captures worth of provenance. Not left for the export guard to
refuse — that leaves the leak on disk forever and re-exposes it the day somebody
changes export.

**Scrubbing happens on the machine, BEFORE anything is sent.** Never on arrival.
Once a file carrying a name is in the bucket it has been collected, and "clean it
later" means a bucket full of other people's handles waiting on someone's
attention.

## Related

- `prompt-code-collector-log-first-redesign-2026-08-13.md` — the order
- `ERRATUM-collector-leak-and-location-parser-2026-08-13.md` — §5 correction
- Cloudflare upload setup is deliberately AFTER the leak fix, per Sleven.
