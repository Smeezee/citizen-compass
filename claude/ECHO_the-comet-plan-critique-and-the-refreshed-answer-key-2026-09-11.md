# ECHO — the Comet plan critique, and the answer key checked against the served site

**Filed 2026-09-11 by the Adjutant desk.** Echo's review of
`claude/ECHO_review-the-comet-test-plan-2026-09-11.md`, verbatim, then what was done with
it. **Comet has not run.**

---

## ECHO'S REVIEW, VERBATIM

Sleven, do not run this yet. The plan is thoughtful, but the everyday signed-in browser is an unacceptable risk. Written instructions are not a security barrier.

Findings

1. ESTABLISHED — Prompt A is incomplete.
It proves access to the JavaScript-generated page, but not necessarily visual understanding. JSON could produce several correct answers. Require a screenshot plus a layout-specific question at 390 pixels wide.
2. RECOMMENDATION — Use a separate browser profile.
It should contain no unrelated accounts, saved passwords, payment information, history, or personal tabs. Only the two Citizen Compass sites should be open. Type the test-site password yourself inside that profile.
3. FORECAST — Labels alone will not prevent overconfidence.
Add UNVERIFIED. "Confirmed" must require repeatable steps plus a screenshot, exact text, or observed link result. Accessibility claims require an actual keyboard or contrast test.
4. ESTABLISHED — Prompt B is too large.
Two sites, desktop, phone, six tasks, five ship pages, accessibility, and comparison will reduce consistency. Split it into:
   * Capability test
   * Public-site desktop review
   * Test-site desktop review
   * Phone review
   * Final comparison
5. RECOMMENDATION — Fix the bias.
Conduct the no-scroll first impression before explaining the site's purpose. Keep the six tasks afterward because they are intentional usability tests. Keep Cutlass Black so results are reproducible.
6. RECOMMENDATION — Replace the all-or-nothing score.
Wrong dynamic content should block the review. Failure to resize should block only the phone review. A transcription error should not invalidate a screenshot proving the correct rendered content.

Also remove permission to visit external websites. Record external links for a separate isolated link test.

I would have Claude rewrite the prompts after the answer key is rechecked against the currently served site. The new browser profile and refreshed answer key are prerequisites, so rewriting the final runnable prompts before those two things would be premature.

Sources
OWASP recommends least-privilege access and human oversight for browsing agents exposed to untrusted webpage instructions. No useful primary Perplexity documentation was found establishing that prompt wording alone confines Comet.

* [OWASP Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
* [OWASP GenAI Security Project](https://genai.owasp.org/)

---

## WHAT WAS DONE WITH IT

**All six findings and the external-link change are accepted.** The Adjutant desk's
original "limits in the prompt" approach was the weak part, and Echo is right that
wording is not a barrier.

### PREREQUISITE 1 — A SEPARATE COMET PROFILE. **NOT DONE. SLEVEN'S.**

Comet's own help page: click the profile icon top right, "Add Comet Profile", name it,
pick a colour, Done. "Every profile keeps its own history, bookmarks, passwords,
extensions, and theme." The page does not say whether the Perplexity sign-in is shared
between profiles; the agent may need that one sign-in and nothing else.
[Profiles on Comet](https://www.perplexity.ai/help-center/comet/en/articles/11642916-profiles-on-comet)

### PREREQUISITE 2 — THE ANSWER KEY. **DONE, against the served, rendered site.**

Checked 2026-09-11 18:50 UTC / 13:50 CDT by the Adjutant desk in Chrome, on the live
testing origin unlocked, reading the rendered page rather than the file. **Every value
from the build-payload key held.**

**Test site `/next`, desktop, 1510 px wide:**

    header                  "v0.4.0 · 253 ships testing 2026-09-11"
    stat tiles              253 SHIPS TRACKED · 237 WITH A PLEDGE PRICE ·
                            179 BUYABLE IN GAME · 18 MANUFACTURERS ·
                            5 SHIP DEALERS · 28 JOBS COVERED
    first three headings    Aegis Dynamics   "28 ships · 19 buyable in game"
                            Anvil Aerospace  "38 ships · 24 buyable in game"
                            Aopoa            "3 ships · 3 buyable in game"
    first ship              Avenger Stalker, IN GAME, Fighter, 1,508,220 aUEC, $60,
                            at New Deal
    its link                loadout.html?from=next#AEGS_Avenger_Stalker
    cards per row           4
    tabs                    Ships · Development Progress · Sale Calendar ·
                            Legend & Sources

**Test site `/next`, phone, 386 px usable width** (a same-origin iframe 390 px wide,
because Chrome reported the window resize as done and left the width at 1510):

    stat tiles              two columns, three rows: 253 / 237, 179 / 18, 5 / 28
    cards per row           1
    tab row                 Ships, Development Progress, Sale Calendar visible;
                            "Legend & Sources" entirely off the right edge, with
                            no visible sign the row scrolls
    category buttons        "Buyable in game", "Combat", "Transporter", and a
                            fourth cut off at the edge
    version and stamp       NOT VISIBLE (computed display: none)
    bottom of screen        the trademark notice bar sits over the page content

**Public site `https://citizencompass.netlify.app`, desktop:**

    page title              "Citizen Compass v0.3.9"
    data date               "Compiled/updated: 2026-07-30"
    patch line              Alpha 4.9.0 "Frontier Tensions" (LIVE July 15-16, 2026)
    password                none

**Two of these are candidates for the layout question Echo asked for,** because JSON alone
cannot produce them: how many ship cards sit side by side, and which tab name is missing
from the visible tab row at phone width.

### SOMETHING THE CHECK FOUND

**On a phone, the testing front door shows no testing stamp.** The version line is
hidden at that width, so the fix Code deployed at 12:50 CDT holds on desktop only. Sent
to Build as `memo_build_on-a-phone-the-front-door-hides-the-testing-stamp.md`, not to stop
current work.

**The key can drift.** Code is mid-way through Q55.P1, which changes the front page. The
header, headings and counts come from the ship data and should not move; the tab row and
addresses may. **Whoever scores a run re-reads the served page at the time of the run.**

### NEXT

When Sleven confirms the separate profile exists with only the two sites open and the
test site unlocked, the Adjutant desk writes the five runs Echo specified: capability
test, public-site desktop, test-site desktop, phone, final comparison. Each carries
UNVERIFIED as a third label, stronger evidence rules for CONFIRMED, no external sites,
and the first impression taken before the site's purpose is explained.
