package main

// window.go - the window, as a plain Windows window.
//
// ===========================================================================
// WHY THIS IS NOT A BROWSER ENGINE - Sleven's ruling, 2026-08-15
// ===========================================================================
//
// Four defects in one day traced to one root: a three-button panel rendered in
// an embedded browser. The empty black box, the bridge that never answered, the
// twelve-second timeout invented to notice, the browser fallback, the parity
// check keeping two transports honest - none of that is a feature. All of it is
// scaffolding around WebView2.
//
// And the bridge failed on a machine that HAD a runtime, so bundling the 162 MB
// payload would not have helped.
//
// The requirement was "future proof for the next twenty years". Microsoft has
// replaced its embedded browser four times in twenty years - MSHTML, the Edge
// WebBrowser control, EdgeHTML/WebView, WebView2. Windows from the 1990s that
// creates a window and puts controls on it still runs today, unchanged. This
// file is that bet.
//
// NO NEW DEPENDENCY, per the order. Only user32/gdi32, the same way winapi.go,
// tray.go and shortcut.go already work.
//
// ===========================================================================
// HOW IT STAYS CHEAP TO CHANGE
// ===========================================================================
//
// Nothing here is hand-placed. window_rows.go holds the rows as DATA; this file
// walks that list, creates a label and a value for each, and stacks them. A row
// added in 2046 is one entry in a slice.
//
// Scaling is computed from the window's DPI rather than from constants, so the
// same code is correct on a 1080p laptop and a 4K monitor. That was not
// optional: this is a gaming machine's program, and gaming machines are exactly
// where high-DPI displays are.

import (
	"fmt"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"unsafe"
)

var (
	procUpdateWindow                  = modUser32.NewProc("UpdateWindow")
	procSetWindowTextW                = modUser32.NewProc("SetWindowTextW")
	procSetTimer                      = modUser32.NewProc("SetTimer")
	procKillTimer                     = modUser32.NewProc("KillTimer")
	procMoveWindow                    = modUser32.NewProc("MoveWindow")
	procGetDpiForWindow               = modUser32.NewProc("GetDpiForWindow")
	procCreateFontW                   = modGdi32.NewProc("CreateFontW")
	procGetSysColorBrush              = modUser32.NewProc("GetSysColorBrush")
	procSetBkMode                     = modGdi32.NewProc("SetBkMode")
	procSetTextColor                  = modGdi32.NewProc("SetTextColor")
	procIsWindow                      = modUser32.NewProc("IsWindow")
	procSetProcessDpiAwarenessContext = modUser32.NewProc("SetProcessDpiAwarenessContext")
)

const (
	wsOverlappedWindow = 0x00CF0000
	wsChild            = 0x40000000
	wsTabStop          = 0x00010000
	wsVScroll          = 0x00200000

	ssLeft           = 0x00000000
	ssRight          = 0x00000002
	ssLeftNoWordWrap = 0x0000000C
	ssEndEllipsis    = 0x00004000

	bsPushButton   = 0x00000000
	bsAutoCheckBox = 0x00000003

	esAutoHScroll = 0x00000080

	swShow = 5

	wmDestroy        = 0x0002
	wmSize           = 0x0005
	wmPaint          = 0x000F
	wmTimer          = 0x0113
	wmCtlColorStatic = 0x0138
	wmSetFont        = 0x0030
	bmGetCheck       = 0x00F0
	bmSetCheck       = 0x00F1

	colorWindow  = 5
	colorBtnFace = 15

	transparentBk = 1

	// DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 as a uintptr.
	dpiPerMonitorV2 = ^uintptr(0) - 3

	windowTimerID = 1
	// refreshEvery is how often the values are re-read.
	//
	// One second. The old window polled on a JavaScript interval at the same
	// cadence; this is the same rate with none of the machinery. Cheap: reading
	// the state is a directory count and a few file stats.
	refreshEveryMs = 1000
)

// control ids. Small integers, ours, in one place so a duplicate is visible.
const (
	idSend = 2001 + iota
	idCaptureNow
	idOpenPictures
	idCheckUpdate
	idAutoSend
	idAutostart
	idShowWindow
	idHotkey
	idInterval
	idSaveSettings
	idRevert
)

// collectorWindow is the window and everything it needs to refresh itself.
type collectorWindow struct {
	hwnd     uintptr
	font     uintptr
	fontBold uintptr

	headline uintptr
	problem  uintptr
	result   uintptr
	values   []uintptr // one per statusRows entry, same order

	chkAutoSend  uintptr
	chkAutostart uintptr
	chkShowWin   uintptr
	edHotkey     uintptr
	edInterval   uintptr

	exeDir string
	outDir string
	state  func() uiState
	acts   map[string]uiCall
	logf   func(string, ...interface{})

	mu sync.Mutex
}

var theWindow *collectorWindow

// ShowCollectorWindow creates the window if it does not exist, and brings it to
// the front if it does.
//
// ONE WINDOW. Called from startup and from the tray menu, and the second call
// must raise the first rather than make another - which is the same lesson
// single_instance.go exists for, one scope down.
func ShowCollectorWindow(exeDir, outDir string, state func() uiState,
	acts map[string]uiCall, logf func(string, ...interface{})) {
	if theWindow != nil && theWindow.hwnd != 0 {
		if r, _, _ := procIsWindow.Call(theWindow.hwnd); r != 0 {
			procShowWindow.Call(theWindow.hwnd, swRestore)
			procSetForegroundWindow.Call(theWindow.hwnd)
			return
		}
	}
	w := &collectorWindow{exeDir: exeDir, outDir: outDir, state: state, acts: acts, logf: logf}
	theWindow = w
	w.create()
}

// dpiScale returns how much to multiply sizes by on this window's monitor.
//
// GetDpiForWindow is Windows 10 1607+. On anything older it is absent and 96
// (100%) is the right answer, because per-monitor DPI did not exist to get
// wrong.
func (w *collectorWindow) dpiScale() float64 {
	if procGetDpiForWindow.Find() != nil || w.hwnd == 0 {
		return 1
	}
	d, _, _ := procGetDpiForWindow.Call(w.hwnd)
	if d == 0 {
		return 1
	}
	return float64(d) / 96.0
}

func (w *collectorWindow) create() {
	className, _ := syscall.UTF16PtrFromString("CitizenCollectorWindow")
	title, _ := syscall.UTF16PtrFromString("Citizen Collector")

	wndProc := syscall.NewCallback(func(h, msg, wp, lp uintptr) uintptr {
		switch uint32(msg) {
		case wmCommand:
			w.onCommand(uint32(wp) & 0xFFFF)
			return 0
		case wmTimer:
			w.refresh()
			return 0
		case wmCtlColorStatic:
			// Labels on the dialog background rather than in white boxes.
			procSetBkMode.Call(wp, transparentBk)
			br, _, _ := procGetSysColorBrush.Call(colorBtnFace)
			return br
		case wmClose:
			// CLOSING IS NOT QUITTING. The tray is home; the window is
			// something you open when you want it. Quitting is a deliberate
			// choice in the tray menu, so that closing this by reflex does not
			// stop the collection somebody installed it for.
			procShowWindow.Call(h, swHide)
			return 0
		case wmDestroy:
			procKillTimer.Call(h, windowTimerID)
			w.hwnd = 0
			return 0
		}
		r, _, _ := procDefWindowProcW.Call(h, msg, wp, lp)
		return r
	})

	brush, _, _ := procGetSysColorBrush.Call(colorBtnFace)
	wc := wndClassEx{
		CbSize:        uint32(unsafe.Sizeof(wndClassEx{})),
		LpfnWndProc:   wndProc,
		LpszClassName: className,
		HbrBackground: brush,
	}
	wc.HIcon = trayIcon(nil)
	procRegisterClassExW.Call(uintptr(unsafe.Pointer(&wc)))

	// Size is computed from the content, not chosen. Adding a row therefore
	// makes the window taller by itself.
	hwnd, _, _ := procCreateWindowExW.Call(0,
		uintptr(unsafe.Pointer(className)), uintptr(unsafe.Pointer(title)),
		wsOverlappedWindow,
		0x80000000, 0x80000000, 620, 760, // CW_USEDEFAULT position
		0, 0, 0, 0)
	w.hwnd = hwnd

	if w.hwnd == 0 {
		if w.logf != nil {
			w.logf("window: could not be created. The collector keeps running and " +
				"the tray icon still works.")
		}
		return
	}
	setWindowIcon(w.hwnd, w.logf)
	w.makeFonts()
	w.buildControls()
	w.refresh()

	procShowWindow.Call(w.hwnd, swShow)
	procUpdateWindow.Call(w.hwnd)
	procSetTimer.Call(w.hwnd, windowTimerID, refreshEveryMs, 0)
}

func (w *collectorWindow) makeFonts() {
	s := w.dpiScale()
	name, _ := syscall.UTF16PtrFromString("Segoe UI")
	mk := func(px int, weight uintptr) uintptr {
		f, _, _ := procCreateFontW.Call(
			uintptr(int32(-float64(px)*s)), 0, 0, 0, weight,
			0, 0, 0, 0, 0, 0, 0, 0,
			uintptr(unsafe.Pointer(name)))
		return f
	}
	w.font = mk(15, 400)
	w.fontBold = mk(19, 700)
}

// mk creates one child control and applies the font.
func (w *collectorWindow) mk(class, text string, style uintptr, x, y, cx, cy int, id uintptr) uintptr {
	c, _ := syscall.UTF16PtrFromString(class)
	t, _ := syscall.UTF16PtrFromString(text)
	h, _, _ := procCreateWindowExW.Call(0,
		uintptr(unsafe.Pointer(c)), uintptr(unsafe.Pointer(t)),
		wsChild|wsVisible|style,
		uintptr(int32(x)), uintptr(int32(y)), uintptr(int32(cx)), uintptr(int32(cy)),
		w.hwnd, id, 0, 0)
	if h != 0 {
		procSendMessageW.Call(h, wmSetFont, w.font, 1)
	}
	return h
}

// buildControls lays the window out FROM THE ROW LIST.
//
// Nothing below names a row or a coordinate for one. The loop is the layout.
func (w *collectorWindow) buildControls() {
	s := w.dpiScale()
	px := func(n int) int { return int(float64(n) * s) }

	const (
		margin = 18
		labelW = 170
		rowH   = 24
		gap    = 6
	)
	x := px(margin)
	y := px(margin)
	fullW := px(620 - margin*2 - 16)

	// Headline - the one line that says whether it is working.
	w.headline = w.mk("STATIC", "Starting...", ssLeftNoWordWrap|ssEndEllipsis,
		x, y, fullW, px(30), 0)
	procSendMessageW.Call(w.headline, wmSetFont, w.fontBold, 1)
	y += px(38)

	// A problem line, hidden by being empty when there is nothing wrong.
	w.problem = w.mk("STATIC", "", ssLeftNoWordWrap|ssEndEllipsis, x, y, fullW, px(rowH), 0)
	y += px(rowH)

	// What the last button did. Empty until something is pressed.
	w.result = w.mk("STATIC", "", ssLeftNoWordWrap|ssEndEllipsis, x, y, fullW, px(rowH), 0)
	y += px(rowH + gap)

	// THE ROWS. One pass over the data.
	w.values = make([]uintptr, len(statusRows))
	for i, row := range statusRows {
		w.mk("STATIC", row.Label, ssLeft, x, y, px(labelW), px(rowH), 0)
		w.values[i] = w.mk("STATIC", "-", ssLeftNoWordWrap|ssEndEllipsis,
			x+px(labelW), y, fullW-px(labelW), px(rowH), 0)
		y += px(rowH)
	}
	y += px(gap * 2)

	// Buttons - what a person came here to do.
	bw, bh := px(150), px(32)
	w.mk("BUTTON", "Send my data", bsPushButton|wsTabStop, x, y, bw, bh, idSend)
	w.mk("BUTTON", "Take a picture", bsPushButton|wsTabStop, x+bw+px(8), y, bw, bh, idCaptureNow)
	w.mk("BUTTON", "Open pictures", bsPushButton|wsTabStop, x+(bw+px(8))*2, y, bw, bh, idOpenPictures)
	y += bh + px(gap)
	w.mk("BUTTON", "Check for updates", bsPushButton|wsTabStop, x, y, bw, bh, idCheckUpdate)
	w.mk("BUTTON", "Go back a version", bsPushButton|wsTabStop, x+bw+px(8), y, bw, bh, idRevert)
	y += bh + px(gap*3)

	// Settings - §5. Every one of them, here, so nobody opens a text file.
	w.mk("STATIC", "Settings", ssLeft, x, y, fullW, px(rowH), 0)
	y += px(rowH)

	w.chkAutoSend = w.mk("BUTTON", "Send automatically when I finish playing",
		bsAutoCheckBox|wsTabStop, x, y, fullW, px(rowH), idAutoSend)
	y += px(rowH + 2)
	w.chkAutostart = w.mk("BUTTON", "Start with Windows and wait for the game",
		bsAutoCheckBox|wsTabStop, x, y, fullW, px(rowH), idAutostart)
	y += px(rowH + 2)
	w.chkShowWin = w.mk("BUTTON", "Show this window when it starts",
		bsAutoCheckBox|wsTabStop, x, y, fullW, px(rowH), idShowWindow)
	y += px(rowH + gap)

	w.mk("STATIC", "Hotkey", ssLeft, x, y+px(4), px(labelW), px(rowH), 0)
	w.edHotkey = w.mk("EDIT", "", esAutoHScroll|wsTabStop|0x00800000, /*WS_BORDER*/
		x+px(labelW), y, px(180), px(rowH), idHotkey)
	y += px(rowH + 4)
	w.mk("STATIC", "Seconds between pictures", ssLeft, x, y+px(4), px(labelW), px(rowH), 0)
	w.edInterval = w.mk("EDIT", "", esAutoHScroll|wsTabStop|0x00800000,
		x+px(labelW), y, px(180), px(rowH), idInterval)
	y += px(rowH + gap)

	w.mk("BUTTON", "Save settings", bsPushButton|wsTabStop, x, y, bw, bh, idSaveSettings)
	y += bh + px(margin)

	// The window is exactly as tall as what it holds.
	procMoveWindow.Call(w.hwnd, 200, 120, uintptr(int32(px(620))), uintptr(int32(y+px(46))), 1)

	w.loadSettingsIntoControls()
}

func (w *collectorWindow) setText(h uintptr, s string) {
	if h == 0 {
		return
	}
	p, err := syscall.UTF16PtrFromString(s)
	if err != nil {
		return
	}
	procSetWindowTextW.Call(h, uintptr(unsafe.Pointer(p)))
}

func (w *collectorWindow) getText(h uintptr) string {
	if h == 0 {
		return ""
	}
	buf := make([]uint16, 256)
	procGetWindowTextW.Call(h, uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
	return syscall.UTF16ToString(buf)
}

func (w *collectorWindow) setCheck(h uintptr, on bool) {
	v := uintptr(0)
	if on {
		v = 1
	}
	procSendMessageW.Call(h, bmSetCheck, v, 0)
}

func (w *collectorWindow) checked(h uintptr) bool {
	r, _, _ := procSendMessageW.Call(h, bmGetCheck, 0, 0)
	return r == 1
}

func (w *collectorWindow) loadSettingsIntoControls() {
	w.setCheck(w.chkAutoSend, ReadSendMode(w.exeDir) == SendAutomatic)
	w.setCheck(w.chkAutostart, AutostartEnabled())
	w.setCheck(w.chkShowWin, ShowWindowSetting(w.exeDir))

	cfg, _ := loadSettings(w.exeDir)
	hk, _ := cfg.str("hotkey")
	if strings.TrimSpace(hk) == "" {
		hk = defaultHotkey
	}
	w.setText(w.edHotkey, hk)
	iv := "120"
	if v, found, err := cfg.intVal("interval_seconds"); found && err == nil {
		iv = strconv.Itoa(v)
	}
	w.setText(w.edInterval, iv)
}

// refresh re-reads the state and pushes it into the controls.
//
// THE ONLY PLACE VALUES ARE WRITTEN, and it walks the same list the layout
// walked, so a row cannot exist in one loop and not the other.
func (w *collectorWindow) refresh() {
	if w.hwnd == 0 || w.state == nil {
		return
	}
	w.mu.Lock()
	defer w.mu.Unlock()

	s := w.state()
	w.setText(w.headline, s.Headline)
	w.setText(w.problem, s.Problem)

	ctx := rowContext{S: s, ExeDir: w.exeDir}
	for i, row := range statusRows {
		if i >= len(w.values) {
			break
		}
		v := row.Value(ctx)
		if row.Warn != nil && row.Warn(ctx) {
			v = "! " + v
		}
		w.setText(w.values[i], v)
	}
}

func (w *collectorWindow) onCommand(id uint32) {
	run := func(name string, arg interface{}, loud bool) {
		act, ok := w.acts[name]
		if !ok {
			return
		}
		// OFF THE UI THREAD. Sending takes minutes; doing it here would freeze
		// the window, and a frozen window is what this whole rebuild exists to
		// stop being possible.
		go func() {
			var raw []byte
			if arg != nil {
				raw = []byte(fmt.Sprintf("%v", arg))
			}
			w.setText(w.result, "Working...")
			v, err := act(raw)
			msg := ""
			if err != nil {
				msg = err.Error()
			} else if sv, ok := v.(string); ok {
				msg = sv
			}
			if msg == "" {
				msg = "Done."
			}
			// THE ANSWER GOES WHERE THEY ARE LOOKING.
			w.setText(w.result, msg)

			// A BOX ONLY FOR THE TWO THEY WAIT ON. Sending takes minutes and
			// somebody may have walked away; everything else is instant and a
			// dialog to dismiss is just something in the way. A modal box is
			// also the one thing that can trap a person who is mid-game.
			if loud {
				messageBox("Citizen Collector", msg, 0x00000040)
			}
			w.refresh()
		}()
	}

	switch id {
	case idSend:
		run("sendData", nil, true)
	case idCaptureNow:
		run("captureNow", nil, false)
	case idOpenPictures:
		run("openCaptures", nil, false)
	case idCheckUpdate:
		go w.checkUpdate()
	case idRevert:
		go w.doRevert()
	case idSaveSettings:
		w.saveSettings()
	case idAutoSend, idAutostart, idShowWindow:
		// Checkboxes apply immediately. A settings screen with a Save button
		// that some controls ignore is worse than one with no Save button.
		w.applyToggles()
	}
}

func (w *collectorWindow) applyToggles() {
	if err := WriteSendMode(w.exeDir, map[bool]SendMode{
		true: SendAutomatic, false: SendAsk}[w.checked(w.chkAutoSend)]); err != nil {
		w.logf("settings: could not record the send choice: %v", err)
	}
	if w.checked(w.chkAutostart) {
		if exe, err := executablePath(); err == nil {
			if err := EnableAutostart(exe, w.exeDir); err != nil {
				w.logf("settings: could not turn on start-with-Windows: %v", err)
			}
		}
	} else if err := DisableAutostart(); err != nil {
		w.logf("settings: could not turn off start-with-Windows: %v", err)
	}
	if err := SetShowWindow(w.exeDir, w.checked(w.chkShowWin)); err != nil {
		w.logf("settings: could not record the window choice: %v", err)
	}
}

func (w *collectorWindow) saveSettings() {
	w.applyToggles()
	hk := strings.TrimSpace(w.getText(w.edHotkey))
	if hk != "" {
		_ = SetSetting(w.exeDir, "hotkey", hk)
	}
	iv := strings.TrimSpace(w.getText(w.edInterval))
	if n, err := strconv.Atoi(iv); err == nil && n >= 0 {
		_ = SetSetting(w.exeDir, "interval_seconds", strconv.Itoa(n))
	}
	messageBox("Citizen Collector",
		"Saved.\n\nThe hotkey and the interval take effect the next time it starts. "+
			"Everything else is already in force.", 0x00000040)
}

func (w *collectorWindow) doRevert() {
	msg, err := RevertToPrevious(w.exeDir, w.logf)
	if err != nil {
		showErrorBox("Citizen Collector", err.Error())
		return
	}
	messageBox("Citizen Collector", msg, 0x00000040)
}

// executablePath is os.Executable in one place, so the several callers that
// need "which file am I" cannot disagree about it.
func executablePath() (string, error) { return osExecutable() }

// waitForTrayExit blocks until the tray's Exit is chosen.
//
// The tray owns the program's lifetime now. That is the point of the rebuild:
// the surface that is always working is the one that decides when to stop,
// rather than a window that might not have rendered.
func waitForTrayExit(t *trayHandle) {
	if t == nil {
		// No tray - nothing would ever stop this, so do not pretend. Better to
		// return and let the caller exit than to hang forever with no way out.
		return
	}
	t.WaitForExit()
}

// makeDpiAware tells Windows this process draws at the monitor's real DPI.
//
// WITHOUT THIS the window is bitmap-stretched by Windows on any display above
// 100% scaling - which on a 4K monitor means a blurry, soft-edged window that
// looks like a badly-made program. This is a gaming machine's tool and gaming
// machines are exactly where high-DPI displays are, so it is not an edge case.
//
// PER-MONITOR V2 IF AVAILABLE, falling back to system-DPI-aware. The newer call
// is Windows 10 1703+; the older one goes back to Vista. Trying the good one
// first and accepting the old one is how this stays correct on both without
// asking what version of Windows it is on - a question whose answer changes and
// whose API for asking has itself been deprecated twice.
//
// Called before any window exists, because both calls are refused once one does.
func makeDpiAware() {
	if procSetProcessDpiAwarenessContext.Find() == nil {
		if r, _, _ := procSetProcessDpiAwarenessContext.Call(dpiPerMonitorV2); r != 0 {
			return
		}
	}
	procSetProcessDPIAware.Call()
}

// checkUpdate asks the feed and says the answer in a sentence.
//
// Calls CheckForUpdate directly - the same function the JSON action wraps - so
// there is one network check and one meaning, and the window never renders a
// data structure at somebody.
func (w *collectorWindow) checkUpdate() {
	w.setText(w.result, "Checking for updates...")
	st := CheckForUpdate(w.logf)

	switch {
	case st.Problem != "":
		w.setText(w.result, "Could not check for updates: "+st.Problem)
	case st.Available:
		w.setText(w.result, fmt.Sprintf(
			"Version %s is available - you have %s. %s", st.Latest, st.Current, st.Notes))
	default:
		w.setText(w.result, "You are on the newest version ("+st.Current+").")
	}

	// The feed may also carry the destination. Same handling as everywhere
	// else: remember it, then let precedence decide - local settings still win.
	if st.SendURL != "" && st.SendKey != "" {
		_ = SaveCachedDestination(w.exeDir, st.SendURL, st.SendKey)
	}
	w.refresh()
}
