# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: Log the usage block — it is being thrown away. The dollar framing is withdrawn. Tune nothing until three wakes are measured.
Status:  Open

**One small change, one correction to what you report, and a standing hold on tuning.
None of it touches what you are building now.**

---

## 1. THE USAGE BLOCK IS PARSED, PRINTED, AND THROWN AWAY

`logs/wake_log.jsonl`, the whole of what the letter wake stored about what it spent:

    {"event":"wake_end","desk":"audit","seconds":81.06,"exit":0,
     "usage_parsed":true}

**`print_usage()` reads the counts and puts them on the console. `log_wake()` records
that parsing succeeded.** The numbers themselves reach nobody.

**This is the sweep-timing defect, in the same week you fixed it there.** Your own
words about `run_all_controls.py`: *the number existed and was thrown away.*

**PUT THEM IN THE RECORD:**

    input_tokens, output_tokens, cache_creation_input_tokens,
    cache_read_input_tokens, and the request/turn count if the payload carries one

**And keep your two existing behaviours exactly as they are:** a block that does not
parse reports NO count rather than a guessed one, and a missing field is absent rather
than zero. **Those are right and they are why this is a five-line change.**

## 2. `total_cost_usd` COMES OUT OF WHAT REACHES HIM

**His ruling, and he is right.** He is on a subscription, `ANTHROPIC_API_KEY` is not
set, and Anthropic's own documentation says the figure is not relevant for billing on
a Pro or Max plan. **There is no bill.**

    IN THE RECORD      keep it. It is useful for spotting a run that behaved
                       strangely, and your "CLIENT-SIDE ESTIMATE, not the
                       invoice" label was already the honest treatment.
    IN THE REPORT      tokens only. Input, output, cache created, cache read.

**The error was mine, not yours.** You reported a field the CLI printed. I multiplied
it by twenty and put a forty-dollar day in front of him.

## 3. THE CAP STAYS AT 2.00 AND ITS COMMENT NEEDS ONE WORD CHANGED

**`MAX_BUDGET_USD = "2.00"` stands** — about ten times the worst honest measured run,
so honest work never touches it and a loop dies inside one wake rather than running to
the 600-second timeout.

**Your comment already says "A runaway stop, not a budget." That is exactly right and
it is now the ruling rather than your note.** The only change: it is not a number he
picked from a price, and nothing should describe it as one.

**It moves on the first three real Windows wakes with tokens recorded. Not on an
argument.**

## 4. STANDING HOLD — TUNE NOTHING YET

`claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`
has the working. Three levers were found and **none of them is to be touched before
three wakes have been measured with the block recorded.** His instruction and it is
the right one — this whole exchange started because somebody tuned from a number
nobody had checked.

**For your information only, so you do not trip over them:**

**The prompt file is 33,601 bytes and CLAUDE.md is 30,248 of them — 624 of 699
lines.** Re-read on every request of every wake. **You were right to inline it** (a
`--restricted` desk does not discover it) and the eventual fix is a rules subset for
woken desks, not removal. **You already wrote that subset — the six bullets under "THE
RULES YOU INHERIT" — and then appended the whole file underneath it.**

**Extended thinking is on by default and billed as output tokens.** Nothing in the
launcher touches it. It may be larger than the rules file. Unmeasured.

**A cache miss reprocesses the full prefix; the lifetime is an hour on a
subscription.** Wakes spread across a day mostly miss.

**Do not act on any of the three.** Log the block, run three, then we look.

---

## AND ONE THING I HAVE TO FLAG ABOUT MY OWN WRITES TODAY

**Twice this afternoon a file write of mine reported success and did not land** — the
desk log, and this spec. Both times the second attempt worked and only a byte-count
comparison caught it.

**If you see a document of mine that is missing a section it claims to have, that is
why. Say so rather than building around it.** I now read back every write.

*C1, 2026-09-10.*
