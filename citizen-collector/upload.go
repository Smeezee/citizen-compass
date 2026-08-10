package main

// upload.go - one click packages AND sends, then clears what was confirmed.
//
// # THE RULE THIS DOES NOT BREAK
//
// "Nothing is sent automatically. Export is manual, always."
//
// A person pressing SEND MY DATA is the manual act. This does not add
// background transmission, a schedule, or a silent retry - it removes the
// busywork of finding the zip afterwards. Nothing here runs unless somebody
// clicks, and with no endpoint configured nothing here runs at all.
//
// # CONFIRM BEFORE CLEARING, AND NEVER THE OTHER WAY ROUND
//
// Sleven asked for exactly this: "their data gets verified that it's complete,
// and then their storage gets wiped". The order is the whole point. The client
// sends a SHA256 of what it uploaded; the receiver computes its own over what
// it actually stored and hands it back. Only an exact match clears anything.
//
// A truncated upload, a proxy that mangled the body, a half-written object -
// all of them produce a different hash and all of them leave the sender's data
// exactly where it was. The failure mode is "you still have your data", which
// is the only acceptable direction for this to fail in.
//
// # ONLY WHAT WAS ACTUALLY SENT IS CLEARED
//
// Not "the captures folder". The exact files the zip contains, recorded as
// each one was written into it successfully. A frame captured while the zip
// was being built, or one held back by the not-the-game guard, is untouched.
//
// # ABOUT THE KEY, HONESTLY
//
// The upload key lives in a settings file on a machine somebody else owns. It
// is extractable, and pretending otherwise would be worse than saying so. What
// it buys is a closed door rather than an open one: it stops drive-by abuse of
// a public endpoint. It is not authentication and must not be treated as such,
// which is why the receiving end is built to accept ONLY uploads - it cannot
// list, read or delete anything even with the key in hand.

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// UploadReceipt is what the receiver returns.
type UploadReceipt struct {
	OK       bool   `json:"ok"`
	SHA256   string `json:"sha256"`
	Bytes    int64  `json:"bytes"`
	StoredAs string `json:"stored_as"`
	Message  string `json:"message"`
}

// UploadResult is what the window reports.
type UploadResult struct {
	Sent     bool   `json:"sent"`
	Cleared  int    `json:"cleared"`
	Freed    int64  `json:"freed_bytes"`
	StoredAs string `json:"stored_as"`

	// RowsMarkedSent is how many transaction rows MarkTxnsSent actually
	// cleared. Reported separately from Cleared (screenshots) because the two
	// are governed by different rules - see the note above MarkTxnsSent's
	// call below.
	RowsMarkedSent int `json:"rows_marked_sent"`

	Note string `json:"note"`
}

// SendExport uploads a finished export and clears what the receiver confirms.
//
// endpoint == "" means no sending is configured, which is a supported state,
// not an error: the zip is already on disk and the operator can hand it over
// however they like. That is exactly what happened before this file existed.
// clearAfterSend is honoured against C3's preservation work order of 2026-08-08.
//
// outDir is where gamelog-dataset.json lives. It is only ever touched AFTER
// the hash gate below confirms the receiver has a byte-identical copy - see
// the call to MarkTxnsSent.
//
// # WHY THIS BECAME A SETTING RATHER THAN STAYING A BEHAVIOUR
//
// The project now has a hard rule: "An importer may create a row and may update
// a row. It may never delete one." That rule is about the CATALOGUE - keeping
// the Aurora Mk I after CIG removes it - and it does not govern a contributor's
// screenshots. Checked deliberately rather than assumed, because a new hard
// rule landing the same hour as new deletion code is exactly when somebody
// should look.
//
// But the ETHIC behind it applies here, and it is worth honouring: this is the
// only code in the collector that destroys anything. It does so only after a
// receiver has confirmed a byte-identical copy, which is a stronger condition
// than the rule asks for - and it still leaves that machine with no copy of its
// own. If the receiving bucket is ever lost, those frames are gone.
//
// So it is a switch, and the person who owns the disk decides.
func SendExport(res ExportResult, outDir, endpoint, key, installID string, clearAfterSend bool,
	logf func(string, ...interface{})) (UploadResult, error) {

	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	var out UploadResult
	if strings.TrimSpace(endpoint) == "" {
		out.Note = "no send address is set, so the file is on your disk and yours to hand over"
		return out, nil
	}

	body, err := os.ReadFile(res.Path)
	if err != nil {
		return out, fmt.Errorf("could not read the export to send it: %w", err)
	}
	sum := sha256.Sum256(body)
	mine := hex.EncodeToString(sum[:])

	req, err := http.NewRequest("POST", endpoint, bytes.NewReader(body))
	if err != nil {
		return out, err
	}
	req.Header.Set("Content-Type", "application/zip")
	req.Header.Set("X-Collector-Sha256", mine)
	req.Header.Set("X-Collector-Install", installID)
	req.Header.Set("X-Collector-Version", Version)
	req.Header.Set("X-Collector-Filename", filepath.Base(res.Path))
	if strings.TrimSpace(key) != "" {
		req.Header.Set("X-Collector-Key", strings.TrimSpace(key))
	}

	logf("send: uploading %s (%d bytes)", filepath.Base(res.Path), len(body))
	// Generous, because somebody on a slow connection sending screenshots is a
	// normal case and a timeout mid-upload looks like a failure that is not one.
	client := &http.Client{Timeout: 10 * time.Minute}
	resp, err := client.Do(req)
	if err != nil {
		return out, fmt.Errorf("the upload did not go through (%w). Your data is "+
			"untouched and the file is still on your disk", err)
	}
	defer resp.Body.Close()
	rb, _ := io.ReadAll(io.LimitReader(resp.Body, 32*1024))
	if resp.StatusCode != 200 {
		return out, fmt.Errorf("the receiver said %d: %s. Nothing has been cleared",
			resp.StatusCode, strings.TrimSpace(string(rb)))
	}

	var rc UploadReceipt
	if err := json.Unmarshal(rb, &rc); err != nil {
		return out, fmt.Errorf("the receiver's reply could not be understood, so "+
			"nothing has been cleared: %w", err)
	}

	// THE GATE. Anything other than an exact match leaves everything alone.
	if !rc.OK || !strings.EqualFold(rc.SHA256, mine) {
		return out, fmt.Errorf("the receiver did not confirm the file arrived intact "+
			"(sent %s, it has %s). NOTHING has been cleared - send it again, or hand "+
			"the file over by other means",
			mine[:16]+"...", safePrefix(rc.SHA256))
	}
	out.Sent = true
	out.StoredAs = rc.StoredAs
	logf("send: confirmed - the receiver has the same file (%s)", mine[:16]+"...")

	// ROWS ARE MARKED SENT UNCONDITIONALLY - never gated behind
	// clear_after_send. That setting exists for screenshots, on a genuine
	// ethical question (should a contributor's only copy of a picture be
	// deleted). There is no equivalent question for dedup keys: leaving rows
	// un-marked because a PICTURE-retention switch happens to be off would
	// silently bring back the original bug this exists to fix - send #10
	// re-sending everything from sends #1-9 again.
	if n, merr := MarkTxnsSent(outDir, res.IncludedTxnKeys, logf); merr != nil {
		// NOT fatal to the send - the upload already succeeded and is
		// confirmed. Worst case here is redundant work next time, which is
		// the safe direction to fail in.
		logf("send: %v", merr)
	} else {
		out.RowsMarkedSent = n
		if n > 0 {
			logf("send: marked %d row(s) sent - they will not be exported again", n)
		}
	}

	// Confirmed. NOW clear the SCREENSHOTS - if the operator asked for that -
	// and only what was in the zip.
	if !clearAfterSend {
		out.Note = fmt.Sprintf("Sent and confirmed. %d row(s) marked sent. Pictures were "+
			"not cleared (clear_after_send is off).", out.RowsMarkedSent)
		logf("send: confirmed, and keeping the local pictures - clear_after_send is off")
		return out, nil
	}
	out.Cleared, out.Freed = clearIncluded(res.IncludedFiles)

	if out.Cleared > 0 {
		logf("send: cleared %d picture(s), %d MB freed - the dataset is kept, it is "+
			"small and it is what stops the same rows being counted twice later",
			out.Cleared, out.Freed/(1024*1024))
		out.Note = fmt.Sprintf("Sent and confirmed. %d row(s) marked sent, %d picture(s) "+
			"cleared, %d MB freed.", out.RowsMarkedSent, out.Cleared, out.Freed/(1024*1024))
	} else {
		out.Note = fmt.Sprintf("Sent and confirmed. %d row(s) marked sent.", out.RowsMarkedSent)
	}
	return out, nil
}

func safePrefix(s string) string {
	s = strings.TrimSpace(s)
	if s == "" {
		return "nothing"
	}
	if len(s) > 16 {
		return s[:16] + "..."
	}
	return s
}

// clearIncluded removes exactly the files named, and each one's sidecar.
//
// Split out from SendExport so the rule that decides what gets DELETED can be
// tested without a network. That is the only part of this file where a mistake
// costs somebody their data.
func clearIncluded(files []string) (int, int64) {
	var n int
	var freed int64
	for _, p := range files {
		fi, err := os.Stat(p)
		if err != nil {
			continue
		}
		if err := os.Remove(p); err != nil {
			continue
		}
		n++
		freed += fi.Size()
		// THE SIDECAR IS KEPT, AND THAT IS A REVERSAL.
		//
		// It used to be deleted alongside its picture, on the reasoning that an
		// orphan sidecar makes a folder unreadable. Review 2026-08-08 caught
		// what that missed: only PNGs are ever added to the zip, so a sidecar is
		// never hashed, never sent, and never confirmed by anyone - yet it was
		// being erased from the only disk in the world that held it.
		//
		// It carries the trigger, the patch, the build, the location and the
		// window record. Deleting an unsent thing breaks the one promise this
		// file exists to keep. A few KB of orphan JSON is the cheaper mistake.
	}
	return n, freed
}
