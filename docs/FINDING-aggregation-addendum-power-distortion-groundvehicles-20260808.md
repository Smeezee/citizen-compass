# FINDING ADDENDUM — the ground-vehicle case, Distortion, and why Power is not a sum

    from      Claude Code, 2026-08-08
    for       C1
    extends   FINDING-aggregation-rules-shields-solved-20260808.md
    covers    the four items that finding's §7 listed as NOT checked

Same corpus, same join, read-only: `scunpacked-data/snapshots/20260801T204744Z/`.

---

# 1. The Tumbril Nova exception — evidence, and why it is still n=1

The previous finding flagged the Nova as the sole exception to
`Hp = min(N,2) × unit_hp` and offered "it is a ground vehicle" as an untested
hypothesis. Tested now:

**23 ships have `IsSpaceship` falsey.** 22 of them satisfy the cap rule. The
Nova does not.

**But 22 of those 23 cannot discriminate.** They fit one or two generators, and
at N≤2 the cap rule and full summation are the same arithmetic. Listing the only
ships where the two rules can disagree:

| class | ships with N>2 | behaviour |
|---|---|---|
| spaceships | **56** (31 at N=3, 23 at N=4, 2 at N=6) | **all 56 capped at 2** |
| ground vehicles | **1** (Tumbril Nova, N=3) | **full sum** |

So the split is clean and it is real — every spaceship that *could* break the cap
does not, and the only ground vehicle that could, does. **But the ground-vehicle
side of it rests on exactly one ship.** One observation consistent with a
hypothesis is not the hypothesis confirmed, and this is the same trap the
original N-1 reading fell into: a rule inferred from a single vehicle whose
fitting happened to make two rules agree.

**Do not write "ground vehicles sum fully" into anything shippable.** The
defensible statement is: the cap holds for all 290 ships except the Nova, and the
Nova is the only non-spaceship in the corpus fitting more than two generators.

---

# 2. `Distortion.Pool` is NOT an item sum — and is not explained

Tested `Distortion.Pool = Σ (fitted item `stdItem.Distortion.Maximum`)`:

    exact: 14 of 315        miss: 301

The misses are not noise, they are enormous and structured:

| ship | summed from items | actual `Pool` | difference |
|---|---|---|---|
| Anvil Ballista | 9,040 | 1,023,040 | 1,014,000 |
| RSI Lynx | 9,040 | 1,013,040 | 1,004,000 |
| Greycat MDC | 8,900 | 1,010,900 | 1,002,000 |
| Anvil Centurion | 19,840 | 2,523,840 | 2,504,000 |

The item contribution is real and present in the total — the last three digits
track the summed value exactly — but it sits on top of a base of roughly one to
2.5 million that does not come from the fitted items. **The hull contributes the
overwhelming majority of the distortion pool and I did not find where that
number lives.**

Two things follow. First, `Distortion.Pool` **stays unshippable as a derived
value** — a rule explaining 14 of 315 is not a rule. Second, it is displayable
**as given** from `ships[].Distortion.Pool`, which is what the page spec already
said, and that remains correct.

---

# 3. Power generation is a partial rule with a systematic, diagnosable miss

Tested `Power.GenerationSegments = Σ (Generation/Power rates on fitted items)`:

    exact: 207 of 307       miss: 100

That is a real rule for two-thirds of the fleet, and the misses share a shape:
**the actual value is always LOWER than the sum**, at ratios clustering near
0.55.

The clean discriminating case is the **Drake Mule**:

    fitted: hardpoint_power_plant  Steadfast  rate 11
            hardpoint_batteries    Steadfast  rate 11     (same item, same UUID)
    summed  = 22
    actual  = 12

Neither the sum (22), nor one unit (11), nor a cap-at-two. **12.**

The important structural observation: **both entries are typed `PowerPlant`, but
one is fitted to a battery hardpoint.** A battery is a store, not a generator,
and the item table gives it the same type as the plant it shares a model with.
So the naive sum counts a battery as a second generator.

That explains the *direction* of every miss and the rough magnitude. It does not
explain 12 rather than 11, which is off by exactly one and which I did not
resolve. **Do not ship a power-generation figure on this.** The candidate worth
testing next is that hardpoint name — not item type — decides what generates,
plus a segment conversion that accounts for the off-by-one.

---

# 4. Emission group → item: not established, and the sample was degenerate

The intended test was whether each `EmGroupsShields` entry equals the sum of the
fitted items of that type. The item-side field is
`stdItem.Emission.Em.Maximum` (and a scalar `Ir`), which I did locate.

The test did not run meaningfully: the first ship carrying the group field is the
**ATLS Orange Line**, whose entire breakdown is `{"Radar": 900}` — a single
component. That distinguishes nothing.

**Reporting this as not done rather than as a result.** It needs a ship with a
rich breakdown, and I ran out of budget before doing it properly. It remains the
highest-value open step, because it is the one that would enable custom loadouts.

---

# 5. A second self-caught error, disclosed

The previous finding disclosed one bug of mine (counting `ShieldController`
entries as join failures). Here is the second, in the same class:

I filtered `ResourceNetwork.States` on `Name == "Default"`. The real state name
is **`Online`** (2,460 items). Only 7 items in the entire table have a `Default`
state. The first run reported **"no generation items" on 307 of 307 ships** — a
clean, total, entirely false negative that could easily have been written up as
"ResourceNetwork does not connect to the ship aggregates."

Both bugs had the same signature: **a filter that silently matched nothing, and
a result that looked like a finding about the data.** The general lesson for this
corpus is that a check reporting *zero* joins should be assumed broken until the
join is demonstrated on one hand-verified example.

---

# 6. Status of C1's six aggregates

| aggregate | status |
|---|---|
| **`ShieldsTotal.Hp`** | **SOLVED** — `min(N,2) × unit_hp`, 289/290, cross-validated on `RegenRaw` |
| **`ShieldsTotal.Regen`** | unshippable — power-state dependent |
| **`Power`** | **partial** — 207/307 by naive sum; miss cause identified (batteries typed as PowerPlant), rule not closed |
| **`Cooling`** | totals reproduce their own groups 316/316; group→item **not done** |
| **`Emission` EM** | totals reproduce their own groups 314/314; group→item **not done** (degenerate sample) |
| **`Emission` IR** | **no group breakdown exists in the file** — cannot decompose |
| **`Distortion.Pool`** | **not derivable** — 14/315; hull supplies ~99% from an unlocated source |
| **DPS** | **no ground truth exists** — nothing to score a rule against |

**One aggregate of the six is solved. One is partial with a named cause. Four are
not derivable from this corpus, three of them for structural reasons that more
analysis will not fix.**

That is a worse headline than "we found the rules", and it is the accurate one.
The single genuinely valuable next job is §4 — Emission/Cooling group→item on a
ship with a rich breakdown — because it is the only remaining path to custom
loadouts, and it is a bounded piece of work.
