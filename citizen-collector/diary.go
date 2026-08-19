package main

// diary.go - keep the whole session log, compressed, forever, on this computer.
//
// ===========================================================================
// V1 §3: KEEP THE WHOLE DIARY
// ===========================================================================
//
// The miner reads Game.log and keeps the fields it understands. Everything else
// - every line it has no pattern for - is read and dropped. Then Star Citizen
// overwrites Game.log on the next launch and that session is gone for good.
//
// So the collector currently keeps what it already knew how to want. Anything
// learned later can only be applied to sessions that have not happened yet.
//
// THIS IS THE SAME ARGUMENT AS THE APPEND-ONLY HISTORY, one layer down: the
// value is in elapsed time and it cannot be backfilled. A better parser written
// in March can be re-run over a diary kept since August. It cannot be re-run
// over logs the game has already overwritten.
//
// ===========================================================================
// IT IS AFFORDABLE, MEASURED RATHER THAN ASSUMED
// ===========================================================================
//
// Against 241 real sessions in Sleven's own logbackups, 2026-08-16:
//
//	total raw            206.7 MB
//	mean per session      0.86 MB     median 0.50 MB
//	largest session       8.66 MB
//	gzip ratio            6.5%        (measured on the 12 largest, worst case)
//
//	241 sessions  206.7 MB raw  ->  13.5 MB gzipped
//	a year at 3 sessions/week   ->  134 MB raw, 9 MB gzipped
//
// 13.5 MB against 1.8 GB of screenshots on the same machine is 0.7%. Logs
// compress to a fifteenth of their size because they are enormously repetitive.
//
// ===========================================================================
// THE DIARY NEVER LEAVES THIS COMPUTER
// ===========================================================================
//
// A raw Game.log is full of real handles, account ids, shard ids and everything
// else the name swap exists to keep out of the export. The scrubbed dataset is
// what travels; the diary is the person's own file, kept for the person's own
// tool to re-read later.
//
// So: it is written OUTSIDE the captures folder that gets packaged, and there is
// a check that a package cannot contain one. If that check ever fails, the
// diary has become a leak and the feature is worth less than the harm.

import (
	"compress/gzip"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// diaryDirName sits beside the exe, NOT inside the captures folder.
//
// package.go zips the captures folder. Putting the diary in it would send every
// session's raw log, with every handle in it, to the receiver - the exact thing
// the write-time name swap exists to prevent, arriving by a different door.
const diaryDirName = "diary"

// diaryIndexName is the append-only record of what has been kept.
//
// SAME SPINE AS THE OTHER TWO HISTORIES - at, kind, subject, name, fingerprint,
// source - so the roadmap watcher's rows, the model fingerprints' rows and these
// can be read as one time series. See roadmap-watcher/history.go.
const diaryIndexName = "diary-index.jsonl"

// DiaryEntry is one session log, as it was kept.
type DiaryEntry struct {
	At          string `json:"at"`
	Kind        string `json:"kind"`    // "session-log"
	Subject     string `json:"subject"` // the sha256, which IS the identity
	Name        string `json:"name"`    // the archive's file name
	Fingerprint string `json:"fingerprint"`
	Source      string `json:"source"` // "game-exit" | "startup-sweep"

	FromPath string `json:"from_path"`
	Bytes    int64  `json:"bytes"`
	GzBytes  int64  `json:"gz_bytes"`
	Patch    string `json:"patch,omitempty"`
	Build    string `json:"build,omitempty"`
	Lines    int    `json:"lines,omitempty"`
}

func diaryDir(exeDir string) string { return filepath.Join(exeDir, diaryDirName) }
func diaryIndex(exeDir string) string {
	return filepath.Join(diaryDir(exeDir), diaryIndexName)
}

// sha256File is the identity of a session log.
//
// KEYED ON CONTENT, NOT ON A TIMESTAMP OR A PATH. The same log can be seen twice
// - once by the startup sweep and once at game exit - and both must resolve to
// one archive rather than two copies of the same session. Content is the only
// thing that says "this is that log" when the path is always Game.log and the
// mtime moves.
func sha256File(path string) (string, int64, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", 0, err
	}
	defer f.Close()
	h := sha256.New()
	n, err := io.Copy(h, f)
	if err != nil {
		return "", 0, err
	}
	return hex.EncodeToString(h.Sum(nil)), n, nil
}

// KeepDiary archives one Game.log if it has not been kept already.
//
// Returns (archivePath, kept, error). kept=false with a nil error means it was
// already in the diary - the normal case for a startup sweep after a clean exit.
//
// NEVER OVERWRITES. If the target name somehow exists with different content the
// write is refused and reported, because a diary that can lose an entry is a
// diary nobody can trust to answer a question about last March.
func KeepDiary(exeDir, logPath, source string, info GameLogInfo,
	logf func(string, ...interface{})) (string, bool, error) {

	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	st, err := os.Stat(logPath)
	if err != nil {
		return "", false, fmt.Errorf("no log to keep at %s: %w", logPath, err)
	}
	if st.Size() == 0 {
		// An empty log is not a session. Keeping it would put a row in the
		// index that answers no question and looks like a session that
		// produced nothing.
		return "", false, nil
	}

	sum, size, err := sha256File(logPath)
	if err != nil {
		return "", false, fmt.Errorf("could not read %s to keep it: %w", logPath, err)
	}

	if err := os.MkdirAll(diaryDir(exeDir), 0o755); err != nil {
		return "", false, err
	}

	// ALREADY KEPT? Asked of the index, which is the record, rather than of the
	// directory listing, which is a guess.
	if seen, err := diaryHas(exeDir, sum); err == nil && seen {
		return "", false, nil
	}

	name := fmt.Sprintf("%s_%s_%s.log.gz",
		st.ModTime().UTC().Format("20060102T150405Z"),
		safeForFileName(strDeref(info.Patch)), sum[:8])
	dest := filepath.Join(diaryDir(exeDir), name)

	if _, err := os.Stat(dest); err == nil {
		return dest, false, fmt.Errorf("%s already exists - refusing to overwrite "+
			"a diary entry", name)
	}

	// WRITTEN TO A TEMP NAME AND RENAMED. A half-written .gz from a power cut
	// would be indistinguishable from a corrupt session, and the index would
	// claim it was kept.
	tmp := dest + ".part"
	if err := gzipFile(logPath, tmp); err != nil {
		_ = os.Remove(tmp)
		return "", false, err
	}
	if err := os.Rename(tmp, dest); err != nil {
		_ = os.Remove(tmp)
		return "", false, err
	}
	gz, _ := os.Stat(dest)
	var gzSize int64
	if gz != nil {
		gzSize = gz.Size()
	}

	entry := DiaryEntry{
		At:          time.Now().UTC().Format(time.RFC3339),
		Kind:        "session-log",
		Subject:     sum,
		Name:        name,
		Fingerprint: sum[:16],
		Source:      source,
		FromPath:    logPath,
		Bytes:       size,
		GzBytes:     gzSize,
		Patch:       strDeref(info.Patch),
		Build:       strDeref(info.Build),
		Lines:       info.LinesRead,
	}
	if err := appendDiaryIndex(exeDir, entry); err != nil {
		// The archive is on disk and the index is not. Say so loudly: the file
		// is recoverable by hand, and silence here would leave a diary entry
		// nothing knows about.
		logf("diary: kept %s but could NOT record it in the index (%v) - the "+
			"file is there and the index is short one row", name, err)
		return dest, true, nil
	}

	pct := 0.0
	if size > 0 {
		pct = float64(gzSize) / float64(size) * 100
	}
	logf("diary: kept the whole session log - %s (%.1f MB -> %.2f MB, %.1f%%)",
		name, float64(size)/(1<<20), float64(gzSize)/(1<<20), pct)
	return dest, true, nil
}

func gzipFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()
	zw := gzip.NewWriter(out)
	zw.Name = filepath.Base(src)
	if _, err := io.Copy(zw, in); err != nil {
		zw.Close()
		return err
	}
	if err := zw.Close(); err != nil {
		return err
	}
	return out.Sync()
}

// appendDiaryIndex adds one row. O_APPEND, like every other history in this
// project - see roadmap-watcher/history.go for the argument.
func appendDiaryIndex(exeDir string, e DiaryEntry) error {
	f, err := os.OpenFile(diaryIndex(exeDir),
		os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	b, err := json.Marshal(e)
	if err != nil {
		return err
	}
	if _, err := f.Write(append(b, '\n')); err != nil {
		return err
	}
	return f.Sync()
}

// ReadDiaryIndex returns every row, and how many lines were unreadable.
//
// A bad line is skipped and counted, never fatal - this file is meant to be
// years old, and one truncated row from a power cut must not hide the rest.
func ReadDiaryIndex(exeDir string) ([]DiaryEntry, int, error) {
	b, err := os.ReadFile(diaryIndex(exeDir))
	if os.IsNotExist(err) {
		return nil, 0, nil
	}
	if err != nil {
		return nil, 0, err
	}
	var out []DiaryEntry
	bad := 0
	for _, line := range strings.Split(string(b), "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		var e DiaryEntry
		if err := json.Unmarshal([]byte(line), &e); err != nil {
			bad++
			continue
		}
		out = append(out, e)
	}
	return out, bad, nil
}

func diaryHas(exeDir, sum string) (bool, error) {
	rows, _, err := ReadDiaryIndex(exeDir)
	if err != nil {
		return false, err
	}
	for _, r := range rows {
		if r.Subject == sum {
			return true, nil
		}
	}
	return false, nil
}

func strDeref(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}

// safeForFileName keeps a patch string usable as part of a file name without
// inventing one when it is absent.
func safeForFileName(s string) string {
	s = strings.TrimSpace(s)
	if s == "" {
		return "unknown-patch"
	}
	var b strings.Builder
	for _, r := range s {
		switch {
		case r >= '0' && r <= '9', r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z',
			r == '.', r == '-', r == '_':
			b.WriteRune(r)
		default:
			b.WriteRune('-')
		}
	}
	return b.String()
}
