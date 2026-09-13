# ECHO — two social videos: OmniRoute, and the "20 AI agent mistakes" file setup

**Filed 2026-09-11 by the Adjutant desk, at Sleven's order.** He sent two phone
screenshots of short videos and asked for them to be translated into text for Echo.
Copy-paste block for Echo below.

---

Echo — Sleven saw two short videos and wants your read on both. They are unrelated to each other. Below is everything the screenshots show, word for word where there is text, followed by what the Claude desk checked and the questions for you. Keep using your labels: ESTABLISHED, RECOMMENDATION, FORECAST.

## VIDEO 1 — "OmniRoute", posted by charlieautomates

**On screen:** a presenter talking to camera. Above him is an OpenRouter-style API key list with three keys, named "Omniroute", "Hermes" and "Generate Report", each with "No guardrails", expiry "Never". A caption reads "WHICH IS".

**The post text, word for word:**
"Comment "gateway" for the OmniRoute install link + my free playbook
You hit your Claude Code limit mid-build. Session dead.
Someone dropped a free tool on GitHub that fixes it.
It's called OmniRoute. One command in your terminal.
It routes Claude Code across 460+ models. Add a free OpenRouter key, flip on free only, done.
Hit your limit? Switch to the free models and keep building.
Number one repo of the day for a reason."
Hashtags: #ClaudeCode #AItools #Automation #OpenSource.

**What the Claude desk found in a first look, 2026-09-11. Not a review.**
- The project exists: github.com/diegosouzapw/OmniRoute. MIT licence. About 61,500 stars, version 3.8.51 at the time of reading.
- It runs as a local server on the user's own machine. Claude Code is pointed at that local address instead of Anthropic, and the gateway forwards each request to whichever outside provider it picks, falling back when one runs out.
- The repository's own description says 352 providers, 150+ free, and 1,200+ models. That does not match the video's "460+", so the video is older or loose with numbers.
- It says it can use both API keys and logged-in subscription accounts, includes providers that need no key at all, and has a feature it calls "TLS stealth" for blocked regions.
- It claims it sends no prompts or usage data to its own servers. That is the project's own claim, not checked.
- One article is titled, in part, "why you shouldn't touch it", with a subtitle mentioning security risks and CVEs (Level Up Coding, on Medium). The article body could not be read, so its claims are unknown.

**Why it matters for Citizen Compass.** Claude Code works inside the whole project repository. Pointed at a gateway, the files Code reads — and whatever an outside model is shown — go to providers nobody on the project has vetted, some of them free and keyless. The project has a standing rule that secrets, correspondence and machine paths never go to outside AI services. The repository also holds an environment file. A cheaper model silently standing in for Claude mid-task would also undermine every "who did this work" record the desks keep.

## VIDEO 2 — "Fix These 20 Common AI Agent Mistakes (in 53 seconds)", posted by cooper.simson

**On screen:** the title above, a presenter, and a numbered list. Post text: "Comment "FILES" and I'll send you the full file tree + ..." (cut off). About 4,921 likes, 11,300 comments, 11,800 saves at the time of the screenshot.

**The list, word for word:**
1. One root folder
2. Brain folder
3. CLAUDE.MD
4. Model routing
5. 5 Context files
6. Memory Folder
7. Index file
8. Tools.md
9. Project folders
10. Context files
11. Obsidian
12. Connect GitHub
13. Now.md
14. Notion
15. Rules.md
16. Skills folder
17. Workflow folder
18. Python scripts
19. .env
20. .gitignore

No explanation of any item is visible. The actual file tree is behind a comment-to-receive offer.

**How Citizen Compass already compares, from what the Claude desk can see on disk today:**
- Already in place: one project root folder; a CLAUDE.md; a documents folder the desks write findings, specs and handoffs into; Obsidian (vault settings folders are present); Python scripts; a .env file and a .gitignore; a Git repository; per-user Claude memory; a claude.ai project holding about 870 documents.
- Already in place under other names: "Now.md" is close to the project's NEXT.md, LIVE.md and CURRENT-STATE; "Rules.md" is close to CLAUDE.md plus OWNERS.md; "Memory Folder" and "Brain folder" are close to the claude.ai project and the day-page logs.
- Not in place or undecided: Notion (not used); "Connect GitHub" (whether the repository is pushed, and whether it is public, is still waiting on Sleven); model routing (that is Video 1's subject); a skills folder and a workflow folder (not checked).

**The Claude desk's candid point for you to test.** The list is mostly things this project already has. Architecture reported today that the project's net process went up, not down. The risk from this video is adding more context files that every session must read, when the real problem this week has been too many documents, too many copies of them, and sessions reading stale ones.

## WHAT WOULD HELP FROM YOU

Short answers, only where you see something real:
1. OmniRoute: is it safe enough to use on a project like this at all, and if so, under what limits? Check the project's own security notes, any CVEs, and whether sending requests through it or pooling subscription logins breaks Anthropic's or other providers' terms.
2. OmniRoute: is there an established, safer way to keep Claude Code working when it hits its usage limit, without handing the repository to unvetted models?
3. The 20-item list: which items, if any, would fix a problem this project actually has, rather than repeat something it already has?
