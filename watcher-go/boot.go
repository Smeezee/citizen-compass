package main

// boot.go - BOOT.md, the page a desk reads first. Brain two v0, 2026-09-12.
//
// Ordered by Architecture (2026-09-12_memo_build_go-build-brain-two-v0-the-swap-
// is-authorised), scoped in claude/SCOPE_brain-two-v0-the-boot-page-2026-09-12.md.
// A desk that followed its boot prompt read CLAUDE.md, docs/CURRENT-STATE.md and
// NEXT.md - about 115,000 tokens - before doing any work. This page is ~1,700.
//
// THE RULES IT IS BUILT UNDER, each one held by boot_test.go:
//
//	IT IS A PURE FUNCTION OF THE TREE. Every call rebuilds the whole page from
//	the files on disk. There is no event log to fall behind and no diff to get
//	wrong, and at a fraction of a second it is cheap enough for every watcher
//	cycle. Nothing on it is typed by hand: a hand edit is a bug report here.
//
//	EVERY SECTION NAMES THE FILES IT READ, with their size and time - provenance
//	per section, not one stamp at the top.
//
//	A MISSING SOURCE SAYS MISSING. Never a blank, never an absent line, never an
//	old value. The deploy version reads NOT RECORDED ON DISK until a receipt
//	exists.
//
//	TWO SOURCES THAT DISAGREE ARE BOTH NAMED, AND NOTHING IS MERGED.
//
//	IT SAYS WHAT IT CANNOT KNOW, on the page, every time. A digest that implies
//	a completeness it does not have is worse than the read it replaces.
//
// WHY THE LIVE.md PARSER IS ANCHORED TO INDENTED LINES: the Python prototype's
// first run matched the word "verified" in LIVE.md's opening PROSE and printed
// it as a date - a digest confidently wrong on its first outing. Only an
// indented "key  value" line is a fact line here, and a test plants the trap.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

const bootLineCap = 400

var (
	bootLiveVersion  = regexp.MustCompile(`(?m)^[ \t]+version[ \t]+(\S+)[ \t]*$`)
	bootLiveVerified = regexp.MustCompile(`(?m)^[ \t]+verified[ \t]+(\S.*?)[ \t]*$`)
	bootNextItem     = regexp.MustCompile(`(?m)^### (.+?)[ \t]*$`)
	bootOwnerDesk    = regexp.MustCompile(`(?m)^## ((?:C1|CODE|SLEVEN)\b.*?)[ \t]*$`)
	bootCardsData    = regexp.MustCompile(`(?s)<script>const DATA=(\{.*?\});</script>`)
)

// bootSrc is one file a section read, as the page reports it.
type bootSrc struct {
	rel     string
	present bool
	size    int64
	mod     time.Time
}

func bootStat(root, rel string) bootSrc {
	st, err := os.Stat(filepath.Join(root, filepath.FromSlash(rel)))
	if err != nil || st.IsDir() {
		return bootSrc{rel: rel}
	}
	return bootSrc{rel: rel, present: true, size: st.Size(), mod: st.ModTime()}
}

func (s bootSrc) String() string {
	if !s.present {
		return s.rel + " - MISSING"
	}
	return fmt.Sprintf("%s (%d bytes, %s)", s.rel, s.size, s.mod.Format("2006-01-02 15:04"))
}

// bootRead returns a file's text with CRLF folded to LF, so a line-anchored
// pattern never captures a trailing \r.
func bootRead(root, rel string) (string, bool) {
	b, err := os.ReadFile(filepath.Join(root, filepath.FromSlash(rel)))
	if err != nil {
		return "", false
	}
	return strings.ReplaceAll(string(b), "\r\n", "\n"), true
}

// bootJSON reads a receipt. The second value says why there is no map:
// MISSING or UNREADABLE - never an empty map passed off as a reading.
func bootJSON(root, rel string) (map[string]interface{}, string) {
	text, ok := bootRead(root, rel)
	if !ok {
		return nil, "MISSING"
	}
	var m map[string]interface{}
	if err := json.Unmarshal([]byte(strings.TrimPrefix(text, string(rune(0xFEFF)))), &m); err != nil {
		return nil, "UNREADABLE (" + err.Error() + ")"
	}
	return m, ""
}

func jStr(m map[string]interface{}, k string) string {
	switch x := m[k].(type) {
	case string:
		return x
	case float64:
		return strconv.FormatFloat(x, 'f', -1, 64)
	case bool:
		return strconv.FormatBool(x)
	}
	return ""
}

func jLen(m map[string]interface{}, k string) int {
	if a, ok := m[k].([]interface{}); ok {
		return len(a)
	}
	return 0
}

func bootAge(now, t time.Time) string {
	d := now.Sub(t)
	switch {
	case d < time.Minute:
		return "just now"
	case d < time.Hour:
		return fmt.Sprintf("%d min", int(d.Minutes()))
	case d < 48*time.Hour:
		return fmt.Sprintf("%.1f h", d.Hours())
	}
	return fmt.Sprintf("%d d", int(d.Hours()/24))
}

func bootClip(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n-3]) + "..."
}

func bootMod(path string) time.Time {
	if st, err := os.Stat(path); err == nil {
		return st.ModTime()
	}
	return time.Time{}
}

// bootNewest lists the newest files matching a repo-relative glob.
func bootNewest(root, pattern string, n int) (lines []string, count int) {
	files, _ := filepath.Glob(filepath.Join(root, filepath.FromSlash(pattern)))
	sort.Slice(files, func(i, j int) bool { return bootMod(files[i]).After(bootMod(files[j])) })
	for i, f := range files {
		if i >= n {
			break
		}
		rel, err := filepath.Rel(root, f)
		if err != nil {
			rel = f
		}
		lines = append(lines, fmt.Sprintf("    %s  %s", bootMod(f).Format("01-02 15:04"), filepath.ToSlash(rel)))
	}
	if len(files) == 0 {
		lines = append(lines, "    none found for "+pattern)
	}
	return lines, len(files)
}

// buildBoot renders the page from the tree at root. Pure: same tree, same page.
func buildBoot(root string, now time.Time, audit bool) string {
	var b []string
	add := func(lines ...string) { b = append(b, lines...) }
	src := func(ss ...bootSrc) string {
		parts := make([]string, len(ss))
		for i, s := range ss {
			parts[i] = s.String()
		}
		return "source: " + strings.Join(parts, "; ")
	}

	title := "# BOOT.md - read this first"
	if audit {
		title = "# BOOT.md - AUDIT RUN (not the canonical page; no desk reads this copy)"
	}
	add(title, "",
		fmt.Sprintf("Generated %s by the inbox watcher (watcher-go/boot.go), from the files named under each section.", now.Format("2006-01-02 15:04:05")),
		"Nothing here is typed by hand - a hand edit is a bug report against the generator.",
		"Every figure points into a deep file. Read that file before acting on the figure.", "")

	// ---- what the project is ------------------------------------------------
	add("## WHAT THE PROJECT IS", src(bootStat(root, "CLAUDE.md")), "",
		"    Citizen Compass - a fan-built Star Citizen reference site. The rules are CLAUDE.md;",
		"    the queue is NEXT.md; who writes what is OWNERS.md; what is public is LIVE.md.", "")

	// ---- what is live --------------------------------------------------------
	add("## WHAT IS LIVE", src(bootStat(root, "LIVE.md"), bootStat(root, "checks/.last_sweep.json"),
		bootStat(root, "testing/_src/.last_build.json"), bootStat(root, "testing/_src/.last_deploy.json"),
		bootStat(root, pollerRunsRel), bootStat(root, "testing/_src/next.src.html")), "")
	if text, ok := bootRead(root, "LIVE.md"); !ok {
		add("    public site    MISSING - LIVE.md not found")
	} else {
		v := bootLiveVersion.FindStringSubmatch(text)
		w := bootLiveVerified.FindStringSubmatch(text)
		if v == nil && w == nil {
			add("    public site    NOT FOUND - LIVE.md has no indented version / verified fact line")
		} else {
			ver, when := "NOT FOUND", "NOT FOUND"
			if v != nil {
				ver = v[1]
			}
			if w != nil {
				when = w[1]
			}
			add(fmt.Sprintf("    public site    version %s, verified %s  (LIVE.md)", ver, when))
		}
	}
	sweep, sErr := bootJSON(root, "checks/.last_sweep.json")
	if sweep == nil {
		add("    last sweep     " + sErr + " - checks/.last_sweep.json")
	} else {
		add(fmt.Sprintf("    last sweep     %s  %s passed, %d failed, %d not run  (checks/.last_sweep.json)",
			jStr(sweep, "at"), jStr(sweep, "passed"), jLen(sweep, "failed"), jLen(sweep, "not_run")))
	}
	build, bErr := bootJSON(root, "testing/_src/.last_build.json")
	if build == nil {
		add("    last build     " + bErr + " - testing/_src/.last_build.json")
	} else {
		add(fmt.Sprintf("    last build     %s  status %s  (testing/_src/.last_build.json)", jStr(build, "at"), jStr(build, "status")))
	}
	deploy, dErr := bootJSON(root, "testing/_src/.last_deploy.json")
	switch {
	case deploy == nil && dErr == "MISSING":
		add("    testing site   version NOT RECORDED ON DISK - testing/_src/.last_deploy.json does not exist")
	case deploy == nil:
		add("    testing site   " + dErr + " - testing/_src/.last_deploy.json")
	case jStr(deploy, "version_id") == "":
		add(fmt.Sprintf("    testing site   version NOT FOUND in the deploy output (receipt %s, testing/_src/.last_deploy.json)", jStr(deploy, "at")))
	default:
		add(fmt.Sprintf("    testing site   version %s, deployed %s  (testing/_src/.last_deploy.json)", jStr(deploy, "version_id"), jStr(deploy, "at")))
	}
	add(bootPollerLine(root, now))
	if text, ok := bootRead(root, "testing/_src/next.src.html"); !ok {
		add("    front page     MISSING - testing/_src/next.src.html not found")
	} else if m := bootCardsData.FindStringSubmatch(text); m == nil {
		add("    front page     NOT FOUND - no DATA block in testing/_src/next.src.html")
	} else {
		var d struct {
			Ships []json.RawMessage `json:"ships"`
		}
		if err := json.Unmarshal([]byte(m[1]), &d); err != nil {
			add("    front page     UNREADABLE - " + err.Error())
		} else {
			add(fmt.Sprintf("    front page     %d cards in the built source  (testing/_src/next.src.html)", len(d.Ships)))
		}
	}
	add("")

	// ---- what is open: letters -----------------------------------------------
	trayRoot := filepath.Join(root, "correspondence", "open")
	if desks, err := os.ReadDir(trayRoot); err != nil {
		add("## WHAT IS OPEN - LETTERS", "source: correspondence/open/ - MISSING", "",
			"    MISSING - there is no correspondence/open/ folder to read", "")
	} else {
		type row struct {
			desk, newest string
			open         int
			when         time.Time
		}
		var rows []row
		total := 0
		for _, d := range desks {
			if !d.IsDir() {
				continue
			}
			r := row{desk: d.Name()}
			files, _ := filepath.Glob(filepath.Join(trayRoot, d.Name(), "*.md"))
			for _, f := range files {
				total++
				raw, err := os.ReadFile(f)
				if err != nil {
					continue
				}
				head := string(raw)
				if len(head) > 4000 {
					head = head[:4000]
				}
				st := reMemoStatus.FindStringSubmatch(head)
				if st == nil || !strings.EqualFold(strings.TrimSpace(st[1]), "open") {
					continue
				}
				r.open++
				if m := bootMod(f); m.After(r.when) {
					r.when, r.newest = m, filepath.Base(f)
				}
			}
			rows = append(rows, r)
		}
		add("## WHAT IS OPEN - LETTERS",
			fmt.Sprintf("source: correspondence/open/*/*.md - the Status: line of each of %d letters", total), "",
			"    desk          open  newest open letter (age)")
		for _, r := range rows {
			nl := "-"
			if r.newest != "" {
				nl = fmt.Sprintf("%s (%s)", bootClip(strings.TrimSuffix(r.newest, ".md"), 70), bootAge(now, r.when))
			}
			add(fmt.Sprintf("    %-12s %5d  %s", r.desk, r.open, nl))
		}
		add("", `    "Open" is each letter's own Status: line. A desk that answers with a NEW letter`,
			"    leaves the old one reading Open, so these counts are an upper bound, not a to-do list.", "")
	}

	// ---- what is open: the queue ---------------------------------------------
	add("## WHAT IS OPEN - THE QUEUE", src(bootStat(root, "NEXT.md")), "")
	if text, ok := bootRead(root, "NEXT.md"); !ok {
		add("    MISSING - NEXT.md not found", "")
	} else {
		items := bootNextItem.FindAllStringSubmatch(text, -1)
		add(fmt.Sprintf("    %d items. Their state is PROSE (DONE-WHEN / BLOCKED-BY), so they are listed", len(items)),
			"    in their own words and none is judged done or open. First 20 in file order:", "")
		for i, m := range items {
			if i >= 20 {
				break
			}
			add("    - " + bootClip(m[1], 100))
		}
		if len(items) > 20 {
			add(fmt.Sprintf("    ... %d more in NEXT.md", len(items)-20))
		}
		add("")
	}

	// ---- recent rulings, decisions and findings ------------------------------
	rl, rn := bootNewest(root, "claude/RULING_*.md", 6)
	dl, dn := bootNewest(root, "docs/DECISION_*.md", 2)
	add("## RECENT RULINGS AND DECISIONS (newest first)",
		fmt.Sprintf("source: claude/RULING_*.md (%d files); docs/DECISION_*.md (%d files)", rn, dn), "")
	add(rl...)
	add(dl...)
	add("")
	fl, fn := bootNewest(root, "claude/FINDING_*.md", 6)
	add("## RECENT FINDINGS (newest first)", fmt.Sprintf("source: claude/FINDING_*.md (%d files)", fn), "")
	add(fl...)
	add("")

	// ---- who owns what ---------------------------------------------------------
	add("## WHO OWNS WHAT", src(bootStat(root, "OWNERS.md")), "")
	if text, ok := bootRead(root, "OWNERS.md"); !ok {
		add("    MISSING - OWNERS.md not found", "")
	} else {
		ds := bootOwnerDesk.FindAllStringSubmatch(text, -1)
		if len(ds) == 0 {
			add("    NOT FOUND - no C1 / CODE / SLEVEN section in OWNERS.md")
		}
		for _, m := range ds {
			add("    " + bootClip(m[1], 100))
		}
		add("    The per-file list is OWNERS.md itself.", "")
	}

	// ---- disagreements ----------------------------------------------------------
	var dis []string
	if sweep != nil && build != nil {
		sa, ba := jStr(sweep, "at"), jStr(build, "at")
		if sa != "" && ba != "" && ba > sa {
			dis = append(dis, fmt.Sprintf("the payload was BUILT at %s (testing/_src/.last_build.json), after the last "+
				"sweep at %s (checks/.last_sweep.json) - the sweep receipt may not describe what is built now", ba, sa))
		}
	}
	if sweep != nil && deploy != nil {
		sf, df := jStr(sweep, "fingerprint"), jStr(deploy, "sweep_fingerprint")
		if sf != "" && df != "" && sf != df {
			dis = append(dis, fmt.Sprintf("the testing site was deployed against sweep %s (testing/_src/.last_deploy.json), "+
				"but the latest sweep is %s (checks/.last_sweep.json) - a newer sweep is not deployed, or what is live "+
				"was not the last thing swept", bootClip(df, 19), bootClip(sf, 19)))
		}
	}
	add("## DISAGREEMENTS (reported, never merged)", "source: the two files named in each line", "")
	if len(dis) == 0 {
		add("    none detected by the two checks this page runs: build vs sweep, deploy vs sweep")
	}
	for _, d := range dis {
		add("    - " + d)
	}
	add("")

	// ---- what this page cannot know ------------------------------------------
	add("## WHAT THIS PAGE CANNOT KNOW", "source: none - this list is the generator's own statement of its limits", "",
		"    - whether a queue item is done: NEXT.md records state in prose",
		"    - whether a letter reading Open was answered by a later, different letter",
		"    - anything in the claude.ai project store, which has no file on this machine",
		"    - a decision made in a chat and never filed",
		"    - anything a file says beyond the one fact this page lifts from it - read the deep file")
	if deploy == nil {
		add("    - what the testing site is serving, until a deploy writes testing/_src/.last_deploy.json")
	}
	add("")

	// ---- deep files ----------------------------------------------------------------
	add("## DEEP FILES", "source: the files themselves", "")
	for _, rel := range []string{"CLAUDE.md", "NEXT.md", "docs/CURRENT-STATE.md", "OWNERS.md", "LIVE.md", "LATEST_HANDOFF.md"} {
		add("    " + bootStat(root, rel).String())
	}

	if n := len(b); n > bootLineCap {
		b = append(b, "", fmt.Sprintf("OVER THE %d-LINE CAP: %d lines. Nothing was cut; the generator must be tightened.", bootLineCap, n))
	}
	return strings.Join(b, "\n") + "\n"
}

// writeBoot writes the page to out through a temporary file, so a reader never
// catches it half-written.
func writeBoot(root, out string, now time.Time, audit bool) error {
	text := buildBoot(root, now, audit)
	if err := os.MkdirAll(filepath.Dir(out), 0o755); err != nil {
		return err
	}
	tmp := out + ".tmp"
	if err := os.WriteFile(tmp, []byte(text), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, out)
}

// runBootOnce is the audit-only path (-boot-once): generate once to a named
// path and report. It runs BEFORE the logger and the startup guard are set up,
// so it never writes a line into the live watcher's log.
func runBootOnce(root, out string) int {
	start := time.Now()
	if err := writeBoot(root, out, start, true); err != nil {
		fmt.Fprintf(os.Stderr, "boot-once: could not write %s: %v\n", out, err)
		return 1
	}
	text, _ := os.ReadFile(out)
	fmt.Printf("boot-once: wrote %s from %s - %d lines, %d bytes, in %s\n",
		out, root, strings.Count(string(text), "\n"), len(text), time.Since(start).Round(time.Millisecond))
	return 0
}
