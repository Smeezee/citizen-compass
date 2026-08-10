package main

// ui_state.go - what the window says, derived from reality every time.
//
// WO-UI-01 §9, which outranks everything else in that document:
//
//	THE STATUS MUST BE DERIVED FROM REALITY, NEVER FROM WHAT THE UI THINKS IT
//	DID. Read the actual process state. Read the actual log path. Count the
//	actual files on disk. Never track it in a variable and trust the variable.
//
// So there is deliberately NO cached "isCollecting" field anywhere in this
// file. Every value below is measured at the moment it is asked for:
//
//	is the game running   -> enumerate windows and look for the process
//	which install         -> read the resolved log path
//	how many captures     -> count files in the folder
//	last capture          -> stat the newest file and read its sidecar
//	recent log lines      -> read the tail of the log
//
// This project has been bitten four times by components that looked healthy
// because they were saying nothing. A window that says COLLECTING while
// nothing collects would be the fifth, and the worst, because the person
// reading it cannot check and has nobody to ask.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// uiState is the whole of what the window displays. It is rebuilt from scratch
// on every refresh; nothing in it persists between calls.
type uiState struct {
	// Collecting is true only when a game window is present RIGHT NOW.
	Collecting bool `json:"collecting"`
	// Headline is the one big line: "Collecting", "Waiting for Star Citizen…".
	Headline string `json:"headline"`
	// Install is LIVE / PTU / EPTU / TECH-PREVIEW, or "" when unknown.
	Install string `json:"install"`
	// Patch is what the game itself wrote into its log, when readable.
	Patch string `json:"patch"`

	// LogPath is the FULL path being watched, and LogHow is how it was chosen.
	LogPath string `json:"log_path"`
	LogHow  string `json:"log_how"`

	// Captures is a count of files on disk, not a running total.
	Captures    int    `json:"captures"`
	CaptureDir  string `json:"capture_dir"`
	LastCapture string `json:"last_capture"`
	LastReason  string `json:"last_reason"`

	// PendingRows is how many transaction rows are sitting in the local
	// dataset waiting to go out. It is len(Txns) at read time - nothing more -
	// because a row already confirmed sent is removed from Txns entirely (see
	// MarkTxnsSent), so this number IS "new since your last confirmed send"
	// without any separate bookkeeping to keep in step with that fact.
	PendingRows int `json:"pending_rows"`

	// RecentLog is the last few lines of collector-auto.log.
	RecentLog []string `json:"recent_log"`

	// Hotkey is the key that takes a picture, and HotkeyOK says whether
	// Windows actually gave it to us.
	//
	// # WHY THIS IS ON SCREEN AND NOT ONLY IN A LOG FILE
	//
	// Sleven, watching it run on somebody else's machine 2026-08-08: "there
	// need to be a place for users to look at what the hotkey [is] with the
	// collector."
	//
	// He is right and it is the obvious omission. The window told a person the
	// log path, the capture count and the folder - everything except the one
	// thing they have to DO. A key you cannot see is a key you do not press.
	//
	// The OK flag matters as much as the name. Hotkey registration genuinely
	// fails - another collector still running, a vendor utility that grabbed
	// the combination first - and the failure is silent from the outside. A
	// person pressing a key that was never registered gets exactly the same
	// experience as a person pressing one that is broken, and this is the only
	// place the difference can be shown.
	Hotkey   string `json:"hotkey"`
	HotkeyOK bool   `json:"hotkey_ok"`

	// WatchKeys describes capture_keys / capture_keys_held in the player's own
	// words, so they can see the tool read their settings the way they meant.
	WatchKeys string `json:"watch_keys"`

	// SettingsPath is where to change any of it.
	SettingsPath string `json:"settings_path"`

	// Problem is a plain-English sentence, or "" when nothing is wrong.
	// §9: no error codes, no paths, no stack traces in the window.
	Problem string `json:"problem"`
}

// installChannelFromPath pulls LIVE/PTU/EPTU out of a Game.log path.
//
// The channel is a directory NAME in the install layout
// (...\StarCitizen\PTU\Game.log), so it is read from the path rather than
// guessed from anything the UI selected. §6 requires the detected install to be
// named in the status line, and this is where that name comes from.
func installChannelFromPath(p string) string {
	if p == "" {
		return ""
	}
	known := []string{"LIVE", "PTU", "EPTU", "TECH-PREVIEW"}
	parts := strings.Split(strings.ToUpper(filepath.ToSlash(p)), "/")
	// Walk from the end: the channel directory is the one holding Game.log.
	for i := len(parts) - 1; i >= 0; i-- {
		for _, k := range known {
			if parts[i] == k {
				return k
			}
		}
	}
	return ""
}

// countCaptures counts PNG files actually present in the folder.
//
// §10 requires that deleting a file behind the UI's back makes the number go
// down. That only works because this counts the directory every time instead of
// incrementing a variable when a capture succeeds.
func countCaptures(dir string) (n int, newest string, newestAt time.Time) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 0, "", time.Time{}
	}
	for _, e := range entries {
		if e.IsDir() || !strings.EqualFold(filepath.Ext(e.Name()), ".png") {
			continue
		}
		n++
		info, err := e.Info()
		if err != nil {
			continue
		}
		if info.ModTime().After(newestAt) {
			newestAt = info.ModTime()
			newest = e.Name()
		}
	}
	return n, newest, newestAt
}

// reasonForCapture reads the sidecar next to a PNG and reports why it was taken.
//
// Read from the file rather than remembered, so a capture made by a previous
// run of the program still explains itself.
func reasonForCapture(dir, png string) string {
	if png == "" {
		return ""
	}
	side := filepath.Join(dir, strings.TrimSuffix(png, filepath.Ext(png))+".json")
	b, err := os.ReadFile(side)
	if err != nil {
		return ""
	}
	var sc struct {
		Trigger Trigger `json:"trigger"`
	}
	if err := json.Unmarshal(b, &sc); err != nil {
		return ""
	}
	switch sc.Trigger.Kind {
	case "hotkey":
		return "you pressed the key"
	case "interval":
		return "routine check"
	case "state_change", "event":
		return "something changed in game"
	case "once":
		return "single capture"
	case "":
		return ""
	}
	return sc.Trigger.Kind
}

// tailLines returns the last n lines of a file, oldest first.
func tailLines(path string, n int) []string {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil
	}
	all := strings.Split(strings.ReplaceAll(string(b), "\r\n", "\n"), "\n")
	var out []string
	for _, l := range all {
		if strings.TrimSpace(l) != "" {
			out = append(out, l)
		}
	}
	if len(out) > n {
		out = out[len(out)-n:]
	}
	return out
}

// humanAge turns a timestamp into something a person reads without doing sums.
func humanAge(t time.Time) string {
	if t.IsZero() {
		return ""
	}
	d := time.Since(t)
	switch {
	case d < time.Minute:
		return "just now"
	case d < 2*time.Minute:
		return "1 minute ago"
	case d < time.Hour:
		return fmt.Sprintf("%d minutes ago", int(d.Minutes()))
	case d < 2*time.Hour:
		return "1 hour ago"
	case d < 24*time.Hour:
		return fmt.Sprintf("%d hours ago", int(d.Hours()))
	}
	return t.Format("2 Jan 15:04")
}

// uiDeps are the measurements the state is built from.
//
// Injected so §10's tests can drive the window's logic without a running game:
// "assert the watched path contains PTU" needs to be able to SAY there is a PTU
// install, and "kill the process and it must say stopped" needs to be able to
// say the game is gone.
type uiDeps struct {
	gameAlive func() error
	findLog   func() (string, string)
	outDir    string
	autoLog   string

	// hotkey/hotkeyOK/watchKeys are what the window reports about input. They
	// are values rather than a lookup because they are decided once, at
	// startup, by whether Windows accepted the registration - re-deriving them
	// every refresh would be re-asking a question that has already been
	// answered, and would report an intention rather than the outcome.
	hotkey    string
	hotkeyOK  bool
	watchKeys string
	settings  string
}

func defaultUIDeps(outDir, autoLog string) uiDeps {
	return uiDeps{
		gameAlive: func() error {
			_, err := findGameWindow(false, "")
			return err
		},
		// §6: derived from the RUNNING game every refresh, not from a
		// startup scan that can only ever answer LIVE.
		findLog: findLogFromRunningGame,
		outDir:  outDir,
		autoLog: autoLog,
	}
}

// buildUIState measures everything, now.
func buildUIState(d uiDeps) uiState {
	s := uiState{CaptureDir: d.outDir}
	s.Hotkey, s.HotkeyOK = d.hotkey, d.hotkeyOK
	s.WatchKeys, s.SettingsPath = d.watchKeys, d.settings

	// THE ONE FACT THAT DECIDES THE HEADLINE, asked of the operating system
	// rather than of a variable this program set earlier.
	gameErr := d.gameAlive()
	s.Collecting = gameErr == nil

	s.LogPath, s.LogHow = d.findLog()
	s.Install = installChannelFromPath(s.LogPath)

	if s.LogPath != "" {
		if gl := ReadGameLog(s.LogPath, s.LogHow); gl.Patch != nil {
			s.Patch = *gl.Patch
		}
	}

	n, newest, newestAt := countCaptures(d.outDir)
	s.Captures = n
	if newest != "" {
		s.LastCapture = humanAge(newestAt)
		s.LastReason = reasonForCapture(d.outDir, newest)
	}

	// Read fresh every time, same rule as everything else in this function -
	// an unreadable or absent dataset just means nothing is pending yet, not
	// an error worth surfacing here (countData already reports that case when
	// it matters, at send time).
	if mst, err := loadMineStore(d.outDir); err == nil {
		s.PendingRows = len(mst.Txns)
	}

	s.RecentLog = tailLines(d.autoLog, 3)

	// The headline. §2 gives the two shapes; the install name is included
	// because §6 requires a person to be able to SEE it found the right one.
	if s.Collecting {
		what := "Star Citizen"
		if s.Install != "" {
			what += " " + s.Install
		}
		if s.Patch != "" {
			what = "Star Citizen " + s.Patch
			if s.Install != "" {
				what += " " + s.Install
			}
		}
		s.Headline = "Collecting  —  " + what
	} else {
		s.Headline = "Waiting for Star Citizen…"
	}

	// PROBLEMS, in plain sentences (§9). Only things the person can act on.
	s.Problem = firstProblem(d, s, gameErr)
	return s
}

// firstProblem reports the most useful single thing that is wrong, or "".
//
// One sentence, no error codes, no paths, no stack traces - those go in the log.
// Ordered so the most actionable comes first: a person with two problems should
// be told the one they can fix.
func firstProblem(d uiDeps, s uiState, gameErr error) string {
	// Captures folder unwritable - this stops everything, so it leads.
	if err := os.MkdirAll(d.outDir, 0o755); err != nil {
		return "I can't write to the captures folder. Try moving the program somewhere like your Documents folder."
	}
	probe := filepath.Join(d.outDir, ".ui-write-probe")
	if err := os.WriteFile(probe, []byte("x"), 0o644); err != nil {
		return "I can't save pictures to the captures folder. It may be read-only, or the drive may be full."
	}
	_ = os.Remove(probe)

	if free, err := freeSpaceBytes(d.outDir); err == nil && free > 0 && free < 500*1024*1024 {
		return fmt.Sprintf("The captures folder is nearly full — %s left on this drive.", humanBytes(free))
	}

	// Game running but no readable log: collecting will produce pictures with
	// no version or location attached, which is worth saying.
	if s.Collecting && s.LogPath == "" {
		return "I found Star Citizen but it isn't writing a log I can read."
	}

	// Not running is not a problem - it is the normal waiting state, and §2
	// already says so in the headline. Saying it twice would read as a fault.
	_ = gameErr
	return ""
}

// humanBytes formats a size the way a person would say it.
func humanBytes(b uint64) string {
	switch {
	case b >= 1<<30:
		return fmt.Sprintf("%.1f GB", float64(b)/float64(1<<30))
	case b >= 1<<20:
		return fmt.Sprintf("%d MB", b/(1<<20))
	}
	return fmt.Sprintf("%d KB", b/(1<<10))
}

// sortedStrings is a tiny helper kept so log tails render deterministically in
// tests that compare output.
func sortedStrings(in []string) []string {
	out := append([]string(nil), in...)
	sort.Strings(out)
	return out
}
