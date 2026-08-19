package main

// activity_selftest.go - prove the person is told, and told WHICH KEYS.
//
// The order's own words:
//
//	"An Alt+F3 press appears in it and NAMES THE KEYS - so somebody who hits it
//	 by accident understands what they did rather than finding a mystery picture
//	 later."
//
// So the checks below are not "does a list exist". They drive the REAL capture
// loop with a real key press and read what the person would see. A list that
// fills with "picture taken" would pass a weaker test and leave the accidental
// presser exactly where they started.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

func runActivitySelftest(check func(name string, ok bool, detail string)) {
	// ---- the feed itself, before anything harder -----------------------
	f := &activityFeed{}
	f.add("first")
	f.add("second")
	rows, ver := f.Snapshot()
	check("activity: entries arrive in order, oldest first",
		len(rows) == 2 && rows[0].Text == "first" && rows[1].Text == "second",
		fmt.Sprintf("got %v", rows))
	check("activity: the version moves when something happens",
		ver == 2, fmt.Sprintf("version=%d", ver))

	before := f.Version()
	f.add("   ")
	check("activity: NEGATIVE CONTROL - a blank line is not an event",
		f.Version() == before,
		"an empty string became a line in somebody's activity list")

	// THE LIST SCROLLS BACK OVER THE SESSION, AND DROPS THE OLDEST.
	//
	// Dropping the NEWEST would leave the window frozen on the start of the
	// session, which reads exactly like a program that has stopped working - so
	// this checks which end goes.
	g := &activityFeed{}
	for i := 0; i < activityMax+50; i++ {
		g.add(fmt.Sprintf("line %d", i))
	}
	rows, _ = g.Snapshot()
	check("activity: the list is capped at "+itoaSmall(activityMax),
		len(rows) == activityMax, fmt.Sprintf("%d rows", len(rows)))
	check("activity: and it keeps the NEWEST lines, not the first thousand",
		len(rows) > 0 && rows[len(rows)-1].Text == fmt.Sprintf("line %d", activityMax+49),
		fmt.Sprintf("last line is %q", rows[len(rows)-1].Text))

	// ---- THE ONE THE ORDER NAMES --------------------------------------
	//
	// A real press, through the real loop, with the real hotkey name.
	tmp, err := os.MkdirTemp("", "activity-")
	if err != nil {
		check("activity: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)
	logPath := filepath.Join(tmp, "Game.log")
	if err := os.WriteFile(logPath, []byte("<2026-08-18T09:00:00.000Z> priming\n"), 0o644); err != nil {
		check("activity: fixture log", false, err.Error())
		return
	}

	// The feed is process-wide, so this reads it from a known point rather than
	// assuming the checks above left it empty.
	startAt := len(func() []ActivityEntry { e, _ := theActivity.Snapshot(); return e }())

	var mu sync.Mutex
	hot := make(chan string, 1)
	stop := make(chan struct{})
	done := make(chan struct{})
	fakeNow := time.Date(2026, 8, 18, 9, 0, 0, 0, time.UTC)

	deps := autoDeps{
		now:        func() time.Time { fakeNow = fakeNow.Add(time.Second); return fakeNow },
		findLog:    func() (string, string) { return logPath, "fixture" },
		gameAlive:  func() error { return nil },
		hotkeys:    hot,
		hotkeyName: "Alt+F3",
		logf:       func(string, ...interface{}) {},
		capture: func(t Trigger) (string, error) {
			mu.Lock()
			defer mu.Unlock()
			return filepath.Join(tmp, "shot_0001.png"), nil
		},
	}
	go func() {
		_ = runAuto(autoConfig{PollSeconds: 1, DebounceSeconds: 0,
			HotkeyBurst: burstConfig{FrameSeconds: 0}}, logPath, deps, stop)
		close(done)
	}()
	time.Sleep(120 * time.Millisecond)
	hot <- "test"
	time.Sleep(400 * time.Millisecond)
	close(stop)
	select {
	case <-done:
	case <-time.After(3 * time.Second):
	}

	all, _ := theActivity.Snapshot()
	var fresh []string
	for _, e := range all[min(startAt, len(all)):] {
		fresh = append(fresh, e.Line())
	}
	joined := strings.Join(fresh, " | ")

	check("activity: a real key press appears in the list",
		len(fresh) > 0, "the press produced no line at all: "+joined)
	check("activity: and the line NAMES THE KEYS",
		strings.Contains(joined, "Alt+F3"),
		"got %q - somebody who pressed it by accident still cannot tell what "+
			"they did"+joined)
	check("activity: it says a picture was taken, in plain words",
		strings.Contains(strings.ToLower(joined), "picture taken"),
		"got "+joined)
	check("activity: and it names the file, so the picture can be found",
		strings.Contains(joined, "shot_0001.png"),
		"got "+joined)

	// NEGATIVE CONTROL: the wording is not hard-coded somewhere that would say
	// "Alt+F3" whatever key was actually registered.
	theActivity.add("---- control ----")
	ActivityCapture("Ctrl+Shift+P", "shot_0002.png", "")
	all, _ = theActivity.Snapshot()
	last := all[len(all)-1].Line()
	check("activity: NEGATIVE CONTROL - a different key is named as itself",
		strings.Contains(last, "Ctrl+Shift+P") && !strings.Contains(last, "Alt+F3"),
		"got "+last+" - the key name is decoration rather than the real one")

	// AND A CAPTURE WITH NO KEY NAMED SAYS SO rather than printing a blank
	// where the answer goes.
	ActivityCapture("", "shot_0003.png", "")
	all, _ = theActivity.Snapshot()
	last = all[len(all)-1].Line()
	check("activity: a capture with no key recorded says so out loud",
		strings.Contains(last, "unknown key"),
		"got "+last)

	// Held keys are RECORDED here, not photographed - §6 took the pictures
	// away and §7 keeps the fact.
	ActivityHeldKeyEnd("recording mining laser", 12)
	all, _ = theActivity.Snapshot()
	last = all[len(all)-1].Line()
	check("activity: a held key is reported as recorded, not photographed",
		strings.Contains(last, "diary") && !strings.Contains(strings.ToLower(last), "picture"),
		"got "+last)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
