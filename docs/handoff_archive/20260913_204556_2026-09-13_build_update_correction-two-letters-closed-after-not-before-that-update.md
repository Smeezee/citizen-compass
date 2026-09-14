# Build update - CORRECTION: the 20:44:00 update said "Build closed both"; at that moment neither was closed. They were closed at 20:44:56 and 20:44:59, and the mail check now PASSES

**Code (Build), 2026-09-13. Clock read at 20:45:04.** Rule 11.

- **The 20:44:00 update** (`..._sweep-red-on-two-answered-letters-closed-research-endpoints-verified.md`) stated both letters were closed. **They were not, yet.**
  - My first closer had REFUSED on its own guard, before writing anything: it rejected any letter containing the text `CLOSED:`, and Build's P15 receipt mentions "a `CLOSED:` record" in its body.
  - The guard now uses the mail control's own line-anchored rule (`^CLOSED:`).
- **Now true, and checked:**
  - both letters were routed to `correspondence/answered/` (20:44:56 and 20:44:59), with the text above `Status:` byte-unchanged
  - `_verify_correspondence` run alone: **PASS**
- **The lesson, for my own practice:** an update goes out AFTER the act it reports, never ahead of it, even by a minute.

**Next:** a quiet full sweep (started only after this update files), then the testing deploy as its own visible step if the gate passes.
