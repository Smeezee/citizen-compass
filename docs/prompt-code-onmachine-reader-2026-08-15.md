# PROMPT FOR CODE — plan D: read the price board on the contributor's machine, send numbers not pictures. The blocker is one glyph and it is measured.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD to build, after the Worker order.
    order   2 of 2. The other is prompt-code-worker-and-release-feed-2026-08-15.md.
    basis   I tested OCR against Sleven's real captures this session. Numbers
              below are measured on his frames, not estimated.

    THIS REVERSES A SCOPE DECISION. The collector is currently marked
    "NO OCR. No atlas. No vocabulary." in three file headers. That was a
    deliberate simplification and it is being deliberately undone, by Sleven,
    with a reason. Update those headers rather than leaving them contradicting
    the code.

---

## 0. Why this exists

Uploading pictures costs storage and carries handles. Reading them on the
machine and sending only numbers costs neither.

**What is on a single shop capture** — read off frame `20260808T210114Z_0134`:

```
Nomadic_Pagan          <- his handle, printed on the shop UI, every frame
Wallet: 1,957,836      <- his balance
```

**If the reading happens locally, none of that ever leaves the contributor's
computer.** That is the whole argument, and it is stronger than the storage one.

## 1. What I measured, so nobody re-derives it

**The frames are good.** `hotkey (manual)` captures show full shop pages —
Platinum Bay BUY tab, item names, prices, volumes, manufacturer, stats. 38 such
frames exist today.

**Isolating the text works, cleanly.** The price glyphs are blue-violet on dark
navy. This mask turns them into crisp black-on-white:

```python
r, g, b = <RGB channels>
mask = (b - r > 40) & (b > 120)
```

Luminance thresholding does NOT work — the text and its background are close in
brightness, and a simple cut erases the numbers. I tried it first; it wipes them.

**And then exactly one thing fails:**

| truth | tesseract reads |
|---|---|
| 11,000 | 11,0**88** |
| 11,150 | 11,1**58** |
| 6,930 | 6,93**8** |
| 108,000 | 1**88**,**868** |
| 396,000 | 1396,**888** |

**Every zero becomes an 8. Five samples, no exceptions.** Star Citizen's UI font
uses a **slashed zero**; the stock model has never seen that glyph and maps it to
8.

**Do not "fix" this by substituting 8 for 0.** Real 8s exist, and the failure is
silent — `11,088` is a plausible price. Wrong data that looks right is worse than
no data.

## 2. Build a digit reader for the game's own font

Not general OCR. **Ten classes, one fixed font, fixed width, perfect contrast
after the mask.** About the easiest recognition problem available.

- **Training data is already on disk.** 592 captures, 38 of them shop pages.
  Segment the masked glyphs and label them once.
- **Digits and the comma are the entire alphabet** for a price. Nothing else may
  be emitted from a price field.
- **A glyph the reader is not confident about is not a guess.** Emit no price and
  say why. A missing price is recoverable; a wrong one propagates into the site.

**Rule 12 applies hardest here.** The check that matters is a slashed zero
correctly read as 0 — because that is the exact thing that is currently broken,
and a test suite that passes without covering it proves nothing.

## 3. Item names are easier — use the catalogue, do not trust the reader

`ship-items.json` holds **5,384 real item names**. The reader does not need to be
right, only close:

- Read the name approximately, then **match against the known catalogue.**
- `Quikcoot` -> `QUIKCOOL` is a trivial fuzzy match against a fixed list.
- **A name that matches nothing is reported as unmatched, never invented.**

This is the same discipline as `ship_resolution.json`: anchor on the trusted set,
match outward, classify the residue.

## 4. The governing rule applies to everything this produces

From `docs/DECISION_screenshots-are-internal-only-2026-08-13.md`, Sleven's words:

> A frame may contain a name. Nothing derived from that frame ever may.

**This order is the first code that derives data from a frame, so it is the first
place that rule has teeth.** Output goes through an allow-list naming the fields
that may exist — item name, price, volume, shop, timestamp — and drops everything
else. Same shape as `mineTxnKeep` / `mineForbidden`, which has 308 rows and zero
leaks behind it.

**Do not write a second, weaker mechanism for frame data.** The decision doc
forbids it by name.

`Nomadic_Pagan` and the wallet balance sit on every shop frame. They must not
appear in the output, in a log line, in a filename, or in a debug dump.

## 5. Where it runs

On the contributor's machine, after capture, before upload. The picture stays
local; the numbers go up.

**Keep picture upload working** — plan B ships first and Sleven may want both
while the reader is being trusted. This is an addition, not a replacement, until
he says otherwise.

## 6. Acceptance

1. A slashed zero reads as `0`. Covered by a test that fails if the reader
   regresses to `8`.
2. All five prices in frame `20260808T210114Z_0134` read exactly:
   `11,000` · `396,000` · `11,150` · `6,930` · `108,000`.
3. A deliberately blurred or occluded price emits **nothing**, with a stated
   reason — not a guess.
4. `QUIKCOOL`, `RAMPART`, `RN-7S`, `SOLARFLARE`, `RUMFORD` resolve against the
   catalogue.
5. A name matching nothing is reported unmatched, not invented.
6. **No output field contains a handle, a wallet balance, or any raw text not on
   the allow-list.** Verified by grepping real output, not by reading the code.
7. The three "NO OCR" file headers are updated to describe what the program now
   does.

## 7. Report back

- Accuracy across all 38 shop frames, not just the one I tested.
- What the reader does when it is wrong, and how often it knows it is wrong.
  **A reader that fails loudly at 80% is worth more here than one that fails
  silently at 95%.**
- Whether the mask in §1 holds across every shop page or needs per-screen tuning.
