//go:build master

// MASTER BUILD ONLY - Sleven's ruling, 2026-08-30.
//
// The learning half does not ship to crew. Not compiled-and-disabled: ABSENT.
// variant_crew.go states the principle for calibration, zone tuning, the review
// pen and the package generator, and it applies here for the same reason - a
// feature that is compiled out cannot be found by a curious crew member, and a
// pairs/ folder that cannot be written cannot be wondered about.
//
// Everything shared stays shared. This forks nothing: capture, logging, the
// send path and the scrub layer remain one implementation each.

package main

// pairstore_selftest.go - prove the pair store collapses, attaches, survives
// and REFUSES.
//
// Rule 12: a selftest that cannot fail is not a control. Each block below is
// written so that removing the behaviour it checks makes it go red, and the
// negative controls are the point rather than decoration:
//
//	collapse   the same pair twice must be ONE entry, not two
//	attach     a second VIEW must join the existing entry, not create one
//	survive    a store re-opened from disk must read what the first wrote,
//	           and a truncated final line must not lose the lines before it
//	refuse     an unlisted context must be REFUSED and SAID, not stored
//
// Every fixture writes to t.TempDir()-equivalent scratch under the OS temp
// directory and never touches a real pairs/ folder.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func runPairStoreSelftest(check func(name string, ok bool, detail string)) {
	root, err := os.MkdirTemp("", "cc-pairs-*")
	if err != nil {
		check("pairstore scratch dir", false, err.Error())
		return
	}
	defer os.RemoveAll(root)

	ps, err := NewPairStore(root)
	if err != nil {
		check("pairstore opens", false, err.Error())
		return
	}
	at := time.Date(2026, 8, 30, 12, 0, 0, 0, time.UTC)
	region := []byte("REGION-A-bytes")
	other := []byte("REGION-B-bytes")

	// --- 1. it records at all, from a named context ------------------------
	ok1, key1, err := ps.StorePair("Hazard-Zone Repeater", CtxInventory,
		region, 64, 32, "10487514", at)
	check("pair from a named context is recorded", ok1 && err == nil && key1 != "",
		detailOf(err))

	// --- 2. COLLAPSE: the same pair twice is one entry ----------------------
	ok2, key2, err2 := ps.StorePair("Hazard-Zone Repeater", CtxInventory,
		region, 64, 32, "10487514", at.Add(time.Minute))
	entries, _ := ps.Entries()
	check("the same pair twice collapses to ONE entry",
		ok2 && err2 == nil && key2 == key1 && len(entries) == 1,
		detailf("%d entr(ies)", len(entries)))

	// --- 3. ATTACH: a second VIEW joins rather than forking -----------------
	_, key3, err3 := ps.StorePair("Hazard-Zone Repeater", CtxInventory,
		other, 64, 32, "10487514", at.Add(2*time.Minute))
	entries, _ = ps.Entries()
	views := 0
	if len(entries) == 1 {
		views = len(entries[0].Views)
	}
	check("a second VIEW attaches to the existing entry",
		err3 == nil && key3 == key1 && len(entries) == 1 && views == 2,
		detailf("%d entr(ies), %d view(s)", len(entries), views))

	// A DIFFERENT LABEL MUST NOT COLLAPSE INTO IT. Without this, an
	// implementation that keyed on context alone would pass everything above.
	_, _, _ = ps.StorePair("Ballistic Repeater", CtxInventory, other,
		64, 32, "10487514", at.Add(3*time.Minute))
	entries, _ = ps.Entries()
	check("a different label is a different entry - the key is not the context",
		len(entries) == 2, detailf("%d entr(ies)", len(entries)))

	// --- 4. REFUSE: an unlisted context is declined and SAID ----------------
	stored, _, err4 := ps.StorePair("Someone's Handle", PairContext("chat_window"),
		region, 64, 32, "10487514", at.Add(4*time.Minute))
	entries, _ = ps.Entries()
	refusals, _ := ps.Refusals()
	check("an UNLISTED context is refused, not stored",
		!stored && err4 == nil && len(entries) == 2,
		detailf("stored=%v, %d entr(ies)", stored, len(entries)))
	check("and the store says WHICH context it refused",
		refusals["chat_window"] == 1,
		detailf("refusals=%v", refusals))

	// An empty label and an empty region are refused for the same reason: a
	// pair is a view AND a name, and half of one is not a smaller pair.
	s5, _, _ := ps.StorePair("", CtxInventory, region, 1, 1, "b", at)
	s6, _, _ := ps.StorePair("Name", CtxInventory, nil, 1, 1, "b", at)
	check("half a pair is refused - no label, or no view",
		!s5 && !s6, detailf("emptyLabel=%v emptyRegion=%v", s5, s6))

	// --- 5. SURVIVE: a new store on the same directory reads it -------------
	ps2, err5 := NewPairStore(root)
	if err5 != nil {
		check("pairstore re-opens", false, err5.Error())
		return
	}
	e2, err6 := ps2.Entries()
	check("a re-opened store reads what the first one wrote",
		err6 == nil && len(e2) == 2, detailf("%d entr(ies) after reopen", len(e2)))

	// APPEND-ONLY, PROVEN BY BYTES. A store that rewrote its index would pass
	// every assertion above; only the file itself shows the difference.
	idx := filepath.Join(root, "pairs", "pairs.jsonl")
	before, _ := os.ReadFile(idx)
	_, _, _ = ps2.StorePair("Another Thing", CtxShopKiosk, []byte("R3"),
		8, 8, "10487514", at.Add(5*time.Minute))
	after, _ := os.ReadFile(idx)
	check("the index is APPEND-ONLY - earlier bytes are unchanged",
		len(after) > len(before) && strings.HasPrefix(string(after), string(before)),
		detailf("%d -> %d bytes", len(before), len(after)))

	// --- 6. a truncated final line does not lose the lines before it --------
	if err := os.WriteFile(idx, append(after, []byte(`{"key":"broken`)...), 0o644); err == nil {
		ps3, _ := NewPairStore(root)
		e3, err7 := ps3.Entries()
		check("a truncated final line survives - the log before it still reads",
			err7 == nil && len(e3) == 3, detailf("%d entr(ies)", len(e3)))
	}

	// --- 7. the allowlist is a CLOSED set, checked by name ------------------
	// If somebody adds a context to the enum and forgets the allowlist, this
	// says so rather than the store silently refusing everything from it.
	for _, c := range []PairContext{CtxInventory, CtxItemInspect, CtxGroundPmt,
		CtxShopKiosk} {
		ok, _ := ContextAllowed(c)
		if !ok {
			check("every named context is on the allowlist", false, string(c))
			return
		}
	}
	check("every allowed context is on the allowlist", true, "4 contexts")

	// HUD TARGET IS DEFINED AND NOT ALLOWED, and that is the assertion.
	// A HUD target can be a player-piloted ship, so its label can be a person's
	// handle. nameclass.go cannot tell one from the other - measured
	// 2026-08-30: it swaps six of ten real item labels and still passes
	// "xX_Pilot_Xx" as an NPC role. So the context is off the list until
	// something can make that distinction, and this control is what stops it
	// being put back without one.
	hudOK, hudWhy := ContextAllowed(CtxHUDTarget)
	check("hud_target is DEFINED but NOT recordable - it can show a person",
		!hudOK, hudWhy)
	storedHUD, _, _ := ps.StorePair("Some Pilot", CtxHUDTarget, region,
		8, 8, "b", at.Add(6*time.Minute))
	check("and a hud_target pair is refused in practice, not just on paper",
		!storedHUD, detailf("stored=%v", storedHUD))

	// A DELTA IS ONE LINE, NOT THE WHOLE ENTRY AGAIN. Without this, the
	// quadratic growth that made a tenth sighting rewrite nine views would come
	// back unnoticed - every other assertion here passes either way.
	idx2 := filepath.Join(root, "pairs", "pairs.jsonl")
	b1, _ := os.ReadFile(idx2)
	_, _, _ = ps.StorePair("Hazard-Zone Repeater", CtxInventory,
		[]byte("REGION-C"), 8, 8, "b", at.Add(7*time.Minute))
	b2, _ := os.ReadFile(idx2)
	grew := len(b2) - len(b1)
	entries2, _ := ps.Entries()
	views2 := 0
	for _, e := range entries2 {
		if e.Label == "Hazard-Zone Repeater" {
			views2 = len(e.Views)
		}
	}
	check("a third view appends a DELTA - one view's worth, not the entry again",
		views2 == 3 && grew > 0 && grew < 320,
		detailf("%d view(s), index grew %d bytes", views2, grew))

	bad, why := ContextAllowed(PairContext("anything_else"))
	check("and an unnamed one is not, with a reason",
		!bad && strings.Contains(why, "not on the recorded list"), why)
}

func detailOf(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}

func detailf(f string, a ...interface{}) string {
	return fmt.Sprintf(f, a...)
}
