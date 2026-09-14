package main

// rsi-watcher - the local, free, no-AI replacement for the Claude hourly RSI
// sweep (Architecture's order with Owner's word, 2026-09-14,
// `..._go-rsi-firehose-watcher-sc-brain.md`). Findings:
// claude/FINDING_the-rsi-watcher-pays-an-ai-to-do-a-diff-2026-09-09.md and
// claude/FINDING_the-rsi-watcher-is-blind-and-the-knowledge-base-is-at-82-percent-2026-09-14.md.
//
// A QUIET HOUR IS A DIFF, NOT A THOUGHT:
//
//	1  GET each configured source (cache-busted) and the roadmap board's build line
//	2  diff post ids against the stored set; diff LIVE/PTU against the stored build
//	3  detect staleness - an unreachable or unreadable source, or a newest post
//	   whose relative age has not moved (quiet is not blind)
//	4  write state
//	5  on NEW: one JSON card per item on its sc-brain shelf - no summaries
//	6  a wake marker only on change; the trigger is a CIG id or build, which
//	   nothing a woken session writes can produce
//
// THE MANUAL CHECK RUNS THE SAME CODE PATH AS THE TIMER, as in roadmap-watcher:
//
//	rsi-watcher            run on the configured cadence
//	rsi-watcher -check     check now, once, and exit
//	rsi-watcher -status    print what is known, poll nothing
//
// THREE OUTCOMES, NEVER CONFUSED: NEW (cards written), CHECKED NOTHING NEW (every
// surface named), and DID NOT LOOK (LastGood not advanced). A source with no
// verified endpoint is NOT CONFIGURED and says so on every run.

import (
	"flag"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"citizencompass/pkg/apikeyguard"
	"citizencompass/pkg/pipelinelog"
)

// Paths are where this writes - all under the project root except settings.
type Paths struct {
	State  string // sc-brain/plumbing/state/rsi-watcher-state.json
	Wake   string // sc-brain/plumbing/state/rsi-watcher-wake.json
	Shelf  string // sc-brain/cig-firehose
	Builds string // shelf for build changes, under Shelf
}

func pathsFor(root string) Paths {
	return Paths{
		State:  filepath.Join(root, "sc-brain", "plumbing", "state", "rsi-watcher-state.json"),
		Wake:   filepath.Join(root, "sc-brain", "plumbing", "state", "rsi-watcher-wake.json"),
		Shelf:  filepath.Join(root, "sc-brain", "cig-firehose"),
		Builds: "patches",
	}
}

func main() {
	check := flag.Bool("check", false, "check now, once, then exit")
	status := flag.Bool("status", false, "print what is known and exit; polls nothing")
	fromTask := flag.Bool("from-task", false, "with -check: tag run as scheduled (Task Scheduler owns the interval)")
	flag.Parse()

	exeDir := "."
	if p, err := os.Executable(); err == nil {
		exeDir = filepath.Dir(p)
	}
	root := findProjectRoot(exeDir)
	log := pipelinelog.New(root, "rsi-watcher")

	// The same startup guard every Go tool here carries (pkg/apikeyguard);
	// -check and -status go through it too.
	apikeyguard.Enforce("rsi-watcher", func(msg string) { log.Logf("%s", msg) })

	cfg, cfgFrom, err := LoadConfig(exeDir)
	if err != nil {
		log.Logf("REFUSING TO START: %v", err)
		os.Exit(1)
	}
	if err := cfg.Validate(); err != nil {
		log.Logf("REFUSING TO START: %v", err)
		os.Exit(1)
	}
	p := pathsFor(root)
	if *status {
		printStatus(p, cfg, cfgFrom)
		return
	}
	log.Logf("rsi-watcher starting | settings from %s | every %.1fh | %s",
		cfgFrom, cfg.IntervalHours, describeSources(cfg))
	client := &http.Client{Timeout: 60 * time.Second}
	if *check {
		trigger := "manual"
		if *fromTask || fromTaskScheduler() {
			trigger = "scheduled"
		}
		runOnce(log, cfg, p, client, trigger, time.Now().UTC())
		return
	}
	runOnce(log, cfg, p, client, "scheduled", time.Now().UTC())
	t := time.NewTicker(cfg.Interval())
	defer t.Stop()
	for range t.C {
		runOnce(log, cfg, p, client, "scheduled", time.Now().UTC())
	}
}

func describeSources(cfg Config) string {
	var on, off []string
	for _, s := range cfg.Sources {
		if s.Configured() {
			on = append(on, s.Name)
		} else {
			off = append(off, s.Name)
		}
	}
	return fmt.Sprintf("sources %v; NOT CONFIGURED %v", on, off)
}

// Result is what one pass found, for the log and for tests.
type Result struct {
	Outcome       string // NEW | NOTHING NEW | DID NOT LOOK | BASELINE
	Polled        []string
	Failed        []string
	Stale         []string
	NotConfigured []string
	Cards         []string
	BuildRead     bool
}

// runOnce is THE code path: the timer and -check both call exactly this.
func runOnce(log *pipelinelog.Logger, cfg Config, p Paths, client *http.Client, trigger string, now time.Time) Result {
	var r Result
	st, first, err := LoadState(p.State)
	if err != nil {
		log.Logf("STOPPING THIS PASS: state unreadable (%v) - not re-baselining over it", err)
		r.Outcome = "DID NOT LOOK"
		return r
	}
	stamp := now.Format(time.RFC3339)
	var news []Card
	baselined := false

	for _, s := range cfg.Sources {
		if !s.Configured() {
			r.NotConfigured = append(r.NotConfigured, s.Name)
			log.Logf("%s: NOT CONFIGURED - no verified endpoint yet (routed to Research 2026-09-13). "+
				"Not polled, and NOT quiet.", s.Name)
			continue
		}
		ss := st.source(s.Name)
		items, code, ferr := Fetch(client, cfg.UserAgent, s, now)
		if ferr != nil {
			ss.LastError = fmt.Sprintf("%s: %v", stamp, ferr)
			r.Failed = append(r.Failed, s.Name)
			log.Logf("%s: DID NOT LOOK - %v (HTTP %d)", s.Name, ferr, code)
			continue
		}
		// Stuck relative age: same newest post, same "N minutes ago", for too long.
		top := items[0]
		if top.ID == ss.NewestID && top.Time == ss.NewestTime && ss.NewestTimeSince != "" {
			if since, perr := time.Parse(time.RFC3339, ss.NewestTimeSince); perr == nil &&
				strings.Contains(strings.ToLower(top.Time), "ago") &&
				now.Sub(since) > time.Duration(cfg.StaleAgeMinutes*float64(time.Minute)) {
				r.Stale = append(r.Stale, s.Name)
				ss.LastError = fmt.Sprintf("%s: STALE - newest post still reads %q since %s", stamp, top.Time, ss.NewestTimeSince)
				log.Logf("%s: STALE - the newest post has read %q since %s. A stuck page, not a quiet "+
					"feed - counted as DID NOT LOOK.", s.Name, top.Time, ss.NewestTimeSince)
				continue
			}
		} else {
			ss.NewestID, ss.NewestTime, ss.NewestTimeSince = top.ID, top.Time, stamp
		}
		r.Polled = append(r.Polled, s.Name)
		ss.LastOK, ss.LastError = stamp, ""
		baseline := len(ss.Known) == 0
		fresh := 0
		for _, it := range items {
			if ss.known(it.ID) {
				continue
			}
			ss.remember(it.ID)
			if baseline {
				continue
			}
			fresh++
			news = append(news, Card{Source: s.Name, Shelf: s.Shelf, ID: it.ID, Title: it.Title,
				URL: it.URL, Time: it.Time, FirstSeenUTC: stamp, Trigger: trigger})
		}
		if baseline {
			baselined = true
			log.Logf("%s: BASELINE TAKEN - %d item(s) recorded as already known. None of it is news.", s.Name, len(items))
		} else {
			log.Logf("%s: %d item(s) read, %d new", s.Name, len(items), fresh)
		}
	}

	live, ptu, berr := FetchBuild(client, cfg.UserAgent, cfg.LiveURL)
	if berr != nil {
		log.Logf("build: DID NOT LOOK - %v", berr)
	} else {
		r.BuildRead = true
		switch {
		case st.Live == "":
			st.Live, st.PTU, st.BuildSince = live, ptu, stamp
			baselined = true
			log.Logf("build: BASELINE TAKEN - live %s, PTU %s", live, ptu)
		case live != st.Live || ptu != st.PTU:
			log.Logf("build: CHANGED - live %s -> %s, PTU %s -> %s", st.Live, live, st.PTU, ptu)
			if live != st.Live {
				news = append(news, Card{Source: "build", Shelf: p.Builds, ID: "live-" + live,
					Title: "LIVE is now " + live + " (was " + st.Live + ")", URL: cfg.LiveURL,
					FirstSeenUTC: stamp, Trigger: trigger})
			}
			if ptu != st.PTU {
				news = append(news, Card{Source: "build", Shelf: p.Builds, ID: "ptu-" + ptu,
					Title: "PTU is now " + ptu + " (was " + st.PTU + ")", URL: cfg.LiveURL,
					FirstSeenUTC: stamp, Trigger: trigger})
			}
			st.Live, st.PTU, st.BuildSince = live, ptu, stamp
		default:
			log.Logf("build: live %s, PTU %s - unchanged since %s", live, ptu, st.BuildSince)
		}
	}

	st.LastRun, st.LastRunBy = stamp, trigger
	if len(r.Polled) == 0 && !r.BuildRead {
		_ = SaveState(p.State, st)
		r.Outcome = "DID NOT LOOK"
		log.Logf("STALE / FAILING - nothing was read this pass, so this is NOT 'CIG was quiet', it is "+
			"'we did not look'. %s trigger=%s", sinceGood(st, now), trigger)
		return r
	}
	st.LastGood = stamp
	if trigger == "scheduled" {
		st.LastGoodScheduled = stamp
	}

	for _, c := range news {
		path, wrote, werr := WriteCard(p.Shelf, c)
		switch {
		case werr != nil:
			log.Logf("CARD NOT WRITTEN %s/%s: %v", c.Shelf, c.ID, werr)
		case wrote:
			r.Cards = append(r.Cards, path)
		default:
			log.Logf("card %s/%s already on the shelf - not rewritten", c.Shelf, c.ID)
		}
	}
	if err := SaveState(p.State, st); err != nil {
		log.Logf("WARNING: state not saved (%v) - the next pass will re-report what this one found", err)
	}
	if trigger == "manual" {
		if stale, why := scheduledIsStale(st, cfg, now); stale {
			log.Logf("STALE / FAILING - this manual check read something, but %s", why)
		}
	}
	surfaces := fmt.Sprintf("read %v; failed %v; stale %v; NOT CONFIGURED %v; build read %v",
		r.Polled, r.Failed, r.Stale, r.NotConfigured, r.BuildRead)
	if len(news) > 0 {
		if err := WriteWake(p.Wake, Wake{At: stamp, Trigger: trigger, Items: news}); err != nil {
			log.Logf("WAKE MARKER NOT WRITTEN: %v", err)
		}
		r.Outcome = "NEW"
		log.Logf("NEW - %d item(s) at %s, %d card(s) written. %s | trigger=%s", len(news), stamp, len(r.Cards), surfaces, trigger)
		return r
	}
	if first || baselined {
		r.Outcome = "BASELINE"
	} else {
		r.Outcome = "NOTHING NEW"
	}
	log.Logf("CHECKED, %s at %s. %s | trigger=%s", r.Outcome, stamp, surfaces, trigger)
	return r
}

func scheduledIsStale(st *State, cfg Config, now time.Time) (bool, string) {
	if st.LastGoodScheduled == "" {
		return true, fmt.Sprintf("the SCHEDULED watcher has never completed a good run (threshold %s)", cfg.StaleAfter())
	}
	t, err := time.Parse(time.RFC3339, st.LastGoodScheduled)
	if err != nil {
		return true, "the last scheduled run time is unreadable - treated as stale, not assumed healthy"
	}
	if age := now.Sub(t); age > cfg.StaleAfter() {
		return true, fmt.Sprintf("the scheduled watcher has not completed a good run since %s (%s ago)",
			st.LastGoodScheduled, age.Round(time.Minute))
	}
	return false, ""
}

func sinceGood(st *State, now time.Time) string {
	if st.LastGood == "" {
		return "NO successful check has EVER completed."
	}
	if t, err := time.Parse(time.RFC3339, st.LastGood); err == nil {
		return fmt.Sprintf("Last successful check: %s (%s ago).", st.LastGood, now.Sub(t).Round(time.Minute))
	}
	return "Last successful check: " + st.LastGood + "."
}

func printStatus(p Paths, cfg Config, cfgFrom string) {
	st, first, err := LoadState(p.State)
	if err != nil {
		fmt.Println("state unreadable:", err)
		return
	}
	fmt.Printf("settings : %s\ncadence  : every %.1f hours\nsources  : %s\n", cfgFrom, cfg.IntervalHours, describeSources(cfg))
	if first {
		fmt.Println("state    : none yet - nothing has been polled")
		return
	}
	fmt.Printf("last run : %s (%s)\nlast good: %s\nbuild    : live %s, PTU %s (since %s)\n",
		st.LastRun, st.LastRunBy, st.LastGood, st.Live, st.PTU, st.BuildSince)
	if stale, why := scheduledIsStale(st, cfg, time.Now().UTC()); stale {
		fmt.Println("state    : STALE / FAILING -", why)
	}
	for name, s := range st.Sources {
		fmt.Printf("  %-11s known %d, last ok %s, last error %s\n", name, len(s.Known), s.LastOK, s.LastError)
	}
}

// findProjectRoot walks up to the repo so logs and sc-brain land in the project.
func findProjectRoot(start string) string {
	d := start
	for i := 0; i < 6; i++ {
		if _, err := os.Stat(filepath.Join(d, "CLAUDE.md")); err == nil {
			return d
		}
		parent := filepath.Dir(d)
		if parent == d {
			break
		}
		d = parent
	}
	return start
}
