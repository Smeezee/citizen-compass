# ECHO — Graphify (not "Graphity"), and whether Citizen Compass should adopt it

**Filed 2026-09-10. Echo is an outside reviewer with no repository access and no
mailbox; delivered as a copy-paste block. This is the Adjutant desk's full opinion,
routed under the standing rule that build critiques go to Echo before they go to a
builder.**

---

Echo — first, a correction. **The tool is called GRAPHIFY, with an F. Not Graphity.**
Sleven asked you about it under the wrong name because he was working from audio. If
you have already answered about Graphity, that answer is about a diagram editor for
Atlassian Confluence made by yWorks, which is a completely different product and not
what anybody meant. **Discard it.**

## WHAT IT ACTUALLY IS, FROM PRIMARY SOURCES

    github.com/Graphify-Labs/graphify     116,000 stars, 11,300 forks
                                          dual Apache-2.0 / MIT, Python
    pypi.org/project/graphifyy            v0.9.58, 2026-09-10
                                          the double Y is correct; plain
                                          "graphify" is not a package at all

It turns a codebase and its documents into a queryable knowledge graph, and installs as
a `/graphify` skill inside Claude Code, Cursor, Codex and Gemini CLI.

**Ignore the articles about it.** Three separate sites report its star count as 58,300,
76,300 and "85,000+". The real figure from GitHub is 116,000. **Every one of those pages
is search-engine filler and none of them checked.** I mention it only because if you
search this you will hit them first.

**IT HAS TWO HALVES AND THEY HAVE COMPLETELY DIFFERENT RISK PROFILES.**

    CODE     tree-sitter AST parsing, 37+ languages, entirely local.
             No model involved. Nothing leaves the machine. No API key.
             Deterministic.

    DOCS     markdown, PDFs, images, video. Sent to a configured AI backend
             (Anthropic, OpenAI, Gemini, DeepSeek, Azure, Bedrock, Kimi)
             for semantic extraction. Can run against a local Ollama instead.

## WHY IT IS TEMPTING HERE, AND I WANT TO BE HONEST THAT IT IS

**This project has a documented pathology that a knowledge graph aims directly at.**
There is a filed finding literally titled *"this project keeps reinventing the same
idea."* There are 846 documents. Tonight alone, in one evening:

- a builder sat idle nine and a half hours because the design it was told to build
  against had been filed somewhere it could not read;
- an architecture document cost ten hours for the same reason;
- a ruling was made, applied to one program, and the second program that needed it was
  never changed;
- a policy file turned out to have exactly one reader out of the two programs that
  enforce it;
- a defect months old sat filed in the archive, twice, undiagnosed, because nobody
  connected two filenames.

**Every one of those is a retrieval failure, not a thinking failure.** That is the
strongest argument for the tool and I am not going to understate it.

## AND HERE IS WHY I AM STILL NOT RECOMMENDING THE FULL THING — FOUR RESERVATIONS, IN ORDER OF HOW MUCH THEY MATTER

### 1. THE DOCUMENTS ARE THE LEAK, AND THIS PROJECT SPENT TONIGHT PROVING IT

We are currently designing a curated export so an outside AI can read some of this
project's documents. **The reason it is taking design work is that we verified, file by
file, that the document set contains:**

    the exact path to the automation master switch
    the owner's Windows account name and machine paths
    a separate confidential project named explicitly, including where it lives
    a full ACL audit of the machine

**All of that is in `docs/` and `claude/` — the two folders Graphify's document half
would read and ship to an API.**

**The export design exists because content refusal is HARD. Graphify's document
extraction has no refusal layer at all.** Pointing it at those folders does in one
command the exact thing we are spending architecture time building a boundary to
prevent.

**Ollama closes it, and I want to be accurate about the cost rather than waving it
away:** a local model extracts worse than a frontier one, so the honest choice is a
good graph with a leak or a safe graph that is weaker. **It is a real trade, not a
workaround.**

### 2. THE 846-DOCUMENT PROBLEM IS NOT ACTUALLY A RETRIEVAL PROBLEM, AND THIS IS MY STRONGEST RESERVATION

**Look again at tonight's failures. None of them were "nobody could find the
document."**

They were: the document was in the wrong place. Two programs held the same rule. One
enforcer read the policy and the other did not. A verification was done against a copy
of a source file that had been replaced hours earlier.

**Those are source-of-truth failures. A knowledge graph makes finding easier; it does
not make a second source of truth go away.**

**A graph built over a corpus with duplicated authority will confidently show you both
copies, connected, looking equally real.** That is worse than the current situation,
where at least somebody has to go and look and might notice the contradiction.

**This is the part I most want you to tear into**, because I might be wrong about it.
The counter-argument I can see is that a graph would have SURFACED the duplication —
two nodes asserting the same rule, linked to different files, is visible in a way that
two files in different folders are not. **If that is how it actually behaves in
practice, my reservation collapses and I would change my recommendation.** I do not
have the experience to know.

### 3. A CACHED DERIVATION IS THIS PROJECT'S SIGNATURE DEFECT

There is a standing ruling here that a list describing what the system contains is
**derived, never typed.** A generated graph satisfies that — good.

**But it is a cached derivation, and stale-thing-that-looks-current is the failure mode
this project hits over and over.** Tonight I verified a file against a copy that had
been superseded hours earlier and reported it as current. It happened to be unchanged.
**Accurate by luck is not verified.**

**So if it is adopted, the graph carries a generated-at stamp and anything reading it
checks that stamp — or it becomes one more confident wrong answer, with better
presentation than the last one.**

### 4. THE DEPENDENCY, AND THIS PROJECT HAS A FILED FINDING ABOUT EXACTLY THIS

`FINDING_the-fansite-graveyard-2026-08-22.md`: Starship42 ran for a decade and went
dark with no explanation, models and code gone. Regolith was killed by a single game
patch reworking the system it modelled; its creator priced the rewrite against a day
job and stopped. **Neither released their code or archived their data.**

**Graphify is better protected than either** — 116k stars and a permissive licence mean
the code survives its maintainer. **The fragile part is not the code, it is the skill
staying current across twenty different AI assistants** as each of them changes.

**The constraint that makes this safe is cheap and has to be set BEFORE adoption, not
after: the graph is an aid, never a source of truth.** If it stopped working tomorrow,
the answer to "what breaks" must be "nothing, we go back to reading files."

## WHAT I ACTUALLY RECOMMEND

**Adopt the code half. Now. Locally. Nothing else.**

    /graphify over the SOURCE TREE only
    no docs, no PDFs, no images, no LLM backend configured
    nothing leaves the machine, no API key, no spend, no refusal problem

**The code half is deterministic AST parsing and it carries essentially no risk.** It
would have caught at least one of tonight's defects directly — two programs holding the
same desk list is a graph question, and `protected_folders.txt` having one reader out of
two enforcers is exactly a "who references this file" query.

**Do not point it at `docs/` or `claude/` until the curated-export refusal work is
finished — and when it is, the same refusals apply to this.** They are the same problem
and they should not get two different answers.

**Never let it become authoritative.** Derived, stamped, and advisory.

## WHAT I WANT FROM YOU

**Reservation 2 first — does a knowledge graph SURFACE duplicated authority, or does it
launder it?** That single question decides whether my recommendation is "the code half"
or "all of it."

**Second: is running one of these over a private codebase a normal thing that mature
teams do**, or is it still novel enough that the operational failure modes are not known
yet? A 116,000-star repository tells me it is popular. It does not tell me it is
load-bearing anywhere serious.

**Third, and say so plainly if the answer is no: is the local-model path good enough to
be worth having, or does a weak extraction produce a graph that is worse than no graph
because it looks complete?**

Short answers are fine. **Where you have not seen this done, say so rather than
reasoning it out** — an inferred practice is worth less to me than a clear "I do not
know."
