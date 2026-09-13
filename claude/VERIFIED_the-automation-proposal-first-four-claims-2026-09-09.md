# VERIFIED — the automation proposal, first four claims

    date     2026-09-09
    desk     Adjutant
    source   CCDesk-logs/HOLD_automation-architecture-proposal_for-2026-09-09.md
    method   Anthropic's own documentation and help centre, read directly.
             No wiki, no tracker, no aggregator.

Sleven ruled this document supersedes the queue, and ruled that every claim in it
is unverified until checked, in his words: *"I do not fully trust the other AI.
They have made up things to me and lied a lot in the past, so it needs
verification entirely across the board."*

Four claims checked. **Three hold. One does not, and it is the one the document
itself called its sharpest practical finding.**

---

## 1. THE CREDIT CLAIM — the retraction is TRUE, and this removes the biggest unknown

**Original claim (item 29):** since June 15, 2026, Agent SDK and `claude -p` usage
on subscription plans draws from a separate monthly Agent SDK credit pool rather
than normal interactive usage.

**Its own author later retracted it.** The retraction is correct.

Anthropic, *Use the Claude Agent SDK with your Claude plan* (article 15036540,
dated June 16, 2026), opens with:

> **"Update June 15: We're pausing the changes to Claude Agent SDK usage described below."**

and states that Agent SDK, `claude -p`, and third-party app usage **still draw
from the subscription's usage limits**, and that the promised monthly credit is
not currently available. The original text is preserved below that update for
reference only.

**What this decides:** the Max subscription can currently power the automation out
of the same allowance. There is no separate pool to budget against and no second
limit to design around.

**What it does not decide:** this is a pause, not a cancellation, and the paused
text is still sitting on the page. Anything built on it should be able to survive
the change being un-paused. That is a design constraint, not a blocker.

---

## 2. `--bare` — CORRECTED: the restriction IS documented, and I missed it

**Original claim:** `--bare` skips the expensive boot read, **but is documented as
not using subscription login** — it wants API/provider credentials, so cheap boot
and Max billing are mutually exclusive. The document called this *"the sharpest
practical finding"* and shaped Step 2 around it.

**Half true. The half that shaped the design is unsupported.**

The flag exists and skips what was claimed. Anthropic's CLI reference:

> **"Minimal mode: skip auto-discovery of hooks, skills, custom commands, subagents, plugins, MCP servers, auto memory, and CLAUDE.md so scripted calls start faster. Skills in a directory you pass with `--add-dir` still load. Claude has access to Bash, file read, and file edit tools."**

**OVERTURNED THE SAME DAY. I WAS WRONG AND THE OUTSIDE AI WAS RIGHT.**

I wrote that the restriction "is not in the documentation" on the strength of
reading the CLI reference and finding no mention. **It is documented, on a
different page, and Echo produced it when asked.** Verified here directly at
`code.claude.com/docs/en/headless`, section *Start faster with bare mode*:

> **"Set `ANTHROPIC_API_KEY` before running it, because bare mode doesn't use your subscription login"**

> **"In bare mode, Claude Code never reads OAuth credentials or the system keychain. For the Anthropic API, set `ANTHROPIC_API_KEY` in the environment, with a key created in the Claude Console, or supply an `apiKeyHelper` in the `--settings` JSON."**

**So the outside AI's sharpest practical finding is correct**, and the trade-off
is real: **a cheap boot and subscription billing are mutually exclusive.**

**My error is the one this project has spent the week correcting in other desks.**
I read one page, did not find the thing, and reported its absence as a fact about
the documentation rather than about my search. A primary source read halfway. It
is recorded here rather than quietly edited, because the original entry was
confident and would have steered Step 2 wrong.

**And the same page carries a landmine**, in a note under that section:

> **"`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release."**

**Read that against finding 1.** Subscription billing for `claude -p` survives
only while `-p` is not bare. If bare becomes the default, scripted runs stop
using the subscription by default. **Two separate findings on this page each look
settled and point opposite ways**, and anything built here has to survive that
change landing.

**Also on that page, and useful rather than alarming:** `--permission-prompts none`
exists for runs where nobody can answer a prompt, and `--output-format json`
returns `total_cost_usd` plus a per-model breakdown, described as a client-side
estimate. That second one settles addendum 2's usage question against the source.

---

## 3. TOOL PERMISSIONS — confirmed, including the trap

**Original claim:** deny rules bind even in bypass mode; `--allowedTools` is NOT a
whitelist, it means "these need no approval"; to actually restrict, use `--tools`
and `--disallowedTools`.

**Confirmed on the substance.** Anthropic's CLI reference:

- `--allowedTools` — **"Tools that execute without prompting for permission."**
  That is permission-to-skip-the-prompt, not a restriction on what exists.
- `--disallowedTools` — **"Deny rules. A bare tool name removes the matching
  tools from Claude's context."**
- and directly: **"To restrict which tools are available, use `--tools` instead."**

**The trap is real and worth stating plainly:** a system that lists its safe tools
in `--allowedTools` and believes it has restricted anything has restricted
nothing — it has removed the approval prompt from those tools and left every other
tool available. That is the opposite of what the name suggests.

---

## 4. THE MONEY TRAP — CONFIRMED, and it is the live risk on this list

**Original claim:** if `ANTHROPIC_API_KEY` is present in the environment, Claude
Code prefers it and bills API pay-as-you-go instead of the Max subscription.
Silent; it would look like nothing.

**Confirmed by Anthropic's own help centre**, *Manage API key environment
variables in Claude Code*:

> **"When an API key is set as an environment variable, you'll be charged via API pay-as-you-go rates using the API account associated with that key."**

> **"To use Claude Code with your Claude subscription: Keep the ANTHROPIC_API_KEY environment variable unset."**

**And it has already cost somebody real money in a setup close to ours.** A
reported case in Anthropic's own tracker (issue #86723) describes scheduled runs
billing metered API credits instead of the subscription because
`ANTHROPIC_API_KEY` was set in the environment, while subscription headroom went
unused — **$1,122.83 over two months.** That is a user report, not an Anthropic
confirmation of root cause, and is marked as such.

**This is the one item that must be settled before anything runs unattended.** The
check belongs to the desk that can read the machine's environment, and it reports
presence or absence only — never the value.

---

## WHAT IS STILL UNCHECKED

In the HOLD document's own priority order, and none of it is started:

    item 2, 28      the Agent SDK — does it exist as claimed, is it the
                    supported path, what can it actually do
    item 5, 7, 21   Temporal — the Windows half is now ANSWERED, see
                    addendum below. Self-hosted against cloud and the real
                    cost are checked. What remains is production-server
                    suitability on Windows
    the two he named for challenge:
                    the PostgreSQL / Temporal ownership split
                    whether C5 should do the post-Code verification
    addendum 3      the prior-art and failure research — issue numbers,
                    the 50-million-token runaway, the correlated-failure
                    experiments. Cited with sources; unverified here
    addendum 4      the video prior art — Starchives, Transcribe Critic

## WHAT THE FIRST FOUR SAY ABOUT THE SOURCE

**Four of four held.** The one I marked unsupported was supported and I had not
looked hard enough. The largest claim in the document was retracted by its own
author before anyone here caught it.

**That record is better than this desk's on the same material**, and it is worth
saying plainly rather than filing quietly. It does not make it a design source —
Sleven's standing on that is unchanged and correct — but "verify everything it
says" has now cost this desk one wrong finding and gained nothing on these four.
**The value was in the second opinion, not in the suspicion.**

---

# ADDENDUM — TEMPORAL, checked while waiting on a shader compile

## 5. THE AI REFERENCE ARCHITECTURE IS REAL AND SAYS WHAT WAS CLAIMED

Temporal's own AI Agent Reference Architecture confirms the split the proposal
described, in its own words:

> **"all non-deterministic I/O belongs in Activities, not Workflows."**

The reason given is the one that matters here: when Temporal replays a workflow's
history to recover from a crash, a direct LLM call would return something different
and corrupt the state. Activities record the result once and replay it from history.

It also carries the human-in-the-loop pattern the proposal leaned on — a durable
wait that **"blocks durably without consuming worker threads"** — and one warning
the proposal did not mention: **"The default exponential backoff retry policy is not
appropriate for LLM API calls."** Rate-limit errors carry their own `Retry-After`;
content-policy refusals should never be retried at all. That is directly relevant to
item 23, which said retries are for safe technical problems only. **Their own docs
say the default retry is one of the unsafe ones.**

**So item 14's shape — orchestration in the workflow, every desk call as an
activity — is supported by the vendor's own guidance rather than only by the
outside AI.**

## 6. THE COST, AND IT IS A REAL DECISION

    Temporal Cloud, Essentials      from $100/month — 1M actions, 1GB active
                                    storage, 40GB retained
    Business                        from $500/month
    additional actions              from $50 per million, down to $25 at volume
    active storage                  $0.042 per GB-hour
    support                         the greater of the plan price or 5–10% of usage
    starting credit                 $1,000
    self-hosted                     free and open source — "Everything you need,
                                    on your infra", community support

**Citizen Compass is a free, non-commercial fan project under CIG's Fan Kit
Agreement.** A $100/month floor is not a rounding error against that, and the
$1,000 credit only delays the question by about ten months. **Self-hosting is the
default unless somebody makes the case for the other one**, and that is Sleven's
call, not a technical one.

## 7. THE ONE THAT IS NOT ANSWERED — DOES THE SERVER RUN ON HIS WINDOWS MACHINE

**Temporal's self-hosting guide does not state operating-system support at all.** It
names the database requirement (PostgreSQL, MySQL or Cassandra — this project
already runs PostgreSQL) and describes deployment by Docker, Kubernetes/Helm, or
running the binary. **It never says which platforms are supported or unsupported.**

Absence is not a no, and it is not a yes either. **Recorded as unanswered rather
than inferred**, because the whole point of this pass is that nobody here gets to
fill a gap with a reasonable guess.

This is now the biggest practical unknown in the proposal: everything else is
design, and this is whether the thing runs on the machine it has to run on.

## Sources, this addendum

- Temporal, *AI Agent Reference Architecture* —
  https://go.temporal.io/platform-hub/ai-engineering/ai-reference-architecture
- Temporal, *Pricing* — https://temporal.io/pricing
- Temporal, *Self-hosted guide: setup* —
  https://docs.temporal.io/self-hosted-guide/setup

---

# ADDENDUM 2 — TEMPORAL ON WINDOWS: ANSWERED, WITH THE LIMIT NAMED

**Answered by Echo, an outside AI with no access to this project, verified here
against Temporal's own page.**

`docs.temporal.io/cli/setup-cli`:

> **"The CLI is available for macOS, Linux, and Windows, or as a Docker image."**

> **"The CLI includes a local Temporal development service for fast feedback while building your application."**

Started with `temporal server start-dev`. It brings up the Web UI, the default
namespace, and an **in-memory SQLite database**.

**So a real Temporal server runs on his machine, not just a client pointing
somewhere else.** That was the biggest practical unknown in the whole proposal
and it is now closed.

**The limit, and Echo named it without being asked:** this is the DEVELOPMENT
server. Nothing on the self-hosted deployment page confirms native Windows
support for a production server, and the two are different questions.

**And the development server's storage is in memory** — which for a system whose
entire purpose is surviving crashes and reboots is not a footnote. **Durability
is the product.** A dev server that forgets on restart cannot hold a job that
waits three days for Sleven to answer.

**What is now open, and it is a smaller and much better question than the one it
replaces:** whether `start-dev` can be pointed at the PostgreSQL this project
already runs, or whether the production deployment path is needed, and whether
that path supports Windows.

## WHAT THIS SAYS ABOUT USING AN OUTSIDE MODEL FOR THIS

Two questions went out. **Both came back answered, sourced, quoted, and with
their limits marked** — including one this desk had got wrong.

Today's own prior-art research warned that separate sessions of the same model
converge on the same mistakes and over-trust each other, measured rather than
theorised. **This is the first live test of the countermeasure and it worked.**
A different vendor's model, given a specific question and no project context,
found a page this desk had concluded did not exist.

**That is now an argument for a standing habit, not a one-off**: anything
load-bearing gets a second opinion from outside the family before it is designed
against.
