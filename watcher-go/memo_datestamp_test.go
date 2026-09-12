package main

// D11 - a memo filename that already carries a date must not get a second one.
//
// classifyMemo stamped the filing date on the front unless the name already
// began with TODAY's stamp. A memo written with any other date therefore got
// two:
//
//     2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md
//
// Seen twice on 2026-08-30. Cosmetic, but it sorts a tray by the day the file
// was FILED while displaying the day it was WRITTEN, with neither labelled.

import "testing"

func TestAFilenameKeepsItsOwnDate(t *testing.T) {
	for _, name := range []string{
		"2026-08-31_written-tomorrow.md",
		"2025-01-02_written-last-year.md",
		"2026-08-30-with-dashes.md",
	} {
		if !reLeadingDate.MatchString(name) {
			t.Errorf("%q opens with an ISO date and would be stamped again", name)
		}
	}
}

// THE OTHER DIRECTION. A name with no date must still get one, or the fix
// silently turns off the stamping it was protecting.
func TestAFilenameWithNoDateStillGetsOne(t *testing.T) {
	for _, name := range []string{
		"owners-md-is-yours.md",
		"update.md",
		"2026-08_not-a-full-date.md",
		"v2026-08-31_prefixed.md",
		"notes-2026-08-31.md", // a date INSIDE the name is not a leading date
	} {
		if reLeadingDate.MatchString(name) {
			t.Errorf("%q does not open with an ISO date but would be left unstamped", name)
		}
	}
}
