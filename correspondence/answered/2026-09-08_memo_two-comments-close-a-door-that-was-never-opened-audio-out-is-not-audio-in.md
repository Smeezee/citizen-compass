To:      Build
From:    Architecture
Date:    2026-09-08
Subject: two comments say "audio is out" when they mean the collector must not make a NOISE — fix the wording only
Status:  Answered

**Wording correction. No design, no build, nothing authorised.**

Two current statements read as though sound is a closed subject in this project.
Both are actually about the collector *emitting* an alert, and both are correct
about that. Neither is about the collector *listening*, which has never been
examined either way.

    docs/prompt-collector-roadmap-CF-02.md:131
        "Sleven has no speakers, so audio is out."

    citizen-collector/tray.go:10
        "Sleven has no speakers, so audio was never an option."

I read both in place. The sentence before each one is about alerting him
mid-flight, so the intent is unambiguous in context and ambiguous out of it.

**Why it matters enough to fix:** a reader arriving at either line cold concludes
the subject is settled and stops. That is the exact failure the sixth document
check was built for — a document that is true and that stops somebody anyway.

**The fix is the narrower words, nothing else:** say no alert *sound*, because he
has no speakers. Do not add a claim about capture in either direction; there is
no ruling to record and I am not making one.

**One more thing to note in passing, not to act on.** `citizen-collector/winapi.go`
has a section header comment reading only `// audio` at line 422. What follows it
is `beep()`, output again, deliberately synchronous so the confirmation is heard.
Flagging it only so nobody reads that header later and thinks audio input already
exists in the collector. It does not.

Everything about the collector rebuild remains Sleven's and closed to this desk.

ANSWERS:

Both lines carry the narrower words as of 2026-09-09 14:52 CDT. Wording only —
no claim added about capture in either direction, in either file.

    docs/prompt-collector-roadmap-CF-02.md:130
        "Sleven has no speakers, so an alert sound is out."
    citizen-collector/tray.go:10
        "Sleven has no speakers, so an alert sound was never an option."

The doc paragraph re-wrapped by one line to stay inside its column; nothing else
in either file moved. `gofmt -l` is clean on tray.go.

`citizen-collector/winapi.go:422` — the bare `// audio` section header — is left
exactly as it is, as your memo instructed. Noted here rather than fixed, so the
next reader of this letter knows it was seen and deliberately not touched.

Not committed. It sits in the working tree with the rest.
