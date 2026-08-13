package main

// sent_rows_selftest.go - checks for the fix to the resend defect: every
// export used to carry the entire history, forever, because nothing marked a
// row as delivered. See gamelog_mine.go's SentTxnKeys, MarkTxnsSent and
// dedupAgainstSent, and upload.go's SendExport.
//
// EVERY CHECK HAS A NEGATIVE CONTROL. Hard rule 12: a check that cannot fail
// is not a check, and this is exactly the kind of defect a check that always
// passes would hide - "the export contains data" is true whether the row is
// new or the ninth repeat of something already sent.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func txnFixture(ts, price string) MineTxn {
	return MineTxn{TS: ts, Side: "buy", Market: "item", Shop: "SCShop_Test", Item: "test_item", Price: price}
}

// --- 1. an export only ever carries unflagged rows -------------------------

func runSentRowsExportSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "sent-rows-")
	if err != nil {
		check("sent-rows: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	// ISOLATE THE FILESYSTEM, FOR REAL THIS TIME.
	//
	// Seeding the store directly is not enough and never was: BuildExport calls
	// MineAll, which calls the target scan, so on a machine with the game
	// installed the whole archive was mined into this temp folder and these
	// checks found 309 rows where they had planted 1. They passed only where
	// there was no game to find.
	//
	// Replacing the scan is what makes "the export carries exactly the row I
	// seeded" a statement about the export rather than about whoever's laptop
	// is running it.
	savedTargets := mineTargets
	mineTargets = func() []string { return nil }
	defer func() { mineTargets = savedTargets }()

	st := newMineStore()
	st.Txns = []MineTxn{txnFixture("t1", "1000")}
	if err := saveMineStore(tmp, st); err != nil {
		check("sent-rows: seed store", false, err.Error())
		return
	}

	res, err := BuildExport(tmp, tmp, tmp, false, nil)
	if err != nil {
		check("sent-rows: first export builds", false, err.Error())
		return
	}
	check("sent-rows: first export carries the one pending row",
		res.Rows == 1 && len(res.IncludedTxnKeys) == 1,
		fmt.Sprintf("rows=%d keys=%d", res.Rows, len(res.IncludedTxnKeys)))

	// SIMULATE THE RECEIVER CONFIRMING. This is the exact call SendExport
	// makes after its hash gate passes - exercised directly here so this
	// check does not depend on a live network round trip.
	marked, err := MarkTxnsSent(tmp, res.IncludedTxnKeys, nil)
	check("sent-rows: confirming marks exactly the exported row",
		err == nil && marked == 1, fmt.Sprintf("marked=%d err=%v", marked, err))

	stAfter, err := loadMineStore(tmp)
	check("sent-rows: the row's CONTENT is gone from the local store",
		err == nil && len(stAfter.Txns) == 0,
		fmt.Sprintf("%d row(s) remain (want 0)", len(stAfter.Txns)))
	check("sent-rows: the row's KEY survives the confirm",
		stAfter.SentTxnKeys[txnFixture("t1", "1000").key()],
		fmt.Sprintf("sent_txn_keys: %v", stAfter.SentTxnKeys))

	// THE ACTUAL REQUIREMENT: the next export must NOT resend it.
	res2, err := BuildExport(tmp, tmp, tmp, false, nil)
	if err != nil {
		check("sent-rows: second export builds", false, err.Error())
		return
	}
	check("sent-rows: the NEXT export contains only unflagged rows - zero here",
		res2.Rows == 0 && len(res2.IncludedTxnKeys) == 0,
		fmt.Sprintf("second export carried %d row(s) (want 0 - this is send #10 "+
			"re-sending sends #1-9, the defect this fixes)", res2.Rows))

	// NEGATIVE CONTROL: a genuinely NEW row, arriving after the confirm, must
	// still go out. Without this, "the export is empty" could just as easily
	// mean the export mechanism is broken as mean it is working correctly.
	stNow, _ := loadMineStore(tmp)
	stNow.Txns = append(stNow.Txns, txnFixture("t2", "500"))
	_ = saveMineStore(tmp, stNow)
	res3, err := BuildExport(tmp, tmp, tmp, false, nil)
	check("NEGATIVE CONTROL: a genuinely new row IS still exported",
		err == nil && res3.Rows == 1 && len(res3.IncludedTxnKeys) == 1,
		fmt.Sprintf("rows=%d (want 1 - the sent-filter must not eat unrelated rows)", res3.Rows))
}

// --- 2. resurrection: re-reading the same archive must not bring rows back -

func runSentRowsResurrectionSelftest(check func(name string, ok bool, detail string)) {
	sentKey := txnFixture("t1", "1000").key()
	sent := map[string]bool{sentKey: true}

	// The exact scenario this whole feature exists to stop: the same log line
	// gets mined again (the archive on disk does not change, and MineAll
	// re-reads it every session), producing the identical row a second time.
	resurfaced := []MineTxn{txnFixture("t1", "1000")}
	out, alreadySent := dedupAgainstSent(resurfaced, sent)
	check("sent-rows: a row already sent does NOT resurrect on re-scan",
		len(out) == 0 && alreadySent == 1,
		fmt.Sprintf("%d row(s) survived, %d counted as already-sent (want 0/1)",
			len(out), alreadySent))

	// NEGATIVE CONTROL: an UNRELATED row mined in the same pass must survive.
	// If dedupAgainstSent dropped everything regardless of key, the check
	// above would pass for the wrong reason.
	mixed := []MineTxn{txnFixture("t1", "1000"), txnFixture("t2", "500")}
	out2, alreadySent2 := dedupAgainstSent(mixed, sent)
	check("NEGATIVE CONTROL: an unrelated row in the same pass is kept",
		len(out2) == 1 && out2[0].key() == txnFixture("t2", "500").key() && alreadySent2 == 1,
		fmt.Sprintf("%d row(s) kept (want 1, the new one)", len(out2)))

	// In-run duplicates (never sent, just seen twice this pass) still collapse
	// to one - the sent-filter must not have replaced the original dedup.
	dup := []MineTxn{txnFixture("t2", "500"), txnFixture("t2", "500")}
	out3, alreadySent3 := dedupAgainstSent(dup, map[string]bool{})
	check("sent-rows: plain in-run duplicates still collapse to one",
		len(out3) == 1 && alreadySent3 == 0,
		fmt.Sprintf("%d row(s) (want 1), alreadySent=%d (want 0)", len(out3), alreadySent3))
}

// --- 3. MarkTxnsSent itself: exact rows, no more, no less -------------------

func runMarkTxnsSentSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "mark-sent-")
	if err != nil {
		check("mark-sent: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	a, b := txnFixture("t1", "1000"), txnFixture("t2", "500")
	st := newMineStore()
	st.Txns = []MineTxn{a, b}
	_ = saveMineStore(tmp, st)

	// Mark only ONE of the two rows, as a partial confirm would - proves
	// MarkTxnsSent acts on the exact keys given, not "everything pending".
	marked, err := MarkTxnsSent(tmp, []string{a.key()}, nil)
	check("mark-sent: marks exactly the row named, not the whole store",
		err == nil && marked == 1, fmt.Sprintf("marked=%d err=%v", marked, err))

	st2, _ := loadMineStore(tmp)
	check("mark-sent: the OTHER row is untouched",
		len(st2.Txns) == 1 && st2.Txns[0].key() == b.key(),
		fmt.Sprintf("%d row(s) remain: %v", len(st2.Txns), keysOfTxnsForTest(st2.Txns)))
	check("mark-sent: only the confirmed key was recorded as sent",
		st2.SentTxnKeys[a.key()] && !st2.SentTxnKeys[b.key()],
		fmt.Sprintf("sent_txn_keys: %v", st2.SentTxnKeys))

	// NEGATIVE CONTROL: a key that matches NOTHING currently in the store
	// (already cleared by an earlier run, or simply wrong) must not error and
	// must not touch the remaining row. "Nothing to do" is a valid outcome.
	marked2, err2 := MarkTxnsSent(tmp, []string{"no-such-key"}, nil)
	st3, _ := loadMineStore(tmp)
	check("NEGATIVE CONTROL: an unmatched key marks nothing and errors nothing",
		err2 == nil && marked2 == 0 && len(st3.Txns) == 1,
		fmt.Sprintf("marked=%d err=%v rows=%d", marked2, err2, len(st3.Txns)))

	// Empty key list - the shape SendExport would pass if BuildExport ran
	// with zero rows. Must be a safe no-op, not a call that wipes the store.
	marked3, err3 := MarkTxnsSent(tmp, nil, nil)
	st4, _ := loadMineStore(tmp)
	check("sent-rows: MarkTxnsSent with no keys is a safe no-op",
		err3 == nil && marked3 == 0 && len(st4.Txns) == 1,
		fmt.Sprintf("marked=%d err=%v rows=%d", marked3, err3, len(st4.Txns)))
}

func keysOfTxnsForTest(txns []MineTxn) []string {
	out := make([]string, 0, len(txns))
	for _, t := range txns {
		out = append(out, t.key())
	}
	return out
}

// --- 4. the panel's pending count is derived, not tracked -------------------

func runPendingRowsPanelSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "pending-panel-")
	if err != nil {
		check("pending-panel: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	// Nothing on disk yet - the panel must read this as zero, not error.
	d := uiDeps{outDir: tmp, gameAlive: func() error { return fmt.Errorf("no game") },
		findLog: func() (string, string) { return "", "" }}
	s0 := buildUIState(d)
	check("pending-panel: reads 0 pending rows with no dataset on disk",
		s0.PendingRows == 0, fmt.Sprintf("got %d", s0.PendingRows))

	st := newMineStore()
	st.Txns = []MineTxn{txnFixture("t1", "1000"), txnFixture("t2", "500")}
	_ = saveMineStore(tmp, st)
	s1 := buildUIState(d)
	check("pending-panel: reflects the rows actually pending",
		s1.PendingRows == 2, fmt.Sprintf("got %d (want 2)", s1.PendingRows))

	// NEGATIVE CONTROL: after those rows are confirmed sent, the SAME
	// function must report 0 again, proving the count is read fresh each
	// time rather than cached from the moment the two rows were written.
	keys := keysOfTxnsForTest(st.Txns)
	_, _ = MarkTxnsSent(tmp, keys, nil)
	s2 := buildUIState(d)
	check("NEGATIVE CONTROL: after confirming, the panel drops back to 0",
		s2.PendingRows == 0,
		fmt.Sprintf("got %d (want 0 - a stale cached count would still show 2)", s2.PendingRows))
}

// --- 5. PRIVACY: SentTxnKeys must never reach a zip -------------------------
//
// Found while building this feature, not after shipping it. ScrubForExport
// makes a SHALLOW copy of the store (`out := *st`) and only rebuilds the maps
// it explicitly touches. SentTxnKeys was not one of them, so without the fix
// in scrub.go it would ride along into every future export - and a key is
// built from RAW, PRE-SCRUB Shop and Item text (see txnKeys), so a shop name
// that is not asset-shaped and would otherwise have been pseudonymised in
// Txns could leave the machine anyway, hidden inside a field nobody thought
// to look at because "the export contains data" looks correct either way.
func runSentRowsExportPrivacySelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "sent-rows-privacy-")
	if err != nil {
		check("sent-rows privacy: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	// A shop name shaped like a PERSON, not a game asset - exactly what
	// ScrubForExport's Shop/Item pseudonymisation exists to catch. If this
	// string appears anywhere in an export, something bypassed the scrubber.
	const personShapedShop = "dark_wolf_77_shopfront"

	st := newMineStore()
	st.Txns = []MineTxn{{TS: "t1", Side: "buy", Market: "item",
		Shop: personShapedShop, Item: "test_item", Price: "10"}}
	sentKey := st.Txns[0].key()
	st.Txns = nil // this row is already sent - only its key remains
	st.SentTxnKeys = map[string]bool{sentKey: true}
	if err := saveMineStore(tmp, st); err != nil {
		check("sent-rows privacy: seed store", false, err.Error())
		return
	}

	// A second, currently-pending row, so the export actually writes a
	// non-empty file - an export with nothing in it would pass the checks
	// below for the wrong reason.
	st2, _ := loadMineStore(tmp)
	st2.Txns = append(st2.Txns, txnFixture("t2", "500"))
	_ = saveMineStore(tmp, st2)

	res, err := BuildExport(tmp, tmp, tmp, false, nil)
	if err != nil {
		check("sent-rows privacy: export builds", false, err.Error())
		return
	}
	body := zipEntry(res.Path, "gamelog-dataset.json")
	check("PRIVACY: SentTxnKeys is not present in the exported dataset at all",
		!strings.Contains(body, "sent_txn_keys"),
		"the field must be cleared before the copy is marshalled, not merely relied on to be harmless")
	check("PRIVACY: the person-shaped shop name hidden inside a sent key does not leak",
		!strings.Contains(body, personShapedShop),
		fmt.Sprintf("checked for %q in the exported JSON", personShapedShop))

	// NEGATIVE CONTROL: the detector itself must be capable of catching a
	// leak, or the two checks above are meaningless. Prove it against the
	// LOCAL (unscrubbed) store, which legitimately does carry both.
	raw, _ := os.ReadFile(filepath.Join(tmp, "gamelog-dataset.json"))
	check("NEGATIVE CONTROL: the local store DOES carry sent_txn_keys (that's the point of it)",
		strings.Contains(string(raw), "sent_txn_keys") && strings.Contains(string(raw), sentKey[:8]),
		"if the local store did not have it either, the two PRIVACY checks above would prove nothing")
}
