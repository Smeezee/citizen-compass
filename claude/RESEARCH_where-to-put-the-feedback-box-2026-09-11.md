# RESEARCH — where to put the feedback box

**Run 2026-09-11 by Sleven in Perplexity, prompt
`claude/PROMPT_perplexity-where-to-put-the-feedback-box-2026-09-11.md`. Assessed by the
Adjutant desk. Feeds Architecture's pick on placement and wording; the destination is
already recommended and not reopened.**

## ASSESSMENT

**Honest about its own weakness, which is the useful part.** It labelled the evidence, named
the interested parties, and said plainly where no study exists: inline versus floating versus
footer has never been compared head to head, item-level versus page-level has no direct test,
and nobody has measured an optional email field with no promised reply. It refused to invent
"time to first report" as an established measure.

**One claim needs discounting before anyone builds on it.** The 10% against 65% number is
presented as evidence that the word "feedback" loses clicks. Read the study description in
the answer itself: the comparison is a feedback link against **"Finish"**, the primary button
ending a government transaction. That is a different button doing a different job, not the
same button relabelled. The direction is plausible; the size of the effect is not transferable
to our page, and its own follow-up source says wording effects flipped sign between pages.

**Ages matter here.** The strongest placement number is Wikipedia, 2012, desktop era. The
field-count numbers are 2010 and 2013, from marketing forms. The touch-target numbers are the
only ones that carry over cleanly, because they measure fingers.

## WHAT IT MEANS FOR US

- **A report control on each ship card**, not one box at the bottom, is the recommendation,
  and it fits what this site is for: the visitor who can see the wrong price is the one
  holding the correction.
- **This collides with two findings we already have.** Run 3's T-018 says the card notes are
  already clipped, and run 4's M-009 says the controls on a card are already 30 px where 44 px
  is the floor. A per-card control has to be designed into that, not added on top of it.
- **One free-text field.** No category picker.
- **Do not call it "feedback".** Use words about the problem, not about us.
- **No pop-up, no timed prompt, no floating tab, no leaving the site.** This agrees with the
  destination already recommended.
- **Success cannot be a submission count.** Architecture said the same thing this evening for
  a different reason, and the research backs it: below roughly 30 responses, read them, do not
  count them.

## ROUTED

To Architecture:
`memo_architecture_the-feedback-research-is-in-per-card-one-field-and-do-not-call-it-feedback.md`.

---

## PERPLEXITY'S REPLY, VERBATIM AS SLEVEN CARRIED IT IN

Ranked recommendation

1. Placement: Put the control inline, next to each item — not in a floating tab, not only in the footer, and never gated behind a final "done" step. Banners and end-of-flow-only placements are the two patterns evidence directly shows failing.
2. Granularity: Keep it per-card, not one page-level box. No study proves this head-to-head, but every real system that gets used at scale (OpenStreetMap, Wikipedia edits) is item-level, and the one relevant efficiency study only questioned the most granular option (per-fact), not per-item.
3. Wording: Avoid "Feedback" or "Give feedback" as the label. The one hard number available shows feedback-branded wording gets clicked far less than neutral/task wording.
4. Fields: One field. A single free-text box. No required dropdown, no required category. Optional email is fine but there's no data on its cost — treat it as a guess, not a proven safe choice.
5. Avoid: pop-ups, timed/forced prompts, off-site redirects, star/NPS scales. Weakest evidence of any answer here, but everything found points one direction.
6. Mobile: Control and tap target at least 1cm (≈48px), sitting in the lower two-thirds of the screen where a thumb reaches without re-gripping.
7. After send: A short, plain "what happens next" line. Don't over-explain outcomes.
8. Low traffic: Don't judge the feature by counting submissions. Read every single one by hand instead.

Below is the evidence behind each, labeled as you asked. A quick translation: EVIDENCE = real numbers/study. WEAK EVIDENCE = respected org says so, no numbers. VENDOR = numbers are real but the source sells something related.

1. Placement
No study tests inline-vs-floating-vs-footer-vs-nav against each other directly — flagged as a real gap, and nobody has studied this on a catalog/reference site specifically (all data is government forms, Wikipedia, or maps).
What does exist:

* GOV.UK's own design team admits their banner-based feedback link causes "banner blindness" and is still unresolved as of writing — WEAK EVIDENCE (GOV.UK Design System, https://design-system.service.gov.uk/components/feedback/, undated).
* A real before/after case: banner-only feedback got 15 clicks and 10 completed forms out of 8,600 visitors — EVIDENCE, but only for the "before" baseline, not the fix (DfE Design Histories, https://design-histories.education.gov.uk/check-an-early-years-qualification/post-59, 2025).
* Wikipedia's large randomized test (9.4M page views) found bottom-of-page feedback links converted worse than a standard top-of-page control — EVIDENCE, but this is 2012, desktop-era, so treat with caution (Wikimedia Meta-Wiki, https://meta.wikimedia.org/wiki/Research:Article_feedback/Stage_3/Conversion_and_newcomer_quality, 2012).
* GDS separately called out gating feedback behind a final "Finish" click as a dark pattern that suppressed responses — WEAK EVIDENCE, no numbers given (GOV.UK Design Notes, https://designnotes.blog.gov.uk/2015/08/13/how-good-is-your-service-how-many-users-give-up/, 2015).

No source at all addresses top-navigation placement. That's a stated gap, not a "weak" answer — nobody has measured it.

2. Item-level vs. page-level
No direct comparison exists. Closest real data:

* A peer-reviewed crowdsourcing study found the most granular level (fact-by-fact, finer than "per item") isn't always worth it — sometimes fixing the source data is cheaper than crowdsourced per-fact correction — EVIDENCE, but this is about data infrastructure, not a "report" button UI (Acosta et al., Semantic Web journal, https://journals.sagepub.com/doi/full/10.3233/SW-160239, 2016).
* OpenStreetMap's per-item reports: about half go unanswered by anyone, ever — EVIDENCE from a large real dataset, but informal (a contributor's own analysis, not peer-reviewed) (OSM diary, https://www.openstreetmap.org/user/joost%20schouppe/diary/43057, 2018).

Google Maps' "suggest an edit," Genius corrections, and IMDB corrections were all checked — none publish usage numbers. This whole question is under-evidenced; per-item is the reasonable choice by analogy to what large systems actually ship, not because it's been proven better.

3. Wording
Best-evidenced of your eight questions, but still not a direct test of your five exact phrases.

* A UK government team tested four button labels in sequence on real traffic: "Give feedback" got 10% clicks; "Finish" got 65%. Explicitly labeling something as feedback tanked response — EVIDENCE, real numbers (Inside GOV.UK, https://insidegovuk.blog.gov.uk/2014/04/23/book-a-practical-driving-test-how-changing-the-wording-on-one-button-increased-clickthroughs-by-600/, 2014 — near the mobile-first cutoff, treat as borderline).
* A follow-up test showed wording effects flip by page: the same kind of change was +5.1% on one page and −18.8% on another — EVIDENCE that wording doesn't generalize (Inside GOV.UK, https://insidegovuk.blog.gov.uk/2016/08/23/absolutely-fabulous-testing/, 2016).

No source tested "Something wrong?" vs "Suggest a correction" vs "Was this helpful?" against each other. Also: nobody has measured whether wording changes what people submit (real correction vs. spam vs. rant) — stated gap, not filled with a guess.

4. Fields

* One added required field cut conversion by 11.9% in a live randomized test — EVIDENCE, VENDOR-ADJACENT (MarketingSherpa, https://marketingsherpa.com/article/case-study/how-one-additional-form-field, 2013, pre-2015/B2B context).
* Analyzing 40,000+ pages: single-line fields cost little; free-text boxes and dropdowns cost a lot more — EVIDENCE, VENDOR (HubSpot, https://blog.hubspot.com/blog/tabid/6307/bid/6746/which-types-of-form-fields-lower-landing-page-conversions.aspx, undated).
* Short forms lose people fastest per extra question in the first 15 questions — meaning your tiny form sits in the steepest part of the drop-off curve, so every field really does cost you — EVIDENCE, VENDOR (SurveyMonkey, https://www.surveymonkey.com/curiosity/survey_questions_and_completion_rates/, 2010, desktop-era).

On your specific question — an optional email field with no promise of reply: I found nothing. A UK government page describes exactly this pattern but literally states "number entering email: not stated." This is the one clean gap in the whole brief — there is no published answer, and I'm not going to invent one.

5. What kills it
This is the weakest-evidenced section overall — mostly documented usability-test observations, not statistics.

* Pop-ups before the user has done anything: one tester threw his phone; Google penalizes intrusive interstitials, "especially on mobile" — EVIDENCE (single observed case) / WEAK EVIDENCE (the Google penalty claim) (NN/g, https://www.nngroup.com/articles/popups/, 2019/2024).
* A forced feedback pop-up with no skip option made a user pick "thumbs down" because of the interruption itself — a real, documented case of the prompt poisoning its own data (NN/g, https://www.nngroup.com/articles/user-feedback/, 2023).
* Nobody has measured off-site redirects (Google Forms/Typeform) or floating scroll-tabs specifically. Both are stated gaps — the "avoid these" guidance is real but has no numbers behind it.
* GOV.UK deliberately built theirs as inline, on-page, not a redirect, and uses binary "useful/not useful" rather than stars — a design decision, not a proven comparison (Inside GOV.UK, https://insidegovuk.blog.gov.uk/2022/03/28/making-the-gov-uk-feedback-component-more-accessible/, 2022).

6. Phones
Best-evidenced technical section, though it's general touch research, not feedback-widget-specific.

* Minimum reliable tap target: ~1cm × 1cm, based on multiple real touchscreen studies including a 120-million-touch-event dataset — EVIDENCE (NN/g summary, https://www.nngroup.com/articles/touch-target-size/, studies from 2006–2011, but touch-specific so still applicable).
* Apple/Google/Microsoft's own current specs: 44pt / 48dp / ~13mm minimum — EVIDENCE, current official guidance.
* A 1,333-person observational study found 49% of people use their phone one-handed, and of those, 67% use their right thumb — this is the basis for "thumb-zone" maps (bottom-center reachable, top corners not) — EVIDENCE, though from 2013, before today's larger phones, so absolute reach distances may be smaller now than measured (Steven Hoober / UXmatters, https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php, 2013).

No one has tested a "report a problem" button's size/placement specifically — this is an inference from general touch research, not a direct measurement.

7. After the send

* The closest real study: explaining how something was processed (procedural transparency) raised trust, especially when someone got a worse outcome than expected — but over-explaining the specific outcome actually lowered trust again (a bell curve, not "more is better") — EVIDENCE, peer-reviewed, but it's a grading-fairness study, not a feedback form, so it's an analogy (Kizilcec, CHI 2016, https://rene.kizilcec.com/wp-content/uploads/2016/01/kizilcec2016information.pdf).
* A 2024 study found generic transparency text about data use doesn't actually make people feel informed — implementation quality matters more than just having a line of text (Kyi et al., CHI 2024, https://www.franziroesner.com/pdf/kyi-purposes-chi24.pdf).

Nobody has tested this on an actual feedback confirmation screen. This is analogy, not direct proof — say a short line like "a human reviews this" and don't overload it with process detail.

8. Low traffic

* The core stat to internalize: if 5 out of 5 people report success, the real rate could be as low as 48% — small counts lie to you — EVIDENCE (MeasuringU, https://measuringu.com/conf_intervals/, 2004, but this is math, not tech, so it doesn't age out).
* Nielsen Norman Group's standard advice: below ~30 responses, stop treating counts as statistics and switch to reading each one qualitatively — this is well-established guidance, not new data, but it's exactly built for your situation (NN/g, https://www.nngroup.com/articles/5-test-users-qual-quant/, 2021).
* Heuristic evaluation (3–5 people reviewing the page against known usability problems) needs zero visitors at all — a real way to check quality when traffic won't give you numbers (NN/g, https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/, 2023).

"Time-to-first-report" and "impression-to-click ratio" — I looked specifically for these. No named UX source studies either one. They're reasonable homemade heuristics, not established practice — don't cite them as if they were.

Bottom line on evidence quality overall: almost nothing here is a controlled experiment run on a site like yours. Most hard numbers come from government transaction forms or Wikipedia, both very different from a low-traffic hobby reference site. Treat the ranking above as the best synthesis available, not as proven fact.
