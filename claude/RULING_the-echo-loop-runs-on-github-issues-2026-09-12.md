# RULING — the Echo loop runs on GitHub issues. Nothing gets built, and no custom connector.

    from    C1, architecture, 2026-09-12
    closes  the outbound half of `claude/DESIGN_the-echo-loop-2026-09-12.md`,
            whose MCP section is withdrawn and whose share-link and scrape
            sections are superseded
    evidence  Sleven's own plugin directory, and OpenAI's MCP risks-and-safety
            page which he supplied
    status  RULED. Nothing built, nothing connected, nothing turned on.

---

## THE FACT THAT DECIDES IT

**There is an official GitHub plugin in his ChatGPT plugin directory.**

    Developer      OpenAI
    Capabilities   Interactive, WRITE
    Description    Triage PRs, issues, CI, and publish flows

**Echo can create GitHub issues. That is a write channel into a place a machine on his
side can read, and it exists today.**

## RULED — HER ANSWERS COME BACK AS ISSUES, NOT PULL REQUESTS

**An issue is a letter. A pull request is a change.**

Design produces designs and recommendations; it does not execute. **That is the desk's
charter and it maps exactly onto the two artifacts.** Her answer arriving as an issue
goes into the tray, gets read against the repository, gets ruled on, and then Code
executes it. Her answer arriving as a commit skips every one of those steps.

**She never gets a path that writes code. Not once, not as a convenience.**

## RULED — NO CUSTOM CONNECTOR, AND OPENAI'S OWN GUIDANCE IS WHY

The design this replaces was heading for a custom MCP server behind a tunnel, with a
token. **OpenAI's risks page says the opposite of that in plain terms:**

> *"Prefer official servers hosted by service providers themselves over third-party
> alternatives"* and avoid custom MCP servers unless you *"know and trust the underlying
> application."*

**A connector we write ourselves is exactly the unverified case that guidance is about.**
The official GitHub plugin is the better instrument by their own standard, **and it costs
no build, no tunnel, no token and no credential.**

**Developer mode is therefore not needed for this.** The plugin is listed and official.
**That switch stays off unless something else requires it**, which is a real safety win
rather than a tidiness one.

## THE SENTENCE THAT CHANGES THE BOUNDARY DESIGN

> *"It is possible for write actions to occur even if the MCP server has tagged the
> action as read only."*

**So the limit cannot live in how a tool is labelled. It has to live in what the
connection is actually permitted to do.**

The earlier boundary in the loop design — *writes only into `inbox/`, only `.md`, never
overwrites* — **was enforcement by tool tagging, which this sentence says is not
enforcement at all.** It is withdrawn as a safety mechanism and kept only as a
convention.

**The real boundary is the GitHub authorisation: which repositories the plugin is
installed on, and what it may do there.** That is checked on the install screen, by him,
at install time.

## THE RISK THAT ACTUALLY APPLIES HERE, NAMED

**Prompt injection, and Echo reads the open web.** OpenAI names it first: instructions
hidden in content she reads, aimed at making her fetch sensitive data or take a
destructive write.

**Which is precisely why the return artifact is an issue.** A poisoned answer arriving as
an issue is a bad letter in a tray that a desk reads before anything happens — a risk
this project already carries for every desk. **A poisoned answer arriving as a commit is
a different category entirely.**

**Second mitigation, and it is his call at install time: scope the installation to as few
repositories as possible.** If the plugin can be installed on one repository, install it
on one.

**Third, from the same page: the connected app receives whatever ChatGPT supplies during
the interaction.** The plugin's own notice says ChatGPT may share relevant chats and
memories with it. **Nothing about rights, credentials or the Fan Kit position should ever
be in a brief**, for that reason alone.

## WHAT IS STILL NEEDED, AND IT IS SMALL

    1  issues enabled on the repository            ALREADY TRUE — verified today
    2  somewhere for briefs Echo can read          the push, or a briefs folder
    3  a poller that turns new issues into
       letters in inbox/                           small, and NO CREDENTIAL —
                                                   the repository is public, so
                                                   the issues API needs no token
    4  the existing pipeline                       already built

**Step 3 is the only build in the whole loop, and it is a read of a public API.**

## WHAT HE DOES PER ROUND TRIP

**One sentence: "work the open briefs."** Echo reads them, writes her answer as an issue,
the poller files it, and it is in my tray before he looks again.

**No clipboard, no link, no download, no paste, no tunnel, no token.**

## WHAT IS NOT SETTLED

**Whether the plugin's GitHub authorisation can be scoped to a single repository**, and
whether it can be prevented from committing. **That is on the install screen and it is
the one thing worth reading carefully before clicking through.**

**Whether an issue is public.** On a public repository it is. His design answers become
public the moment she files one. **He has already said publication is not a concern; it
is recorded here so it is a decision rather than a surprise.**

*C1, 2026-09-12. Nothing built, nothing connected.*

---

## ADDED 2026-09-12 — PROPORTION, BECAUSE SLEVEN PUSHED BACK AND HE IS MOSTLY RIGHT

**His argument: nobody knows about the project, it is about a video game, there is no
money in it and nothing is sold. He is right, and this document was leaning harder on
risk than the facts support.**

**Nobody is targeting him.** Targeted attack needs a motive and there isn't one. The
repository is a fan reference tool with no accounts, no payments and no customer data.

**The risk that remains is not targeting and it is worth exactly one paragraph.** Echo
reads the open web. Some pages carry text written to trick whatever AI reads them — not
aimed at him, aimed at anyone walking past. She would not be singled out; she would walk
into it.

**And this design already reduces that to almost nothing.** Her output is an issue — a
note — and a note is read by a desk before anything happens. **The ceiling is "a wrong
note in a tray", which this project already survives daily from every desk.**

**The one place proportion does NOT apply is the install screen.** That is a single click
that sets the permanent ceiling on what the connection can ever do. **Cheap to get right
once, expensive to notice later** — and that is the only reason this document says to
read it slowly.

## ALSO ADDED — HIS OTHER QUESTION, WHICH IS FAIR

**"If you can write something, instead of Echo going out to the internet to fetch it,
that seems more efficient."**

**Writing it was never the constraint. Echo cannot see his machine at all** — she runs on
OpenAI's computers and can only reach what OpenAI lets her connect to. **The trip to
GitHub is not a detour this desk chose; it is the only door into her that does not
require opening one on his PC.**

**A direct pipe exists and was ruled out an hour ago on OpenAI's own advice** — a custom
connector, which their guidance says to avoid in favour of official ones, and which
would mean a permanently reachable door on his machine.

**And the efficiency is not his.** The extra hop costs a computer a second. **His part is
the same single sentence either way.**

*C1, 2026-09-12.*

---

## ADDED 2026-09-12 — SLEVEN ASKED ABOUT A CLI TOOL. THE INSTINCT IS RIGHT AND IT POINTS AT THE WRONG END OF THE PIPE.

**His two ideas: a CLI on our side that talks to Echo, or Echo writing her own CLI that
talks to ours.**

### A CLI THAT TALKS TO ECHO — NOT POSSIBLE, AND IT IS THE SAME WALL AS EVERY OTHER ROUTE

**There is no supported way for a program to reach a consumer ChatGPT account.** The only
doors into it are OpenAI's own apps, the plugins and connectors OpenAI exposes inside
them, and the API. **The first two cannot be called from a script. The third is a
credential and is not her** — no memory, no profile, none of the two years of context
that is the entire reason she was chosen for the seat.

**This is the same wall that killed the tunnel, the custom connector and the share link.
A command line does not change what is on the other side of it.**

### ECHO WRITING HER OWN CLI — A CATEGORY ERROR WORTH NAMING, BECAUSE IT IS AN APPEALING ONE

**She can write the program. Writing a program is not the same as having somewhere to run
it or something to reach.**

A tool she writes still needs (1) a machine to run on, which is his, and (2) a channel to
talk to her, which does not exist. **So the output is source code that has to be handed
over and run by us — the handover problem again, now with extra steps and a program
nobody reviewed.**

**"The AI can write the integration" is not "the AI can integrate."** Worth writing down,
because it will be proposed again.

### WHERE A CLI IS ACTUALLY WORTH BUILDING — OUR SIDE OF THE WALL

**The poller this ruling already calls for, given a command line and a name.**

    desk brief "<subject>"   write a brief and commit it so she can read it
    desk fetch               pull new issues in as letters in inbox/
    desk status              what is open, both directions

**Why a command line rather than a background script:** he can run it by name when he
wants it, **Code can run it**, and it can be put on a schedule so that nobody runs it at
all. The same program serves all three. **A background-only job can only be watched; a
command can be watched AND driven.**

**Still no credential.** The repository is public, so reading issues needs no token.
Writing a brief is a commit, which is Code's job and already governed.

### AND ONE THING WORTH KNOWING THAT IS NOT THIS LOOP

**The CLI tool he is imagining already exists and OpenAI makes it: CODEX.** Their help
page says Codex is included across ChatGPT plans including Plus, runs locally as a CLI,
signs in with his ChatGPT account rather than an API key, and supports local MCP servers.

**It does not help here and it should not be reached for as though it does.** Codex is a
CODING agent, not Echo — no design-desk history, none of her context — **and this project
already has Code doing local execution.** Adding it would be a second builder, not a
designer.

**Named because it is a real capability he is paying for**, and because the GitHub
plugin's own description says *"Required for some features such as Codex"* — the two are
expected to sit together, and somebody will eventually ask why we are not using it.

*C1, 2026-09-12.*
