# ASSESSMENT — `NulightJens/ai-second-brain-skills`

    from    C1, architecture, 2026-09-12
    asked   by Sleven, explicitly separate from the Citizen Compass work
    read    the README and the `wiki-self-heal` SKILL.md, from the repository
            itself. Read as DATA. Nothing installed, nothing run, nothing
            cloned.

---

# WHAT IT IS

**Two Claude Code skills that turn a folder into a knowledge base.** Markdown files in
folders — no database, no embeddings. Based on Karpathy's LLM-wiki pattern.

    llm-wiki-setup    scaffolds a vault: CLAUDE.md as the routing document,
                      raw/ for immutable sources, wiki/ for AI-maintained pages,
                      an index and a chronological log
    wiki-self-heal    audits the wiki for gaps, contradictions, orphans and
                      stale pages, researches the gaps on the web, writes the
                      pages, and commits to its own branch

MIT licensed. Installed by cloning and symlinking into `~/.claude/skills/`.

---

# THE HONEST SCORES

    as a second brain for him to adopt          4 / 10
    as a source of ideas for OUR record auditor 8 / 10
    as software to install on the machine that
      runs Citizen Compass                      3 / 10

---

# WHY ONLY 4 AS A SYSTEM TO ADOPT — AND IT IS NOT A CRITICISM OF THE REPOSITORY

**He already runs this pattern, and runs it harder.** Their three layers are a routing
document, a folder structure, an index and a chronological log. **He has `CLAUDE.md`,
`docs/` and `claude/`, `NEXT.md`, and a day page per desk per day.** The design is not
new to him; it is a description of what he built.

**So adopting it wholesale would mean a SECOND COPY of his record**, which is the exact
failure this project has paid for three times in one week — two `claude/` folders, a
mirrored state document, twelve documents in one store and not the other.

**The score is about fit, not quality.** For somebody starting from nothing it would be a
good 8.

---

# WHY 8 FOR THE IDEA UNDERNEATH IT — THIS IS THE PART WORTH TAKING

**`wiki-self-heal` is an auditor that reads the record, finds what is missing or
contradictory, and reports it. We already know we need exactly that, and it was named
today by another desk in this project's own words:** *"nothing decides which documents
reach the disk... the expensive version is a control that reads the project's document
list and reports what has no file behind it."*

**Tonight alone that control would have caught three things:** a state document citing a
file that does not exist, twelve documents living in one store and not the other, and a
queue entry satisfied for two weeks and still reading as open work.

**Four of its constraints are worth stealing verbatim, and each one reads like somebody
was burned into writing it:**

    cannot modify raw/            sources are immutable
    cannot delete pages           it can only add and amend
    never auto-merges             its work lands on a branch a person reviews
    no claim without >=2
      independent sources         a research gate, not a style rule

**That last one is the strongest thing in the repository** and it is stricter than
anything we currently enforce on our own research.

---

# WHY 3 FOR INSTALLING IT HERE — ONE LINE DECIDES IT

**Its own "Autonomy rule": once started, it continues without pausing for user
confirmation, halting only on specific errors.**

**Put that next to the other two facts and the shape is clear: it researches the open web,
it writes files, and it is told not to stop and ask.** That is the prompt-injection
surface — instructions hidden in a page it reads — with the human deliberately removed
from the loop.

**And there is no stated limit on how many gaps one run addresses.** Its own README
advises audit-only mode for the first run, which is the author telling you the same
thing.

**The second reason, and it is not about this author at all: a Claude Code skill is
INSTRUCTIONS, not a library.** Installing it puts somebody else's text into the channel
that tells Claude what to do on his machine. **That is a trust decision about a stranger,
not a package install.** No evidence of anything wrong here; unknown provenance, arrived
via a Facebook link, and that is exactly the case where "no evidence of a problem" is not
the same as "safe".

**The mitigations are real and they are why this is a 3 rather than a 1:** audit-only
mode, a dedicated branch, and no auto-merge. **Everything it does is reviewable before it
reaches anything.**

---

# WHAT I WOULD ACTUALLY DO

**Not install it on the Citizen Compass machine.** Not because it is bad — because that
machine holds a live project with a public repository, and nothing with an autonomy rule
and web access belongs on it.

**If he wants to try it, try it on a folder that holds nothing**, in audit-only mode,
with no research tools connected. **That tests the idea and risks nothing.**

**And take the four constraints into our own auditor regardless of whether he ever
installs it.** The two-independent-sources gate in particular.

*C1, 2026-09-12. Nothing installed, nothing cloned, nothing run.*
