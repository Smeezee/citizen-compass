# Update — order received: rebuild clears the leaked comment

**2026-09-04 · Code**

Received `docs/ORDER_rebuild-clears-the-leaked-comment-2026-09-04.md` from C1,
found while checking why my sweep came back red.

Sleven sent a screenshot of the Carrack ship page on testing with **twelve lines
of internal notes rendered as visible text above the ship name.**
`cc_glossary.inc.html` wrote the marker it looks for in full, angle brackets and
terminator included, inside its own opening comment. HTML comments do not nest,
so `strip_comments.py` closed on the first terminator - correctly - and left the
rest as page content. The stripper was right; the include was lying to it.

C1 has fixed the source and added `checks/_verify_no_leaked_comments.py`. **My
job is the rebuild and redeploy** - the fix is in the source and the two
deployed pages still carry the leak.

Doing that now.

**Note on the red sweep I reported minutes ago.** The failure was
`_verify_rule16_labels.py`, and the cause is C1's new control having no RULE16
label yet. That file was created at 09:15:30 while my sweep was running, which
is why it appeared mid-flight. It is a genuine finding by that control, not
noise - the debt list does not accept additions - but it is C1's brand-new work
and I am not editing it out from under them. Reporting instead.

My own new control, `checks/_verify_count_line.mjs`, ran and passed in that same
sweep.
