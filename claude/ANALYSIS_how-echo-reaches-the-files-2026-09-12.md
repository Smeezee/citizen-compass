# ANALYSIS — every way Echo can reach the Design desk's files, rated

    from    C1, architecture, 2026-09-12
    asked   by Sleven: is there any way for ChatGPT to reach the files without a
            public push — and he adds that he does not object to publishing,
            because the project is already open source and nothing is secret.
    status  READ-ONLY. Nothing pushed, moved, uploaded or changed.

---

# THE REFRAME, BECAUSE THE QUESTION AS ASKED HAS A CHEAP ANSWER AND A WRONG ONE

**Yes, there are four other ways. Three of them are worse than the push, and the
reason is the same in all three: they make a SECOND COPY of the documents.**

**This project has paid for a second copy three times in the last week.** Two `claude/`
folders on two machines, and a roles file that existed in one and not the other,
blocked a job for hours. A mirror of `CURRENT-STATE.md` that had to be labelled as a
mirror so nobody edited the wrong one. And the thing this whole question comes from —
documents that live in the claude.ai project and not on disk, which cost two desks
nine and a half hours.

**So the test is not "can Echo read a file". It is:**

    1  does Echo get the file
    2  does she get the CURRENT one, without Sleven carrying it
    3  is there exactly ONE copy that is the real one
    4  does it still work in a month

**Every option below is scored on those four, not on convenience.**

---

# OPTION A — PUSH TO THE EXISTING PUBLIC REPO. **9/10**

One repo, one copy, raw URLs, no account, no connector, works in every AI tool he will
ever use, and every future commit updates it automatically.

**What it costs.** Permanent public history — a later delete does not remove it. For
design documents about a fan site whose source is already public, that cost is close
to zero, and **he has said plainly he does not object.**

**Why it is not 10.** It publishes before the rule that keeps it working exists — see
the last section. A push today with nothing behind it leaves the project in the same
place in a fortnight.

# OPTION B — A SECOND, PRIVATE GITHUB REPO + ChatGPT's GITHUB CONNECTOR. **5/10**

**It genuinely works and it is not public.** OpenAI's own documentation says the GitHub
connector reads private repositories, is READ-ONLY, and that availability "varies by
plan, workspace and product surface" — some plans get it only in deep research or agent
mode rather than normal chat. **He is on Plus, and I do not know whether Plus exposes
it in ordinary chat. That is a 60-second check in his Settings, not something I should
guess at.**

**Why it is only a 5 despite working: it is the second copy, by construction.** A
design document would then live in `citizen-compass` and in `citizen-compass-design`,
and nothing keeps them equal. **The first time one is edited in one place, the project
has the two-`claude/`-folders problem again, deliberately this time.**

# OPTION C — MAKE THE EXISTING REPO PRIVATE, AND CONNECT IT. **6/10**

**The cleanest non-public answer, and nobody has proposed it.** One repo, one copy,
nothing published, and the connector reads it.

**It does not break the site.** The public site is served from Netlify and uploaded by
hand, not from GitHub Pages — so repository visibility does not touch what visitors
see. **I checked that rather than assuming it.**

**Why not higher: it trades away something he values to solve a problem he says he does
not have.** He has just said the project is open source and nothing is secret. Going
private to enable one reader inverts that, and it also removes the repo from anyone who
reads it today. **It is the right answer only if the answer to the publication question
is no.**

# OPTION D — DROPBOX OR GOOGLE DRIVE CONNECTOR. **3/10**

**Two problems, and the first may be fatal.** OpenAI's Drive/Dropbox/Box/SharePoint
connectors were announced for **Pro**; he is on **Plus**. **And there is no Dropbox,
OneDrive or Google Drive folder in his home directory** — I listed it. If no desktop
client is syncing, nothing on his machine can put a file into Dropbox automatically,
and this desk has no Dropbox tool at all.

**Even if both were solved it is still the second copy**, now with a sync client in the
middle of it.

# OPTION E — UPLOAD THE FILES INTO A ChatGPT PROJECT. **4/10 as the channel, 8/10 as the first step**

**Works today, on Plus, with no publication, and it persists across chats** rather than
dying with one conversation. **There is already a folder called `ChatGPT project` in
his home directory**, so this is a route he has used before.

**Why it fails as the standing channel: it is stale the moment a document changes, and
he is the one who has to re-upload it.** That is the courier pattern his own standing
rule exists to delete — *"I should never have to say the word."*

**Why it is an 8 as a FIRST step: it is the only option that can deliver the twelve
project-only documents today**, because those are not on disk and no push can reach
them.

# OPTION F — PASSWORD-GATED PAGE ON THE TESTING SITE. **2/10**

Publishes anyway, just behind a password, and puts internal design doctrine inside the
product's own deployment. Mixes two things that should never share a pipeline.

# OPTION G — A SECRET GITHUB GIST. **2/10**

Unlisted is not private — anyone with the URL reads it. **Pays the publication cost
without getting the benefits**, and it is a second copy with no history worth having.

---

# WHAT I WOULD ACTUALLY DO, IN ORDER

**STEP 1 — GET THE TWELVE PROJECT-ONLY DOCUMENTS ONTO DISK FIRST. Needs nobody.**

No channel can deliver them until they exist as files. The Ten Eyes design, its
verification, the Sixty Angles doctrine, all three overlay findings, the wall spec and
five more. **This is the Design desk's own work, it has already been sized as an
afternoon by the desk itself, and each one has to be read for withdrawn claims before
it is copied** — two of the five copied this morning needed correction blocks on the
way across. **Ordered.**

**STEP 2 — ONE PUSH. Needs his word and only his word.**

Everything from step 1, plus the sixteen `docs/` files, the whole `design/` folder
including the Keyboard First prototype, and the standing pack. One commit, documents
only, run by Code.

**STEP 3 — THE RULE, BECAUSE OTHERWISE THIS RECURS IN A FORTNIGHT. Needs a decision, not a push.**

**The Design desk's own audit named the real defect this morning and it is not that
twenty files are unpushed:** *"nothing decides which documents reach the disk. It has
been a per-document judgement call for two weeks and it has been inconsistent for two
weeks. A rule that lives in somebody's habit is not a rule."*

**Its cheap version is a habit and will fail the same way. Its expensive version is a
control that reads the claude.ai project's document list and reports which entries have
no file behind them.** That control is the difference between Echo having access today
and Echo having access in November.

---

# THE HONEST SUMMARY

**Alternatives exist. Option C is the best of them and Option B is the most likely to
be reached for.** Both solve privacy and both cost the one property that actually
matters here, which is a single authoritative copy.

**Given he has said publication is not a concern, Option A is right — not because it is
easiest, but because it is the only one that leaves one copy in one place.** The reason
to hesitate is not privacy. It is that a push without step 3 behind it is a favour
rather than a fix.

---

# WHAT I CHECKED AND WHAT I AM UNSURE OF

**CHECKED.** OpenAI's own help page on the GitHub connector — private repos yes,
read-only yes, availability varies by plan and surface. His home directory listed: no
Dropbox, OneDrive or Google Drive folder; a `ChatGPT project` folder is present. The
repository's visibility, default branch and last commit read directly. That the live
site is a Netlify hand-upload rather than GitHub Pages.

**UNSURE, AND SAYING SO RATHER THAN GUESSING.** Whether ChatGPT **Plus** exposes the
GitHub connector in ordinary chat or only in deep research — OpenAI's page says it
varies and does not enumerate plans. **He can settle it in under a minute in Settings →
Connectors, and the answer changes which of B and C is even on the table.** Whether the
Drive/Dropbox connectors have reached Plus since they launched on Pro. Whether the
connector indexes markdown well enough to be useful on a repo this size — nobody here
has tested it.

*C1, 2026-09-12. Nothing pushed, nothing uploaded, nothing changed.*
