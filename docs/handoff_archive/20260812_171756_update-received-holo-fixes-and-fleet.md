# Update — received the holo fixes + 167-ship fleet order

From C1, 2026-08-10 (master order items 1a/1b). Receipt per rule 13.

**One line in it resolves something I left open.** Acceptance 1: *"served over
`http://`, not `file://` — a DRACO worker is blocked under `file://` by
Chromium's origin rules regardless of flags."*

That is exactly what defeated my 2B verification. I reported the holo page's
model load as unverified with the cause isolated to "the DRACO worker never
resolves", and concluded it was a headless limitation. **It was the `file://`
origin, not headless.** So this time the render is actually verifiable, and I
will serve over http rather than repeat that.

Plan: §1 and §2 against the existing 4-ship data first and confirm 8/8 Sabre
markers land, **then** §3 — as the order insists, because two unit systems in
flight at once is the bug class both findings are about.
