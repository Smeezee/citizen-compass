# CITIZEN COMPASS — HUMAN-CENTERED UX & BEHAVIORAL DESIGN DOCTRINE
Version: 6.2

ADOPTED by Sleven 2026-09-08. Section numbers are FROZEN as of this filing.
v6.2 is v6.1 with Section 9 amended on his order — the section policed only
browser controls, and the measurement does not support that framing.

## OPERATIVE CORE — READ BEFORE USER-FACING WORK
This is the binding short form. The body explains and operationalizes it.
- ANSWER FIRST
  Answer → Action → Context → Deep Detail.
- NEVER GUESS IDENTITY
  Declared exact mappings are allowed. Computed similarity is not identity.
  See CLAUDE.md hard rule 17.
- RIGHTS ARE A GATE
  If exposure of third-party material changes, normal UX comparison stops
  until Sleven rules.
  See CLAUDE.md hard rules 8 and 23.
- REQUIREMENT BEFORE CONTROL
  A control tests an independently stated requirement. Never derive the
  expected result from whatever the current implementation happens to do.
  See CLAUDE.md hard rules 12 and 16.
- MEASURE, THEN LOOK
  Rendered work is visually inspected. Where objective spatial, geometric,
  sizing, positioning, framing, or similar correctness is involved, visual
  inspection is paired with an independent measurement of that property.
  See CLAUDE.md hard rules 12 and 16.
- AUTOMATE WHAT CAN BE PROVEN
  Prefer reliable deterministic controls over permanent prose without
  duplicating controls or making verification too expensive to run.
- DO NOT REDESIGN FOR THE SAKE OF REDESIGNING
  Preserve working behavior unless evidence supports changing it.
- DO NOT CREATE WORK TO SATISFY THIS DOCTRINE
  This doctrine does not outrank the queue, reopen publication, invent
  interfaces, or manufacture UX projects.
- THIS DOCTRINE HAS A COST
  Its requirements add work to user-facing tasks. That cost is justified only
  while it catches meaningful defects or prevents repeat failures. Rules that
  become ritual rather than useful verification must be revised.
If the operative core and detailed body appear to conflict, reconcile the
doctrine before relying on the disputed instruction.
## STATUS / HOME / OWNER
This doctrine governs human-facing experience across Citizen Compass.
It applies to:
- password-gated website/testing builds;
- future public website builds;
- defined human-facing surfaces of the Collector rebuild;
- other Citizen Compass software or interfaces used by people;
- upstream design decisions that materially constrain a future user experience,
  as described in the Collector section.
When adopted:
- canonical home: docs/UX_DOCTRINE.md
- register its owner/writer in OWNERS.md
- C1 owns technical interpretation and maintenance
- Sleven owns product direction, publication, rights/legal decisions, and
  acceptance, revision, or retirement of this doctrine
This doctrine creates NO project hard rules.
CLAUDE.md remains the authority for the project's hard rules and is the only
hard-rule list. Where this doctrine appears to conflict with CLAUDE.md,
CLAUDE.md wins and the doctrine must be corrected.
Do not create competing UX doctrine files.
This document is governance, not project state. Current defects, releases,
queues, deployment status, and temporary implementation state belong in their
existing authoritative mechanisms.
SECTION NUMBERS FREEZE AT ADOPTION.
After adoption:
- amend an existing section in place; or
- append a new section at the end.
Do not renumber existing sections.
If renumbering ever becomes unavoidable, preserve an explicit old-to-new
mapping in the document so existing work orders and evidence do not silently
point at the wrong requirement.
# 1. CURRENT DELIVERY BOUNDARY
The current public site is intentionally NOT the product target for this
doctrine.
Sleven has removed public deployment from the queue until he raises it himself.
Nothing in this doctrine:
- recommends publication;
- builds a case for publication;
- puts deployment back on the queue;
- treats UX progress as evidence that the site is ready to publish.
Publishing is an owner decision and is CLOSED unless Sleven reopens it.
The doctrine's active scope today includes:
- password-gated/current testing builds;
- deterministic UX controls;
- owner-use evidence;
- currently defined human-facing behavior;
- observations about upstream decisions that may constrain a future interface.
This doctrine does not require a public product in order for deterministic UX
work to be useful.
# 2. ADOPTION BOUNDARY FOR WORK ALREADY IN FLIGHT
This doctrine governs work ordered AFTER adoption.
Items already in flight complete under the DONE-WHEN and acceptance criteria
that existed when they were authorized.
Do not launch a retrofit campaign merely to make existing orders conform to
this doctrine.
If an in-flight item contains a real UX or visual defect, fix it as a normal
defect.
The fact that an older order did not follow this doctrine is not itself a
defect.
# 3. PURPOSE
Design Citizen Compass around how people think, scan, search, compare, decide,
understand, and complete tasks.
Do not design primarily around:
- database structure;
- implementation convenience;
- developer habits;
- visual novelty;
- time-on-site;
- engagement metrics.
Optimize for:
USEFULNESS
COMPREHENSION
CONFIDENCE
DISCOVERY
EFFICIENCY
ACCESSIBILITY
PREDICTABILITY
SATISFACTION
Complex underlying information does not require a complex first encounter.
# 4. ANSWER FIRST
Whenever practical:
ANSWER
→ ACTION
→ CONTEXT
→ DEEP DETAIL
Examples:
"Where can I buy this?"
→ show where.
"What does it cost?"
→ show the relevant price.
"What fits this hardpoint?"
→ show valid compatible choices.
"Is this current?"
→ show currentness/verification clearly.
"Where did this come from?"
→ make allowed provenance available after the useful answer.
Supporting information matters.
It must not stand between the user and the primary answer.
# 5. SUCCESS IS NOT ENGAGEMENT
A user who receives the answer immediately and leaves has succeeded.
Do not optimize for:
- session length;
- compulsive clicking;
- artificial engagement;
- deceptive urgency;
- hidden exits;
- manipulative rewards;
- unnecessary friction;
- artificial scarcity;
- dark patterns.
Use behavioral understanding to remove friction, not exploit users.
# 6. DO NOT REDESIGN FOR THE SAKE OF REDESIGNING
This doctrine does not authorize a broad redesign.
Before replacing working behavior, determine:
- what problem exists;
- what evidence supports it;
- whether the proposed change materially improves it;
- what useful behavior might be lost.
Visual novelty is not progress.
Preserve interfaces that already perform their jobs well.
# 7. REQUIREMENT FIRST, CONTROL SECOND
Citizen Compass already has an automated-control architecture.
UX should use it.
A control is valid only when it tests a requirement that exists independently
of the implementation being checked.
Required ordering:
STATED REQUIREMENT
→ INDEPENDENT EXPECTED RESULT
→ CONTROL
→ IMPLEMENTATION
Never:
CURRENT IMPLEMENTATION
→ OBSERVE WHAT IT DOES
→ WRITE THAT BEHAVIOR INTO THE CONTROL
A control whose expected result was read from the running system is not
independent evidence.
If no requirement exists:
- state the requirement first; or
- do not create the control yet.
This directly applies CLAUDE.md hard rule 16: verification truth must come from
a different source than the thing being verified.
It also applies hard rule 12: a check that cannot fail is not a check.
If implementation and control derive truth from the same assumption, the result
is UNPROVEN.
This is especially important for:
- search behavior;
- autocomplete;
- zero-result behavior;
- trust indicators;
- loading states;
- error states;
- navigation behavior;
- responsive behavior.
Do not accidentally convert today's implementation into tomorrow's
specification.
# 8. AUTOMATE WHAT CAN BE PROVEN
A reliable UX control outlives the session that wrote the doctrine.
A requirement left only as prose will eventually be forgotten, reinterpreted,
or re-litigated.
Therefore:
IF AN INDEPENDENTLY SPECIFIED UX REQUIREMENT CAN BE TESTED DETERMINISTICALLY,
PREFER MAKING IT A CONTROL.
Potential controls include:
- browser/page errors;
- broken links;
- missing assets;
- duplicate IDs;
- heading structure;
- alt text;
- labels;
- keyboard traversal;
- focus visibility;
- contrast;
- touch-target dimensions;
- overflow at defined viewports;
- elements escaping containers;
- responsive regressions;
- search rules;
- autocomplete rules;
- zero-result behavior;
- native-link behavior;
- required trust indicators;
- loading/error states;
- accessibility requirements;
- defined performance budgets.
Before writing a control:
1. Confirm the requirement is independently stated.
2. Inspect controls discoverable by the existing control runner.
3. Inspect OWNERS.md.
4. Determine whether an existing control already proves the invariant.
5. Extend an appropriate existing control when cleaner.
6. Create a new control only for a genuinely distinct invariant.
Do not create a separate UX verification framework.
A control that cannot fail when its protected behavior is wrong is not a useful
control.
## EXTERNAL-RESOURCE FAILURE SEMANTICS
A control that depends on an external resource must distinguish:
LOOKED AND FOUND A DEFECT
from:
COULD NOT LOOK.
If a required external resource is unavailable — for example a real browser,
served origin, database, PowerShell, or another required execution dependency —
the control exits 2 and reports NOT PERFORMED according to the project's
existing control convention.
Do not report that condition as PASS.
Do not report it as an ordinary defect FAIL.
"Could not look" and "looked and it was wrong" are different states, and neither
proves success.
# 9. CONTROL-SUITE COST
The project's full-sweep runtime baseline already exists.
Authoritative measurement location:
checks/.last_sweep.json → "seconds"
Measured baseline:
- 2026-09-07
- 122 controls
- partial: false
- 2,871.4 seconds
- approximately 47.9 minutes
Do not create another mechanism merely to re-measure something the runner
already records.
The outstanding decision is the acceptable MAIN-SWEEP runtime budget.
That budget is a C1/owner project decision informed by measured operating needs;
it is not something this doctrine invents.
UNTIL AN AGREED MAIN-SWEEP BUDGET EXISTS:
A new browser-driven UX control joins the main sweep the moment its file lands.
The control runner DISCOVERS its work from disk rather than from a list, so
there is no hold-out state, and an instruction to "build it but keep it out of
the sweep" cannot be followed by anyone.
When any new control is added — browser-driven or not — the cost is not
avoided. It is MEASURED AND REPORTED.
Browser controls are not privileged here. As of the 2026-09-06 sweep they
were 17% of total runtime, and the three most expensive controls in the
suite were not browser controls. A rule that accounts only for browser cost
polices the smaller half.
1. take the control's measured runtime from the sweep output — the runner
   already prints the elapsed seconds beside every control on every result
   line;
2. record that runtime in the closure of the queue item that produced the
   control, beside the control's name;
3. state whether it materially moves the total sweep runtime, and if it does,
   raise the budget decision there rather than absorbing the cost silently.
Controls execute one at a time, so a control's own runtime is the sweep's
increase. A before-and-after full sweep is needed only when that is in doubt.
The budget is a ceiling on TOTAL sweep runtime, not a per-control
allowance.
When a full sweep's recorded runtime moves materially against the last
recorded figure, report the change rather than absorbing it. A suite that
grows quietly is how verification becomes too expensive to run, and
Section 42 already names "controls are routinely skipped because they are
too expensive" as a sign the doctrine has failed.
Do not create a parallel holding area for controls that are not yet budgeted.
A second place where controls live is a second place where a control can be
forgotten while everyone believes it is running.
Do not invent a "separate browser suite" as hidden infrastructure.
If the project wants a dedicated browser-control suite or grouping mechanism,
that is its own queue item with:
- owner;
- scope;
- design;
- DONE-WHEN.
There are already browser controls in the main sweep. This section governs new
additions; it does not retroactively remove existing ones.
Verification that becomes too expensive to run routinely will eventually be
skipped.
Do not make that problem worse without measuring the cost.
Where appropriate, control cost may also be managed by:
- combining related assertions into one browser execution;
- running controls when affected artifacts change;
- sampling only when the invariant genuinely permits sampling.
Do not weaken coverage merely to hit a runtime target.
# 10. VISUAL EVIDENCE — WHY LOOKING ALONE IS NOT PROOF
Structural automation alone cannot establish every visual fact.
Visual inspection alone cannot establish every visual fact either.
A viewer may misinterpret a low-resolution render.
A render may agree with a broken artifact because the render and artifact share
the same incorrect assumption.
Therefore, for objective rendered properties:
MEASURE THE PROPERTY INDEPENDENTLY
→ THEN LOOK AT THE RESULT TO INTERPRET IT
The measurement establishes the objective property.
The visual result establishes how that property manifests to a viewer.
A measurement produced from the same broken assumption as the artifact is not
independent proof.
This applies CLAUDE.md hard rules 12 and 16.
The complete acceptance rule and proportional trigger are defined once in
Section 39.
This section explains why that rule exists.
# 11. EVIDENCE MODES
Do not invent user evidence.
## CURRENT PRE-PUBLIC STATE
Today, Sleven is the regular human evidence source for the password-gated site.
Valid evidence currently includes:
- deterministic controls;
- real-browser measurement;
- accessibility measurement;
- performance measurement;
- independent visual measurement;
- visual inspection by a capable inspector;
- responsive testing;
- keyboard testing;
- Sleven's actual use;
- reproducible interaction failures.
## AUTHORIZED TESTERS — CONDITIONAL
Direct observation of authorized testers becomes evidence only when actual
testers exist and are using the relevant current build.
Do not say:
"testers found"
"users reported"
"people are struggling with"
unless such evidence actually exists.
## AFTER A CURRENT PUBLIC PRODUCT EXISTS
Additional evidence may include:
- search behavior;
- zero-result frequency;
- navigation patterns;
- feature usage;
- error patterns;
- support questions;
- usability testing;
- direct feedback;
- privacy-respecting analytics.
Always distinguish:
MEASURED PUBLIC USER BEHAVIOR
OWNER OBSERVATION
AUTHORIZED TESTER OBSERVATION
DETERMINISTIC FAILURE
MEASURED VISUAL PROPERTY
VISUAL INTERPRETATION
DESIGN HEURISTIC
PERSONAL PREFERENCE
Never present one as another.
# 12. HUMAN-CENTERED DESIGN
Before changing user-facing behavior, determine:
WHO
Who uses it?
TASK
What are they trying to accomplish?
ANSWER
What do they need first?
ACTION
What comes next?
FRICTION
What makes that difficult?
RISK
What could mislead them?
DEPTH
What information is primary versus advanced?
Design around the user's task, not internal implementation structure.
# 13. TASK-ORIENTED UX
Organize important experiences around real goals.
Examples:
- find a ship;
- find a component;
- determine where something is sold;
- compare prices;
- inspect a loadout;
- determine compatibility;
- compare alternatives;
- understand verification/currentness;
- move among related entities.
For meaningful pages identify:
PRIMARY TASK
SECONDARY TASKS
The primary task receives the clearest path and strongest informational
priority.
# 14. RECOGNITION OVER RECALL — WITHOUT FUZZY IDENTITY
Users should recognize valid choices rather than memorize internal terminology.
Useful mechanisms may include:
- autocomplete;
- thumbnails;
- manufacturer names;
- categories;
- contextual navigation;
- visible filters;
- declared aliases;
- declared abbreviations.
But:
DECLARED DATA IS NOT FUZZY MATCHING.
A safe alias is an explicit mapping:
DECLARED INPUT
→ CANONICAL ENTITY
Computed similarity is not identity.
If an alias/name mapping is:
- contested;
- ambiguous;
- unsupported;
- awaiting owner decision;
it remains unbuilt.
A designer, C1, Code, or search algorithm may not manufacture the mapping to
make UX easier.
Declared aliases are only as trustworthy as the declaration behind them.
# 15. SEARCH AND DISCOVERY
Search is a major navigation system.
Support imperfect human input while preserving exact identity.
Potential mechanisms:
- prefix completion;
- declared aliases;
- declared abbreviations;
- manufacturer + entity search;
- valid categories;
- keyboard navigation;
- predictable autocomplete acceptance;
- useful zero-result recovery.
Autocomplete must complete from known valid vocabulary.
If several valid choices remain, expose them.
Do not guess.
# 16. ZERO-RESULT EXPERIENCE
"No results" may still provide a useful next action.
When supported by evidence, explain:
- nothing exists;
- the query is incomplete;
- another category is relevant;
- a declared alias exists;
- another valid path is available.
Do not fabricate a probable match because an empty state feels unfriendly.
# 17. INFORMATION ARCHITECTURE
Information should have predictable homes.
Users should develop stable expectations such as:
"I know where ship information lives."
"I know where buying information lives."
"I know where compatibility lives."
"I know where verification lives."
Avoid:
- duplicate concepts with inconsistent names;
- multiple unrelated homes for one function;
- implementation-history-driven navigation;
- interaction meanings that change between pages.
# 18. INFORMATION SCENT
Links, cards, headings, buttons, and navigation labels should make their
destination or outcome reasonably predictable.
Prefer user-language over internal terminology.
Use secondary information only when it helps users predict what lies behind an
interaction.
# 19. COGNITIVE LOAD
Do not make users perform mental work the interface can safely perform.
Reduce unnecessary:
- choices;
- labels;
- jargon;
- competing emphasis;
- repeated information;
- navigation decisions;
- manual cross-referencing;
- memory requirements.
Prefer:
SIMPLE FIRST ENCOUNTER
+
AVAILABLE DEPTH
# 20. PROGRESSIVE DISCLOSURE
A useful hierarchy is:
LEVEL 1 — immediate answer
LEVEL 2 — useful context
LEVEL 3 — alternatives/comparison
LEVEL 4 — technical detail
LEVEL 5 — allowed provenance/history/supporting evidence
Do not require Level 5 comprehension before receiving Level 1 value.
Do not remove useful expert depth merely to make a page look simple.
# 21. TRUST AND PROVENANCE
Citizen Compass depends on trustworthy information.
The interface should eventually communicate meaningful states such as:
- verified;
- unverified;
- stale;
- current;
- source-backed;
- uncertain;
- unavailable.
Use:
ANSWER
→ CURRENTNESS / CONFIDENCE SIGNAL
→ SOURCE SUMMARY
→ FULL ALLOWED PROVENANCE
Do not hide uncertainty.
## WHOLE-LAYER UNVERIFIED CONDITION
If an important data/product layer is largely or entirely unverified, the
honest interface may display that condition almost everywhere.
How Citizen Compass presents itself when that is true is an OWNER PRODUCT
DECISION.
Do not solve the problem by:
- weakening "verified";
- hiding the state;
- inventing confidence;
- silently treating unverified data as verified.
### STRUCK 2026-09-08 — THE TEXT THAT STOOD HERE WAS NEVER SLEVEN'S
A section stood here headed *"RULED BY SLEVEN 2026-09-08 — SAY IT ONCE, LOUDLY,
NOT 254 TIMES QUIETLY"*, ruling that the unverified condition is stated once at
site level and NOT put on every card, followed by four bullets introduced as
*"His reasoning, recorded so it can be applied to cases he has not named."*
**HE NEVER SAID ANY OF IT.** It was written in his voice by a session drafting an
order he never approved, and it reached this document as a ruling anyway. C1
carried it here without checking that the words were his.
**It is recorded as struck rather than quietly corrected, on his instruction:**
*"the record should show that a fabricated ruling got in, or nobody learns
anything from it."*
It was also backwards. It ruled against the decision he actually made when he was
shown both options drawn as real cards.
**The lesson is wider than this section.** A ruling attributed to the owner is
only his if he said it. A desk drafting an order in his voice produces a
proposal, not a ruling, and the difference does not survive being pasted into a
frozen document by somebody downstream.
### RULED BY SLEVEN 2026-09-08 — THE MARK GOES ON EVERY CARD
**His words, and this one he did say**, after being shown both options drawn with
real card shapes:
**Every ship card carries a mark saying its data has not been checked against a
game patch.** All of them, while all of them are unverified. Not a single line at
the top of the page.
**The mark is per-card and stays per-card.** When ships start getting verified,
the mark keeps its place and starts distinguishing checked from unchecked, which
is when it begins carrying real information.
**BUILD IT SO THAT SWITCH IS A DATA CONDITION, NOT A REWRITE.** This is the only
sentence carried over from the struck text, and it was sound.
**His reason, in his own words, for choosing the card over the bar:**
*"a person landing on a single ship from a search never sees the top of the ship
list, and on a phone a line at the top of the page scrolls away in one flick. The
mark travels with the card. The bar does not."*
**The argument against it is recorded because he recorded it himself:** a mark on
all 254 cards never varies, so it stops being read after the first screen, and it
cannot tell one ship from another. He went with the card anyway, for the reason
above.
**NOT DECIDED: the words on the badge.** He was shown wording written for a
page-level bar and it does not fit a card. C1 proposes the card wording and shows
him before it ships.
Hard rule 20 is untouched and is not in play here: every row still carries
`last_verified_patch` and the front end still flags unverified data. This rules
only on how the flag is PRESENTED while the whole layer is unverified.

### DECIDED 2026-09-09 — THE WORDING, AND THERE ARE THREE STATES RATHER THAN TWO
**Sleven approved the wording on 2026-09-09** after a human-factors check he
ordered before signing off. Two changes came with the go, and the second one
found a hole in the design rather than in the words.
#### NO COLOUR ON ANY CHIP — HIS RULING
Every state gets the **identical chip**: same colour, same weight, same position.
**The only thing that changes is the word.** C1 had proposed a small positive
tint on the verified state; he cut it, on the grounds that a visually distinct
chip sitting where a badge sits is the shape a reader has learned to skip, and
that this is worse on a phone, which is how he reads the site. **The tint would
have made the good news the part nobody sees.**
The reasoning and its source are recorded in
`claude/HUMAN-CHECK_the-card-mark-wording-2026-09-09.md`. It is his ruling, made
on a check he commissioned; this section records it rather than restating the
research behind it.
**A consequence that binds the wording:** with no colour anywhere, the word
carries the entire signal. **Each state's label must therefore be distinguishable
from the others at a glance, without colour**, which is a constraint on the words
and not a preference about them.
#### THREE STATES, AND THE THIRD IS CREATED BY CIG RATHER THAN BY US
He asked what the card says when 4.11 ships, and the honest answer is that the
two-state design could not say it. **A row that was checked against 4.10 becomes
a different thing the moment the game moves, without anybody here touching it.**
    NEVER CHECKED        last_verified_patch IS NULL
    CHECKED, CURRENT     last_verified_patch == the patch the game is on
    CHECKED, OVERTAKEN   last_verified_patch is behind the patch the game is on
**The dangerous one is the third**, and it is the case he named: *checked and
correct* and *checked two patches ago and nobody has looked since* are opposite
facts that the two-state design printed identically.
#### THE LABELS
    Awaiting check          never checked against anything
    Checked · 4.10          checked, and 4.10 is what the game is on
    Needs re-check · 4.9    checked, and the game has moved past it
**THE UNVERIFIED LABEL NAMES NO PATCH, and this reverses C1's own strongest
argument for the wording.** C1 recommended `Awaiting 4.10 check` because the
number moves on its own and gives every card information from day one. **Sleven
showed that it breaks in both directions** — rolled forward it resets the promise
every patch day and hides every ship already verified; frozen it names a patch
that is not current.
**Both readings are wrong because the number should never have been there.** A
row that has never been checked has no relationship to any patch. Naming one
states a fact that does not exist, which is the defect this whole section was
written to prevent.
#### THE STATE IS DERIVED, NEVER STORED
It is computed where the page is built, from the row's `last_verified_patch`
against **one** current-patch value. **No per-row state column, and no data
migration on patch day.**
This is what makes the switch a data condition rather than a rewrite, as ruled:
when the game patches, every `Checked · 4.10` becomes `Needs re-check · 4.10` by
itself. **Nothing on the site can silently go on claiming to be current, because
the comparison happens in the build and not in the reader's head.**
#### THE CURRENT-PATCH VALUE NEEDS A CONTROL OR THE WHOLE MARK ROTS SILENTLY
Every label above depends on one value. **If that value is typed by hand and
somebody forgets it on patch day, every verified card keeps saying `Checked`
about a patch the game has left** — and the mark built to prevent exactly that
becomes the thing asserting it.
**So the current-patch value is read from a source and a control asserts it is
current.** Hard rule 12: without that check, nothing about this mark can ever
fail, and a mark that cannot be wrong is decoration.
#### NOTHING CARRIES `Checked` UNTIL THE CHECK IS REAL
His condition, accepted without qualification. **The word raises the cost of
every error on that card** — a wrong number under `Awaiting check` costs little,
because the site said it had not looked; the same number under `Checked` is a
broken promise with the evidence attached.
A verification that cannot be re-run does not earn the word, which is the
standing this project already applies to any measurement.
**As of 2026-09-09 no row qualifies.** All 254 carry no `last_verified_patch` at
all, so the site shows `Awaiting check` and nothing else. That is the honest
picture and it is not a defect in the mark.
#### THE COST HE IS CARRYING KNOWINGLY
`Awaiting` is a promise with a clock on it. It reads as diligence now and as
abandonment if it is still sitting on 254 cards in three months. **That is a fact
about how fast verification actually moves, not about the words** — and it is
recorded here so nobody later reads the label as a mistake rather than as a
choice made with its cost known.


# 22. RIGHTS / LEGAL / PUBLICATION — HARD GATE
Rights are not a priority weighed against convenience.
Sleven alone owns rights/legal/publication decisions.
If a proposal changes public exposure of third-party material, normal UX
comparison stops until owner authorization exists.
This may include:
- CIG prose;
- item descriptions;
- mission text;
- game tips;
- extracted game material;
- third-party copyrighted text;
- imagery/assets;
- raw evidence;
- restricted or uncertain source material.
Possessing material does not establish permission to publish it.
UX operates inside the approved publication boundary.
# 23. ERROR PREVENTION
Prefer preventing predictable mistakes over warning about them afterward.
Make invalid, incompatible, destructive, ambiguous, or misleading actions
difficult to perform accidentally.
Communicate meaningful consequences before action.
# 24. FEEDBACK AND SYSTEM STATUS
Users should understand what the system is doing.
Provide useful feedback for:
- loading;
- searching;
- filtering;
- copying;
- saving;
- processing;
- capture;
- failures;
- unavailable information;
- long-running operations.
Avoid making users wonder whether an action worked or whether the system failed.
# 25. VISUAL HIERARCHY AND SCANNABILITY
Visual prominence should follow informational importance.
Use:
- position;
- spacing;
- typography;
- contrast;
- grouping;
- scale;
- density;
to communicate priority.
Assume users scan before reading.
Simple facts should not require paragraphs.
Decoration must not overpower utility.
# 26. CONSISTENCY
Similar things should behave similarly.
Learning one interaction should help users understand others.
Standardize demonstrated recurring patterns such as:
- cards;
- buttons;
- filters;
- search;
- navigation;
- provenance/status indicators;
- expandable sections;
- tables;
- error states;
- loading states.
Do not create a unique interaction model for every page.
# 27. ACCESSIBILITY
Accessibility is part of correctness.
Consider:
- keyboard navigation;
- visible focus;
- semantic HTML;
- screen-reader labels;
- contrast;
- text resizing;
- touch-target size;
- non-color status signals;
- motion sensitivity;
- responsive zoom;
- accessible errors;
- image alternatives where appropriate.
Do not accept behavioral optimization that reduces accessibility.
# 28. RESPONSIVE EXPERIENCE
Design for:
- desktop;
- laptop;
- tablet;
- phone;
- touch;
- keyboard/mouse.
Do not merely shrink desktop layouts.
Determine what remains primary as space decreases.
Do not damage desktop capability merely to achieve mobile minimalism.
# 29. PERFORMANCE UX
Do not claim a performance improvement without a measurement basis.
If no relevant baseline exists:
ESTABLISH THE BASELINE FIRST.
Then compare.
Potential measurements:
- useful-content timing;
- interaction latency;
- layout stability;
- payload size;
- relevant browser metrics;
- task-specific processing time.
The same baseline discipline governs verification runtime under Section 9.
# 30. NOVICE AND EXPERT COEXISTENCE
Citizen Compass should serve:
- people learning Star Citizen;
- experts who know what they need.
Prefer:
OBVIOUS DEFAULT PATH
+
OPTIONAL ADVANCED DEPTH
New users should not need expert terminology for basic answers.
Experts should not be forced through beginner instruction.
# 31. CONTEXTUAL HELP
Teach where knowledge is needed.
Prefer:
- concise tooltips;
- short inline explanations;
- meaningful empty states;
- contextual compatibility help;
over large instruction manuals.
Do not explain what is already obvious.
# 32. USER CONTROL AND NATIVE EXPECTATIONS
Preserve normal web behavior whenever practical:
- middle-click;
- open in new tab;
- back/forward;
- copyable/shareable URLs;
- keyboard behavior;
- native links.
Do not replace native behavior with custom JavaScript without a concrete
benefit.
# 33. USEFUL DISCOVERY
After satisfying the primary question, contextual exploration may be offered.
Examples:
- related ships;
- variants;
- alternate sellers;
- compatible equipment;
- price differences;
- adjacent useful information.
Discovery follows the answer.
It does not bury it.
# 34. DATA DENSITY, JOURNEYS, AND CONTINUITY
Large data volume does not justify showing everything simultaneously.
Use:
- search;
- filters;
- sorting;
- grouping;
- comparison;
- progressive disclosure;
- contextual relationships;
- meaningful defaults.
Evaluate complete journeys, not just screens:
SEARCH
→ IDENTIFY
→ OPEN
→ UNDERSTAND
→ COMPARE
→ ACT
→ VERIFY
Preserve useful state when practical:
- searches;
- filters;
- comparisons;
- navigation context;
- relevant page state.
# 35. COLLECTOR REBUILD — DO NOT INVENT A SURFACE
The withdrawn Collector is historical.
Do not create UX repair work against it unless Sleven explicitly reopens it.
The Collector rebuild currently has no defined user-facing surface.
Therefore:
BEFORE A USER-FACING SURFACE EXISTS,
THIS DOCTRINE CREATES NO COLLECTOR UI REQUIREMENTS.
Do not invent:
- windows;
- buttons;
- shortcuts;
- keybindings;
- menus;
- installers;
- status displays;
merely so the doctrine has something to govern.
## UPSTREAM DESIGN CONSULTATION
The absence of a defined interface does NOT mean future human consequences
should be ignored.
C1 must consult this doctrine when an architectural/data decision determines
whether information needed for a future human-facing explanation is retained
or discarded.
Examples include decisions controlling whether a future surface can distinguish:
- unresolved from missing;
- no-match from error;
- unknown from discarded;
- unavailable from never observed;
- recoverable history from permanently lost context.
Consultation at this stage produces observations only.
It does NOT create:
- UI requirements;
- screens;
- buttons;
- workflows;
- presentation designs.
The doctrine begins producing actual Collector UX requirements only when an
actual human-facing surface is defined.
Historical failures remain lessons, not backlog items.
# 36. ANALYTICS WITH PURPOSE
The website analytics design already exists and is PARKED pending Sleven's
decision.
Do not re-derive it as though the architecture were open.
Current parked design:
- GoatCounter hosted free/non-commercial tier;
- no cookies;
- IP hashed with a daily-rotating salt only to deduplicate same-day uniques,
  then discarded;
- country-level geography derived at request time and discarded;
- real localStorage opt-out that prevents the analytics script loading at all;
- footer privacy link.
Netlify analytics was previously ruled out because server-log collection cannot
be prevented by a client-side opt-out.
This section does not authorize implementation.
If analytics are eventually activated, use them to answer real product
questions rather than collect telemetry for its own sake.
Potential questions:
- What are users searching for?
- Where do zero results occur?
- Where do errors occur?
- Which features are used?
- Where does navigation fail?
Respect privacy, rights, legal constraints, and non-commercial requirements.
# 37. SIGNIFICANT USER-FACING CHANGE
A change is significant when it:
- creates a new page or major workflow;
- changes a default;
- changes navigation structure/labels;
- changes search behavior;
- changes what a first-time user sees above the fold;
- changes trust/verification presentation;
- materially changes an important user decision;
- changes a major defined user-tool interaction;
- creates a recurring interaction pattern.
"Significant" does not mean "requires C1 to manually review everything."
It means the order needs appropriate acceptance criteria before execution.
# 38. ACCEPTANCE CRITERIA — NOT A STOP GATE
Significant user-facing work receives measurable UX requirements in its work
order before implementation.
Potential criteria:
- primary answer occupies the intended hierarchy;
- keyboard behavior works;
- no overflow at defined viewport widths;
- native links preserve expected browser behavior;
- zero-result behavior matches its stated requirement;
- required trust state appears;
- accessibility controls pass;
- browser has no relevant errors;
- task reaches the intended outcome;
- defined responsive states function;
- identity ambiguity is not guessed.
DONE-WHEN must be evaluable without automatically routing every item through
C1.
For rendered work, apply Section 39.
# 39. RENDERED-WORK DONE-WHEN — SINGLE AUTHORITATIVE RULE
This section is the only full definition of rendered/visual acceptance.
## OBJECTIVE TRIGGER
This section applies whenever a change alters what is rendered to a screen,
including changes to:
- page layout;
- visible page content;
- visual styling that materially changes presentation;
- imagery;
- model geometry;
- markers;
- overlays;
- positioning;
- scaling;
- framing;
- camera behavior;
- drawing/rendering code;
- code whose output determines where or how any of those are shown.
Applicability is determined by WHAT THE CHANGE AFFECTS, not by whether the
author believes they are making a visual claim.
The worker does not opt into or out of visual verification.
## DEPTH IS PROPORTIONAL TO RISK
Where classification between levels is unclear, APPLY THE HIGHER LEVEL.
Do not resolve ambiguity by choosing the cheaper level.
### LEVEL A — SIMPLE VISIBLE CONTENT
Examples:
- correcting a label;
- changing static wording;
- replacing known imagery where placement/layout is unchanged.
DONE-WHEN may require:
- stated expected result;
- visual inspection of the finished result;
- normal deterministic controls relevant to the change.
Independent geometric measurement is not required when no objective geometric,
spatial, sizing, positioning, or framing claim is involved.
### LEVEL B — LAYOUT / PRESENTATION BEHAVIOR
Examples:
- spacing;
- responsive layout;
- overflow;
- visible alignment;
- container sizing;
- above-the-fold placement;
- touch-target dimensions.
DONE-WHEN requires:
- independently stated requirement;
- objective browser/DOM/accessibility measurement appropriate to the property;
- visual inspection of the finished result.
### LEVEL C — GEOMETRY / POSITION / SCALE / FRAMING / RENDERING
Examples:
- 3D model geometry;
- hardpoint-marker placement;
- overlay placement;
- model orientation;
- model scale;
- camera framing;
- coordinate conversion;
- geometry transforms;
- rendering code that determines those outputs.
DONE-WHEN requires BOTH:
1. INDEPENDENT MEASUREMENT
   Measure the claimed property against a source independent of the
   artifact-generation/rendering assumption being tested.
   A measurement produced from the same broken assumption as the artifact is
   not independent proof.
2. VISUAL INSPECTION
   Load and actually examine the finished visual result.
   The render/view explains whether the independently measured fact makes sense
   as a visible result.
   Do not satisfy this by generating a screenshot nobody examines.
## WHO MAY INSPECT
The inspector is whoever actually loads and examines the finished result using
a capability that can genuinely inspect that output.
The inspector may be:
- Sleven;
- another human tester when one exists;
- C1 or another capable AI session using an actual rendered/browser/image view.
The inspector must be identified in the record.
Generating a screenshot, render, or browser result without any person/session
actually examining it does not satisfy inspection.
Sleven is NOT required to personally inspect every Level B or Level C item.
Owner/C1 escalation is reserved for the decision cases listed below.
## REQUIRED RECORD AND HOME
The visual-verification record belongs in the closure record of the work order
whose DONE-WHEN it satisfies.
Record:
- inspector;
- inspection time;
- exact URL/build/model/render/file;
- pass/fail;
- stated requirement;
- applicable Level A/B/C classification;
- where applicable, the independent measurement the visual result was read
  against.
Any supporting image, render, screenshot, or measurement artifact that needs to
persist goes under:
docs/evidence/
Use a filename carrying at minimum:
- date;
- meaningful subject;
- evidence type where useful.
Do not create a second independent status record for the same closure.
The work-order closure is the authoritative record of whether DONE-WHEN was
satisfied.
## ESCALATION
A separate C1/owner decision is required only when:
- a genuine design decision remains unresolved;
- acceptance criteria cannot establish success;
- rights/publication authorization is required;
- finished work materially departs from approved design;
- risk creates a genuinely new owner/project-head decision;
- whole-layer trust presentation requires owner judgment.
Otherwise, when DONE-WHEN is satisfied, the queue advances.
# 40. PROJECT-HEAD RESPONSIBILITY
C1 owns project-level interpretation and enforcement.
C1 should:
- ensure requirements exist before controls;
- include appropriate UX criteria in user-facing orders;
- inspect existing controls and OWNERS.md before creating controls;
- apply the external-resource NOT PERFORMED convention;
- use the existing full-sweep runtime receipt rather than inventing another;
- report the runtime a new control adds to the sweep, rather than letting it
  enlarge the sweep silently;
- apply Section 39 according to the observable effect of the change;
- ensure rendered-work evidence is written into the work-order closure;
- prevent duplicate/competing writers;
- resolve genuine design conflicts;
- prevent recurring failures from remaining prose-only lessons;
- keep UX governance compatible with the self-advancing queue.
C1 does not manually approve every CSS change.
# 41. USER-FACING PRIORITY ORDER
Apply this ranking only after hard preconditions are satisfied.
PRECONDITIONS:
- rights/publication authorization where applicable;
- legal requirements;
- security requirements;
- data-integrity requirements.
Within those boundaries:
1. Correctness and truth
2. User safety and accessibility
3. Primary-task completion
4. Clarity
5. Trust
6. Predictability and consistency
7. Low cognitive effort
8. Responsiveness/performance
9. Useful discovery
10. Visual polish
11. Novelty
A convenient interface that invents identity is a regression.
A beautiful interface that hides the answer is a regression.
# 42. PROCESS COST — THE DOCTRINE MUST EARN ITS KEEP
This doctrine deliberately adds work to some user-facing tasks.
That cost buys:
- independently specified behavior;
- repeatable acceptance criteria;
- fewer silent regressions;
- accessible behavior;
- objective visual evidence where needed;
- protection against self-validating controls;
- less dependence on memory or personal taste.
That cost must remain proportional to its value.
Signs that the doctrine is becoming ceremony include:
- acceptance criteria are routinely written but never evaluated;
- screenshots are generated but nobody examines them;
- measurements are recorded but never used to decide pass/fail;
- controls are routinely skipped because they are too expensive;
- workers copy boilerplate without understanding the protected behavior;
- user-facing throughput materially collapses while added process is not
  catching meaningful defects.
If that happens, do not quietly stop following the doctrine.
Trigger a doctrine review and simplify or redesign the expensive requirement.
# 43. ADOPTION ASSESSMENT — CAP THE INPUT
This doctrine does not take priority over existing queue work.
The initial adoption assessment may use ONLY:
- measurements already recorded;
- existing owner-use evidence;
- existing visual evidence;
- results available from one normal pass of the existing control runner;
- existing project records.
It must NOT create:
- new instrumentation;
- broad new browser crawls;
- new measurement systems;
- new UX test harnesses;
- a site-wide manual inspection campaign;
merely to complete the assessment.
Anything requiring new instrumentation or substantial new measurement becomes
a normal queue candidate with its own scope and DONE-WHEN.
The assessment output should remain approximately one page and contain only:
A. DETERMINISTIC CONTROLS BUILDABLE FROM EXISTING REQUIREMENTS
B. VERIFIED CURRENT UX DEFECTS ALREADY SUPPORTED BY AVAILABLE EVIDENCE
C. OWNER DECISIONS
## IMPORTANT: SECTION B MAY CORRECTLY BE EMPTY
An empty or nearly empty Section B is an expected and valid result today if
existing evidence does not support verified UX-defect claims.
Do not manufacture measurements, expand scope, reinterpret heuristics as
defects, or begin new inspections merely to fill the section.
If B is empty, that itself establishes:
THE PROJECT CURRENTLY HAS LITTLE RECORDED UX MEASUREMENT FROM WHICH TO CLAIM
CURRENT DEFECTS.
That makes Section A — useful deterministic controls based on real stated
requirements — the more important output.
Do not substitute this assessment for difficult work already assigned.
Then STOP and wait for Sleven's adoption decision.
### CLOSED 2026-09-08
The assessment was performed and accepted, and the doctrine adopted. Section B
was NOT empty: four defects were supported by evidence that already existed.
This section is history now; it does not run again.
# 44. FALSIFICATION / REVIEW TRIGGERS
This doctrine is not permanent truth merely because it was adopted.
Re-read it when:
- Citizen Compass becomes publicly available in its current form;
- the Collector rebuild gains a defined human-facing surface;
- the Collector rebuild ships to real users;
- a major new user-facing product category appears;
- repeated user evidence contradicts an important behavioral assumption;
- a doctrine-mandated control remains failing or routinely bypassed long enough
  to show the rule may be impractical;
- acceptance criteria are routinely written but not evaluated;
- visual requirements are routinely satisfied with unexamined or meaningless
  evidence;
- verification requirements materially reduce throughput without catching
  meaningful failures;
- the control runner's discovery or scheduling behavior changes, since
  Section 9 depends on how controls enter the sweep;
- architecture changes make a requirement obsolete;
- rights/legal/publication rules materially change.
A review does not automatically mean rewriting the doctrine.
Ask:
- Which assumptions became false?
- Which rules no longer produce useful outcomes?
- Which evidence contradicts the doctrine?
- Which requirements became obsolete?
- Which rules have become ritual?
- Which repeated failures expose a missing rule?
- Is the value of a requirement still worth its measured process cost?
C1 proposes revisions.
Sleven accepts, materially revises, or retires the doctrine.
If superseded, mark it through the project's existing governance mechanism
rather than leaving multiple apparently-current versions.
# FINAL PRINCIPLE
Citizen Compass should require as little unnecessary thought from the user as
possible while remaining completely honest about what it knows, what it does
not know, and what it is allowed to publish.
Answer first.
Never guess identity.
Rights are a gate.
Write the requirement before the control.
Automate what can be proven.
Measure, then look.
Scale verification to the risk.
Do not invent user evidence.
Do not invent interfaces.
Do not create work merely to satisfy the doctrine.
Make the doctrine earn the time it costs.
And never let the person, session, control, renderer, or system producing an
artifact be the sole source of truth used to prove that artifact correct.
