# CORRECTION — extracted game textures are NOT the granted class. C2 was wrong.

    from    C2, 2026-08-06
    for     C1 -> Claude Code
    amends  docs/FINDING_images-why-cstone-fails-and-the-four-options.md §2A
    trigger CIC declined to research p4k icon extraction and gave its reason.
            C2 checked the reason. CIC is right.

---

## 1. WHAT C2 SAID, AND WHY IT IS WRONG

C2 wrote, of icons inside `Data.p4k`:

> "Those are CIG's own assets, which is precisely the granted class under RSI
> ToS §XIII.D — *images, graphics or artwork* — for a free, ad-free fansite."

**That is a misreading of the clause, and it is C2's error.** The actual text:

> "permission to reproduce and redistribute on your fansite to end users,
> **certain** RSI Services-related images, graphics or artwork (the "RSI Fansite
> Content")"

**"Certain" is doing the work.** The grant covers a *designated set* CIG makes
available for fansite use. **It does not say "any image CIG has ever made."**

**A texture pulled out of the shipped game archive was never designated for
anything.** It is copyrighted CIG expression that happens to be reachable.
**Reachable is not licensed.**

**C2 stated the opposite as fact and recommended a build on it. Retracted.**

---

## 2. THE SECOND PROBLEM, WHICH IS SEPARATE AND ALSO REAL

`Data.p4k` ships with **partial encryption.** Circumventing technical protection
on copyrighted content is a distinct legal question from copyright itself — it is
not answered by the content being non-commercial or the site being free.

**Worth stating precisely, because the project's own record matters here:** the
`defaultProfile.xml` extraction **decrypted nothing.** That entry was
ZStandard-compressed, not encrypted, and was read as a normal archive member.
**So nothing done to date crossed that line.**

**But "we have opened this archive before" is not a licence to open all of it**,
and C2 used that precedent to argue for the texture route. **That argument does
not hold.**

---

## 3. THE DISTINCTION THAT ACTUALLY GOVERNS THIS PROJECT

**This is the line, and it should be written into the standing rules:**

    FACTUAL DATA extracted from game files
      item names, stats, prices, quantities, coordinates, blueprint recipes,
      contract structures, fuel rates
      -> facts and numbers. This is what the whole project runs on and it is
         a fundamentally different category.

    CREATIVE ASSETS extracted from game files
      textures, icons, 3D models, artwork, audio, written descriptions
      -> copyrighted expression. NOT covered by §XIII.D unless CIG designated
         that specific asset for fansite use.

**The project has always been on the correct side of this and did not know it
was a line.** The description-rights hold (`stdItem.DescriptionText`) is the
same principle already applied to text. **Textures are the same principle
applied to pictures. It was inconsistent to hold one and not the other.**

---

## 4. WHAT THIS COSTS — both self-sourced options drop out

    Option A  extract item icons from Data.p4k     WITHDRAWN - §1, §2
    Option B  render thumbnails from .cga models   WITHDRAWN - same reason.
                                                   A model is creative
                                                   expression exactly as a
                                                   texture is.

**That was C2's recommendation and its fallback. Both gone.**

**Note this does NOT touch the 3D viewer question**, which is a separate
decision Sleven has already been making with models he obtains himself. **It
means C2 should not be recommending an automated pipeline that pulls artwork out
of the archive at scale.**

---

## 5. WHAT REMAINS

    C  the official RSI Fan Kit          the only unambiguously licensed source.
                                         Nobody has looked at what is in it.
    D  community sources WITH PERMISSION Cornerstone, the wiki. Their images,
                                         their call. Ask, do not assume.
                                         The wiki may carry a CC licence -
                                         unchecked.
    E  ask CIG directly                  the separate-licence path named in
                                         their own terms. Parked by Sleven.
    F  in-game screenshots               what every SC fan site actually runs
                                         on. See the caution below.

**On F, honestly:** the entire Star Citizen fan ecosystem is built on player
screenshots, and CIG plainly tolerates it. **Tolerance is not a licence, and
"everyone does it" is not a position this project should build on.** It is worth
finding out whether CIG has ever said anything explicit about republishing
player screenshots — **that is a research question, not an assumption to make.**

---

## 6. THE LESSON WORTH KEEPING

**C2 read a clause it wanted to be permissive, and it read it permissively.**

The same thing happened earlier today with the subscription clause — C2 filed a
paraphrase from memory and repeated it as fact. **Both times the correction came
from checking the actual words.**

**Standing rule to apply going forward: any claim about what the Fan Kit
Agreement or the ToS permits gets quoted verbatim before it is acted on, and
"certain" and similar qualifiers get read as load-bearing.** Rule 8 already puts
this with Sleven; C2 should stop forming confident positions and start surfacing
quotes.

---

## 7. NOT VERIFIED

- **Whether the Fan Kit contains anything usable as item artwork.** §5C. Still
  the highest-value open question and still unchecked.
- **Whether the SC wiki's images carry a reusable licence.** Unchecked.
- **Whether Cornerstone permits reuse.** Never asked.
- **Whether CIG has published anything about player screenshots on fan sites.**
  Never looked for.
- **C2 is not a lawyer.** None of this is legal advice. Hard rule 8.
