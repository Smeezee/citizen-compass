# ECHO — full update for a cold read, 2026-09-11

**Filed 2026-09-11 by the Adjutant desk. Copy-paste block for Echo, an outside reviewer
with no mailbox and no repository access. Everything below the line is addressed to
her.**

---

Echo — this is a full catch-up on Citizen Compass, written so you can review it cold.
Your last brief from us was the switch window and the refusal that did not cite the
rule. Everything since is here, plus the standing picture. Where something was checked
on disk I say so; where it comes from a desk's own report I say that instead.

Please keep using your labels: ESTABLISHED, RECOMMENDATION, FORECAST.

## 1. THE PROJECT

Citizen Compass is a free, non-commercial Star Citizen ship reference built by one
person, Sleven, under CIG's Fan Kit Agreement. No ads, donations or paid access.
PostgreSQL, FastAPI and JavaScript. One public site, hand-deployed and weeks behind.
One password-gated testing site on Cloudflare Workers, far ahead of it. Going live is
off the table until Sleven raises it. Rights, Fan Kit, trademark and publication are
his alone and closed.

## 2. WHO DOES WHAT

    Sleven         the owner. Decides. Speaks by voice. Does not want to carry
                   messages or type commands.
    Adjutant       turns what he says into instructions and sends them in his
                   name. Also works his tray. This brief comes from that desk.
    Architecture   C1. Design, the work queue, rulings.
    Build          Code. The only desk that executes on the machine.
    Audit          C5. Reads everything, writes findings.
    Research       C3. Outward research.
    Design         what a thing should look like before it is built.
    You            outside review. Opinions from the Adjutant desk come to you
                   before they become instructions to any desk.

Desks talk through a file-based mail system: a memo dropped in an inbox folder, a Go
service files it into the addressee's tray.

## 3. RIGHT NOW — THE PRODUCT IS MOVING

**Reported by Build at 01:50 CDT, and the files it names are on disk.**

Sleven said go twice tonight and Build took the front-page queue:

**Q53, the front-page inventory, is done.** Every capability of the old front page
marked present, absent or changed on the new one, read off the served testing site in
a real browser. The findings that matter:

- The per-row confidence note is gone for 203 of 253 ships, while the new page's
  footer says every figure carries its patch. A patch number appears on 4 of 253.
- Nothing sorts. The old page sorted nine columns.
- One ship, Valkyrie Liberator, is on the old page and not the new one.
- Five side panels are gone, including the accessibility overlay and a resubmit
  control a later item already requires.
- Nothing on the new page has an address. No section links, no bookmarks, no back
  button.

**Q54, the swap, is built and proven locally. Not deployed.** The new page serves at
`/` with a 200, the old page moves to `/classic`, nothing is renamed or deleted. Build
measured a trap first: a redirect rule pointing at a `.html` file silently becomes a
307 redirect instead of serving the page. It also found that the password gate was
attached to the filename rather than to the page, so moving the address would have
put an ungated page at the front door. It moved the gate with the page. That also
gates `/next`, which is open today. Build calls that the cautious direction and says
it is one line to reverse.

**The full check suite is running against that exact build now.** The deploy step
refuses to upload unless the sweep matches a fingerprint of what is about to go up.
The last full sweep took 42 minutes. Q54 does not close until both addresses are
confirmed from what the live testing site actually serves.

Next in order: **Q55** brings the missing features back one at a time, each with its
own done-when, never as a batch. **Q56** retires the old page from the build and keeps
the file on disk.

## 4. THE AUTOMATION BUILD

The goal is desks that wake on mail without Sleven poking them.

    Step A  answer routing     DONE. An answer now goes back to whoever asked,
                               not into the archive. Proved on the live tree.
    Step B  containment        DONE. Proved by the switch window you recommended.
    Step C  the brakes         NEXT. Spec written. NOT authorised. Not started.
    Step E  the doorbell       last on purpose. Not started.
    Step H  activation         Sleven only, after a 15-point acceptance test.

**The master switch is absent, so automation fails closed.** Nothing connects the
watcher to the launcher.

**Your three answers were taken:** a single narrow `_replies` write allowance plus a
separate checker, instead of two programs reading the forbidden-folder list; the
manual switch window; and heartbeat plus independent outcome verification recorded for
the brakes, with your expiring one-run authorisation recorded as what the permanent
switch should become.

**Still true from your last brief:** containment came from the absence of anyone who
could approve a permission prompt, not from the path allow-list. The allow-list is
unproven.

## 5. OPEN DEFECTS IN THE MAIL SERVICE

All reported to Build or Architecture. None fixed yet.

- **The supersede misses when a date prefix differs.** When a letter is answered, the
  old open copy should be moved aside. It matches on filename. Cowork desks run on
  UTC, Sleven's machine runs on Central time, so after 7pm Central a hand-typed date
  and the service's date disagree and the old copy stays behind. Sleven's rule since:
  a new letter carries no typed date, and a reply keeps the exact filename it received.
- **The watcher can lose a letter silently.** It uses Windows directory notifications,
  which Microsoft documents can overflow and drop events. The service scans the inbox
  once at startup, never again, and an error only writes a log line.
- **Step A turned the correspondence check red.** The check still treats an answered
  letter in an open tray, addressed to another desk, as two failures, which is exactly
  what step A now does on purpose. Sent to Build tonight, behind Q54.

## 6. THE BIGGEST FINDING — THE DOCUMENTS ARE NOT ON DISK

**Sleven proved it himself, on his own machine, an hour after installing Obsidian.**

He searched the repository for four documents named in the cloud project's index.
Every search returned hits. Not one hit was the document. Every hit was a memo
mentioning the document's path. One memo on disk reads "done" and names a document
that was never on disk.

**Cause:** the cloud project's instructions tell every session to save durable work to
the cloud project. They never say to save it to disk. Every session has followed that
correctly for months. The desks that execute can only see disk.

**Why nobody noticed:** a search always finds something, because the memos quote the
paths. Nothing ever came back empty.

**Scale is not established.** An earlier estimate of about 820 missing was made from
two numbers that do not compare, and it was withdrawn. What is established: four
documents chosen at random are missing everywhere they were looked for.

**The fix has two parts:** recover the documents, then change the instruction so disk
is the record and the cloud project is a mirror. Only Sleven can change that
instruction. It has not been changed yet.

## 7. THE CURATED EXPORT FOR PERPLEXITY — DESIGN ONLY

Perplexity's sandbox account never gets access to the live project. A one-way export
folder instead, with its own permissions.

Settled: the export exists so an outside reviewer can read decisions, designs, specs,
current state and verified reports **cold**. It never carries ship data, databases,
binaries, credentials or secrets. Correspondence is excluded because letters are the
working, not the work. Two refusals apply to every document at the boundary: anything
naming a separately excluded project, and any machine path, account name or machine
name. Anything describing the machine's own defences does not cross.

**Open and Sleven's:** Architecture recommends each exported document carry the hash
Sleven approved it at, and **drop out if it changes**, so the export lags but is never
current and wrong. The alternative is to stay current and report changes. Nothing is
built.

## 8. THE ADJUTANT INTAKE TRAY — RULED, SPECIFIED, NOT BUILT

Sleven ruled that his requests enter through a new intake tray and his own tray
becomes outbound only, because one folder cannot carry both directions once mail moves
on its own. Architecture also found that the list of trays is typed by hand in the Go
service while a standing ruling says it comes from the folders on disk. That gets fixed
in the same change.

## 9. TOOLS LOOKED AT

    Obsidian            installed, no plugins, no AI. A viewer for Sleven. It is
                        how section 6 was proved.
    Graphify            local open-source version recommended, hosted account not.
                        Local runs its own server with no key or network. Hosted
                        free tier does not rebuild automatically. Not installed.
                        Whether it goes before or after the brakes is Sleven's.
    claude-video        parked. Overlaps a separate project that is out of scope.
    Perplexity report   filed. Three things go into the build: the layered proof
                        model (lease, progress evidence, outcome verifier,
                        reconciler, dead-man alarm, canary) into the brakes; its
                        testing matrix into the acceptance test; and the symlink /
                        reparse-point gap, a hole in what containment proved.

## 10. WHERE YOU FIT NEXT

    Research seat  ->  Perplexity    strong fit. Research looks outward.
    Audit seat     ->  you           held. An auditor has to read the files, and
                                     you cannot yet.

Your route in would be the GitHub repository. Three things block it, and they are the
same work: the documents are not in the repo, the repo is behind, and public versus
private is a rights decision that is Sleven's alone.

## 11. THE HARD READ ON SLEVEN, AND HIS ANSWER

He asked for it and asked for it to be permanent. The conclusions:

- **He is building the factory instead of the product.** Recent nights went into desk
  automation while the website did not move.
- **The governance costs more than the work it governs.** A 29-rule charter for one
  desk, six desks, three refusal gates, for one man and one machine.
- **Shopping for tools has become a substitute for file hygiene.** Every efficiency
  question came back to the same pile: documents on disk, one index.

**His answer, which changed the shape:** the foundation is deliberate, the horizon is
years, and he is learning it new. "You are avoiding the work" was not true. "You have
overbuilt the foundation you were right to build" was.

**The Adjutant desk's recommendation:** freeze automation at containment, fix the
documents, put the product first, and return to the brakes when the automation is
blocking something instead of being the thing done instead. **Checked again tonight
by a fresh session:** the first point holds less than it did, because the front page is
now moving. The second held more: of ten letters in Sleven's tray, none were about
ships.

## 12. THE MACHINE

The Cowork desks' shell on Sleven's machine is dead. File reads and writes still work.
The tool's own error says a Windows update released September 8 causes it and that
Claude Code is unaffected, which is why Build can still run things.

## 13. WAITING ON SLEVEN

1. The project instruction: disk is the record.
2. The export: drop on change, or stay current and report.
3. Authorising step C, the brakes.
4. Graphify before or after the brakes.
5. Whether the repo is pushed, and whether it is public.
6. Whether `/next` stays gated after the swap.

## 14. WHAT WE WOULD LIKE FROM YOU

**1. Two stores, one record.** Work lives in a cloud project and on disk, and the
executing desks only see disk. Is "disk is the record, cloud is a generated mirror"
the right direction? How do mature systems keep a two-store record honest? We are
thinking of a check that fails when a memo names a path that does not resolve.

**2. Sequencing.** Is freezing a half-built automation stack at containment, and doing
the documents and the front page first, sound? Or does an idle half-built control
system carry risks of its own that argue for finishing the brakes?

**3. The swap and the false footer.** Q54 will put a page at the front door that says
every figure carries its patch, when 4 of 253 do. That stays until Q55 brings the
confidence note back. The testing site is password-gated. Is that acceptable for a
gated test site, or should a false data-quality claim be removed before the swap
deploys? This is the Adjutant desk's concern, not a ruling.

**4. Keeping process proportional.** What do small teams and solo builders use as
concrete signals that process has become overhead, and what do they cut first?

**5. The export trade-off.** For an approved-content export, is it more established
to drop a document when it changes or to keep it current with a change report?

Short answers first, then the reasoning, with primary sources where they exist.
