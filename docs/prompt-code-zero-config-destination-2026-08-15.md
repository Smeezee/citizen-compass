# PROMPT FOR CODE — nobody should ever type an upload address or a key. Serve the destination from the feed the collector already trusts.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD. Sleven, on hitting this live on his wife's machine:
              "I shouldn't have to manually do that. There should be a way to
              pull it directly from the code and put it where it needs to be
              without ever having to look at it."

---

## 0. What happened, and why it is a design fault not a mistake

Sleven's wife's collector updated itself to 0.3.0 cleanly. Then she pressed SEND
and got a 27 MB zip on her disk and nothing else.

**Nothing was broken.** The updater replaces the executable; it does not touch
`collector-settings.txt`. Her `send_url` and `send_key` were blank, and the
documented behaviour of blank is "write a zip locally and stop." So a correctly
working collector, freshly updated, silently did nothing useful — and it looked
like a failure.

**Every person who ever installs this hits that**, and the setup step that fixes
it is "open a text file, paste two values one of which is a 51-character
password." That does not survive contact with a second contributor, let alone
two hundred.

## 1. The fix: the destination comes down the feed

`update.go` already fetches, over HTTPS, on a schedule:

```
https://raw.githubusercontent.com/Smeezee/citizen-compass/main/releases/collector-latest.json
```

**It already trusts that file enough to download and execute a binary named in
it.** Config from the same source is strictly less dangerous than what the
program already does with it.

Add the destination to that file:

```json
{
  "version": "0.3.1",
  "url":     "...",
  "sha256":  "...",
  "notes":   "...",
  "min_from":"",

  "send_url": "https://collector-receiver.citizencompass-contact.workers.dev",
  "send_key": "<the shared upload token>"
}
```

**Result:** a contributor installs, opens it, presses SEND. Nothing to configure,
nothing to read, nothing to paste.

**And you can change the endpoint or rotate the token by editing one file** —
every collector picks it up on its next check. No rebuild, no re-install, no
asking anybody to edit anything.

### Precedence, and it matters

```
1. a non-empty send_url/send_key in collector-settings.txt   <- local wins
2. otherwise, whatever the feed supplied
3. otherwise, no destination - and SAY SO (see §3)
```

**Local wins deliberately.** Sleven has his own values in place and a future
tester may need to point somewhere else. The feed is a default for people who
have configured nothing, not an override that silently redirects a machine
somebody set up on purpose.

**Cache the last good feed values on disk**, so a collector with no network still
knows where to send when the network returns.

## 2. On putting the token in a public file — read before objecting

**This does not weaken anything, because the threat model already assumed it.**
The 2026-08-10 design states it plainly: the key lives in a text file on other
people's machines, so one will leak eventually; that is why it can ADD ONLY and
why list, read and delete are refused. **A leaked upload-only token costs junk in
a bucket. That was accepted when the key was invented.**

Publishing it in the feed changes the timeline, not the exposure. What it buys is
every contributor after the first getting a working tool.

**But make the Worker earn its keep**, since the token now stops only casual
abuse:

- **Cap the request body.** A legitimate export has a known ceiling; anything
  wildly beyond it is refused.
- **Rate-limit per install ID** (`collector-install-id.txt` already exists and is
  already sent). Refuse a caller uploading far faster than a human plays.
- **Refuse anything not shaped like a collector export**, before it reaches R2.
- **Keep list, read and delete refused.** Unchanged, and re-verify it.

**Rotation must be one edit.** Change the token in the feed, change the secret in
Cloudflare, done — every collector follows within a check cycle. Write that
procedure down; it is the whole reason this is safe to publish.

**If you think this is wrong, say so before building it.** You have been right
against me twice this week — the marker and the restart handover — and this is
the kind of call worth arguing rather than executing.

## 3. Blank must never look like success

Independent of the above, and required either way.

Today, no destination produces a local zip and a completed-looking send. Sleven
read it as a failure; someone less patient reads it as the tool being broken.

- **Before packaging**, if there is no destination, say so plainly: *"There is
  nowhere to send to yet, so this will only write a zip to your disk."*
- **After writing a local-only zip**, the result must not read as "sent." Name
  the file, say it stayed on this computer, say why.
- **When the feed supplies a destination, say where it came from** the first time
  it is used — a program that starts uploading to an address the operator never
  entered should announce it, once.

## 4. Ship 0.3.1 with this in it

The restart-handover fix is built and tested and **not committed**. Commit it,
add this, cut **0.3.1**, republish.

**Sequencing matters:** publish the feed carrying `send_url`/`send_key` FIRST, so
that 0.3.0 machines already in the field pick up the destination on their next
check even before they take 0.3.1. Sleven's wife's machine then works without
anyone touching it again.

**The feed is written by PowerShell.** The UTF-8 BOM you caught last time made it
unreadable to `encoding/json`. Same trap, same file, more fields. Verify the
published feed parses **with the same library update.go uses**, over the real
network, before calling it done.

## 5. What NOT to do

- **Do not put the token in the repository outside the feed**, in a commit
  message, or in a log line.
- **Do not make the R2 bucket public.**
- **Do not remove `send_url`/`send_key` from `collector-settings.txt`.** Local
  override stays; it is the escape hatch.
- **Do not auto-send.** SEND stays a button a human presses. Consent v3 says
  nothing leaves until they press it, and that promise is not yours to soften.
- **Do not `git add -A`.**

## 6. Acceptance

1. A machine with blank settings, given only the feed, sends successfully to the
   bucket with **nothing typed by the operator**.
2. A machine with values in `collector-settings.txt` uses those, not the feed's.
3. Feed unreachable + cached values present -> still sends.
4. Feed unreachable + nothing cached + nothing local -> refuses to look like a
   send, and says what is missing.
5. Changing `send_url` in the feed moves where the next send goes, with no
   rebuild and no reinstall.
6. The published feed parses with `encoding/json` over the real network.
7. Oversized and malformed uploads are refused by the Worker; list, read and
   delete still refused with a valid token — observed, not inferred.
8. `-selftest` passes, including a negative control for each precedence rule.

## 7. Report back

- Whether you think publishing the token is the right call, honestly.
- The rotation procedure, written where the next person will find it.
- What the Worker now refuses, and what you observed it refusing.
- Confirmation that Sleven's wife's machine can send **without anyone opening a
  text file on it**. That is the whole test.
