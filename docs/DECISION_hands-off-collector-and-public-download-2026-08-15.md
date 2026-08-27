# DECISION — the collector becomes hands-off, the download goes public unsigned, and consent is what makes the first one legitimate

    ruled by  Sleven, 2026-08-15, in session with C1.
    status    STANDING. These are answers, not proposals. Build to them.

---

## What Sleven asked for, in his words

> "we should build in the feature to where as soon as the session ends and the
> collector no longer recognizes Star Citizen, it sends all of the data back
> wipes the data collected from the user's computer and then shuts down so that
> way they don't have to do anything. also should be a ways when you launch the
> Star Citizen launcher or the game. The collector automatically comes up so that
> way nobody has to do anything in the background."

And on distribution:

> "is there an easier way for us to distribute it to people? like I'm thinking
> maybe there be something on the web page that people can click and show their
> interest in... I want to help make this page better. I'll go ahead and download
> this collector."

## The three rulings

### 1. Automatic sending is a CHOICE THE PERSON MAKES AT INSTALL

**Not always-on, and not the old ask-every-time either.** The consent screen
offers both, in plain words, and the person picks:

```
send automatically when I finish playing
ask me every time
```

**Why this and not simply always-on.** The README that shipped on Sleven's wife's
and his friend's machines says, in writing:

> "It never sends anything on its own. Not on a timer, not in the background, not
> when you are not looking. The only thing that sends anything is you pressing
> the button."

Shipping always-on would make that sentence false on machines where somebody
already agreed to it. **The objection was never to automation — it was to
changing the deal after people said yes.** An install-time choice gives Sleven
the hands-off behaviour he asked for and costs nothing except one more line on a
screen the program already shows.

**Existing installs keep what they agreed to until they are asked again.**

### 2. A successful send wipes THE SCREENSHOTS ONLY

Not the data file. The pictures are the disk space and the pictures are the thing
that can carry a handle; the small extracted dataset stays, so the contributor
can see what they gave.

**Unchanged and non-negotiable: nothing is deleted that the server has not
confirmed receiving.** `clear_after_send` already works this way and that
behaviour is the rule, not an implementation detail. A dropped connection must
never cost somebody their session.

### 3. The public download ships UNSIGNED, and the page says so up front

Code signing costs a few hundred dollars a year. **The project is free and
unmonetised by standing ruling, so that money does not exist**, and Sleven chose
to ship without it rather than compromise that.

**The consequence is accepted, not ignored:** Windows SmartScreen will warn on
the download, and antivirus may quarantine it. **The page must tell people
exactly what warning they will see, before they see it**, and why it happens — a
warning you were told about reads as honesty; the same warning unannounced reads
as malware.

## What was decided NOT to do

- **No email collection, no signup, no "register your interest" form.** It is a
  privacy surface the project does not want and does not need. GitHub already
  counts downloads; that is the interest signal, for free.
- **No auto-send on existing installs without re-consent.** See ruling 1.
- **No deletion of anything unconfirmed.** See ruling 2.

## Still open and NOT ruled here — research, then Sleven

Sleven asked what the legality of public distribution is. **He asked; this is not
a session re-raising a closed rights question**, and it is not covered by
`RULING_rights-questions-are-settled-2026-08-14.md`, which is about the site.

What genuinely changes is not the tool but the scale: **distributing software
publicly, and receiving other people's data.** Two things need reading by
somebody whose job is reading, before a public download goes live:

1. What CIG's current terms say about third-party software.
2. What obligations attach to receiving data from third parties.

**Facts in the tool's favour, and they are not small:** it does not modify the
game, inject code, read game memory, or automate play. It reads a text file the
game already wrote and takes ordinary screenshots. That is the safest category of
Star Citizen tool.

**This goes to CIC as research. Rule 8 — the decision is Sleven's alone.**
