package main

// beat_isolation_test.go - a stalled GitHub read must never stall the mail path.
// Architecture's condition on the beat, 2026-09-12: "A slow or failed GitHub read
// must never stall or skip a mail cycle." Proven by breaking it, not by reading it.
//
// The only thing the beat and the mail path share is bootWriteMu, the BOOT.md write
// lock. tickOnce runs the fetch BEFORE it takes that lock, so while a fetch hangs
// the mail path's own BOOT.md write (writeBootLocked, which regenerateHandoff calls)
// must still finish at once. A beat that held the lock across the network call would
// freeze every mail cycle for as long as GitHub did.

import (
	"errors"
	"path/filepath"
	"testing"
	"time"
)

func TestAStalledFetchNeverBlocksTheMailPath(t *testing.T) {
	r := bootTree(t)
	beatLogger(t, r)
	release := make(chan struct{})
	entered := make(chan struct{})
	beatDone := make(chan error, 1)
	go func() {
		beatDone <- tickOnce(r, bootNow, func(string) (string, error) {
			close(entered)
			<-release // the network hangs here
			return "", errors.New("timed out after 2m0s")
		})
	}()
	<-entered

	mail := make(chan error, 1)
	go func() { mail <- writeBootLocked(r, filepath.Join(r, "BOOT.md"), bootNow) }()
	select {
	case err := <-mail:
		if err != nil {
			close(release)
			t.Fatalf("the mail path's BOOT.md write failed while a fetch hung: %v", err)
		}
	case <-time.After(3 * time.Second):
		close(release)
		t.Fatal("the mail path's BOOT.md write waited on a hung fetch - the beat is holding the lock across the network call")
	}

	close(release)
	select {
	case err := <-beatDone:
		if err != nil {
			t.Fatalf("after the hung fetch was released the beat did not write BOOT.md: %v", err)
		}
	case <-time.After(5 * time.Second):
		t.Fatal("the beat never finished after the fetch was released")
	}
}
