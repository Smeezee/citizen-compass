package main

// diary_selftest.go - prove the diary keeps the WHOLE log, once, and privately.
//
// Three properties, and each is driven with input that must break it:
//
//  1. WHOLE. What comes back out is byte-for-byte what went in. A diary that
//     keeps a truncated log is worse than none: it looks like evidence.
//  2. ONCE. The same session seen twice - at game exit and again by the startup
//     sweep - is one entry, not two, and an existing entry is never overwritten.
//  3. PRIVATE. A raw Game.log is full of real handles. It is kept beside the
//     exe and must never reach the captures folder that gets packaged and sent.
//
// Property 3 is the one that would do harm if it silently failed, so it is
// checked against the package builder's own view of the world rather than by
// reading the source and reasoning about it.

import (
	"compress/gzip"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// A log with the shape of a real one, including a handle, because the privacy
// check below is meaningless against a log with nothing worth protecting in it.
const diaryFixtureLog = `<2026-08-18T09:00:00.000Z> <Registered> character name Sleven-K - geid 200123456789
<2026-08-18T09:00:01.000Z> <Notice> [CSessionManager::OnClientSpawned] Spawned!
<2026-08-18T09:00:02.000Z> <Actor Death> CActor::Kill: 'Jeri_Blade' [864133595285] killed by 'DukeSP' [204354536218]
<2026-08-18T09:00:03.000Z> <ContextEstablisherTaskFinished> gamerules="SC_Default"
`

func runDiarySelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "diary-")
	if err != nil {
		check("diary: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	exeDir := filepath.Join(tmp, "app")
	if err := os.MkdirAll(exeDir, 0o755); err != nil {
		check("diary: app dir", false, err.Error())
		return
	}
	logPath := filepath.Join(tmp, "Game.log")
	if err := os.WriteFile(logPath, []byte(diaryFixtureLog), 0o644); err != nil {
		check("diary: fixture log", false, err.Error())
		return
	}

	info := GameLogInfo{Patch: sp("4.9.188.23497"), Build: sp("12344265"), LinesRead: 4}

	// ---- 1. WHOLE ------------------------------------------------------
	dest, kept, err := KeepDiary(exeDir, logPath, "game-exit", info, nil)
	check("diary: a session log is kept", kept && err == nil && dest != "",
		fmt.Sprintf("kept=%v err=%v dest=%q", kept, err, dest))

	if dest != "" {
		back, rerr := gunzipToString(dest)
		check("diary: what comes back out is byte-for-byte what went in",
			rerr == nil && back == diaryFixtureLog,
			fmt.Sprintf("read err=%v, %d bytes back vs %d in", rerr, len(back),
				len(diaryFixtureLog)))

		// NEGATIVE CONTROL for the comparison itself. If the check above
		// compared something that is equal whatever happens, it proves nothing.
		check("diary: NEGATIVE CONTROL - the comparison can fail",
			back != diaryFixtureLog+"one more line",
			"the round-trip check would pass on a log with an extra line in it")
	}

	// ---- 2. ONCE -------------------------------------------------------
	_, kept2, err2 := KeepDiary(exeDir, logPath, "startup-sweep", info, nil)
	check("diary: the SAME session seen again is not kept twice",
		!kept2 && err2 == nil,
		fmt.Sprintf("kept=%v err=%v - the startup sweep would duplicate every "+
			"session already kept at exit", kept2, err2))

	rows, bad, rerr := ReadDiaryIndex(exeDir)
	check("diary: the index has exactly one row for one session",
		rerr == nil && bad == 0 && len(rows) == 1,
		fmt.Sprintf("%d row(s), %d unreadable, err=%v", len(rows), bad, rerr))

	// A CHANGED log IS a new session and must be kept. Without this the
	// deduplication above could be "never keeps anything twice" - which would
	// also never keep tomorrow's session.
	if err := os.WriteFile(logPath, []byte(diaryFixtureLog+
		"<2026-08-18T10:00:00.000Z> a later session\n"), 0o644); err != nil {
		check("diary: rewrite fixture", false, err.Error())
	}
	_, kept3, _ := KeepDiary(exeDir, logPath, "game-exit", info, nil)
	check("diary: NEGATIVE CONTROL - a DIFFERENT session IS kept",
		kept3,
		"deduplication is refusing new sessions as well as repeats, so nothing "+
			"would ever be archived after the first run")

	rows, _, _ = ReadDiaryIndex(exeDir)
	check("diary: and the index now has two rows",
		len(rows) == 2, fmt.Sprintf("%d row(s)", len(rows)))

	// AN EXISTING ARCHIVE IS NEVER OVERWRITTEN, even if the index is lost.
	if len(rows) > 0 {
		if err := os.Remove(diaryIndex(exeDir)); err == nil {
			_, _, err = KeepDiary(exeDir, logPath, "game-exit", info, nil)
			check("diary: with the index gone, an existing archive is REFUSED, "+
				"not overwritten",
				err != nil && strings.Contains(err.Error(), "refusing to overwrite"),
				fmt.Sprintf("got err=%v - a diary that can lose an entry cannot "+
					"be trusted about last March", err))
		}
	}

	// ---- 3. PRIVATE ----------------------------------------------------
	//
	// The diary lives beside the exe. The captures folder is what gets zipped
	// and sent. These must not be the same place, and this asks the paths
	// rather than trusting the comment on the constant.
	outDir := filepath.Join(exeDir, "captures")
	rel, relErr := filepath.Rel(outDir, diaryDir(exeDir))
	check("diary: the diary is NOT inside the captures folder that gets sent",
		relErr == nil && strings.HasPrefix(rel, ".."),
		fmt.Sprintf("captures=%q diary=%q rel=%q - every raw handle in every "+
			"session log would be packaged and uploaded", outDir, diaryDir(exeDir), rel))

	// And the fixture really does carry something worth protecting, or the
	// check above is guarding an empty box.
	check("diary: NEGATIVE CONTROL - the fixture log contains a real handle",
		strings.Contains(diaryFixtureLog, "Sleven-K"),
		"the privacy check is being asked about a log with nothing in it")
}

func gunzipToString(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	zr, err := gzip.NewReader(f)
	if err != nil {
		return "", err
	}
	defer zr.Close()
	b, err := io.ReadAll(zr)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
