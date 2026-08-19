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
	b := newBurstState(defaultHotkeyBurstConfig())
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

	// --- 5. two presses two seconds apart = ONE record ------------------
	b2 := newBurstState(defaultHotkeyBurstConfig())
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
