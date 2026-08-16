package main

// tray_probe.go - what actually happens when the notification area clicks.
//
// ===========================================================================
// WHY THIS EXISTS
// ===========================================================================
//
// The tray menu has never opened, on any build, and three separate diagnoses
// were made by reading the source - including one of mine that blamed a change
// which postdated the defect entirely. The source has looked correct every
// time. That is the pattern this project keeps paying for.
//
// So this drives the tray the two ways a message can reach a window and reports
// what came out, including whether a menu is on the screen. It cannot move
// Sleven's mouse and does not claim to: what it proves is which delivery path
// reaches the handler, and whether TrackPopupMenu puts a window up when it
// does. A real right-click is still the acceptance test.
//
// Run:  collector.exe -tray-probe
//
// It takes about ten seconds and puts an icon in the notification area for that
// long. It never sends, captures, or writes to the dataset.

import (
	"fmt"
	"sync/atomic"
	"time"
)

const (
	wmCancelMode = 0x001F
	wmRButtonDn  = 0x0204
)

// menuOnScreen reports whether a popup menu is up right now.
//
// "#32768" is the class Windows gives every menu, in every program, and has
// done since Windows 3.0 - about as stable a fact as this check could rest on.
// A menu that exists is an observation. A TrackPopupMenu call that returned is
// not, which is the difference this whole file is about.
func menuOnScreen() (bool, string) {
	found := false
	name := ""
	EnumTopWindows(func(h HWND) bool {
		if windowClass(h) == "#32768" && windowVisible(h) {
			found = true
			name = fmt.Sprintf("hwnd=0x%x class=#32768", uintptr(h))
			return false
		}
		return true
	})
	return found, name
}

func waitForMenu(want bool, within time.Duration) (bool, string) {
	deadline := time.Now().Add(within)
	for {
		up, what := menuOnScreen()
		if up == want || time.Now().After(deadline) {
			return up, what
		}
		time.Sleep(50 * time.Millisecond)
	}
}

func dismissMenu(hwnd uintptr) {
	procPostMessageW.Call(hwnd, wmCancelMode, 0, 0)
	waitForMenu(false, 2*time.Second)
}

// runTrayProbe drives the tray and prints what happened.
func runTrayProbe() int {
	logf := func(format string, args ...interface{}) {
		fmt.Printf("  [tray] "+format+"\n", args...)
	}
	fmt.Println("tray probe - the notification-area click path, observed")
	fmt.Println()

	t := StartTray(logf)
	if t == nil || !t.ok || t.hwnd == 0 {
		fmt.Println("RESULT: the tray did not start, so nothing below could be observed.")
		fmt.Println("        That is a 'could not check', NOT a pass.")
		return 2
	}
	defer t.Stop()
	hwnd := t.hwnd
	fmt.Printf("  tray window: 0x%x class=%q\n", hwnd, windowClass(HWND(hwnd)))

	fail := 0
	say := func(name string, ok bool, detail string) {
		mark := "ok  "
		if !ok {
			mark = "FAIL"
			fail++
		}
		fmt.Printf("  [%s] %s\n         %s\n", mark, name, detail)
	}

	// NEGATIVE CONTROL FIRST. If a menu were already on screen, every check
	// below would pass without the tray having done anything at all.
	if up, what := menuOnScreen(); up {
		fmt.Printf("  VOID: a menu is already open before the probe started (%s).\n", what)
		fmt.Println("        Close it and run again - these results would be meaningless.")
		return 2
	}
	say("NEGATIVE CONTROL: no menu is on screen before any message is sent",
		true, "so a menu found later was put there by this probe")

	// --- CAN THIS WINDOW TAKE THE FOREGROUND? -------------------------------
	//
	// TrackPopupMenu silently does nothing when its owner cannot. Asked here
	// rather than assumed, because "message-only windows cannot" was the last
	// wrong answer given about this defect.
	procSetForegroundWindow.Call(hwnd)
	fg, _, _ := procGetForegroundWindow.Call()
	if fg == 0 {
		// NOT A FAILURE, AND NOT A PASS. GetForegroundWindow returning 0 means
		// NO window in this session holds the foreground - a locked or
		// unattended desktop. Nothing can be concluded about whether this
		// window could have taken it, and calling it either way would be the
		// fabrication this project refuses.
		fmt.Println("  [----] the tray window can be brought to the foreground")
		fmt.Println("         COULD NOT CHECK: no window in this session holds the " +
			"foreground (GetForegroundWindow()=0), which is what a locked or " +
			"unattended desktop looks like. Re-run while somebody is using the machine.")
	} else {
		say("the tray window can be brought to the foreground",
			fg == hwnd,
			fmt.Sprintf("SetForegroundWindow(0x%x) then GetForegroundWindow()=0x%x - if "+
				"these differ the menu can still appear, but it will not dismiss on the "+
				"first click elsewhere", hwnd, fg))
	}

	// --- PATH 1: A POSTED MESSAGE -------------------------------------------
	before := atomic.LoadInt64(&trayCallbackViaLoop)
	procPostMessageW.Call(hwnd, wmTrayCallback, 1, wmRButtonUp)
	up, what := waitForMenu(true, 3*time.Second)
	detail := "menu did NOT appear"
	if up {
		detail = "menu IS on screen: " + what
	}
	say("POSTED: a posted callback opens the menu", up, detail)
	say("POSTED: it arrived through the message LOOP",
		atomic.LoadInt64(&trayCallbackViaLoop) > before,
		fmt.Sprintf("loop has now seen %d callback(s)", atomic.LoadInt64(&trayCallbackViaLoop)))
	dismissMenu(hwnd)

	// --- PATH 2: A SENT MESSAGE, WHICH IS WHAT THE SHELL DOES ---------------
	//
	// THE ONE THAT MATTERS. A sent message is delivered straight to the window
	// procedure while the thread sits inside GetMessage; it never appears in
	// the MSG that GetMessage hands back. Before today the window procedure
	// passed everything to DefWindowProc and only the LOOP looked for tray
	// messages - so this path did nothing, on every build, which is exactly
	// what Sleven has been reporting.
	loopBefore := atomic.LoadInt64(&trayCallbackViaLoop)
	wpBefore := atomic.LoadInt64(&trayCallbackViaWndProc)
	procSendNotifyMessage.Call(hwnd, wmTrayCallback, 1, wmRButtonUp)
	up2, what2 := waitForMenu(true, 3*time.Second)
	detail2 := "menu did NOT appear"
	if up2 {
		detail2 = "menu IS on screen: " + what2
	}
	say("SENT: a sent callback - what the notification area actually does - opens the menu",
		up2, detail2)
	say("SENT: it arrived at the WINDOW PROCEDURE, not the loop",
		atomic.LoadInt64(&trayCallbackViaWndProc) > wpBefore &&
			atomic.LoadInt64(&trayCallbackViaLoop) == loopBefore,
		fmt.Sprintf("window procedure +%d, loop +%d - if the loop count moved, the "+
			"premise of this fix is wrong and it must be re-examined",
			atomic.LoadInt64(&trayCallbackViaWndProc)-wpBefore,
			atomic.LoadInt64(&trayCallbackViaLoop)-loopBefore))
	dismissMenu(hwnd)

	// --- NEGATIVE CONTROL: NOT EVERY MESSAGE OPENS A MENU -------------------
	//
	// Without this, a handler that opened the menu on ANY message would pass
	// everything above.
	shownBefore := atomic.LoadInt64(&trayMenuShown)
	procSendNotifyMessage.Call(hwnd, wmTrayCallback, 1, wmRButtonDn)
	time.Sleep(600 * time.Millisecond)
	downUp, _ := menuOnScreen()
	say("NEGATIVE CONTROL: a button-DOWN callback does not open the menu",
		!downUp && atomic.LoadInt64(&trayMenuShown) == shownBefore,
		"the handler discriminates on the mouse message rather than opening on anything")
	dismissMenu(hwnd)

	// --- LEFT IS NOT RIGHT ---------------------------------------------------
	//
	// Sleven, after seeing this probe open the menu on both buttons: left should
	// open the WINDOW and right the MENU, which is what every other tray icon
	// does and what version one assumes now that the tray is the main surface.
	// Checked in both directions, because "left opens the window" is only half
	// the requirement - it must also stop opening the menu.
	opened := make(chan struct{}, 4)
	t.onOpenWindow = func() { opened <- struct{}{} }
	leftMenuBefore := atomic.LoadInt64(&trayMenuShown)
	procSendNotifyMessage.Call(hwnd, wmTrayCallback, 1, wmLButtonUp)
	sawOpen := false
	select {
	case <-opened:
		sawOpen = true
	case <-time.After(3 * time.Second):
	}
	say("LEFT-click opens the window", sawOpen,
		"the window action fired for a left-click on the icon")
	leftUp, _ := menuOnScreen()
	say("NEGATIVE CONTROL: LEFT-click does NOT open the menu",
		!leftUp && atomic.LoadInt64(&trayMenuShown) == leftMenuBefore,
		"otherwise both buttons still do the same thing and the distinction is cosmetic")
	dismissMenu(hwnd)

	// --- THE MENU'S OWN COMMANDS --------------------------------------------
	//
	// TrackPopupMenu SENDS its WM_COMMAND to the owner window. The same defect
	// would have eaten every menu choice even if the menu had opened, so it is
	// checked the same way rather than assumed to be fixed by the same change.
	clicked := make(chan string, 4)
	t.onOpenPictures = func() { clicked <- "open pictures" }
	cmdBefore := atomic.LoadInt64(&trayCommandViaWndProc)
	procSendNotifyMessage.Call(hwnd, wmCommand, uintptr(cmdOpenPictures), 0)
	got := ""
	select {
	case got = <-clicked:
	case <-time.After(3 * time.Second):
	}
	say("a SENT menu command reaches its action",
		got == "open pictures" && atomic.LoadInt64(&trayCommandViaWndProc) > cmdBefore,
		fmt.Sprintf("action fired: %q, window procedure saw +%d command(s)",
			got, atomic.LoadInt64(&trayCommandViaWndProc)-cmdBefore))

	fmt.Println()
	if fail > 0 {
		fmt.Printf("tray probe FAIL (%d)\n", fail)
		return 1
	}
	fmt.Println("tray probe PASS on the synthesised paths.")

	// -----------------------------------------------------------------------
	// AND NOW THE ONLY TEST THAT COUNTS: A REAL MOUSE.
	// -----------------------------------------------------------------------
	//
	// THIS IS THE ANSWER TO THE TESTING BLOCKER, and it is not "please close
	// your collector". This probe never takes the single-instance lock, so it
	// puts a SECOND icon in the notification area, clearly labelled, for three
	// minutes. Sleven right-clicks that one. His collector keeps running
	// throughout; nothing is sent, captured or written.
	//
	// What is observed: the notification area's own callback arriving at the
	// window procedure, and a menu window existing on screen. Neither is
	// synthesised here - during the hold the probe only watches.
	return holdForARealClick(t, hwnd)
}

// holdForARealClick keeps the icon alive and reports what a human's mouse did.
func holdForARealClick(t *trayHandle, hwnd uintptr) int {
	const hold = 180 * time.Second
	t.SetStatus("TRAY TEST - right-click THIS icon")

	fmt.Println()
	fmt.Println("  ============================================================")
	fmt.Println("  RIGHT-CLICK THE TRAY ICON NOW.")
	fmt.Println()
	fmt.Println("  There are two collector icons in the notification area: the")
	fmt.Println("  one that has been running, and this test one - hover to find")
	fmt.Println("  the one that says TRAY TEST. Right-click that one.")
	fmt.Println()
	fmt.Println("  Nothing needs closing. This holds for three minutes, reports")
	fmt.Println("  what it saw, and removes its own icon.")
	fmt.Println("  ============================================================")
	fmt.Println()

	startCb := atomic.LoadInt64(&trayCallbackViaWndProc)
	startLoop := atomic.LoadInt64(&trayCallbackViaLoop)
	startMenu := atomic.LoadInt64(&trayMenuShown)
	sawMenuOnScreen := false

	deadline := time.Now().Add(hold)
	reported := int64(0)
	for time.Now().Before(deadline) {
		if up, _ := menuOnScreen(); up {
			sawMenuOnScreen = true
		}
		if n := atomic.LoadInt64(&trayCallbackViaWndProc) - startCb; n > reported {
			reported = n
			fmt.Printf("  [%s] the notification area sent a callback - menu shown %d time(s)\n",
				time.Now().Format("15:04:05"),
				atomic.LoadInt64(&trayMenuShown)-startMenu)
		}
		time.Sleep(150 * time.Millisecond)
	}

	clicks := atomic.LoadInt64(&trayCallbackViaWndProc) - startCb
	viaLoop := atomic.LoadInt64(&trayCallbackViaLoop) - startLoop
	menus := atomic.LoadInt64(&trayMenuShown) - startMenu

	var verdict, detail string
	code := 0
	switch {
	case clicks == 0 && viaLoop == 0:
		// COULD NOT CHECK. Nobody clicked, or the notification area never
		// delivered anything. Reported as not performed - never as a pass.
		verdict = "NOT TESTED"
		detail = "No click ever reached the icon in three minutes.\n\n" +
			"If you did right-click it and this still says nothing arrived, that " +
			"is a bigger finding than the menu not opening: it would mean the " +
			"notification area is not delivering to this program at all."
		code = 2
	case menus > 0 && sawMenuOnScreen:
		verdict = "MENU OPENED"
		detail = fmt.Sprintf("%d click(s) arrived and a menu window was seen on "+
			"screen. This is the first build where that happens.", clicks)
	case menus > 0:
		verdict = "MENU OPENED BUT WAS NEVER SEEN ON SCREEN"
		detail = fmt.Sprintf("%d click(s) arrived and the menu was created %d "+
			"time(s), but no menu window was ever found. Report this exactly as "+
			"written - it is a different defect from the one being fixed.",
			clicks, menus)
		code = 1
	default:
		verdict = "CLICK ARRIVED, NO MENU"
		detail = fmt.Sprintf("%d click(s) reached the window procedure and no menu "+
			"was created. Delivery is fixed and something else is wrong.", clicks)
		code = 1
	}

	fmt.Printf("\n  RESULT: %s\n  %s\n", verdict, detail)
	showErrorBox("Citizen Collector - tray test: "+verdict,
		detail+"\n\nNothing was sent, captured or changed by this test.")
	return code
}
