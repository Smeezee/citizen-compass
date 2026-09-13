# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: check the machine environment for `ANTHROPIC_API_KEY` before anything ever runs unattended
Status:  Answered

**One read-only check, and it needs the machine, which is why it is yours.**

Tell me whether `ANTHROPIC_API_KEY` is set in the Windows environment — user scope
and machine scope both, and inside the repo's `.env`. **Presence or absence only.
Never the value, not in a memo, not in a log, not in a commit.**

## WHY IT MATTERS AND WHY NOW

Checked today against Anthropic's own help centre, *Manage API key environment
variables in Claude Code*:

> "When an API key is set as an environment variable, you'll be charged via API
> pay-as-you-go rates using the API account associated with that key."

> "To use Claude Code with your Claude subscription: Keep the ANTHROPIC_API_KEY
> environment variable unset."

My subscription does not include API access. If that variable is set, an
unattended run bills a separate pay-as-you-go account and **looks like nothing
happened** — no error, no prompt, no line in a log anybody reads.

A reported case in Anthropic's tracker (issue #86723) describes exactly this on
scheduled runs: metered API credits billed while subscription headroom sat unused,
**$1,122.83 over two months.** That is a user report, root cause not confirmed by
Anthropic, and it is close enough to what is being designed here to act on.

## SCOPE

Nothing is being changed. Do not unset it, do not edit `.env`, do not touch the
environment. **Look and report.** If it is set, that is my decision to make, not a
thing anybody fixes quietly.

Full record: `claude/VERIFIED_the-automation-proposal-first-four-claims-2026-09-09.md`.

---

**Correction to the copy of this memo filed earlier today:** it went out with the
wrong `From:` line. Same instruction, same scope. This is the one on the record.

ANSWERS:

**`ANTHROPIC_API_KEY` IS NOT SET. Nowhere. Checked 2026-09-09 16:48 CDT.**

    Windows USER scope        NOT SET
    Windows MACHINE scope     NOT SET
    this session's PROCESS    NOT SET
    repo .env                 does not name it
    _to_delete/.env archive   does not name it

Read with `[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY', <scope>)`
for each of the three scopes, which reads the registry rather than whatever this
shell happens to have inherited. **All three returned null** — not empty-string,
which would be a different and more confusing state. Had any returned a value I
would have reported its length and nothing else.

**`.env` holds four keys and none of them is an ANTHROPIC one.** Names only, no
values read or shown: `DATABASE_URL`, `UEX_API_TOKEN`, `CLOUDFLARE_API_TOKEN`,
`CC_TAKEDOWN_CONTACT`.

**And nothing in the repository sets it.** A ripgrep of the whole tree for the
string finds exactly two files, and both are documents about this question — your
memo and `claude/VERIFIED_the-automation-proposal-first-four-claims-2026-09-09.md`.
No script, no `.ps1`, no scheduled task's command line, and nothing under
`.claude/` sets or exports it.

**That last part is the one worth having.** A variable absent from the environment
today could still be set by a wrapper script at the moment an unattended run
starts, and the answer to "is it set" would have been correct and useless. It is
not being set anywhere.

## WHAT I DID NOT DO

Nothing was changed, unset, edited or exported. No value was read, printed,
logged or written. This was a read.

## ONE THING FOR WHEN THE UNATTENDED WORK IS ACTUALLY BUILT

**The answer above is true as of 2026-09-09 16:48 CDT and has no memory.** Anything that runs
unattended can assert this for itself at startup — presence or absence, never the
value — and refuse to start if it finds the variable set, rather than billing an
account nobody is watching and looking like nothing happened.

**That is a proposal, not something I have built**, and the decision about the
variable itself stays yours as you said.
