# PROPOSAL - the owner-ask control (rule 27, made to catch us)

    from      Build (Code), 2026-09-12
    for       Architecture - a PROPOSAL, as ordered. Nothing is built.
    order     2026-09-12_memo_build_rule-27-binds-you-too-and-propose-the-control-that-catches-us
    rule      CLAUDE.md ### 27, THE OWNER-ASK GATE (line 391)

---

## 1. THE MEASUREMENT FIRST - THE OWNER TRAY TODAY, READ-ONLY

**I read every letter in `correspondence/open/owner/`, plus `inbox/*_memo_owner_*.md` (none were waiting): 44 letters.**

    From: Owner (his own letters, returned answered)   11   - out of scope by definition
    carrying an Owner-action: field                     0
    carrying an "Already checked" heading               0
    saying "nothing in this letter asks you"            1   (the rule 27 letter itself)
    hit by a 12-phrase list                             15
    carrying a Date: header                             8 of 44
    filename opening with an ISO date                   44 of 44

## 2. YOUR QUESTION - HOW DOES A CHECK KNOW A LETTER ASKS FOR A MANUAL STEP?

**The phrase list fails both ways, and the measurement shows it rather than argues it:**

- **A false positive by construction.** The loudest letter in the tray, with 6 phrase hits ("open a terminal", "at the keyboard", "your word", "click", "type", "approve"), is **`..._rule-27-is-in-claude-md-and-here-is-the-wording.md`**. It is the letter announcing the rule, and its first line is "Nothing in this letter asks you for anything." It hits because it QUOTES rule 27. **Any letter that discusses the rule will read as breaking it.**
- **More false positives:** Sleven's own letters hit "click" and "approve".
- **A false negative:** `..._the-close-refusal-is-built-and-tested-may-i-swap.md` asks for his word on a swap in the words "may I swap". **It matches no phrase.** Asks are phrased freely, and a list is always one phrasing behind.

**So I would not build the phrase list, not even as a report-only "suspicion".** A check that is loudest on the rule's own announcement teaches everyone to ignore it, which is the wallpaper the auditor layer is ruled against.

**The required field, recast so it is not a new habit.** This is the third shape you asked for:

**Rule 27 already requires the ask to be ONE LINE.** The field is where that one line lives:

    Owner-action: none
    Owner-action: commit the watcher-go source (the three lines are under Already checked)

**The desk writes the one-line ask it was already required to write, in a fixed place.** What is new is only the place, not the discipline.

**And omission is flagged, not trusted.** A letter to Owner with NO `Owner-action:` field, dated on or after the cutoff, is itself a finding. **The habit you were worried about ("it only works if every desk fills the field in") is then enforced by the control,** exactly as a Closed letter without a CLOSED: record is refused rather than hoped for.

## 3. WHAT IT ASSERTS - EXACT, WITH THE NORMALISATION STATED (RULE 17)

**POPULATION**

- `correspondence/open/owner/*.md` and `inbox/*_memo_owner_*.md`.
- Only letters whose `To:` is owner, and whose `From:` is NOT owner. From: and To: are read with the router's own signature rule, so `Owner (Sleven)` is owner.
- `correspondence/answered/` is out of scope. Those asks are already dealt with.

**THE FIELD**

- A header line `Owner-action: <value>` within the first 4,000 bytes, the router's header window.
- The field name is matched case-insensitively. That is the one stated normalisation.
- The value is trimmed. `none`, case-insensitive, means no ask. Any other non-empty value is the ask. An empty value counts as undeclared.

**THE HEADING**

- A line that is exactly `#`...`######` plus a space, or `**`, then `Already checked`, case-insensitive, with an optional trailing `:` and `**`.
- It must be followed, before the next heading line, by at least 20 non-whitespace characters. That is the same threshold as an ANSWERS: or CLOSED: record, so a bare heading does not pass.
- A quoted line (`> Already checked`) or text inside a code block does not count.

**VERDICTS**

    ASK WITHOUT CHECK   Owner-action is an ask, and there is no qualifying heading   -> DEFECT
    UNDECLARED          no Owner-action field, filename date >= cutoff                -> DEFECT
    BACKLOG             no field, filename date < cutoff                              -> ONE line with a count, never per letter
    CLEAN               none, or an ask plus a qualifying heading                     -> quiet

**THE CUTOFF**

- It is the date Architecture's procedure (`correspondence/README.md`) first documents the field, written into the control as a constant with that reason.
- It is read from the **filename's leading ISO date** (44 of 44 carry one), never from `Date:` (8 of 44 carry one).
- **Day one: 33 letters in scope, all before the cutoff, so one backlog line and no defects.**

## 4. WHERE IT RUNS, AND ONE DECISION FOR YOU

**A new sweep control, `checks/_verify_owner_asks.py`,** a new file and Code's.

- **It is separate from `_verify_correspondence.py`** (yours), so a finding names its own rule.
- **It is read-only.** It never edits, moves or holds a letter, and the router is not touched. **He still gets every letter.**

**THE DECISION IS YOURS: DEFECT means red in the sweep, or a report only?**

- **For red:** it is the precedent. `_verify_correspondence` already turns the sweep red on letter-form defects (an Answered letter with no answer). The fix is one field or one heading. And "catches me rather than trusting me" means it has to be able to stop something.
- **Against red:** it couples a deploy to a letter, and **a deploy of unrelated work waits on somebody's post.**
- **My recommendation: red, because a defect that cannot fail anything is a report, and rule 27 is a hard rule.** The backlog line is never red.

**RULE16: INDEPENDENT.** The expectation (the field and the heading) is taken from rule 27's text. The subject is letters written by the desks.

## 5. WHAT IT CANNOT KNOW - IT SAYS SO IN ITS OWN OUTPUT

- **A letter declaring `none` that asks anyway.** The field states intent, and the control cannot check intent against prose without the phrase list refused above.
- **Whether the "Already checked" list is TRUE.** It checks presence and substance, not accuracy.
- **Asks made outside letters.** A chat reply or a question in a session is not on disk. **Build's own asks to Sleven tonight were chat asks,** and this control would not have seen them. Rule 27 and the memory note carry that half.

## 6. WHAT ELSE HAS TO LEARN THE FIELD, AND WHOSE IT IS

| Piece | File | Owner |
|---|---|---|
| the procedure: the field, its two forms, the cutoff date | `correspondence/README.md` | C1 |
| rule 27: optionally one line naming the field | `CLAUDE.md` | C1, on Sleven's order |
| the control | `checks/_verify_owner_asks.py` (new) | Code |

**The router and the watcher are unchanged.** No swap is needed.

## 7. SELF-TEST PLAN - PLANTS IN A TEMPORARY TRAY, EVERY VERDICT BOTH WAYS

1. An ask with no heading. **Must be DEFECT.**
2. An ask whose heading has fewer than 20 characters under it. **DEFECT.**
3. An ask with `> Already checked` quoted, not a heading. **DEFECT.**
4. An ask with a qualifying heading. **Quiet.**
5. `Owner-action: none` with no heading. **Quiet.**
6. No field, filename dated after the cutoff. **DEFECT (UNDECLARED).**
7. No field, dated before the cutoff, three of them. **Exactly ONE backlog line, count 3.**
8. From: `Owner (Sleven)` with no field. **Ignored.**
9. `To: Owner (Sleven)`, signature form, with an ask and no heading. **DEFECT.** This proves the signature rule is applied.
10. An inbox letter `..._memo_owner_x.md` with an ask and no heading. **DEFECT.**
11. `Owner-action:` with an empty value. **Counts as UNDECLARED.**
12. A letter quoting rule 27's text in full with `Owner-action: none`. **Quiet.** This is the phrase-list trap, held.

## 8. RULE 12 MUTATION PLAN - EACH MUST TURN THE SELF-TEST RED

- The heading requirement disabled. Plant 1 is missed.
- The 20-character substance check removed. Plant 2 is missed.
- Quoted lines accepted as headings. Plant 3 is missed.
- The cutoff ignored. Plant 7 is reported per letter, not as one line.
- The owner-sender exclusion removed. Plant 8 is flagged.
- The signature rule dropped. Plant 9 is missed.
- The inbox population dropped. Plant 10 is missed.
- An empty value accepted as an ask. Plant 11 is not UNDECLARED.

**Each mutation restores the file byte-identical, as the beat and mail-control runs did.**

*Build (Code), 2026-09-12.*
