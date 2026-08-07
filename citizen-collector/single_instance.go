package main

// single_instance.go - one collector, not three.
//
// THE DEFECT THIS FIXES
//
// Double-clicking the icon started ANOTHER collector. The log showed two
// consecutive "UI start" entries, each reporting
//
//	WARNING: hotkey NOT REGISTERED: Hot key is already registered
//
// which means a THIRD instance already held the key. Three copies were
// photographing the same screen, writing into the same folder, competing for
// the same sequence numbers.
//
// The hotkey warning was also actively misleading: it reads as "your hotkey is
// broken" when the real cause is "you are already running". Whoever saw it
// would go looking for a keyboard conflict that does not exist.
//
// HOW THE INSTANCE IS DETECTED
//
// A named mutex, which the kernel owns. It disappears when the process dies -
// including when it is killed - so there is no stale lock file to clean up and
// no window where a crash leaves the program permanently unable to start.
//
// HOW THE EXISTING WINDOW IS FOUND
//
// By PROCESS IDENTITY, never by title alone. This project already learned that
// lesson in findGameWindow: a title is a string any program can set, and
// matching on one picked this project's own terminal as "Star Citizen". So a
// candidate window must belong to a process running the SAME EXECUTABLE as this
// one before it is raised.

import (
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

const (
	// errAlreadyExists is ERROR_ALREADY_EXISTS. CreateMutex still returns a
	// valid handle in this case - the error is how it reports that somebody
	// else created it first.
	errAlreadyExists = 183

	swRestore  = 9
	swMinimize = 6

	// FLASHW_ALL | FLASHW_TIMERNOFG - flash caption and taskbar until focused.
	flashwAll       = 0x00000003
	flashwTimerNoFG = 0x0000000C

	// singleInstanceMutex is per-user, not global: two people on one machine
	// via fast user switching are two legitimate collectors.
	singleInstanceMutex = "Local\\CitizenCollector.SingleInstance"
)

var (
	procCreateMutexW        = modKernel32.NewProc("CreateMutexW")
	procSetForegroundWindow = modUser32.NewProc("SetForegroundWindow")
	procAttachThreadInput   = modUser32.NewProc("AttachThreadInput")
	procBringWindowToTop    = modUser32.NewProc("BringWindowToTop")
	procSwitchToThisWindow  = modUser32.NewProc("SwitchToThisWindow")
	procFlashWindowEx       = modUser32.NewProc("FlashWindowEx")
)

// alreadyRunning reports whether another collector window already owns the
// instance mutex.
//
// The handle is deliberately never closed: it is held for the lifetime of the
// process and released by the kernel on exit, which is what makes a killed
// process leave nothing behind.
func alreadyRunning() bool { return alreadyRunningNamed(singleInstanceMutex) }

// alreadyRunningNamed is the testable form.
//
// The selftest must not use the PRODUCT's mutex name: running it while a real
// collector is open would make the guard correctly report "already running" and
// the check would fail for a reason that has nothing to do with the guard. Same
// collision the hotkey checks hit, and the same fix - a test must not contend
// with the thing it is testing.
func alreadyRunningNamed(mutexName string) bool {
	name, err := syscall.UTF16PtrFromString(mutexName)
	if err != nil {
		// Cannot even build the name. Fail OPEN - starting a second collector
		// is bad, refusing to start the only one is worse.
		return false
	}
	_, _, lastErr := procCreateMutexW.Call(0, 0, uintptr(unsafe.Pointer(name)))
	if errno, ok := lastErr.(syscall.Errno); ok && uintptr(errno) == errAlreadyExists {
		return true
	}
	return false
}

// findExistingWindow returns the collector window belonging to ANOTHER process
// running this same executable, or 0.
func findExistingWindow() HWND {
	self, err := os.Executable()
	if err != nil {
		return 0
	}
	selfBase := strings.ToLower(filepath.Base(self))
	me := uint32(os.Getpid())

	var found HWND
	EnumTopWindows(func(h HWND) bool {
		if found != 0 || !windowVisible(h) {
			return true
		}
		pid := windowPID(h)
		if pid == me {
			return true // our own window, if we somehow have one
		}
		// PROCESS IDENTITY, not the title. A window merely called "Citizen
		// Collector" proves nothing - see the header.
		if !strings.EqualFold(filepath.Base(processImageName(pid)), selfBase) {
			return true
		}
		if windowText(h) == "" {
			return true
		}
		found = h
		return false
	})
	return found
}

// raiseWindow brings an existing collector window to the front.
//
// # WHY THIS IS MORE THAN SetForegroundWindow
//
// Measured, not assumed. A plain ShowWindow+SetForegroundWindow left the window
// where it was: the second launch exited correctly, exactly one process
// remained - and the person still could not see their window, which is the
// entire point of yielding to it.
//
// Windows refuses to let a process that does not own the foreground steal it.
// The documented way round is to attach this thread's input queue to the thread
// that currently owns the foreground; for the duration of the attachment the
// two share focus state and the call is permitted. Detached immediately after,
// because leaving input queues attached couples the two windows' focus
// handling for as long as it lasts.
func raiseWindow(h HWND) {
	if h == 0 {
		return
	}

	fg, _, _ := procGetForegroundWindow.Call()
	me := GetCurrentThreadId()

	var fgThread uintptr
	if fg != 0 {
		fgThread, _, _ = procGetWindowThreadPID.Call(fg, 0)
	}

	attached := false
	if fgThread != 0 && uintptr(me) != fgThread {
		r, _, _ := procAttachThreadInput.Call(uintptr(me), fgThread, 1)
		attached = r != 0
	}

	// Restore first: a minimised window cannot be brought to the front.
	procShowWindow.Call(uintptr(h), swRestore)
	procBringWindowToTop.Call(uintptr(h))
	procSetForegroundWindow.Call(uintptr(h))

	// SwitchToThisWindow is what Alt-Tab uses. AttachThreadInput alone did NOT
	// raise the window in testing - the launch exited correctly and the person
	// still could not see anything - so this is here because the documented
	// route was measured and found insufficient, not as cargo cult.
	procSwitchToThisWindow.Call(uintptr(h), 1)

	if attached {
		procAttachThreadInput.Call(uintptr(me), fgThread, 0)
	}

	// ALWAYS FLASH, and never claim the raise worked.
	//
	// Four documented mechanisms were tried against Windows 11 - SetForeground-
	// Window, BringWindowToTop, AttachThreadInput and SwitchToThisWindow - and
	// the window stayed where it was every time. Windows deliberately refuses a
	// foreground change from a process the user did not just interact with, and
	// every one of those calls reports success regardless.
	//
	// An earlier version sampled GetForegroundWindow straight afterwards, saw
	// the window in the foreground for an instant, and logged "brought its
	// window to the front". An observer checking a moment later found it was
	// not. That is this project's oldest defect wearing a new hat, so the claim
	// is gone: the log now says what was attempted, never what was achieved.
	//
	// Flashing the taskbar button is not a consolation prize. It ALWAYS works,
	// it is what Windows offers an application in exactly this situation, and a
	// flashing icon beats a double-click that appears to do nothing.
	fi := flashwinfo{
		Size:  uint32(unsafe.Sizeof(flashwinfo{})),
		Hwnd:  uintptr(h),
		Flags: flashwAll | flashwTimerNoFG,
		Count: 3,
	}
	procFlashWindowEx.Call(uintptr(unsafe.Pointer(&fi)))
}

// flashwinfo is FLASHWINFO.
type flashwinfo struct {
	Size    uint32
	Hwnd    uintptr
	Flags   uint32
	Count   uint32
	Timeout uint32
}

// windowIsForeground reports whether h currently owns the foreground. Used by
// the raise path to check its own work rather than trust three API calls that
// all report success regardless.
func windowIsForeground(h HWND) bool {
	cur, _, _ := procGetForegroundWindow.Call()
	return cur == uintptr(h) && h != 0
}

// yieldToExistingInstance is the whole policy in one call.
//
// Returns true when this process should exit because another collector is
// already running and has been brought to the front.
//
// A person who double-clicks the icon twice gets their window back. They do not
// get a second collector, and they are not told anything about mutexes.
func yieldToExistingInstance(logf func(string, ...interface{})) bool {
	if !alreadyRunning() {
		return false
	}
	h := findExistingWindow()
	raiseWindow(h)
	if logf != nil {
		if h == 0 {
			logf("another collector is already running, so this launch is exiting - " +
				"but its window could not be found to raise. Look for collector-master.exe in Task Manager.")
		} else {
			logf("another collector is already running - exited instead of starting a second one, " +
				"and flashed its taskbar button. Windows does not reliably allow a new launch to " +
				"steal focus, so the existing window may not come to the front by itself.")
		}
	}
	return true
}
