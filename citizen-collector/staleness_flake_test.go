package main

// staleness_flake_test.go - MEASUREMENT, not a fix.
//
// Section 1 of docs/ORDER_collector-staleness-selftest-flake-2026-08-20.md:
// "FIRST, MEASURE IT. Do not fix anything yet." The rate is how the fix gets
// proven afterwards, and there is no second chance to collect a before number.
//
// This runs runAutoHeartbeatSelftest - the REAL fixture, not a copy of it -
// many times over and records which named checks failed on each run. It exists
// so that "intermittent" becomes a number instead of an impression.
//
// It is a _test.go file, so it is not in the shipped binary. Nothing here is
// built into collector.exe and nothing is installed.
//
//	go test -run TestStalenessFlakeRate -v -timeout 40m \
//	    -count=1 ./... 2>&1
//
// CC_FLAKE_RUNS   how many iterations (default 40, the order asks for 200)
// CC_FLAKE_LOAD   set to spin busy goroutines alongside, to reproduce the
//                 loaded case the flake was first seen under
// CC_FLAKE_HANG   per-run watchdog in seconds (default 60). A run that exceeds
//                 it is recorded as a HANG rather than waited on forever -
//                 section 5 says the hang outranks everything else if it
//                 recurs, so it has to be counted, not endured.

import (
	"fmt"
	"os"
	"runtime"
	"sort"
	"strconv"
	"sync/atomic"
	"testing"
	"time"
)

func envInt(name string, def int) int {
	if v := os.Getenv(name); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return def
}

// loadGenerator spins CPU on every core, which is what was running when the
// flake first appeared (a 235-model geometry decode). Returns a stop func.
func loadGenerator() func() {
	stop := make(chan struct{})
	for i := 0; i < runtime.NumCPU(); i++ {
		go func() {
			x := 0
			for {
				select {
				case <-stop:
					return
				default:
					for j := 0; j < 1e6; j++ {
						x += j % 7
					}
					_ = x
				}
			}
		}()
	}
	return func() { close(stop) }
}

// runOnce runs the real fixture under a watchdog and returns the names of the
// checks that failed, plus whether the run hung.
func runOnce(watchdog time.Duration) (failed []string, hung bool) {
	type result struct{ failed []string }
	done := make(chan result, 1)

	go func() {
		var f []string
		defer func() {
			if r := recover(); r != nil {
				f = append(f, fmt.Sprintf("PANIC: %v", r))
			}
			done <- result{failed: f}
		}()
		// CC_FLAKE_MODE=selftest runs the whole entry point including its
		// controls, which is what the BEFORE measurement ran. The default
		// measures the fixture on its own, so the before and after numbers are
		// about the same thing rather than about how long the controls take.
		if os.Getenv("CC_FLAKE_MODE") == "selftest" {
			runAutoHeartbeatSelftest(func(name string, ok bool, detail string) {
				if !ok {
					f = append(f, name)
				}
			})
			return
		}
		run := runHeartbeatFixture(sabotageNone, 0)
		for _, name := range run.order {
			if !run.results[name] {
				f = append(f, name)
			}
		}
	}()

	select {
	case r := <-done:
		return r.failed, false
	case <-time.After(watchdog):
		// Deliberately NOT waited on. A hung run is the observation.
		return []string{"HANG"}, true
	}
}

func TestStalenessFlakeRate(t *testing.T) {
	runs := envInt("CC_FLAKE_RUNS", 40)
	watchdog := time.Duration(envInt("CC_FLAKE_HANG", 60)) * time.Second
	loaded := os.Getenv("CC_FLAKE_LOAD") != ""

	var stopLoad func()
	if loaded {
		stopLoad = loadGenerator()
		defer stopLoad()
		t.Logf("LOAD GENERATOR RUNNING on %d cores", runtime.NumCPU())
	}

	counts := map[string]int{}
	cooccur := map[string]int{}
	hangs := 0
	clean := 0
	started := time.Now()

	for i := 0; i < runs; i++ {
		failed, hung := runOnce(watchdog)
		if hung {
			hangs++
		}
		if len(failed) == 0 {
			clean++
		} else {
			sort.Strings(failed)
			key := fmt.Sprintf("%v", failed)
			cooccur[key]++
			for _, name := range failed {
				counts[name]++
			}
			t.Logf("run %3d/%d FAILED: %v", i+1, runs, failed)
		}
	}

	elapsed := time.Since(started)
	t.Logf("")
	t.Logf("=== %d runs, %s, load=%v ===", runs, elapsed.Round(time.Second), loaded)
	t.Logf("clean runs : %d/%d (%.1f%%)", clean, runs, 100*float64(clean)/float64(runs))
	t.Logf("hangs      : %d", hangs)
	if len(counts) == 0 {
		t.Logf("no check failed in any run")
		return
	}
	t.Logf("per-check failure counts:")
	names := make([]string, 0, len(counts))
	for n := range counts {
		names = append(names, n)
	}
	sort.Strings(names)
	for _, n := range names {
		t.Logf("  %-58s %d  (%.1f%%)", n, counts[n],
			100*float64(counts[n])/float64(runs))
	}
	t.Logf("failure SETS - this is what says whether the four fail together:")
	sets := make([]string, 0, len(cooccur))
	for k := range cooccur {
		sets = append(sets, k)
	}
	sort.Strings(sets)
	for _, k := range sets {
		t.Logf("  x%-4d %s", cooccur[k], k)
	}
}

// TestStalenessSelftestGoroutineLeak looks for the section 5 hang from the
// other end: if each fixture run leaves its loop goroutine behind, back-to-back
// runs would pile them up and eventually contend. Recorded rather than
// asserted on a threshold nobody has justified.
func TestStalenessSelftestGoroutineLeak(t *testing.T) {
	runtime.GC()
	before := runtime.NumGoroutine()
	var ran int32
	for i := 0; i < 10; i++ {
		runAutoHeartbeatSelftest(func(name string, ok bool, detail string) {
			atomic.AddInt32(&ran, 1)
		})
	}
	time.Sleep(200 * time.Millisecond)
	runtime.GC()
	after := runtime.NumGoroutine()
	t.Logf("goroutines before %d, after 10 fixture runs %d (delta %+d), "+
		"%d checks executed", before, after, after-before, ran)
	if after-before > 10 {
		t.Errorf("the fixture leaks goroutines: %d left behind after 10 runs. "+
			"That is a candidate for the ten-minute hang in section 5.",
			after-before)
	}
}
