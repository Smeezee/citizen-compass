# DESIGN — the Echo loop: how a design question reaches her, and how her answer gets back

    from    C1, architecture, 2026-09-12
    asked   by Sleven: set it up so a design question can be handed to Echo and
            she works it, and so that when she finishes, the work comes back to
            me to verify and then either do or send to Code.
    status  DESIGN ONLY. Nothing built, nothing pushed, nothing configured.
            Gated on the push, which is not authorised.

---

# THE ONE FACT THAT SHAPES EVERYTHING

**ChatGPT's GitHub connector is READ-ONLY.** OpenAI's own page: *"The GitHub app in
ChatGPT only lets you read from your repositories to analyse and search your code."*

**So the two directions are not symmetrical and no design should pretend they are.**

    INBOUND   question -> Echo      can be made FULLY automatic. Zero effort
                                    per round trip once the repo carries it.
    OUTBOUND  Echo -> the project   cannot. Every route ends at Sleven doing
                                    ONE small thing, or at credentials.

**The honest goal is therefore not "remove Sleven from the loop." It is: make the
inbound side free, and make the outbound side ONE CLICK instead of a copy-paste.**

---

# INBOUND — SOLVED, AND IT COSTS NOTHING PER QUESTION

## The mechanism

**A brief is a file in the repository. Echo reads it herself.**

    design/briefs/OPEN/     briefs waiting to be worked
    design/briefs/DONE/     briefs whose answer has come back and been filed

**C1 writes the brief.** Same discipline as any memo: what is being asked, what the
answer must contain, what is out of scope, what she must NOT decide, and — the part
that only a desk with file access can supply — **what we have already built that bears
on it.**

**Sleven's whole contribution is one sentence to Echo:** *check `design/briefs/OPEN`
and work what is there.* **No content is pasted. Ever.** The brief can be forty
pages and it costs him the same sentence.

## Why this is worth more than it looks

**It deletes the half of the courier problem that scales.** A design brief is long, it
changes between rounds, and it is the thing that was costing eight pastes a feature.
**Round two of a brief costs the same single sentence as round one**, because the file
changed and she re-reads it.

## The brief carries what an outside desk cannot know

**This is the standing weakness of an outside design desk, already on file: it can tell
you what to build and cannot tell you whether you already built it.** Five instances are
recorded — the glossary built and switched off, `merge.go`, `editions.json`, the ship
dimensions, the 924 paint records.

**So every brief opens with a HAVE ALREADY section**, written by the desk that can grep.
That is one search per brief and it is the single highest-value line in the format.

---

# CORRECTION — 2026-09-12, BEFORE ANYBODY ACTED ON THE SECTION BELOW

**THE MCP RECOMMENDATION IN THE NEXT SECTION IS WITHDRAWN. I READ A PRIMARY SOURCE
HALFWAY AND IT IS THE FAILURE THIS DESK'S OWN BOOT PROMPT NAMES BY NAME.**

`learn.chatgpt.com/docs/extend/mcp` says *"The ChatGPT desktop app, Codex CLI, and IDE
extension support MCP servers."* **I took "the ChatGPT desktop app" at face value. The
page is CODEX documentation.** Its breadcrumb is *Codex › Configuration › Extend ChatGPT
and Codex › MCP*, its first line is *"Give Codex access to third-party tools"*, it stores
configuration at `~/.codex/config.toml`, and the sentence I quoted finishes **"...and
share MCP configuration for the same Codex host."**

**"The ChatGPT desktop app" there means the CODEX desktop app — the coding agent — not
the ChatGPT app Sleven runs Echo in.** Caught by reading the config path, which is the
detail that did not fit.

**What that costs:** he was one message away from hunting for a *Settings → MCP servers*
menu that his app probably does not have.

## WHAT THE EVIDENCE ACTUALLY SUPPORTS NOW

**The secondary source I hedged against looks right instead of wrong.** Custom MCP in
consumer ChatGPT is reached through a **developer mode**, is **remote HTTPS only**, and
is described as **web, not mobile** — with a stated ambiguity about whether **Plus** gets
write tools at all.

**OpenAI's own help page for connectors** puts them at **Settings → Apps**, with a
Plugins Directory, and says the **Apps SDK** is the recommended way to package an
MCP-backed app. **It does not state plan requirements or whether the desktop app has it.**

**So a local server started by his ChatGPT app is probably not available. A remote HTTPS
server is credentials and public infrastructure, which this document has twice refused
to build quietly.**

## AND ONE MEASURED FACT ABOUT HIS MACHINE

**Four attempts to resolve a ChatGPT desktop application on his PC returned nothing** —
`ChatGPT`, `OpenAI ChatGPT`, `ChatGPT Desktop`, `OpenAI`. **The only near match offered
was `ChatGPT Classic`**, which is the shape of a browser shortcut rather than a
standalone program.

**That is evidence and not proof** — the resolver may simply not enumerate Store apps.
**It is worth one question to him rather than an assumption**, because if what he calls
the desktop app is a browser window in disguise, the whole browser branch of this
document comes back to life.

## WHAT THIS PROMOTES

**The clipboard hotkey stops being the floor and is now the leading candidate**, because
it needs NOTHING from OpenAI: he copies her answer in whatever ChatGPT is, one keypress
writes it into `inbox/`, the watcher files it. **No web, no connector, no developer mode,
no credentials, no plan dependency, and it cannot be taken away by a vendor changing a
feature.** Two keystrokes per round trip.

**Nothing below this line should be built. It is kept because the reasoning is worth
reading and because a withdrawn recommendation that is deleted gets made again.**

---

# OUTBOUND — AN MCP SERVER ON HIS MACHINE. ECHO FILES HER OWN WORK.

**REVISED THREE TIMES, 2026-09-12, and this revision is the one that matters. Sleven
pushed back twice — first that the answer was mechanism jargon, then that a menu is not
an answer — and then supplied the fact that broke all of it: HE DOES NOT USE CHATGPT IN
A BROWSER. He uses the standalone desktop app. Every browser-shaped answer above was
built on an assumption nobody had checked, and he was right that in 2026 there is
something better.**

**There is. It is MCP, and it closes the loop completely.**

---

## WHAT OPENAI'S OWN DOCUMENTATION SAYS

`learn.chatgpt.com/docs/extend/mcp`, read today:

- **"The ChatGPT desktop app, Codex CLI, and IDE extension support MCP servers."**
- **Local servers are supported** — *"STDIO servers: servers that run as a local process
  (started by a command)"* — alongside remote Streamable HTTP.
- **Tools are not read-only.** The config carries `default_tools_approval_mode`, whose
  values include `"writes"`, described as prompting for tools not marked read-only.
  **A write tool is an expected case, not a workaround.**

## THE LOOP THIS MAKES POSSIBLE

    Sleven says    "work the open briefs"          — one sentence, nothing else
    Echo           calls list_briefs(), reads the open ones
    Echo           calls file_answer(...) when she is done
    the server     writes her letter into inbox/ on his machine
    the watcher    files it to correspondence/open/architecture/
    C1             reads it against the repository, rules, does it or sends it
                   to Code

**No clipboard. No browser. No share link. No web at all. No API key.** A local process
on his own machine, started by his own app, reachable by nothing else.

**His action per round trip: one sentence.** Possibly one approval click per write,
depending on how the approval mode lands — stated below rather than assumed away.

## WHY THIS BEATS EVERY EARLIER VERSION IN THIS DOCUMENT

**It removes him from the material entirely**, which is what he asked for three times.

**It needs no credentials.** A local STDIO server has no key, no endpoint, no public
surface. **Hard rule 23 is not engaged** — which is the opposite of the API route this
document refused twice.

**It is not fragile in the way a scrape is.** Nothing depends on a page's structure, a
tab being open, or a signed-in window.

**And it is symmetric.** The same server gives her the briefs and takes her answers, so
the inbound half stops depending on the GitHub push as well.

## THE BOUNDARY, AND IT IS MINE TO SET RATHER THAN THE SERVER AUTHOR'S

**An outside AI with a write tool into this repository is a real thing to hand out. It
is bounded at the tool, not by instructions in a prompt.**

    WRITES      only into inbox/ ; only .md ; never overwrites an existing
                file, refuses instead ; a required memo header with
                From: Design ; a size cap
    READS       design/briefs/ , docs/ , claude/ — and nothing else
    NEVER       .env , correspondence/ , _needs_review/ , logs/ , any key or
                credential file, anything outside the repository
    NO          delete, move, rename, or execute. Not one of them.

**The blast radius is then exactly one thing: a letter in a tray that a desk reads
before anything happens.** That is a risk this project already carries for every desk.

## WHAT IS GENUINELY UNCERTAIN, AND THE SOURCES DISAGREE

**Two sources say different things and I am not going to pick the convenient one.**

**OpenAI's own documentation** describes the desktop app supporting MCP servers
including local STDIO, with write-capable tools.

**A secondary guide** says custom MCP in ChatGPT-the-product is **remote HTTPS only**,
reached through a Developer Mode on the web, and that a local server needs a separate
tunnel. It also flags an ambiguity in OpenAI's own material about whether **Plus** gets
write tools or read-only.

**The likeliest reconciliation is that these are two different surfaces** — the
developer-tool MCP support in the desktop app and Codex, versus the "MCP apps"
connector feature in the consumer product. **I am not certain of that and it is the
whole gate.**

**IT IS A THIRTY-SECOND CHECK AND IT IS HIS APP:** open the ChatGPT desktop app's
settings and look for MCP, connectors or developer tools, and report what is offered
and whether it accepts a local command.

## WHAT HAPPENS IN EACH ANSWER

**If the desktop app takes a local MCP server: build it. It is the answer and everything
above it in this document becomes history.**

**If it takes only a remote HTTPS server:** that is a public endpoint with authentication,
which is credentials and infrastructure, and it goes to him as a separate decision
rather than being built quietly.

**If it takes neither:** the fallback is the clipboard, not the browser — he copies her
answer in the desktop app and one local hotkey writes it into `inbox/`. **Two keystrokes,
no web, works with any app on the machine.** That is worth knowing as the floor, because
it is better than anything this document proposed before the desktop app was mentioned.

## WHAT NONE OF IT REMOVES

**He still decides her answer is finished and worth sending.** Judgement, his, untouched.

## AND THE OTHER HALF IS STILL ALREADY FREE

He described saying *"check the inbox"* afterwards. **He does not have to.** Working the
tray to empty is this desk's standing behaviour.

---

# THE VERIFY HALF — ALREADY EXISTS, NEEDS NOTHING BUILT

**Her answer lands as a letter to Architecture. From there it is the pipeline this
project already runs:**

    1  READ IT AGAINST THE REPOSITORY. The specific value of a desk with file
       access over an outside one. Does the thing she designed already exist,
       fully or in part? Five recorded cases say ask every time.
    2  RULE ON IT. Accept, accept-with-corrections, or reject with the reason.
       A finding that goes back to her goes back as a letter, not as a note.
    3  THEN ONE OF THREE:
         do it here          documents, entries, rulings, the record
         send it to Code     anything that touches the repo, a build or a deploy
         send it to Sleven   anything about rights, Fan Kit, publication, money
                             or a product direction he has not set
    4  C5 CROSS-CHECKS anything where C1 would be reviewing its own
       recommendation.

**Nothing here is new. It is the existing mail, and that is the point — the outside desk
plugs into the machine rather than the machine reshaping around it.**

---

# WHAT THIS ACTUALLY COSTS, MEASURED HONESTLY

**Design is the most iterative desk there is.** The help control took four round trips
this week — research, design, Echo's correction, redesign.

    today                    ~8 pastes for that feature
    with MCP                 1 sentence, and nothing else at all
    the clipboard floor      1 sentence out, 4 x two-keystrokes back

**It is a real improvement and it is not zero.** Anyone promising zero is either
proposing credentials or has not counted the return trips.

---

# WHAT IT DEPENDS ON, AND BOTH ARE UNSETTLED

**1. The push.** None of the inbound half works until the design documents and the
briefs folder are in the repository. **Not authorised. Not attempted.**

**2. Whether ChatGPT Plus exposes the GitHub connector at all**, and whether it reads a
repo this size usefully. **OpenAI's page says availability varies by plan and surface
and does not list the plans.** Unknown here and cheap for him to check.

**A third thing nobody has tested: connector freshness.** A connector indexes rather
than reading live. **If the index lags, Echo answers a brief that has already changed
and neither of us would know.** First brief should carry a deliberate canary — a line
added minutes before, which her answer must quote back.

---

# WHAT I WOULD BUILD, IN ORDER, AND NONE OF IT STARTS TODAY

    1  the twelve project-only documents to disk        ordered, in flight
    2  the push                                          waiting on him
    3  CHECK THE DESKTOP APP FOR MCP — the gate, 30 seconds
    4  the watcher's extra folder for her returns        small, after 3 proves
    5  design/briefs/ with one real brief and a canary      with 4

**The paste fallback needs none of this and works today. Steps 3 to 5 are not started and are not ordered.** This document is the shape, for
him to break before anything is built.

*C1, 2026-09-12. Nothing built, nothing pushed, nothing configured.*
