# WORK ORDER — Citizen Compass: finish the Go migration, remove generate_handoff.py

Repo: `C:\Users\david\citizen-compass` (Windows). Go source in `watcher-go/`.

## Decision (settled — do not re-litigate)

The Go watcher (`inbox_watcher.exe`) becomes the **single writer** of
`LATEST_HANDOFF.md`. `generate_handoff.py` is removed.

It cannot be a straight deletion. Two defects exist in the Go path that Python
already fixed. Delete Python first and both become permanent.

## Context (minimum needed)

Both programs build `LATEST_HANDOFF.md` from `docs/handoff_archive/_updates_log.md`
and `_latest_raw.md`. Both are live. Last write wins. Observed 2026-08-01 twelve
seconds apart: Go emitted 50,535 chars, Python 93,132. Different logs
(`logs/inbox_watcher.log` vs `pipeline_log.txt`) is why it went unnoticed.

The size gap is Defect 1. The Go output is wrong, not terser.

---

## DEFECT 1 — invents entries that were never logged

**File:** `watcher-go/handoff_regen.go`, `parseUpdateEntries()`, line 108.

Splits on every `\n### `, so any `###` subheading inside an update body becomes a
phantom top-level entry and truncates the real entry it was cut from. Python
fixed this; see its `_parse_update_entries()` comment.

Measured against the live `_updates_log.md`: **44** real timestamped headers,
**61** total `###` headers → 17 phantoms. Both cap display at 20, so Go shows 20
fragments where Python shows 20 real entries.

### Replacement

```go
// Matches ONLY headers appendUpdate() writes:
//   ### 2026-08-01 00:11:55 — update_something.md
// Separator after the timestamp is not pinned (hyphen or em dash both parse).
var updateEntryHeaderRe = regexp.MustCompile(
	`(?m)^### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b.*$`)

func parseUpdateEntries() []string {
	raw, err := os.ReadFile(updatesLogPath())
	if err != nil {
		return nil
	}
	s := string(raw)
	locs := updateEntryHeaderRe.FindAllStringIndex(s, -1)

	// No recognisable headers (old or hand-edited log): return the whole file
	// as one entry rather than dropping content.
	if len(locs) == 0 {
		whole := strings.TrimSpace(s)
		if whole == "" {
			return nil
		}
		return []string{whole}
	}

	var entries []string
	// Preamble before the first header is kept, not discarded.
	if pre := strings.TrimSpace(s[:locs[0][0]]); pre != "" {
		entries = append(entries, pre)
	}
	for i, loc := range locs {
		end := len(s)
		if i+1 < len(locs) {
			end = locs[i+1][0]
		}
		if chunk := strings.TrimSpace(s[loc[0]:end]); chunk != "" {
			entries = append(entries, chunk)
		}
	}
	return entries
}
```

Add `"regexp"` to imports. Both edge cases above are required — they exist to
avoid silently dropping content.

---

## DEFECT 2 — classifies documents by scanning their prose

**File:** `watcher-go/handoff.go`, `isHandoffDoc()` line 49, `isUpdateDoc()` line 65.

Both call `firstRunesUpper(text, 500)` — scanning the document body for keywords.
Any update that merely mentions "handoff" early is classified as a full handoff
doc: it overwrites `_latest_raw.md`, replaces the entire PROJECT NOTES section,
and never reaches the updates log. Python fixed this with a title-only check; see
its `_title_line()` comment.

Live, not theoretical.

### Replacement

Add:

```go
// titleLine returns the doc's own title, uppercased -- its first markdown
// heading, or its first non-blank line. A doc's type is stated by its title,
// not by whatever it mentions in passing.
func titleLine(text string) string {
	for _, line := range strings.Split(text, "\n") {
		stripped := strings.TrimSpace(line)
		if stripped == "" {
			continue
		}
		if strings.HasPrefix(stripped, "#") {
			return strings.ToUpper(strings.TrimSpace(strings.TrimLeft(stripped, "#")))
		}
		return strings.ToUpper(stripped)
	}
	return ""
}
```

In **both** functions replace `head := firstRunesUpper(text, 500)` with
`head := titleLine(text)`. Remove `firstRunesUpper` if nothing else calls it.

**Do not change evaluation order:** `isHandoffDoc()` runs before `isUpdateDoc()`,
filename hints before title. A doc matching both is a full handoff.

---

## KEEP — Go-only feature

`handoff_regen.go:182` writes `# LATEST_HANDOFF.md — Update #N — <date time>` at
the top of the output. Python has no equivalent. Preserve it.

---

## EXECUTION ORDER — do not reorder

Run after Task 2 (source 1 re-acquisition) and after the CC-10/CC-12 schema order.

1. Fix Defect 1. Preserve both edge cases.
2. Fix Defect 2 via `titleLine()`.
3. Prove both against known-bad input. HARD RULE 12 applies — reading the diff
   and declaring it fixed does not satisfy it.
   - Defect 1: parsing the live `_updates_log.md` returns **44**, not 61. Every
     entry begins with a timestamped header. A body with `###` subheadings yields
     exactly one entry.
   - Defect 2: an update-titled doc mentioning the keyword in its first 500 chars
     routes to the updates log. Assert `_latest_raw.md` is unchanged.
4. Regenerate with the fixed binary; compare to `generate_handoff.py` output.
   Should match modulo the version marker. **If they still disagree there is a
   third difference — stop and report, do not assume Go is now correct.**
5. Only then delete `generate_handoff.py`. Also retire `_verify_generate_handoff.py`.
   Check `generate_ai_brief.py` for shared code before deleting anything it needs.
6. Add to `CLAUDE.md`:
   - The Go watcher is the ONLY writer of `LATEST_HANDOFF.md`. Never invoke a
     generator directly; dropping into `inbox/` is the sole supported path. A
     second writer produced a silently divergent context document for three days.
   - The watcher logs to `logs/inbox_watcher.log`. `pipeline_log.txt` belongs to
     the retired Python path; diagnosing watcher health from it gives the wrong
     answer.

## Out of scope — do not act on

Ollama/local AI compression is deliberately disabled by the owner and parked. Do
not re-diagnose it. The watcher process and its Scheduled Task are verified
healthy and need no work.
