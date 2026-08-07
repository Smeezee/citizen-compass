package main

// citizen-collector - THE GRABBER (WO-COLLECT-01 rev 5 sec 5.1)
//
// SCOPE - deliberately tiny.
//   One hotkey. On press: capture the Star Citizen window, write a PNG, write a
//   sidecar JSON with patch/build/UTC/location/sequence, make a noise.
//
//   NO OCR. No atlas. No vocabulary. No zones. Those are the reading half and
//   they are not in this binary.
//
// WHY IT EXISTS
//   To answer one question that has been open since 2 August and is blocking
//   the entire reading half of the collector:
//
//       IS THE GAME FONT LEGIBLE IN A CAPTURED FRAME AT SLEVEN'S RESOLUTION?
//
//   Everything here serves that. It is why the capture method is recorded in
//   every sidecar, why a blank frame is a hard failure rather than a written
//   file, and why the display resolution is stamped on every capture.

import (
	"encoding/json"
	"flag"
	"fmt"
	"image/png"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"syscall"
	"time"
)

const (
	// Version stamps every capture. The rev 5 addendum requires that any file a
	// crew member sends back names the package version that produced it, so the
	// stamping starts here, at the first artifact this tool ever writes.
	Version = "0.1.0"

	hotkeyID = 1
)

// --- window identification -------------------------------------------------

// THE ONLY PROCESS THIS TOOL WILL EVER CAPTURE.
//
// Rev 5 §3 defect. This used to select a window by TITLE, and a title is not
// evidence of anything - it is a string any program can set. The failure was
// not hypothetical: auto-detection picked this project's own terminal, titled
// "Build Star Citizen data pipeline with three jobs", and reported a confident
// match on the wrong window for an entirely plausible reason. On a crew
// machine that same logic captures a browser, a chat client, or whatever else
// happens to mention the game.
//
// An intermediate fix used an exact-title test plus a denylist of known
// bystanders. That was still wrong in kind:
//
//   - exact-title is still title-as-authority. Any window CAN be titled
//     "Star Citizen"; a browser tab is enough.
//   - a denylist FAILS OPEN. It stops the programs someone thought of, and
//     silently permits every one they did not.
//
// Matching the process is a whitelist and FAILS CLOSED. An unknown program is
// refused by default rather than captured by default, and the exe name is what
// the launcher actually runs rather than a label the program chooses.
//
// Title is now a HINT ONLY - used to pick between several windows belonging to
// this process. It can never authorise a capture.
var scProcessNames = []string{"starcitizen.exe"}

func isGameProcess(exe string) bool {
	e := strings.ToLower(strings.TrimSpace(exe))
	for _, want := range scProcessNames {
		if e == want {
			return true
		}
	}
	return false
}

type foundWindow struct {
	H     HWND
	Title string
	Class string
	Exe   string
	Rect  RECT
	How   string
}

// findGameWindow returns the window to capture.
//
// allowAny is only ever true in the master build - the flag that sets it does
// not exist in the crew binary (see variant_crew.go). So on a crew machine the
// process gate below has no bypass at all: not a discouraged one, an absent one.
func findGameWindow(allowAny bool, titleHint string) (foundWindow, error) {
	var candidates []foundWindow
	rejectedProcesses := map[string]int{}

	EnumTopWindows(func(h HWND) bool {
		if !windowVisible(h) {
			return true
		}
		r, err := GetWindowRectOf(h)
		if err != nil || r.Width() < 200 || r.Height() < 200 {
			return true // tool windows and 0-size ghosts
		}
		title := windowText(h)
		if title == "" {
			return true
		}
		exe := strings.ToLower(filepath.Base(processImageName(windowPID(h))))

		// THE GATE. Anything that is not the game is refused here, before any
		// title is consulted.
		if !isGameProcess(exe) && !allowAny {
			if exe == "" {
				exe = "<unreadable>"
			}
			rejectedProcesses[exe]++
			return true
		}

		fw := foundWindow{H: h, Title: title, Class: windowClass(h), Exe: exe, Rect: r}
		if isGameProcess(exe) {
			fw.How = "process is " + exe
		} else {
			fw.How = "NOT the game process (" + exe + ") - permitted only by --allow-any-window"
		}

		// Title is a hint for choosing among candidates, never authority.
		if titleHint != "" && !strings.Contains(strings.ToLower(title), strings.ToLower(titleHint)) {
			return true
		}
		candidates = append(candidates, fw)
		return true
	})

	if len(candidates) == 0 {
		if allowAny {
			return foundWindow{}, fmt.Errorf("no visible window matched hint %q", titleHint)
		}
		// Name what was refused. "Not found" plus the list of rejected processes
		// is diagnosable; "not found" alone invites someone to reach for a title
		// match again.
		var seen []string
		for e, n := range rejectedProcesses {
			seen = append(seen, fmt.Sprintf("%s x%d", e, n))
		}
		sort.Strings(seen)
		if len(seen) > 8 {
			seen = append(seen[:8], fmt.Sprintf("and %d more", len(seen)-8))
		}
		hint := ""
		if titleHint != "" {
			hint = fmt.Sprintf(" whose title contains %q", titleHint)
		}
		return foundWindow{}, fmt.Errorf(
			"no window belonging to %s%s.\n"+
				"    Refused %d other process(es): %s\n"+
				"    This build captures that process and nothing else - a matching "+
				"window title is not sufficient.",
			strings.Join(scProcessNames, " or "), hint,
			len(rejectedProcesses), strings.Join(seen, ", "))
	}

	// Among the game's own windows prefer the largest - the game proper rather
	// than a splash or launcher shim.
	sort.SliceStable(candidates, func(i, j int) bool {
		gi, gj := isGameProcess(candidates[i].Exe), isGameProcess(candidates[j].Exe)
		if gi != gj {
			return gi
		}
		ai := int(candidates[i].Rect.Width()) * int(candidates[i].Rect.Height())
		aj := int(candidates[j].Rect.Width()) * int(candidates[j].Rect.Height())
		return ai > aj
	})

	// Belt and braces: whatever the selection above did, the returned window must
	// belong to the game unless the master build explicitly permitted otherwise.
	// This cannot fire today - it exists so a future edit to the logic above
	// cannot quietly reintroduce the defect.
	win := candidates[0]
	if err := finalWindowGuard(win, allowAny); err != nil {
		return foundWindow{}, err
	}
	return win, nil
}

// finalWindowGuard is LAYER TWO of the process lock.
//
// It is a named function rather than an inline `if` so that it can be tested on
// its own. Two layers means two tests: a test that only exercises the first
// gate would still pass if this one were deleted, which would leave the second
// layer's protection entirely unproven. It is called from exactly one place, so
// extracting it duplicates no logic.
//
// It takes a window that has ALREADY passed selection and asks the only
// question that matters at the end: does this actually belong to the game?
func finalWindowGuard(win foundWindow, allowAny bool) error {
	if allowAny {
		return nil
	}
	if !isGameProcess(win.Exe) {
		return fmt.Errorf(
			"internal guard: selected a window from %q, which is not %s - refusing",
			win.Exe, strings.Join(scProcessNames, "/"))
	}
	return nil
}

// --- sidecar ---------------------------------------------------------------

type Sidecar struct {
	// Required by the work order.
	Sequence int     `json:"sequence"`
	UTC      string  `json:"utc"`
	Patch    *string `json:"patch"`
	Build    *string `json:"build"`
	Location *string `json:"location"`

	// WHY THIS CAPTURE HAPPENED.
	//
	// Not optional and not a pointer: once --auto exists, a folder of images
	// with no provenance cannot be read by anyone. A state change, a timer and
	// a stray double-fire are indistinguishable after the fact unless the file
	// says which it was. A capture with no stated reason is a bug, so the field
	// is always present and always populated - manual captures say "hotkey" or
	// "once" rather than saying nothing.
	Trigger Trigger `json:"trigger"`

	// Provenance. The whole point of this tool is to answer a question about
	// image quality, so how the image was made is part of the record.
	Collector struct {
		Name    string `json:"name"`
		Version string `json:"version"`
		Variant string `json:"variant"` // crew | master
	} `json:"collector"`

	Capture struct {
		Method     string `json:"method"`
		Note       string `json:"note"`
		PNG        string `json:"png"`
		WidthPx    int    `json:"width_px"`
		HeightPx   int    `json:"height_px"`
		SourceW    int    `json:"source_width_px"`
		SourceH    int    `json:"source_height_px"`
		DurationMS int64  `json:"duration_ms"`
	} `json:"capture"`

	Window struct {
		Title    string `json:"title"`
		Class    string `json:"class"`
		Exe      string `json:"exe"`
		Rect     [4]int `json:"rect_ltrb"`
		HowFound string `json:"how_found"`
	} `json:"window"`

	Display struct {
		VirtualW int `json:"virtual_width_px"`
		VirtualH int `json:"virtual_height_px"`
	} `json:"display"`

	GameLog GameLogInfo `json:"game_log"`
}

// --- capture sequence ------------------------------------------------------

var reSeq = regexp.MustCompile(`_(\d{4,})\.png$`)

// nextSequence continues from whatever is already on disk rather than restarting
// at 1. Restarting would silently overwrite an earlier session's captures, and
// the sequence number is one of the five fields the work order asks for.
func nextSequence(dir string) int {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 1
	}
	max := 0
	for _, e := range entries {
		if m := reSeq.FindStringSubmatch(e.Name()); m != nil {
			if n, err := strconv.Atoi(m[1]); err == nil && n > max {
				max = n
			}
		}
	}
	return max + 1
}

// --- sounds ----------------------------------------------------------------
//
// "Audible confirmation on each capture - no silent operation." A failure is
// also an outcome of a press, so a failure has its own sound. If only success
// beeped, a press that produced nothing would be indistinguishable from not
// having registered the press at all - and the operator is looking at a game,
// not at this console.

func soundOK()      { beep(1200, 90); beep(1700, 120) } // rising two-tone
func soundFail()    { beep(400, 250); beep(300, 350) }  // falling, longer
func soundStartup() { beep(900, 80); beep(1200, 80); beep(1500, 120) }

// --- the capture action ----------------------------------------------------

func doCapture(outDir string, allowAny bool, titleHint, forcedBackend string, seq int, trig Trigger) (string, error) {
	start := time.Now()

	// Fail closed on an unattributed capture. This cannot happen through any
	// call site today; it exists so a future one cannot quietly omit the reason
	// and leave an anonymous file in the corpus.
	if strings.TrimSpace(trig.Kind) == "" {
		return "", fmt.Errorf("internal: capture requested with no trigger reason - refusing to write an unattributed capture")
	}

	win, err := findGameWindow(allowAny, titleHint)
	if err != nil {
		return "", err
	}

	frame, err := CaptureWindow(win.H, forcedBackend)
	if err != nil {
		return "", err
	}

	now := time.Now().UTC()
	stamp := now.Format("20060102T150405Z")
	base := fmt.Sprintf("%s_%04d", stamp, seq)

	pngPath := filepath.Join(outDir, base+".png")
	jsonPath := filepath.Join(outDir, base+".json")

	// PNG first. If the image cannot be written there is nothing to describe,
	// and a sidecar pointing at a file that does not exist is worse than no
	// sidecar at all.
	pf, err := os.Create(pngPath)
	if err != nil {
		return "", fmt.Errorf("creating %s: %w", pngPath, err)
	}
	if err := png.Encode(pf, frame.Img); err != nil {
		pf.Close()
		return "", fmt.Errorf("encoding %s: %w", pngPath, err)
	}
	if err := pf.Close(); err != nil {
		return "", fmt.Errorf("closing %s: %w", pngPath, err)
	}

	logPath, how := FindGameLog(win.H)
	gl := ReadGameLog(logPath, how)

	var sc Sidecar
	sc.Sequence = seq
	sc.UTC = now.Format(time.RFC3339Nano)
	sc.Patch = gl.Patch
	sc.Build = gl.Build
	sc.Location = gl.Location
	sc.Trigger = trig

	sc.Collector.Name = "citizen-collector"
	sc.Collector.Version = Version
	sc.Collector.Variant = BuildVariant

	b := frame.Img.Bounds()
	sc.Capture.Method = frame.Method
	sc.Capture.Note = frame.Note
	sc.Capture.PNG = filepath.Base(pngPath)
	sc.Capture.WidthPx = b.Dx()
	sc.Capture.HeightPx = b.Dy()
	sc.Capture.SourceW = frame.SrcW
	sc.Capture.SourceH = frame.SrcH
	sc.Capture.DurationMS = time.Since(start).Milliseconds()

	sc.Window.Title = win.Title
	sc.Window.Class = win.Class
	sc.Window.Exe = win.Exe
	sc.Window.Rect = [4]int{int(win.Rect.Left), int(win.Rect.Top), int(win.Rect.Right), int(win.Rect.Bottom)}
	sc.Window.HowFound = win.How

	vw, _, _ := syscall.SyscallN(modUser32.NewProc("GetSystemMetrics").Addr(), 0)
	vh, _, _ := syscall.SyscallN(modUser32.NewProc("GetSystemMetrics").Addr(), 1)
	sc.Display.VirtualW = int(vw)
	sc.Display.VirtualH = int(vh)

	sc.GameLog = gl

	data, err := json.MarshalIndent(&sc, "", "  ")
	if err != nil {
		return "", fmt.Errorf("marshalling sidecar: %w", err)
	}
	if err := os.WriteFile(jsonPath, append(data, '\n'), 0o644); err != nil {
		return "", fmt.Errorf("writing %s: %w", jsonPath, err)
	}

	return pngPath, nil
}

// --- selftest --------------------------------------------------------------
//
// Required by the rev 5 addendum: the package verifier runs the crew exe with
// --selftest and requires exit 0. It must therefore be a real check - one that
// can actually fail - not a stub that returns success.

// lookupFlagExists asks whether a flag was REGISTERED, which is the question
// the crew-variant check needs answered. "Registered but false" and "does not
// exist" are different facts, and only the second one is a guarantee.
func lookupFlagExists(name string) bool {
	return flag.Lookup(name) != nil
}

func selftest(outDir string) int {
	fmt.Printf("citizen-collector %s (%s) selftest\n", Version, BuildVariant)
	fail := 0
	check := func(name string, ok bool, detail string) {
		status := "ok  "
		if !ok {
			status = "FAIL"
			fail++
		}
		fmt.Printf("  [%s] %-34s %s\n", status, name, detail)
	}

	// 1. output directory is writable
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		check("captures dir writable", false, err.Error())
	} else {
		probe := filepath.Join(outDir, ".selftest-probe")
		err := os.WriteFile(probe, []byte("probe"), 0o644)
		check("captures dir writable", err == nil, outDir)
		os.Remove(probe)
	}

	// 2. the blank-frame detector must reject a blank image AND accept a
	//    non-blank one. A detector that only ever says "fine" is the exact
	//    silent-success shape rule 12 is about, so both directions are proven.
	blankImg := newTestImage(64, 64, false)
	isBlank, why := looksBlank(blankImg)
	check("blank detector rejects blank", isBlank, why)

	noisyImg := newTestImage(64, 64, true)
	isBlank2, why2 := looksBlank(noisyImg)
	if why2 == "" {
		why2 = "accepted as real content"
	}
	check("blank detector accepts content", !isBlank2, why2)

	// 3. PNG encoder round-trips
	tmp := filepath.Join(outDir, ".selftest.png")
	f, err := os.Create(tmp)
	encOK := err == nil
	if encOK {
		encOK = png.Encode(f, noisyImg) == nil
		f.Close()
	}
	if encOK {
		st, serr := os.Stat(tmp)
		encOK = serr == nil && st.Size() > 100
	}
	check("png encode", encOK, tmp)
	os.Remove(tmp)

	// 4. Win32 surface responds
	vw, _, _ := syscall.SyscallN(modUser32.NewProc("GetSystemMetrics").Addr(), 0)
	vh, _, _ := syscall.SyscallN(modUser32.NewProc("GetSystemMetrics").Addr(), 1)
	check("win32 reachable", vw > 0 && vh > 0, fmt.Sprintf("primary display %dx%d", vw, vh))

	// 5. THE PROCESS LOCK. Proven by refusal, not by reading the source.
	fmt.Println("  -- process lock --")
	runProcessLockSelftest(check)

	// 6. --auto trigger detection, against a synthetic Game.log.
	//    Runs its own negative control FIRST; if that fires, the whole group
	//    is void and this reports NO RESULT rather than a set of passes.
	fmt.Println("  -- auto mode --")
	if runAutoSelftest(outDir, check) {
		fmt.Println("selftest VOID - the auto negative control fired; results are not trustworthy")
		return 2
	}

	// 6b. THE HOTKEY IN AUTO MODE. Registration is asked of Windows, not of a
	//     variable, and the press path is exercised through runAuto itself.
	//     This group exists because --auto shipped with the hotkey unreachable
	//     and every existing check still passed.
	fmt.Println("  -- hotkey (auto mode) --")
	// "Could not be performed" is NOT failure. A live capture session
	// legitimately holds a global hotkey, and reporting that as FAIL would make
	// the packager's "assert exit 0" fail for a reason unrelated to the package.
	// VOID keeps the two facts apart, which is the whole point of exit 2.
	hkVoid := runHotkeySelftest(check)
	runHotkeyLoopSelftest(check)
	runHotkeyPressLoggingSelftest(check)
	if runAutoHotkeyE2ESelftest(check) {
		hkVoid = true
	}

	// 6c. Which log is watched, and whether the loop says anything while quiet.
	fmt.Println("  -- game log, heartbeat, staleness --")
	runGameLogSelftest(check)
	runAutoHeartbeatSelftest(check)

	// 6d. THE WINDOW. WO-UI-01 §10 - auto-detect, follows the game, count from
	//     disk, and the interface carries what §2 requires.
	fmt.Println("  -- window (WO-UI-01) --")
	runUIDetectSelftest(check)
	runUIFollowsGameSelftest(check)
	runUICountSelftest(check)
	runSingleInstanceSelftest(check)
	runLifecycleSelftest(check)
	runPanicLoggingSelftest(check)
	runUIInterfaceSelftest(check)

	// 7. Game.log discovery - reported, never fatal. The game not being
	//    installed on a crew member's machine is not a broken collector.
	fmt.Println("  -- environment --")
	p, how := FindGameLog(0)
	if p == "" {
		fmt.Printf("  [note] %-34s %s\n", "Game.log", how)
	} else {
		gl := ReadGameLog(p, how)
		d := fmt.Sprintf("%s (%d lines", p, gl.LinesRead)
		if gl.Patch != nil {
			d += ", patch " + *gl.Patch
		}
		fmt.Printf("  [note] %-34s %s)\n", "Game.log", d)
	}

	if fail > 0 {
		fmt.Printf("selftest FAIL (%d checks failed)\n", fail)
		return 1
	}
	if hkVoid {
		fmt.Println("selftest VOID - the hotkey registration checks could not be performed")
		fmt.Println("  (something already holds the test key - a live capture session will do this)")
		fmt.Println("  Reported as NOT PERFORMED, never as a pass.")
		return 2
	}
	fmt.Println("selftest PASS")
	return 0
}

// --- main ------------------------------------------------------------------

func main() {
	// COM/WinRT apartments are per-thread, and so is RegisterHotKey's message
	// queue. Without this the Go scheduler can move the goroutine to a thread
	// that never initialised either.
	runtime.LockOSThread()

	// Without DPI awareness Windows reports virtualised coordinates on a scaled
	// display, so the window rect and the captured texture disagree and the
	// crop lands in the wrong place.
	syscall.SyscallN(procSetProcessDPIAware.Addr())

	exeDir := "."
	if p, err := os.Executable(); err == nil {
		exeDir = filepath.Dir(p)
	}

	defCfg := defaultAutoConfig()

	var (
		outDir  = flag.String("out", filepath.Join(exeDir, "captures"), "directory for captures")
		backend = flag.String("backend", "", "force one backend: wgc, dxgi or gdi (default: try all in order)")
		hotkey  = flag.String("hotkey", "ctrl+alt+f9", "capture hotkey")
		once    = flag.Bool("once", false, "capture once immediately and exit (no hotkey)")
		list    = flag.Bool("list-windows", false, "list capturable windows and exit")
		test    = flag.Bool("selftest", false, "run internal checks and exit")
		ui      = flag.Bool("ui", false, "open the window (this is also what happens with no arguments at all)")

		gamelog = flag.String("gamelog", "", "force the Game.log to watch (default: derive from the game window, else scan LIVE, PTU, EPTU, TECH-PREVIEW in that order)")

		auto     = flag.Bool("auto", false, "capture automatically on Game.log state changes (no hotkey needed)")
		interval = flag.Int("interval", defCfg.IntervalMinutes, "minutes between fallback captures when nothing changes; 0 = off")
		poll     = flag.Int("poll", defCfg.PollSeconds, "seconds between Game.log checks in --auto")
		debounce = flag.Int("debounce", defCfg.DebounceSeconds, "minimum seconds between two automatic captures")
	)
	// Bench flags come from the variant file. In the crew build this registers
	// nothing at all, so --allow-any-window and --window are not merely refused -
	// they do not exist.
	bench := registerBenchFlags()

	flag.Parse()
	allowAny, windowHint := bench()

	// Applied before anything resolves a log path, so --selftest, --once and
	// --auto all agree about which install is being watched.
	gameLogOverride = *gamelog

	// --- settings file --------------------------------------------------
	//
	// Values come from collector-settings.txt next to the exe, so a crew member
	// who has never opened a terminal can change the interval. A flag given on
	// the command line still WINS, so a support instruction ("just run it with
	// --interval 5 this once") is not silently overridden by the file.
	//
	// flag.Visit reports only the flags actually typed, which is the whole
	// mechanism: anything not typed is eligible to come from the file.
	typed := map[string]bool{}
	flag.Visit(func(f *flag.Flag) { typed[f.Name] = true })

	cfgSettings, settingNotes := loadSettings(exeDir)
	for _, n := range settingNotes {
		fmt.Fprintf(os.Stderr, "settings: %s\n", n)
	}
	applyInt := func(name string, key string, dst *int) {
		if typed[name] {
			return
		}
		if v, present, err := cfgSettings.intVal(key); err != nil {
			fmt.Fprintf(os.Stderr, "settings: %v (ignored, using %d)\n", err, *dst)
		} else if present {
			*dst = v
		}
	}
	applyInt("interval", "interval_minutes", interval)
	applyInt("poll", "poll_seconds", poll)
	applyInt("debounce", "debounce_seconds", debounce)
	if !typed["auto"] {
		if v, ok := cfgSettings.boolVal("auto"); ok {
			*auto = v
		}
	}
	if !typed["out"] {
		if v, ok := cfgSettings.str("out"); ok && strings.TrimSpace(v) != "" {
			v = strings.TrimSpace(v)
			if !filepath.IsAbs(v) {
				v = filepath.Join(exeDir, v)
			}
			*outDir = v
		}
	}
	if !typed["backend"] {
		if v, ok := cfgSettings.str("backend"); ok && strings.TrimSpace(v) != "" {
			*backend = strings.TrimSpace(v)
		}
	}
	if !typed["hotkey"] {
		if v, ok := cfgSettings.str("hotkey"); ok && strings.TrimSpace(v) != "" {
			*hotkey = strings.TrimSpace(v)
		}
	}

	// Master-only subcommands. Empty in the crew build, so an unknown verb here
	// behaves identically to any other unrecognised argument rather than hinting
	// that a hidden command exists.
	if args := flag.Args(); len(args) > 0 {
		if cmds := masterOnlyCommands(); cmds != nil {
			if fn, ok := cmds[args[0]]; ok {
				os.Exit(fn())
			}
		}
		fmt.Fprintf(os.Stderr, "unknown argument %q\n", args[0])
		flag.Usage()
		os.Exit(2)
	}

	// WO-UI-01 §4.1 - NO ARGUMENTS = THE WINDOW OPENS.
	//
	// "Do not rely on the desktop shortcut carrying a flag. Shortcuts get
	// deleted, moved and copied. The default behaviour of the program is the
	// program."
	//
	// So this is keyed on there being no arguments AT ALL, not on a --ui flag
	// being passed. --ui exists too, for automation and for testing, but it is
	// never required and never the documented way to do anything.
	if *ui || flag.NFlag() == 0 && flag.NArg() == 0 {
		logPath := filepath.Join(exeDir, "collector-auto.log")
		cfg := autoConfig{
			PollSeconds:     *poll,
			DebounceSeconds: *debounce,
			IntervalMinutes: *interval,
		}
		if err := runUI(cfg, *outDir, exeDir, logPath, *hotkey); err != nil {
			// No console to print to. Windows' own message box is the only
			// place a person will ever see this.
			showErrorBox("Citizen Collector", err.Error())
			os.Exit(1)
		}
		return
	}

	if *test {
		// WO-UI-01 §5, all three parts. The console attach is what makes a
		// -H=windowsgui build still print when a human ran it from a shell; the
		// results file is what automation reads; the exit code is the contract.
		attachParentConsole()
		code, transcript := runTeed(func() int { return selftest(*outDir) })
		p := writeSelftestResults(exeDir, code, transcript)
		fmt.Printf("results written to %s\n", p)
		os.Exit(code)
	}

	if *list {
		fmt.Println("visible windows (>=200x200):")
		EnumTopWindows(func(h HWND) bool {
			if !windowVisible(h) {
				return true
			}
			r, err := GetWindowRectOf(h)
			if err != nil || r.Width() < 200 || r.Height() < 200 {
				return true
			}
			t := windowText(h)
			if t == "" {
				return true
			}
			fmt.Printf("  %-52s %-22s %4dx%-4d  %s\n",
				truncate(t, 52), truncate(windowClass(h), 22),
				r.Width(), r.Height(),
				filepath.Base(processImageName(windowPID(h))))
			return true
		})
		return
	}

	if err := os.MkdirAll(*outDir, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "cannot create %s: %v\n", *outDir, err)
		os.Exit(1)
	}

	seq := nextSequence(*outDir)

	if *once {
		p, err := doCapture(*outDir, allowAny, windowHint, *backend, seq,
			Trigger{Kind: "once", Note: "run with --once"})
		if err != nil {
			soundFail()
			fmt.Fprintf(os.Stderr, "capture failed: %v\n", err)
			os.Exit(1)
		}
		soundOK()
		fmt.Printf("wrote %s\n", p)
		return
	}

	// =====================================================================
	// AUTO MODE
	// =====================================================================
	if *auto {
		// --allow-any-window IS MANUAL-ONLY, AND THIS IS WHERE THAT IS
		// ENFORCED RATHER THAN ASSUMED.
		//
		// The flag only exists in the master build at all. But a master build
		// left running unattended with the process restriction lifted would
		// quietly photograph whatever happened to be on screen - a browser, a
		// chat window, a bank tab - for hours, into a corpus meant to be
		// shared. Refusing the COMBINATION is the guard; the auto loop below
		// then hardcodes allowAny=false so there is no value to pass anyway.
		if allowAny {
			fmt.Fprintln(os.Stderr,
				"--allow-any-window cannot be combined with --auto.\n"+
					"    Lifting the process restriction is a bench-testing tool for a human\n"+
					"    watching the screen. Unattended, it would capture whatever window\n"+
					"    happened to be in front for as long as it ran.\n"+
					"    Use --auto alone, or --allow-any-window with --once.")
			os.Exit(2)
		}
		if *poll < 1 {
			fmt.Fprintf(os.Stderr, "--poll must be at least 1 second (got %d)\n", *poll)
			os.Exit(2)
		}
		if *debounce < 0 {
			fmt.Fprintf(os.Stderr, "--debounce cannot be negative (got %d)\n", *debounce)
			os.Exit(2)
		}
		if *interval < 0 {
			fmt.Fprintf(os.Stderr, "--interval cannot be negative; use 0 to turn it off (got %d)\n", *interval)
			os.Exit(2)
		}

		// Give the user something to edit. Never overwrites an existing file.
		if sp, created, err := writeSettingsTemplateIfAbsent(exeDir); err != nil {
			fmt.Fprintf(os.Stderr, "could not write %s: %v\n", sp, err)
		} else if created {
			fmt.Printf("wrote a settings file you can edit: %s\n", sp)
		}

		logPath := filepath.Join(exeDir, "collector-auto.log")
		lf, err := openAutoLog(logPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "cannot open %s: %v\n", logPath, err)
			os.Exit(1)
		}
		defer lf.Close()

		logf := func(format string, args ...interface{}) {
			fmt.Fprintf(lf, "[%s] %s\n", time.Now().Format("2006-01-02 15:04:05"),
				fmt.Sprintf(format, args...))
		}

		fmt.Printf("citizen-collector %s (%s) - AUTO\n", Version, BuildVariant)
		fmt.Printf("captures : %s\n", *outDir)
		fmt.Printf("log      : %s\n", logPath)
		fmt.Printf("settings : %s\n", filepath.Join(exeDir, settingsFileName))
		fmt.Printf("poll %ds, debounce %ds, interval %s\n",
			*poll, *debounce, intervalDesc(*interval))

		// The watched log, and HOW it was chosen, on every start. The scan
		// takes the first of LIVE, PTU, EPTU, TECH-PREVIEW that exists, which
		// is always LIVE on a machine with both - so the reason matters as much
		// as the path. A session spent watching the wrong install should be
		// visible here, not deduced later from captures that never happened.
		if gp, ghow := findLogFromRunningGame(); gp == "" {
			fmt.Printf("watching : NO Game.log - %s\n", ghow)
		} else {
			fmt.Printf("watching : %s\n", gp)
			fmt.Printf("           (%s)\n", ghow)
		}
		logf("---- citizen-collector %s (%s) auto start ----", Version, BuildVariant)

		// THE HOTKEY, REGISTERED IN THE AUTO BRANCH.
		//
		// This used to live after the `return` at the bottom of this branch, so
		// in --auto RegisterHotKey was never reached. Ctrl+Alt+F9 did nothing,
		// logged nothing, and gave no sign it was dead - found only when the key
		// was pressed repeatedly at a shop terminal during a live session.
		//
		// It has to be here, before the poll loop, because auto mode triggers on
		// state change and standing still is not a state change. At a shop, a
		// mission board or an inventory screen the log does not move, so the
		// hotkey is the ONLY way to capture those screens.
		//
		// Registration failure is reported on stdout AND in collector-auto.log.
		// A hotkey that silently fails to register is the same defect in a
		// different place, and the console is hidden moments from now - so the
		// log line is the only record that will still exist.
		var (
			hotkeyPresses <-chan struct{}
			hotkeyName    string
		)
		if hl, err := startHotkeyListener(hotkeyID, *hotkey); err != nil {
			fmt.Fprintf(os.Stderr,
				"WARNING: hotkey %q NOT registered: %v\n"+
					"Automatic captures still work. Manual capture does not.\n"+
					"Another program probably owns that combination - pick another with --hotkey.\n",
				*hotkey, err)
			logf("WARNING: hotkey %q NOT REGISTERED: %v - automatic capture still active, manual capture unavailable", *hotkey, err)
		} else {
			hotkeyPresses = hl.Presses
			hotkeyName = hl.Pretty
			fmt.Printf("hotkey   : %s (manual capture)\n", hl.Pretty)
			logf("hotkey registered: %s", hl.Pretty)
		}

		// Auto mode continues even with no hotkey. Losing manual capture is bad;
		// losing unattended capture as well, because of it, would be worse.

		fmt.Println("This window will now hide. Close it from Task Manager to stop.")

		soundStartup()
		hideConsole()

		deps := autoDeps{
			logf:       logf,
			hotkeys:    hotkeyPresses,
			hotkeyName: hotkeyName,
			// The window gate. allowAny is LITERALLY false here - not a
			// variable that happens to be false.
			gameAlive: func() error {
				_, err := findGameWindow(false, "")
				return err
			},
			capture: func(t Trigger) (string, error) {
				p, err := doCapture(*outDir, false, "", *backend, seq, t)
				if err == nil {
					seq++
					soundOK()
				} else {
					soundFail()
				}
				return p, err
			},
		}

		cfg := autoConfig{
			PollSeconds:     *poll,
			DebounceSeconds: *debounce,
			IntervalMinutes: *interval,
		}
		if err := runAuto(cfg, logPath, deps, nil); err != nil {
			logf("auto mode ended: %v", err)
			os.Exit(1)
		}
		return
	}

	mods, vk, keyName, err := parseHotkey(*hotkey)
	if err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}
	if err := RegisterHotKey(hotkeyID, mods|ModNoRepeat, vk); err != nil {
		fmt.Fprintf(os.Stderr,
			"could not register %s: %v\n"+
				"Another program probably owns that combination. Pick a different one with --hotkey.\n",
			keyName, err)
		os.Exit(1)
	}
	defer UnregisterHotKey(hotkeyID)

	fmt.Printf("citizen-collector %s (%s)\n", Version, BuildVariant)
	fmt.Printf("hotkey   : %s\n", keyName)
	fmt.Printf("captures : %s\n", *outDir)
	fmt.Printf("next seq : %04d\n", seq)
	if *backend != "" {
		fmt.Printf("backend  : %s (forced)\n", *backend)
	} else {
		fmt.Printf("backend  : wgc -> dxgi -> gdi (first one that yields a non-blank frame)\n")
	}
	if w, err := findGameWindow(allowAny, windowHint); err == nil {
		fmt.Printf("target   : %q %dx%d - %s\n", w.Title, w.Rect.Width(), w.Rect.Height(), w.How)
	} else {
		fmt.Printf("target   : not found yet - %v\n", err)
		fmt.Printf("           (that is fine; it is looked up again on every press)\n")
	}
	fmt.Println("\nPress the hotkey to capture. Ctrl+C here to quit.")
	soundStartup()

	var msg MSG
	for GetMessage(&msg) {
		if msg.Message != WM_HOTKEY {
			continue
		}
		p, err := doCapture(*outDir, allowAny, windowHint, *backend, seq,
			Trigger{Kind: "hotkey", Note: keyName})
		if err != nil {
			soundFail()
			fmt.Printf("[%s] seq %04d FAILED: %v\n", time.Now().Format("15:04:05"), seq, err)
			continue
		}
		soundOK()
		fmt.Printf("[%s] seq %04d -> %s\n", time.Now().Format("15:04:05"), seq, filepath.Base(p))
		seq++
	}
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n-3] + "..."
}
