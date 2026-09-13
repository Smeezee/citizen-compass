# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: CORRECTION — my "your flags are proven wrong" is withdrawn. Your flags worked on this machine. And the real hole is now bigger.
Status:  Open

**The wake ran at 16:43:55 and the reply was in my tray at 16:45:21. Eighty-one
seconds, exit 0, and the numbers are right. The test passed.**

`logs/wake_log.jsonl` records the command, and **it is your original flag set** —
`--restricted`, `--permission-prompts none`, `--disallowedTools`, the charter as
text. **No `--tools`, no `--allowedTools`, and the desk wrote its reply anyway.**

## WITHDRAWN

**My letter said your flag set denies the desk permission to write, and called it
PROVEN.** It is not proven here. I measured it on a Linux container running CLI
2.1.267 and asserted it about your Windows machine on 2.1.266. **That is the same
mistake I have made twice today — evidence from one place, stated as fact about
another.**

**The four runs in the record stand as what happened there. Every conclusion drawn
about THIS machine from them is withdrawn.**

## WHAT SURVIVES, AND ONE OF IT IS NOW WORSE

**The containment has never been tested and it just became the open question.**

The run proves a woken desk **can** write. **Nothing anywhere proves it can only
write into `inbox/`.** With no `--allowedTools` path rule in that command, the
likeliest reading is that it could have written wherever it liked, and the only
reason nothing else changed is that it was not asked to.

**That is the desk's good manners, not a control** — and I watched a desk decline a
write on its own judgement and produce a clean run that proved nothing.

**So the containment probe is next, and it is no longer an optimisation.** Two jobs,
one inside `inbox/`, one outside, worded so the desk cannot decline on judgement.
Pennies. **If the outside write succeeds, we have been running with no containment
at all and that is the finding.**

Also still standing, none of them contradicted by the run:

    the launcher must refuse to start if ANTHROPIC_API_KEY is in the environment
    a timeout on the subprocess, because nobody is present
    .env can be read by a woken desk and should be denied
    the exit code is not proof of anything - score from the filesystem
    --tools is now an OPTIMISATION to be measured here, not a fix

## AND THE ONE THING THE RUN SETTLED THAT I HAD DOUBTED

**Launching from Python on Windows worked.** My concern about `claude.cmd` versus
`claude.exe` did not materialise on this machine. **Leave the explicit resolution in
anyway** — it costs nothing and it stops the failure the day something reinstalls
the CLI a different way.

## THE GO

**You had it and the run happened, so this is not a question about permission.** The
containment probe is authorised on the same footing: **pennies, one run, report what
was refused.**

**Nothing else is authorised to run unattended, and nothing goes on a schedule.**
