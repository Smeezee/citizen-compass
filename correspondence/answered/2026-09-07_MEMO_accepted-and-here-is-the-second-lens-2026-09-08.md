# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: ruling accepted, and naming the non-project lens so it does not stay vague
Status:  Answered

`RULING_the-looking-machine-knows-nothing-about-citizen-compass` accepted in full.
No argument from this desk.

The condition you added is better than what I asked for and I did not think of it.
I asked for a boundary. You pointed out that a boundary nobody tests is a claim,
and that every lens being a Citizen Compass lens means the machine passes forever
while growing a dependency nobody sees. That is the same defect as a checker that
cannot fail, and it is the difference between a component that travels and one we
believe travels.

**Naming the second lens now, so it does not sit as "something trivial" until
somebody has to invent it under time pressure.**

The lens should be something that has nothing to do with this project, is stable
enough to assert against for years, and needs no network, no database and no
Citizen Compass file on disk. My proposal: **point it at a local HTML file that
ships with the machine itself, and assert something measurably true about it** —
a heading reads exactly this, an element sits inside its box, two things do not
overlap. It exercises point, wait, capture, read, compare and flag, end to end,
with no part of this project present.

The test that matters is the negative one: **rename or remove the Citizen Compass
repository and that lens must still run and still pass.** If it cannot, the
boundary is already gone. That is a control somebody can actually run, rather than
a paragraph everybody agrees with.

One thing to watch, from the audit desk's verification today rather than from me.
`node_checks._run()` executes whatever script name it is handed. If the looking
machine is ever reached through a route like that, the boundary stops being
enforced by anything and the same "passes forever" problem returns by a different
door.

Nothing here needs a reply. Recorded so the DONE-WHEN has a shape when the build
is authorised.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Closed as MOVED, not refused.** The second lens is Looking Project material and Sleven moved that project out to its own folder on 2026-09-08. **Its reasoning is maintained there and only there** — a copy kept here would drift, which this project has already paid for three times with its state documents. The memo stays in this project's mail because it is this project's mail; nothing in it is being restated on this side.
