package main

// ticker.go - the watcher's beat. Architecture's ruling, 2026-09-12
// (memo_build_the-beat-is-ruled-the-matchup-gets-labelled-and-apply-the-diff).
//
// Until now the watcher did nothing between letters. BOOT.md regenerated only
// when mail routed, so the page a desk boots from went stale on exactly the
// quiet morning a desk boots cold, and `desk fetch` ran only when somebody
// remembered to run it. One ticker, one process, two jobs:
//
//	every tickInterval   run `desk fetch`, then rewrite BOOT.md
//
// EXEC, NOT A PORT. The fetch stays in scripts/desk.py, the copy with the
// self-test; a Go port would be a second copy that drifts from it.
//
// THE 70-SECOND RESCAN STAYS ON THE MAIL PATH. BOOT.md costs about 130 ms; the
// handoff and its update counter are not touched by the beat.
//
// A FAILED FETCH DOES NOT STOP THE PAGE. desk.py records its own run, failure
// included, and BOOT.md is written regardless - a page that stopped when the
// poller stopped would hide the stop, which is the defect this exists to fix.

import (
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"syscall"
	"time"
)

const tickInterval = 10 * time.Minute
const fetchTimeout = 2 * time.Minute

// bootWriteMu: BOOT.md has two writers inside this process now - the mail path
// (regenerateHandoff) and the beat. One lock, so they cannot interleave on the
// .tmp file. Rule 14, applied inside a process.
var bootWriteMu sync.Mutex

func writeBootLocked(root, out string, now time.Time) error {
	bootWriteMu.Lock()
	defer bootWriteMu.Unlock()
	return writeBoot(root, out, now, false)
}

// runDeskFetch execs `scripts/desk.py fetch` with the project's venv Python.
func runDeskFetch(root string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), fetchTimeout)
	defer cancel()
	py := filepath.Join(root, "venv", "Scripts", "python.exe")
	cmd := exec.CommandContext(ctx, py, filepath.Join(root, "scripts", "desk.py"), "fetch")
	cmd.Dir = root
	// No console window flashing on the desktop every ten minutes - the same
	// reason as ocr.go, plus CREATE_NO_WINDOW so none is even allocated.
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
	out, err := cmd.CombinedOutput()
	if ctx.Err() == context.DeadlineExceeded {
		err = fmt.Errorf("timed out after %s", fetchTimeout)
	}
	return string(out), err
}

// oneLine folds a command's output into one log line.
func oneLine(s string) string {
	var parts []string
	for _, l := range strings.Split(strings.ReplaceAll(s, "\r\n", "\n"), "\n") {
		if l = strings.TrimSpace(l); l != "" {
			parts = append(parts, l)
		}
	}
	return bootClip(strings.Join(parts, " | "), 240)
}

// tickOnce is one beat. The fetcher is a parameter so a test can make it fail.
func tickOnce(root string, now time.Time, fetch func(string) (string, error)) error {
	out, err := fetch(root)
	if err != nil {
		logMsg("beat: desk fetch FAILED (%v): %s", err, oneLine(out))
	} else {
		logMsg("beat: desk fetch ran: %s", oneLine(out))
	}
	// The filed-mail commit, at most once an hour (the script keeps the hour),
	// BEFORE the receipt so the receipt counts what this commit left behind.
	if mout, merr := runMailCommit(root); merr != nil {
		logMsg("beat: mail commit FAILED (%v): %s", merr, oneLine(mout))
	} else {
		logMsg("beat: %s", oneLine(mout))
	}
	// The uncommitted receipt, BEFORE the page, so the page reads this beat's
	// number. A failed run does not stop the page: the receipt records its own
	// did-not-look, and a missing receipt prints NOT READ (boot_uncommitted.go).
	if rout, rerr := runReceipt(root); rerr != nil {
		logMsg("beat: uncommitted receipt FAILED (%v): %s", rerr, oneLine(rout))
	} else {
		logMsg("beat: %s", oneLine(rout))
	}
	if werr := writeBootLocked(root, filepath.Join(root, "BOOT.md"), now); werr != nil {
		logMsg("beat: BOOT.md could NOT be written: %v", werr)
		return werr
	}
	return nil
}

func startBeat(root string) {
	go func() {
		t := time.NewTicker(tickInterval)
		defer t.Stop()
		for range t.C {
			tickOnce(root, time.Now(), runDeskFetch)
		}
	}()
}
