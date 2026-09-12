package main

// boot_poller_test.go - the beat and the poller line (Architecture's ruling,
// 2026-09-12). The condition that decides it: "nothing to refuse" and "never
// ran" must never look alike, and a stopped beat must be visible on the page.

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"citizencompass/pkg/pipelinelog"
)

func runsJSON(at time.Time, outcome, reason string) string {
	return fmt.Sprintf(`{"last":{"attempted_at":%q,"outcome":%q,"reason":%q,"read":2,"filed":["7"],"refused":[]},"runs":[]}`,
		at.Format(time.RFC3339), outcome, reason)
}

// No run recorded is MISSING, and it is named in the section's source line.
func TestBootPollerMissingSaysMissing(t *testing.T) {
	page := buildBoot(bootTree(t), bootNow, true)
	for _, want := range []string{
		"echo poller    MISSING - logs/desk_fetch_runs.json (no fetch run is recorded)",
		"logs/desk_fetch_runs.json - MISSING",
	} {
		if !strings.Contains(page, want) {
			t.Fatalf("with no runs file the page does not say %q", want)
		}
	}
}

// A planted run moves the page, and a planted failure moves it again - with the
// reason on it, so "did not look" can never read as "nothing new".
func TestBootPollerLastRunMovesThePage(t *testing.T) {
	r := bootTree(t)
	empty := buildBoot(r, bootNow, true)

	okAt := bootNow.Add(-4 * time.Minute)
	bootPut(t, r, pollerRunsRel, runsJSON(okAt, "ok", ""))
	okPage := buildBoot(r, bootNow, true)
	if okPage == empty {
		t.Fatal("a recorded run did not move the page")
	}
	for _, want := range []string{
		"last run " + okAt.Format(time.RFC3339) + ", ok - read 2, filed 1, refused 0",
		"(4 min ago)",
		"logs/desk_fetch_runs.json (",
	} {
		if !strings.Contains(okPage, want) {
			t.Fatalf("the ok run is not on the page: missing %q", want)
		}
	}
	if strings.Contains(okPage, "STALE") {
		t.Fatal("a four-minute-old run was called STALE")
	}

	badAt := bootNow.Add(-2 * time.Minute)
	bootPut(t, r, pollerRunsRel, runsJSON(badAt, "did-not-look", "URLError: simulated outage"))
	badPage := buildBoot(r, bootNow, true)
	want := "last run " + badAt.Format(time.RFC3339) + ", did-not-look - URLError: simulated outage"
	if !strings.Contains(badPage, want) {
		t.Fatalf("a failed run is not on the page with its reason: missing %q", want)
	}
	if strings.Contains(badPage, "read 2, filed 1") {
		t.Fatal("a run that did not look still shows the counts of one that did")
	}
}

// Three missed ticks is a stopped beat, and the page says so.
func TestBootPollerStaleIsSaid(t *testing.T) {
	r := bootTree(t)
	bootPut(t, r, pollerRunsRel, runsJSON(bootNow.Add(-45*time.Minute), "ok", ""))
	page := buildBoot(r, bootNow, true)
	if !strings.Contains(page, "STALE - the beat runs every 10 min") {
		t.Fatal("a 45-minute-old run is not called STALE")
	}
}

func TestBootPollerUnreadableAndEmptySayWhy(t *testing.T) {
	r := bootTree(t)
	bootPut(t, r, pollerRunsRel, "{")
	if page := buildBoot(r, bootNow, true); !strings.Contains(page, "echo poller    UNREADABLE") {
		t.Fatal("an unreadable runs file is not called UNREADABLE")
	}
	bootPut(t, r, pollerRunsRel, `{"runs":[]}`)
	if page := buildBoot(r, bootNow, true); !strings.Contains(page, `echo poller    NOT FOUND - no "last" run`) {
		t.Fatal("a runs file with no last run is not called NOT FOUND")
	}
}

func beatLogger(t *testing.T, r string) {
	sLog := logger
	t.Cleanup(func() { logger = sLog })
	logger = pipelinelog.New(r, "beat_test")
}

// A failed fetch does not stop the page.
func TestBeatWritesBootEvenWhenTheFetchFails(t *testing.T) {
	r := bootTree(t)
	beatLogger(t, r)
	called := false
	err := tickOnce(r, bootNow, func(string) (string, error) {
		called = true
		return "DID NOT LOOK - simulated\n", errors.New("exit status 2")
	})
	if !called {
		t.Fatal("the beat did not run the fetch")
	}
	if err != nil {
		t.Fatalf("a failed fetch stopped the beat: %v", err)
	}
	raw, rerr := os.ReadFile(filepath.Join(r, "BOOT.md"))
	if rerr != nil || !strings.HasPrefix(string(raw), "# BOOT.md - read this first") {
		t.Fatalf("BOOT.md was not written after a failed fetch: %v", rerr)
	}
}

// The beat's page reflects what the fetch just recorded - fetch first, page second.
func TestBeatWritesThePageAfterTheFetch(t *testing.T) {
	r := bootTree(t)
	beatLogger(t, r)
	at := bootNow.Add(-30 * time.Second)
	if err := tickOnce(r, bootNow, func(root string) (string, error) {
		bootPut(t, root, pollerRunsRel, runsJSON(at, "ok", ""))
		return "desk fetch - ok\n", nil
	}); err != nil {
		t.Fatal(err)
	}
	raw, _ := os.ReadFile(filepath.Join(r, "BOOT.md"))
	if !strings.Contains(string(raw), "last run "+at.Format(time.RFC3339)+", ok") {
		t.Fatal("the page was written before the fetch recorded its run")
	}
}

// Two writers in one process - the mail path and the beat - never collide.
func TestBootWritersDoNotCollide(t *testing.T) {
	r := bootTree(t)
	out := filepath.Join(r, "BOOT.md")
	var wg sync.WaitGroup
	errs := make(chan error, 40)
	for i := 0; i < 40; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := writeBootLocked(r, out, bootNow); err != nil {
				errs <- err
			}
		}()
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		t.Fatalf("concurrent BOOT.md writes collided: %v", err)
	}
	if _, err := os.Stat(out + ".tmp"); err == nil {
		t.Fatal("a temporary file was left behind")
	}
}
