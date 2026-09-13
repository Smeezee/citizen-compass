package main

// boot_uncommitted_test.go - the DONE-WHEN for BOOT.md's uncommitted line
// (Architecture, 2026-09-13): it prints the count and the oldest age; it reads
// zero correctly and says so rather than omitting the line; a receipt that could
// not look is NOT READ, never zero; a stale one says STALE; and the beat writes
// the receipt BEFORE the page, without a failed receipt stopping the page.

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"citizencompass/pkg/pipelinelog"
)

func receiptLine(t *testing.T, body string) string {
	t.Helper()
	r := t.TempDir()
	if body != "" {
		bootPut(t, r, uncommittedRel, body)
	}
	return bootUncommittedLine(r, bootNow)
}

func TestUncommittedZeroIsPrintedNotOmitted(t *testing.T) {
	l := receiptLine(t, `{"at":"2026-09-12T22:55:00","state":"ok","outside_doc_set":0,"outside_oldest":null,"doc_set":4,"doc_set_oldest":null}`)
	if !strings.Contains(l, "0 files outside the documentation set - nothing waits on his hand") {
		t.Fatalf("a real zero is not printed as zero: %q", l)
	}
}

func TestUncommittedManyWithTheOldestAge(t *testing.T) {
	l := receiptLine(t, `{"at":"2026-09-12T22:55:00","state":"ok","outside_doc_set":12,"outside_oldest":"2026-08-30T11:10:00","doc_set":3,"doc_set_oldest":null}`)
	for _, want := range []string{"12 files outside the documentation set", "oldest 2026-08-30 11:10", "3 doc-set", "(measured 5 min ago)"} {
		if !strings.Contains(l, want) {
			t.Fatalf("line %q does not say %q", l, want)
		}
	}
	if strings.Contains(l, "STALE") {
		t.Fatalf("a five-minute-old receipt is marked STALE: %q", l)
	}
}

func TestUncommittedMissingReceiptIsNotRead(t *testing.T) {
	if l := receiptLine(t, ""); !strings.Contains(l, "uncommitted    NOT READ - MISSING") {
		t.Fatalf("a missing receipt is not NOT READ - MISSING: %q", l)
	}
}

func TestUncommittedDidNotLookIsNotReadNeverZero(t *testing.T) {
	l := receiptLine(t, `{"at":"2026-09-12T22:55:00","state":"did-not-look","reason":"git status timed out after 30s"}`)
	if !strings.Contains(l, "NOT READ - did-not-look: git status timed out after 30s") || strings.Contains(l, "0 files") {
		t.Fatalf("a receipt that could not look is not NOT READ, or reads as a zero: %q", l)
	}
}

func TestUncommittedOkWithoutACountIsNotRead(t *testing.T) {
	if l := receiptLine(t, `{"at":"2026-09-12T22:55:00","state":"ok"}`); !strings.Contains(l, "NOT READ - the receipt says ok but carries no count") {
		t.Fatalf("an ok receipt with no count is not refused: %q", l)
	}
}

func TestUncommittedUnreadableReceiptIsNotRead(t *testing.T) {
	if l := receiptLine(t, `{not json`); !strings.Contains(l, "NOT READ - UNREADABLE") {
		t.Fatalf("an unreadable receipt is not NOT READ - UNREADABLE: %q", l)
	}
}

func TestUncommittedStaleReceiptSaysStale(t *testing.T) {
	l := receiptLine(t, `{"at":"2026-09-12T21:00:00","state":"ok","outside_doc_set":5,"outside_oldest":"2026-09-01T10:00:00","doc_set":0,"doc_set_oldest":null}`)
	if !strings.Contains(l, "STALE") {
		t.Fatalf("a two-hour-old receipt is not marked STALE: %q", l)
	}
}

func receiptBeatLogger(t *testing.T, r string) {
	sLog := logger
	t.Cleanup(func() { logger, runReceipt = sLog, runUncommittedReceipt })
	logger = pipelinelog.New(r, "boot_uncommitted_test")
}

func TestTheBeatWritesTheReceiptBeforeThePage(t *testing.T) {
	r := bootTree(t)
	receiptBeatLogger(t, r)
	runReceipt = func(root string) (string, error) {
		bootPut(t, root, uncommittedRel, `{"at":"2026-09-12T22:59:50","state":"ok","outside_doc_set":42,"outside_oldest":"2026-09-01T10:00:00","doc_set":1,"doc_set_oldest":null}`)
		return "uncommitted: 42 outside", nil
	}
	if err := tickOnce(r, bootNow, func(string) (string, error) { return "fetch ok", nil }); err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(filepath.Join(r, "BOOT.md"))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(b), "42 files outside the documentation set") {
		t.Fatal("the page was written from an older receipt: the beat must run the receipt BEFORE the page")
	}
}

func TestAFailedReceiptDoesNotStopThePage(t *testing.T) {
	r := bootTree(t)
	receiptBeatLogger(t, r)
	runReceipt = func(string) (string, error) { return "", errors.New("planted failure") }
	if err := tickOnce(r, bootNow, func(string) (string, error) { return "fetch ok", nil }); err != nil {
		t.Fatalf("a failed receipt stopped the beat: %v", err)
	}
	b, err := os.ReadFile(filepath.Join(r, "BOOT.md"))
	if err != nil || !strings.Contains(string(b), "## WHAT IS UNCOMMITTED") {
		t.Fatal("a failed receipt stopped the page, or the page lost its uncommitted section")
	}
}
