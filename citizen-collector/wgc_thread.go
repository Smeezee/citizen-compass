package main

// wgc_thread.go - give WGC its own thread, because it cannot have the main one.
//
// # WHY WGC HAS NEVER ONCE RUN
//
// Found by review 2026-08-08. The webview library this program uses has an
// unconditional package init():
//
//	func init() {
//	    runtime.LockOSThread()
//	    w32.Ole32CoInitializeEx.Call(0, 2)   // 2 = COINIT_APARTMENTTHREADED
//	}
//
// That runs on the MAIN thread before main() starts, in every mode, simply
// because ui.go imports the package. So the main thread is a COM
// single-threaded apartment before this program does anything.
//
// captureWGC then calls RoInitialize(RO_INIT_MULTITHREADED). On a thread that
// is already in an STA, that returns RPC_E_CHANGED_MODE (0x80010106), which the
// code correctly treats as failure - so WGC bails on its first line, every
// time, on every path that runs on the main goroutine.
//
// Nobody noticed because the backend chain silently falls through to DXGI and
// still produces a picture. The only trace is that every sidecar says
// "method": "dxgi". WGC exists precisely for the fullscreen and occluded cases
// DXGI handles worst, and it has never been reached.
//
// # AND EVEN OFF THE MAIN THREAD IT WAS WRONG
//
// A COM apartment belongs to a THREAD, not a goroutine. captureWGC called
// RoInitialize with no runtime.LockOSThread, and its retry loop calls
// time.Sleep - a rescheduling point. So after the first iteration the remaining
// WinRT calls could run on threads that never joined an apartment, which is an
// intermittent, machine-dependent failure that would have been miserable to
// chase. It also never called RoUninitialize, permanently joining every worker
// thread it touched to the MTA.
//
// # THE FIX: ONE THREAD, OWNED, FOR THE LIFETIME OF THE PROCESS
//
// A single goroutine locked to a single OS thread, initialised once into the
// multithreaded apartment, doing every WGC capture in sequence. Requests arrive
// on a channel. The apartment is entered once and never changes; nothing else
// in the program is affected; and captures cannot race each other because there
// is only one worker.
//
// It is started lazily on the first WGC attempt, so a run that never captures
// pays nothing.

import (
	"fmt"
	"runtime"
	"sync"
)

type wgcRequest struct {
	h     HWND
	reply chan wgcReply
}

type wgcReply struct {
	frame *Frame
	err   error
}

var (
	wgcOnce  sync.Once
	wgcQueue chan wgcRequest
	wgcFatal error // set once if the worker could not enter the apartment
)

// startWGCWorker brings up the dedicated capture thread. Called once.
func startWGCWorker() {
	wgcQueue = make(chan wgcRequest)
	ready := make(chan error, 1)

	go func() {
		// LOCKED FOR THE LIFETIME OF THIS GOROUTINE, AND NEVER UNLOCKED.
		// The apartment belongs to the thread. Unlocking would let the Go
		// runtime hand this thread to other goroutines, and hand THIS goroutine
		// a thread with no apartment - the exact bug this file exists to fix.
		runtime.LockOSThread()

		if err := RoInitialize(RO_INIT_MULTITHREADED); err != nil {
			ready <- fmt.Errorf("this thread could not join the multithreaded "+
				"apartment: %w", err)
			return
		}
		ready <- nil

		for req := range wgcQueue {
			f, err := captureWGCOnThisThread(req.h)
			req.reply <- wgcReply{frame: f, err: err}
		}
	}()

	wgcFatal = <-ready
}

// captureWGC hands the work to the owned thread and waits for the answer.
//
// Keeps the original name and signature so backendChain and every caller are
// unchanged - the fix is entirely in where the work happens.
func captureWGC(h HWND) (*Frame, error) {
	if h == 0 {
		return nil, fmt.Errorf("no window handle")
	}
	wgcOnce.Do(startWGCWorker)
	if wgcFatal != nil {
		return nil, wgcFatal
	}
	reply := make(chan wgcReply, 1)
	wgcQueue <- wgcRequest{h: h, reply: reply}
	r := <-reply
	return r.frame, r.err
}
