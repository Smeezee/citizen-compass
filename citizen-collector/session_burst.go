package main

// session_burst.go - keep shooting while a shop terminal is open.
//
// # WHAT SLEVEN ASKED FOR, IN HIS WORDS
//
//	"If I open up a shop terminal, it needs to know everything that
//	 and it captured everything in it as I scroll. I'll even scroll
//	 slowly."
//
// # WHY ONE FRAME PER EVENT WAS NEVER GOING TO DO THAT
//
// The terminal_open trigger added earlier today fires once, when the log says a
// shop or inventory screen was opened. That gets the first screenful. A shop
// list is longer than a screen, so everything below the fold - which is most of
// the stock, most of the prices, most of the point - was never in any frame.
//
// A timer does not fix it either. At a 60-second interval a person scrolling a
// list for forty seconds gets zero or one frame, at a moment chosen by the
// clock rather than by them.
//
// So: while a terminal is open, capture on a SHORT rhythm, and stop when it
// closes. Nothing else in the session changes.
//
// # WHAT ENDS A BURST, AND WHY IT IS NOT JUST A TIMER
//
// Three ways out, because a burst that only ends on a timeout is a burst that
// fills a disk when the log stops mentioning the terminal:
//
//  1. a new HIGH-value trigger that is not part of this terminal - the player
//     moved on
//  2. maxFrames - a hard ceiling, so a stuck burst is bounded by arithmetic
//     rather than by hope
//  3. idleTimeout - no burst frame taken for this long, the screen is done
//
// The ceiling is the load-bearing one. Every other stop condition depends on
// something else behaving; that one cannot fail to fire.
//
// # THE PART THAT COSTS DISK, STATED HONESTLY
//
// A 20-frame burst at ~2.5 MB is ~50 MB per shop visit. That is a lot, and it
// is the correct trade only because the alternative is one frame of a list
// whose useful half is off-screen. The ceiling and the interval are both
// settings, so this is tunable without a rebuild.

import (
	"fmt"
	"time"
)

// burstConfig is the shape of the rhythm. Zero FrameSeconds disables bursting
// entirely, which is a supported state rather than a broken one.
type burstConfig struct {
	FrameSeconds int // how often to shoot while a terminal is open
	MaxFrames    int // hard ceiling per burst
	IdleSeconds  int // give up if no frame taken in this long
}

func defaultBurstConfig() burstConfig {
	// Two seconds is chosen against the thing being photographed, not picked
	// round: the log poll is already 2s, so a faster burst would shoot frames
	// the detector cannot yet explain. Twenty-four frames covers roughly fifty
	// seconds of scrolling, which is a long look at one kiosk.
	return burstConfig{FrameSeconds: 2, MaxFrames: 24, IdleSeconds: 20}
}

// defaultHotkeyBurstConfig is the rhythm ONE deliberate press produces.
//
// Six seconds at one frame per second, which is the order's starting point and
// Sleven's own description: "I can scroll for a few seconds and try to capture
// multiple things."
//
// BOTH NUMBERS ARE SETTINGS, and that is the important part. The right values
// depend on how fast he actually scrolls a commodity board, which nobody knows
// yet - so these are a starting point to be measured against, not a judgement.
// hotkey_burst_seconds = 0 turns bursting off entirely and restores one press,
// one frame.
//
// Faster than the terminal burst deliberately: a terminal is followed patiently
// for as long as it is open, while a press means "this screen, right now".
// 1 frame/second is also the fastest rate a person can meaningfully scroll to.
func defaultHotkeyBurstConfig() burstConfig {
	return burstConfig{FrameSeconds: 1, MaxFrames: 6, IdleSeconds: 10}
}

// burstState tracks ONE burst - whichever kind is running.
//
// THERE IS DELIBERATELY ONE OF THESE. A hotkey burst and a terminal burst use
// the same state, so "never two overlapping bursts" is a property of the type
// rather than a rule somebody has to keep in mind. Two instances would have
// been a second burst implementation wearing the first one's name, which is
// exactly what the order forbade.
//
// `cfg` is now per-burst, because the two kinds want different rhythms: a
// terminal is followed patiently for as long as it is open, while a hotkey
// press is a person saying "now, and for a few seconds".
type burstState struct {
	cfg     burstConfig // the rhythm of the burst currently running
	termCfg burstConfig // the rhythm terminals get

	active   bool
	kind     string // "terminal" or "hotkey" - recorded on every frame
	what     string // the terminal that opened, or the key that was pressed
	started  time.Time
	lastShot time.Time
	frames   int
	press    int // which press this burst belongs to (hotkey bursts only)
	extended int // how many further presses landed inside it
	stopWhy  string
}

func newBurstState(cfg burstConfig) *burstState {
	return &burstState{cfg: cfg, termCfg: cfg}
}

// Begin starts a burst for a named terminal.
//
// Re-opening the SAME terminal while a burst is running is treated as the
// player still being there - it extends rather than restarts, so the frame
// ceiling still bounds the whole visit. Without that, a log that mentions the
// terminal every few seconds would reset the counter forever and the ceiling
// would never be reached.
func (b *burstState) Begin(what string, now time.Time) {
	if b.termCfg.FrameSeconds <= 0 {
		return
	}
	// A DELIBERATE PRESS OUTRANKS THE LOG. If the person is holding the key
	// down on a screen they chose, the terminal that happens to be open does
	// not get to relabel their frames halfway through. The terminal burst can
	// start the moment theirs finishes.
	if b.active && b.kind == "hotkey" {
		return
	}
	if b.active && b.what == what {
		return
	}
	b.cfg = b.termCfg
	b.active = true
	b.kind = "terminal"
	b.what = what
	b.started = now
	b.lastShot = now // the trigger itself already took the opening frame
	b.frames = 0
	b.press = 0
	b.extended = 0
	b.stopWhy = ""
}

// BeginHotkey starts - or EXTENDS - the burst a person asked for by pressing
// the key.
//
// A SECOND PRESS EXTENDS, it does not start anything. That is the choice the
// order left open, and it is the one that matches what the key is for: thirty
// presses were recorded in one session, nine of them inside twelve seconds,
// which is somebody saying "keep going" rather than "start again". Extending
// pushes the ceiling out and resets the idle clock, so the frames stay one
// coherent record with one press number on them.
//
// Returns the log line, so the loop states which of the two happened rather
// than leaving a person to infer it from the frame count.
func (b *burstState) BeginHotkey(what string, now time.Time, cfg burstConfig, press int) (string, *Trigger) {
	if cfg.FrameSeconds <= 0 {
		return "", nil // single-frame mode - the caller takes one picture instead
	}
	if b.active && b.kind == "hotkey" {
		b.extended++
		b.cfg.MaxFrames += cfg.MaxFrames
		b.lastShot = now
		return fmt.Sprintf("burst extended by press #%d - now up to %d frames",
			press, b.cfg.MaxFrames), nil
	}
	prev := ""
	if b.active {
		prev = fmt.Sprintf(" (took over from the %s burst on %q)", b.kind, b.what)
	}
	b.cfg = cfg
	b.active = true
	b.kind = "hotkey"
	b.what = what
	b.started = now
	b.lastShot = now
	b.frames = 0
	b.press = press
	b.extended = 0
	b.stopWhy = ""

	// FRAME 1 BELONGS TO THE PRESS, and the caller takes it straight away.
	//
	// Not a nicety: the rest of the burst is served from decide(), which runs
	// below the loop's window gate, while the press is handled above it. If the
	// press produced no frame of its own, pressing the key with the game
	// minimised would capture nothing while the log announced a burst.
	//
	// It is numbered as frame 1 of this burst rather than dressed as a separate
	// one-off, so the sidecars still reassemble into one record.
	b.frames = 1
	first := b.frame()
	return fmt.Sprintf("burst started by press #%d: up to %d frames, one every %ds%s",
		press, cfg.MaxFrames, cfg.FrameSeconds, prev), first
}

// frame builds the Trigger for the frame just counted. One formatter, so a
// press-taken frame and a Due-taken frame cannot describe themselves
// differently.
func (b *burstState) frame() *Trigger {
	if b.kind == "hotkey" {
		note := fmt.Sprintf("frame %d of at most %d from press #%d",
			b.frames, b.cfg.MaxFrames, b.press)
		if b.extended > 0 {
			note += fmt.Sprintf(" (extended by %d further press(es))", b.extended)
		}
		return &Trigger{
			Kind: "burst", Field: "hotkey_burst", To: b.what,
			Seconds: b.cfg.FrameSeconds, Value: valueHigh,
			Press: b.press, Index: b.frames, Note: note,
		}
	}
	return &Trigger{
		Kind: "burst", Field: "terminal_scroll", To: b.what,
		Seconds: b.cfg.FrameSeconds, Value: valueHigh,
		Index: b.frames,
		Note: fmt.Sprintf("frame %d of at most %d while %q is open",
			b.frames, b.cfg.MaxFrames, b.what),
	}
}

// Interrupt ends a burst because the player did something else.
func (b *burstState) Interrupt(why string) {
	if !b.active {
		return
	}
	b.active = false
	b.stopWhy = why
}

// Due reports whether a burst frame should be taken now, and stops the burst
// when a ceiling or the idle timeout is reached.
//
// Returning (nil, "") is the common case and costs nothing. The stop reason is
// returned rather than logged in here so this stays testable without a logger.
func (b *burstState) Due(now time.Time) (*Trigger, string) {
	if !b.active {
		return nil, ""
	}

	// CEILING FIRST. Checked before the clock so a burst cannot take one more
	// frame than it is allowed to, no matter how the timing falls.
	if b.frames >= b.cfg.MaxFrames {
		b.active = false
		return nil, fmt.Sprintf("reached the %d-frame ceiling for %q", b.cfg.MaxFrames, b.what)
	}
	if now.Sub(b.lastShot) >= time.Duration(b.cfg.IdleSeconds)*time.Second {
		b.active = false
		return nil, fmt.Sprintf("no frames for %ds - %q looks closed", b.cfg.IdleSeconds, b.what)
	}
	if now.Sub(b.lastShot) < time.Duration(b.cfg.FrameSeconds)*time.Second {
		return nil, ""
	}

	b.lastShot = now
	b.frames++

	// EVERY FRAME SAYS WHICH BURST IT IS AND WHERE IT SITS IN IT. A burst that
	// cannot be reassembled afterwards is noise with a timestamp - so the press
	// number and the index travel in the sidecar, not just in the log.
	return b.frame(), ""
}

// ActiveKind reports which sort of burst is running, or "" for none.
func (b *burstState) ActiveKind() string {
	if !b.active {
		return ""
	}
	return b.kind
}

// Active reports whether a terminal is currently being followed. Used by the
// interval fallback, which must stand down during a burst - two mechanisms
// shooting at once would double the frames and make the record ambiguous about
// which one was responsible.
func (b *burstState) Active() bool { return b.active }
