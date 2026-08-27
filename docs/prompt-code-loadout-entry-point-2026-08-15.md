# PROMPT FOR CODE — the loadout bench is deployed and unreachable. Wire the entry point and delete the reason it was never wired.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD, but QUEUED BEHIND the collector work. Do not start this
              until the feed is published, 0.3.1 is cut, and a blank-settings
              machine has sent. That order finishes first.

---

## 0. What Sleven reported, and why he was right

> "I also noticed that the test site did not get updated at all yesterday no
> matter how many things you told me it did get updated."

**Both halves of this are true and that is the whole finding.**

The deploy happened. Fetched off the live testing URL today:

```
/loadout_data.gen.js   -> real, 316 ships, header names snapshot 20260801T204744Z
/loadout.html          -> the real Loadout Bench, no mock banner
```

**And there is no way to reach either one from the site.** No tab, no link, no
button. A person opening the testing site sees exactly what they saw the day
before, because for them nothing changed. **A page nobody can navigate to is not
shipped.** C1 reported it as shipped on the strength of the deploy, which is the
same mistake as reporting the collector fixed because the source was fixed.

## 1. The reason it was never wired is now stale, and the file says so itself

`testing/_deploy/index.html` carries this, verbatim:

```
That entry point is deliberately NOT wired yet - loadout.html
currently knows one ship, so 315 of 316 links would dead-end.
```

**`loadout.html` no longer knows one ship. It knows 316.** The condition that
comment names as the blocker is satisfied. The comment is a note from the past
being read as a decision about today.

**The 2026-08-02 removal of the floating LOADOUT tab is NOT being reversed.**
Sleven's reasons stand and are recorded twice in that file: the right edge stacks
tabs at 44% + 0/150/290/430px, so a fourth started at 826px on a 900px window;
and a floating tab has no idea which ship you are looking at. **Do not put the
tab back.** His own stated replacement is what gets built:

> the loadout belongs on the ship page, reached from the ship, opening on that
> ship.

## 2. The mechanism already exists — this is smaller than it looks

`loadout.html` already reads a deep link:

```js
history.replaceState(null,"","#"+shipId+"|"+enc(A)+"|"+enc(B));
function readHash(){
  const h=decodeURIComponent(location.hash.slice(1)); if(!h)return false;
  const [sid,a,b]=h.split("|"); if(!SHIPS[sid])return false;
  ...
}
```

So `loadout.html#AEGS_Avenger_Titan` already opens the bench on that ship, and
**an id the data does not carry already returns false rather than breaking** —
the dead-end failure mode the comment feared is already handled in code.

**What is missing is one link from the ship view, carrying the ship's own id.**

## 3. What to build

- **A control on the ship detail view** that opens the bench on that ship. Label
  it in Sleven's language, not the codebase's — he calls this the loadout.
- **It passes the ship's real id**, the same key `LOADOUT_SHIPS` is keyed on.
  Never a display name. Ship identity in this project is resolved on ids for a
  reason (`data-layer/ship_resolution.json`); a name join here would reintroduce
  the exact class of failure that finding closed.
- **A ship with no bench data does not show a broken control.** Either the
  control is absent, or it is present and states why it cannot open. **It must
  not open the bench onto an empty ship** — that reads as the tool being broken
  rather than the data being absent.
- **Delete or correct both stale comment blocks** in `index.html` (offsets around
  1461205 and 1530585). Leave the *reasons* the floating tab was removed — those
  are Sleven's ruling and stay on record. Remove the "currently knows one ship"
  claim, which is now false and is the thing that would stop the next session
  from wiring this.

## 4. Rule 12 — the check that matters

**Not "the link works on the Avenger."** The check is: **every ship reachable in
the site's ship view either offers a working bench link or correctly offers
none** — enumerated, counted, and reported as two numbers that add up to the
total. A spot check on one ship is exactly how 315 dead ends would ship
unnoticed.

Report the pair: how many ships offer the bench, how many correctly do not, and
name a few of the second group so Sleven can sanity-check that the absences are
real absences.

## 5. And the deploy is not the acceptance

**Do not report this done on a successful deploy.** Fetch the deployed page back
over the real network and confirm the control is present in what the server
actually serves. This project has silently published to a second URL five times,
and today it reported a page shipped that no human could open. **Deploying and
shipping are different events and only one of them is worth telling Sleven
about.**

## 6. What NOT to do

- **Do not restore the floating LOADOUT tab.** Removed twice, on Sleven's call,
  for reasons recorded in the file.
- **Do not touch `loadout.html`'s hash handling.** It works.
- **Do not `git add -A`.**
- **Do not start this before the collector order is finished.**

## 7. Acceptance

1. From the ship view, one action opens the bench already loaded with that ship.
2. Every ship in the ship view is accounted for: bench offered, or correctly not
   offered. Counts reported, and they sum to the total.
3. A ship with no bench data never opens an empty bench.
4. The stale "knows one ship" comments are gone; the tab-removal reasons remain.
5. The control is present in the page as fetched back from the live testing URL,
   not merely in `_deploy/` on disk.
