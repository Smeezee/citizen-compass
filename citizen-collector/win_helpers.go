package main

// win_helpers.go - the few standard-library calls the window and the rollback
// share, named once so they cannot drift and so the selftest can stub them.

import (
	"os"
	"os/exec"
	"sync"
	"time"
)

func osExecutable() (string, error) { return os.Executable() }
func osExit(code int)               { os.Exit(code) }
func sleepBriefly()                 { time.Sleep(400 * time.Millisecond) }

// runForOutput runs a program and returns its first line of output.
//
// Used to ask a kept binary what version it is, which is the only honest way to
// know what a revert would land on - a filename says nothing.
func runForOutput(path string, args ...string) (string, error) {
	out, err := exec.Command(path, args...).Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func osGetenv(k string) string { return os.Getenv(k) }

// comOnce guards the process-wide COM apartment.
var comOnce sync.Once

// ensureCOM initialises an apartment-threaded COM apartment, once.
//
// # WHY THIS EXISTS AT ALL
//
// It did not, until the browser engine was removed. shortcut.go's own comment
// said the apartment was "already initialised - the process is
// apartment-threaded from go-webview2's init": COM was working because a
// DEPENDENCY happened to set it up on import.
//
// That is a load-bearing side effect of something nobody thought of as
// providing it, and deleting the dependency would have turned every
// CoCreateInstance into CO_E_NOTINITIALIZED. The symptom would have been a
// shortcut that silently never appears - indistinguishable, to the person, from
// having said no to it.
//
// S_FALSE means the apartment was already initialised on this thread, which is
// success, not failure. RPC_E_CHANGED_MODE means somebody got there first with
// a different model - also not something to fail over, because the calls that
// need this work fine in either.
func ensureCOM() {
	comOnce.Do(func() {
		const coinitApartmentThreaded = 2
		procCoInitializeEx.Call(0, coinitApartmentThreaded)
	})
}
