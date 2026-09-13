# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: One constraint on the launcher before you build it — it will need two modes
Status:  Open

**New requirement, and it lands before you write the launcher rather than after.**

**I want Code woken automatically during the daytime while I am sitting here.** Not
only the thinking desks, and not only overnight.

**That means the launcher will need two modes**, and the difference between them is
the shell and nothing else:

    ALWAYS REMOVED, BOTH MODES
        deploy, commit, push, delete, spend, credentials

    REMOVED ONLY WHEN NOBODY IS PRESENT
        the shell and everything that runs code

**Do not build the tool list as a constant.** In the runbook I sent you, the working
set is `--tools "Read,Glob,Grep,Write"`. **Make that a per-desk, per-mode value the
launcher looks up, not a literal in the command builder** — otherwise the first
change to it is a rewrite of the thing that spends money.

**Nothing else changes about the runbook.** Build the four steps exactly as sent.
**Mode selection is not in scope for this run** — the test wakes the audit desk with
no shell, which is the unattended set. This letter exists so the shape you build does
not have to be undone next week.

**Architecture is specifying how presence is established.** Do not invent it, and do
not wire a mode switch to anything until it has.

**The go to spend is still mine and I have not given it.**
