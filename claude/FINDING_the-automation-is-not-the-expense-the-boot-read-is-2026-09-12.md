# FINDING — the automation is not the expense. The boot read is. And the 09-10 lever order is wrong.

    date     2026-09-12
    from     C1, architecture
    asked    Sleven: "I looked at my uses today... having you do things for me is my
             biggest expense. Code doesn't. You are. A lot of your usage comes from
             the other desks — CIC, C3, C5, the old C1, the adjutant."
    method   measured off logs/wake_log.jsonl and the one payload probe on disk, plus
             file sizes measured today. Every figure says measured or derived.
    corrects `claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`
             on the ORDER of its levers, not on its mechanism.

---

## 1. YOU ARE RIGHT THAT IT IS ME AND WRONG ABOUT WHICH PART OF ME

**The background automation has run four times in its life.** Measured, the whole of
`logs/wake_log.jsonl`:

    wake_start    4
    wake_end      4
    wake_refused  7      (six of them: automation.switch cannot be read)
    wake_usage    1

    first  2026-09-10 16:43 UTC
    last   2026-09-11 03:19 UTC
    since  nothing

**Four wakes, thirty-six hours ago, then silence.** Whatever is spending your allowance, it is
not the wake system. **The desks you named — CIC, C3, C5, the old C1, the adjutant — spent it as
interactive chats, not as automation**, and that matters because the fix is completely different.

## 2. THE ONE WAKE WE HAVE A RECEIPT FOR

**Step 1 of the 09-10 order of work was done** — the usage block is logged now. One record exists:

    label                         probe
    seconds                       26.5
    what it did                   wrote three one-line files, replied in plain text
    num_turns                     5

    input_tokens                     66
    output_tokens                 1,663      of which thinking   583
    cache_creation_input_tokens  44,149      1-hour TTL
    cache_read_input_tokens      85,602
    TOTAL COST                   $0.53       measured, not derived

    model                         claude-opus-5

**Fifty-three cents to write three lines.** And `iterations[0]` alone shows `cache_read` of
**43,200**, so **the cached prefix is about 43,200 tokens** before the desk does anything.

## 3. TWO CORRECTIONS TO THE 09-10 FINDING

**That document guessed at three levers without measurements. Two of the guesses were wrong.**

**LEVER 2 WAS THE BIG UNKNOWN AND IT IS SMALL.** It warned that extended thinking could be
"tens of thousands of tokens per request" and might exceed lever 1. **Measured: 583 thinking
tokens out of 1,663 output, in the whole run.** Real, worth a flag on long-reasoning desks, **not
a lever.**

**LEVER 1 WAS CALLED THE LARGEST AND IT IS ABOUT A FIFTH.** CLAUDE.md is 30,248 bytes, roughly
7,600 tokens, against a measured prefix of ~43,200. **That is 18%.** The split proposal is still
worth doing — **it is not the thing that will move your bill.**

**AND NOBODY NAMED THE LEVER THAT IS SITTING IN PLAIN SIGHT.** Measured: **not one of the four
wake commands carries a `--model` flag.** Every desk, including one whose entire job was writing
three one-line files, runs on the most expensive model available.

## 4. THE ACTUAL LARGEST TERM, AND IT IS THE BOOT READ

**DERIVED from measured file sizes, at roughly four bytes to the token:**

    CLAUDE.md                   30,248 B    ~7,600 tokens
    docs/CURRENT-STATE.md      138,539 B   ~34,600 tokens
    NEXT.md                    272,897 B   ~68,200 tokens
    a desk boot prompt          19,787 B    ~4,900 tokens
                                           ------------------
                                           ~115,000 tokens

**A desk that obeys its own boot instruction — read the state, then the queue — spends about
115,000 tokens before it has done a single piece of work.** That is two and a half times the
entire cached prefix the 09-10 finding was worried about, **paid once at cold cache-creation
rates and then carried in every subsequent request of that session.**

**Multiply by the number of desks you have booted.** That is where your usage went.

**NOT MEASURED, and I want to be plain about it:** there is no usage record for any interactive
chat session. The logging covers wakes only. **The wake figures above are measured; this section
is arithmetic on file sizes.** It is strongly supported and it is not a receipt.

## 5. THE ORDER I WOULD ACTUALLY WORK, LARGEST FIRST

**1. A DESK STOPS READING THE WHOLE RECORD AT BOOT.** One capped digest — what is current, what
is open, where to look for the rest — instead of 411KB of state and queue. **A desk reads the
full file only when it is working on that file.** This is the single biggest saving available and
it is architecture, so it is mine. **It is also the thing that makes more desks cheap instead of
expensive**, which is the opposite of merging them.

**2. `--model` PER DESK.** Filing mail, running a check, routing a letter — none of it needs the
top model. Nothing currently sets this at all. Cheap to add, and it is Code's.

**3. ME. TONIGHT I WROTE ABOUT 40,000 BYTES ACROSS EIGHT FILES**, restructuring three relayed
documents into filed copies with verification passes. **Output tokens are the expensive kind and
that was my choice, not a requirement.** From here: **a relayed document is filed as it arrived,
with a short verification note on top. It does not get rewritten to look like ours.** No
permission needed; it starts now.

**4. BROWSING RESEARCH LEAVES CIC.** Claude in Chrome is Claude tokens. Echo and the other
outside tools are on subscriptions you already pay for. **This is the one you asked for directly
and it is the easiest to do**, because Echo's channel already exists and works.

**5. THE CLAUDE.md SPLIT.** Still worth doing, still waiting on your word since 2026-09-11 — and
**I am downgrading my own claim about it.** At 18% of the prefix it is a tidy-up, not the fix.

## 6. WHAT THIS DOES NOT SAY

**It does not say the wake system is fine** — it says the wake system has barely run, which is
its own problem and a different one. **Six of the seven refusals are the same missing switch
file.**

**It does not price the interactive sessions**, because nothing logs them. **If you want that
measured rather than derived, the only instrument is your own usage page**, and I cannot read it.

*C1, 2026-09-12.*
