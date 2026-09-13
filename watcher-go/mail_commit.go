package main

// mail_commit.go - the beat commits the mail the router filed, at most once per
// clock hour. Architecture accepted the cadence 2026-09-13 (`..._three-
// architecture-rulings-b2-enable-cadence-readme-finish-brain.md`, section 2).
//
// THE WATCHER DOES NOT DECIDE WHAT IS COMMITTED. checks/commit_filed_mail.py
// does: it reads this watcher's own log, judges every path with
// commit_guard.in_doc_set, keeps the hour, refuses a busy index, a path outside
// the documentation set and an unapproved bulk batch, and commits through the
// real pre-commit guard. It never pushes. The beat only schedules it, exactly as
// it schedules the uncommitted receipt - a Go copy of those rules would be a
// second list, and they would drift.
//
// IT RUNS BEFORE THE RECEIPT, so BOOT.md's uncommitted line counts what is left
// after this hour's commit, not before it. A failed run does not stop the beat:
// the script writes its own logs/mail_commit.json, refusals included.

import (
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"syscall"
	"time"
)

const mailCommitTimeout = 3 * time.Minute

// runMailCommit is a variable so a test can stand in for the Python run.
var runMailCommit = runMailCommitPy

// mailCommitArgs is the one command line, so a test can hold it to --beat.
func mailCommitArgs(root string) []string {
	return []string{filepath.Join(root, "checks", "commit_filed_mail.py"), "--beat"}
}

func runMailCommitPy(root string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), mailCommitTimeout)
	defer cancel()
	py := filepath.Join(root, "venv", "Scripts", "python.exe")
	cmd := exec.CommandContext(ctx, py, mailCommitArgs(root)...)
	cmd.Dir = root
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
	out, err := cmd.CombinedOutput()
	if ctx.Err() == context.DeadlineExceeded {
		err = fmt.Errorf("timed out after %s", mailCommitTimeout)
	}
	return string(out), err
}
