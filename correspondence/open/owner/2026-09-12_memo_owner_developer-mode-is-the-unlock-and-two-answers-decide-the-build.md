# Memo

To:      Owner
From:    Architecture
Subject: Developer mode is the unlock — "connectors that could modify" is write access. Two answers off that screen decide what gets built, and one of them could mean nothing gets built at all.

**Filed against `claude/DESIGN_the-echo-loop-2026-09-12.md`, whose MCP section is
already marked withdrawn. Nothing built.**

## WHAT YOU FOUND CHANGES THE ANSWER

**"Allows you to add unverified connectors that could modify" is the sentence that
matters.** That is write access, and it is on your account. **The open question about
whether Plus gets write tools is answered by your own screen** — better evidence than
either document I read tonight.

## THE CHEAPEST POSSIBLE OUTCOME, AND IT IS WORTH CHECKING BEFORE ANYTHING IS BUILT

**Search that plugin directory for GitHub.** If a GitHub plugin exists and can CREATE
rather than only read, **Echo can file her answer as a GitHub issue and we build
nothing** — no server, no tunnel, no token. A small job turns issues into letters in my
tray.

**That would be the whole loop solved with an existing, verified plugin.** It is the
first thing to rule in or out, because every other route costs a build.

## IF THERE IS NO WRITE-CAPABLE GITHUB PLUGIN

**Then it is a custom connector, and the form tells us which kind.**

**IF IT ASKS FOR A URL** — that is a remote server, and it needs a public HTTPS address.
**The right shape is a Cloudflare tunnel to a small program on your own PC**, not a cloud
service: your letters never sit in somebody else's database, there is only one copy, and
it writes straight into `inbox/`. **You already have Cloudflare on this project.**

**It needs a token so the address is not open to the world. That token is a credential —
yours, created by you, and it never goes in the repository.**

**IF IT ASKS FOR A COMMAND** — a local program, no tunnel, no token, nothing exposed.
Simplest outcome and the safest.

## THE BOUNDARY DOES NOT CHANGE IN ANY OF THE THREE

    writes   only into inbox/, only .md, never overwrites, memo header
             required, size capped
    reads    design/briefs/, docs/, claude/ and nothing else
    never    .env, correspondence/, logs/, credentials, anything outside
             the repository
    no       delete, move, rename, execute

## THE ONE THING I WILL SAY AGAINST TURNING IT ON

**Developer mode is a standing posture, not a one-time permission.** Once it is on, any
connector you add later is also unverified and also able to modify. **Ours is bounded in
the tool; the next one you try at 2am is not.**

**Not a reason to refuse it. A reason to treat that switch as a decision you made rather
than a box you ticked** — and to be deliberate about what else goes in there.

## AND THE THING THAT WORKS TONIGHT REGARDLESS

**The clipboard hotkey needs none of this.** Copy her answer, one keypress, filed. It is
not competing with the connector — it is what covers you while the connector is built,
and the fallback for the day a vendor changes something.

---

**THE QUESTIONS, IN ORDER:**

1. In Browse plugins, search for GitHub — is there one, and does it say it can create or
   write, or only read?
2. With developer mode on, start adding your own connector: does the form ask for a URL,
   or for a command to run?

*C1, 2026-09-12. Nothing built, nothing turned on.*
