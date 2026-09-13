package main

// mail_commit_test.go - the beat schedules the filed-mail commit: it runs with
// --beat (the script keeps the hour), BEFORE the uncommitted receipt so the
// receipt counts what the commit left, and a failed run stops neither the
// receipt nor the page. What is committed is the script's to decide and its own
// self-test's to prove (checks/commit_filed_mail.py --self-test).

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"citizencompass/pkg/pipelinelog"
)

func mailBeatLogger(t *testing.T, r string) {
	sLog := logger
	t.Cleanup(func() {
		logger, runReceipt, runMailCommit = sLog, runUncommittedReceipt, runMailCommitPy
	})
	logger = pipelinelog.New(r, "mail_commit_test")
}

func TestTheBeatRunsTheMailCommitBeforeTheReceipt(t *testing.T) {
	r := bootTree(t)
	mailBeatLogger(t, r)
	var order []string
	runMailCommit = func(string) (string, error) {
		order = append(order, "mail")
		return "mail commit: committed - 3 path(s) at abc", nil
	}
	runReceipt = func(string) (string, error) {
		order = append(order, "receipt")
		return "uncommitted: 0 outside", nil
	}
	if err := tickOnce(r, bootNow, func(string) (string, error) { return "fetch ok", nil }); err != nil {
		t.Fatal(err)
	}
	if strings.Join(order, ",") != "mail,receipt" {
		t.Fatalf("the beat ran %v; the mail commit must run exactly once, BEFORE the receipt", order)
	}
}

func TestAFailedMailCommitStopsNeitherTheReceiptNorThePage(t *testing.T) {
	r := bootTree(t)
	mailBeatLogger(t, r)
	receipt := false
	runMailCommit = func(string) (string, error) { return "", errors.New("planted failure") }
	runReceipt = func(string) (string, error) { receipt = true; return "uncommitted: 0 outside", nil }
	if err := tickOnce(r, bootNow, func(string) (string, error) { return "fetch ok", nil }); err != nil {
		t.Fatalf("a failed mail commit stopped the beat: %v", err)
	}
	if !receipt {
		t.Fatal("a failed mail commit stopped the uncommitted receipt")
	}
	if _, err := os.Stat(filepath.Join(r, "BOOT.md")); err != nil {
		t.Fatal("a failed mail commit stopped the page")
	}
	log, _ := os.ReadFile(logger.Path())
	if !strings.Contains(string(log), "beat: mail commit FAILED") {
		t.Fatal("a failed mail commit was not logged as FAILED")
	}
}

func TestTheMailCommitRunsWithTheHourGate(t *testing.T) {
	a := mailCommitArgs(`C:\repo`)
	if len(a) != 2 || a[0] != filepath.Join(`C:\repo`, "checks", "commit_filed_mail.py") || a[1] != "--beat" {
		t.Fatalf("the beat must run checks/commit_filed_mail.py --beat and nothing else, got %v", a)
	}
}
