package main

// boot_uncommitted.go - BOOT.md's uncommitted-work line. Architecture's go,
// 2026-09-13 (memo_build_boot-line-go-the-844-are-not-a-chore-and-a-bounced-
// answer-is-invisible), as scoped in Build's answer to the his-push letter.
//
// THE WATCHER DOES NOT DECIDE WHAT IS UNCOMMITTED. checks/uncommitted_receipt.py
// does, importing commit_guard.in_doc_set, and writes logs/uncommitted.json; the
// beat runs it and this only READS it. So the documentation-set rule exists in
// one language - a Go copy of it would be a second list, and they would drift.
//
// NEVER AN OMITTED LINE. A missing receipt, one that could not look, or one with
// no count prints NOT READ and says why. A real zero prints as zero, in words.
// An absent line and a zero look identical, which is the defect this exists to
// stop; a stale receipt says STALE.

import (
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"syscall"
	"time"
)

const uncommittedRel = "logs/uncommitted.json"
const uncommittedStaleAfter = 3 * tickInterval
const receiptTimeout = time.Minute

// The receipt's own clock format: Python's isoformat(timespec="seconds"), local time.
const receiptTimeLayout = "2006-01-02T15:04:05"

// runReceipt is a variable so a test can stand in for the Python run.
var runReceipt = runUncommittedReceipt

// runUncommittedReceipt execs `checks/uncommitted_receipt.py` with the project's
// venv Python, the same way runDeskFetch execs desk.py.
func runUncommittedReceipt(root string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), receiptTimeout)
	defer cancel()
	py := filepath.Join(root, "venv", "Scripts", "python.exe")
	cmd := exec.CommandContext(ctx, py, filepath.Join(root, "checks", "uncommitted_receipt.py"))
	cmd.Dir = root
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
	out, err := cmd.CombinedOutput()
	if ctx.Err() == context.DeadlineExceeded {
		err = fmt.Errorf("timed out after %s", receiptTimeout)
	}
	return string(out), err
}

func bootUncommittedLine(root string, now time.Time) string {
	const lead = "    uncommitted    "
	rec, why := bootJSON(root, uncommittedRel)
	if rec == nil {
		return lead + "NOT READ - " + why + " - " + uncommittedRel
	}
	at := jStr(rec, "at")
	state := jStr(rec, "state")
	if state != "ok" {
		if state == "" {
			state = "NO STATE RECORDED"
		}
		reason := jStr(rec, "reason")
		if reason == "" {
			reason = "no reason recorded"
		}
		return fmt.Sprintf("%sNOT READ - %s: %s (receipt %s, %s)", lead, state, bootClip(reason, 100), at, uncommittedRel)
	}
	n, docs := jStr(rec, "outside_doc_set"), jStr(rec, "doc_set")
	if n == "" || docs == "" {
		return lead + "NOT READ - the receipt says ok but carries no count - " + uncommittedRel
	}
	var line string
	if n == "0" {
		line = fmt.Sprintf("%s0 files outside the documentation set - nothing waits on his hand; %s doc-set", lead, docs)
	} else {
		old := "oldest NOT RECORDED"
		if o, err := time.ParseInLocation(receiptTimeLayout, jStr(rec, "outside_oldest"), time.Local); err == nil {
			old = fmt.Sprintf("oldest %s (%s)", o.Format("2006-01-02 15:04"), bootAge(now, o))
		}
		line = fmt.Sprintf("%s%s files outside the documentation set wait on his hand, %s; %s doc-set", lead, n, old, docs)
	}
	t, err := time.ParseInLocation(receiptTimeLayout, at, time.Local)
	if err != nil {
		return line + "  [receipt time UNREADABLE]  (" + uncommittedRel + ")"
	}
	if age := bootAge(now, t); age == "just now" {
		line += "  (measured just now)"
	} else {
		line += "  (measured " + age + " ago)"
	}
	if now.Sub(t) > uncommittedStaleAfter {
		line += fmt.Sprintf("  STALE - the beat runs every %d min", int(tickInterval.Minutes()))
	}
	return line + "  (" + uncommittedRel + ")"
}
