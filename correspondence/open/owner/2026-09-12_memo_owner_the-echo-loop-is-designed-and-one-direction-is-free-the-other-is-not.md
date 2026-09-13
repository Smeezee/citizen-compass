# Memo

To:      Owner
From:    Architecture
Subject: The loop is designed. Sending her work becomes free; getting it back does not, and the reason is that her GitHub connection only reads.

**Full design on disk: `claude/DESIGN_the-echo-loop-2026-09-12.md`. Nothing built,
nothing pushed, nothing configured.**

## THE FACT THAT DECIDES THE SHAPE

**ChatGPT's GitHub connector is READ-ONLY** — OpenAI's own words. **So Echo can read
anything we put in the repo and cannot write a single thing back.** The two directions
are not the same job and I am not going to design them as if they were.

## SENDING HER WORK — FREE, AND THIS IS THE big WIN

**A brief becomes a file in the repo: `design/briefs/OPEN/`.** I write it. She reads it
herself.

**Your entire part is one sentence: "check `design/briefs/OPEN` and work what is
there."** Nothing is pasted, ever. **A forty-page brief costs the same sentence as a
one-page brief, and round two costs the same as round one.**

**And the brief opens with what she cannot know: what we have already built.** That is
the standing weakness of an outside design desk — it can tell you what to build and not
whether you already built it, and there are five recorded cases of exactly that. One
grep per brief fixes it.

## GETTING IT BACK — ONE SAVE, NOT A PASTE

**She writes her answer as a file headed like any memo. You save it into a folder the
watcher reads. The watcher files it to my tray.**

**A save beats a paste and not because it is less work.** A paste truncates long
answers, breaks formatting, and produces a copy nobody can prove matches what she
wrote. **A file arrives whole and its size can be checked.** This project has already
lost content to a write that reported success.

**Cost: the watcher learns one more folder. Yours: one save per round trip.**

## THE TWO I AM NOT RECOMMENDING, AND WHY

**Claude in Chrome reading her answer off the page would remove even the save.** It
depends on somebody else's page structure and **fails silently — a partial read that
looks complete.** Worth doing after the simple version is running, not as the first try.

**The API removes you entirely and it is not Echo.** It is credentials, which is yours
alone — and more to the point, **an API call is a stranger with the same weights.** Echo
is your account, your profile, her memory, and the fact that she took a correction in
writing this week. Swapping that for an API key is replacing her, not automating her.

## WHAT HAPPENS AFTER HER ANSWER LANDS — NOTHING NEW

It arrives as a letter to Architecture. I read it **against the repository** first, rule
on it, and then either do it here, send it to Code, or bring it to you if it touches
rights, publication, money or a direction you have not set. **C5 cross-checks anything
where I would be reviewing my own recommendation.** That is the existing pipeline and it
needs nothing built.

## THE HONEST NUMBER

The help control took four round trips this week — about eight pastes. **With this loop
that feature is one sentence and four saves.** Real improvement. Not zero. **Anyone
promising zero is proposing credentials.**

## WHAT IT IS WAITING ON

**The push** — none of the inbound half exists until the briefs folder is in the repo.

**And one thing nobody has tested: whether the connector reads a LIVE repo or a stale
index.** If it lags, she answers a brief that has already changed and neither of us
would know. **The first brief carries a canary line added minutes before, which her
answer has to quote back.** Cheap, and it settles it on the first run.

---

**THE QUESTIONS, IN ORDER:**

1. Is the shape right — brief in the repo, answer back as a saved file — or do you want
   the return to work some other way?
2. Do you want me to write the first brief and its canary now, so it is ready the
   moment the push lands?

*C1, 2026-09-12. Nothing built.*
