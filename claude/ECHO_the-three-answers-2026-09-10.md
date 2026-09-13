# ECHO — the three answers

**Received 2026-09-10. Echo is an outside reviewer with no repository access and no
mailbox. This is her text as received, with her sources, filed so the desks can be
pointed at a path rather than handed a block.**

Routed to Build as
`memo_build_echo-answered-the-three-questions.md`.

---

## HER SHORT ANSWERS

    1  Use heartbeat plus independent outcome verification.
    2  Use the narrow `_replies` allowance, not two independent parsers of the
       forbidden-folder list.
    3  Use the short manual switch window now; replace the permanent on/off switch
       later with an expiring, one-run authorization.

---

## 1. RUNNING BUT NOT DOING THE JOB

Mature systems separate three questions:

- **Alive:** Is the process running?
- **Progressing:** Is it producing heartbeats or checkpoints?
- **Successful:** Did it produce the required result?

A clean exit and heartbeat cannot prove success. Your launcher should only mark the job
successful when an independent checker finds and validates the expected output letter.

A heartbeat should include measurable progress — current stage, artifact count, or last
completed checkpoint — not merely "I'm alive." AWS follows this pattern by failing a
task when it stops heartbeating: "A Task state failed to send a heartbeat" within its
configured period.
*(AWS Step Functions documentation — concepts-error-handling)*

I have not found one universal standard defining how every system verifies its business
result. Scoring the expected artifact is the correct final authority here.

Also make retries use the permanent job number so repeating a task cannot create
duplicate work. Temporal explicitly documents that activities can execute more than
once and recommends idempotency keys.
*(Temporal documentation — error handling best practices)*

## 2. ONE POLICY FILE AND MULTIPLE ENFORCERS

"One policy, multiple enforcement points" is a recognized architecture. NIST describes
one policy decision system directing relevant enforcement points, and says business
traffic can pass through "one or more PEPs."
*(NIST SP 800-207)*

But that is not quite what your two programs would do. They would independently
translate the same text file into two different kinds of rules. The failure risks are:

- interpretation drift;
- different behavior when the file is malformed or unavailable;
- one component loading a newer version than the other;
- one failing closed while the other fails open.

For Citizen Compass, the narrower positive permission is safer:

- Launcher permits only `_replies`.
- Watcher independently protects its forbidden locations.
- A separate check proves the two cannot overlap.

NIST's supporting principle is to make access "as granular as possible" and grant only
the privileges needed.
*(NIST SP 800-207)*

If the launcher eventually needs many writable destinations, replace the separate
interpretations with one shared policy evaluator — not merely two readers of the same
file.

## 3. TESTING THE MASTER SWITCH

For tonight, Option 1 is reasonable:

- everything is staged first;
- you enable the real switch;
- Code performs one prepared run;
- you remove the switch on an independent timer;
- you personally confirm it is gone.

That is testing the genuine production gate, not bypassing it.

The stronger long-term design is an authorization containing:

- one job number;
- one permitted run;
- an expiration time.

Once used or expired, it becomes invalid automatically. This is a standard lease shape.
HashiCorp describes the principle directly: "When a lease is expired, Vault will
automatically revoke that lease."
*(HashiCorp Vault lease documentation)*

That should become the normal production authorization mechanism — not a special
testing exemption. Until that is designed, use the controlled manual window. Do not
postpone containment until Step H, and do not add a bypass.
