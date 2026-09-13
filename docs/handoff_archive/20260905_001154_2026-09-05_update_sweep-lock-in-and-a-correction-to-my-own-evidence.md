# Update — the sweep lock is in and proven, and I have a correction to make

**2026-09-05 · Code**

## The guard

`checks/run_all_controls.py` (Code's under OWNERS.md) now refuses to start when
another sweep is already running.

**Structural, not a lock file.** It asks the operating system which processes
are executing this file, which is rule 14's own remedy - match on what a process
EXECUTES rather than what it is called. No pid file to go stale, nothing to
clean up after a killed sweep, and it cannot be evaded by a different
interpreter or a renamed copy.

**Proven both ways:**

    nothing else sweeping        runs normally, writes its receipt
    a real sweep in flight       REFUSED, exit 2, and it names the pids

`--allow-concurrent` exists for the case where the other process is genuinely
dead, and it says so loudly rather than being silent.

If the enumeration itself fails it prints a NOT PERFORMED warning and
**continues** - a sweep that cannot run at all is worse than two that might -
but it never passes that off as "checked and clear".

## The correction, and it is to evidence I gave Sleven and put in a memo to C1

I reported that two sessions were sweeping at once, on the strength of two
processes started in the same second, "one of them under the SYSTEM python,
which is not how I invoke it."

**That reasoning was wrong.** `venv\Scripts\python.exe` is a LAUNCHER. It spawns
the base interpreter as a child, and `os.getpid()` is the child:

    35864 <- 36756   C:\...\citizen-compass\venv\Scripts\python.exe
    29052 <- 35864   C:\...\Programs\Python\Python311-64\python.exe   <- os.getpid()

So **every sweep shows up as two python processes, one "venv" and one
"system"**. The pair I read as two sessions was one sweep wearing two pids, and
the system-python one was my own invocation's real interpreter.

**What still stands:** the pair I found at 11:41:40 had started 1h41m after I
launched mine, and mine was no longer in the list - so a sweep I did not start
was running. That much is unchanged. What I cannot support is the inference I
drew from the two process names, and I stated it as fact to both Sleven and C1.

The wrong reasoning is written into the guard's own comment at the point where
it excludes ancestors, because that is exactly the mistake the code has to avoid
making.

## Two self-inflicted bugs on the way, both caught immediately by running it

1. **The query contained the string it was looking for.** Filtering inside
   PowerShell with `-like '*run_all_controls*'` put the marker in the query
   process's own command line, so the guard matched itself and refused every
   sweep including the first. Now it lists processes and filters in Python.
2. **Ancestors matched.** The shell that typed the command carries the file name
   too. The parent chain is walked and excluded.

Both would have been invisible in a guard nobody tested against a real second
sweep - it would simply have refused everything, or nothing, and looked fine.
