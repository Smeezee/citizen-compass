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
	"runtime"
	"sync"
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
	procRegisterClassExW = modUser32.NewProc("RegisterClassExW")
	procDefWindowProcW   = modUser32.NewProc("DefWindowProcW")
	procLoadIconW        = modUser32.NewProc("LoadIconW")
	procPostMessageW     = modUser32.NewProc("PostMessageW")
)

const (
	nimAdd    = 0x00000000
	nimModify = 0x00000001
	nimDelete = 0x00000002
	nifIcon   = 0x00000002
	nifTip    = 0x00000004

	idiApplication = 32512
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

// trayHandle is what the collector holds. Every method on it is safe to call
// on a zero value, so no caller ever has to check whether the tray came up.
type trayHandle struct {
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
	t := &trayHandle{}
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
		wndProc := syscall.NewCallback(func(h uintptr, msg uint32, w, l uintptr) uintptr {
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
		hwnd, _, _ := procCreateWindowExW.Call(0,
			uintptr(unsafe.Pointer(className)), uintptr(unsafe.Pointer(className)),
			0, 0, 0, 0, 0, 0, 0, 0, 0)
		if hwnd == 0 {
			logf("tray: could not create its hidden window - no icon. Everything " +
				"else is unaffected.")
			ready <- false
			return
		}
		hIcon, _, _ := procLoadIconW.Call(0, uintptr(idiApplication))

		nid := notifyIconData{
			CbSize: uint32(unsafe.Sizeof(notifyIconData{})),
			HWnd:   hwnd,
			UID:    1,
			UFlags: nifIcon | nifTip,
			HIcon:  hIcon,
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
			if m.Message == wmClose {
				break
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
