    state        IDLE
    blocked_on   your approval on §§3-6 below, and the watcher swap
    clears_by    OWNER

Filed at 19:26 CDT / 00:26 UTC — `date` run at 19:22:56, this typed straight
after it.

# THE PERPLEXITY ACL AUDIT, IN FULL. RULE 13 COMPLETION RECORD.

**You are right and it was missed.** The audit ran 18:56–19:02, produced findings
and eight proposed commands, and went into a chat window and nowhere else. **A
finished unit of work with findings in it is exactly what rule 13 covers.** The
authorisation for that task said no file changes; I raised the conflict and then
did not come back to it when the work finished. That is on me, not on the
authorisation.

Filed through `inbox/`, which is the only supported way in — the Go watcher is
the sole writer of `LATEST_HANDOFF.md` and of this archive.

**Nothing else was touched, corrected, reformatted or updated while filing
this.** No permission on this machine has been changed. No command below has
been executed. **Nothing was swapped.**

---

## THE TASK

A read-only NTFS audit: why `DESKTOP-TQEKVJB\perplexitysandbox` gets
`UnauthorizedAccessException` on `C:\Users\david\citizen-compass`, what the
minimal read-only grant would be, what it would expose, and how to undo it.

---

## 1. IS NTFS THE CAUSE? YES, CONFIRMED.

**The account is real, enabled, and was in use twelve minutes before the audit.**

    name        DESKTOP-TQEKVJB\PerplexitySandbox   (case differs from the
                                                     request; same principal)
    SID         S-1-5-21-1019676958-2023951196-3462819575-1022
    enabled     True
    source      Local
    last logon  2026-09-10 18:44:29

**It appears nowhere in the project's ACL:**

    C:\Users\david\citizen-compass
        NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
        BUILTIN\Administrators:(I)(OI)(CI)(F)
        DESKTOP-TQEKVJB\david:(I)(OI)(CI)(F)

Three principals. No `Users`, no `Everyone`, no sandbox entry. Every one is
`(I)` — inherited from `C:\Users\david`.

**And it has no group that would grant access anyway:**

    Administrators        NO   (members: Administrator, david)
    Users                 NO
    Guests                NO
    Remote Desktop Users  NO
    Backup Operators      NO

**Not even in `BUILTIN\Users`**, so it picks up nothing from the common-user
grants higher in the tree, and it has no administrative override.

**The DACL fully explains the exception.** Nothing else — antivirus, file locks,
EFS, controlled folder access — needs to be invoked, and none of it was
investigated.

## 2. THE RELEVANT ENTRIES

**`C:\Users\david\citizen-compass`** — the three inherited Full entries above,
**no explicit ACE of its own, inheritance enabled.** That last part matters for
§4: one inheritable ACE at this folder reaches the tree without stamping
120,000 files.

**`C:\Users\david`** — and this is where the chain breaks:

    NT AUTHORITY\SYSTEM              (OI)(CI)(F)   explicit, NOT inherited
    BUILTIN\Administrators           (OI)(CI)(F)   explicit
    DESKTOP-TQEKVJB\david            (OI)(CI)(F)   explicit
    S-1-15-3-65536-599108337-...     (S,X)         an app-container capability
                                                   SID, traverse only

**Nothing is marked `(I)`, so inheritance from `C:\Users` is blocked at the
profile root.** That app-container entry is worth noting for a different reason:
**a narrow traverse-only ACE at this exact level already exists as a
precedent.**

**`C:\Users`** — `Everyone:(RX)` and `BUILTIN\Users:(RX)`, plus inherit-only
`(OI)(CI)(IO)(GR,GE)` for both. The sandbox account can already traverse and
list `C:\Users`. **The inheritable read dies at `C:\Users\david`.**

## 3. WOULD A GRANT ON THE PROJECT FOLDER ALONE WORK? ALMOST CERTAINLY — AND I AM NOT CALLING IT CONFIRMED.

    C:\                              not inspected
    C:\Users                         Everyone:(RX)            traversable
    C:\Users\david                   NO ACE for the sandbox   <- the question
    C:\Users\david\citizen-compass   NO ACE for the sandbox

Opening a file deep in a tree normally needs traverse (`X`) on every parent.
**The exception is the `SeChangeNotifyPrivilege` user right — "Bypass traverse
checking" — which Windows assigns to `Everyone` by default.** `Everyone`
includes this account. If the local policy is unmodified, **the project-folder
grant alone is enough and nothing is added to `C:\Users\david` at all.**

**Why not confirmed:** proving it needs either `whoami /priv` run *as that
account*, which I cannot do, or `secedit /export /cfg <file> /areas USER_RIGHTS`,
**which writes a file** and was outside that task's authorisation.

**The free way to settle it: apply the §4 grant and have Perplexity retry.** If
it works, the question is moot. If it still fails, the minimal remedy is a
traverse-only ACE on the profile folder:

    icacls "C:\Users\david" /grant:r "DESKTOP-TQEKVJB\PerplexitySandbox:(NP)(X)"

`(NP)` no propagation, `(X)` traverse only. **No directory listing, no file
read, no access to Documents, Desktop, AppData or anything else in your
profile.** It opens the door and confers no right to look round the room — which
is materially different from "access to the David profile".

## 4. THE MINIMAL READ-ONLY GRANT

    icacls "C:\Users\david\citizen-compass" /grant:r "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"

    /grant:r   replaces any existing grant FOR THIS PRINCIPAL ONLY - SYSTEM,
               Administrators and david are untouched. Idempotent.
    (OI)(CI)   inherits to files and subfolders
    (RX)       read and execute

**Deliberately no `/T`.** Inheritance is enabled and `data-layer/` alone holds
~120,000 files / ~13.9 GB. `/T` would stamp an explicit ACE on every one: slow
going in, slow and error-prone coming out.

Verify, read-only:

    icacls "C:\Users\david\citizen-compass" | findstr /i perplexity
    icacls "C:\Users\david\citizen-compass\README.md" | findstr /i perplexity

The second is the one that matters — it proves the ACE actually reached a child.

## 5. THE SECRET-BEARING FILES, AND THE DENY COMMANDS

**No file contents were opened. Names and metadata only.**

**Real candidates:**

    .env                                                    275 B  09-04 15:04
    _to_delete\.env.pre_takedown_contact_20260904T200457Z   223 B  09-04 15:04
    .claude\settings.local.json                           7,240 B  08-07 13:25
    .claude\settings.json                                   653 B  07-30 17:59
    .wrangler\cache\wrangler-account.json                   125 B  08-06 17:32
    citizen-collector\.wrangler\cache\wrangler-account.json 125 B  08-14 21:55
    citizen-collector\collector-destination.json
    citizen-collector\collector-last-send.txt
    citizen-compass.ccpp
    _needs_review\guardproof_20260909\citizen-compass.ccpp
    _to_delete\2026-09-09_claude-settings-before-stop-hook-removal\settings.json
    .claude\worktrees\...\.claude\settings.local.json

**ZERO results for `*.key`, `*.pem`, `*.pfx`, `*.p12`, `*.jks`, `*.crt`, and no
`.dev.vars`.**

**There is no `.env.example` or template of any kind.** The only two
`.env`-family files are the live one and one dated archive copy — so there is
nothing in that family that is safe to expose by definition.

**Sixteen name-pattern hits that are NOT secrets, listed so nobody blocks
them:** twelve Star Citizen game-data items under
`data-layer\external-sources\scunpacked-data\` (`crus_star_runner_secret_cargo_panel.json`,
`fps_consumable_keycard_stormbreaker_doctorcredentials.json` and similar), four
handoff/memo filenames containing "token", and
`docs\RULING_credentials-are-rotated-2026-08-15.md` — a ruling ABOUT
credentials, not a credential.

**The denies. Directories first, and that is on purpose:**

    icacls "...\.claude"                      /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"
    icacls "...\.wrangler"                    /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"
    icacls "...\citizen-collector\.wrangler"  /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"
    icacls "...\_to_delete"                   /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"
    icacls "...\_needs_review"                /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"

    icacls "...\.env"                                         /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(R)"
    icacls "...\citizen-compass.ccpp"                          /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(R)"
    icacls "...\citizen-collector\collector-destination.json"  /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(R)"
    icacls "...\citizen-collector\collector-last-send.txt"     /deny "DESKTOP-TQEKVJB\PerplexitySandbox:(R)"

Explicit deny beats inherited allow, so ordering does not matter.

**`_to_delete\` and `_needs_review\` are denied wholesale deliberately.** Both
are quarantine areas that accumulate superseded copies of live files — today's
`_to_delete\.env.pre_takedown_contact_...` is exactly that pattern. **A deny list
of individual files is a list somebody has to maintain. A deny on the folder
survives the next thing that lands in it.**

**Two limits, stated rather than buried.** This list comes from the filename
patterns in the brief; **a secret in an unremarkable filename would not appear**,
and finding one means reading contents, which was forbidden. And a deny stops a
file being read from now on; it says nothing about whether it was ever read
before — the ACL says it could not have been, but that is an inference from the
current state, not an access audit.

## 6. THE ROLLBACK

**Targeted, preferred, fast:**

    icacls "C:\Users\david\citizen-compass" /remove:g "DESKTOP-TQEKVJB\PerplexitySandbox"

then `/remove:d "DESKTOP-TQEKVJB\PerplexitySandbox"` on each of the nine deny
paths in §5, one command each.

**The sweep, only if you suspect an ACE landed somewhere unlisted:**

    icacls "C:\Users\david\citizen-compass" /remove:g /remove:d "DESKTOP-TQEKVJB\PerplexitySandbox" /T /C

**On ~120,000 files this takes a long time**, and `/C` means failures scroll past
instead of stopping it. Capture the output and read it if you use this one.

**If the §3 traverse ACE was added it comes off separately:**

    icacls "C:\Users\david" /remove:g "DESKTOP-TQEKVJB\PerplexitySandbox"

**Every command names the principal explicitly.** `/remove:g` and `/remove:d`
strip only that SID's entries; SYSTEM, Administrators and david are untouched and
inheritance is not altered.

Confirm — **and no output is the pass condition, so test the check against a path
that DOES contain the string first, or it proves nothing:**

    icacls "C:\Users\david\citizen-compass" | findstr /i perplexity
    icacls "C:\Users\david"                 | findstr /i perplexity

## 7. COULD THE GRANT ALLOW WRITING, DELETION, OWNERSHIP OR PERMISSION CHANGES?

**On the ACL as inspected: no, to all of them.**

    write / append          FILE_WRITE_DATA, FILE_APPEND_DATA    not in (RX)
    change attributes       FILE_WRITE_ATTRIBUTES                not in (RX)
    delete                  DELETE, or FILE_DELETE_CHILD on the
                            parent                               not in (RX)
    create                  FILE_ADD_FILE / _SUBDIRECTORY        not in (RX)
    take ownership          WRITE_OWNER, or SeTakeOwnership      not in (RX),
                                                                 and it is not
                                                                 an admin
    change permissions      WRITE_DAC, or ownership              not in (RX)

**Four conditions would change that answer:**

**1. A subfolder with inheritance disabled and its own permissive ACE.** I read
the project root, `C:\Users\david` and `C:\Users`. **I did not walk 120,000
children.** If some subfolder carries `Everyone:(F)` with inheritance blocked,
the sandbox may already have write access there TODAY, independent of anything
proposed here. **Unknown, and it is the one I would check before granting** — a
read-only scan for child ACLs lacking `(I)` entries, on your word.

**2.** A `CREATOR OWNER` ACE deeper in the tree. None at the three levels read.

**3.** Typing `(RX,W)` instead of `(RX)`. The §4 verification exists for that.

**4.** Escalation outside NTFS entirely. Nothing suggests it — the exception
itself is evidence the account is not elevated.

### AND THE REAL RISK IS EXECUTE, NOT WRITE

**`(RX)` grants the right to execute any binary in the tree.** That tree holds
six `inbox_watcher*.exe` / `watcher*.exe` builds including the live one, the
launcher that spends money, the scripts that register scheduled tasks — and
**roughly 29,000 files cloned from third-party sources that `CLAUDE.md` states
have not been malware-scanned.**

**Hard rule 7 is "never execute code you downloaded."** This grant hands a
third-party automation account the NTFS right to do exactly that. It does not
make it happen, and read-only cannot modify those files — **but the capability is
created by this change and does not exist now.**

**`(R)` is not a safer substitute.** Generic Read excludes `FILE_TRAVERSE`, so
descending into subdirectories starts depending on the bypass privilege for
every open, and you get intermittent failures rather than security. **If Execute
is unacceptable, the answer is §8, not a weaker grant.**

## 8. THE SAFER ALTERNATIVE, AND IT IS WHAT I RECOMMEND

**Do not grant the sandbox account anything on the live project. Give it a
curated export folder outside your profile.**

    C:\Users\Public\cc-share\
        david                 Full          writes the export
        PerplexitySandbox     (OI)(CI)(RX)  reads it

    icacls "C:\Users\Public\cc-share" /grant:r "DESKTOP-TQEKVJB\PerplexitySandbox:(OI)(CI)(RX)"

                            live-folder grant          export folder
    secrets                 a deny list somebody       never copied in
                            maintains
    rule 7 / 29,000 files   capability granted         no binaries present
    120k unaudited children real, unquantified         folder is small and known
    a mistyped (M)          the whole project          a copy
    the §3 traverse問題      unresolved                 does not arise
    rollback                many commands, maybe /T    delete the folder

**And it is the interface this project already specified.** Section 9 of today's
state report defines the file-based contract for exactly this: a third party
gets named extracts with path, size and mtime, requests go through `inbox/` via a
person, and it never writes to the repository. **An export folder IS that
contract with an ACL on it.** Granting the live tree goes around a design that
already exists.

**A read-only SMB share or a junction does not help** — share rights intersect
with NTFS, and a junction resolves to the target's ACL.

---

## WHAT IS STILL WITH YOU

    the ACL change itself       §§4-6 modify the machine OUTSIDE the repository.
                                Hard rule 6 makes that yours, not mine.
    my recommendation           §8. Do not grant on the live tree at all.
    the watcher swap            unchanged and untouched, per your memo.

## ONE MORE THING THAT IS ALSO ONLY IN A CHAT WINDOW

**The technical state report of 18:16–18:25 was never filed either.** Same
window, same session, same defect — it went to the requester and not to disk.
Its ARRIVAL note is in the archive; its content is not.

**It is roughly ten times the length of this.** I have not filed it because you
named the ACL audit specifically and told me not to do anything else while I was
in here. **Say the word and it goes in next, in full.**

Nothing committed. Nothing swapped. No permission changed.
