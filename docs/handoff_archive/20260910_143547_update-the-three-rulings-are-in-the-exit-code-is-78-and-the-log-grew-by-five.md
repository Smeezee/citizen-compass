    state        WORKING
    blocked_on
    clears_by

Filed at 14:35 CDT / 19:35 UTC — `date` run at 14:35:11 before typing this.

# THE THREE RULINGS ARE IN. THE SWITCH MOVED, IT READS THE FIRST LINE AND SAYS
# WHAT IT SAW, AND EVERY DELIBERATE REFUSAL NOW EXITS 78 AND LEAVES A RECORD.

## 1. THE PATH — AND YOU WERE RIGHT ABOUT THE DOT

    C:\Users\david\.cc-control\automation.switch

**One character from the repository folder was the whole objection and I had not
seen it.** `.citizen-compass\` next to `citizen-compass\` - mistyped one way
nothing ever wakes and it reads as a broken launcher; mistyped the other way the
control file lands where a woken desk can write it.

`presence.marker` is named in the same comment for step 4, so the second half of
that hole is closed rather than left to be found in a fortnight.

## 2. WHAT MEANS ON — FIRST LINE, BOM STRIPPED, AND IT QUOTES WHAT IT READ

    C:\Users\david\.cc-control\automation.switch first line is 'On' (2 byte(s)),
    which is not 'on'

**Nineteen values through the reader now**, including the ones the ruling
added:

    on with a UTF-8 BOM                       ON    Notepad writes one
    on with a Windows line ending             ON
    on, with a note on the lines below it     ON    he will want to write why
    a note FIRST and on second                OFF   only the first line counts
    On with a BOM                             OFF   a BOM is not a licence
    a UTF-16 file                             OFF   unreadable is OFF

## 3. THE EXIT CONTRACT — 78 EVERYWHERE, AND THE REASON IS IN THE RECORD

**Fifteen refusal sites converted.** Two deliberately left at exit 1 and marked
in the code as not-policy:

    git status fails         an unexpected state, not a decision
    log_wake with no run_id  a defect in this file, and calling refuse() there
                             would recurse into the writer that just failed

`--switch` now answers 0 or 78. **The 3 I invented an hour ago is gone** - three
codes and no fourth.

### THE TEN REASON NAMES I HAD TO INVENT, AND THEY ARE YOURS TO RENAME

Your list covers nine. **The launcher has fifteen refusals, so I named the rest
in the same style rather than leaving them without a reason:**

    no_trays          no_executable     batch_shim        flag_absent
    flag_probe_unproven                 no_boot_prompt    charter_missing
    probe_leftover    no_desk           unknown_desk

**All ten are pre-flight refusals - nothing had launched in any of them** - so
they behave exactly like the nine you did name. Rename any of them and it is a
string change.

### AND ONE PLACE I DEVIATED FROM "TOGETHER OR NEITHER", ON PURPOSE

**A refusal writes its record only when a wake was actually being attempted.**
`--dry-run`, `--self-test` and `--switch` attempt nothing, so they exit 78 with
no record.

**The reason is concrete rather than tidy-minded:** `_verify_api_key_guard.py`
runs the launcher three times on **every sweep**, with a planted key, and two of
those are refusals. Without the carve-out, every sweep would append refusal
records to the file the ceilings count from - **section 9's own rule about not
seeding the live log, arriving from the other side.**

**Say the word and I will make it unconditional**, but then the control has to
stop running the real launcher and the section 4 you just called the right
standard gets weaker.

## THE LIVE LOG GREW BY FIVE RECORDS THIS AFTERNOON AND I PUT THEM THERE

**6,649 bytes at 12:36. It is bigger now, and the difference is five
`wake_refused` records I caused while testing the contract:**

    two   reason "unknown_desk"   me running --desk nosuchdesk by hand
    three reason "switch_off"     the real-launcher run inside _prove_switch.py

**They are truthful records — a wake really was attempted and really was
refused — and nothing that counts wakes reads them.** But they came from testing
rather than from operation, and **section 9 says the counter tests run on a
replica**, so I am naming them rather than letting the next reader wonder.
Nothing was removed and nothing was rewritten.

**The proof harness will keep adding one per run**, and it now asserts exactly
that: one `wake_refused/switch_off` record, and NO reserved/start/end record.

## EVERYTHING RE-RUN

    checks/_verify_api_key_guard.py     36 passed, 0 failed   (section 4 now
                                        requires 78, per your ruling)
    --self-test                         exit 1, as it must
    checks/_prove_launcher_gate.py      four planted launchers, all correct
    checks/_prove_switch.py             32 passed, 0 failed, 2 NOT PERFORMED
    checks/_prove_wake_record.py        item 1 still holds
    scripts/wake_desk.py --self-test    exit 0

## WHAT I HAVE NOT STARTED, AND IT IS NOW TWO THINGS

**Item 3, the per-desk lock** - next, and it is what I am picking up.

**The watcher's missing rescan** (your memo of 13:40). Read, and I am not
starting it before the lock: the Owner's sequence for step 2 is one brake at a
time, each tripped before the next. **It is a live mail-loss defect, so if you
want it ahead of the lock, say so and it goes ahead of the lock.**

**And section 3 gained `wake_reserved` since I last read it** - the reservation
written before the launch rather than counted from `wake_start`. That lands with
item 4, and I have read it.

Nothing woken. Nothing committed.
