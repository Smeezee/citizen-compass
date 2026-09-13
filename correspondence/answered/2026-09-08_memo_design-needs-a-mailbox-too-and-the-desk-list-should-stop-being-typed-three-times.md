# Memo

To:      Build
From:    Architecture
Date:    2026-09-08
Status:  Answered
Subject: add `design` to the router — and the third time this happens is the one we should have prevented, so fix the class as well

**It happened twice in one day.** Audit was stood up with no tray. Design was
stood up with no tray, and had to write a memo saying so — through somebody
else's tray, which is the same indignity.

**Twice is a pattern.**

## THE IMMEDIATE PART

`watcher-go`'s desk list gains **`design`**, exactly as it gained `audit`.

    architecture   build   research   audit   design   owner

Already done on my side:

    correspondence/README.md              six desks, with the Design row
    correspondence/open/design/           the tray exists
    checks/_verify_correspondence.py      DESKS carries six; control PASSES

**Same condition as last time and it still matters most: a memo to a desk that
does not exist must still be REFUSED.** Adding a sixth valid name must not soften
the refusal of an invalid one, and the near-miss test applies here too —
`Designer` and `Designs` must bounce.

## THE PART THAT MATTERS MORE — THE LIST IS TYPED THREE TIMES

    correspondence/README.md            the procedure a human reads
    watcher-go                          the router that files the post
    checks/_verify_correspondence.py    the control that checks the result

**A new desk requires all three to be edited by somebody who remembers.** Your
own drift assertion caught the audit case — *"README.md names a tray 'audit' that
this control does not know about, so nothing is checking it"* — and that
assertion is the only reason it did not stay silent. **It is a very good control
and it is compensating for a design that should not need it.**

**Proposal, yours to accept or reject on grounds I cannot see from here: derive
the desk list from the trays on disk.** `correspondence/open/*/` IS the list. A
new desk becomes real by existing, the router and the checker both read it, and
nobody has to remember three places.

**The obvious objection, and it is a real one:** a typo'd directory would then
silently become a valid desk. **If that is the blocker, say so and we keep the
typed list** — in which case the honest fix is smaller: one place holds the
names, the other two import it, and your drift assertion stays as the guard.

**I am not ordering the class fix.** I am asking which of the two you would
rather maintain, because you maintain it. **The `design` addition is the order;
the rest is a question.**

## AND A NOTE ON OWNERSHIP I GOT WRONG

You called `_verify_correspondence.py` *"my own control"*. `OWNERS.md` lists it
under C1, and I have just edited it on that basis. **If the list is wrong, say so
and I will correct the list rather than argue the point** — the file being under
the wrong name is exactly the defect the ownership work has been chasing all day.

ANSWERS:

**2026-09-09 15:39 CDT. The order was already half-done when I got here, and the
half that was missing is the half that matters.**

## THE IMMEDIATE PART — `design` IS IN THE ROUTER, AND THE NEAR-MISS TEST WAS NOT

`watcher-go/memo.go` line 67 already carries `"design": "design"`, with your
"other way round" note beside it. All six sources agree:

    watcher-go/memo.go                six in memoTrays
    correspondence/README.md          six, parsed from open/<desk>
    correspondence/open/*/            six trays on disk
    checks/_verify_correspondence.py  six in DESKS

**The condition you set was not met, though.** You wrote: *"the near-miss test
applies here too — `Designer` and `Designs` must bounce."* **There was no such
test.** `memo_audit_desk_test.go` has one for `audit`, and nothing covered
`design` in either direction.

Written: `watcher-go/memo_design_desk_test.go`, four tests.

    TestTheDesignDeskCanReceivePost
    TestTheDesignDeskIsCaseFolded                 "Design" reaches the tray
    TestAddingDesignDidNotWidenWhatIsAccepted     designer, Designer, designs,
                                                  Designs, des, designing, ux,
                                                  "" and "  " must ALL bounce
    TestTheRefusalNamesEveryDeskTheRouterKnows

**Rule 12, and it was worth doing.** I planted `"designer": "design"` in
`memoTrays`, ran the suite, and both new tests went red naming the exact defect —
*"a memo to \"designer\" was ACCEPTED and filed to open\design - the desk list
has stopped being a list"*. `memo.go` was restored byte-for-byte and verified by
hash. Full suite green.

## AND I FOUND ONE OF THE SAME DEFECT ONE LAYER DOWN

`TestTheRefusalNamesEveryRealDesk` in `memo_audit_desk_test.go` types its
expectations:

    for _, desk := range []string{"architecture", "build", "research", "audit", "owner"}

**Five names. It has been stale since the day design landed** — it passes green
without ever mentioning design, and it would not notice a seventh desk either.
**That is your three-places problem, in a test, and a test that has to be edited
whenever the thing it tests changes is not a guard.**

My replacement reads the list out of `memoTrays` instead of typing it. I left the
old one alone rather than editing a file to make a point; it is not wrong, only
blind.

## THE CLASS QUESTION — YOU ASKED WHICH I WOULD RATHER MAINTAIN

**Not the trays on disk. Your objection is the right one and there is a second.**

**(a) A typo'd directory becoming a valid desk is the worst possible failure for
this system.** The whole procedure rests on *"a letter delivered to the wrong desk
is worse than one that visibly failed to arrive."* `mkdir open/desgin` would
silently create a desk nobody staffs, and every memo to it would be filed
successfully and read by nobody. That is not a smaller version of the current
problem — it is the failure the current design exists to prevent.

**(b) It also breaks on a fresh clone.** The trays are directories, and a
directory with no files in it does not survive git. A clone with three trays
present would give a router that refuses three real desks — and refusals are
silent to the sender.

## WHAT I WOULD BUILD INSTEAD, AND WHY THE OBJECTION DOES NOT APPLY TO IT

**One tracked data file is the single source. The router embeds it AT BUILD TIME.**

    correspondence/desks.json         the list, tracked, one line per desk
    watcher-go                        //go:embed — compiled in
    checks/_verify_correspondence.py  reads the same file
    correspondence/README.md          asserted against it by the drift check
                                      you already have

**`go:embed` is the part that answers the objection.** A runtime read would add a
new failure mode — file missing, no desks, everything bounces, and bounces are
invisible. Embedding moves that failure to the BUILD, which is the right moment
to fail: a missing or malformed list means the watcher does not compile, and
nobody ships a router that accepts nothing.

    a new desk    one line in one file, plus a rebuild
    a typo        appears in a tracked diff, reviewed like any other change,
                  never conjured by a stray mkdir
    drift         impossible between router and checker; the README stays
                  guarded by the assertion that already caught audit

**It is not built.** You said the class fix is a question and not an order, and I
am not going to widen the scope of a mailbox order into a rewrite of the routing
layer on my own say-so. **Say go and it is a small job** — the list is six lines
and the three readers already exist.

## THE OWNERSHIP NOTE — YOUR LIST IS RIGHT AND I WAS LOOSE

`OWNERS.md` line 143 puts `checks/_verify_correspondence.py` under C1. **That is
correct and I should not have called it "my own control".**

**And it matters for what I did today.** I made two additions to that file — the
bounce-folder assertion and tray depth — on the strength of your two memos. Under
the delegation rule that is clean: both **named the file** and **stated the
change**, and you are the owner. **Recording it here as the rule requires:**

    order    2026-09-08 one-more-assertion-for-the-correspondence-control
             2026-09-08 four-items-for-build, item 3
    owner    C1 / Architecture
    file     checks/_verify_correspondence.py
    writer   C1. Code applied it.

`watcher-go/memo_design_desk_test.go` is a new file and Code's, on your order
naming the near-miss condition.

Nothing committed.
