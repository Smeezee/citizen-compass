package main

// no_auto_capture_selftest.go - prove NOTHING takes a picture on its own.
//
// ===========================================================================
// WHY THIS EXISTS, AND WHY IT IS NOT A UNIT TEST OF decide()
// ===========================================================================
//
// §6 of the version-one design: no automatic pictures. On 2026-08-16 the
// window's interval control was removed on the strength of that - and the
// engine underneath went on firing on loading screens, spawns, shop terminals,
// transactions and a timer for two more days. The UI asserted a property the
// program did not have, which is this project's oldest failure wearing new
// clothes.
//
// Reading the source would not have caught it; somebody did read the source and
// removed the control. So this drives the REAL LOOP with a real log full of the
// exact lines that used to fire, and counts pictures. Zero is the only passing
// answer.
//
// And a check that can only pass is worth nothing, so the same fixture is run
// again with a key press, where it must produce a picture. If the negative
// control ever stops capturing, this file is measuring a broken harness rather
// than a working guarantee.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// everyTriggerThereEverWas is one line of each kind that used to cause a
// capture. Taken from the detector's own patterns rather than invented, so this
// stays honest if the parser changes: if any of these stops being recognised,
// the negative control below is what notices.
const everyTriggerThereEverWas = `<2026-08-18T09:00:00.000Z> Loading screen for Frontend_Main : SC_Frontend closed after 5.0 seconds.
<2026-08-18T09:00:01.000Z> <Corpsify> Player 'Sleven-K' <remote client>: Corpse created.
<2026-08-18T09:00:02.000Z> CImplementationRoom::OnPlayerEnteredRoom: Player entered room 'RR_JP_NyxPyro'
<2026-08-18T09:00:03.000Z> <Notice> [CSessionManager::OnClientSpawned] Spawned!
<2026-08-18T09:00:04.000Z> <ContextEstablisherTaskFinished> establisher="CReplicationModel" message="CEntityComponentInstancedInterior" gamerules="SC_Default"
<2026-08-18T09:00:05.000Z> <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'AEGS_Gladius_1234' [1234] in zone 'Hangar' [pos x: 1.0, y: 2.0]
`

func runNoAutoCaptureSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "no-auto-capture-")
	if err != nil {
		check("§6: could not make a temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	logPath := filepath.Join(tmp, "Game.log")
	if err := os.WriteFile(logPath, []byte("<2026-08-18T08:59:59.000Z> priming\n"), 0o644); err != nil {
		check("§6: could not write the fixture log", false, err.Error())
		return
	}

	run := func(name string, press bool) (int, []string) {
		var mu sync.Mutex
		captures := 0
		var lines []string

		hot := make(chan string, 1)
		stop := make(chan struct{})
		done := make(chan struct{})

		// A CLOCK THAT RUNS FAST, so the loop's own timers cannot be the reason
		// nothing fired. Every interval this program ever had - 60s, 120s, the
		// 10-minute original - is long past by the end of this run.
		start := time.Date(2026, 8, 18, 9, 0, 0, 0, time.UTC)
		var tmu sync.Mutex
		fakeNow := start
		now := func() time.Time {
			tmu.Lock()
			defer tmu.Unlock()
			fakeNow = fakeNow.Add(37 * time.Second)
			return fakeNow
		}

		deps := autoDeps{
			now:        now,
			findLog:    func() (string, string) { return logPath, "fixture" },
			gameAlive:  func() error { return nil },
			hotkeys:    hot,
			hotkeyName: "alt+f3",
			logf: func(f string, a ...interface{}) {
				mu.Lock()
				lines = append(lines, fmt.Sprintf(f, a...))
				mu.Unlock()
			},
			capture: func(t Trigger) (string, error) {
				mu.Lock()
				captures++
				lines = append(lines, "CAPTURED: "+t.Reason())
				mu.Unlock()
				return filepath.Join(tmp, "shot.png"), nil
			},
		}

		go func() {
			// PollSeconds 1, not 0: the loop tickers on it and a zero interval
			// panics. The fake clock above is what makes this fast, not the
			// poll rate.
			_ = runAuto(autoConfig{PollSeconds: 1, DebounceSeconds: 0,
				HotkeyBurst: burstConfig{FrameSeconds: 0}}, logPath, deps, stop)
			close(done)
		}()

		// Everything that used to fire, appended while the loop is running.
		time.Sleep(120 * time.Millisecond)
		f, err := os.OpenFile(logPath, os.O_APPEND|os.O_WRONLY, 0o644)
		if err == nil {
			_, _ = f.WriteString(everyTriggerThereEverWas)
			_ = f.Close()
		}
		if press {
			hot <- "test"
		}
		time.Sleep(400 * time.Millisecond)
		close(stop)
		select {
		case <-done:
		case <-time.After(3 * time.Second):
		}

		mu.Lock()
		defer mu.Unlock()
		out := append([]string{}, lines...)
		return captures, out
	}

	// ---- THE CHECK THAT MATTERS ---------------------------------------
	n, lines := run("quiet", false)
	detail := "captured " + fmt.Sprint(n) + " time(s) with nobody touching a key"
	if n > 0 {
		for _, l := range lines {
			if len(l) > 9 && l[:9] == "CAPTURED:" {
				detail += " | " + l
			}
		}
	}
	check("§6: a log full of loading screens, spawns, terminals, transactions "+
		"and state changes produces NO pictures", n == 0, detail)

	// ---- AND THE CONTROL THAT MAKES IT MEAN SOMETHING -----------------
	m, _ := run("pressed", true)
	check("§6: NEGATIVE CONTROL - the same fixture with a key press DOES capture",
		m > 0,
		"a press produced no picture either, so the check above is measuring a "+
			"broken harness rather than a working guarantee")

	// ---- AND THE FEATURE IS GONE, NOT DISABLED ------------------------
	//
	// A settings file is the way a removed-but-present feature comes back. The
	// template must not offer one, and the reader must not know these keys.
	// A SETTING IS AN ASSIGNMENT, NOT A MENTION.
	//
	// The first version of this searched for the key names anywhere in the
	// template and failed on the comment that EXPLAINS the keys are gone. A
	// check that forbids documenting a removal is a check pushing in the wrong
	// direction, so it now looks for a line that actually sets one.
	defines := func(tmpl, key string) bool {
		for _, line := range strings.Split(tmpl, "\n") {
			t := strings.TrimSpace(line)
			if strings.HasPrefix(t, "#") {
				continue
			}
			if strings.HasPrefix(t, key) {
				rest := strings.TrimSpace(strings.TrimPrefix(t, key))
				if strings.HasPrefix(rest, "=") {
					return true
				}
			}
		}
		return false
	}

	tmpl := settingsTemplate
	for _, dead := range []string{"interval_seconds", "capture_low_value",
		"burst_seconds", "burst_max_frames"} {
		check("§6: the settings template does not SET "+dead,
			!defines(tmpl, dead),
			"a settings file could switch automatic capture back on")
	}
	check("§6: NEGATIVE CONTROL - the template still sets the hotkey burst",
		defines(tmpl, "hotkey_burst_seconds"),
		"the check above would pass on an empty template, which proves nothing")
}
