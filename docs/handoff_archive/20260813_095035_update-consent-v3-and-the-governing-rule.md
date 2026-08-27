# Update — Sleven's two standing decisions built. Consent bumped to v3, the governing rule recorded, and the four statements are now machine-checked.

## First, a correction about the source

**`claude/DECISION_screenshots-are-internal-only-2026-08-13.md` is not in the
tree.** I looked, and there is no `claude/` directory. I worked from Sleven's
message, which is the decision itself, so nothing is blocked - but the document
it cites does not exist here and the next session will not find it either.

## Decision 1 - screenshots are internal-only, build no scrubbing

**Nothing to undo.** §5 and §6 were already scoped to sidecars only: the parser
fix, the payload removal and the export guard all operate on `*.json`. No
screenshot scrubbing or UI-region blanking was built or started.

## Decision 2 - the governing rule

> A frame may contain a name; nothing derived from a frame ever may.

**Nothing derives data from a frame today.** The collector is scoped "NO OCR. No
atlas. No vocabulary" in three separate file headers, and grepping for image
decoding finds nothing. So there is no code to guard, and building a guard for a
data path that does not exist would be a check that has never seen its subject -
which this project has a rule about.

**So it is recorded where the first violation would be written**, beside
`mineTxnKeep`, because that is the discipline being extended rather than a
document nobody opens. The note says what will actually happen: the day somebody
builds the reading half, frame data will not look like log data, and writing "a
quick scrubber for the OCR output" will feel reasonable. That is the second,
weaker mechanism the decision forbids. Extend the allow-list or write another
one in that shape - never a filter.

## Consent, version 3

Version 2 said screenshots "are NOT sent unless you specifically ask for them".
True about the mechanism, **misleading about the outcome** - the whole reason the
box exists is that the pictures are wanted, and a promise that leads with what
does not happen is one somebody can agree to without understanding what does.

The new text leads with `PICTURES OF YOUR SCREEN ARE PART OF WHAT IS SENT`, then
states that a frame can show the user's handle and the handles of players near
them, that the pictures are looked at internally and **never published**, and
that anything taken out of one **carries no name**.

**The version is bumped, which re-asks everybody including Sleven.** That is
this file's own rule and this is the case it was written for: the promise about
screenshots became both plainer and broader, and holding someone to a yes given
to the softer wording is precisely what `consent.go` exists to prevent.

## The checklist caught my rewrite, which is the best thing that happened here

`consent_selftest.go` carries a capability -> required-disclosure list. My
rewrite dropped the exact phrase it required:

```
FAIL  CONSENT: every capability that can surprise somebody is disclosed
        not mentioned: screenshots are not scrubbed
```

The check worked. I widened it to accept the new phrasing rather than weakening
it, and **added the decision's three new statements as required disclosures** -
screenshots are uploaded plainly, other people's handles can be in frame, never
published, nothing extracted carries a name.

The decision says *"Must be true before any build goes to a third party."*
Those four checks are what make that enforceable instead of remembered. All
consent checks pass.

## ONE OPEN QUESTION, and it is a behaviour question rather than a wording one

**Screenshots are still opt-in in code.** `BuildExport` takes
`includeCaptures bool`, and the comment beside it is emphatic that there is no
default. The new text says pictures are part of what is sent, which is true when
they are included - but if the intent is that sending now always includes them,
**that is a code change I have not made.**

I did not change it because the decision names the consent text, not the export
behaviour, and quietly widening what gets uploaded is the exact thing the
version bump exists to prevent.

**Which is it?**

- Screenshots stay opt-in, and the consent describes what including them means -
  what is built now; or
- sending always includes screenshots, in which case `includeCaptures` should go
  and I will make that change deliberately.

Rule 8 note: the substance here is Sleven's and he stated it. **The exact
wording is still his to approve** - it is the program's central promise, and I
have drafted rather than decided it. The full text is in the update above and in
`consent.go`.
