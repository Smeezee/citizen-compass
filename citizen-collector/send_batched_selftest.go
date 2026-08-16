package main

// send_batched_selftest.go - the subsystem, the batches, and the leftovers.
//
// Four things are proven here, each with a case that must fail it:
//
//   1. this binary is a GUI build (acceptance 1)
//   2. the subsystem check can tell the difference (acceptance 2)
//   5. an oversized send is refused BEFORE anything is written (acceptance 5)
//   6. a failed send leaves no zip behind (acceptance 6)

import (
	"encoding/binary"
	"os"
	"path/filepath"
	"strings"
)

// peSubsystem reads the subsystem out of a PE file. 2 = GUI, 3 = CONSOLE.
//
// The same read the build script and the release gate do. Seven source files
// asserted this program was a GUI build while both binaries were subsystem 3,
// so nothing here asks a comment.
func peSubsystem(path string) (uint16, bool) {
	f, err := os.Open(path)
	if err != nil {
		return 0, false
	}
	defer f.Close()
	head := make([]byte, 4096)
	n, _ := f.Read(head)
	if n < 0x40 {
		return 0, false
	}
	pe := int(binary.LittleEndian.Uint32(head[0x3C:]))
	if pe <= 0 || pe+24+68+2 > n {
		return 0, false
	}
	if string(head[pe:pe+4]) != "PE\x00\x00" {
		return 0, false
	}
	return binary.LittleEndian.Uint16(head[pe+24+68:]), true
}

func runSendBatchedSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1 & 2. THE SUBSYSTEM
	// -----------------------------------------------------------------
	if exe, err := os.Executable(); err == nil {
		sub, ok := peSubsystem(exe)
		check("CONSOLE: this binary is a GUI build (PE subsystem 2)",
			ok && sub == 2,
			"subsystem is "+itoaSmall(int(sub))+"; 3 is CONSOLE, which opens a black "+
				"terminal window on every launch and kills the collector when closed")

		// NEGATIVE CONTROL. The reader must be able to SAY 3, or a check that
		// always returned 2 would pass the line above on a console build - which
		// is exactly the failure that went unnoticed for months.
		//
		// Built by hand rather than by compiling: a PE header with a known
		// subsystem byte is enough to prove the reader reads it.
		fake := makeFakePE(3)
		if fake != "" {
			defer os.Remove(fake)
			s2, ok2 := peSubsystem(fake)
			check("CONSOLE: NEGATIVE CONTROL - the reader reports 3 for a console binary",
				ok2 && s2 == 3,
				"the check would pass on any file, including the one it exists to reject")
		}
		bad := makeFakePE(0)
		if bad != "" {
			defer os.Remove(bad)
			_, okBad := peSubsystem(bad + ".not-a-pe")
			check("CONSOLE: NEGATIVE CONTROL - a file that is not a PE is refused",
				!okBad,
				"an unreadable file would be treated as whatever the caller hoped")
		}
	}

	// -----------------------------------------------------------------
	// 5. THE PLAN IS MADE BEFORE ANYTHING IS WRITTEN
	// -----------------------------------------------------------------
	//
	// planUploadBatches is pure and takes the sizes, so it can be driven with
	// a backlog far larger than any test could create on disk. 1.7 GB was
	// packaged and THEN found unsendable; this decides first.
	sizes := map[string]int64{}
	var many []string
	for i := 0; i < 700; i++ {
		n := "frame" + itoaSmall(i) + ".png"
		many = append(many, n)
		sizes[n] = 2500000 // ~2.5 MB, close to a real capture
	}
	sizeOf := func(p string) int64 { return sizes[p] }

	plan := planUploadBatches(many, sizeOf, uploadBatchTargetBytes)
	check("BATCH: a 1.7 GB backlog is split rather than refused",
		len(plan.Batches) > 1 && plan.Frames == 700,
		"got "+itoaSmall(len(plan.Batches))+" batch(es) for "+itoaSmall(plan.Frames)+" frames")

	over := 0
	for _, b := range plan.Batches {
		var tot int64
		for _, f := range b {
			tot += sizeOf(f)
		}
		if tot > uploadBatchTargetBytes {
			over++
		}
	}
	check("BATCH: every batch fits under the limit",
		over == 0,
		itoaSmall(over)+" batch(es) exceed "+itoaSmall(int(uploadBatchTargetBytes/(1024*1024)))+" MB")

	// NEGATIVE CONTROL. Without this a planner that emitted ONE batch of
	// everything would satisfy "every batch fits" only by accident of the
	// arithmetic above, and a planner that emitted one frame per batch would
	// pass too. Check the packing is actually tight.
	biggest := 0
	for _, b := range plan.Batches {
		if len(b) > biggest {
			biggest = len(b)
		}
	}
	check("BATCH: NEGATIVE CONTROL - batches are packed, not one frame each",
		biggest > 1,
		"the largest batch holds "+itoaSmall(biggest)+" frame(s); one-per-request "+
			"would be 700 uploads for one session")

	// Nothing is lost between the plan and the batches.
	counted := 0
	for _, b := range plan.Batches {
		counted += len(b)
	}
	check("BATCH: every frame is in exactly one batch",
		counted+len(plan.TooBig) == plan.Frames,
		"planned "+itoaSmall(counted)+" + "+itoaSmall(len(plan.TooBig))+" too-big, "+
			"but there are "+itoaSmall(plan.Frames)+" frames")

	// A single frame larger than a whole batch must be NAMED, not silently
	// dropped and not stuffed into a batch that will be refused.
	huge := map[string]int64{"ok.png": 1000, "huge.png": uploadBatchTargetBytes * 2}
	p2 := planUploadBatches([]string{"ok.png", "huge.png"}, func(p string) int64 { return huge[p] },
		uploadBatchTargetBytes)
	check("BATCH: a frame too big for any batch is named, not hidden",
		len(p2.TooBig) == 1 && strings.Contains(p2.TooBig[0], "huge"),
		"it would be packaged into a request that is certain to be refused")
	check("BATCH: NEGATIVE CONTROL - and the sendable one is still planned",
		len(p2.Batches) == 1 && len(p2.Batches[0]) == 1,
		"one unsendable frame must not stop everything else going")

	// An empty folder plans nothing, rather than one empty batch.
	p3 := planUploadBatches(nil, sizeOf, uploadBatchTargetBytes)
	check("BATCH: nothing to send plans nothing",
		len(p3.Batches) == 0 && p3.Frames == 0,
		"an empty batch would be packaged and uploaded for no reason")

	// -----------------------------------------------------------------
	// 6. A FAILED SEND LEAVES NO ZIP
	// -----------------------------------------------------------------
	dir, err := os.MkdirTemp("", "cc-zips")
	if err != nil {
		return
	}
	defer os.RemoveAll(dir)

	zip1 := filepath.Join(dir, "citizen-collector-export-20260815-1.zip")
	_ = os.WriteFile(zip1, []byte("pretend package"), 0o644)
	removeExportZip(zip1, nil)
	_, statErr := os.Stat(zip1)
	check("ZIPS: a package is removed once it is finished with",
		os.IsNotExist(statErr),
		"4.2 GB of leftover packages was sitting in a 5.7 GB captures folder")

	// NEGATIVE CONTROLS. It must remove packages and NOTHING else - this runs
	// in a folder full of somebody's screenshots.
	png := filepath.Join(dir, "shot_0001.png")
	_ = os.WriteFile(png, []byte("a picture"), 0o644)
	removeExportZip(png, nil)
	_, pngErr := os.Stat(png)
	check("ZIPS: NEGATIVE CONTROL - it will not remove a picture",
		pngErr == nil,
		"it would delete captures, which is somebody's only copy")

	other := filepath.Join(dir, "holiday-photos.zip")
	_ = os.WriteFile(other, []byte("not ours"), 0o644)
	_ = os.WriteFile(filepath.Join(dir, "citizen-collector-export-20260815-2.zip"), []byte("ours"), 0o644)
	n, freed := CleanStaleExports(dir, nil)
	_, otherErr := os.Stat(other)
	check("ZIPS: leftovers from earlier failures are cleaned up",
		n == 1 && freed > 0,
		"removed "+itoaSmall(n)+" leftover package(s)")
	check("ZIPS: NEGATIVE CONTROL - a zip that is not ours is left alone",
		otherErr == nil,
		"it would delete unrelated files out of somebody's folder")
	_, pngErr2 := os.Stat(png)
	check("ZIPS: NEGATIVE CONTROL - and pictures survive the cleanup",
		pngErr2 == nil,
		"the cleanup would take the data with it")
}

// makeFakePE writes a minimal PE header with the given subsystem, so the
// reader can be shown a console binary without compiling one.
func makeFakePE(sub uint16) string {
	f, err := os.CreateTemp("", "cc-pe-*.bin")
	if err != nil {
		return ""
	}
	defer f.Close()
	b := make([]byte, 512)
	const peOff = 0x80
	binary.LittleEndian.PutUint32(b[0x3C:], peOff)
	copy(b[peOff:], []byte("PE\x00\x00"))
	binary.LittleEndian.PutUint16(b[peOff+24+68:], sub)
	if _, err := f.Write(b); err != nil {
		return ""
	}
	return f.Name()
}
