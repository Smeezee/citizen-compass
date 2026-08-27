# Update — Phase C complete, and the thruster/armour/fuel-tank question has numbers

C1–C6 DONE and committed. Five auditors in `checks/shop_checks.py`, flag-only,
wired into `run_checks.py --group db` and verified against the real findings
store — 185 findings written, 11 checkers ok, 0 errored. Continuing to Phase D.

## The three answers, measured (§3.3)

**Fuel tanks — YES, comprehensively.** `Utility / External Fuel Tanks`: 8 items,
8 priced, **100% coverage**. Not a gap at all.

**Armour — YES.** 2,366 armour items, 710 priced — roughly 30% across
Arms / Helmets / Legs / Torso, 17% on Backpacks. One hole: `Armor / Full Set` is
109 items with **zero** priced. Sets look like a UEX grouping rather than
something a shop sells as one unit.

**Thrusters — the question cannot be answered from this source, and that is the
honest result rather than a "no".** UEX has **no thruster category** among its
100, and **not one** of the 7,932 items has "thruster" anywhere in its name. The
nearest thing in the entire taxonomy is `Propulsion / Jump Modules` (3 items, all
priced). So this is not "thrusters aren't sold" — it is "UEX does not model
thrusters as a purchasable item at all". Answering the original question needs a
different source, not a different query.

Overall: **2,945 of 7,932 items carry at least one price (37.1%).** 10 categories
at 100%, 37 partial, 9 with items but no prices, 44 with no items at all. Full
table in the ledger.

## Name collisions — not the problem the order expected

| population | collisions | worst case |
|---|---|---|
| item names, within items | **7** of 7,721 | 2 |
| commodity names | 0 of 204 | — |
| terminal names | 20 of 803 | 2 |
| **uuids shared by >1 item** | **120** | **10** |
| items with no uuid at all | **2,162** of 7,932 | — |

The order expected "one display name spans up to 12 records". It is 2. **The
uuid is the problem, by an order of magnitude** — the A4 finding arriving again
from a different direction.

A separate 193 names exist as *both* an item and a commodity ("Agricium" is
both). Reported separately as a LIMITATION rather than pooled in: that is UEX
describing one real thing through two endpoints, which is a completely different
situation from two distinct guns sharing a name. Pooling reported 200 collisions
and buried the 7 that matter.

## C6 found a real defect, which is the point of C6

The outlier detector's **first** version flagged 590 of 26,657 rows. Reading them
showed it was asking the wrong question — an expensive magazine in a cheap
category is not an anomaly, it is Star Citizen. Game prices are multiplicative,
so the fence now sits in log space: 205 rows, 0.77%. The linear figure stays in
the code as the evidence for the change.

Then the negative control **failed on C3** — it reported only "worst case 2 share
X", so a new collision was invisible unless it became the worst, and the reader
got a number they could not act on. **The auditor was fixed; the control was not
weakened to match it.**

C2's hard-orphan branch is unreachable while its foreign key exists, so the
control drops the key inside a transaction, watches the branch fire, rolls back,
then confirms from `pg_constraint` that all three keys are back. An unobservable
branch is not a check.

## One thing worth your decision

`Commodities / Commodities` (category 36) holds **158 items with zero prices**,
while the separate commodity import has **147 of 204 priced at 72%**. Those are
two different UEX representations of the same thing and only one carries prices.
Both are stored, neither is guessed at — but the site should probably show one
of them, and which is your call.
