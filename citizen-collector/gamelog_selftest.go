package main

// gamelog_selftest.go - the --gamelog override, the heartbeat, and the
// staleness warning.
//
// All three exist to stop the collector looking healthy while doing nothing
// useful, so all three are tested by making them FAIL first.
//
// The clock is injected rather than waited on. Testing a three-minute heartbeat
// by sleeping three minutes would make the selftest unrunnable, and a test
// nobody runs is worth as much as a check that cannot fail.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// fakeClock is a hand-advanced clock, safe to move from the test goroutine
// while runAuto reads it from its own.
type fakeClock struct {
	mu sync.Mutex
	t  time.Time
}

func newFakeClock() *fakeClock { return &fakeClock{t: time.Date(2026, 8, 6, 12, 0, 0, 0, time.UTC)} }

func (c *fakeClock) Now() time.Time {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.t
}

func (c *fakeClock) Advance(d time.Duration) {
	c.mu.Lock()
	c.t = c.t.Add(d)
	c.mu.Unlock()
}

// logSink collects log lines for assertions.
type logSink struct {
	mu    sync.Mutex
	lines []string
}

func (s *logSink) logf(format string, args ...interface{}) {
	s.mu.Lock()
	s.lines = append(s.lines, fmt.Sprintf(format, args...))
	s.mu.Unlock()
}

func (s *logSink) has(sub string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, l := range s.lines {
		if strings.Contains(l, sub) {
			return true
		}
	}
	return false
}

// hasLineWithBoth requires ONE line to contain both substrings, so a check
// cannot be satisfied by two unrelated lines each carrying half of it.
func (s *logSink) hasLineWithBoth(a, b string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, l := range s.lines {
		if strings.Contains(l, a) && strings.Contains(l, b) {
			return true
		}
	}
	return false
}

// dump returns the collected lines, for diagnosing a failed assertion.
func (s *logSink) dump() []string {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]string, len(s.lines))
	copy(out, s.lines)
	return out
}

func (s *logSink) count(sub string) int {
	s.mu.Lock()
	defer s.mu.Unlock()
	n := 0
	for _, l := range s.lines {
		if strings.Contains(l, sub) {
			n++
		}
	}
	return n
}

// waitFor polls cond until it holds or the deadline passes. Returns whether it
// held. Used instead of a fixed sleep so a slow machine does not produce a
// false failure and a fast one does not waste a second.
func waitFor(cond func() bool, timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	for {
		if cond() {
			return true
		}
		if time.Now().After(deadline) {
			return false
		}
		time.Sleep(10 * time.Millisecond)
	}
}

// runGameLogSelftest covers the --gamelog override in isolation.
func runGameLogSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-gamelog-")
	if err != nil {
		check("gamelog override testable", false, fmt.Sprintf("no temp dir: %v", err))
		return
	}
	defer os.RemoveAll(dir)

	fake := filepath.Join(dir, "Game.log")
	if err := os.WriteFile(fake, []byte("hello\n"), 0o644); err != nil {
		check("gamelog override testable", false, fmt.Sprintf("could not write fixture: %v", err))
		return
	}

	saved := gameLogOverride
	defer func() { gameLogOverride = saved }()

	// BASELINE: with no override, discovery does whatever it does on this
	// machine. Recorded, not asserted - the game may not be installed here.
	gameLogOverride = ""
	basePath, baseHow := FindGameLog(0)
	check("no override leaves discovery alone", true,
		fmt.Sprintf("scan reports %q (%s)", basePath, baseHow))

	// THE OVERRIDE IS HONOURED.
	gameLogOverride = fake
	gotPath, gotHow := FindGameLog(0)
	check("--gamelog forces the path", gotPath == fake,
		fmt.Sprintf("resolved %q", gotPath))
	check("--gamelog says HOW it was chosen", strings.Contains(gotHow, "--gamelog"),
		fmt.Sprintf("reason is %q", gotHow))

	// AND IT ACTUALLY CHANGED SOMETHING. If the machine's scan already returned
	// this path, the check above would pass while proving nothing.
	check("the override changes the answer", gotPath != basePath,
		fmt.Sprintf("scan said %q, override said %q", basePath, gotPath))

	// FAILS CLOSED. A bad path must NOT silently fall back to the scan, because
	// falling back means quietly watching LIVE again - the exact defect.
	gameLogOverride = filepath.Join(dir, "does-not-exist", "Game.log")
	badPath, badHow := FindGameLog(0)
	check("a bad --gamelog refuses, not falls back", badPath == "",
		fmt.Sprintf("resolved %q (empty means it refused)", badPath))
	check("the refusal explains itself", strings.Contains(badHow, "refusing to fall back"),
		fmt.Sprintf("reason is %q", badHow))
	check("a bad --gamelog does NOT return the scan result", badPath != basePath || basePath == "",
		"the failure path did not quietly resolve to whatever the scan would have found")
}

// runAutoHeartbeatSelftest covers the heartbeat and the staleness warning by
// driving runAuto with an injected clock and a log file under test control.
func runAutoHeartbeatSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-heartbeat-")
	if err != nil {
		check("heartbeat testable", false, fmt.Sprintf("no temp dir: %v", err))
		return
	}
	defer os.RemoveAll(dir)

	logPath := filepath.Join(dir, "Game.log")
	if err := os.WriteFile(logPath, []byte("start\n"), 0o644); err != nil {
		check("heartbeat testable", false, fmt.Sprintf("could not write fixture: %v", err))
		return
	}

	clock := newFakeClock()
	sink := &logSink{}
	stop := make(chan struct{})

	deps := autoDeps{
		logf:      sink.logf,
		gameAlive: func() error { return nil }, // a window is always present
		findLog:   func() (string, string) { return logPath, "forced by --gamelog" },
		now:       clock.Now,
		capture:   func(t Trigger) (string, error) { return filepath.Join(dir, "shot.png"), nil },
	}
	// Poll fast so the loop iterates often in real time; the CLOCK is what
	// advances, so heartbeat and staleness are driven deliberately, not by
	// waiting.
	cfg := autoConfig{PollSeconds: 1, DebounceSeconds: 0, IntervalMinutes: 0}

	done := make(chan struct{})
	go func() { _ = runAuto(cfg, logPath, deps, stop); close(done) }()
	defer func() { close(stop); <-done }()

	// The startup line names the path AND how it was chosen.
	ok := waitFor(func() bool { return sink.has("startup: watching " + logPath) }, 4*time.Second)
	check("startup states the watched path", ok, "auto log names the resolved path at start")
	check("startup states HOW it was chosen", sink.has("forced by --gamelog"),
		"the startup line carries the reason, not just the path")

	// SEQUENCING, not a sleep. Wait until the loop has actually resolved the
	// log and built a tailer before touching the clock.
	//
	// Without this the test races the loop: the fake clock can jump past the
	// heartbeat interval before the first poll runs, so the first heartbeat
	// legitimately reports "(no log resolved yet)" and the assertions below
	// measure the wrong line. That is a defect in the test, not in the loop -
	// and getting it wrong once already produced a red result on working code.
	ok = waitFor(func() bool { return sink.has("watching " + logPath + " (forced by --gamelog)") }, 5*time.Second)
	if !ok {
		check("loop established a tailer", false, "the poll loop never reported watching the fixture")
		return
	}
	check("loop established a tailer", true, "first poll resolved the log and started tailing it")

	// NEGATIVE CONTROL: before the clock moves, there must be NO heartbeat.
	// Without this, a heartbeat printed unconditionally on every poll would
	// pass the positive check below while measuring nothing.
	beatsBefore := sink.count("alive: watching")
	check("no heartbeat before its interval elapses", beatsBefore == 0,
		fmt.Sprintf("%d heartbeat lines after startup with the clock held still", beatsBefore))

	// Now let time pass.
	clock.Advance(heartbeatEvery + time.Second)
	ok = waitFor(func() bool { return sink.count("alive: watching") >= 1 }, 4*time.Second)
	check("heartbeat appears once the interval passes", ok,
		fmt.Sprintf("%d heartbeat line(s) after advancing %s", sink.count("alive: watching"), heartbeatEvery))
	check("heartbeat names the file and the counters",
		sink.has("alive: watching "+logPath) && sink.has("bytes read since last line") && sink.has("captures total"),
		"the line carries path, bytes read and capture count - checkable, not decorative")

	// STALENESS. The file has not grown and a window is present, so after
	// stalenessAfter the loop must say so.
	staleBefore := sink.count("has not grown in")
	check("no staleness warning before its interval", staleBefore == 0,
		fmt.Sprintf("%d staleness lines so far", staleBefore))

	clock.Advance(stalenessAfter + time.Second)
	ok = waitFor(func() bool { return sink.count("has not grown in") >= 1 }, 4*time.Second)
	check("staleness warning fires on a dead log", ok,
		"a game window with a log that never grows is reported, not treated as a quiet game")
	// Look for the fix INSIDE the warning line, not anywhere in the log. The
	// startup line also contains "--gamelog", so a bare sink.has() would pass
	// on the startup line while the warning said nothing useful.
	check("staleness warning names the fix", sink.has("has not grown in") &&
		sink.hasLineWithBoth("has not grown in", "--gamelog"),
		"the warning itself tells the operator what to do about it")

	// WARNED ONCE, not every poll. A line every second would bury the log it is
	// meant to make readable.
	firstCount := sink.count("has not grown in")
	clock.Advance(30 * time.Second)
	time.Sleep(1500 * time.Millisecond)
	check("staleness warns once per stall, not every poll",
		sink.count("has not grown in") == firstCount,
		fmt.Sprintf("still %d warning(s) after further polls", firstCount))

	// AND IT CLEARS. Growth must reset the staleness clock, otherwise the
	// collector would keep complaining about a file that started working again.
	//
	// The clock is advanced by LESS than stalenessAfter here on purpose. Moving
	// it past the threshold again would legitimately re-warn - the file would
	// genuinely have been still for another five minutes - and the test would
	// be asserting that a correct warning is a bug.
	f, err := os.OpenFile(logPath, os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		check("a log that starts growing again is NOT reported stale", false,
			fmt.Sprintf("could not append to the fixture: %v", err))
		return
	}
	_, _ = f.WriteString("<2026-08-06T12:00:00Z> the log is moving again\n")
	f.Close()

	// Let the loop observe the growth, then step forward well short of another
	// full stall.
	time.Sleep(1500 * time.Millisecond)
	clock.Advance(stalenessAfter - time.Minute)
	time.Sleep(1500 * time.Millisecond)
	check("a log that starts growing again is NOT reported stale",
		sink.count("has not grown in") == firstCount,
		fmt.Sprintf("still %d warning(s) after the file resumed growing - the clock reset rather than latching", firstCount))

	if os.Getenv("CC_SELFTEST_DUMP") != "" {
		fmt.Println("  --- auto log as collected ---")
		for _, l := range sink.dump() {
			fmt.Println("      " + l)
		}
	}
}
