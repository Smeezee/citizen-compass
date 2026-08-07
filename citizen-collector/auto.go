package main

// auto.go - unattended capture driven by Game.log state changes.
//
// WHAT THIS ADDS
//   The collector could only be fired by hand, one shot per hotkey press. That
//   is fine for answering the legibility question but useless for building a
//   corpus: the interesting moments (leaving the menu, arriving in a system,
//   spawning) are exactly the ones a human is too busy playing to catch.
//
//   --auto watches the Game.log the tool already locates and captures when the
//   game's STATE changes, with an interval fallback so a long quiet stretch
//   still produces evidence.
//
// WHAT IT DELIBERATELY DOES NOT ADD
//   No OCR, no database routing, no ZIP packager. Same scope line as main.go.
//
// ---------------------------------------------------------------------------
// EVERY CAPTURE STATES ITS REASON
// ---------------------------------------------------------------------------
// The sidecar carries a "trigger" object naming exactly what fired the shot.
// This is not decoration. Once captures arrive on their own, a folder of images
// with no provenance is unreadable - nobody can tell a state change from a
// timer from a stray double-fire, and the corpus becomes evidence of nothing.
//
// A CAPTURE WITH NO STATED REASON IS A BUG. doCapture takes a Trigger, not a
// *Trigger, and the selftest asserts that every path which can produce a
// capture produces a non-empty Kind - including the manual ones, which now say
// "hotkey" or "once" rather than saying nothing.
//
// ---------------------------------------------------------------------------
// PRIMING - why the first poll never fires
// ---------------------------------------------------------------------------
// Game.log already holds a whole session's history when this starts. Feeding
// that backlog through the detector would fire a burst of captures describing
// state changes that happened before the tool was launched, timestamped now.
// So the first read establishes the baseline SILENTLY and only subsequent
// appended lines can trigger. This is proven by a selftest check, because a
// priming bug is invisible in normal use - it just looks like a busy start.

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"syscall"
	"time"
)

// --- the reason a capture happened ----------------------------------------

// Trigger is written into the sidecar as "trigger".
//
// Kind is one of:
//
//	state_change - a tracked field changed value (gamerules, map, zone, location)
//	event        - something happened that has no before/after (a loading
//	               screen, a client spawn)
//	interval     - nothing changed for long enough that the fallback fired
//	hotkey       - a human pressed the key
//	once         - a human ran --once
type Trigger struct {
	Kind    string `json:"kind"`
	Field   string `json:"field,omitempty"`
	From    string `json:"from,omitempty"`
	To      string `json:"to,omitempty"`
	Minutes int    `json:"minutes,omitempty"`
	Note    string `json:"note,omitempty"`
}

// Reason is the canonical one-line form, used in logs AND in the selftest's
// assertions. Having one formatter means the test compares against the same
// string a human reads in the log, rather than against a parallel description
// that could drift away from what the tool actually reports.
func (t Trigger) Reason() string {
	switch t.Kind {
	case "state_change":
		return fmt.Sprintf("state_change:%s %q->%q", t.Field, t.From, t.To)
	case "event":
		return fmt.Sprintf("event:%s %q", t.Field, t.To)
	case "interval":
		return fmt.Sprintf("interval:%dm", t.Minutes)
	default:
		if t.Field != "" {
			return t.Kind + ":" + t.Field
		}
		return t.Kind
	}
}

// --- observed state --------------------------------------------------------

type logState struct {
	gameRules string
	mapName   string
	zone      string
	location  string
}

// unverifiedPatternByName looks the shared parser up by NAME rather than by
// slice index. If someone renames or reorders unverifiedLocationPatterns in
// gamelog.go this returns nil and the selftest fails loudly, instead of this
// file silently binding to a different regex than it thinks it has.
func unverifiedPatternByName(name string) *regexp.Regexp {
	for _, up := range unverifiedLocationPatterns {
		if up.name == name {
			return up.re
		}
	}
	return nil
}

// autoDetector turns appended Game.log lines into Triggers.
//
// It holds no file handles and no clock, so the selftest can drive it with a
// literal sequence of lines and assert the exact triggers it produces. That is
// the whole reason the parsing lives here and not inline in the poll loop.
type autoDetector struct {
	st     logState
	primed bool
}

// Feed applies one line and returns any triggers it produced.
//
// While primed is false the state is updated but nothing fires - see the
// priming note in the file header.
func (d *autoDetector) Feed(line string) []Trigger {
	var out []Trigger

	// change records a state transition, emitting a trigger only once primed.
	change := func(field string, cur *string, next string) *Trigger {
		if next == "" || next == *cur {
			return nil
		}
		from := *cur
		*cur = next
		if !d.primed {
			return nil
		}
		return &Trigger{Kind: "state_change", Field: field, From: from, To: next}
	}

	// ORDER IS DETERMINISTIC and asserted by the selftest: gamerules, map,
	// zone, location, then the two events. A non-deterministic order would make
	// "which trigger did this capture record" depend on map iteration.

	if m := reGameRules.FindStringSubmatch(line); m != nil {
		if t := change("gamerules", &d.st.gameRules, m[1]); t != nil {
			out = append(out, *t)
		}
	}
	if m := reMap.FindStringSubmatch(line); m != nil {
		if t := change("map", &d.st.mapName, m[1]); t != nil {
			out = append(out, *t)
		}
	}

	// Zone, from the shared OnClientSpawned parser.
	zoneChangedTo := ""
	if re := unverifiedPatternByName("OnClientSpawned-zone"); re != nil {
		if m := re.FindStringSubmatch(line); m != nil {
			v := strings.TrimSpace(m[1])
			if plausibleLocation(v) {
				if t := change("zone", &d.st.zone, v); t != nil {
					out = append(out, *t)
					zoneChangedTo = v
				}
			}
		}
	}

	// Location, from all the unverified patterns, last plausible match wins.
	//
	// DEDUPE: an OnClientSpawned line sets zone AND location from the SAME
	// captured value, because the zone pattern is one of the location patterns.
	// Emitting both would report one fact as two triggers and inflate every
	// count in the selftest. Same fact, one trigger.
	for _, up := range unverifiedLocationPatterns {
		if m := up.re.FindStringSubmatch(line); m != nil {
			v := strings.TrimSpace(m[up.grp])
			if !plausibleLocation(v) {
				continue
			}
			if v == zoneChangedTo {
				d.st.location = v // keep state honest, suppress the duplicate
				continue
			}
			if t := change("location", &d.st.location, v); t != nil {
				out = append(out, *t)
			}
		}
	}

	// --- events: no before/after, they simply happened ---------------------

	if m := reLoadingScreen.FindStringSubmatch(line); m != nil {
		if d.primed {
			out = append(out, Trigger{
				Kind: "event", Field: "loading_screen",
				To: m[1] + " : " + m[2],
			})
		}
	}

	if strings.Contains(line, "OnClientSpawned") {
		if d.primed {
			out = append(out, Trigger{
				Kind: "event", Field: "client_spawned", To: d.st.zone,
			})
		}
	}

	return out
}

// --- tailing ---------------------------------------------------------------

// logTailer reads only what has been APPENDED since the last poll.
//
// Re-reading the whole file every 2 seconds would work on the 165 KB sample but
// Game.log grows for the length of a session; at 2-second polling that is a lot
// of pointless I/O against a file the game is actively writing.
type logTailer struct {
	path string
	off  int64
	det  *autoDetector
	part []byte // trailing partial line carried to the next poll
}

func newLogTailer(path string) *logTailer {
	return &logTailer{path: path, det: &autoDetector{}}
}

// Poll reads new bytes and returns the triggers they produced.
//
// The first call primes: it consumes the existing file and returns nothing.
func (t *logTailer) Poll() ([]Trigger, error) {
	f, err := openSharedRead(t.path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	st, err := f.Stat()
	if err != nil {
		return nil, err
	}

	// TRUNCATION / ROTATION. Starting a new game session replaces Game.log, so
	// the file gets SHORTER. Continuing to read from the old offset would skip
	// the whole new session and then read garbage from the middle of a line.
	// Treat it as a fresh file and re-prime, so the new session's backlog does
	// not fire a burst either.
	if st.Size() < t.off {
		t.off = 0
		t.part = nil
		t.det.primed = false
	}
	if st.Size() == t.off {
		return nil, nil
	}

	if _, err := f.Seek(t.off, io.SeekStart); err != nil {
		return nil, err
	}
	chunk, err := io.ReadAll(f)
	if err != nil {
		return nil, err
	}
	t.off += int64(len(chunk))

	// Stitch the carried partial line onto the front, and hold back any new
	// trailing partial. Without this a line split across two polls is parsed as
	// two broken lines and can match nothing - or worse, match wrongly.
	data := append(t.part, chunk...)
	t.part = nil
	if n := bytes.LastIndexByte(data, '\n'); n >= 0 {
		t.part = append([]byte(nil), data[n+1:]...)
		data = data[:n+1]
	} else {
		t.part = data
		data = nil
	}

	var triggers []Trigger
	sc := bufio.NewScanner(bytes.NewReader(data))
	sc.Buffer(make([]byte, 0, 64*1024), 4*1024*1024)
	for sc.Scan() {
		triggers = append(triggers, t.det.Feed(sc.Text())...)
	}

	if !t.det.primed {
		// Baseline established. Nothing above fired; from here on it can.
		t.det.primed = true
		return nil, nil
	}
	return triggers, sc.Err()
}

// --- the decision --------------------------------------------------------

type autoConfig struct {
	PollSeconds     int
	DebounceSeconds int
	IntervalMinutes int // 0 = interval fallback off
}

func defaultAutoConfig() autoConfig {
	return autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalMinutes: 10}
}

// autoRunner owns the debounce and interval decisions.
//
// The clock is a field so the selftest can drive minutes of behaviour in
// microseconds and assert it deterministically. A debounce tested by sleeping
// is a debounce tested once, slowly, and flakily.
type autoRunner struct {
	cfg     autoConfig
	now     func() time.Time
	lastCap time.Time
}

func newAutoRunner(cfg autoConfig, now func() time.Time) *autoRunner {
	return &autoRunner{cfg: cfg, now: now, lastCap: now()}
}

// decide returns the trigger to capture on, or nil to do nothing.
//
// Precedence is deliberate: a real state change always beats the interval
// fallback, and the fallback only speaks when nothing has been said.
func (r *autoRunner) decide(triggers []Trigger) *Trigger {
	now := r.now()

	if len(triggers) > 0 {
		if now.Sub(r.lastCap) < time.Duration(r.cfg.DebounceSeconds)*time.Second {
			return nil // debounced
		}
		t := triggers[0]
		if len(triggers) > 1 {
			// The others are named so the record does not imply this was the
			// only thing that happened in this poll.
			var rest []string
			for _, o := range triggers[1:] {
				rest = append(rest, o.Reason())
			}
			t.Note = "also in this poll: " + strings.Join(rest, "; ")
		}
		r.lastCap = now
		return &t
	}

	if r.cfg.IntervalMinutes > 0 &&
		now.Sub(r.lastCap) >= time.Duration(r.cfg.IntervalMinutes)*time.Minute {
		r.lastCap = now
		return &Trigger{
			Kind: "interval", Minutes: r.cfg.IntervalMinutes,
			Note: "no state change for the configured interval",
		}
	}
	return nil
}

// --- settings file ---------------------------------------------------------

// Settings live in a plain text file next to the exe so that a crew member who
// has never opened a terminal can change the interval. Command-line flags still
// win, so a support instruction ("run it with --interval 5 once") is not
// defeated by whatever is in the file.
const settingsFileName = "collector-settings.txt"

const settingsTemplate = `# citizen-collector settings
#
# Plain text. One setting per line, "name = value".
# Lines starting with # are notes and are ignored.
# Delete this file to go back to the defaults - a fresh one is written on the
# next run.

# Capture automatically while the game is running.
auto = true

# Take a picture every this many minutes even when nothing changes.
# Set to 0 to turn the timer off completely.
interval_minutes = 10

# How often to check the game log, in seconds.
poll_seconds = 2

# Never take two pictures closer together than this, in seconds.
debounce_seconds = 3

# Where the pictures go. Relative names are next to this file.
out = captures
`

type settings struct {
	values map[string]string
	path   string
	loaded bool
}

// loadSettings reads the file if it exists. A missing file is not an error -
// it means "use the defaults" - but an unreadable or malformed one is
// reported, never silently ignored.
func loadSettings(dir string) (*settings, []string) {
	s := &settings{values: map[string]string{}, path: filepath.Join(dir, settingsFileName)}
	var notes []string

	raw, err := os.ReadFile(s.path)
	if err != nil {
		if !os.IsNotExist(err) {
			notes = append(notes, fmt.Sprintf("could not read %s: %v (using defaults)", s.path, err))
		}
		return s, notes
	}
	s.loaded = true

	// Notepad writes UTF-8 with a BOM. Left in place the BOM becomes part of
	// the FIRST key name, so the first setting in the file is silently ignored
	// while every other one works - which is close to the worst possible
	// failure for a file a non-technical user edits.
	raw = bytes.TrimPrefix(raw, []byte{0xEF, 0xBB, 0xBF})

	for n, line := range strings.Split(string(raw), "\n") {
		line = strings.TrimSpace(strings.TrimSuffix(line, "\r"))
		if line == "" || strings.HasPrefix(line, "#") || strings.HasPrefix(line, ";") {
			continue
		}
		eq := strings.Index(line, "=")
		if eq < 0 {
			notes = append(notes, fmt.Sprintf("%s line %d: no '=', ignored: %q", settingsFileName, n+1, line))
			continue
		}
		k := strings.ToLower(strings.TrimSpace(line[:eq]))
		v := strings.TrimSpace(line[eq+1:])
		if k == "" {
			notes = append(notes, fmt.Sprintf("%s line %d: empty name, ignored", settingsFileName, n+1))
			continue
		}
		s.values[k] = v
	}
	return s, notes
}

// writeSettingsTemplateIfAbsent creates the file the first time, so the user
// has something to edit rather than having to invent it. It NEVER overwrites an
// existing file - that would silently discard whatever the user had set.
func writeSettingsTemplateIfAbsent(dir string) (string, bool, error) {
	p := filepath.Join(dir, settingsFileName)
	if _, err := os.Stat(p); err == nil {
		return p, false, nil
	} else if !os.IsNotExist(err) {
		return p, false, err
	}
	if err := os.WriteFile(p, []byte(settingsTemplate), 0o644); err != nil {
		return p, false, err
	}
	return p, true, nil
}

func (s *settings) str(key string) (string, bool) {
	v, ok := s.values[key]
	return v, ok
}

func (s *settings) intVal(key string) (int, bool, error) {
	v, ok := s.values[key]
	if !ok {
		return 0, false, nil
	}
	var n int
	if _, err := fmt.Sscanf(strings.TrimSpace(v), "%d", &n); err != nil {
		return 0, true, fmt.Errorf("%s: %q is not a whole number", key, v)
	}
	return n, true, nil
}

func (s *settings) boolVal(key string) (bool, bool) {
	v, ok := s.values[key]
	if !ok {
		return false, false
	}
	switch strings.ToLower(strings.TrimSpace(v)) {
	case "1", "true", "yes", "on":
		return true, true
	case "0", "false", "no", "off":
		return false, true
	}
	return false, false
}

// --- console -------------------------------------------------------------

// hideConsole detaches the visible console window.
//
// "No console window. Survives being left running." The proper build for
// unattended use is
//
//	go build -ldflags "-H windowsgui" -o collector.exe .
//
// which has no console at all. But the tool is also started by
// double-clicking the ordinary build, and that pops a window which the user
// will eventually close - killing the collector. Hiding it covers that case
// without needing a second binary.
//
// The console is hidden, not freed: freeing it would break the log writer's
// underlying handles on some Windows builds.
func hideConsole() bool {
	h, _, _ := procGetConsoleWindow.Call()
	if h == 0 {
		return false // already windowless - built with -H windowsgui
	}
	procShowWindow.Call(h, swHide)
	return true
}

// --- the loop --------------------------------------------------------------

type autoDeps struct {
	// capture is injected so the selftest can exercise the loop's decisions
	// without a game window or a PNG encoder.
	capture   func(t Trigger) (string, error)
	gameAlive func() error
	logf      func(format string, args ...interface{})

	// hotkeys delivers manual capture requests while auto mode is running.
	//
	// Auto mode fires on STATE CHANGE, and standing still is not a state
	// change. At a shop terminal, a mission board or an inventory screen -
	// precisely the screens worth photographing - nothing is written to
	// Game.log, so nothing triggers. The hotkey is the only way to say
	// "capture THIS", which is why it has to reach this loop.
	//
	// A nil channel is valid and simply never fires: select on a nil channel
	// blocks forever, so callers that have no hotkey need no special case.
	hotkeys <-chan struct{}

	// hotkeyName is the registered key's canonical name, recorded on the frames
	// it produces so a manual capture is distinguishable afterwards.
	hotkeyName string

	// findLog resolves the log to watch. Injected so the selftest can drive
	// discovery, staleness and the heartbeat without a Star Citizen install.
	// Nil means use the real FindGameLog.
	findLog func() (path string, how string)

	// now is the clock. Injected so the heartbeat and the staleness warning can
	// be tested in milliseconds instead of in minutes.
	now func() time.Time
}

// heartbeatEvery is how often the auto log says "still alive" during a quiet
// period.
//
// # WHY IT EXISTS
//
// collector-auto.log was written ONLY on capture. During a quiet stretch - the
// game sitting on a landing pad, or the collector silently broken - the file
// said exactly the same thing in both cases: nothing. A running collector and a
// dead one were indistinguishable from outside.
//
// That is the same shape as a backup reporting exit 0 having copied nothing:
// silence read as health. So the loop now states its own liveness on a timer,
// with the numbers that make the statement checkable rather than decorative.
const heartbeatEvery = 3 * time.Minute

// stalenessAfter is how long a watched log may sit at the same size, WHILE A
// GAME WINDOW EXISTS, before the loop says so.
//
// A game running and writing nothing to the log it is supposedly watching means
// the wrong file is being watched - the LIVE/PTU mix-up being the obvious
// cause. Watching a dead file should not look like a quiet game.
const stalenessAfter = 5 * time.Minute

// runAuto is the unattended loop.
//
// It is written to SURVIVE. Every recoverable problem - game not running, log
// briefly unreadable, capture failed - is logged and the loop continues. The
// only things that stop it are a stop signal and a genuinely unusable
// configuration, because a collector that exits when the game closes is a
// collector that is never running when the game opens.
func runAuto(cfg autoConfig, logPath string, deps autoDeps, stop <-chan struct{}) error {
	now := deps.now
	if now == nil {
		now = time.Now
	}
	findLog := deps.findLog
	if findLog == nil {
		findLog = findLogFromRunningGame
	}
	runner := newAutoRunner(cfg, now)

	var tailer *logTailer
	lastLogPath := ""

	deps.logf("auto mode started: poll %ds, debounce %ds, interval %s",
		cfg.PollSeconds, cfg.DebounceSeconds, intervalDesc(cfg.IntervalMinutes))

	// WHICH LOG, AND HOW IT WAS CHOSEN - stated at every start.
	//
	// In --auto this resolves before any game window exists, so the scan picks
	// the first of LIVE, PTU, EPTU, TECH-PREVIEW that is installed. That is
	// always LIVE on a machine that has both. Printing the path AND the reason
	// means a session spent watching the wrong install is visible in the first
	// line of the log instead of being inferred later from missing captures.
	// reportedPath is what the heartbeat names. It is seeded here so that a
	// heartbeat arriving before the first successful poll does not claim "no
	// log resolved yet" one line under a startup line that just resolved one.
	// Two lines contradicting each other is worse than either line alone.
	reportedPath := ""
	if p, how := findLog(); p == "" {
		deps.logf("startup: NO Game.log resolved - %s", how)
	} else {
		deps.logf("startup: watching %s (%s)", p, how)
		reportedPath = p
	}

	// Heartbeat and staleness bookkeeping.
	var (
		lastBeat    = now()
		bytesAtBeat int64
		captures    int
		lastSize    int64 = -1
		lastGrowth        = now()
		staleWarned bool
	)

	ticker := time.NewTicker(time.Duration(cfg.PollSeconds) * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-stop:
			deps.logf("auto mode stopping")
			return nil

		case <-deps.hotkeys:
			// A human asked for THIS frame. It deliberately bypasses the
			// debounce and the interval bookkeeping: those exist to stop the
			// automatic triggers from flooding the folder, and an explicit
			// press is not one of them.
			//
			// The window gate still applies, because there is nothing to
			// photograph without a game window - but a press that lands with no
			// window SAYS SO. A hotkey that appears to do nothing is the defect
			// being fixed here, and "pressed but no window" is information.
			// LOGGED ON RECEIPT, BEFORE ANYTHING IS ATTEMPTED.
			//
			// Without this line the log recorded "hotkey registered" and then
			// nothing until a capture SUCCEEDED, so these two faults were
			// indistinguishable:
			//
			//   the press never arrived        (nothing reached this process)
			//   the press arrived and failed   (capture broke downstream)
			//
			// They have completely different causes and completely different
			// fixes, and telling them apart took an evening of guessing. Now it
			// takes one keystroke: press the key and look. A line means the
			// press arrived; no line means it did not.
			//
			// The leading suspect for a press that never arrives is Star
			// Citizen in exclusive fullscreen taking the key before any global
			// hotkey sees it. This line is what makes that diagnosable rather
			// than suspected.
			deps.logf("hotkey press received (%s)", deps.hotkeyName)

			if err := deps.gameAlive(); err != nil {
				deps.logf("hotkey press received but no game window: %v", err)
				continue
			}
			t := Trigger{Kind: "hotkey", Note: deps.hotkeyName}
			out, err := deps.capture(t)
			if err != nil {
				deps.logf("hotkey capture FAILED: %v", err)
				continue
			}
			captures++
			deps.logf("captured %s  <- %s (manual)", filepath.Base(out), t.Reason())
			continue

		case <-ticker.C:
		}

		// DETECTION RUNS FIRST, AND UNCONDITIONALLY (WO-UI-01 §6).
		//
		// This used to sit BELOW the window gate. When the game window was not
		// detected the loop hit `continue` and never re-resolved, so the watched
		// path stayed whatever the startup scan had picked - LIVE - and the
		// heartbeat went on reporting it as though it were current. Detection
		// could not re-run at exactly the moment it mattered most, and an hour
		// of "0 bytes read since last line" looked like a quiet game rather than
		// a collector pointed at the wrong install.
		//
		// Resolving before the gate means the answer tracks reality whether or
		// not the game is currently visible, which is what "continuously" has to
		// mean to be worth anything.
		gameErr := deps.gameAlive()

		p, how := findLog()
		if p != "" && p != lastLogPath {
			deps.logf("watching %s (%s)", p, how)
			tailer = newLogTailer(p)
			lastLogPath = p
			lastSize = -1
			lastGrowth = now()
			staleWarned = false
		}
		if p != "" {
			reportedPath = p
		}

		// THE HEARTBEAT. Emitted whether or not a game window exists, because
		// "no game running" is itself a state worth being able to read back.
		// It is the only line that proves the process is still alive.
		//
		// It now states whether the game is actually there. Saying "watching X"
		// while no game is running invited exactly the wrong conclusion - that
		// the file was being followed and had gone quiet, rather than that
		// nothing was being followed at all.
		if t := now(); t.Sub(lastBeat) >= heartbeatEvery {
			var off int64
			watching := reportedPath
			if tailer != nil {
				off = tailer.off
			}
			if watching == "" {
				watching = "(no log resolved yet)"
			}
			presence := "game running"
			if gameErr != nil {
				presence = "NO game window - not capturing"
			}
			deps.logf("alive: %s, watching %s, %d bytes read since last line, %d captures total",
				presence, watching, off-bytesAtBeat, captures)
			lastBeat = t
			bytesAtBeat = off
		}

		// THE WINDOW GATE. No StarCitizen.exe window means no capture, and it
		// also means the log is not moving, so there is nothing to miss.
		// allowAny is not a parameter here and cannot be: --allow-any-window is
		// manual-only by construction, not by convention.
		if gameErr != nil {
			// The game is gone, so the log standing still proves nothing. Reset
			// the staleness clock rather than accusing a file of being dead
			// when nothing was writing to it in the first place.
			lastGrowth = now()
			staleWarned = false
			continue
		}

		if p == "" {
			deps.logf("no Game.log yet (%s)", how)
			continue
		}

		triggers, err := tailer.Poll()
		if err != nil {
			deps.logf("log read failed, will retry: %v", err)
			continue
		}

		// THE STALENESS WARNING.
		//
		// A game window exists, so something SHOULD be writing to the log. If
		// the file has not grown in stalenessAfter, the overwhelmingly likely
		// cause is that this is the wrong file - LIVE while the session is on
		// PTU. Watching a dead file looks exactly like a quiet game from in
		// here, and only saying so distinguishes them.
		//
		// Warned once per stall, not every poll: a line every two seconds for
		// five minutes would bury the log it is trying to make readable.
		if tailer.off != lastSize {
			lastSize = tailer.off
			lastGrowth = now()
			staleWarned = false
		} else if !staleWarned && now().Sub(lastGrowth) >= stalenessAfter {
			deps.logf("WARNING: %s has not grown in %s while a game window is open. "+
				"This is usually the wrong install - if the session is on PTU or EPTU, "+
				"start with --gamelog pointing at that Game.log.",
				lastLogPath, stalenessAfter)
			staleWarned = true
		}

		t := runner.decide(triggers)
		if t == nil {
			continue
		}

		out, err := deps.capture(*t)
		if err != nil {
			deps.logf("capture FAILED (%s): %v", t.Reason(), err)
			continue
		}
		captures++
		deps.logf("captured %s  <- %s", filepath.Base(out), t.Reason())
	}
}

func intervalDesc(m int) string {
	if m <= 0 {
		return "off"
	}
	return fmt.Sprintf("%dm", m)
}

// openAutoLog opens the append-only log for unattended runs. With no console
// there is nowhere else for the record to go, and a collector that has been
// running for six hours needs to be able to say what it did.
func openAutoLog(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
}

var _ = syscall.Handle(0)
