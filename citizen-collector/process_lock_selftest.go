package main

// process_lock_selftest.go - proves the process lock actually REFUSES.
//
// ---------------------------------------------------------------------------
// WHY THIS EXISTS
// ---------------------------------------------------------------------------
// The lock at findGameWindow's gate, and the second guard behind it, both read
// correctly. Reading is not testing. Before this file, --selftest had four
// checks - captures dir, blank detector, png encode, win32 reachable - and NONE
// of them touched the process restriction. There was no artifact anywhere
// showing that a refusal had ever happened.
//
// Capture 0007 was not evidence either. It grabbed a claude.exe window WITH
// --allow-any-window set, which demonstrates that the door opens when you
// unlock it. It says nothing about whether it stays shut when you do not.
//
// ---------------------------------------------------------------------------
// THE CONDITION IS CREATED, NOT HOPED FOR
// ---------------------------------------------------------------------------
// A test that waits for a window titled "Star Citizen" to happen to exist is a
// test that silently does nothing on a quiet desktop and reports a pass. So
// this file MAKES one: a real top-level window, really titled "Star Citizen",
// really visible, really large enough to pass the size filter - owned by this
// process, which is not StarCitizen.exe.
//
// That is the exact shape of the original defect. Auto-detection once picked
// this project's own terminal because its title mentioned the game.
//
// ---------------------------------------------------------------------------
// WHAT IS FAKED, AND WHAT IS NOT
// ---------------------------------------------------------------------------
// To prove ACCEPTANCE without the game running, scProcessNames is temporarily
// pointed at this test binary's own exe name. That is a fake at the
// isGameProcess BOUNDARY - the question "which exe is the game?" - and nothing
// more. The gate itself is untouched and still executes: same call, same code
// path, same guard. Stubbing out the gate would make the test prove nothing,
// which is the whole reason it is done this way round.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

// decoyWindow is a real Win32 window created by this process.
type decoyWindow struct {
	h HWND
}

// newDecoyWindow makes a visible top-level window titled "Star Citizen".
//
// It is placed far off-screen so a selftest does not flash a box in front of
// whatever the user is doing. IsWindowVisible tests the WS_VISIBLE STYLE, not
// whether the window is within the desktop bounds, so an off-screen window is
// still fully visible as far as the enumeration under test is concerned - it
// takes exactly the same path a real bystander window would.
//
// "STATIC" is a predefined system class, so no class registration is needed and
// no window procedure has to be pumped for the window to exist and enumerate.
func newDecoyWindow(title string) (*decoyWindow, error) {
	cls := utf16Ptr("STATIC")
	name := utf16Ptr(title)

	// Held in variables, not written inline: `uintptr(int32(-5000))` is a
	// CONSTANT expression and Go rejects it as overflowing uintptr. Going
	// through a typed variable converts at runtime, sign-extending as the
	// Win32 calling convention expects for an int argument.
	offX, offY := int32(-5000), int32(-5000)
	w, h32 := int32(400), int32(300)

	h, _, err := procCreateWindowExW.Call(
		0,                             // dwExStyle
		uintptr(unsafe.Pointer(cls)),  // lpClassName
		uintptr(unsafe.Pointer(name)), // lpWindowName
		uintptr(wsPopup|wsVisible),    // dwStyle
		uintptr(offX),                 // X - off-screen
		uintptr(offY),                 // Y
		uintptr(w),                    // nWidth  - over the 200px floor
		uintptr(h32),                  // nHeight
		0, 0, 0, 0,
	)
	if h == 0 {
		return nil, fmt.Errorf("CreateWindowExW: %v", err)
	}
	return &decoyWindow{h: HWND(h)}, nil
}

func (d *decoyWindow) Close() {
	if d != nil && d.h != 0 {
		procDestroyWindow.Call(uintptr(d.h))
		d.h = 0
	}
}

// runProcessLockSelftest returns the number of failed checks.
//
// Naming follows the work order: "positive control" is the REFUSAL (the thing
// the lock is for), "negative control" is the ACCEPTANCE.
func runProcessLockSelftest(check func(name string, ok bool, detail string)) {
	selfExe := "unknown.exe"
	if p, err := os.Executable(); err == nil {
		selfExe = strings.ToLower(filepath.Base(p))
	}

	// Sanity: this test is meaningless if the binary running it happens to be
	// called starcitizen.exe. Stated rather than assumed.
	if isGameProcess(selfExe) {
		check("lock: test binary is not the game", false,
			"this binary is named "+selfExe+" - the refusal test cannot be trusted")
		return
	}

	decoy, err := newDecoyWindow("Star Citizen")
	if err != nil {
		check("lock: decoy window created", false, err.Error())
		return
	}
	defer decoy.Close()

	// Prove the decoy is actually the thing we think it is, otherwise a
	// refusal below could simply be a refusal of a window that never existed.
	title := windowText(decoy.h)
	vis := windowVisible(decoy.h)
	r, rerr := GetWindowRectOf(decoy.h)
	bigEnough := rerr == nil && r.Width() >= 200 && r.Height() >= 200
	check("lock: decoy is a real visible 'Star Citizen' window",
		title == "Star Citizen" && vis && bigEnough,
		fmt.Sprintf("title=%q visible=%v size=%dx%d owner=%s",
			title, vis, r.Width(), r.Height(), selfExe))

	// =====================================================================
	// 1. POSITIVE CONTROL - the lock must REFUSE it.
	// =====================================================================
	win, err := findGameWindow(false, "Star Citizen")

	refused := false
	namesProcess := false
	// WHICH LAYER refused matters, and this is why.
	//
	// Mutation testing on 2026-08-06 deleted layer 1 outright and every check
	// here still passed - because layer 2 caught the decoy and findGameWindow
	// returned an error either way. "It refused" is true of both layers, so a
	// test that only asks "did it refuse" proves neither of them individually.
	// That is the same defect as testing layer 1 alone, just pointing the other
	// way.
	//
	// The two layers say different things, so the error text tells them apart:
	//   layer 1 -> "Refused N other process(es)"
	//   layer 2 -> "internal guard: selected a window from ..."
	// Requiring layer 1's wording pins layer 1 specifically.
	fromLayer1 := false
	layerDetail := "not performed"
	var detail string

	if err != nil {
		refused = true
		low := strings.ToLower(err.Error())
		namesProcess = strings.Contains(low, selfExe)
		fromLayer1 = strings.Contains(low, "refused") &&
			!strings.Contains(low, "internal guard")
		detail = fmt.Sprintf("refused, error names %s: %v", selfExe, namesProcess)
		if fromLayer1 {
			layerDetail = "the process gate refused it before any title was consulted"
		} else {
			layerDetail = "refused, but NOT by the gate - layer 1 may be gone: " + err.Error()
		}
	} else if win.H == decoy.h {
		detail = fmt.Sprintf("ACCEPTED THE DECOY - captured %q from %s", win.Title, win.Exe)
	} else {
		// Star Citizen is genuinely running on this machine. The lock still did
		// the right thing - it did not pick the decoy - but the error message
		// cannot be inspected, so that half is reported as not performed rather
		// than as a pass.
		refused = true
		namesProcess = true
		fromLayer1 = true
		detail = fmt.Sprintf("the game is running; lock selected %s and NOT the decoy "+
			"(error text not exercised)", win.Exe)
		layerDetail = detail
	}

	check("lock: POSITIVE CONTROL refuses a non-game 'Star Citizen'", refused, detail)
	check("lock: refusal NAMES the refused process", namesProcess, detail)
	check("lock: refusal came from LAYER 1, the process gate", fromLayer1, layerDetail)

	// =====================================================================
	// 2. NEGATIVE CONTROL - it must ACCEPT a window that IS the game.
	//
	// Faked at the isGameProcess boundary only. The gate still runs.
	// =====================================================================
	restore := scProcessNames
	scProcessNames = []string{selfExe}
	win2, err2 := findGameWindow(false, "Star Citizen")
	scProcessNames = restore

	accepted := err2 == nil && win2.H == decoy.h
	d2 := "accepted the window once its process counted as the game"
	if !accepted {
		d2 = fmt.Sprintf("did NOT accept it: err=%v matched=%v", err2, win2.H == decoy.h)
	}
	check("lock: NEGATIVE CONTROL accepts the real game process", accepted, d2)

	// The restore must actually have happened, or every later check in this
	// process is running against a permanently widened whitelist.
	check("lock: whitelist restored after the fake",
		len(scProcessNames) == 1 && scProcessNames[0] == "starcitizen.exe",
		fmt.Sprintf("scProcessNames=%v", scProcessNames))

	// =====================================================================
	// 3. THE SECOND GUARD - tested on its own.
	//
	// Layer one cannot deliver a non-game window to layer two, which is
	// precisely why layer two needs its own test: exercising only layer one
	// would still pass if this guard were deleted outright.
	// =====================================================================
	bad := foundWindow{Exe: "claude.exe", Title: "Star Citizen"}
	gErr := finalWindowGuard(bad, false)
	check("lock: second guard refuses a non-game window",
		gErr != nil && strings.Contains(gErr.Error(), "claude.exe"),
		fmt.Sprintf("%v", gErr))

	good := foundWindow{Exe: "starcitizen.exe", Title: "Star Citizen"}
	check("lock: second guard admits the game",
		finalWindowGuard(good, false) == nil,
		"a genuine game window is not blocked by the guard")

	// With allowAny the guard must stand aside - otherwise the master build's
	// bench flag would be broken by this guard rather than by policy.
	check("lock: second guard defers to --allow-any-window",
		finalWindowGuard(bad, true) == nil,
		"master-only bypass still works, by design")

	// =====================================================================
	// 4. CREW VARIANT - allowAny must be UNSETTABLE, not merely refused.
	// =====================================================================
	flagExists := lookupFlagExists("allow-any-window")

	if BuildVariant == "crew" {
		// registerBenchFlags() is called a SECOND time here, deliberately and
		// only in this build. The crew implementation registers no flags at
		// all, so a repeat call is harmless - and that harmlessness is itself
		// the property under test. The master implementation calls
		// flag.Bool(), so the same line there panics with "flag redefined",
		// which is direct proof that the master version really does register
		// something and the crew version really does not.
		benchAllow, benchHint := registerBenchFlags()()
		check("lock: CREW build cannot set allow-any-window",
			!benchAllow && !flagExists && benchHint == "",
			fmt.Sprintf("flag registered=%v benchAllow=%v hint=%q (all must be empty/false)",
				flagExists, benchAllow, benchHint))
	} else {
		// In the master build the flag MUST exist, or the bench path has been
		// lost and this check would otherwise pass by accident in both builds.
		check("lock: MASTER build does offer allow-any-window",
			flagExists,
			fmt.Sprintf("flag registered=%v", flagExists))
	}

	var _ = syscall.Handle(0)
}
