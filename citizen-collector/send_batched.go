package main

// send_batched.go - the notes go first, and the pictures go in pieces.
//
// ===========================================================================
// WHAT HAPPENED
// ===========================================================================
//
// Sleven pressed Send. It packaged 1,704,563,569 bytes and was refused 413.
//
// THE REFUSAL CAME FROM CLOUDFLARE, NOT FROM OUR WORKER. Their free plan caps a
// single request body at 100 MB - confirmed against Cloudflare's own limits
// page, which also names 413 as the response - and that cap applies at the edge,
// before a byte reaches any code we wrote. So MAX_BYTES was never the binding
// constraint and raising it would have fixed nothing.
//
// Three things were wrong, and only one of them was the size:
//
//  1. THE NOTES WERE HOSTAGE TO THE PICTURES. gamelog-dataset.json is 249 KB
//     and is the entire point of the project. It went in the same zip as 1.7 GB
//     of screenshots, so it had never once been sent on its own - and on its
//     own it would have succeeded instantly, every time, from the first day.
//
//  2. IT PACKAGED BEFORE IT CHECKED. 1.7 GB was written to disk and only then
//     discovered to be unsendable.
//
//  3. THE FAILED ZIP STAYED. Three of them were on his disk - 816 MB, 1.70 GB,
//     1.70 GB - 4.2 GB of derived files inside a 5.7 GB captures folder.
//
// ===========================================================================
// WHAT DOES NOT CHANGE
// ===========================================================================
//
// NOTHING IS DELETED THAT THE SERVER HAS NOT CONFIRMED. That rule does not bend
// for batching: each batch clears its own frames only after its own upload is
// confirmed, and a batch that fails leaves every frame it held exactly where it
// was. A failure part-way through means some batches are gone from the machine
// because they are safely on the server, and the rest are still here.
//
// The zip is the one thing that IS removed on failure - it is a derived file,
// rebuildable from data that is still on disk, and leaving gigabytes of them
// behind is what filled his drive.

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// uploadBatchTargetBytes is how much picture data goes in one request.
//
// Cloudflare's free-plan request body limit is 100 MB and our Worker's own
// ceiling is 64 MB. This sits under both with room to spare, because a zip of
// PNGs is very close to the sum of its inputs - PNG is already compressed, so
// there is no meaningful saving to count on and no reason to cut it fine.
const uploadBatchTargetBytes int64 = 48 * 1024 * 1024

// batchPlan is what a send is going to do, worked out BEFORE anything is
// written to disk.
type batchPlan struct {
	Batches    [][]string
	TotalBytes int64
	Frames     int
	// TooBig lists frames that cannot be sent in any batch, because one of them
	// alone exceeds the limit. Named rather than silently skipped.
	TooBig []string
}

// planUploadBatches groups frames into batches that will fit.
//
// PURE, so it can be driven with sizes that must fail it. Sorted by name first
// so the plan is deterministic: the same captures folder always produces the
// same batches, which is what makes a partial send resumable in a way a person
// can reason about.
func planUploadBatches(frames []string, sizeOf func(string) int64, target int64) batchPlan {
	var p batchPlan
	if target <= 0 {
		target = uploadBatchTargetBytes
	}
	names := append([]string(nil), frames...)
	sort.Strings(names)

	var cur []string
	var curBytes int64
	for _, f := range names {
		sz := sizeOf(f)
		if sz <= 0 {
			continue
		}
		p.TotalBytes += sz
		p.Frames++

		// ONE FILE BIGGER THAN A WHOLE BATCH can never be sent, and putting it
		// in a batch of its own would just move the refusal. Name it instead.
		if sz > target {
			p.TooBig = append(p.TooBig, f)
			continue
		}
		if curBytes+sz > target && len(cur) > 0 {
			p.Batches = append(p.Batches, cur)
			cur, curBytes = nil, 0
		}
		cur = append(cur, f)
		curBytes += sz
	}
	if len(cur) > 0 {
		p.Batches = append(p.Batches, cur)
	}
	return p
}

// SendEverything sends the notes, then the pictures in batches.
//
// Returns a sentence for the person and, separately, whether anything failed -
// because "the notes went and four batches of pictures went and one did not" is
// a real outcome that is neither success nor failure, and reporting it as
// either would be a lie.
func SendEverything(exeDir, outDir, sendURL, sendKey string, clearAfterSend bool,
	logf func(string, ...interface{})) (string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	// ------------------------------------------------------------------
	// 1. THE NOTES, ALONE, FIRST.
	// ------------------------------------------------------------------
	//
	// This is the upload that has never once been attempted separately, and it
	// is the one that carries everything the project exists to collect.
	logf("send: packaging the notes on their own first")
	notes, err := BuildExport(exeDir, outDir, outDir, false, logf)
	if err != nil {
		return "", fmt.Errorf("the notes could not be packaged: %w", err)
	}
	notesUp, err := SendExport(notes, outDir, sendURL, sendKey, notes.InstallID, false, logf)
	if err != nil {
		// The zip goes; the data stays.
		removeExportZip(notes.Path, logf)
		return "", fmt.Errorf("sending the notes failed: %w. Nothing was cleared and "+
			"your data is untouched", err)
	}
	removeExportZip(notes.Path, logf)
	if !notesUp.Sent {
		return "", fmt.Errorf("the server did not confirm the notes. Nothing was cleared")
	}
	logf("send: the notes are away - %s", notesUp.Note)

	// ------------------------------------------------------------------
	// 2. THE PICTURES, IN BATCHES, PLANNED BEFORE ANYTHING IS WRITTEN.
	// ------------------------------------------------------------------
	audit := listCaptures(outDir)
	// ONLY THE FRAMES THAT PROVED THEY PHOTOGRAPHED THE GAME. audit.Quaranti
	// holds the ones that did not, and that guard exists because the captures
	// folder once contained screenshots of a command prompt. Batching does not
	// get to relax it.
	plan := planUploadBatches(audit.OK, fileSize, uploadBatchTargetBytes)

	if plan.Frames == 0 {
		return "Your notes were sent. There are no pictures waiting.", nil
	}
	logf("send: %d picture(s), %d MB, in %d batch(es) of up to %d MB",
		plan.Frames, plan.TotalBytes/(1024*1024), len(plan.Batches),
		uploadBatchTargetBytes/(1024*1024))
	for _, f := range plan.TooBig {
		logf("send: %s is larger on its own than a whole batch, so it cannot be "+
			"sent and has been left alone", filepath.Base(f))
	}

	sentFrames, sentBytes, failed := 0, int64(0), 0
	for i, batch := range plan.Batches {
		logf("send: batch %d of %d - %d picture(s)", i+1, len(plan.Batches), len(batch))
		res, err := BuildExportBatch(exeDir, outDir, outDir, batch, logf)
		if err != nil {
			logf("send: batch %d could not be packaged (%v) - stopping here", i+1, err)
			failed++
			break
		}
		up, err := SendExport(res, outDir, sendURL, sendKey, res.InstallID, clearAfterSend, logf)
		removeExportZip(res.Path, logf)
		if err != nil || !up.Sent {
			// STOP, DO NOT CONTINUE. If one batch is refused the next is
			// likely to be refused for the same reason, and hammering an
			// endpoint that just said no is not persistence.
			if err != nil {
				logf("send: batch %d failed (%v). Nothing in it was cleared.", i+1, err)
			} else {
				logf("send: batch %d was not confirmed. Nothing in it was cleared.", i+1)
			}
			failed++
			break
		}
		sentFrames += len(batch)
		for _, f := range batch {
			sentBytes += fileSize(f)
		}
	}

	switch {
	case failed == 0:
		return fmt.Sprintf("Sent everything: your notes, and %d picture(s) in %d batch(es). "+
			"%d MB left this computer, and the pictures were removed only after the "+
			"server confirmed each batch.",
			sentFrames, len(plan.Batches), sentBytes/(1024*1024)), nil
	case sentFrames > 0:
		return fmt.Sprintf("Your notes were sent, and %d of %d picture(s) went before a "+
			"batch was refused.\n\nNothing that failed was deleted - those pictures are "+
			"still on this computer and will go next time.",
			sentFrames, plan.Frames), nil
	default:
		return "Your notes were sent. The pictures were refused, and none of them were " +
			"deleted - they are all still on this computer.", nil
	}
}

// removeExportZip deletes a package this program just wrote.
//
// SAFE BY CONSTRUCTION, and worth saying why: the zip is derived. Every byte in
// it either came from files still on disk, or has just been confirmed received
// by the server. It is never the only copy of anything.
//
// Three of these were sitting on Sleven's disk - 4.2 GB inside a 5.7 GB folder -
// because a failed send left its package behind and nothing ever came back for
// it.
func removeExportZip(path string, logf func(string, ...interface{})) {
	if path == "" {
		return
	}
	if !strings.HasSuffix(strings.ToLower(path), ".zip") {
		return
	}
	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		if logf != nil {
			logf("send: could not remove the package %s (%v) - it is safe to delete by hand",
				filepath.Base(path), err)
		}
	}
}

// CleanStaleExports removes export packages left behind by earlier failures.
//
// Only files this program names, only in its own output folder, and only zips.
// They are derived from data that is still on disk - a failed send clears
// nothing - so removing them loses nothing and returns the space.
func CleanStaleExports(outDir string, logf func(string, ...interface{})) (int, int64) {
	entries, err := os.ReadDir(outDir)
	if err != nil {
		return 0, 0
	}
	var n int
	var freed int64
	for _, e := range entries {
		name := e.Name()
		low := strings.ToLower(name)
		if !strings.HasSuffix(low, ".zip") || !strings.HasPrefix(low, "citizen-collector-export-") {
			continue
		}
		p := filepath.Join(outDir, name)
		fi, err := os.Stat(p)
		if err != nil {
			continue
		}
		if err := os.Remove(p); err != nil {
			continue
		}
		n++
		freed += fi.Size()
		if logf != nil {
			logf("cleanup: removed a leftover package %s (%d MB) - it was built from "+
				"data that is still here", name, fi.Size()/(1024*1024))
		}
	}
	return n, freed
}

// SendNotesOnly sends the dataset and nothing else.
//
// The same first step SendEverything takes, exposed on its own. It clears
// nothing, because a notes package contains no pictures - there is nothing of
// anybody's to remove.
func SendNotesOnly(exeDir, outDir, sendURL, sendKey string,
	logf func(string, ...interface{})) (string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	notes, err := BuildExport(exeDir, outDir, outDir, false, logf)
	if err != nil {
		return "", fmt.Errorf("the notes could not be packaged: %w", err)
	}
	up, err := SendExport(notes, outDir, sendURL, sendKey, notes.InstallID, false, logf)
	removeExportZip(notes.Path, logf)
	if err != nil {
		return "", fmt.Errorf("sending the notes failed: %w. Nothing was cleared", err)
	}
	if !up.Sent {
		return "", fmt.Errorf("the server did not confirm the notes. Nothing was cleared")
	}
	return "Your notes were sent. " + up.Note +
		"\n\nThe pictures are still on this computer and were not touched.", nil
}
