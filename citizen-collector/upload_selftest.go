package main

// upload_selftest.go - checks for send-then-clear.
//
// The network cannot be tested here. What CAN be, and what actually decides
// whether somebody loses data, is the clearing rule: what gets deleted, when,
// and what must survive. Every check below is about that.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func runUploadSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "send-")
	if err != nil {
		check("send: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	mk := func(name string) string {
		p := filepath.Join(tmp, name)
		_ = os.WriteFile(p, []byte("fake"), 0o644)
		return p
	}
	sent1, sent2 := mk("a.png"), mk("b.png")
	_ = mk("a.json")
	_ = mk("b.json")
	kept := mk("c.png") // taken while the zip was being written - must survive
	zipPath := mk("export.zip")

	// A row sitting in the dataset, as if BuildExport had just mined it and
	// handed its key back in IncludedTxnKeys.
	seedSt := newMineStore()
	seedSt.Txns = []MineTxn{{TS: "t1", Side: "buy", Market: "item", Shop: "s", Item: "i", Price: "10"}}
	rowKey := seedSt.Txns[0].key()
	_ = saveMineStore(tmp, seedSt)

	res := ExportResult{Path: zipPath, IncludedFiles: []string{sent1, sent2},
		IncludedTxnKeys: []string{rowKey}}

	// NO ENDPOINT = NO SENDING, AND NO CLEARING. This is the state every
	// machine is in by default and it must be completely inert.
	out, err := SendExport(res, tmp, "", "", "id", true, nil)
	check("send: with no address configured, nothing is sent and nothing cleared",
		err == nil && !out.Sent && out.Cleared == 0 && out.RowsMarkedSent == 0,
		"the default state must be inert")
	if _, e := os.Stat(sent1); e != nil {
		check("send: and the files are still there", false, "a.png was removed")
		return
	}
	check("send: and the files are still there", true, "nothing touched")

	// A FAILED SEND MUST NOT CLEAR. Pointed at an address that cannot work.
	_, err = SendExport(res, tmp, "http://127.0.0.1:9/nothing-here", "k", "id", true, nil)
	_, e1 := os.Stat(sent1)
	_, e2 := os.Stat(sent2)
	check("send: a failed upload clears NOTHING",
		err != nil && e1 == nil && e2 == nil,
		"the only acceptable way for this to fail is 'you still have your data'")
	check("send: and it says so plainly",
		err != nil && strings.Contains(err.Error(), "untouched"),
		"got: "+errText(err))

	// THE ROW MUST STILL BE THERE TOO. A failed upload leaves the dataset
	// exactly where it was, same as it leaves the screenshots - MarkTxnsSent
	// must never run before the hash gate confirms.
	stAfterFail, _ := loadMineStore(tmp)
	check("send: a failed upload marks NO rows sent",
		len(stAfterFail.Txns) == 1 && !stAfterFail.SentTxnKeys[rowKey],
		fmt.Sprintf("%d row(s) remain, sent-marked: %v", len(stAfterFail.Txns), stAfterFail.SentTxnKeys[rowKey]))

	// The clearing rule itself, exercised directly: only IncludedFiles, plus
	// each one's sidecar, and nothing else in the folder.
	cleared, freed := clearIncluded(res.IncludedFiles)
	check("send: clearing removes exactly what was in the zip",
		cleared == 2, "two files were included")
	// THE SIDECAR SURVIVES. This asserted the opposite until 2026-08-08, and
	// the assertion was written for behaviour that was itself the bug.
	//
	// Only PNGs are ever put in the zip. A sidecar is therefore never hashed,
	// never sent, and never confirmed by any receiver - so deleting it alongside
	// its picture erased the only copy in existence of the trigger, patch,
	// build, location and window record for that frame. clearIncluded exists to
	// remove things that have been safely received; an unsent file is exactly
	// what it must not touch.
	//
	// An orphan sidecar is a few KB of readable JSON. That is the cheaper
	// mistake by a wide margin.
	check("send: the sidecar SURVIVES, because it was never sent",
		exists(filepath.Join(tmp, "a.json")) && exists(filepath.Join(tmp, "b.json")),
		"deleting an unsent file destroys the only copy of that frame's record")
	check("send: a picture taken AFTER the zip was built survives",
		exists(kept),
		"clearing the folder rather than the manifest would have eaten it")
	check("send: the export zip itself is not deleted",
		exists(zipPath), "the operator may still want to hand it over")
	check("send: it reports how much was freed",
		freed > 0, "so the person can see the point of it")

	// NEGATIVE CONTROL. If clearIncluded deleted nothing at all, three of the
	// checks above would pass. Prove it actually removes things.
	check("NEGATIVE CONTROL: the files really were removed",
		!exists(sent1) && !exists(sent2),
		"the guard must clear the right things, not merely spare the wrong ones")
}

func exists(p string) bool { _, err := os.Stat(p); return err == nil }

func errText(e error) string {
	if e == nil {
		return "<nil>"
	}
	return e.Error()
}
