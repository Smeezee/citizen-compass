> **REFUSED 2026-09-12** by Architecture, on Sleven's ruling:
> `correspondence/open/build/2026-09-12_memo_build_no-new-tray-cic-work-goes-to-research.md`.
> Sleven: "since CIC was mostly used for research and web research. That should be the research tray."
> **No new tray is built.** Open-web work is addressed to `research`. "CIC" is an instrument, not a desk.
> This file is kept as the record of the question that decided it. It is not updated.

# PROPOSAL - a tray for the desk now called CIC

    from      Build (Code), 2026-09-12
    for       Architecture - a PROPOSAL, as ordered. Nothing is built.
    order     2026-09-12_memo_build_the-beat-is-ruled-the-matchup-gets-labelled-and-apply-the-diff, item 5
    why       Grok is the acting CIC. CIC carries real work and cannot receive post.
              Tonight's rental letter bounced at 04:44 and held the sweep red.

---

## 1. ONE THING TO SETTLE FIRST: THE NAME

**"cic" is a codename, and the project's rule is that trays are named after the job:**

> "MEMOS ARE ADDRESSED TO THE JOB, NEVER TO A CODENAME - architecture, build, research, owner. Sleven's requirement: *'...if I ever hand this off to somebody, they know what to look at.'*"
> - OWNERS.md, "A NOTE ON `correspondence/`"

**Every existing tray follows that rule:** architecture, build, research, audit, design, owner. **`open/cic/` would be the first one that does not,** and a stranger reading the folder list would not know what it is.

**CIC's job, as CLAUDE.md rule 26 describes it, is "CIC for the live web".** So I propose a job word:

    web        my recommendation - short, and says what the desk reads
    live-web   the same, but longer
    cic        only if you rule the codename is now the job's name

**This is yours, and probably Sleven's,** since the naming rule is his requirement. **Everything below works with any of the three,** so I write `<job>` for whichever you choose.

**One consequence either way:** `To: CIC` is refused today, and it would still be refused under `web`. **I would not add an alias.** The router's list is deliberately a list, not a lookup of nicknames (memo.go:57-61), and a second name for one tray is the kind of fuzziness rule 17 forbids. **Senders learn the one name.** A bounce says what the tray is called, so the mistake teaches.

## 2. A DESK IS FOUR THINGS, AND TWO DESKS HAVE ALREADY BEEN HALF-ADDED

From the comment in `watcher-go/memo.go:71-86`:

- **`audit`** (2026-09-08): the router learned first, and the checker stayed silent until its drift assertion caught it.
- **`design`** (2026-09-08): the checker, the README and the tray learned first, **and the router did not**. A memo to Design would have bounced.

**So all four are one change, landed together, with a proof that each one knows about the desk:**

| # | Piece | File | Owner | Change |
|---|---|---|---|---|
| 1 | the procedure | `correspondence/README.md` | C1 | one line: `open/<job>  waiting on the live-web desk` |
| 2 | the tray | `correspondence/open/<job>/` | C1 | the folder, with `.keep` |
| 3 | the router | `watcher-go/memo.go` `memoTrays` | Code | one entry, plus a test that `To: <job>` routes to `open/<job>/` |
| 4 | the checker | `checks/_verify_correspondence.py` `DESKS` | C1 | one entry |

**Nothing else needs to learn the desk:**

- **BOOT.md** reads `correspondence/open/` with `os.ReadDir`, so a new tray appears on the page by itself. The fixture test "a tray letter" already proves that.
- **The drift assertion** in the checker holds DESKS against the README, so pieces 1 and 4 cannot drift apart silently.
- **OWNERS.md's correspondence note** lists four trays in prose ("architecture, build, research, owner"). It is already two behind, since audit and design are not in it. **That is a separate staleness for you to fix or leave. I am not touching OWNERS.md.**

## 3. ORDER OF LANDING, SO NO WINDOW OPENS

**The bad window is "the README says the desk exists, and the router refuses it".** Tonight that window cost a bounce. So:

1. **The router first:** build, test and swap. **A swap is Sleven's word.** Until the tray folder exists, a memo to `<job>` has nowhere to go, so the router change must also create `open/<job>/` if it is missing. The test covers that case.
2. **Then the README, the tray and DESKS together,** as C1's one change, or delegated to me. **The sweep that follows must be green**, and the drift assertion is what proves the README and DESKS agree.

**Once step 1 is live, a memo to `<job>` is delivered.** Before it, it bounces, which is visible and is today's behaviour.

## 4. PROOF, BEFORE ANYTHING IS CALLED DONE

- **Router:** a memo `To: <job>` lands in `open/<job>/`. A memo `To: CIC` (if `<job>` is not `cic`) still bounces. **The existing test that an unknown desk is refused stays green,** and a mutation dropping the new entry must fail the new test.
- **Checker:** the self-test gains a planted `<job>` memo that must raise nothing. The drift assertion is run once against a README that names `<job>` while DESKS does not, and it must go red.
- **Live:** one test letter to `<job>` through `inbox/` after the swap, confirmed in the tray. **Then Grok is told the address.**

## 5. WHAT THIS PROPOSAL DOES NOT DO

- **It does not decide whether CIC and Research overlap.** Tonight's rental job was re-addressed to Research because it was Research's work. **A live-web tray will attract work that belongs to Research,** and which desk takes a job is yours to rule, not the router's.
- **It does not touch the Grok / Echo "two design desks" holding pattern** from your Owner memo.
- **It builds nothing.** Ruling first.

*Build (Code), 2026-09-12.*
