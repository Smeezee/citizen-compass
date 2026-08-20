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

// pollDriver runs the auto loop one COMPLETE poll at a time.
//
// S1 of docs/ORDER_collector-staleness-selftest-flake-2026-08-20.md. The old
// fixture advanced a fake clock - which sets a variable and wakes nothing -
// and then waited four real seconds for the loop's REAL one-second ticker to
// happen to notice. That is a race, and measured before the fix it lost that
// race 12.5% of the time on an idle machine and far more often under load.
//
// Now the fixture owns the schedule. cfg.PollSeconds is set so high the real
// ticker never fires during a run, every poll is requested through
// deps.pollNow, and the loop closes the acknowledgement channel once that
// poll's body has finished. So "the clock advanced AND the loop has seen it"
// is something the fixture is told, not something it hopes for.
//
// NO ASSERTION BELOW DEPENDS ON HOW MANY REAL SECONDS ELAPSE. The only
// timeouts left are watchdogs on the loop being alive at all, and hitting one
// is reported as NOT PERFORMED with the reason - never as a pass (S3).
type pollDriver struct {
	ch      chan chan struct{}
	timeout time.Duration
	failed  string // non-empty once the loop stopped answering
}

// poll runs exactly one complete poll and returns when its body has finished.
// false means the loop stopped answering, which is a fact about the loop and
// not a reason to assert anything.
func (p *pollDriver) poll() bool {
	if p.failed != "" {
		return false
	}
	ack := make(chan struct{})
	select {
	case p.ch <- ack:
	case <-time.After(p.timeout):
		p.failed = "the loop did not accept a poll request within " + p.timeout.String()
		return false
	}
	select {
	case <-ack:
		return true
	case <-time.After(p.timeout):
		p.failed = "a poll was accepted but never completed within " + p.timeout.String()
		return false
	}
}

// polls runs n complete polls.
func (p *pollDriver) polls(n int) bool {
	for i := 0; i < n; i++ {
		if !p.poll() {
			return false
		}
	}
	return true
}

// stalenessRun is one execution of the heartbeat and staleness fixture against
// a loop configured by the caller - normally, or deliberately broken.
//
// It returns the result of every named check rather than reporting them, so a
// control can require them to be FALSE. A check that has never been observed
// failing is not known to work (hard rule 12), and before this rewrite not one
// of these four had been.
type stalenessRun struct {
	results map[string]bool
	details map[string]string
	order   []string
}

func (r *stalenessRun) record(name string, ok bool, detail string) {
	if r.results == nil {
		r.results = map[string]bool{}
		r.details = map[string]string{}
	}
	if _, seen := r.results[name]; !seen {
		r.order = append(r.order, name)
	}
	r.results[name] = ok
	r.details[name] = detail
}

// The four checks this order is about, named once so the controls and the
// reporting cannot drift apart from the fixture.
const (
	ckStaleFires    = "staleness warning fires on a dead log"
	ckStaleNamesFix = "staleness warning names the fix"
	ckStaleOnce     = "staleness warns once per stall, not every poll"
	ckStaleClears   = "a log that starts growing again is NOT reported stale"
)

var stalenessCheckNames = []string{
	ckStaleFires, ckStaleNamesFix, ckStaleOnce, ckStaleClears,
}

// runHeartbeatFixture drives the real loop and records every result.
//
// sabotage and staleWindow are what a control varies. With sabotageNone and a
// zero window this is the ordinary fixture.
func runHeartbeatFixture(sabotage stalenessSabotage, staleWindow time.Duration) *stalenessRun {
	run := &stalenessRun{}

	dir, err := os.MkdirTemp("", "cc-heartbeat-")
	if err != nil {
		run.record("heartbeat testable", false, fmt.Sprintf("no temp dir: %v", err))
		return run
	}
	defer os.RemoveAll(dir)

	logPath := filepath.Join(dir, "Game.log")
	if err := os.WriteFile(logPath, []byte("start\n"), 0o644); err != nil {
		run.record("heartbeat testable", false, fmt.Sprintf("could not write fixture: %v", err))
		return run
	}

	clock := newFakeClock()
	sink := &logSink{}
	stop := make(chan struct{})
	pollNow := make(chan chan struct{})

	deps := autoDeps{
		logf:      sink.logf,
		gameAlive: func() error { return nil }, // a window is always present
		findLog:   func() (string, string) { return logPath, "forced by --gamelog" },
		now:       clock.Now,
		capture:   func(t Trigger) (string, error) { return filepath.Join(dir, "shot.png"), nil },

		pollNow:        pollNow,
		sabotage:       sabotage,
		stalenessAfter: staleWindow,
	}

	// THE REAL TICKER IS PUT OUT OF REACH. Every poll in this fixture is
	// requested, so nothing happens because a wall clock happened to tick.
	// PollSeconds used to be 1 here, and that ticker was the other half of the
	// race this rewrite removes.
	cfg := autoConfig{PollSeconds: 3600, DebounceSeconds: 0}

	done := make(chan struct{})
	go func() { _ = runAuto(cfg, logPath, deps, stop); close(done) }()
	defer func() {
		close(stop)
		select {
		case <-done:
		case <-time.After(10 * time.Second):
			// Recorded rather than waited on. A loop that will not shut down is
			// a candidate for the ten-minute hang in section 5 of the order,
			// and enduring it here would just reproduce that hang.
			run.record("the auto loop shuts down when told to", false,
				"NOT PERFORMED - the loop did not return within 10s of stop")
		}
	}()

	driver := &pollDriver{ch: pollNow, timeout: 20 * time.Second}

	// The startup lines are written BEFORE the loop reaches its select, so a
	// poll that is accepted at all proves they have been written. No wait.
	if !driver.poll() {
		run.record("loop established a tailer", false,
			"NOT PERFORMED - "+driver.failed)
		return run
	}

	run.record("startup states the watched path",
		sink.has("startup: watching "+logPath),
		"auto log names the resolved path at start")
	run.record("startup states HOW it was chosen", sink.has("forced by --gamelog"),
		"the startup line carries the reason, not just the path")

	established := sink.has("watching " + logPath + " (forced by --gamelog)")
	run.record("loop established a tailer", established,
		"first poll resolved the log and started tailing it")
	if !established {
		return run
	}

	// NEGATIVE CONTROL: before the clock moves, there must be NO heartbeat.
	// Without this, a heartbeat printed unconditionally on every poll would
	// pass the positive check below while measuring nothing.
	//
	// This one is now worth something it was not before: several polls have
	// definitely run, so "no heartbeat yet" means the loop declined to print
	// one rather than that it has not got round to polling.
	if !driver.polls(3) {
		run.record("no heartbeat before its interval elapses", false,
			"NOT PERFORMED - "+driver.failed)
		return run
	}
	beatsBefore := sink.count("alive:")
	run.record("no heartbeat before its interval elapses", beatsBefore == 0,
		fmt.Sprintf("%d heartbeat lines after 4 polls with the clock held still", beatsBefore))

	clock.Advance(heartbeatEvery + time.Second)
	if !driver.poll() {
		run.record("heartbeat appears once the interval passes", false,
			"NOT PERFORMED - "+driver.failed)
		return run
	}
	run.record("heartbeat appears once the interval passes", sink.count("alive:") >= 1,
		fmt.Sprintf("%d heartbeat line(s) after advancing %s and running one poll",
			sink.count("alive:"), heartbeatEvery))
	run.record("heartbeat names the file and the counters",
		sink.hasLineWithBoth("alive:", logPath) &&
			sink.has("bytes read since last line") && sink.has("captures total"),
		"the line carries path, bytes read and capture count - checkable, not decorative")

	// STALENESS. The file has not grown and a window is present, so once the
	// staleness interval has passed the loop must say so.
	staleBefore := sink.count("has not grown in")
	run.record("no staleness warning before its interval", staleBefore == 0,
		fmt.Sprintf("%d staleness lines so far", staleBefore))

	clock.Advance(stalenessAfter + time.Second)
	if !driver.poll() {
		run.record(ckStaleFires, false, "NOT PERFORMED - "+driver.failed)
		return run
	}
	fired := sink.count("has not grown in") >= 1
	run.record(ckStaleFires, fired,
		"a game window with a log that never grows is reported, not treated as a quiet game")
	// Look for the fix INSIDE the warning line, not anywhere in the log. The
	// startup line also contains "--gamelog", so a bare sink.has() would pass
	// on the startup line while the warning said nothing useful.
	run.record(ckStaleNamesFix,
		sink.has("has not grown in") && sink.hasLineWithBoth("has not grown in", "--gamelog"),
		"the warning itself tells the operator what to do about it")

	// WARNED ONCE, not every poll. A line every second would bury the log it is
	// meant to make readable.
	//
	// THE GATE STAYS. Both remaining checks compare a count against firstCount,
	// so if the warning above never fired, firstCount is 0 and "the count did
	// not go up" is trivially true - they would report a pass having measured
	// nothing. That is the SILENT SUCCESS pattern and it was observed for real.
	// The race underneath it is gone; the gate is not, because the gate is what
	// makes a genuinely broken warning report honestly instead of green.
	firstCount := sink.count("has not grown in")
	if firstCount == 0 {
		run.record(ckStaleOnce, false,
			"NOT PERFORMED - no warning ever fired, so there is no count to hold steady")
		run.record(ckStaleClears, false,
			"NOT PERFORMED - no warning ever fired, so a cleared warning cannot be observed")
		return run
	}

	// Five polls with the clock past the threshold. The old version slept
	// 1500ms and compared a count, which on a loaded machine passed BECAUSE
	// NOTHING HAD RUN - a check too slow to observe the defect it exists to
	// catch. These five polls definitely ran.
	clock.Advance(30 * time.Second)
	if !driver.polls(5) {
		run.record(ckStaleOnce, false, "NOT PERFORMED - "+driver.failed)
		return run
	}
	run.record(ckStaleOnce, sink.count("has not grown in") == firstCount,
		fmt.Sprintf("still %d warning(s) after 5 further polls past the threshold", firstCount))

	// AND IT CLEARS. Growth must reset the staleness clock, otherwise the
	// collector would keep complaining about a file that started working again.
	//
	// The clock is advanced by LESS than stalenessAfter here on purpose. Moving
	// it past the threshold again would legitimately re-warn - the file would
	// genuinely have been still for another five minutes - and the test would
	// be asserting that a correct warning is a bug.
	f, err := os.OpenFile(logPath, os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		run.record(ckStaleClears, false,
			fmt.Sprintf("NOT PERFORMED - could not append to the fixture: %v", err))
		return run
	}
	_, _ = f.WriteString("<2026-08-06T12:00:00Z> the log is moving again\n")
	f.Close()

	// One poll to observe the growth - the write completed before this poll
	// started, so it cannot be missed - then step forward well short of another
	// full stall and run several more.
	if !driver.poll() {
		run.record(ckStaleClears, false, "NOT PERFORMED - "+driver.failed)
		return run
	}
	clock.Advance(stalenessAfter - time.Minute)
	if !driver.polls(5) {
		run.record(ckStaleClears, false, "NOT PERFORMED - "+driver.failed)
		return run
	}
	run.record(ckStaleClears, sink.count("has not grown in") == firstCount,
		fmt.Sprintf("still %d warning(s) after the file resumed growing and 6 more polls - "+
			"the clock reset rather than latching", firstCount))

	if os.Getenv("CC_SELFTEST_DUMP") != "" {
		fmt.Println("  --- auto log as collected ---")
		for _, l := range sink.dump() {
			fmt.Println("      " + l)
		}
	}
	return run
}

// runAutoHeartbeatSelftest covers the heartbeat and the staleness warning, and
// then proves each staleness check can FAIL by breaking the loop on purpose.
func runAutoHeartbeatSelftest(check func(name string, ok bool, detail string)) {
	run := runHeartbeatFixture(sabotageNone, 0)
	for _, name := range run.order {
		check(name, run.results[name], run.details[name])
	}

	// ---------------------------------------------------------------------
	// THE CONTROLS. Each one breaks the loop in the specific way the check it
	// is aimed at exists to catch, and requires that check to FAIL.
	//
	// Without these, "the four staleness checks pass" means only that they ran.
	// The fix for the flake was to stop the fixture depending on wall-clock
	// timing - and the obvious wrong way to achieve that is to widen a timeout
	// until nothing ever fails, which would satisfy every other line of this
	// fixture. These are what that cannot survive.
	// ---------------------------------------------------------------------

	// S1's control: break the warning itself. A staleness window of 1000 hours
	// means the loop never warns, so all four must fail.
	broken := runHeartbeatFixture(sabotageNone, 1000*time.Hour)
	allFailed := true
	var stillPassing []string
	for _, name := range stalenessCheckNames {
		if broken.results[name] {
			allFailed = false
			stillPassing = append(stillPassing, name)
		}
	}
	check("CONTROL: with the staleness warning disabled, all four checks fail",
		allFailed,
		fmt.Sprintf("staleness window set to 1000h; still passing: %v", stillPassing))
	check("CONTROL: and the two dependants report NOT PERFORMED, not a pass",
		strings.Contains(broken.details[ckStaleOnce], "NOT PERFORMED") &&
			strings.Contains(broken.details[ckStaleClears], "NOT PERFORMED"),
		"a warning that never fired leaves nothing to count, and the fixture says so")

	// S2's first control: make the loop warn on EVERY poll. "warns once per
	// stall" must fail. This had never been observed failing.
	noisy := runHeartbeatFixture(sabotageWarnEveryPoll, 0)
	check("CONTROL: a loop that warns every poll fails 'warns once per stall'",
		!noisy.results[ckStaleOnce],
		fmt.Sprintf("detail was %q", noisy.details[ckStaleOnce]))
	check("CONTROL: and the warning still fires, so the failure is about "+
		"repetition and not about silence",
		noisy.results[ckStaleFires],
		"the positive check must still pass, or the control proves the wrong thing")

	// S2's second control: growth does not reset the staleness clock. "a log
	// that starts growing again is NOT reported stale" must fail. This had
	// never been observed failing either.
	latched := runHeartbeatFixture(sabotageNeverReset, 0)
	check("CONTROL: a loop whose clock never resets fails 'starts growing again'",
		!latched.results[ckStaleClears],
		fmt.Sprintf("detail was %q", latched.details[ckStaleClears]))

	// And the sabotage is off by default, which is the whole basis for it
	// living in production code at all.
	check("the sabotage switch is off unless a control sets it",
		autoDeps{}.sabotage == sabotageNone,
		"the zero value of autoDeps carries no sabotage, so production has none")
}
