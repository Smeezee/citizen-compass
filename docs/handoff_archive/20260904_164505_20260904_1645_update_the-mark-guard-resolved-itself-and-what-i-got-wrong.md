# Update — the mark contradiction resolved, and I had it backwards for an hour

**2026-09-04 · Code**

## The control was right. My anecdote was the wrong evidence.

At 16:20 I reported that `_verify_community_mark.py` said the mark detector
could not tell marked from unmarked, while I had watched the build refuse 241
unmarked images and accept them once marked - and that I could not say which was
right.

**I could say. I just had not measured it.** The pre-marking originals were
preserved by whoever ran the marking, at
`_to_delete/images_unmarked_20260904T204123Z/`, so a clean pair of the same file
was available the whole time:

    unmarked sha 13f33ddf8df5cbaa  19914 bytes
    deployed sha 13f33ddf8df5cbaa  19914 bytes
    byte-identical: True

    variant white   unmarked 0.0236   deployed 0.0236
    variant black   unmarked 0.0000   deployed 0.0000
    has_mark(deployed): False, both variants

**The images in the payload were never marked.** The build regenerates
`_deploy` and copies the images fresh from source, so my 15:47 build overwrote
the marks applied at 15:42. Five minutes of marking, undone by the next build,
and I reported the build's "241 CIG-sourced image(s), all carry it" as evidence
the guard worked.

It was evidence of a moment, not of a mechanism. The control was measuring the
mechanism.

## What actually settled it

The register is the switch, exactly as the control's own message said. Between
15:16 and now, `data-layer/cig_assets.json` has been rewritten repeatedly - most
recently at **16:41:26, one minute before I looked** - and the 241 images have
been **deregistered**:

    now: 258 assets, all kind=model, source cig-holoviewer
         images registered: 0
    build: "community mark: 0 CIG-sourced images registered - guard armed,
            nothing to mark"

With no images claiming to be CIG-sourced, there is nothing for the mark guard
to enforce, and `_verify_community_mark.py` **passes 13 of 13**.

That is consistent rather than convenient: the control's own reported note says
it is **not established** whether those 241 thumbnails are CIG assets,
screenshots or renders, and Part 2 of the image work order plans to replace them
with our own renders. Deregistering them pending that answer is a coherent
position. **It is not mine and I did not take it** - someone else did, and I am
recording what I observed rather than endorsing it.

## The source notice is unaffected

258 models are still registered, so `_SRC_BLOCK` is still built and the notice
still renders on all four ship-content pages, `_inspect.html` included. That was
the point of my `_SHIP_CONTENT_PAGES` line and it still holds.

## Lesson worth keeping

**A build passing is not a check working.** I watched a guard refuse and then
accept, concluded it discriminated, and offered that against a control that was
measuring the detector directly. The guard's two runs differed because its
REGISTER changed between them, not because its detector had judged anything. A
green build says the conditions for refusal were not met; it does not say the
mechanism can detect them.

## State

Build clean, exit 0. Sweep running. Nothing deployed yet - the registry moved one
minute before this sweep started and I will check it has not moved again before
uploading anything.
