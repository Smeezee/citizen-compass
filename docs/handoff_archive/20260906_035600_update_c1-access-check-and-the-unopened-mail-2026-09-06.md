# update - C1 access check and the mail nobody had opened, 2026-09-06

C1 was ordered to read the whole record and then to verify every access it should have.

**Access verified this session, by using each one:**

    repo (C:\Users\david\citizen-compass)   GRANTED, read/write, one grant
    device shell                            works - Linux VM, folder mounted
    git                                     read only; 389 files modified, HEAD 87b8ae9
    memory                                  works
    claude.ai project                       works
    Gmail                                   works - on citizencompass.contact@gmail.com
    Google Calendar                         works - still on skdave07@gmail.com
    built-in browser                        available
    cloud container                         works, has network
    Claude in Chrome (CIC)                  NO BROWSER CONNECTED
    computer use                            no applications granted

**What that shell CANNOT do, measured not assumed:** no sqlalchemy, no
playwright, no Go, no network, no PowerShell. So it cannot build, cannot run
the browser controls, and cannot deploy. That is unchanged and matches
CURRENT-STATE. What it CAN do is read, edit and run plain python and node
against the repo.

**RULE 24 was not being followed and the mail proves it.** `correspondence/open/`
holds 24 memos across architecture, build, owner and research. Two are addressed
to the Owner and have been sitting since 2026-08-30.

**One of those two is already done and nobody closed it.** The CRLF item is
HEAD's own commit message - `Twelve files stop looking modified: CRLF leaves the
index`. It should move to `answered/`.

**The other is still true, re-measured today rather than taken from the memo:**
`consent.go`'s text is 2,838 characters against `consent_selftest.go:225`
asserting 2,600, at `consentVersion = 4`. Build's finding stands - a Windows
message box does not scroll, so the tail of that text cannot be read by the
person agreeing to it. Wording is Sleven's alone under rule 8.

Nothing was built, nothing was changed, nothing was committed.

C1, 2026-09-06.
