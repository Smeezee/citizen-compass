# RESEARCH — Graphify hosted vs local, and why the hosted account is not needed

**Filed 2026-09-10 by the Adjutant desk. Research only. Nothing installed, nothing
uploaded, no account changed.**

---

## THE ANSWER, BEFORE THE DETAIL

**The open-source install runs its own MCP server, on this machine, with no API key, no
account, and no network access. It exposes ten tools including natural-language search
over the graph.**

**That is the entire thing the Owner wanted, with none of the upload, none of the
credits, and no third party involved.** The hosted account is not needed and should not
be fed.

From the project's own MCP documentation:

    python -m graphify.serve graphify-out/graph.json

> *"No network access or external authentication is required for local operation."*

It registers with Claude Code through a `.mcp.json` in the project root, or `graphify
install` wires it in automatically. **A desk then asks the graph a question instead of
opening thirty files — which is the efficiency claim, delivered locally.**

**The ten tools:** natural-language search, inspect a node, explore neighbours, trace
paths between nodes, examine communities, identify core abstractions, statistics, open
pull-request impact, plus documentation and report resources.

## WHAT THE HOSTED SERVICE ADDS, AND IT IS NOT MUCH FOR ONE PERSON

    keeps the graph built and current in the cloud
    a web console, versions, build history, logs
    a shared endpoint for a team

**All three are team features.** For a solo operator on one machine, the local server
does the same job and the graph is already on the disk the desks read.

## AND A DISCREPANCY THAT IS REASON ENOUGH TO HOLD

**The project is real, active and single-authored, and that part checks out.**

    Graphify-Labs/graphify   117,000 stars   11,300 forks   394 watching
                             1,705 commits   206 tags
                             last release 0.9.58, committed SEVEN HOURS AGO
                             by safishamsi, who is the maintainer
                             Apache-2.0 AND MIT

**So the earlier "two different parties" reading was wrong and is withdrawn.** One
maintainer, one repository, genuinely and currently active.

**WHAT DOES NOT RESOLVE IS WHICH HOSTED DOMAIN IS THE ONE TO TRUST.**

    the repository's own About box links   www.graphify.com
    graphify.com describes the hosted app as   app.graphify.com
    the account was created on               app.graphify.net

**The repository points at `.com`. It does not link `.net`.** The `.net` site also runs
an MCP-server directory and product-comparison guides, which is a content property
rather than the project's home.

**That may be entirely benign — same person, two properties.** But the question "which
of these is the project's own hosted service" is not answered by the project itself,
and **the one the repository endorses is not the one the account is on.**

**The operative rule: do not upload a private corpus to the domain the project does not
link.** And there is no need to, because the local path exists and needs no domain at
all.

## THE PRICING, READ OFF THE CONSOLE

    FREE       $0      2,300 credits/mo   1 repo    100 MB   1 concurrent build
    PRO        $12/mo  30,000 credits     10 repos  10 GB    2 builds
                       + incremental webhook rebuilds
    PRO MAX    $55.50  141,000 credits    50 repos  50 GB    5 builds

Yearly is half price. **"Agent calls, AI usage, and builds all draw from one monthly
Credits balance."**

**ONE THING THEY DESERVE CREDIT FOR:** *"When a guardrail is reached, we slow down or
pause — never charge you automatically."* **That is fail-closed on spend, which is the
same posture this project just spent a week building.** It is the opposite of the
usual metered-overage trap and it is worth saying so.

**AND THE THING THAT IS NOT ANSWERED: a credit is still not defined anywhere.** They
say what DRAWS from the balance. They do not say at what rate. **2,300 could be a month
or an afternoon and there is no way to know before spending it.**

**AND THE ONE THAT MATTERS MOST ON THE FREE TIER: incremental webhook rebuilds are
PRO-ONLY.** So on Free, the graph does not keep itself current — **every refresh is a
manual rebuild that spends credits.**

**Which means the free tier offers exactly two outcomes: a graph that is stale, or a
graph that costs money to keep current.** Stale-thing-that-looks-current is this
project's signature defect. **The local build has neither problem: rebuilding is free
and can be scheduled.**

## WHAT STILL COSTS SOMETHING, EVEN LOCALLY — AND IT IS THE SAME BOUNDARY AS ALWAYS

**The code half is free and fully local.** Tree-sitter AST parsing, no model, no
telemetry, nothing uploaded. This is the half that maps the Python and Go.

**The document half needs a model to read documents**, and that model is configured by
the user. Two options:

    OLLAMA, LOCALLY     already installed on this machine. Nothing leaves.
    A CLOUD MODEL KEY   the documents' semantic content goes to that provider.

**The project's own claim is that only semantic descriptions are transmitted, never raw
source.** That is about the local build path and it is a meaningful distinction — but a
semantic description of a document that names the master switch path still names it.

**So the standing position is unchanged:** the document half does not run against
`docs/` or `claude/` until the curated-export refusals exist. Code half now, documents
later, and the same refusals govern both.

## RECOMMENDATION

    1  DO NOT add Sources to the hosted console. Leave the account dormant.
    2  Install the open-source engine locally, from PyPI or the Graphify-Labs
       repository - not from a link on the .net site.
    3  Run it over the SOURCE TREE only. No documents, no model configured.
    4  Register the local MCP server and let a desk query it.
    5  Measure it. The wake log now carries real token counts, so the question
       "does this actually reduce what a desk reads" is answerable from this
       project's own data rather than from anybody's marketing.

**Step 5 is the one that matters.** Everything before it is setup; step 5 is the only
part that produces evidence.

## WHAT THIS DOES NOT CHANGE

Nothing installed, nothing uploaded, no account modified, no repository change. **The
build order is untouched and this does not delay the brakes.**
