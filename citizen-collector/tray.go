package main

// tray.go - a visible sign of life in the notification area.
//
// # THE RULE THIS SATISFIES
//
// "No silent operation." A collector that is watching must be visibly watching.
// The `alive:` heartbeat in the log satisfies the letter of that and not the
// spirit: nobody reads a log file while flying. Sleven has no speakers, so
// audio was never an option. That leaves the tray.
//
// # THIS FILE IS BUILT TO FAIL WITHOUT CONSEQUENCE
//
// It is Win32 message-loop code and it has never run. It is going into a build
// that is about to be tested for other things, so the ONE property that matters
// more than the feature is that a failure here cannot take anything else down:
//
//   - every Win32 call is checked, and any failure returns quietly
//   - it runs on its own locked OS thread with its own hidden window, so it
//     shares no message queue with the webview
//   - a panic is recovered and logged
//   - the collector never waits on it and never asks it a question
//
// Worst case is no icon. That is a cosmetic loss. The alternative - an untested
// message pump wired into the main window on the day everything else gets
// tested - risks making a good build look broken for a reason nobody would
// think to look for.

import (
	"os"
	"runtime"
	"sync"
	"sync/atomic"
	"syscall"
	"unsafe"
)

var (
	modShell32        = syscall.NewLazyDLL("shell32.dll")
	procShellNotifyIw = modShell32.NewProc("Shell_NotifyIconW")

	// GetMessageW / TranslateMessage / DispatchMessageW already exist in
	// winapi.go. Redeclaring them here compiled as a duplicate and the compiler
	// said so - which is the good version of the two-copies problem, since the
	// bad version is two copies that both compile and then drift.
	procRegisterClassExW  = modUser32.NewProc("RegisterClassExW")
	procDefWindowProcW    = modUser32.NewProc("DefWindowProcW")
	procLoadIconW         = modUser32.NewProc("LoadIconW")
	procCreatePopupMenu   = modUser32.NewProc("CreatePopupMenu")
	procDestroyMenu       = modUser32.NewProc("DestroyMenu")
	procAppendMenuW       = modUser32.NewProc("AppendMenuW")
	procTrackPopupMenu    = modUser32.NewProc("TrackPopupMenu")
	procGetCursorPos      = modUser32.NewProc("GetCursorPos")
	procExtractIconExW    = modShell32.NewProc("ExtractIconExW")
	procSendMessageW      = modUser32.NewProc("SendMessageW")
	procSendNotifyMessage = modUser32.NewProc("SendNotifyMessageW")
	procPostMessageW      = modUser32.NewProc("PostMessageW")
)

const (
	nimAdd     = 0x00000000
	nimModify  = 0x00000001
	nimDelete  = 0x00000002
	nifIcon    = 0x00000002
	nifMessage = 0x00000001

	// The message the shell posts to our window when somebody clicks the icon.
	// Anything from WM_APP up is ours to define.
	wmTrayCallback = 0x0400 + 1 // WM_APP + 1

	// wmAppOpenWindow asks THIS thread to create the window.
	//
	// A window belongs to the thread that creates it, and only a thread with a
	// message loop can service one. The tray thread has both, so startup posts
	// this rather than creating the window on whatever goroutine it happens to
	// be running on - which is exactly the mistake that produced a window with
	// no pump.
	wmAppOpenWindow = 0x0400 + 2

	wmRButtonUp = 0x0205
	wmLButtonUp = 0x0202
	wmCommand   = 0x0111

	// Menu command ids. Small integers, ours alone, because this window has no
	// other menu to collide with.
	cmdSendNow      = 1001
	cmdExit         = 1002
	cmdCaptureNow   = 1003
	cmdOpenPictures = 1004
	cmdOpenWindow   = 1005
	cmdRevert       = 1006

	mfString       = 0x00000000
	tpmRightAlign  = 0x0008
	tpmBottomAlign = 0x0020
	tpmRightButton = 0x0002
	nifTip         = 0x00000004

	idiApplication = 32512

	// HWND_MESSAGE. Passing this as the parent makes a MESSAGE-ONLY window:
	// invisible, never in the taskbar or Alt-Tab, and impossible for a person
	// to close. It still receives the notification-area callbacks, which is the
	// only thing this window is for.
	//
	// THE DEFECT THIS FIXES. The parent was 0, which does not make a hidden
	// window - it makes an ordinary top-level one that happens to have no size
	// and no content. Sleven saw it as a second, empty black window and took it
	// for a command prompt. Closing it delivered WM_CLOSE to the loop below,
	// which is how this thread is asked to shut down, so closing that stray box
	// took the whole collector with it.
	//
	// WS_EX_TOOLWINDOW: no taskbar button, no Alt-Tab entry.
	wsExToolWindow = 0x00000080
	wmClose        = 0x0010
)

// notifyIconData is NOTIFYICONDATAW at its VERSION 1 size, and the size is the
// whole point.
//
// # WHY THE TRAY ICON NEVER APPEARED - FOUND BY REVIEW 2026-08-08
//
// The field layout was already correct. The size was not. SzTip used to be
// [128]uint16, which makes unsafe.Sizeof 296, and the comment here claimed a
// short struct was fine because CbSize declares the version.
//
// That is half true and the missing half is fatal: Shell_NotifyIcon accepts
// only the four PUBLISHED version sizes, which on x64 are
//
//	168   V1   (szTip[64])
//	952   V2
//	968   V3
//	976   current
//
// 296 is none of them - it is just an offset partway through the struct. So
// NIM_ADD returned FALSE on every launch, the code dutifully reported "the
// notification area refused the icon", and the fail-safe design meant nothing
// else broke and nobody had a reason to look.
//
// szTip is now [64]uint16, which makes Sizeof exactly 168 - a real version. 63
// characters of tooltip is more than enough for "Citizen Collector - 41
// captures, last: burst".
type notifyIconData struct {
	CbSize           uint32
	HWnd             uintptr
	UID              uint32
	UFlags           uint32
	UCallbackMessage uint32
	HIcon            uintptr
	SzTip            [64]uint16
}

type msgStruct struct {
	HWnd    uintptr
	Message uint32
	WParam  uintptr
	LParam  uintptr
	Time    uint32
	Pt      struct{ X, Y int32 }
}

type wndClassEx struct {
	CbSize        uint32
	Style         uint32
	LpfnWndProc   uintptr
	CbClsExtra    int32
	CbWndExtra    int32
	HInstance     uintptr
	HIcon         uintptr
	HCursor       uintptr
	HbrBackground uintptr
	LpszMenuName  *uint16
	LpszClassName *uint16
	HIconSm       uintptr
}

// WHICH PATH THE CLICK ARRIVED ON.
//
// Not decoration. "The handler is wired" has been said about this three times
// while the icon did nothing on screen, and each time it was reasoning from the
// source. These are counted at the two places a notification-area message can
// possibly arrive, so the answer is a number that can be printed - see
// -tray-probe, which drives both paths and reports them.
var (
	trayCallbackViaWndProc int64
	trayCallbackViaLoop    int64
	trayCommandViaWndProc  int64
	trayMenuShown          int64
	trayLeftOpenedWindow   int64
)

// trayHandle is what the collector holds. Every method on it is safe to call
// on a zero value, so no caller ever has to check whether the tray came up.
type trayHandle struct {
	// The menu's actions. Injected rather than called directly so this file
	// knows nothing about exporting, capturing or reverting - and so the
	// selftest can prove the menu is wired without doing any of it.
	//
	// THE TRAY IS HOME. Every one of these has to work when the window does
	// not, which is the whole reason they live here.
	onSend         func()
	onCaptureNow   func()
	onOpenPictures func()
	onOpenWindow   func()
	onRevert       func()

	// exited closes when the person chooses Exit, so the program can wait on
	// the one surface that is always present rather than on a window that may
	// never have rendered.
	exited chan struct{}

	mu   sync.Mutex
	hwnd uintptr
	ok   bool
	tip  string
}

// StartTray puts an icon in the notification area and returns a handle.
//
// Returns a usable (dead) handle on ANY failure. The caller is not told to care.
func StartTray(logf func(string, ...interface{})) *trayHandle {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	t := &trayHandle{exited: make(chan struct{})}
	ready := make(chan bool, 1)

	go func() {
		defer func() {
			if r := recover(); r != nil {
				logf("tray: not available (%v) - the collector is unaffected, and the "+
					"log heartbeat still says whether it is alive", r)
				select {
				case ready <- false:
				default:
				}
			}
		}()
		// Its OWN thread and its OWN queue. A message pump belongs to the
		// thread that created its window, and sharing one with the webview is
		// how two working things break each other.
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()

		className, _ := syscall.UTF16PtrFromString("CitizenCollectorTray")
		// THE WINDOW PROCEDURE HANDLES THE TRAY MESSAGES. It used to hand
		// every message straight to DefWindowProc and let the message LOOP
		// below look for them, which is why right-clicking the icon has never
		// opened a menu on any build.
		//
		// A message that is SENT is not a message that is POSTED. GetMessage
		// returns posted messages; sent messages are delivered directly to the
		// window procedure while the thread waits inside GetMessage, and never
		// appear in the MSG it hands back. The notification area sends, and
		// TrackPopupMenu SENDS its WM_COMMAND too - so the loop's checks could
		// only ever have fired for messages this program posted to itself
		// (wmAppOpenWindow, wmClose), which is exactly the set that worked.
		//
		// Counted as well as handled: trayCallbackViaWndProc and
		// trayCallbackViaLoop say which path a real click arrived on, so the
		// next report of this is a number instead of an argument.
		wndProc := syscall.NewCallback(func(h uintptr, msg uint32, w, l uintptr) uintptr {
			switch msg {
			case wmTrayCallback:
				atomic.AddInt64(&trayCallbackViaWndProc, 1)
				// RIGHT OPENS THE MENU, LEFT OPENS THE WINDOW.
				//
				// Both used to open the menu, on the argument that a left-click
				// does nothing in most programs so somebody hunting for SEND
				// would try it first. That argument was made when the window
				// was the main surface and the tray was a shortcut to it. It is
				// now the other way round - version one makes the window
				// optional - and what people expect from a tray icon is left
				// for the program, right for its menu. Doing something else,
				// however defensible, is one more thing to learn.
				switch uint32(l) & 0xFFFF {
				case wmRButtonUp:
					t.showMenu(logf)
				case wmLButtonUp:
					atomic.AddInt64(&trayLeftOpenedWindow, 1)
					if t.onOpenWindow != nil {
						t.onOpenWindow()
					}
				}
				return 0
			case wmCommand:
				atomic.AddInt64(&trayCommandViaWndProc, 1)
				if t.handleCommand(uint32(w) & 0xFFFF) {
					return 0
				}
			}
			r, _, _ := procDefWindowProcW.Call(h, uintptr(msg), w, l)
			return r
		})
		wc := wndClassEx{
			CbSize:        uint32(unsafe.Sizeof(wndClassEx{})),
			LpfnWndProc:   wndProc,
			LpszClassName: className,
		}
		if r, _, _ := procRegisterClassExW.Call(uintptr(unsafe.Pointer(&wc))); r == 0 {
			logf("tray: could not register its window class - no icon. Everything " +
				"else is unaffected.")
			ready <- false
			return
		}
		// INVISIBLE, NOT MESSAGE-ONLY.
		//
		// WS_EX_TOOLWINDOW keeps it out of Alt-Tab and the taskbar, and it is
		// never shown - no WS_VISIBLE and no ShowWindow call - so there is
		// nothing on screen for anybody to find or close.
		//
		// It is deliberately NOT parented to HWND_MESSAGE: a message-only
		// window cannot take the foreground, and TrackPopupMenu wants an owner
		// that can.
		//
		// THAT IS NOT WHY THE MENU NEVER OPENED, and the comment that used to
		// stand here said it was. The menu has never opened on any build,
		// including ones made before HWND_MESSAGE appeared in this file, so the
		// revert of 2026-08-15 cannot have been the fix. The real cause was the
		// window procedure discarding every SENT message - see the note on
		// wndProc above, and docs/ERRATUM_tray-right-click-was-never-delivered
		// -2026-08-16.md.
		hwnd, _, _ := procCreateWindowExW.Call(wsExToolWindow,
			uintptr(unsafe.Pointer(className)), uintptr(unsafe.Pointer(className)),
			wsPopup, 0, 0, 0, 0, 0, 0, 0, 0)
		if hwnd == 0 {
			logf("tray: could not create its hidden window - no icon. Everything " +
				"else is unaffected.")
			ready <- false
			return
		}
		// OUR ICON, NOT WINDOWS' DEFAULT.
		//
		// This was LoadIcon(NULL, IDI_APPLICATION) - the generic white-and-blue
		// window glyph every unstyled program gets. The collector's own icon is
		// embedded in the exe and was already sitting there unused, which is the
		// same defect as the shortcut icon fixed earlier today, in a second
		// place nobody had looked at.
		hIcon := trayIcon(logf)

		nid := notifyIconData{
			CbSize: uint32(unsafe.Sizeof(notifyIconData{})),
			HWnd:   hwnd,
			UID:    1,
			// NIF_MESSAGE, so clicks reach us at all. Without it the icon is
			// decoration: it shows a tooltip and nothing can be done with it,
			// which is what it was before today.
			UFlags:           nifIcon | nifTip | nifMessage,
			UCallbackMessage: wmTrayCallback,
			HIcon:            hIcon,
		}
		copyTip(&nid, "Citizen Collector - starting")
		if r, _, _ := procShellNotifyIw.Call(nimAdd, uintptr(unsafe.Pointer(&nid))); r == 0 {
			procDestroyWindow.Call(hwnd)
			logf("tray: the notification area refused the icon - no icon. Everything " +
				"else is unaffected.")
			ready <- false
			return
		}

		t.hwnd = hwnd
		t.ok = true
		logf("tray: icon added - hover it to see what the collector is doing")
		ready <- true

		var m msgStruct
		for {
			r, _, _ := procGetMessageW.Call(uintptr(unsafe.Pointer(&m)), 0, 0, 0)
			if int32(r) <= 0 {
				break
			}
			// WM_CLOSE is how Stop() asks this thread to finish. Handling it
			// here means the window is destroyed by its owner, which is the
			// only thread allowed to do it.
			//
			// A PERSON CANNOT SEND THIS. The window is never shown and has no
			// frame to close, so this arrives only from Stop() or from Exit on
			// the menu. (It is NOT parented to HWND_MESSAGE - an earlier
			// version of this comment said it was.)
			//
			// MATCHED ON OUR OWN WINDOW. The collector window lives on this
			// thread too now, and closing it must not stop the message loop
			// that every other window here depends on.
			if m.Message == wmClose && m.HWnd == t.hwnd {
				break
			}

			// CREATE THE WINDOW ON THIS THREAD. See wmAppOpenWindow.
			if m.Message == wmAppOpenWindow && m.HWnd == t.hwnd {
				if t.onOpenWindow != nil {
					t.onOpenWindow()
				}
				continue
			}

			// A CLICK ON THE ICON, ARRIVING THE OTHER WAY.
			//
			// The notification area SENDS, so in practice this branch never
			// fires for a real click - it is the window procedure above that
			// does. It is kept, and counted, because a posted callback is still
			// a legal way for one to arrive and because the counts are how the
			// next argument about this gets settled with a number.
			//
			// Right opens the menu, left opens the window. Same rule as above,
			// and the two are the same rule on purpose: a click must not mean
			// different things depending on how Windows chose to deliver it.
			if m.Message == wmTrayCallback && m.HWnd == t.hwnd {
				atomic.AddInt64(&trayCallbackViaLoop, 1)
				switch uint32(m.LParam) & 0xFFFF {
				case wmRButtonUp:
					t.showMenu(logf)
					continue
				case wmLButtonUp:
					atomic.AddInt64(&trayLeftOpenedWindow, 1)
					if t.onOpenWindow != nil {
						t.onOpenWindow()
					}
					continue
				}
			}

			// OUR MENU ONLY. The window's buttons send WM_COMMAND straight to
			// their own parent rather than through the queue, so they never
			// arrive here - but matching on the window makes that a fact rather
			// than a happy accident.
			// A POSTED WM_COMMAND. Menu clicks are SENT and reach the window
			// procedure instead, but the same handler runs either way.
			if m.Message == wmCommand && m.HWnd == t.hwnd {
				if t.handleCommand(uint32(m.WParam) & 0xFFFF) {
					continue
				}
			}
			procTranslateMessage.Call(uintptr(unsafe.Pointer(&m)))
			procDispatchMessageW.Call(uintptr(unsafe.Pointer(&m)))
		}
		// Remove the icon on the way out, or Windows leaves a ghost that only
		// disappears when somebody hovers over it.
		procShellNotifyIw.Call(nimDelete, uintptr(unsafe.Pointer(&nid)))
		procDestroyWindow.Call(hwnd)
	}()

	<-ready
	return t
}

func copyTip(nid *notifyIconData, s string) {
	u, err := syscall.UTF16FromString(s)
	if err != nil {
		return
	}
	if len(u) > len(nid.SzTip) {
		u = u[:len(nid.SzTip)-1]
		u = append(u, 0)
	}
	for i := range nid.SzTip {
		nid.SzTip[i] = 0
	}
	copy(nid.SzTip[:], u)
}

// SetStatus updates the hover text. Safe on a dead handle, safe to call often.
func (t *trayHandle) SetStatus(s string) {
	if t == nil {
		return
	}
	// Called from the auto loop AND from the Capture-now button, which run on
	// different threads. Without this they race on tip and ok, and can race
	// Stop() closing the window out from under a live update.
	t.mu.Lock()
	defer t.mu.Unlock()
	if !t.ok || s == t.tip {
		return
	}
	t.tip = s
	nid := notifyIconData{
		CbSize: uint32(unsafe.Sizeof(notifyIconData{})),
		HWnd:   t.hwnd,
		UID:    1,
		UFlags: nifTip,
	}
	copyTip(&nid, s)
	procShellNotifyIw.Call(nimModify, uintptr(unsafe.Pointer(&nid)))
}

// Stop removes the icon. Safe on a dead handle.
// Stop removes the icon. Safe on a dead handle, safe to call twice.
//
// It POSTS rather than destroys. A window may only be destroyed by the thread
// that created it, and this is called from the UI thread while the window
// belongs to the tray's own locked thread - DestroyWindow would fail with
// access denied, the message loop would never end, and the thread would leak.
// WM_CLOSE reaches the owning thread, which ends its own loop and cleans up.
func (t *trayHandle) Stop() {
	if t == nil {
		return
	}
	t.mu.Lock()
	defer t.mu.Unlock()
	if !t.ok {
		return
	}
	t.ok = false
	procPostMessageW.Call(t.hwnd, wmClose, 0, 0)
}

// trayIcon returns the collector's own icon, falling back to the system default
// only if our own cannot be read.
//
// # WHY EXTRACT FROM THE EXE RATHER THAN LOAD A RESOURCE ID
//
// The icon is embedded by the build, and the resource id it lands on is decided
// by the toolchain rather than by us. Extracting index 0 from our own file asks
// for "the first icon in this program", which is a stable question with a stable
// answer, instead of hardcoding a number that a change of build tooling could
// silently move.
//
// # WHY THE SMALL ONE
//
// The notification area draws at small-icon size. Handing it the large icon
// gets a downscaled, muddy version of the right picture - which looks like a
// rendering bug rather than a wrong call, and is therefore worse than the
// default icon it replaced.
//
// A FALLBACK, NOT A FAILURE. A missing icon is cosmetic; refusing to show a
// tray icon at all because the pretty one could not be read would trade a small
// loss for a real one. It says so in the log rather than doing it quietly.
func trayIcon(logf func(string, ...interface{})) uintptr {
	if exe, err := os.Executable(); err == nil {
		if p, err := syscall.UTF16PtrFromString(exe); err == nil {
			var large, small uintptr
			n, _, _ := procExtractIconExW.Call(
				uintptr(unsafe.Pointer(p)), 0,
				uintptr(unsafe.Pointer(&large)),
				uintptr(unsafe.Pointer(&small)), 1)
			if n > 0 && small != 0 {
				return small
			}
			if n > 0 && large != 0 {
				return large
			}
		}
	}
	if logf != nil {
		logf("tray: could not read this program's own icon, so the notification " +
			"area is showing the generic Windows one. Cosmetic only.")
	}
	h, _, _ := procLoadIconW.Call(0, uintptr(idiApplication))
	return h
}

// setWindowIcon gives a window this program's own icon.
//
// WM_SETICON with BOTH sizes. Windows asks for the small icon for the title bar
// and the large one for Alt-Tab and the taskbar; setting only one leaves the
// other as the default, which looks like a half-finished job rather than a
// missing call.
//
// Never fatal. A window with the wrong picture still works.
func setWindowIcon(hwnd uintptr, logf func(string, ...interface{})) {
	if hwnd == 0 {
		return
	}
	exe, err := os.Executable()
	if err != nil {
		return
	}
	p, err := syscall.UTF16PtrFromString(exe)
	if err != nil {
		return
	}
	var large, small uintptr
	n, _, _ := procExtractIconExW.Call(uintptr(unsafe.Pointer(p)), 0,
		uintptr(unsafe.Pointer(&large)), uintptr(unsafe.Pointer(&small)), 1)
	if n == 0 || (large == 0 && small == 0) {
		if logf != nil {
			logf("window: could not read this program's own icon - the title bar " +
				"will show the generic Windows one. Cosmetic only.")
		}
		return
	}
	const (
		wmSetIcon    = 0x0080
		iconSmallSet = 0
		iconBigSet   = 1
	)
	if small != 0 {
		procSendMessageW.Call(hwnd, wmSetIcon, iconSmallSet, small)
	}
	if large != 0 {
		procSendMessageW.Call(hwnd, wmSetIcon, iconBigSet, large)
	}
}

// handleCommand runs one menu choice. Shared by both delivery paths.
//
// TrackPopupMenu SENDS its WM_COMMAND to the owner window, so the copy of this
// switch that lived in the message loop could never run for a menu click. It is
// one function now, called from the window procedure, and the loop calls the
// same one - so the two cannot drift apart the way they already had.
func (t *trayHandle) handleCommand(id uint32) bool {
	if t == nil {
		return false
	}
	switch id {
	case cmdSendNow:
		// ON ITS OWN GOROUTINE. Packaging and uploading a session takes
		// minutes; doing it on this thread would freeze the message loop, and a
		// frozen loop means the tooltip stops updating and the menu stops
		// opening - the program would look hung at exactly the moment it is
		// working hardest.
		go t.run(t.onSend)
	case cmdCaptureNow:
		go t.run(t.onCaptureNow)
	case cmdOpenPictures:
		go t.run(t.onOpenPictures)
	case cmdOpenWindow:
		// NOT on a goroutine. A window has to be created by a thread with a
		// message loop, and this is one.
		if t.onOpenWindow != nil {
			t.onOpenWindow()
		}
	case cmdRevert:
		go t.run(t.onRevert)
	case cmdExit:
		t.signalExit()
		// Asks the loop on this thread to finish, rather than returning from
		// somewhere inside a sent message and leaving the icon behind.
		procPostMessageW.Call(t.hwnd, wmClose, 0, 0)
	default:
		return false
	}
	return true
}

// showMenu opens the notification-area menu.
//
// # THE SetForegroundWindow CALL IS NOT OPTIONAL
//
// Documented Windows behaviour: a popup menu belonging to a window that is not
// in the foreground never receives the click that dismisses it, so it stays on
// screen until the next click somewhere else. Every tray program does this and
// every one that forgot has the same bug report.
func (t *trayHandle) showMenu(logf func(string, ...interface{})) {
	if t == nil || t.hwnd == 0 {
		return
	}
	menu, _, _ := procCreatePopupMenu.Call()
	if menu == 0 {
		return
	}
	defer procDestroyMenu.Call(menu)

	add := func(id uintptr, text string) {
		p, err := syscall.UTF16PtrFromString(text)
		if err != nil {
			return
		}
		procAppendMenuW.Call(menu, mfString, id, uintptr(unsafe.Pointer(p)))
	}
	add(cmdOpenWindow, "Open Citizen Collector")
	add(cmdSendNow, "Send my data now")
	add(cmdCaptureNow, "Take a picture now")
	add(cmdOpenPictures, "Open the pictures folder")
	if HasPreviousBuild() {
		// ONLY WHEN THERE IS SOMETHING TO GO BACK TO. An item that always
		// exists and usually fails teaches people to ignore it.
		add(cmdRevert, "Go back to the previous version")
	}
	add(cmdExit, "Exit Citizen Collector")

	var pt struct{ X, Y int32 }
	procGetCursorPos.Call(uintptr(unsafe.Pointer(&pt)))

	// See the note above - without this the menu will not close.
	procSetForegroundWindow.Call(t.hwnd)
	atomic.AddInt64(&trayMenuShown, 1)
	procTrackPopupMenu.Call(menu,
		tpmRightAlign|tpmBottomAlign|tpmRightButton,
		uintptr(pt.X), uintptr(pt.Y), 0, t.hwnd, 0)

	// Documented workaround: post a null message so the menu dismisses properly
	// the first time rather than on the click after.
	procPostMessageW.Call(t.hwnd, 0, 0, 0)
}

// run calls a menu action if one is wired, so a missing action is a no-op
// rather than a crash in somebody's notification area.
func (t *trayHandle) run(f func()) {
	if f != nil {
		f()
	}
}

func (t *trayHandle) signalExit() {
	if t == nil || t.exited == nil {
		return
	}
	select {
	case <-t.exited:
	default:
		close(t.exited)
	}
}

// WaitForExit blocks until Exit is chosen from the menu.
//
// THE TRAY OWNS THE PROGRAM'S LIFETIME now that the window is optional. A
// program whose lifetime was owned by a window would stop existing the moment
// somebody closed it by reflex - and for a collector that runs while you play,
// that is the opposite of what it is for.
func (t *trayHandle) WaitForExit() {
	if t == nil || t.exited == nil {
		return
	}
	<-t.exited
}

// RequestOpenWindow asks the tray's thread to create or raise the window.
//
// POSTED, NOT CALLED. The caller is almost never the UI thread, and a window
// created on a thread that does not pump messages is a window that renders once
// and then ignores everything - which is precisely the defect this replaced.
func (t *trayHandle) RequestOpenWindow() bool {
	if t == nil || t.hwnd == 0 {
		return false
	}
	procPostMessageW.Call(t.hwnd, wmAppOpenWindow, 0, 0)
	return true
}
