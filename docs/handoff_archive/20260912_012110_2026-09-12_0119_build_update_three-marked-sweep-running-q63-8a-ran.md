# Build update - three letters marked on Sleven's go, sweep running, Q63.8A lists 1 and 2 ran

**Code (Build), 2026-09-12. The clock read 01:18:48 CDT at the sweep start.**

## 1. THE THREE AUDIT-TO-DESIGN LETTERS ARE MARKED

**Authority:** Sleven replied "go" at about 01:16. That was his answer to my message asking for his word on exactly these three.

- **I am recording that I read "go" as the go**, so he can object. The originals are aside, so the edit is reversible.
- `CLOSED:` was added above each letter's "## ROUND 3 - CLOSED" header, by a direct edit. Each file grew by 9 bytes, and I checked every byte around the marker against the original.
- The originals are in `_to_delete/closed_marker_20260912_three/`.
- The script is `_needs_review/mark_three_closed_20260912.py`, run dry first.
- **The mail check, run alone at 01:18:30: PASS.**

## 2. THE SWEEP IS RUNNING ALONE

It started at 01:18:48 CDT. The log is `_needs_review/sweep_20260912_solo2.log`.

- **If it is green:** deploy T-008 and the Q58 +3, then verify on the served site.
- **If it is red:** stop and name why.

## 3. Q63.8A LISTS 1 AND 2 HAVE RUN, READ-ONLY

- The report is `claude/Q63-8A_career-against-the-official-role-2026-09-12.md`, and a memo went to Architecture.
- **The join is 225 of 253.** The two 253s are different populations.
- Results: **LIST 1 has 3, LIST 2 has 30, LIST 3 has 192.**
- **Waiting on:** someone to own a name mapping for the 28 that do not join.

## 4. PHASE TWO, ODIN: THE MISSING FIGURE IS FOUND ON DISK

`data-layer/derived/model-availability/scale_fix_report.json` records Fleetyards anvl-odin at **length 752.0, beam 222.0, height 213.0**. That is the figure the model was scaled to on 2026-08-27. The rest of phase two is next.

## 5. HELD UNTIL THE DEPLOY

These all change the payload, so nothing touches them while the sweep runs:

- RAPTOR's removal
- the zero-to-absent import fix in `build_loadout_data.py`
- the San'tok filename
- width and height on the cards (2a and 2b, which were ordered as sizing only)
