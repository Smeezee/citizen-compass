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
//
// Value is "high" or "low" and decides whether a frame is actually taken.
//
// # WHY THIS FIELD EXISTS - THE 40-CAPTURE AUDIT, 2026-08-08
//
// Sleven looked through a session's pictures and said they were "random shots
// of nothing", and that he had to sit for ten minutes to get one worth having.
// Rather than take that as a tuning complaint, the 40 sidecars on disk were
// tallied by what fired them:
//
//	14  interval                  a blind timer
//	10  state_change:gamerules    every one of them to or from SC_Frontend
//	                              - which IS the main menu
//	10  event:client_spawned      the instant of appearing, before anything
//	                              is on screen
//	 3  event:loading_screen      literally photographs of loading screens
//	 3  hotkey                    the only deliberate ones
//
// Twenty-three of forty fired on menu, loading and spawn transitions. Zero
// fired on a shop, a kiosk or a mission board. The pattern repeats identically
// every session because it is the game BOOTING: menu, spawn, load, spawn - and
// then the collector goes blind and falls back to the timer.
//
// So the triggers were not broken. They were working perfectly, on the least
// interesting moments a session contains.
//
// The fix is not a better timer. The log ALREADY announces the moments that
// matter - RequestLocationInventory fires when a shop terminal is opened, and
// the four transaction families fire on every buy and sell. Those patterns were
// in the miner, which reads the log after the fact, and were never in the
// detector, which decides when to look. Two halves that were never connected:
// the collector already knew when a shop was open, it just never took a picture.
//
// Low-value triggers still update state and are still logged. They simply do
// not spend a 3 MB frame. Nothing is lost except the noise.
type Trigger struct {
	Kind    string `json:"kind"`
	Field   string `json:"field,omitempty"`
	From    string `json:"from,omitempty"`
	To      string `json:"to,omitempty"`
	Seconds int    `json:"seconds,omitempty"`
	Value   string `json:"value,omitempty"`

	// Press and Index make a burst REASSEMBLABLE from the sidecars alone.
	// Without them a burst is a handful of frames a second apart with no
	// statement that they belong together, which is the same data with the
	// relationship thrown away.
	Press int `json:"burst_press,omitempty"`
	Index int `json:"burst_index,omitempty"`

	Note string `json:"note,omitempty"`
}

const (
	valueHigh = "high"
	valueLow  = "low"
)

// isHigh treats an unset value as high.
//
// Deliberate: a trigger added later by somebody who forgets this field should
// CAPTURE rather than be silently dropped. The failure mode of over-capturing
// is a wasted frame; the failure mode of under-capturing is a moment that is
// gone forever. Those are not symmetric.
func (t Trigger) isHigh() bool { return t.Value != valueLow }

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
		return fmt.Sprintf("interval:%ds", t.Seconds)
	case "burst":
		return fmt.Sprintf("burst:%s %q", t.Field, t.To)
	case "keypress":
		return fmt.Sprintf("keypress:%s (%s)", t.Field, t.To)
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
		return &Trigger{Kind: "state_change", Field: field, From: from, To: next, Value: valueLow}
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
				To: m[1] + " : " + m[2], Value: valueLow,
			})
		}
	}

	if strings.Contains(line, "OnClientSpawned") {
		if d.primed {
			out = append(out, Trigger{
				Kind: "event", Field: "client_spawned", To: d.st.zone,
				Value: valueLow,
			})
		}
	}

	// --- the two that were missing, and are the whole point ----------------
	//
	// Both patterns are borrowed from gamelog_mine.go rather than re-written
	// here. Same package, one definition: a second copy would drift, and the
	// day CIG changes the format one of the two copies would keep matching and
	// hide the other's failure.
	//
	// reMineLocation is a VERIFIED pattern - confirmed live in 4.10 - and it
	// fires when a shop or inventory terminal is opened. That is the moment
	// prices are on the screen.
	if m := reMineLocation.FindStringSubmatch(line); m != nil {
		if v := strings.TrimSpace(m[1]); plausibleLocation(v) && d.primed {
			out = append(out, Trigger{
				Kind: "event", Field: "terminal_open", To: v, Value: valueHigh,
				Note: "a shop or inventory terminal was opened",
			})
		}
	}

	// A transaction is the strongest signal in the whole log: the player is
	// standing at a kiosk with a price list in front of them. The log gives us
	// the price in text; the frame gives us everything AROUND the price that
	// the log does not carry - stock levels, the rest of the list, the shop's
	// layout.
	if m := reMineTxn.FindStringSubmatch(line); m != nil && d.primed {
		side := strings.ToLower(m[2])
		market := "item"
		if strings.HasSuffix(m[1], "Commodity") {
			market = "commodity"
		}
		out = append(out, Trigger{
			Kind: "event", Field: "transaction", To: market + " " + side,
			Value: valueHigh,
			Note:  "a buy or sell happened - the kiosk is on screen right now",
		})
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

	// onLine receives EVERY appended line, live.
	//
	// # WHY THIS EXISTS - SLEVEN, 2026-08-08
	//
	//	"if it takes 2 seconds to open a terminal and find a part purchase
	//	 that part and then back out of that terminal, it's done the entire
	//	 transaction and has no recollection of the data until we get to the
	//	 game log."
	//
	// Exactly right, and it was an architectural accident. This tailer already
	// read every appended line - it had to, to fire triggers - and then threw
	// the content away. The miner was a SEPARATE pass over the same file, run
	// at start and at game exit. So a purchase that took two seconds sat
	// unrecorded for the rest of the session, and if the process died in
	// between (which it did, every fourteen minutes) it was recorded late or
	// not at all.
	//
	// Two readers of one file, one of them blind to what the other was for.
	// Now the same line that decides whether to take a picture also lands in
	// the dataset, in the same pass, as it happens.
	onLine func(string)
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
		line := sc.Text()
		// Data first. A line must reach the dataset even if it produces no
		// trigger and even if the detector is still priming - priming exists to
		// stop a burst of stale CAPTURES, not to discard facts.
		if t.onLine != nil {
			t.onLine(line)
		}
		triggers = append(triggers, t.det.Feed(line)...)
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

	// HotkeyBurst is the rhythm one deliberate press produces. FrameSeconds 0
	// means single-frame mode: one press, one picture, exactly as before. That
	// is a supported configuration and not a disabled feature - if bursts turn
	// out to be wrong for some situation it must be a settings change, not a
	// rebuild.
	HotkeyBurst burstConfig

	// Burst is the keep-shooting-while-a-terminal-is-open rhythm.
	Burst burstConfig

	// Keys the player asked to be watched. See keywatch.go.
	Keys []*watchedKey
}

func defaultAutoConfig() autoConfig {
	return autoConfig{PollSeconds: 2, DebounceSeconds: 3,
		HotkeyBurst: defaultHotkeyBurstConfig(),
	}
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

	// skipped holds the low-value triggers dropped by the most recent decide().
	// Reused between calls, so read it before the next one.
	skipped []Trigger

	// burst follows an open shop terminal. See session_burst.go.
	burst *burstState

	// keys fires when the player presses something they told us about.
	keys *KeyWatcher

	// burstStop carries the reason the last burst ended, for the caller to log.
	burstStop string

	// gameRules is the detector's latest observation, fed in by the loop. It is
	// the ONLY input to the in-world gate - see inGameFromRules in gamelog.go.
	gameRules string

	// menuSkipSaid keeps the pause to one line per state change rather than one
	// line every interval. At 120s a menu session would otherwise write a line
	// every two minutes saying nothing new, which is how a log stops being read.
	menuSkipSaid bool

	// skipNote is emitted once by the loop when the gate first closes.
	skipNote string

	// presses counts deliberate hotkey presses for the whole session, so every
	// burst frame can name the press it came from.
	presses int
}

func newAutoRunner(cfg autoConfig, now func() time.Time) *autoRunner {
	return &autoRunner{cfg: cfg, now: now, lastCap: now(),
		burst: newBurstState(defaultHotkeyBurstConfig()), keys: NewKeyWatcher(cfg.Keys)}
}

// decide returns the trigger to capture on, or nil to do nothing.
//
// Precedence is deliberate: a real state change always beats the interval
// fallback, and the fallback only speaks when nothing has been said.
// decide() IS GONE, and this note stands where it was.
//
// It took the detector's triggers and answered "take a picture?" - on an
// interval, on a state change, on a loading screen, a spawn, a terminal, a
// transaction. §6 removed the feature outright rather than switching it off,
// because a disabled capture path is a capture path waiting for a settings
// file to turn it back on, and the window now tells people nothing captures on
// its own.
//
// What replaced it is nothing. The loop takes a picture when the person presses
// the key, and at no other time.

// hotkeyPressed turns one press into a burst, or into the single frame the
// caller should take when bursting is switched off.
//
// Returns (started, logLine). `started` false means single-frame mode and the
// loop takes one picture the way it always did.
func (r *autoRunner) hotkeyPressed(what string, at time.Time) (bool, string, *Trigger) {
	if r.cfg.HotkeyBurst.FrameSeconds <= 0 {
		return false, "", nil
	}
	r.presses++
	why, first := r.burst.BeginHotkey(what, at, r.cfg.HotkeyBurst, r.presses)
	return true, why, first
}

// burstActive reports whether a burst wants the loop to wake on its rhythm
// rather than only on the poll ticker.
func (r *autoRunner) burstActive() bool { return r.burst.Active() }

// setGameRules feeds the runner the detector's own observation.
//
// Passed in rather than read from a shared pointer so the runner stays
// testable with a literal value and holds no reference to the tailer.
func (r *autoRunner) setGameRules(v string) {
	if v == r.gameRules {
		return
	}
	r.gameRules = v
	// A change of state earns one more sentence. Without this the pause is
	// announced once ever, and a player who goes menu -> world -> menu in one
	// session sees nothing the second time.
	r.menuSkipSaid = false
}

// noteCapture tells the runner a frame was taken by a path that does not go
// through decide - today that means a hotkey press.
//
// WHY THIS EXISTS. The interval means "it has been this long since the last
// picture", not "since the last AUTOMATIC picture". Without this a manual press
// left lastCap untouched and the interval fired seconds later on a scene that
// had just been photographed. At ten minutes that was a curiosity. At sixty
// seconds it would be a duplicate almost every time.
func (r *autoRunner) noteCapture(at time.Time) { r.lastCap = at }

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

# Watch the game while it runs, and read its log for the diary.
#
# THIS TAKES NO PICTURES BY ITSELF. It is what keeps the collector reading the
# log so the diary is complete and so a picture you DO take knows where you
# were.
auto = true

# How often to check the game log, in seconds.
poll_seconds = 2

# Never take two pictures closer together than this, in seconds.
debounce_seconds = 3

# NOTHING HERE TAKES A PICTURE ON ITS OWN, AND NOTHING CAN BE MADE TO.
#
# This file used to carry interval_seconds, capture_low_value, burst_seconds and
# burst_max_frames. Each let the program decide to photograph something - on a
# timer, on a loading screen, at the instant of spawning, when a shop terminal
# opened. Version one removed the feature outright rather than defaulting it
# off, because a setting that can turn automatic capture back on is automatic
# capture with an extra step.
#
# A picture is taken when you press the key. That is the entire list.

# ONE PRESS OF THE HOTKEY TAKES A SHORT BURST, not a single picture, so you can
# scroll a price board for a few seconds while it records.
#
# hotkey_burst_seconds is how often it shoots, in seconds.
# hotkey_burst_frames is how many pictures one press may take.
#
# Pressing again DURING a burst extends it rather than starting a second one -
# the log says so when it happens, and every picture records which press it
# belongs to and where it sits in the burst.
#
# Set hotkey_burst_seconds = 0 for the old behaviour: one press, one picture.
hotkey_burst_seconds = 1
hotkey_burst_frames = 6

# Keys you HOLD DOWN for an activity - mining laser, salvage beam, guns.
#
# These are RECORDED, not photographed: the collector notes that you were
# mining, and for how long, in the diary. Holding a key no longer takes a run of
# pictures, because nothing takes a picture except the hotkey.
#
#   capture_keys_held = mouse1:guns, m:mining laser, v:salvage beam
capture_keys_held =

# Take a picture when YOU press a key. Empty by default - this tool does not
# guess at your bindings.
#
# Write the keys you actually use, with a short label so the picture records
# what you were doing:
#
#   capture_keys = tab:scan, alt+m:mining laser, v:salvage beam
#
# A mining ping lasts about three seconds and Star Citizen writes NOTHING about
# it to its log - checked against 227 sessions. A timer will never catch it.
# Your own keypress will.
#
# It only reads whether the key is down. It never intercepts, consumes or sends
# a keypress, so the game gets every one exactly as it would have.
capture_keys =

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
	hotkeys <-chan string

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

	// pollNow is a TEST-ONLY second reason to wake, and it acknowledges.
	//
	// The staleness and heartbeat fixtures drive this loop with a fake clock.
	// fakeClock.Advance sets a variable; it notifies nothing and wakes nothing,
	// so the loop only discovers that five fake minutes have passed the next
	// time its REAL ticker fires. The fixture used to bridge that with a
	// four-second wall-clock wait, which is a race - and it lost that race
	// roughly one run in five on an idle machine, measured, before this
	// existed.
	//
	// A poll requested through here carries a channel that the loop CLOSES once
	// that poll's body has finished. So the fixture can say "advance the clock,
	// run one poll, and tell me when it is done" instead of advancing a
	// variable and hoping. No assertion then depends on how many real seconds
	// elapsed.
	//
	// Nil in production, and a nil channel blocks forever in a select, so this
	// case simply is not there when nobody injected one. It adds no branch to
	// the running collector beyond one more select arm that never fires.
	pollNow <-chan chan struct{}

	// sabotage deliberately BREAKS the staleness bookkeeping. Test-only, and it
	// is here rather than simulated because of hard rule 12: a check that has
	// never been observed failing is not known to work, and the two negative
	// staleness checks - "warns once per stall" and "growth clears the
	// warning" - had never been observed failing on demand.
	//
	// There is no way to break either of those from outside the loop. The
	// alternative was a fixture that feeds its own assertion a fake log and
	// calls that a control, which proves the ASSERTION can fail and says
	// nothing about the loop. This proves the loop.
	//
	// Zero value is sabotageNone, so production gets exactly the behaviour it
	// had before this field existed. The selftest asserts that default.
	sabotage stalenessSabotage

	// stalenessAfter overrides the package constant, for tests only.
	//
	// It exists so a control can BREAK the staleness warning on demand - set it
	// absurdly high and every staleness check must fail. A check that has never
	// been observed failing is not known to work (hard rule 12), and there is
	// no other way to break this one from outside without editing the loop.
	//
	// Zero means the constant, which is what production always gets.
	stalenessAfter time.Duration

	// onLogLine receives every appended Game.log line as it is written, so the
	// dataset is current during play rather than at exit. See logTailer.onLine.
	onLogLine func(string)

	// onGameExit fires ONCE on the transition from "game running" to "game
	// gone". Mining the log at that moment is the point: the file is finished,
	// so the session is complete rather than half-written.
	//
	// Injected rather than called directly so the selftest can prove it fires
	// exactly once per session and NOT on every poll where the game is absent -
	// which is the obvious way to get this wrong, and would re-read the whole
	// archive every two seconds forever.
	//
	// DO NOT ADD A TIMER HERE. Asked and answered, 2026-08-13.
	//
	// Mining is driven by two events and nothing else: this one, and an export
	// (BuildExport mines first so a SEND never ships a stale file). A periodic
	// pass would re-read the entire archive on a clock for no gain, because
	// between exits there is nothing new in it to find.
	//
	// AND THERE IS DELIBERATELY NO MINE ON STARTUP, which is worth stating
	// because it looks like an omission and is not. `gameWasAlive` below is a
	// plain bool, so it starts false and no exit transition can fire at launch.
	// A startup pass would be a no-op by construction: nothing can have been
	// appended to the archive since the last exit pass ran over it. That is
	// exactly why a real run reports "244 logs read, 0 new rows" and says so in
	// English rather than looking broken.
	//
	// Mining on EXIT rather than on a timer is also the better of the two on
	// its merits: the session's log is complete at that moment, so it is read
	// once in full instead of repeatedly while half-written.
	onGameExit func()
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

// stalenessSabotage names the ways the staleness bookkeeping can be broken on
// purpose, so the checks that exist to catch each one can be seen catching it.
// Never set outside a selftest. See autoDeps.sabotage.
type stalenessSabotage int

const (
	// sabotageNone is the zero value and the only thing production ever uses.
	sabotageNone stalenessSabotage = iota
	// sabotageWarnEveryPoll drops the warn-once suppression, so a stalled log
	// is reported on every single poll. "warns once per stall" must fail.
	sabotageWarnEveryPoll
	// sabotageNeverReset clears the warned flag on growth but NOT the staleness
	// clock, so the loop re-warns about a file that has started working again.
	// "a log that starts growing again is NOT reported stale" must fail.
	//
	// WHY THAT SHAPE AND NOT "SKIP THE WHOLE RESET". Skipping both leaves
	// staleWarned latched at true, so the loop stays silent, the count never
	// moves, and the check PASSES - which is what the first version of this
	// control did, and it is worth writing down: that check cannot detect a
	// broken reset on its own. It detects a reset that clears the flag without
	// clearing the clock, which is the version of this bug that produces a
	// visible symptom - a collector complaining every poll about a log that is
	// moving.
	sabotageNeverReset
)

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

	deps.logf("auto mode started: poll %ds, debounce %ds. Pictures are taken "+
		"when you press the key and at no other time.",
		cfg.PollSeconds, cfg.DebounceSeconds)

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

	// The staleness window. The constant unless a test overrode it - see
	// autoDeps.stalenessAfter for why that override exists.
	staleWindow := deps.stalenessAfter
	if staleWindow <= 0 {
		staleWindow = stalenessAfter
	}

	// Heartbeat and staleness bookkeeping.
	var (
		lastBeat     = now()
		bytesAtBeat  int64
		captures     int
		lastSize     int64 = -1
		lastGrowth         = now()
		staleWarned  bool
		gameWasAlive bool
	)

	ticker := time.NewTicker(time.Duration(cfg.PollSeconds) * time.Second)
	defer ticker.Stop()

	// A BURST CAN BE FASTER THAN THE POLL, so the loop needs a second reason to
	// wake - not a second reason to CAPTURE. The poll is 2s and a hotkey burst
	// runs at 1 frame/second, so waiting for the poll ticker would silently
	// halve the rate somebody configured.
	//
	// IT EXISTS ONLY WHILE A BURST DOES. The first version was a permanent
	// 250ms ticker, which woke the loop eight times per poll for the entire
	// life of the process to do nothing - a burst is a few seconds of a
	// session. A nil channel blocks forever in a select, so when no burst is
	// running this case simply is not there.
	//
	// Everything it wakes goes through exactly the same decide() as an ordinary
	// poll. It produces no frames of its own.
	var burstTick *time.Ticker
	var burstC <-chan time.Time
	stopBurstTick := func() {
		if burstTick != nil {
			burstTick.Stop()
			burstTick, burstC = nil, nil
		}
	}
	startBurstTick := func() {
		if burstTick == nil {
			burstTick = time.NewTicker(250 * time.Millisecond)
			burstC = burstTick.C
		}
	}
	defer stopBurstTick()

	// pendingAck belongs to the poll that is currently being processed, and it
	// is closed at the TOP of the next iteration - which is precisely the
	// moment that poll's body has finished, including every `continue` path
	// through it. Closing it at the bottom of the body would miss those, and a
	// "poll complete" signal that skips the early-exit paths is worse than
	// none: a fixture would wait for a signal that never comes.
	var pendingAck chan struct{}

	for {
		if pendingAck != nil {
			close(pendingAck)
			pendingAck = nil
		}

		select {
		case <-stop:
			deps.logf("auto mode stopping")
			return nil

		case ack := <-deps.pollNow:
			// Test-only. See autoDeps.pollNow. Nil in production, so this arm
			// never fires there.
			pendingAck = ack

		case via := <-deps.hotkeys:
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
			// The mechanism is named because two of them are running and they
			// fail under different conditions - see pollHotkey. One grep after a
			// session says which path is carrying the load on this machine and
			// this renderer, instead of leaving it to be inferred.
			deps.logf("hotkey press received (%s, via %s)", deps.hotkeyName, via)

			if err := deps.gameAlive(); err != nil {
				deps.logf("hotkey press received but no game window: %v", err)
				continue
			}
			// ONE PRESS, A BURST OF FRAMES. Sleven: "Make the hot key a burst.
			// That way I can scroll for a few seconds and try to capture
			// multiple things."
			//
			// The frames themselves come from burstState.Due() below, the same
			// producer the terminal burst uses. This case only STARTS or
			// EXTENDS - it does not take pictures of its own, or there would be
			// two things shooting and the record would not say which.
			started, why, first := runner.hotkeyPressed(deps.hotkeyName+" via "+via, now())
			if started {
				deps.logf("%s", why)
				// Frame 1 is taken here, above the window gate, so a press
				// always produces a picture. The rest arrive from decide().
				if first != nil {
					out, err := deps.capture(*first)
					if err != nil {
						deps.logf("hotkey capture FAILED: %v", err)
						Activity("You pressed %s - but the picture could not be taken: %v",
							deps.hotkeyName, err)
						Activity("You pressed %s - but the picture could not be "+
							"taken: %v", deps.hotkeyName, err)
						continue
					}
					captures++
					runner.noteCapture(now())
					deps.logf("captured %s  <- %s (manual)", filepath.Base(out), first.Reason())
					// §7: the person sees WHICH KEYS did this, in the window,
					// as it happens. Somebody who hit Alt+F3 by accident should
					// learn it here rather than find a mystery picture later.
					ActivityCapture(deps.hotkeyName, filepath.Base(out),
						"holding it keeps taking pictures while you scroll")
				}
				continue
			}

			// Single-frame mode, reached by setting hotkey_burst_seconds = 0.
			t := Trigger{Kind: "hotkey", Note: deps.hotkeyName + " via " + via}
			out, err := deps.capture(t)
			if err != nil {
				deps.logf("hotkey capture FAILED: %v", err)
				Activity("You pressed %s - but the picture could not be taken: %v",
					deps.hotkeyName, err)
				continue
			}
			captures++
			// A manual frame counts as "the last picture" for interval
			// purposes. Without this the fallback fires seconds after a press,
			// on a scene that was just photographed.
			runner.noteCapture(now())
			deps.logf("captured %s  <- %s (manual)", filepath.Base(out), t.Reason())
			ActivityCapture(deps.hotkeyName, filepath.Base(out), "")
			continue

		case <-ticker.C:

		case <-burstC:
			// Reached only while a burst is running - burstC is nil otherwise.
			// If the burst ended between the tick and here, stand the fast
			// clock down and let the ordinary poll take over.
			if !runner.burstActive() {
				stopBurstTick()
				continue
			}
		}

		// Keep the fast clock in step with the burst, wherever the burst was
		// started or ended - a press, a terminal opening, a ceiling being hit.
		// One place decides, so the two cannot drift apart.
		if runner.burstActive() {
			startBurstTick()
		} else {
			stopBurstTick()
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

		// THE EDGE, NOT THE LEVEL. gameWasAlive is what makes this fire once
		// when the player quits, instead of on every tick for the rest of the
		// night.
		if gameWasAlive && gameErr != nil {
			gameWasAlive = false
			if deps.onGameExit != nil {
				deps.logf("game closed - reading the session log")
				deps.onGameExit()
			}
		} else if !gameWasAlive && gameErr == nil {
			gameWasAlive = true
		}

		p, how := findLog()
		if p != "" && p != lastLogPath {
			deps.logf("watching %s (%s)", p, how)
			tailer = newLogTailer(p)
			tailer.onLine = deps.onLogLine
			lastLogPath = p
			lastSize = -1
			lastGrowth = now()
			staleWarned = false

			// The byte counter is per FILE. Without this the next heartbeat
			// subtracts the new file's offset from the old file's, and reports
			// something like "-560917 bytes read since last line" - a number
			// that describes nothing and undermines every other figure on the
			// line. Observed live when the game closed and detection fell back
			// from PTU to LIVE.
			bytesAtBeat = 0
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
			// deps.sabotage is sabotageNone everywhere except in the selftest
			// controls that have to watch these checks fail. Under
			// sabotageNeverReset the WARNED FLAG still clears but the CLOCK
			// does not - see the constant's comment for why that, and not
			// "skip the whole branch", is the failure worth reproducing.
			if deps.sabotage != sabotageNeverReset {
				lastGrowth = now()
			}
			staleWarned = false
		} else if (!staleWarned || deps.sabotage == sabotageWarnEveryPoll) &&
			now().Sub(lastGrowth) >= staleWindow {
			deps.logf("WARNING: %s has not grown in %s while a game window is open. "+
				"This is usually the wrong install - if the session is on PTU or EPTU, "+
				"start with --gamelog pointing at that Game.log.",
				lastLogPath, staleWindow)
			staleWarned = true
		}

		// The detector has already parsed gamerules out of this poll's lines,
		// because a change to it is itself a trigger. Handing that across is
		// what makes the in-world gate a use of existing data rather than a
		// second detector.
		if tailer != nil && tailer.det != nil {
			runner.setGameRules(tailer.det.st.gameRules)
		}

		// NOTHING IS SERVED FROM THE DETECTOR ANY MORE.
		//
		// §6 of the version-one design: no automatic pictures. Not disabled -
		// removed. `decide()` used to turn a loading screen, a spawn, a
		// terminal opening, a transaction, a state change or a plain timer into
		// a capture; every one of those is gone, and so is the value gate that
		// existed only to filter them.
		//
		// THE DETECTOR STAYS, and that is not a contradiction. It parses
		// gamerules and zone out of these same lines, which is what tells a
		// hotkey capture's sidecar whether the player was in the world - and
		// the miner reads every line for the diary regardless. Feed updates
		// state; nothing acts on what it returns.
		_ = triggers

		// A hold that ended: say how much of the activity was recorded. The
		// keys are still watched, because §7 wants the activity LISTED - they
		// simply no longer take pictures.
		for _, r := range runner.keys.Released() {
			deps.logf("finished recording %s", r)
			ActivityHeldKeyEnd(r, 0)
		}

		// THE ONLY REMAINING SOURCE OF A PICTURE: a key the person pressed.
		// A hotkey burst is that same press continuing - one press, several
		// frames while it is held - so it survives §6 while everything the
		// program decided on its own does not.
		if bt, why := runner.burst.Due(now()); bt != nil {
			out, err := deps.capture(*bt)
			if err != nil {
				deps.logf("capture FAILED (%s): %v", bt.Reason(), err)
				continue
			}
			captures++
			runner.noteCapture(now())
			deps.logf("captured %s  <- %s", filepath.Base(out), bt.Reason())
			ActivityCapture(deps.hotkeyName, filepath.Base(out),
				"still holding - frame "+itoaSmall(bt.Index))
		} else if why != "" {
			deps.logf("burst ended: %s", why)
		}
	}
}

func openAutoLog(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
}

var _ = syscall.Handle(0)
