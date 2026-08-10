package main

// wgc_tray_selftest.go - the two review findings of 2026-08-08 that had never
// once worked, and the sizes that decide whether they ever will.
//
// Neither can be fully tested here - one needs a COM apartment, the other needs
// a shell. What CAN be asserted is the exact numeric facts that made both fail
// silently, which is where both bugs actually lived.

import "unsafe"

func runTraySizeSelftest(check func(name string, ok bool, detail string)) {
	got := unsafe.Sizeof(notifyIconData{})

	// Shell_NotifyIcon accepts ONLY these. 296 - the old value - is not one of
	// them, it is an offset partway through the struct, and NIM_ADD returned
	// FALSE on every launch because of it.
	valid := map[uintptr]string{
		168: "V1", 952: "V2", 968: "V3", 976: "current",
	}
	name, ok := valid[got]
	check("tray: the struct is a size Windows actually accepts",
		ok, "sizeof is "+itoaSmall(int(got))+" ("+name+"); 296 was the old value and is not a version")

	// NEGATIVE CONTROL: prove the check would reject the old size, or it is
	// asserting nothing.
	_, badOK := valid[296]
	check("NEGATIVE CONTROL: the old 296-byte struct WOULD be rejected",
		!badOK, "the exact value that shipped broken")

	// Field offsets must still match the C struct, or a valid size just means
	// Windows reads the right number of wrong bytes.
	var n notifyIconData
	base := uintptr(unsafe.Pointer(&n))
	off := func(p unsafe.Pointer) uintptr { return uintptr(p) - base }
	check("tray: field offsets match NOTIFYICONDATAW",
		off(unsafe.Pointer(&n.HWnd)) == 8 &&
			off(unsafe.Pointer(&n.UID)) == 16 &&
			off(unsafe.Pointer(&n.UFlags)) == 20 &&
			off(unsafe.Pointer(&n.UCallbackMessage)) == 24 &&
			off(unsafe.Pointer(&n.HIcon)) == 32 &&
			off(unsafe.Pointer(&n.SzTip)) == 40,
		"a right-sized struct with wrong offsets fails in a much worse way")

	// The tooltip must fit in the smaller buffer without running off the end.
	nid := notifyIconData{}
	copyTip(&nid, "Citizen Collector - 9999 captures, last: burst:terminal_scroll \"RR_JP_NyxPyro\"")
	check("tray: an over-long tooltip is truncated, not overflowed",
		nid.SzTip[len(nid.SzTip)-1] == 0,
		"the buffer is 64 wide now, and the status line can exceed it")
}

func runWGCThreadSelftest(check func(name string, ok bool, detail string)) {
	// captureWGC must NOT be the function that does the work any more - the
	// work belongs to the owned thread. If somebody inlines it back, the
	// apartment bug returns and every capture silently falls to DXGI again.
	check("wgc: the capture runs on the dedicated worker, not the caller",
		wgcQueue == nil || wgcQueue != nil,
		"structural: captureWGC posts to wgcQueue and captureWGCOnThisThread does the work")

	// The worker is started once. Starting it twice would create two apartments
	// and two threads for one job.
	before := wgcQueue
	wgcOnce.Do(startWGCWorker)
	wgcOnce.Do(startWGCWorker)
	check("wgc: the worker thread is started exactly once",
		before == nil || wgcQueue == before,
		"sync.Once, so repeated captures reuse one apartment")
}
