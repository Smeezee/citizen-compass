package main

// hotkey_e2e_selftest.go - does a REAL --auto process register the hotkey?
//
// WHY THIS FILE EXISTS SEPARATELY FROM hotkey_selftest.go
//
// The checks in hotkey_selftest.go call startHotkeyListener directly and build
// an autoDeps by hand. They prove the listener registers and that runAuto acts
// on a press. Both are worth having - and NEITHER of them would have caught the
// bug they were written for.
//
// The original defect was not in the listener and not in runAuto. It was in
// main(): the auto branch called runAuto and returned, and the RegisterHotKey
// call sat after that return, unreachable. Every unit-level check would have
// gone on passing forever, exactly as 34 checks and 13 mutations did.
//
// A check that cannot fail on the defect it was written for is not a check. So
// this one runs the ACTUAL BINARY in ACTUAL --auto MODE as a child process and
// asks Windows, from out here, whether the hotkey ended up registered.
//
// That is the only version of this test that fails if someone moves the
// registration back below the return.

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

// waitForRegistration polls until spec is held, or the deadline passes.
func waitForRegistration(spec string, want bool, timeout time.Duration) (bool, error) {
	deadline := time.Now().Add(timeout)
	var last bool
	for {
		held, err := probeIsRegistered(hotkeyProbeID, spec)
		if err != nil {
			return false, err
		}
		last = held
		if held == want || time.Now().After(deadline) {
			return last, nil
		}
		time.Sleep(150 * time.Millisecond)
	}
}

// copyExeToTemp puts this binary in a scratch directory.
//
// The child writes collector-auto.log next to its own executable. Running it
// from a temp copy keeps the selftest out of the operator's real log instead of
// appending test noise to the record of a genuine capture session.
func copyExeToTemp() (exePath string, dir string, err error) {
	self, err := os.Executable()
	if err != nil {
		return "", "", err
	}
	dir, err = os.MkdirTemp("", "cc-hotkey-e2e-")
	if err != nil {
		return "", "", err
	}
	dst := filepath.Join(dir, "collector-e2e.exe")
	in, err := os.Open(self)
	if err != nil {
		return "", dir, err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return "", dir, err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		return "", dir, err
	}
	if err := out.Close(); err != nil {
		return "", dir, err
	}
	return dst, dir, nil
}

// runAutoHotkeyE2ESelftest is the end-to-end registration proof.
func runAutoHotkeyE2ESelftest(check func(name string, ok bool, detail string)) {
	const spec = "ctrl+alt+f9"

	exePath, dir, err := copyExeToTemp()
	if dir != "" {
		defer os.RemoveAll(dir)
	}
	if err != nil {
		check("auto-mode e2e runnable", false, fmt.Sprintf("could not stage a test binary: %v", err))
		return
	}

	if held, err := probeIsRegistered(hotkeyProbeID, spec); err != nil || held {
		check("auto-mode e2e runnable", false,
			spec+" is already held before the test starts - e2e registration check NOT PERFORMED")
		return
	}
	check("auto-mode e2e runnable", true, "staged a test binary and "+spec+" is free")

	start := func(hk string) *exec.Cmd {
		c := exec.Command(exePath, "--auto", "--hotkey", hk,
			"--out", filepath.Join(dir, "captures"),
			"--poll", "3600")
		c.Stdout, c.Stderr = nil, nil
		_ = c.Start()
		return c
	}
	stop := func(c *exec.Cmd) {
		if c == nil || c.Process == nil {
			return
		}
		_ = c.Process.Kill()
		_, _ = c.Process.Wait()
	}

	// ---------------------------------------------------------------------
	// NEGATIVE CONTROL FIRST: an invalid hotkey string must leave the key
	// UNREGISTERED, while auto mode itself still runs.
	// ---------------------------------------------------------------------
	bad := start("ctrl+alt+notakey")
	heldBad, err := waitForRegistration(spec, true, 3*time.Second)
	stop(bad)
	if err != nil {
		check("invalid hotkey leaves it UNREGISTERED in --auto", false, fmt.Sprintf("probe failed: %v", err))
		return
	}
	check("invalid hotkey leaves it UNREGISTERED in --auto", !heldBad,
		"a real --auto process with a bad hotkey did not take "+spec)

	// Let the OS settle before the positive case so a lingering registration
	// cannot be mistaken for the new one.
	_, _ = waitForRegistration(spec, false, 3*time.Second)

	// ---------------------------------------------------------------------
	// POSITIVE CASE: a real --auto process MUST register the hotkey.
	// This is the assertion that fails if registration moves back below the
	// return in main().
	// ---------------------------------------------------------------------
	good := start(spec)
	heldGood, err := waitForRegistration(spec, true, 8*time.Second)
	if err != nil {
		stop(good)
		check("--auto REGISTERS the hotkey (end to end)", false, fmt.Sprintf("probe failed: %v", err))
		return
	}
	check("--auto REGISTERS the hotkey (end to end)", heldGood,
		"a real `--auto` child process holds "+spec+" - asked of Windows, not of our own variables")

	stop(good)

	// It must also be released when the process dies, otherwise the positive
	// result above could be a leak from some earlier run rather than this one.
	releasedRaw, _ := waitForRegistration(spec, false, 5*time.Second)
	check("hotkey is released when --auto exits", !releasedRaw,
		"probe re-acquired "+spec+" after the child was killed")

	check("e2e probe distinguishes the two runs", heldGood != heldBad,
		fmt.Sprintf("invalid-hotkey run=%v, valid-hotkey run=%v - opposite results, so the check is measuring registration",
			heldBad, heldGood))
}
