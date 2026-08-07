package main

// console.go - making a GUI-subsystem binary still able to report.
//
// WO-UI-01 §4.2 says never a console window, which means building with
// -H=windowsgui. Such a binary has NO stdout: nothing it prints goes anywhere,
// including --selftest, including the packager's own verification step.
//
// WO-UI-01 §5 rules that all three of these happen, not one of them:
//
//   1. attach to the parent console when one exists, so running it from a shell
//      still shows output in that shell, while a double-click creates nothing
//   2. ALWAYS write a results file next to the exe, regardless
//   3. ALWAYS return a meaningful exit code
//
// The packager asserts on the exit code and the results file. Never on stdout -
// stdout is a convenience for humans and never a contract.

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"syscall"
	"time"
	"unsafe"
)

const attachParentProcess = ^uintptr(0) // (DWORD)-1

// GetConsoleWindow is already declared in winapi.go as procGetConsoleWindow -
// reused rather than declared again here, so there is one binding per Win32
// entry point and no chance of the two drifting.
var (
	procAttachConsole       = modKernel32.NewProc("AttachConsole")
	procGetDiskFreeSpaceExW = modKernel32.NewProc("GetDiskFreeSpaceExW")
)

// attachParentConsole hooks this process up to the console of whatever launched
// it, if there is one.
//
// Returns false when there is no parent console - a double-click, a scheduled
// task, a shortcut - and false is the NORMAL case for the people this program
// is built for. It is not an error and nothing is printed about it.
//
// The std handles are reopened onto CONOUT$ afterwards because a
// -H=windowsgui process starts with none, so attaching alone would leave
// fmt.Print writing into a closed handle.
func attachParentConsole() bool {
	r, _, _ := procAttachConsole.Call(attachParentProcess)
	if r == 0 {
		return false
	}
	if f, err := os.OpenFile("CONOUT$", os.O_WRONLY, 0); err == nil {
		os.Stdout = f
		os.Stderr = f
	}
	if f, err := os.OpenFile("CONIN$", os.O_RDONLY, 0); err == nil {
		os.Stdin = f
	}
	return true
}

// hasConsole reports whether this process currently has a console attached.
// Used by the "no console was created" test, which has to observe the absence
// from the outside rather than trust that a build flag was passed.
func hasConsole() bool {
	h, _, _ := procGetConsoleWindow.Call()
	return h != 0
}

// freeSpaceBytes reports free space on the volume holding dir.
//
// Used for the "captures folder is nearly full" sentence in the window. A
// collector that quietly stops saving because the disk filled would be another
// component looking healthy while doing nothing.
func freeSpaceBytes(dir string) (uint64, error) {
	p, err := syscall.UTF16PtrFromString(dir)
	if err != nil {
		return 0, err
	}
	var freeToCaller, total, totalFree uint64
	r, _, e := procGetDiskFreeSpaceExW.Call(
		uintptr(unsafe.Pointer(p)),
		uintptr(unsafe.Pointer(&freeToCaller)),
		uintptr(unsafe.Pointer(&total)),
		uintptr(unsafe.Pointer(&totalFree)))
	if r == 0 {
		return 0, e
	}
	return freeToCaller, nil
}

// selftestResultsName is the file the packager reads. Fixed name, next to the
// exe, so a verifier does not have to guess or parse anything to find it.
const selftestResultsName = "collector-selftest-results.txt"

// runTeed runs fn with os.Stdout duplicated into a buffer.
//
// Everything the selftest prints is captured, including output from helpers
// that print directly rather than going through check(). Capturing only
// check()'s lines would produce a results file that quietly disagreed with what
// a human saw on screen, and the file is the thing automation trusts.
func runTeed(fn func() int) (code int, transcript string) {
	real := os.Stdout
	r, w, err := os.Pipe()
	if err != nil {
		// Cannot tee. Run anyway and report an empty transcript rather than
		// skipping the checks - and the caller records that it was empty.
		return fn(), ""
	}

	var buf bytes.Buffer
	done := make(chan struct{})
	go func() {
		_, _ = io.Copy(io.MultiWriter(real, &buf), r)
		close(done)
	}()

	os.Stdout = w
	code = fn()
	os.Stdout = real
	_ = w.Close()
	<-done
	_ = r.Close()

	return code, buf.String()
}

// verdictFor turns an exit code into the word the results file leads with.
//
// 2 is "could not check", and it is deliberately NOT collapsed into failure:
// a check that could not run is a different fact from a check that ran and
// failed, and reporting the first as the second would hide the difference the
// whole project cares about.
func verdictFor(code int) string {
	switch code {
	case 0:
		return "PASS"
	case 1:
		return "FAIL"
	case 2:
		return "VOID"
	default:
		return "UNKNOWN"
	}
}

// writeSelftestResults always writes the file, whatever happened.
//
// A results file that appears only on success would let a crashed or skipped
// run look identical to one that was never attempted - and a stale file from an
// earlier good run would then be read as today's pass. So it is written on
// every path, and it leads with a machine-readable line so nothing downstream
// has to parse prose.
func writeSelftestResults(dir string, code int, transcript string) string {
	path := filepath.Join(dir, selftestResultsName)

	var b bytes.Buffer
	fmt.Fprintf(&b, "RESULT=%s\r\n", verdictFor(code))
	fmt.Fprintf(&b, "EXIT=%d\r\n", code)
	fmt.Fprintf(&b, "VERSION=%s\r\n", Version)
	fmt.Fprintf(&b, "VARIANT=%s\r\n", BuildVariant)
	fmt.Fprintf(&b, "WHEN=%s\r\n", time.Now().Format(time.RFC3339))
	if transcript == "" {
		fmt.Fprintf(&b, "TRANSCRIPT=unavailable (output could not be captured)\r\n")
	}
	fmt.Fprintf(&b, "----\r\n")
	b.WriteString(transcript)

	// Best effort by necessity: if this cannot be written there is nowhere left
	// to report that fact to. The exit code still carries the verdict, which is
	// why §5 requires both and not either.
	_ = os.WriteFile(path, b.Bytes(), 0o644)
	return path
}

// showErrorBox is the only way to tell a person something went wrong when there
// is no console and the window itself could not be created.
//
// WO-UI-01 §9: plain sentences, no error codes, no stack traces. This is the
// last resort, used when even the window failed.
func showErrorBox(title, msg string) {
	procMessageBoxW := modUser32.NewProc("MessageBoxW")
	const mbIconError = 0x00000010
	t, _ := syscall.UTF16PtrFromString(title)
	m, _ := syscall.UTF16PtrFromString(msg)
	procMessageBoxW.Call(0, uintptr(unsafe.Pointer(m)), uintptr(unsafe.Pointer(t)), mbIconError)
}
