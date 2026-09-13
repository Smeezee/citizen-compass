package main

// boot_test.go - the ship conditions for BOOT.md, each one run against a real
// temporary tree (Architecture, 2026-09-12). v0 does not go live unless these
// pass, and each was also run against a deliberately broken generator to show
// it can fail (rule 12).
//
//	1  a planted change to EVERY source moves the page
//	2  a missing source shows as MISSING, never blank, never an old value
//	3  two sources that disagree are both named
//	4  every section names the files it read, directly under its heading
//	+  the LIVE.md prose trap that caught the Python prototype
//	+  the page states what it cannot know

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"citizencompass/pkg/pipelinelog"
)

// THE OTHER HALF OF THE CHANGE, run for real: regenerateHandoff writes BOOT.md,
// and LATEST_HANDOFF.md's wrong auto section is gone in the same cycle, replaced
// by one line pointing at it. A logger is set because logMsg has no nil guard.
func TestHandoffPointsAtBootAndTheAutoSectionIsGone(t *testing.T) {
	r := bootTree(t)
	sRoot, sArch, sLatest, sCounter, sLog := projectRoot, handoffArchiveDir, latestHandoffPath, updateCounterPath, logger
	t.Cleanup(func() {
		projectRoot, handoffArchiveDir, latestHandoffPath, updateCounterPath, logger = sRoot, sArch, sLatest, sCounter, sLog
	})
	projectRoot = r
	handoffArchiveDir = filepath.Join(r, "docs", "handoff_archive")
	latestHandoffPath = ""
	logger = pipelinelog.New(r, "boot_test")

	regenerateHandoff()

	boot, err := os.ReadFile(filepath.Join(r, "BOOT.md"))
	if err != nil {
		t.Fatalf("regenerateHandoff did not write BOOT.md: %v", err)
	}
	if !strings.HasPrefix(string(boot), "# BOOT.md - read this first") {
		t.Fatal("BOOT.md is not the canonical page")
	}
	h, err := os.ReadFile(filepath.Join(r, "LATEST_HANDOFF.md"))
	if err != nil {
		t.Fatalf("LATEST_HANDOFF.md not written: %v", err)
	}
	hs := string(h)
	if strings.Contains(hs, "CURRENT STATE (auto)") || strings.Contains(hs, "Project health score") {
		t.Fatal("the wrong auto section is still in the handoff")
	}
	if !strings.Contains(hs, "## CURRENT STATE\n\n**The current state is [`BOOT.md`](BOOT.md)") {
		t.Fatal("the handoff does not point at BOOT.md")
	}
}

var bootNow = time.Date(2026, 9, 12, 23, 0, 0, 0, time.Local)

func bootPut(t *testing.T, root, rel, body string) {
	t.Helper()
	p := filepath.Join(root, filepath.FromSlash(rel))
	if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func bootEdit(t *testing.T, root, rel, old, repl string) {
	t.Helper()
	p := filepath.Join(root, filepath.FromSlash(rel))
	raw, err := os.ReadFile(p)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(raw), old) {
		t.Fatalf("fixture %s does not contain %q", rel, old)
	}
	if err := os.WriteFile(p, []byte(strings.Replace(string(raw), old, repl, 1)), 0o644); err != nil {
		t.Fatal(err)
	}
}

// bootTree is a small, complete project: one of every source the page reads.
// LIVE.md carries the prose trap - "verified" in a sentence ABOVE the facts.
func bootTree(t *testing.T) string {
	t.Helper()
	r := t.TempDir()
	bootPut(t, r, "CLAUDE.md", "# rules\n")
	bootPut(t, r, "LIVE.md", "# LIVE\n\nNothing enters this file unless it was verified by loading it.**\n\n"+
		"    version          v0.3.9\n    ships            254\n    verified         2026-08-27 13:10 local, by fetching the page\n")
	bootPut(t, r, "checks/.last_sweep.json", `{"at":"2026-09-12T04:18:58","passed":130,"failed":[],"not_run":[],"fingerprint":"aaaa1111bbbb2222cccc3333"}`)
	bootPut(t, r, "testing/_src/.last_build.json", `{"status":"ok","at":"2026-09-12T04:18:56"}`)
	bootPut(t, r, "testing/_src/.last_deploy.json", `{"at":"2026-09-12T04:21:00","version_id":"cfd9544c-3b90-42d2-8689-f156f49a9a4f","sweep_fingerprint":"aaaa1111bbbb2222cccc3333"}`)
	bootPut(t, r, "correspondence/open/build/2026-09-12_memo_build_one.md", "# Memo\n\nTo: Build\nFrom: Architecture\nSubject: one\nStatus: Open\n\nbody\n")
	bootPut(t, r, "correspondence/open/owner/2026-09-12_memo_owner_two.md", "# Memo\n\nTo: Owner\nFrom: Build\nSubject: two\nStatus: Answered\n\nbody\n")
	bootPut(t, r, "NEXT.md", "# NEXT\n\n### Q1 - the first item\n\n### Q2 - the second item\n")
	bootPut(t, r, "claude/RULING_alpha-2026-09-12.md", "# ruling\n")
	bootPut(t, r, "docs/DECISION_beta-2026-09-08.md", "# decision\n")
	bootPut(t, r, "claude/FINDING_gamma-2026-09-12.md", "# finding\n")
	bootPut(t, r, "OWNERS.md", "# OWNERS\n\n## C1 - Cowork.\n\n## CODE - Claude Code.\n\n## SLEVEN - his alone.\n")
	bootPut(t, r, "testing/_src/next.src.html", `<html><script>const DATA={"ships":[{"n":"a"},{"n":"b"},{"n":"c"}]};</script></html>`)
	bootPut(t, r, "logs/uncommitted.json", `{"at":"2026-09-12T22:55:00","state":"ok","outside_doc_set":7,"outside_oldest":"2026-09-01T10:00:00","doc_set":3,"doc_set_oldest":"2026-09-02T10:00:00"}`)
	return r
}

// CONDITION 1 - every source, not a sample.
func TestBootEverySourceMovesThePage(t *testing.T) {
	cases := []struct {
		name  string
		plant func(t *testing.T, r string)
		want  string
	}{
		{"LIVE.md version", func(t *testing.T, r string) { bootEdit(t, r, "LIVE.md", "v0.3.9", "v9.9.9") }, "version v9.9.9"},
		{"LIVE.md verified", func(t *testing.T, r string) { bootEdit(t, r, "LIVE.md", "2026-08-27 13:10", "2031-01-01 00:00") }, "verified 2031-01-01 00:00"},
		{"sweep receipt", func(t *testing.T, r string) { bootEdit(t, r, "checks/.last_sweep.json", `"passed":130`, `"passed":131`) }, "131 passed"},
		{"build receipt", func(t *testing.T, r string) { bootEdit(t, r, "testing/_src/.last_build.json", `"status":"ok"`, `"status":"broken"`) }, "status broken"},
		{"deploy receipt", func(t *testing.T, r string) {
			bootEdit(t, r, "testing/_src/.last_deploy.json", "cfd9544c-3b90-42d2-8689-f156f49a9a4f", "11111111-2222-3333-4444-555555555555")
		}, "version 11111111-2222-3333-4444-555555555555"},
		{"a tray letter", func(t *testing.T, r string) {
			bootPut(t, r, "correspondence/open/design/2026-09-12_memo_design_planted.md", "# Memo\n\nTo: Design\nFrom: Build\nSubject: p\nStatus: Open\n\nb\n")
		}, "memo_design_planted"},
		{"NEXT.md", func(t *testing.T, r string) { bootEdit(t, r, "NEXT.md", "### Q2 - the second item\n", "### Q2 - the second item\n\n### Q3 - a planted item\n") }, "Q3 - a planted item"},
		{"a ruling", func(t *testing.T, r string) { bootPut(t, r, "claude/RULING_planted-2026-09-12.md", "x") }, "RULING_planted"},
		{"a decision", func(t *testing.T, r string) { bootPut(t, r, "docs/DECISION_planted-2026-09-12.md", "x") }, "DECISION_planted"},
		{"a finding", func(t *testing.T, r string) { bootPut(t, r, "claude/FINDING_planted-2026-09-12.md", "x") }, "FINDING_planted"},
		{"OWNERS.md", func(t *testing.T, r string) { bootEdit(t, r, "OWNERS.md", "## CODE - Claude Code.", "## CODE - Claude Code, PLANTED.") }, "PLANTED"},
		{"the front page", func(t *testing.T, r string) { bootEdit(t, r, "testing/_src/next.src.html", `{"n":"c"}`, `{"n":"c"},{"n":"d"}`) }, "4 cards"},
		{"uncommitted receipt", func(t *testing.T, r string) {
			bootEdit(t, r, "logs/uncommitted.json", `"outside_doc_set":7`, `"outside_doc_set":8`)
		}, "8 files outside the documentation set"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			r := bootTree(t)
			before := buildBoot(r, bootNow, true)
			if strings.Contains(before, c.want) {
				t.Fatalf("the unplanted page already says %q - the case proves nothing", c.want)
			}
			c.plant(t, r)
			after := buildBoot(r, bootNow, true)
			if after == before {
				t.Fatalf("planting a change in %s did not move the page", c.name)
			}
			if !strings.Contains(after, c.want) {
				t.Fatalf("the page moved but does not say %q", c.want)
			}
		})
	}
}

// CONDITION 2 - missing means MISSING, and the old value is gone.
func TestBootMissingSourceShowsMissing(t *testing.T) {
	cases := []struct {
		rel, want, gone string
	}{
		{"LIVE.md", "public site    MISSING", "v0.3.9"},
		{"logs/uncommitted.json", "uncommitted    NOT READ - MISSING", "7 files outside"},
		{"checks/.last_sweep.json", "last sweep     MISSING", "130 passed"},
		{"testing/_src/.last_build.json", "last build     MISSING", "status ok"},
		{"testing/_src/.last_deploy.json", "NOT RECORDED ON DISK", "cfd9544c"},
		{"testing/_src/next.src.html", "front page     MISSING", "3 cards"},
		{"NEXT.md", "MISSING - NEXT.md not found", "Q1 - the first item"},
		{"OWNERS.md", "MISSING - OWNERS.md not found", "C1 - Cowork"},
		{"CLAUDE.md", "CLAUDE.md - MISSING", ""},
		{"claude/RULING_alpha-2026-09-12.md", "none found for claude/RULING_*.md", "RULING_alpha"},
		{"correspondence/open", "correspondence/open/ - MISSING", "memo_build_one"},
	}
	for _, c := range cases {
		t.Run(c.rel, func(t *testing.T) {
			r := bootTree(t)
			if err := os.RemoveAll(filepath.Join(r, filepath.FromSlash(c.rel))); err != nil {
				t.Fatal(err)
			}
			page := buildBoot(r, bootNow, true)
			if !strings.Contains(page, c.want) {
				t.Fatalf("with %s gone the page does not say %q", c.rel, c.want)
			}
			if c.gone != "" && strings.Contains(page, c.gone) {
				t.Fatalf("with %s gone the page still shows its old value %q", c.rel, c.gone)
			}
		})
	}
}

// CONDITION 3 - both sources named, nothing merged.
func TestBootDisagreementNamesBothSources(t *testing.T) {
	r := bootTree(t)
	page := buildBoot(r, bootNow, true)
	if !strings.Contains(page, "none detected by the two checks") {
		t.Fatal("a consistent tree reported a disagreement")
	}

	bootEdit(t, r, "testing/_src/.last_build.json", `"at":"2026-09-12T04:18:56"`, `"at":"2026-09-12T05:00:00"`)
	page = buildBoot(r, bootNow, true)
	for _, want := range []string{"BUILT at 2026-09-12T05:00:00", "testing/_src/.last_build.json", "sweep at 2026-09-12T04:18:58", "checks/.last_sweep.json"} {
		if !strings.Contains(page, want) {
			t.Fatalf("a build newer than the sweep is not reported with both sources: missing %q", want)
		}
	}

	r = bootTree(t)
	bootEdit(t, r, "testing/_src/.last_deploy.json", `"sweep_fingerprint":"aaaa1111bbbb2222cccc3333"`, `"sweep_fingerprint":"zzzz9999yyyy8888"`)
	page = buildBoot(r, bootNow, true)
	// The page clips a long fingerprint to 16 characters plus "..." - it shows
	// that it clipped, rather than printing a prefix as if it were the whole.
	for _, want := range []string{"deployed against sweep zzzz9999yyyy8888", "latest sweep is aaaa1111bbbb2222...", "testing/_src/.last_deploy.json", "checks/.last_sweep.json"} {
		if !strings.Contains(page, want) {
			t.Fatalf("a deploy against another sweep is not reported with both sources: missing %q", want)
		}
	}
}

// CONDITION 4 - provenance per section.
func TestBootEverySectionNamesItsSource(t *testing.T) {
	page := buildBoot(bootTree(t), bootNow, true)
	secs := strings.Split(page, "\n## ")
	if len(secs) < 9 {
		t.Fatalf("expected at least 9 sections, found %d", len(secs)-1)
	}
	for _, s := range secs[1:] {
		lines := strings.SplitN(s, "\n", 3)
		if len(lines) < 2 || !strings.HasPrefix(lines[1], "source:") {
			t.Errorf("section %q has no source line directly under its heading", lines[0])
		}
	}
}

// THE TRAP THAT CAUGHT THE PROTOTYPE - prose "verified" above the fact lines.
func TestBootLiveParserTakesTheFactLineNotTheProse(t *testing.T) {
	page := buildBoot(bootTree(t), bootNow, true)
	if !strings.Contains(page, "verified 2026-08-27 13:10 local, by fetching the page") {
		t.Fatal("the LIVE.md fact line is not on the page")
	}
	if strings.Contains(page, "verified by loading it") {
		t.Fatal("the LIVE.md parser took the prose line as the verification date")
	}
}

func TestBootStatesWhatItCannotKnow(t *testing.T) {
	page := buildBoot(bootTree(t), bootNow, true)
	for _, want := range []string{"## WHAT THIS PAGE CANNOT KNOW", "whether a queue item is done", "claude.ai project store"} {
		if !strings.Contains(page, want) {
			t.Fatalf("the page does not state its limits: missing %q", want)
		}
	}
}

func TestBootWritesThroughATempFile(t *testing.T) {
	r := bootTree(t)
	out := filepath.Join(r, "BOOT.md")
	if err := writeBoot(r, out, bootNow, false); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(out)
	if err != nil || !strings.HasPrefix(string(raw), "# BOOT.md - read this first") {
		t.Fatalf("BOOT.md not written as the canonical page: %v", err)
	}
	if _, err := os.Stat(out + ".tmp"); err == nil {
		t.Fatal("the temporary file was left behind")
	}
}
