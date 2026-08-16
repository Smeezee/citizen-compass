package main

// win_helpers.go - the few standard-library calls the window and the rollback
// share, named once so they cannot drift and so the selftest can stub them.

import (
	"os"
	"os/exec"
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
