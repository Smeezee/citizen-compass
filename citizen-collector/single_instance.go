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
	"time"
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
	h, _, lastErr := procCreateMutexW.Call(0, 0, uintptr(unsafe.Pointer(name)))
	if errno, ok := lastErr.(syscall.Errno); ok && uintptr(errno) == errAlreadyExists {
		// SOMEBODY ELSE OWNS IT. Close the handle we were just given.
		//
		// CreateMutex hands back a valid handle even when the object already
		// exists, and holding it keeps the mutex ALIVE for as long as this
		// process lives. Keeping it made the question unaskable a second time:
		// once this process had looked, it was itself a reason for the answer to
		// stay "yes", so it could never observe the real owner letting go.
		if h != 0 {
			procCloseHandle.Call(h)
		}
		return true
	}
	// WE own it now. Keep the handle so the claim can be released deliberately
	// on the restart path - see releaseInstanceLock.
	if h != 0 {
		instanceLock = h
	}
	return false
}

// instanceLock is this process's claim on the single-instance mutex, kept so it
// can be released before handing over to a replacement.
var instanceLock uintptr

// releaseInstanceLock gives up this process's claim, before it exits.
//
// WHY THIS EXISTS. Restarting after an update starts the new exe and lets this
// one go. The new process checks the mutex immediately; this one held it until
// os.Exit. The replacement therefore saw a collector "already running" - the
// very process that had just launched it - found no window to raise because
// this one's was already gone, and exited. Nothing was left running, and the
// only visible evidence was a message telling the person to look in Task
// Manager for a process that was no longer there.
//
// Releasing before the handover closes that window at the source.
func releaseInstanceLock() {
	if instanceLock != 0 {
		procCloseHandle.Call(instanceLock)
		instanceLock = 0
	}
}

// pidIsLiveSibling reports whether pid is a LIVE process running this same
// executable.
//
// Both halves matter. A dead pid cannot be opened, so it answers false. A pid
// that Windows has since recycled for something unrelated answers false too,
// because the image name will not match - which is why this asks what the
// process IS rather than merely whether the number is in use. Guessing from the
// number alone would refuse to start because some unrelated program happened to
// inherit it.
func pidIsLiveSibling(pid int) bool {
	if pid <= 0 {
		return false
	}
	self, err := os.Executable()
	if err != nil {
		return false
	}
	img := processImageName(uint32(pid))
	if img == "" {
		return false
	}
	return strings.EqualFold(filepath.Base(img), filepath.Base(self))
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

	// A HELD LOCK IS NOT PROOF OF A RUNNING COLLECTOR.
	//
	// A process on its way out still holds it. That is exactly what a restart
	// after an update looks like from here: the collector that launched this one
	// is a second away from exiting, and its window has already gone. Refusing
	// on the spot left the person with NOTHING running - strictly worse than the
	// duplicate this guard exists to prevent.
	//
	// So look for the thing that would actually be there: a window belonging to
	// another process running this same executable. If one exists, raise it and
	// stand down - that is a genuine duplicate launch. If none does, give the
	// holder a moment to finish leaving, re-asking the lock each time.
	deadline := time.Now().Add(3 * time.Second)
	for {
		if h := findExistingWindow(); h != 0 {
			raiseWindow(h)
			if logf != nil {
				logf("another collector is already running - exited instead of starting a second one, " +
					"and flashed its taskbar button. Windows does not reliably allow a new launch to " +
					"steal focus, so the existing window may not come to the front by itself.")
			}
			return true
		}
		if !alreadyRunning() {
			// The holder let go. It was handing over, not running.
			if logf != nil {
				logf("the previous collector was still finishing as this one started; " +
					"it has now let go, so this launch is continuing normally.")
			}
			return false
		}
		if time.Now().After(deadline) {
			break
		}
		time.Sleep(200 * time.Millisecond)
	}

	// Still held, still no window, after three seconds. Say what is true and
	// name the program that is actually running, rather than a hardcoded one.
	if logf != nil {
		self, _ := os.Executable()
		logf("another collector is already holding the single-instance lock and has no "+
			"window to raise, so this launch is exiting. Look for %s in Task Manager; "+
			"if nothing is there, the lock is held by a process that is still shutting "+
			"down and starting again in a few seconds will work.",
			filepath.Base(self))
	}
	return true
}
