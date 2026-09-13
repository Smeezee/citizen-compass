# Memo

To:      Owner
From:    Build
Subject: Follow-up to my swap request: the new binary now carries all three mail repairs Architecture ordered, not one. It is one swap, same procedure. The binary named in my first letter is withdrawn.
Status:  Open

**This amends `2026-09-12_memo_owner_the-close-refusal-is-built-and-tested-may-i-swap-the-watcher`.** I am sending it as a new letter because re-dropping a letter that is already in your tray duplicates it. That is one of the defects fixed here.

## THE BINARY TO SWAP IN, IF YOU SAY GO

    watcher-go/inbox_watcher_pending_20260912b.exe   5,778,432 bytes
    sha256 1dca1fde9aca383b...   console binary, same as the running copy

**The binary my first letter named (`...20260912.exe`, sha256 1594d21d...) is withdrawn.** It is moved to `_to_delete/`, so it cannot be swapped in by mistake.

## THE THREE REPAIRS IT CARRIES

**1. A letter filed Closed without its `CLOSED:` record is refused at filing,** with a reason telling the writer what to add. This is the one that cost two sweeps tonight. It can no longer block a deploy.

**2. `From: Research (CIC)` now reaches Research.** A name in brackets after a desk is treated as a signature. It is kept in the log, not used as the address. **Research's replies stop bouncing.**

**3. A returned answer can be cleared from the tray it came home to.** Dropping the same answer back in now files it, instead of making a second copy beside it. **A changed answer is not swept away:** it still lands in the tray as the newest.

## THE PROOF

- The full test suite passes, and `go vet` is clean.
- **Each repair's tests fail when that repair is disabled,** and pass when it is restored. So the tests can see what they claim to see.
- One existing test changed its example. It used `Research (CIC)` to stand for "unknown desk", which it now isn't, so it uses `Legal (Outside Counsel)` instead and still proves an unknown desk is refused.

## THE SWAP PROCEDURE, UNCHANGED FROM MY FIRST LETTER, PLUS TWO TESTS

The same seven steps: save the running binary under a dated rollback name first, keep exactly one watcher running, test letters only, close them out, check the mail, report, stop.

**Two added live tests:**
- A test answer `From: Research (CIC)` lands in the research tray.
- An identical test answer re-dropped is cleared to `answered/`, and the tray is left empty.

**Still after the zero-dimension deploy.** That sweep is running now.

## THE QUESTION

1. **Go, or not yet?**

*Build (Code), 2026-09-12.*
