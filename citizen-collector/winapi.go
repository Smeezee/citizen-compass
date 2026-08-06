package main

// winapi.go - the raw Win32 / COM / WinRT plumbing shared by every capture
// backend.
//
// WHY THIS IS HAND-ROLLED
//   CGO_ENABLED=0 and there is no C compiler on this machine, so C++/WinRT is
//   not available and neither is any cgo-based capture library. Every COM call
//   below is a manual vtable dispatch through syscall.SyscallN. That is the
//   price of "single static binary, no installer".
//
// CALLING CONVENTION
//   A COM object is a pointer to a struct whose first field is a pointer to a
//   vtable of function pointers. Calling method N means:
//       syscall.SyscallN(vtbl.MethodN, uintptr(thisPointer), args...)
//   The `this` pointer is ALWAYS the first argument. Getting the vtable slot
//   order wrong does not fail to compile - it calls the wrong function with the
//   wrong arguments, so the vtable layouts below are written in full and in
//   order, including methods this program never calls, rather than indexed
//   numerically.

import (
	"fmt"
	"syscall"
	"unsafe"
)

// ---------------------------------------------------------------------------
// DLLs
// ---------------------------------------------------------------------------

var (
	modUser32   = syscall.NewLazyDLL("user32.dll")
	modKernel32 = syscall.NewLazyDLL("kernel32.dll")
	modGdi32    = syscall.NewLazyDLL("gdi32.dll")
	modD3D11    = syscall.NewLazyDLL("d3d11.dll")
	modCombase  = syscall.NewLazyDLL("combase.dll")
	modOle32    = syscall.NewLazyDLL("ole32.dll")

	procRegisterHotKey     = modUser32.NewProc("RegisterHotKey")
	procUnregisterHotKey   = modUser32.NewProc("UnregisterHotKey")
	procGetMessageW        = modUser32.NewProc("GetMessageW")
	procPeekMessageW       = modUser32.NewProc("PeekMessageW")
	procTranslateMessage   = modUser32.NewProc("TranslateMessage")
	procDispatchMessageW   = modUser32.NewProc("DispatchMessageW")
	procFindWindowW        = modUser32.NewProc("FindWindowW")
	procEnumWindows        = modUser32.NewProc("EnumWindows")
	procGetWindowTextW     = modUser32.NewProc("GetWindowTextW")
	procGetClassNameW      = modUser32.NewProc("GetClassNameW")
	procIsWindowVisible    = modUser32.NewProc("IsWindowVisible")
	procGetWindowRect      = modUser32.NewProc("GetWindowRect")
	procGetClientRect      = modUser32.NewProc("GetClientRect")
	procGetWindowDC        = modUser32.NewProc("GetWindowDC")
	procGetDC              = modUser32.NewProc("GetDC")
	procReleaseDC          = modUser32.NewProc("ReleaseDC")
	procPrintWindow        = modUser32.NewProc("PrintWindow")
	procGetForegroundWindow = modUser32.NewProc("GetForegroundWindow")
	procGetWindowThreadPID = modUser32.NewProc("GetWindowThreadProcessId")
	procSetProcessDPIAware = modUser32.NewProc("SetProcessDPIAware")

	// Used by --auto to hide the console it was launched from. See
	// hideConsole() in auto.go for why hidden and not freed.
	procShowWindow = modUser32.NewProc("ShowWindow")

	// Used by the process-lock selftest to CREATE the condition it tests -
	// a real top-level window titled "Star Citizen" that does not belong to
	// StarCitizen.exe. See process_lock_selftest.go.
	procCreateWindowExW = modUser32.NewProc("CreateWindowExW")
	procDestroyWindow   = modUser32.NewProc("DestroyWindow")

	procBeep            = modKernel32.NewProc("Beep")
	procQueryFullProcessImageNameW = modKernel32.NewProc("QueryFullProcessImageNameW")
	procOpenProcess     = modKernel32.NewProc("OpenProcess")
	procCloseHandle     = modKernel32.NewProc("CloseHandle")
	procGetConsoleWindow = modKernel32.NewProc("GetConsoleWindow")

	procCreateCompatibleDC     = modGdi32.NewProc("CreateCompatibleDC")
	procCreateCompatibleBitmap = modGdi32.NewProc("CreateCompatibleBitmap")
	procSelectObject           = modGdi32.NewProc("SelectObject")
	procDeleteObject           = modGdi32.NewProc("DeleteObject")
	procDeleteDC               = modGdi32.NewProc("DeleteDC")
	procBitBlt                 = modGdi32.NewProc("BitBlt")
	procGetDIBits              = modGdi32.NewProc("GetDIBits")

	procD3D11CreateDevice = modD3D11.NewProc("D3D11CreateDevice")
	procCreateDirect3D11DeviceFromDXGIDevice = modD3D11.NewProc("CreateDirect3D11DeviceFromDXGIDevice")

	procRoInitialize            = modCombase.NewProc("RoInitialize")
	procRoGetActivationFactory  = modCombase.NewProc("RoGetActivationFactory")
	procWindowsCreateString     = modCombase.NewProc("WindowsCreateString")
	procWindowsDeleteString     = modCombase.NewProc("WindowsDeleteString")

	procCoInitializeEx = modOle32.NewProc("CoInitializeEx")
)

// ---------------------------------------------------------------------------
// basic types
// ---------------------------------------------------------------------------

type HWND uintptr
type HRESULT int32

type RECT struct{ Left, Top, Right, Bottom int32 }

func (r RECT) Width() int32  { return r.Right - r.Left }
func (r RECT) Height() int32 { return r.Bottom - r.Top }

type POINT struct{ X, Y int32 }

type MSG struct {
	Hwnd    HWND
	Message uint32
	WParam  uintptr
	LParam  uintptr
	Time    uint32
	Pt      POINT
}

type GUID struct {
	Data1 uint32
	Data2 uint16
	Data3 uint16
	Data4 [8]byte
}

func (g GUID) String() string {
	return fmt.Sprintf("{%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X}",
		g.Data1, g.Data2, g.Data3, g.Data4[0], g.Data4[1],
		g.Data4[2], g.Data4[3], g.Data4[4], g.Data4[5], g.Data4[6], g.Data4[7])
}

func succeeded(hr uintptr) bool { return HRESULT(uint32(hr)) >= 0 }

func hrErr(what string, hr uintptr) error {
	return fmt.Errorf("%s failed: hr=0x%08X", what, uint32(hr))
}

// ---------------------------------------------------------------------------
// COM base
// ---------------------------------------------------------------------------

type IUnknownVtbl struct {
	QueryInterface uintptr
	AddRef         uintptr
	Release        uintptr
}

type IUnknown struct{ Vtbl *IUnknownVtbl }

func (u *IUnknown) Release() {
	if u == nil {
		return
	}
	syscall.SyscallN(u.Vtbl.Release, uintptr(unsafe.Pointer(u)))
}

func (u *IUnknown) QueryInterface(iid *GUID) (unsafe.Pointer, error) {
	var out unsafe.Pointer
	hr, _, _ := syscall.SyscallN(u.Vtbl.QueryInterface,
		uintptr(unsafe.Pointer(u)),
		uintptr(unsafe.Pointer(iid)),
		uintptr(unsafe.Pointer(&out)))
	if !succeeded(hr) {
		return nil, hrErr("QueryInterface"+iid.String(), hr)
	}
	return out, nil
}

// releaseAny releases anything that is COM-shaped, given as a raw pointer.
func releaseAny(p unsafe.Pointer) {
	if p == nil {
		return
	}
	(*IUnknown)(p).Release()
}

// ---------------------------------------------------------------------------
// window helpers
// ---------------------------------------------------------------------------

func utf16Ptr(s string) *uint16 {
	p, err := syscall.UTF16PtrFromString(s)
	if err != nil {
		return nil
	}
	return p
}

func GetWindowRectOf(h HWND) (RECT, error) {
	var r RECT
	ok, _, err := syscall.SyscallN(procGetWindowRect.Addr(), uintptr(h), uintptr(unsafe.Pointer(&r)))
	if ok == 0 {
		return r, fmt.Errorf("GetWindowRect: %v", err)
	}
	return r, nil
}

func GetClientRectOf(h HWND) (RECT, error) {
	var r RECT
	ok, _, err := syscall.SyscallN(procGetClientRect.Addr(), uintptr(h), uintptr(unsafe.Pointer(&r)))
	if ok == 0 {
		return r, fmt.Errorf("GetClientRect: %v", err)
	}
	return r, nil
}

func windowText(h HWND) string {
	buf := make([]uint16, 512)
	n, _, _ := syscall.SyscallN(procGetWindowTextW.Addr(), uintptr(h),
		uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
	return syscall.UTF16ToString(buf[:n])
}

func windowClass(h HWND) string {
	buf := make([]uint16, 256)
	n, _, _ := syscall.SyscallN(procGetClassNameW.Addr(), uintptr(h),
		uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
	return syscall.UTF16ToString(buf[:n])
}

func windowVisible(h HWND) bool {
	r, _, _ := syscall.SyscallN(procIsWindowVisible.Addr(), uintptr(h))
	return r != 0
}

func windowPID(h HWND) uint32 {
	var pid uint32
	syscall.SyscallN(procGetWindowThreadPID.Addr(), uintptr(h), uintptr(unsafe.Pointer(&pid)))
	return pid
}

const (
	processQueryLimitedInformation = 0x1000
)

// processImageName returns the full exe path for a pid, or "" if it cannot be
// read. Used to identify the Star Citizen window by its executable rather than
// by window title alone - the title is a string CIG can change, the exe name is
// what the launcher runs.
func processImageName(pid uint32) string {
	h, _, _ := syscall.SyscallN(procOpenProcess.Addr(),
		uintptr(processQueryLimitedInformation), 0, uintptr(pid))
	if h == 0 {
		return ""
	}
	defer syscall.SyscallN(procCloseHandle.Addr(), h)
	buf := make([]uint16, 1024)
	size := uint32(len(buf))
	ok, _, _ := syscall.SyscallN(procQueryFullProcessImageNameW.Addr(),
		h, 0, uintptr(unsafe.Pointer(&buf[0])), uintptr(unsafe.Pointer(&size)))
	if ok == 0 {
		return ""
	}
	return syscall.UTF16ToString(buf[:size])
}

// EnumTopWindows walks every top-level window. Callback returns false to stop.
func EnumTopWindows(fn func(h HWND) bool) {
	cb := syscall.NewCallback(func(h HWND, _ uintptr) uintptr {
		if fn(h) {
			return 1
		}
		return 0
	})
	syscall.SyscallN(procEnumWindows.Addr(), cb, 0)
}

func GetForegroundWindowHandle() HWND {
	h, _, _ := syscall.SyscallN(procGetForegroundWindow.Addr())
	return HWND(h)
}

// ---------------------------------------------------------------------------
// audio
// ---------------------------------------------------------------------------

// beep is synchronous - Beep() does not return until the tone has finished.
// That is deliberate: the confirmation must be heard, and a fire-and-forget
// tone that the process exits out from under is not a confirmation.
func beep(freqHz, durationMs uint32) {
	syscall.SyscallN(procBeep.Addr(), uintptr(freqHz), uintptr(durationMs))
}

// ---------------------------------------------------------------------------
// hotkey
// ---------------------------------------------------------------------------

const (
	ModAlt      = 0x0001
	ModControl  = 0x0002
	ModShift    = 0x0004
	ModWin      = 0x0008
	ModNoRepeat = 0x4000

	WM_HOTKEY = 0x0312
	WM_QUIT   = 0x0012

	PM_REMOVE = 0x0001

	// ShowWindow(SW_HIDE) - used by --auto.
	swHide = 0

	// Window styles for the decoy window in the process-lock selftest.
	wsPopup   = 0x80000000
	wsVisible = 0x10000000
)

func RegisterHotKey(id int, mods, vk uint32) error {
	r, _, err := syscall.SyscallN(procRegisterHotKey.Addr(), 0, uintptr(id),
		uintptr(mods), uintptr(vk))
	if r == 0 {
		return fmt.Errorf("RegisterHotKey: %v", err)
	}
	return nil
}

func UnregisterHotKey(id int) {
	syscall.SyscallN(procUnregisterHotKey.Addr(), 0, uintptr(id))
}

// GetMessage blocks. Returns false when WM_QUIT arrives.
func GetMessage(m *MSG) bool {
	r, _, _ := syscall.SyscallN(procGetMessageW.Addr(), uintptr(unsafe.Pointer(m)), 0, 0, 0)
	return int32(r) > 0
}

// ---------------------------------------------------------------------------
// WinRT
// ---------------------------------------------------------------------------

const (
	RO_INIT_SINGLETHREADED = 0
	RO_INIT_MULTITHREADED  = 1

	COINIT_MULTITHREADED = 0x0
	COINIT_APARTMENTTHREADED = 0x2
)

type HSTRING uintptr

func RoInitialize(kind uintptr) error {
	hr, _, _ := syscall.SyscallN(procRoInitialize.Addr(), kind)
	// S_FALSE (0x00000001) means already initialised on this thread - fine.
	// RPC_E_CHANGED_MODE (0x80010106) means it was initialised in the other
	// apartment model. That is NOT fine for us and must not be swallowed.
	if !succeeded(hr) {
		return hrErr("RoInitialize", hr)
	}
	return nil
}

func CreateHString(s string) (HSTRING, error) {
	u := syscall.StringToUTF16(s)
	var hs HSTRING
	hr, _, _ := syscall.SyscallN(procWindowsCreateString.Addr(),
		uintptr(unsafe.Pointer(&u[0])),
		uintptr(len(u)-1), // length excludes the NUL
		uintptr(unsafe.Pointer(&hs)))
	if !succeeded(hr) {
		return 0, hrErr("WindowsCreateString", hr)
	}
	return hs, nil
}

func DeleteHString(hs HSTRING) {
	syscall.SyscallN(procWindowsDeleteString.Addr(), uintptr(hs))
}

// RoGetActivationFactory returns the activation factory for a WinRT class,
// queried for the given interface.
func RoGetActivationFactory(class string, iid *GUID) (unsafe.Pointer, error) {
	hs, err := CreateHString(class)
	if err != nil {
		return nil, err
	}
	defer DeleteHString(hs)

	var out unsafe.Pointer
	hr, _, _ := syscall.SyscallN(procRoGetActivationFactory.Addr(),
		uintptr(hs),
		uintptr(unsafe.Pointer(iid)),
		uintptr(unsafe.Pointer(&out)))
	if !succeeded(hr) {
		return nil, hrErr("RoGetActivationFactory("+class+")", hr)
	}
	return out, nil
}
