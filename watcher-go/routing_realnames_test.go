package main

import "testing"

// The actual filenames that misrouted, and the ones arriving now.
func TestTheFilenamesThatActuallyMisrouted(t *testing.T) {
	cases := []struct {
		name  string
		title string
	}{
		{"prompt-code-worker-and-update-feed-2026-08-15.md", "# PROMPT FOR CODE — the worker and the update feed"},
		{"prompt-code-worker-and-release-feed-2026-08-15.md", "# PROMPT FOR CODE — publish an update feed so collectors can update"},
		{"prompt-code-worker-and-version-feed-2026-08-15.md", "# PROMPT FOR CODE — deploy the Worker and publish the version feed"},
		{"ADDENDUM_roadmap-watcher-heartbeat-2026-08-15.md", "# ADDENDUM — a stopped watcher must not look like an update saying nothing"},
		{"prompt-code-onmachine-reader-2026-08-15.md", "# PROMPT FOR CODE — read the board on the machine"},
		{"WORKORDER_roadmap-watcher-2026-08-14.md", "# WORK ORDER — do NOT key on updateDate"},
	}
	for _, c := range cases {
		if isUpdateDoc(c.name, c.title) {
			t.Errorf("MISROUTED as an update doc: %s", c.name)
		}
		if isHandoffDoc(c.name, c.title) {
			t.Errorf("MISROUTED as a handoff doc: %s", c.name)
		}
	}
}
