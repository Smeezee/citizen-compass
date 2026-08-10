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

// burstState tracks one open terminal.
type burstState struct {
	cfg burstConfig

	active   bool
	what     string // the terminal that opened, for the log and the sidecar
	started  time.Time
	lastShot time.Time
	frames   int
	stopWhy  string
}

func newBurstState(cfg burstConfig) *burstState { return &burstState{cfg: cfg} }

// Begin starts a burst for a named terminal.
//
// Re-opening the SAME terminal while a burst is running is treated as the
// player still being there - it extends rather than restarts, so the frame
// ceiling still bounds the whole visit. Without that, a log that mentions the
// terminal every few seconds would reset the counter forever and the ceiling
// would never be reached.
func (b *burstState) Begin(what string, now time.Time) {
	if b.cfg.FrameSeconds <= 0 {
		return
	}
	if b.active && b.what == what {
		return
	}
	b.active = true
	b.what = what
	b.started = now
	b.lastShot = now // the trigger itself already took the opening frame
	b.frames = 0
	b.stopWhy = ""
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
	return &Trigger{
		Kind: "burst", Field: "terminal_scroll", To: b.what,
		Seconds: b.cfg.FrameSeconds, Value: valueHigh,
		Note: fmt.Sprintf("frame %d of at most %d while %q is open",
			b.frames, b.cfg.MaxFrames, b.what),
	}, ""
}

// Active reports whether a terminal is currently being followed. Used by the
// interval fallback, which must stand down during a burst - two mechanisms
// shooting at once would double the frames and make the record ambiguous about
// which one was responsible.
func (b *burstState) Active() bool { return b.active }
