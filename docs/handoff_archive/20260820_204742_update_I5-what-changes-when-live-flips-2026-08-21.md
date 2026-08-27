# UPDATE — I5 DONE: what changes when live flips, measured

    from  Code, 2026-08-21
    item  I5
    sha   ebb3a07

**The finding that reframes the release:** `releases/latest.html` is
**byte-identical to the page serving live right now except for the version
string.** Two lines differ — the title and the header. The matrix, all 254
ships, the 233 RSI links, the text, the layout: identical.

"Three weeks behind" does not mean the page drifted. Everything since v0.3.9 is
added on top of an unchanged page, or is a new page beside it.

|  | live now | would ship |
|---|---|---|
| files / size | 1 file, 205 KB | 497 files, 350.8 MB |
| pages | `/` only | `/`, `/find`, `/keybinds`, `/loadout`, `/holo`, `/download`, `/stick-test` |
| 3D models | none | 235 |
| version | v0.3.9 | v0.4.0 |

Checked one by one: all six extra paths and `/models/Hammerhead.glb` return 404
on the live site today and 200 on testing.

**Nothing is removed.** No page, no feature, no data.

## THE ONE THING TO DECIDE BEFORE YOU APPROVE

**Ship names in the matrix stop linking straight to RSI.** They open an in-page
ship view instead, and the RSI link is offered inside that view. Anybody who has
been clicking through to RSI meets this on their first click.

That is a build decision, not a deploy decision — changeable before the flip,
and only changeable by a second release afterwards.

Also: this is the first time the public site would serve anything but a single
HTML page. 497 files against Cloudflare's 20,000 limit, largest file 5.22 MB
against its 25 MiB limit. Both comfortable, but it is a change in kind.

Full inventory: section 6 of `docs/RELEASING-THE-SITE.md`.

Next: I6, the 404 sweep of the deployed testing site.
