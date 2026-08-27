# Update — C3: I overclaimed twice, corrected. And a judgement call on where it sits.

**2026-08-27 · Code** — committed the correction.

## The correction

I reported `textLength` as **VERIFIED**, and later as confirmed "exactly, a
second independent confirmation". **Both were circular and neither should have
been stated.**

I found the string region's start by computing `end - textLength`. Its span was
therefore 17,165,925 **by construction**. Measuring back from that start then
"confirmed" the number I had just used to derive it. That is arithmetic
returning its own input, not evidence.

**It was checkable and I did not check it.** The derived start lands **mid
string** - the first entry reads `TLAWPILOT1_CV_Taunt...`, a truncated
`PU_OUTLAWPILOT1_`, with a printable `U` before it. A real table boundary does
not cut a string in half. Measuring the surrounding run without assuming
`textLength` gives **3,318,370 bytes**, nowhere near 17,165,925.

I spent the day catching three wrong offsets by measurement and then published
a fourth error that measurement would not have caught, because the number came
from my own assumption. Re-reading the claim was the check I should have run
first.

## What actually survives

- 331,435,556 bytes; word 0 = 0, **version 8**, words 2-3 = 0, and 25 plausible
  counts at offset 16
- a large body of packed null-terminated identifiers around 44-61 MB, including
  record-name-shaped `<Type>.<Instance>` strings
- `EntityClassDefinition` recurs **29,185 times as a type prefix**, not as a
  duplicated identifier

## What does not

The meaning of `textLength`, the string section's boundaries, the table layout,
and the name-reference encoding. **The offset searches that returned zero were
run against a base now known to be wrong**, so they rule out less than I said.

## The one durable thing this produced

Judge a candidate table by how often its first field lands on a **string
start**, against a measured random baseline of **1.75%**. And pin a section
boundary by finding a **complete first string**, never by subtracting a header
field from a guessed end.

## A judgement call I am flagging rather than making silently

C3 is the last item in the standing queue and the new hardpoint-picker order is
queued behind it. **C3 is unbounded reverse engineering and I am past the point
of diminishing returns on it** - four milestones, two of them corrections of my
own work, and the schema is no closer.

The picker order is approved, specified, and has a concrete acceptance test
(Polaris at 29 mounts, Perseus at 37). **My judgement is that the picker is the
better use of the next block of work and that C3 should be parked with the
handoff above**, rather than blocking approved work indefinitely.

**I am not acting on that unilaterally** - the instruction was explicit that the
picker comes after the queue, not in front of it. Saying so and holding.
