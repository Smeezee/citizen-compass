package main

// gamelog.go - reads patch, build and location out of Star Citizen's Game.log.
//
// ------------------------------------------------------------------------
// HONESTY BOUNDARY - READ THIS BEFORE ADDING A PATTERN
// ------------------------------------------------------------------------
// The patterns in this file are split into two groups and the split is load
// bearing.
//
//   VERIFIED   - matched against a real Game.log on this machine
//                (StarCitizen/LIVE/Game.log, 776 lines, 2026-08-02 session,
//                FileVersion 4.9.188.23497). Each one is quoted in a comment
//                with the line it came from.
//
//   UNVERIFIED - plausible, not confirmed. The sample log on hand never left
//                the main menu: every line in it carries gamerules="SC_Frontend"
//                and the session ends at "Loading screen for Frontend_Main :
//                SC_Frontend closed". There is therefore NO in-world location
//                line in it to check an in-world pattern against.
//
// Anything UNVERIFIED that matches is reported with Verified=false and the
// pattern name attached, so a value that came from a guess can never be mistaken
// downstream for a value that came from a confirmed format.
//
// When nothing matches, Location is null and Reason says why. It is never
// filled with a plausible-looking default. An unknown location is a fact about
// the log; an invented one is a corrupt record, and this collector's whole
// output is meant to be evidence.
//
// To close a gap: read `location_patterns_tried` in the sidecar, which names
// the matchers that ran and found nothing, and `location_candidate_lines`,
// which says how many lines even looked relevant. Then go to the archive in
// LIVE/logbackups and read the real lines THERE.
//
// That last part is deliberate and is not a detour. This block used to say
// "read location_candidates[]", a field that shipped the raw log lines inside
// the sidecar so they could be read without leaving the captures folder. It is
// the only thing this tool ever wrote that bypassed the allow-listing, and it
// leaked 364 sidecars' worth of player ids and handles in a single session
// before anyone noticed. The archive has the same lines, with none of the
// consequences, and it is where this parser's patterns were confirmed from in
// the first place.

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"syscall"
	"unsafe"
)

// GameLogInfo is what the sidecar JSON carries.
type GameLogInfo struct {
	Path    string `json:"path"`
	Found   bool   `json:"found"`
	ReadErr string `json:"read_error,omitempty"`

	Patch    *string `json:"patch"` // e.g. "4.9.188.23497"
	PatchSrc string  `json:"patch_source,omitempty"`
	Build    *string `json:"build"` // e.g. "12344265"
	BuildSrc string  `json:"build_source,omitempty"`
	Branch   *string `json:"branch"` // e.g. "sc-alpha-4.9.0"

	Location    *string `json:"location"`
	LocationSrc string  `json:"location_source,omitempty"`
	LocationOK  bool    `json:"location_pattern_verified"`
	LocationWhy string  `json:"location_reason,omitempty"`

	// Which graphics API the session actually ran on. Read from the log the
	// capture path is already parsing - it took reading pixels off a PNG to
	// answer "was that session Vulkan?" before this existed.
	Renderer    *string `json:"renderer"`
	RendererSrc string  `json:"renderer_source,omitempty"`

	GameRules *string `json:"game_rules"` // "SC_Frontend" = main menu
	Map       *string `json:"map"`        // "megamap"
	InGame    *bool   `json:"appears_in_game"`

	// WHICH MATCHERS WERE TRIED, AND HOW MANY LINES LOOKED RELEVANT.
	//
	// This replaced `location_candidates []string`, which carried the raw log
	// lines themselves so a human could read them and improve the pattern. It
	// did that job once and then leaked continuously: 364 of 450 sidecars in
	// one session, ~40 raw lines each, every one carrying playerGEID, the
	// account handle and shard ids straight past the allow-listing that governs
	// everything else this tool writes.
	//
	// It is the single field that ever bypassed that allow-listing, and the
	// diagnostic value it provided - WHICH MATCHER SHOULD I BE LOOKING AT -
	// survives here intact, without a byte of log text.
	//
	// Do not reintroduce a raw-line field "temporarily". That is what this was.
	LocationPatternsTried  []string `json:"location_patterns_tried,omitempty"`
	LocationCandidateLines int      `json:"location_candidate_lines,omitempty"`

	LinesRead int `json:"lines_read"`
}

func sp(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}

// --- VERIFIED patterns -----------------------------------------------------
// Each regex below is followed by the exact line it was checked against.

var (
	// "<2026-08-02T02:43:28.680Z> FileVersion: 4.9.188.23497"
	reFileVersion = regexp.MustCompile(`(?m)^.*?\bFileVersion:\s*([0-9]+(?:\.[0-9]+)+)`)

	// "<2026-08-02T02:43:28.680Z> ProductVersion: 4.9.188.23497"
	reProductVersion = regexp.MustCompile(`(?m)^.*?\bProductVersion:\s*([0-9]+(?:\.[0-9]+)+)`)

	// "<2026-08-02T02:43:29.309Z> Changelist: 12344265"
	reChangelist = regexp.MustCompile(`(?m)^.*?\bChangelist:\s*([0-9]+)`)

	// "<2026-08-02T02:43:29.313Z> [CIG] build_version[12344265]"
	reBuildVersion = regexp.MustCompile(`\bbuild_version\[([0-9]+)\]`)

	// `BackupNameAttachment=" Build(12344265) 01 Aug 26 (19 43 20)"`
	reBackupBuild = regexp.MustCompile(`BackupNameAttachment="\s*Build\(([0-9]+)\)`)

	// "<2026-08-02T02:43:29.309Z> Branch: sc-alpha-4.9.0"
	reBranch = regexp.MustCompile(`(?m)^.*?\bBranch:\s*(\S+)`)

	// `... map="megamap" gamerules="SC_Frontend" ...`
	reGameRules = regexp.MustCompile(`gamerules="([^"]+)"`)
	reMap       = regexp.MustCompile(`\bmap="([^"]+)"`)

	// "Loading screen for Frontend_Main : SC_Frontend closed after 4.58 seconds"
	reLoadingScreen = regexp.MustCompile(`Loading screen for\s+(\S+)\s*:\s*(\S+)`)
)

// --- UNVERIFIED patterns ---------------------------------------------------
// No in-world sample was available to confirm these. Anything they produce is
// reported with location_pattern_verified=false.

type unverifiedPattern struct {
	name string
	re   *regexp.Regexp
	grp  int
}

// Each pattern captures a QUOTED value only.
//
// An earlier, looser version used the separator class [=:\s"]+ so it would
// accept `key: value`, `key="value"` and `key value` alike. Run against the real
// log it matched this:
//
//	taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14)
//
// The separator class happily consumed the closing quote and the space, walked
// out of the taskname field and into the NEXT one, and reported the player's
// location as "state". It was flagged unverified, so it was not passed off as
// fact - but a confidently-shaped piece of nonsense in a field that downstream
// code will read is worse than an honest null, and this collector's entire
// output is meant to be evidence.
//
// Requiring ="..." keeps a match inside one field. That is a real constraint,
// not a cosmetic one: a pattern that cannot cross a field boundary cannot
// invent a value out of two unrelated fields.
// verifiedLocationPatterns are formats CONFIRMED against real logs. They
// outrank every guess below, and unlike the guesses they may set
// location_pattern_verified.
//
// reMineLocation is BORROWED from gamelog_mine.go rather than restated - the
// same discipline auto.go already follows for the same regex. One definition,
// three consumers: the miner, the capture trigger, and this parser. A second
// copy would drift, and the day CIG changes the format one copy would keep
// matching and hide the other's failure.
//
// THIS IS THE FIX FOR THE LEAK, and it is also the fix for a data-quality bug
// nobody had connected to it. Every in-world capture was a photograph that did
// not know where it was taken, while the burst path - reading this very
// pattern - named the location correctly in the same second.
var verifiedLocationPatterns = []unverifiedPattern{
	{"RequestLocationInventory-Location[]", reMineLocation, 1},
}

// unverifiedLocationPatterns are guesses. A guess may fill a gap; it may never
// displace something known.
//
// THE name=" FORM IS GONE FROM THIS LIST, and its removal is the whole story of
// the leak. It was the first pattern tried for the subsystem that fires most
// often, and it has never matched anything: 1038 RequestLocationInventory lines
// across 235 archived logs, zero with name=". So the parser reached the end of
// its list, found nothing, and dumped forty raw lines - every time, in-world,
// for months.
var unverifiedLocationPatterns = []unverifiedPattern{
	{"OnClientSpawned-zone", regexp.MustCompile(`OnClientSpawned[^\n]*?\bzone="([^"]+)"`), 1},
	{"SpawnLocation-quoted", regexp.MustCompile(`(?i)\bspawn_?location="([^"]+)"`), 1},
	{"ObjectContainer-quoted", regexp.MustCompile(`(?i)\bobjectcontainer="([^"]+)"`), 1},
}

// Values that are log structure rather than places. Star Citizen's log is full
// of key="value" pairs whose values are state-machine tokens, and a pattern that
// matched the wrong key would otherwise report one of these as a location.
//
// This is a backstop, not the primary defence - the quoted-value patterns above
// are. Two independent guards, because the cost of a wrong value here is a
// corrupt record that looks perfectly well-formed.
var rejectedLocationValues = map[string]bool{
	"state": true, "status": true, "taskname": true, "establisher": true,
	"message": true, "null": true, "none": true, "true": true, "false": true,
	"finished": true, "unknown": true, "default": true, "invalid": true,
	"megamap": true, "sc_frontend": true, "sc_default": true,
}

// inGameFromRules is the ONE place that decides whether the player is in the
// world, from the one field that states it.
//
// Two callers: the sidecar's appears_in_game, and the interval-capture gate in
// auto.go. They must never be able to disagree - a gate that thinks the player
// is in the world while the sidecar says otherwise would produce exactly the
// frames this gate exists to prevent, each one carrying a note saying it should
// not have been taken.
//
// `known` is false until the log has stated gamerules at all. Callers treat
// unknown as NOT a reason to skip: the cost of a wrong skip is a lost frame of
// real gameplay, and the cost of a wrong capture is 3 MB. Those are not
// symmetric, so this fails open and says so.
func inGameFromRules(gameRules string) (in bool, known bool) {
	if strings.TrimSpace(gameRules) == "" {
		return false, false
	}
	return !strings.EqualFold(gameRules, "SC_Frontend"), true
}

func plausibleLocation(v string) bool {
	t := strings.ToLower(strings.TrimSpace(v))
	if t == "" || rejectedLocationValues[t] {
		return false
	}
	// eCVS_UnstowPlayer(14), eCVS_ReadyToStream(13) - CryEngine state enums.
	if strings.HasPrefix(t, "ecvs_") {
		return false
	}
	if len(t) < 2 || len(t) > 120 {
		return false
	}
	return true
}

// Lines worth showing a human when the location cannot be parsed.
var reLocationish = regexp.MustCompile(
	`(?i)\b(zone|location|objectcontainer|spawn|planet|moon|station|stanton|pyro|nyx|terra|crusader|arccorp|microtech|hurston)\b`)

// ---------------------------------------------------------------------------
// file access
// ---------------------------------------------------------------------------

// openSharedRead opens a file that another process holds open for writing.
//
// Star Citizen keeps Game.log open for the whole session. A plain open can be
// refused with a sharing violation, and this tool is meant to be used WHILE the
// game is running - so it asks for the permissive share mode explicitly rather
// than relying on the default.
func openSharedRead(path string) (*os.File, error) {
	p, err := syscall.UTF16PtrFromString(path)
	if err != nil {
		return nil, err
	}
	h, err := syscall.CreateFile(p,
		syscall.GENERIC_READ,
		syscall.FILE_SHARE_READ|syscall.FILE_SHARE_WRITE|syscall.FILE_SHARE_DELETE,
		nil,
		syscall.OPEN_EXISTING,
		syscall.FILE_ATTRIBUTE_NORMAL,
		0)
	if err != nil {
		return nil, err
	}
	return os.NewFile(uintptr(h), path), nil
}

// FindGameLog locates Game.log, preferring the install that the captured window
// actually belongs to. Deriving it from the running process is what makes this
// correct on a machine with LIVE, PTU and EPTU installed side by side - a
// hardcoded LIVE path would silently report the wrong patch.
// findLogFromRunningGame resolves the log from the game that is running NOW.
//
// WO-UI-01 §6 - "detection runs CONTINUOUSLY, not once at startup".
//
// # THE BUG THIS FIXES
//
// Callers passed 0 as the window handle. FindGameLog only derives the install
// from the running process image when it HAS a window, so a zero handle skipped
// the derivation entirely and fell through to the scan - and the scan returns
// the first of LIVE, PTU, EPTU, TECH-PREVIEW that exists, which is always LIVE
// on a machine with more than one installed.
//
// The loop was NOT stuck and detection was NOT running only once: runAuto calls
// this every poll. It was asking a question that could only ever have one
// answer. Sleven launched 4.10 PTU and the collector went on watching a LIVE log
// that had stopped moving an hour earlier, reporting "0 bytes read since last
// line" on every heartbeat while the interval timer kept photographing a static
// screen.
//
// Looking the window up here makes the answer track whichever install is
// actually running, and change when the player switches - which is what
// "continuously" has to mean to be worth anything.
func findLogFromRunningGame() (string, string) {
	if w, err := findGameWindow(false, ""); err == nil {
		if p, how := FindGameLog(w.H); p != "" {
			return p, how
		}
	}
	// No game window, or the derivation failed. The scan is still better than
	// nothing, and FindGameLog reports which of the two answered.
	return FindGameLog(0)
}

// gameLogOverride forces the watched log path when --gamelog is given.
//
// # WHY AN OVERRIDE IS NEEDED
//
// The scan below returns the FIRST channel it finds, in the order LIVE, PTU,
// EPTU, TECH-PREVIEW. On a machine with LIVE and PTU both installed that is
// always LIVE. In --auto the log is resolved at startup, before any game window
// exists, so the window-derived path cannot help - and someone testing a PTU
// patch would silently watch the wrong file for an entire session.
var gameLogOverride string

func FindGameLog(h HWND) (string, string) {
	// THE OVERRIDE FAILS CLOSED.
	//
	// If --gamelog names a file that is not readable, this returns nothing and
	// says why. It deliberately does NOT fall through to the scan: falling back
	// would quietly resume watching LIVE, which is precisely the failure the
	// flag exists to prevent, and the operator would see a working collector
	// pointed at the wrong install.
	if gameLogOverride != "" {
		if _, err := os.Stat(gameLogOverride); err == nil {
			return gameLogOverride, "forced by --gamelog"
		} else {
			return "", fmt.Sprintf("--gamelog %s cannot be read (%v) - refusing to fall back to a scan, "+
				"because that would silently watch a different install", gameLogOverride, err)
		}
	}

	if h != 0 {
		if exe := processImageName(windowPID(h)); exe != "" {
			// ...\StarCitizen\LIVE\Bin64\StarCitizen.exe -> ...\LIVE\Game.log
			dir := filepath.Dir(exe) // Bin64
			cand := filepath.Join(filepath.Dir(dir), "Game.log")
			if _, err := os.Stat(cand); err == nil {
				return cand, "derived from the captured window's process image path"
			}
		}
	}

	var roots []string
	for _, drive := range []string{"C:", "D:", "E:", "F:"} {
		roots = append(roots,
			drive+`\Program Files\Roberts Space Industries\StarCitizen`,
			drive+`\Roberts Space Industries\StarCitizen`)
	}
	for _, r := range roots {
		for _, ch := range []string{"LIVE", "PTU", "EPTU", "TECH-PREVIEW"} {
			cand := filepath.Join(r, ch, "Game.log")
			if _, err := os.Stat(cand); err == nil {
				return cand, "found by scanning known install locations"
			}
		}
	}
	return "", "no Game.log found in any known install location"
}

// ---------------------------------------------------------------------------
// parsing
// ---------------------------------------------------------------------------

// ReadGameLog parses the log. It reads the whole file line by line rather than
// tailing: Game.log is small (the sample is 165 KB) and the version banner is
// at the TOP while the location is near the BOTTOM, so both ends matter.
func ReadGameLog(path, how string) GameLogInfo {
	info := GameLogInfo{Path: path}

	if path == "" {
		info.ReadErr = how
		info.LocationWhy = "no Game.log to read"
		return info
	}

	f, err := openSharedRead(path)
	if err != nil {
		info.ReadErr = fmt.Sprintf("could not open (%v)", err)
		info.LocationWhy = "Game.log could not be opened"
		return info
	}
	defer f.Close()
	info.Found = true

	var (
		patch, patchSrc    string
		build, buildSrc    string
		branch             string
		gameRules, mapName string
		lastLoadingFor     string
		renderer           string
		rendererSrc        string
		candidateLines     int
		locVal, locSrc     string
		locVerified        bool
	)

	sc := bufio.NewScanner(f)
	// Some Game.log lines (the Elastic URL on line 16 of the sample) are very
	// long. The default 64 KB token limit would truncate and silently corrupt.
	sc.Buffer(make([]byte, 0, 64*1024), 4*1024*1024)

	for sc.Scan() {
		line := sc.Text()
		info.LinesRead++

		if patch == "" {
			if m := reFileVersion.FindStringSubmatch(line); m != nil {
				patch, patchSrc = m[1], "FileVersion"
			} else if m := reProductVersion.FindStringSubmatch(line); m != nil {
				patch, patchSrc = m[1], "ProductVersion"
			}
		}
		if build == "" {
			if m := reChangelist.FindStringSubmatch(line); m != nil {
				build, buildSrc = m[1], "Changelist"
			} else if m := reBuildVersion.FindStringSubmatch(line); m != nil {
				build, buildSrc = m[1], "build_version[]"
			} else if m := reBackupBuild.FindStringSubmatch(line); m != nil {
				build, buildSrc = m[1], "BackupNameAttachment Build()"
			}
		}
		if branch == "" {
			if m := reBranch.FindStringSubmatch(line); m != nil {
				branch = m[1]
			}
		}

		// FIRST-WINS, unlike the state fields below: the renderer is chosen at
		// startup and stated once. Taking the last match would let a stray
		// mention later in a long log overwrite the real answer.
		if renderer == "" {
			if m := reMineD3D.FindStringSubmatch(line); m != nil {
				renderer, rendererSrc = strings.TrimSpace(m[1]), "D3D Adapter line"
			} else if reMineVulkan.MatchString(line) {
				renderer, rendererSrc = "Vulkan", "[VK] log channel"
			}
		}

		// These are last-wins: the newest line describes the current state.
		if m := reGameRules.FindStringSubmatch(line); m != nil {
			gameRules = m[1]
		}
		if m := reMap.FindStringSubmatch(line); m != nil {
			mapName = m[1]
		}
		if m := reLoadingScreen.FindStringSubmatch(line); m != nil {
			lastLoadingFor = m[1]
			if gameRules == "" {
				gameRules = m[2]
			}
		}

		// VERIFIED FIRST. A confirmed format that matches is the answer, and no
		// guess below may overwrite it.
		for _, vp := range verifiedLocationPatterns {
			if m := vp.re.FindStringSubmatch(line); m != nil {
				v := strings.TrimSpace(m[vp.grp])
				if plausibleLocation(v) {
					locVal, locSrc, locVerified = v, vp.name+" (VERIFIED pattern)", true
				}
			}
		}

		// unverified location attempts, last plausible match wins - but never
		// over a verified answer already found.
		for _, up := range unverifiedLocationPatterns {
			if m := up.re.FindStringSubmatch(line); m != nil {
				v := strings.TrimSpace(m[up.grp])
				if plausibleLocation(v) && !locVerified {
					locVal, locSrc, locVerified = v, up.name+" (UNVERIFIED pattern)", false
				}
			}
		}

		// COUNTED, NOT KEPT. The count answers "was there anything to look at",
		// which is the only question the raw lines were ever actually used to
		// answer, and it cannot carry a handle.
		if reLocationish.MatchString(line) {
			candidateLines++
		}
	}
	if err := sc.Err(); err != nil {
		info.ReadErr = fmt.Sprintf("read stopped early: %v", err)
	}

	info.Patch, info.PatchSrc = sp(patch), patchSrc
	info.Build, info.BuildSrc = sp(build), buildSrc
	info.Branch = sp(branch)
	info.GameRules, info.Map = sp(gameRules), sp(mapName)
	info.Renderer, info.RendererSrc = sp(renderer), rendererSrc

	// SC_Frontend is the main menu. VERIFIED: every Context Establisher line in
	// the sample log carries gamerules="SC_Frontend" and the session never
	// entered the PU.
	//
	// The predicate itself now lives in inGameFromRules, because auto.go gates
	// interval capture on the same fact and two copies of "what counts as being
	// in the world" would be two things that agree until one of them is edited.
	if in, known := inGameFromRules(gameRules); known {
		info.InGame = &in
	}

	// ORDER MATTERS: a VERIFIED answer outranks an UNVERIFIED guess.
	//
	// This used to be the other way round, and the real log showed why that was
	// wrong. The session never left the menu - which the verified SC_Frontend
	// pattern states plainly - but an unverified pattern had scraped the token
	// "state" out of an unrelated field, and because it was tested first it
	// overwrote a correct, confirmed answer with a wrong, unconfirmed one.
	//
	// A guess may only fill a gap. It may never displace something known.
	switch {
	case gameRules != "" && strings.EqualFold(gameRules, "SC_Frontend"):
		// Verified, and a real answer: the player is in the menu, so there is
		// no in-world location to report and none should be invented.
		v := "main menu (not in world)"
		if lastLoadingFor != "" {
			v = fmt.Sprintf("main menu (%s, not in world)", lastLoadingFor)
		}
		info.Location = sp(v)
		info.LocationSrc = `gamerules="SC_Frontend" (VERIFIED pattern)`
		info.LocationOK = true

	case locVal != "":
		info.Location, info.LocationSrc, info.LocationOK = sp(locVal), locSrc, locVerified
		info.LocationWhy = "matched an UNVERIFIED pattern - treat as a hint, not a fact"

	default:
		info.LocationWhy = "no location pattern matched"
	}

	// The diagnostic, minus the payload. Attached only when the question is
	// live - a confidently answered location has nothing to diagnose.
	if info.Location == nil || !info.LocationOK {
		info.LocationCandidateLines = candidateLines
		for _, vp := range verifiedLocationPatterns {
			info.LocationPatternsTried = append(info.LocationPatternsTried, vp.name)
		}
		for _, up := range unverifiedLocationPatterns {
			info.LocationPatternsTried = append(info.LocationPatternsTried, up.name)
		}
	}
	return info
}

var _ = unsafe.Pointer(nil)
