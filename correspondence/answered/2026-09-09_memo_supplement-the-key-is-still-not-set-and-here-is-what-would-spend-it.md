# Memo

To:      Owner
From:    Build
Date:    2026-09-09
Subject: SUPPLEMENT to the API key answer — the answer is unchanged, and I found what would spend the key if it were ever set
Status:  Answered

**Filed 2026-09-09 17:16 CDT. The answer does not change: `ANTHROPIC_API_KEY` is NOT SET,
in any scope, and nothing sets it.** This adds one thing I should have had in the
first reply.

## MY FIRST SEARCH WAS NARROWER THAN MY SENTENCE

I wrote *"nothing in the repository sets it"* on the strength of a search that
**skipped everything git ignores** — which includes `venv/`. A slower search over
the whole directory finished afterwards and found the string in ten more files.

**None of them sets it. All of them READ it**, which is a different thing and
does not change your answer. But it identifies something you should have.

## WHAT IS SITTING IN THE PROJECT'S OWN VENV

    aider-chat   0.86.2
    litellm      1.81.10
    openai       2.20.0

**These are metered API clients.** `aider/onboarding.py` line 64 pairs
`ANTHROPIC_API_KEY` with a model name — that is a tool whose normal behaviour is
to pick up the variable and start billing against it.

**None is declared.** Neither `requirements.txt` nor `requirements-dev.txt`
mentions any of them — zero matches in both. **And nothing in the project imports
them**: no `import aider`, no `import litellm`, in any `.py`, `.ps1` or
requirements file here. They were installed into this venv at some point and
nothing in the codebase uses them.

## WHY IT IS WORTH TELLING YOU RATHER THAN FILING QUIETLY

Your concern was an unattended run billing a pay-as-you-go account and **looking
like nothing happened**. The variable being unset is what prevents that today.
What I did not know when I answered is that **the machinery which would act on
that variable is already installed, in the same virtual environment every
scheduled task on this machine runs.**

    run_checks_scheduled.ps1   uses venv\Scripts\python.exe
    the build                  needs the venv - the system python cannot run it

So the gap between "safe" and "billing" is exactly one environment variable, with
the client already present rather than a further step away.

## WHAT I HAVE NOT DONE

**Nothing was uninstalled, changed, or added.** No value read, printed or logged.
I am not proposing removing those packages — that is your call and there may be a
reason they are there that I cannot see.

**One thing I would build if you want it**, and only if: the unattended entry
points can assert at startup that the variable is unset and refuse to run if it
is — presence or absence, never the value. That turns a silent billing path into
a loud refusal. **Say the word or leave it; I am not building it unasked.**

---

ANSWERS:

**Both approved. Sent to you in full in
`2026-09-09_memo_go-pull-the-three-api-clients-and-build-the-startup-guard.md`.**

**The three come out**, versions recorded so aider can come back if I want it. One
check first: you confirmed nothing imports `aider` or `litellm` and did not say the
same about `openai` — search for that one, the wide way your second pass did, and
stop and tell me if anything uses it.

**Build the guard.** Every unattended entry point asserts the variable is unset at
startup and refuses to run if it is set. Presence or absence, never the value. Name
the entry points you covered and any you left off.

**Context you did not have:** those packages are mine, from my first attempt at the
AI Historian. I believed I was running something local and free. **They are clients
for paid services and I did not know there was a difference.** Nothing on this
project uses them.

**Your second search is why this was worth asking for.** The first answer was
correct and would have left the machinery sitting there unmentioned. Going back and
narrowing your own claim is the behaviour, not an apology owed.
