package main

// roadmap-watcher - re-checks CIG's public roadmap so "nothing yet" expires by
// itself instead of by somebody remembering to ask.
//
// Sleven: "is there any way that we could keep track of this stuff and hold this
// data and see if we can find truth to it?"
//
// CIC established three independent ways that CIG has said nothing publicly
// about a Constellation rework. That answer is correct and it EXPIRES. The
// signal wanted is a Constellation card appearing on the roadmap.
//
// # THE MANUAL CHECK RUNS THE SAME CODE PATH AS THE TIMER
//
// Not a separate script, not a debug mode, not a different query - the order is
// explicit and the reason is good: if a hand-run and a scheduled run can
// disagree, the hand-run is useless for checking on the scheduled one, which is
// most of what it is for. `-check` and the timer both call runOnce(). The only
// difference is a string in the stored record saying which triggered it.
//
//	roadmap-watcher            run on the configured cadence
//	roadmap-watcher -check     check now, once, and exit
//	roadmap-watcher -status    print what is known, poll nothing

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"time"

	"citizencompass/pkg/pipelinelog"
)

const stateFileName = "roadmap-watcher-state.json"

func main() {
	check := flag.Bool("check", false, "check now, once, then exit")
	status := flag.Bool("status", false, "print what is known and exit; polls nothing")
	flag.Parse()

	exeDir := "."
	if p, err := os.Executable(); err == nil {
		exeDir = filepath.Dir(p)
	}
	root := findProjectRoot(exeDir)
	log := pipelinelog.New(root, "roadmap-watcher")

	cfg, cfgFrom, err := LoadConfig(exeDir)
	if err != nil {
		log.Logf("REFUSING TO START: %v", err)
		os.Exit(1)
	}
	if err := cfg.Validate(); err != nil {
		log.Logf("REFUSING TO START: %v", err)
		os.Exit(1)
	}
	statePath := filepath.Join(exeDir, stateFileName)

	if *status {
		printStatus(statePath, cfg, cfgFrom)
		return
	}

	log.Logf("roadmap-watcher starting | settings from %s | every %.1fh | boards %v | watching %q",
		cfgFrom, cfg.IntervalHours, cfg.Boards, cfg.Watch)
	if !cfg.Stage2Enabled {
		log.Logf("stage 2 (GraphQL progress tracker) is BUILT but not scheduled - " +
			"set stage2_enabled true to turn it on")
	}

	if *check {
		runOnce(log, cfg, statePath, "manual")
		return
	}

	// Once immediately, so starting the watcher tells you something rather than
	// leaving you wondering for four hours whether it works.
	runOnce(log, cfg, statePath, "scheduled")
	t := time.NewTicker(cfg.Interval())
	defer t.Stop()
	for range t.C {
		runOnce(log, cfg, statePath, "scheduled")
	}
}

// runOnce is THE code path. Both the timer and -check call exactly this.
func runOnce(log *pipelinelog.Logger, cfg Config, statePath, trigger string) {
	st, first, err := LoadState(statePath)
	if err != nil {
		log.Logf("STOPPING THIS PASS: %v", err)
		return
	}

	client := &http.Client{Timeout: 60 * time.Second}
	var all []Change
	polled := 0

	for _, board := range cfg.Boards {
		key := fmt.Sprintf("b%d", board)
		res := FetchBoard(client, cfg, board)
		if res.Err != nil {
			// A failed poll is reported and the loop continues. The next pass is
			// four hours away and a network blip must not stop the watcher.
			log.Logf("board %d: poll FAILED (%v) - will try again next pass", board, res.Err)
			continue
		}
		polled++

		st.BoardLastUpdated[key] = res.LastUpdated

		matches := Matches(res.Cards, cfg.Watch)

		// APPENDED BEFORE THE DIFF, ON PURPOSE.
		//
		// Diff MUTATES the stored fingerprints - that is how it works, and it
		// is why main saves before it reports. If the history were written
		// afterwards it would be recording the state the diff had already
		// moved to, and the run that changed a card would be the one run whose
		// "before" was never kept. Writing first means the log holds what was
		// actually observed on the wire, every run, whatever the diff then does
		// with it.
		if n, err := AppendObservations(HistoryPath(filepath.Dir(statePath)), res, cfg.Watch,
			trigger, log.Logf); err != nil {
			// NOT FATAL, AND NOT SILENT. A history that stops recording is
			// exactly the defect this closes, so it is said out loud every run
			// it fails rather than discovered empty in a year.
			log.Logf("HISTORY NOT WRITTEN for board %d: %v", board, err)
		} else if n > 0 {
			log.Logf("history: %d observation(s) appended for board %d", n, board)
		}

		changes := Diff(st, res, cfg.Watch)
		all = append(all, changes...)

		log.Logf("board %d (%s): %d cards, %d matching %q, %d KB decoded",
			board, res.Surface, len(res.Cards), len(matches), cfg.Watch,
			res.Bytes/1024)
	}

	now := time.Now().UTC()

	if polled == 0 {
		// STATE 3. A pass that polled nothing is NOT a clean negative, and
		// LastGood is deliberately NOT advanced: a run that did not look has
		// not looked.
		st.LastRun = now.Format(time.RFC3339)
		st.LastRunBy = trigger
		_ = SaveState(statePath, st)
		log.Logf("STALE / FAILING - every board failed this pass, so nothing was "+
			"checked. This is not 'no Constellation activity', it is 'we did not "+
			"look'. %s trigger=%s", sinceGood(st, now), trigger)
		return
	}

	st.LastRun = now.Format(time.RFC3339)
	st.LastRunBy = trigger
	st.LastGood = now.Format(time.RFC3339)
	if trigger == "scheduled" {
		st.LastGoodScheduled = now.Format(time.RFC3339)
	}
	if err := SaveState(statePath, st); err != nil {
		log.Logf("WARNING: could not save state (%v) - the next pass will re-report "+
			"whatever this one found", err)
	}

	if first {
		// A BASELINE IS NOT NEWS. On the first run every card is "new"; calling
		// three years-old cards a discovery would be a lie of framing, and it is
		// how an alert channel gets muted before it ever matters.
		log.Logf("BASELINE TAKEN: %d watched card(s) recorded as the starting point. "+
			"Nothing here is new - it is what is on the board today. trigger=%s",
			len(st.Baseline), trigger)
		for _, b := range sortedBaseline(st) {
			log.Logf("  baseline: %-34s [%s]", b.Name, b.Surface)
		}
		return
	}

	// A HAND-RUN MUST NOT PAPER OVER A DEAD TIMER. This run succeeded, but if
	// the SCHEDULED watcher has not completed a good pass in a few cycles, that
	// is the thing worth saying - otherwise "nothing new" reads as reassurance
	// while the timer has been down for a month.
	if trigger == "manual" {
		if stale, why := scheduledIsStale(st, cfg, now); stale {
			log.Logf("STALE / FAILING - this manual check succeeded, but %s", why)
		}
	}

	if len(all) == 0 {
		// STATE 2. THE SURFACE IS NAMED, ALWAYS, and so is the time - silence is
		// not a result, and a result with no timestamp on it is barely one.
		log.Logf("CHECKED, NOTHING NEW at %s. %s | trigger=%s",
			now.Format(time.RFC3339), coverage(cfg), trigger)
		return
	}
	// STATE 1.
	log.Logf("NEW CARD FOUND - %d item(s) at %s. %s | trigger=%s",
		len(all), now.Format(time.RFC3339), coverage(cfg), trigger)
	for _, c := range all {
		log.Logf("  %-13s %-34s [%s] %s", c.Kind, c.Card, c.Surface, c.Detail)
	}
}

// coverage states what was actually checked, in words that stay true after
// stage 2 lands.
// scheduledIsStale reports whether the SCHEDULED watcher has gone quiet.
//
// The third state the addendum adds. A tripwire that died three weeks ago and
// one that ran an hour ago and found nothing produce identical silence; this is
// what tells them apart. It errs toward STALE - an unreadable timestamp is
// treated as stale rather than assumed healthy.
func scheduledIsStale(st *State, cfg Config, now time.Time) (bool, string) {
	if st.LastGoodScheduled == "" {
		return true, fmt.Sprintf("the scheduled watcher has NEVER completed a good "+
			"run - only manual checks have ever succeeded (threshold %s)",
			cfg.StaleAfter())
	}
	t, err := time.Parse(time.RFC3339, st.LastGoodScheduled)
	if err != nil {
		return true, "the last scheduled run time is unreadable, so staleness " +
			"cannot be ruled out - treated as stale rather than assumed healthy"
	}
	if age := now.Sub(t); age > cfg.StaleAfter() {
		return true, fmt.Sprintf("the scheduled watcher has not completed a good run "+
			"since %s (%s ago, threshold %s) - the timer may be dead",
			st.LastGoodScheduled, age.Round(time.Minute), cfg.StaleAfter())
	}
	return false, ""
}

// sinceGood is the phrase every failure line carries, so a failure always says
// how long it has been since anything actually worked.
func sinceGood(st *State, now time.Time) string {
	if st.LastGood == "" {
		return "NO successful check has EVER completed."
	}
	if t, err := time.Parse(time.RFC3339, st.LastGood); err == nil {
		return fmt.Sprintf("Last successful check: %s (%s ago).",
			st.LastGood, now.Sub(t).Round(time.Minute))
	}
	return "Last successful check: " + st.LastGood + "."
}

func coverage(cfg Config) string {
	s := fmt.Sprintf("checked boards %v for %q", cfg.Boards, cfg.Watch)
	if !cfg.Stage2Enabled {
		s += "; the GraphQL progress tracker was NOT checked (stage 2 off), so " +
			"this is not a statement about the whole roadmap"
	}
	return s
}

func surfaceOf(st *State, key string, res FetchResult) string {
	if res.Surface != "" {
		return res.Surface
	}
	for _, b := range st.Baseline {
		if fmt.Sprintf("b%d", b.Board) == key && b.Surface != "" {
			return b.Surface
		}
	}
	return "surface unknown"
}

func orNever(s string) string {
	if s == "" {
		return "never"
	}
	return s
}

func sortedBaseline(st *State) []BaselineCard {
	out := make([]BaselineCard, 0, len(st.Baseline))
	for _, b := range st.Baseline {
		out = append(out, b)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Name < out[j].Name })
	return out
}

func printStatus(statePath string, cfg Config, cfgFrom string) {
	st, first, err := LoadState(statePath)
	if err != nil {
		fmt.Println("state unreadable:", err)
		return
	}
	fmt.Printf("settings   : %s\n", cfgFrom)
	fmt.Printf("cadence    : every %.1f hours\n", cfg.IntervalHours)
	fmt.Printf("boards     : %v\n", cfg.Boards)
	fmt.Printf("watching   : %q\n", cfg.Watch)
	fmt.Printf("stage 2    : %s\n", map[bool]string{true: "scheduled", false: "built, not scheduled"}[cfg.Stage2Enabled])
	if first {
		fmt.Println("state      : none yet - nothing has been polled")
		return
	}
	fmt.Printf("last run   : %s (%s)\n", st.LastRun, st.LastRunBy)
	fmt.Printf("last good  : %s\n", orNever(st.LastGood))
	fmt.Printf("last good (scheduled): %s\n", orNever(st.LastGoodScheduled))
	// THE THIRD STATE, on the status screen too. A person checking on the
	// watcher must be told it has stopped, not left to infer it from a
	// timestamp they have to do arithmetic on.
	if stale, why := scheduledIsStale(st, cfg, time.Now().UTC()); stale {
		fmt.Printf("state      : STALE / FAILING - %s\n", why)
	} else {
		fmt.Println("state      : healthy - the scheduled watcher is completing runs")
	}
	fmt.Printf("baseline   : %d watched card(s)\n", len(st.Baseline))
	for _, b := range sortedBaseline(st) {
		fmt.Printf("   %-34s [%s] first seen %s\n", b.Name, b.Surface, b.FirstAt)
	}
}

// findProjectRoot walks up looking for the repo, so logs land in logs/ next to
// every other tool's rather than beside a stray exe.
func findProjectRoot(start string) string {
	d := start
	for i := 0; i < 6; i++ {
		if _, err := os.Stat(filepath.Join(d, "CLAUDE.md")); err == nil {
			return d
		}
		p := filepath.Dir(d)
		if p == d {
			break
		}
		d = p
	}
	return start
}

var _ = json.Marshal
