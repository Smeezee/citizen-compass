# Update — supplement to the owner: the answer holds, my search did not

**Filed 2026-09-09 17:17 CDT.**

A slow full-tree grep I had started earlier and superseded with a faster one
finished afterwards, and it found ten files the fast one had skipped. **The fast
search respected `.gitignore`, which excludes `venv/`.** My answer to the owner
was therefore correct in its conclusion and wider in its wording than in its
evidence.

**The conclusion is unchanged.** `ANTHROPIC_API_KEY` is not set in user scope,
machine scope, this process, `.env` or the archived `.env`, and **nothing sets
it** — every one of the ten files READS it.

**What the wider search found is worth having anyway:**

    aider-chat   0.86.2      installed in the project venv
    litellm      1.81.10     installed in the project venv
    openai       2.20.0      installed in the project venv

Metered API clients. `aider/onboarding.py:64` pairs `ANTHROPIC_API_KEY` with a
model name — a tool whose ordinary behaviour is to pick the variable up and bill
against it.

**None is declared and none is used.** Zero matches in `requirements.txt` and
`requirements-dev.txt`; no `import aider` or `import litellm` anywhere in the
project's own code.

**Why that matters to the question he actually asked.** His worry was an
unattended run billing a pay-as-you-go account and looking like nothing happened.
The variable being unset prevents that. What I did not know when I answered is
that **the machinery which would act on it is already installed in the same venv
every scheduled task here runs** — `run_checks_scheduled.ps1` uses it, and the
build cannot run without it. The distance between safe and billing is one
environment variable, not a variable plus an install.

Supplement sent to the owner tray. **Nothing uninstalled, nothing changed, no
value read or logged.** I offered to make the unattended entry points refuse to
start if the variable is set, and did not build it.

## THE LESSON I AM KEEPING

**A search that skips ignored files is the right default and the wrong evidence
for a sentence containing the word "nothing".** The two searches disagreed
because one of them was not looking where the risk lives — installed packages are
gitignored precisely because they are not ours, and "not ours" is not "not
running".

Nothing committed.
