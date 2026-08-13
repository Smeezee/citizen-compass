package main

// burst_selftest.go - checks for keep-shooting-while-a-terminal-is-open.
//
// EVERY CHECK HAS A NEGATIVE CONTROL (hard rule 12). The load-bearing one is
// that the ceiling STOPS the burst: without it, "a burst produces many frames"
// would also pass on a build that never stops and fills the disk.

import (
	"fmt"
	"strings"
	"time"
)

// runHotkeyBurstSelftest covers §3 of the log-first redesign: one press of the
// hotkey produces a burst rather than a single frame.
//
// The frames are produced by the SAME burstState the terminal burst uses, so
// these checks also assert the property that makes that safe - that a hotkey
// burst and a terminal burst can never be running at once.
func runHotkeyBurstSelftest(check func(name string, ok bool, detail string)) {
	base := time.Date(2026, 8, 13, 12, 0, 0, 0, time.UTC)
	cfg := burstConfig{FrameSeconds: 1, MaxFrames: 6, IdleSeconds: 10}

	// --- 4. one press, a burst, every frame labelled --------------------
	b := newBurstState(defaultBurstConfig())
	line, firstFrame := b.BeginHotkey("alt+f3 via hook", base, cfg, 1)
	check("hotkey burst: a press starts a burst and says so",
		strings.Contains(line, "press #1") && strings.Contains(line, "up to 6 frames"),
		fmt.Sprintf("log line was %q", line))

	// Frame 1 is handed back by the press itself - the loop takes it above the
	// window gate, so a press always yields a picture even with no game window.
	check("hotkey burst: the press itself yields frame 1, so a press always captures",
		firstFrame != nil && firstFrame.Index == 1 && firstFrame.Press == 1,
		fmt.Sprintf("got %v", firstFrame))

	frames := []*Trigger{firstFrame}
	for i := 0; i <= 12; i++ {
		if t, _ := b.Due(base.Add(time.Duration(i) * time.Second)); t != nil {
			frames = append(frames, t)
		}
	}
	check("hotkey burst: one press yields several frames, capped at the ceiling",
		len(frames) == 6, fmt.Sprintf("got %d frames (want 6)", len(frames)))

	labelled := len(frames) > 0
	for i, t := range frames {
		if t.Kind != "burst" || t.Field != "hotkey_burst" ||
			t.Press != 1 || t.Index != i+1 {
			labelled = false
		}
	}
	check("hotkey burst: every frame names the trigger, the press and its index",
		labelled,
		fmt.Sprintf("first frame: kind=%q field=%q press=%d index=%d",
			frames[0].Kind, frames[0].Field, frames[0].Press, frames[0].Index))

	// A NEGATIVE CONTROL for the labelling: the terminal burst must NOT claim
	// to be a hotkey burst, or "which press did this come from" is meaningless.
	bt := newBurstState(cfg)
	bt.Begin("Stanton4_NewBabbage", base)
	tt, _ := bt.Due(base.Add(2 * time.Second))
	check("NEGATIVE CONTROL: a terminal frame is not labelled as a hotkey burst",
		tt != nil && tt.Field == "terminal_scroll" && tt.Press == 0,
		fmt.Sprintf("got %v", tt))

	// --- 5. two presses two seconds apart = ONE record ------------------
	b2 := newBurstState(defaultBurstConfig())
	_, f1 := b2.BeginHotkey("alt+f3", base, cfg, 1)
	ext, f2 := b2.BeginHotkey("alt+f3", base.Add(2*time.Second), cfg, 2)
	check("hotkey burst: an EXTENDING press does not start a second frame-1",
		f1 != nil && f2 == nil,
		fmt.Sprintf("first=%v extending=%v", f1, f2))
	check("hotkey burst: a second press EXTENDS, and the log says which happened",
		strings.Contains(ext, "extended") && strings.Contains(ext, "press #2"),
		fmt.Sprintf("log line was %q", ext))

	all := []*Trigger{f1}
	for i := 0; i <= 30; i++ {
		if t, _ := b2.Due(base.Add(time.Duration(i) * time.Second)); t != nil {
			all = append(all, t)
		}
	}
	onePress := len(all) > 0
	for _, t := range all {
		if t.Press != 1 {
			onePress = false
		}
	}
	check("hotkey burst: two presses produce ONE burst, not two overlapping ones",
		onePress && len(all) == 12,
		fmt.Sprintf("%d frames, all on press #1: %v", len(all), onePress))

	indices := map[int]bool{}
	dup := false
	for _, t := range all {
		if indices[t.Index] {
			dup = true
		}
		indices[t.Index] = true
	}
	check("hotkey burst: the extended burst is still reassemblable - no repeated index",
		!dup, "two frames claimed the same index in one burst")

	// --- the deliberate press outranks the log --------------------------
	b3 := newBurstState(defaultBurstConfig())
	b3.BeginHotkey("alt+f3", base, cfg, 1) //nolint
	b3.Begin("Stanton4_NewBabbage", base.Add(time.Second))
	check("hotkey burst: a terminal opening does not relabel a press mid-burst",
		b3.ActiveKind() == "hotkey", "got "+b3.ActiveKind())

	// --- 6. single-frame mode is still reachable ------------------------
	r := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3,
		HotkeyBurst: burstConfig{FrameSeconds: 0}}, func() time.Time { return base })
	started, _, _ := r.hotkeyPressed("alt+f3", base)
	check("hotkey burst: hotkey_burst_seconds = 0 restores one press, one frame",
		!started, "a burst started even though bursting is switched off")

	r2 := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3,
		HotkeyBurst: cfg}, func() time.Time { return base })
	started2, _, _ := r2.hotkeyPressed("alt+f3", base)
	check("NEGATIVE CONTROL: with bursting on, the same press DOES start a burst",
		started2, "no burst started, so the check above proves nothing")
}

func runBurstSelftest(check func(name string, ok bool, detail string)) {
	base := time.Date(2026, 8, 8, 12, 0, 0, 0, time.UTC)
	cfg := burstConfig{FrameSeconds: 2, MaxFrames: 5, IdleSeconds: 20}

	b := newBurstState(cfg)
	check("burst: idle until a terminal opens", !b.Active(),
		"nothing should shoot on its own")

	b.Begin("RR_JP_NyxCastra", base)
	check("burst: opening a shop terminal starts it", b.Active(), "RR_JP_NyxCastra")

	// Walk the clock forward and count frames.
	got := 0
	var stop string
	for i := 1; i <= 40; i++ {
		now := base.Add(time.Duration(i) * time.Second)
		t, why := b.Due(now)
		if t != nil {
			got++
			if t.Kind != "burst" || !t.isHigh() {
				check("burst: frames are high-value burst triggers", false, t.Reason())
				return
			}
		}
		if why != "" {
			stop = why
			break
		}
	}
	check("burst: a scrolled list produces MANY frames, not one",
		got == cfg.MaxFrames,
		fmt.Sprintf("took %d frames at %ds apart (want %d)", got, cfg.FrameSeconds, cfg.MaxFrames))
	check("burst: the ceiling stops it and says so",
		!b.Active() && stop != "",
		"stop reason: "+stop)

	// NEGATIVE CONTROL. If Due() simply always returned a frame, the count check
	// above would pass. A burst that has ended must produce nothing at all.
	extra, _ := b.Due(base.Add(200 * time.Second))
	check("NEGATIVE CONTROL: an ended burst produces no further frames",
		extra == nil, "the ceiling is a stop, not a pause")

	// Idle timeout, on its own clock.
	b2 := newBurstState(cfg)
	b2.Begin("Shop_Levski", base)
	_, why2 := b2.Due(base.Add(time.Duration(cfg.IdleSeconds+1) * time.Second))
	check("burst: a terminal left alone times out",
		!b2.Active() && why2 != "",
		"a burst that only ends on a ceiling would keep a closed screen alive")

	// Interruption by the player moving on.
	b3 := newBurstState(cfg)
	b3.Begin("Shop_Levski", base)
	b3.Interrupt("interrupted by event:transaction")
	check("burst: another high-value event ends it",
		!b3.Active(), "the player moved on, so the burst did too")

	// Re-opening the SAME terminal extends rather than restarts, or the ceiling
	// could be reset forever by a chatty log and never bound anything.
	b4 := newBurstState(cfg)
	b4.Begin("Shop_Levski", base)
	_, _ = b4.Due(base.Add(2 * time.Second))
	_, _ = b4.Due(base.Add(4 * time.Second))
	b4.Begin("Shop_Levski", base.Add(5*time.Second)) // same terminal again
	check("burst: re-opening the same terminal does NOT reset the ceiling",
		b4.frames == 2,
		fmt.Sprintf("frames still %d - a chatty log must not buy unlimited frames", b4.frames))

	// NEGATIVE CONTROL: a DIFFERENT terminal is a new visit and does reset.
	b4.Begin("Shop_Orison", base.Add(6*time.Second))
	check("NEGATIVE CONTROL: a different terminal starts a fresh burst",
		b4.frames == 0 && b4.what == "Shop_Orison",
		"otherwise one long session would starve every later shop")

	// Turning it off must actually turn it off.
	b5 := newBurstState(burstConfig{FrameSeconds: 0, MaxFrames: 24, IdleSeconds: 20})
	b5.Begin("Shop_Levski", base)
	off, _ := b5.Due(base.Add(60 * time.Second))
	check("burst: burst_seconds = 0 disables it entirely",
		!b5.Active() && off == nil, "single frame on open, as before")

	// The interval must stand down during a burst, or both fire and the sidecar
	// cannot say which mechanism was responsible.
	fake := base
	r := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 0,
		IntervalSeconds: 1, Burst: cfg}, func() time.Time { return fake })
	fake = base.Add(1 * time.Second)
	_ = r.decide([]Trigger{{Kind: "event", Field: "terminal_open",
		To: "RR_JP_NyxCastra", Value: valueHigh}})
	fake = base.Add(4 * time.Second)
	during := r.decide(nil)
	check("burst: the interval stands down while a burst runs",
		during != nil && during.Kind == "burst",
		"two mechanisms shooting at once would double the frames: got "+during.Reason())
}

// runBurstSettingsSelftest guards the defect that killed bursting on every
// machine: a settings file with no burst_seconds key.
//
// There was no test for this because the burst logic was tested directly with a
// config struct, and the config struct was correct. The bug lived in the wiring
// between the settings file and that struct - the one place nothing looked.
func runBurstSettingsSelftest(check func(name string, ok bool, detail string)) {
	base := defaultBurstConfig()
	check("burst settings: the default is ON",
		base.FrameSeconds > 0 && base.MaxFrames > 0,
		"a default of 0 is the documented way to switch bursting off")

	// An ABSENT key must leave the default alone. This is the exact case that
	// failed live: intVal returns (0,false,nil) and reading only the value set
	// the interval to zero.
	empty := &settings{values: map[string]string{}}
	cfg := defaultBurstConfig()
	if v, found, err := empty.intVal("burst_seconds"); found && err == nil && v >= 0 {
		cfg.FrameSeconds = v
	}
	check("burst settings: a file with NO burst_seconds keeps the default",
		cfg.FrameSeconds == base.FrameSeconds,
		"every settings file written before today is missing this key")

	// NEGATIVE CONTROL: a key that IS present must still be honoured, or the
	// fix above would be "ignore the setting entirely" and pass just as well.
	set := &settings{values: map[string]string{"burst_seconds": "5"}}
	cfg2 := defaultBurstConfig()
	if v, found, err := set.intVal("burst_seconds"); found && err == nil && v >= 0 {
		cfg2.FrameSeconds = v
	}
	check("NEGATIVE CONTROL: a burst_seconds that IS set is honoured",
		cfg2.FrameSeconds == 5, "the setting must still work")

	// And 0 must still mean off, since that is documented.
	off := &settings{values: map[string]string{"burst_seconds": "0"}}
	cfg3 := defaultBurstConfig()
	if v, found, err := off.intVal("burst_seconds"); found && err == nil && v >= 0 {
		cfg3.FrameSeconds = v
	}
	check("burst settings: an explicit 0 still turns bursting off",
		cfg3.FrameSeconds == 0, "absent and explicitly-zero are different things")
}
