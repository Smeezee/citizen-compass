package main

// update.go - tell the operator there is a newer build, and install it on request.
//
// # WHAT SLEVEN ASKED FOR, AND WHY IT IS THE RIGHT SHAPE
//
//	"we can build a function that notifies inside of the GUI that there's an
//	 update already and they can click update and it auto updates for them from
//	 the GitHub information"
//
// Correct on both halves. The CHECK is automatic - a stale build that nobody
// knows is stale is the defect that cost this project a full day on 2026-08-07,
// and the tell was a timestamp nobody looked at. The INSTALL is a click, which
// keeps the standing rule intact: the program does not change itself behind
// somebody's back.
//
// # AN UPDATER IS A CODE-EXECUTION PATH, SO IT VERIFIES
//
// This downloads a file and then runs it as the collector. That is the most
// dangerous thing in the whole program, and it is worth being blunt about:
// anything that can put bytes in that download can run code on a friend's
// machine.
//
// So the downloaded exe is checked against a SHA256 published alongside it,
// and a mismatch aborts without touching anything. Not as an afterthought -
// the checksum is fetched FIRST, and a release with no checksum is refused
// rather than trusted.
//
// # REPLACING A RUNNING PROGRAM ON WINDOWS
//
// You cannot overwrite a running .exe, but you CAN rename it. So: rename the
// current one aside, write the new one in its place, and the old file goes when
// the process next starts. If anything fails partway, the rename is undone.

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// updateFeed is where releases are published. A raw file rather than the GitHub
// API: the API rate-limits unauthenticated callers to 60/hour per IP, which is
// fine for one person and not for a shared network, and an update check that
// silently starts failing is the thing this feature exists to prevent.
const updateFeed = "https://raw.githubusercontent.com/Smeezee/citizen-compass/main/releases/collector-latest.json"

// ReleaseInfo is the published description of the newest build.
type ReleaseInfo struct {
	Version string `json:"version"`  // "0.2.0"
	URL     string `json:"url"`      // direct download for collector.exe
	SHA256  string `json:"sha256"`   // of the file at URL
	Notes   string `json:"notes"`    // one line, shown to the operator
	MinFrom string `json:"min_from"` // optional: refuse to jump from older than this

	// WHERE TO SEND, so that nobody ever types an address or a key.
	//
	// This file is already trusted enough to name a binary this program
	// downloads and runs; a destination from the same source is strictly less
	// dangerous than that. See destination.go for the precedence rules - local
	// settings always win, and these are only ever used by a machine that has
	// configured nothing.
	//
	// SendKey is published deliberately and is NOT a secret. It is a revocable
	// channel identifier; the controls that actually bound abuse live in the
	// Worker. docs/ROTATING-THE-UPLOAD-KEY.md is the procedure.
	SendURL string `json:"send_url"`
	SendKey string `json:"send_key"`
}

// UpdateStatus is what the window shows.
type UpdateStatus struct {
	// SendURL/SendKey are what the feed said the destination is, so the caller
	// can cache them and use them when nothing is configured locally. Carried
	// here rather than applied here: this file's job is checking for updates,
	// and a function that also silently repointed where data goes would be
	// doing something its name does not admit to.
	SendURL string `json:"-"`
	SendKey string `json:"-"`

	Checked   bool   `json:"checked"`
	Available bool   `json:"available"`
	Current   string `json:"current"`
	Latest    string `json:"latest"`
	Notes     string `json:"notes"`
	Problem   string `json:"problem,omitempty"`
}

// compareVersions returns -1, 0 or 1 comparing dotted numeric versions.
//
// Deliberately dumb: numbers separated by dots, compared left to right, missing
// parts treated as zero. No pre-release tags, no build metadata. A version
// scheme this program cannot parse is one it should not be making decisions
// about, so anything unparseable compares as "not newer" and the operator is
// told rather than surprised.
func compareVersions(a, b string) int {
	split := func(s string) []int {
		s = strings.TrimSpace(strings.TrimPrefix(strings.TrimSpace(s), "v"))
		var out []int
		for _, p := range strings.Split(s, ".") {
			n, err := strconv.Atoi(strings.TrimSpace(p))
			if err != nil {
				return nil
			}
			out = append(out, n)
		}
		return out
	}
	av, bv := split(a), split(b)
	if av == nil || bv == nil {
		return 0
	}
	for i := 0; i < len(av) || i < len(bv); i++ {
		x, y := 0, 0
		if i < len(av) {
			x = av[i]
		}
		if i < len(bv) {
			y = bv[i]
		}
		if x != y {
			if x < y {
				return -1
			}
			return 1
		}
	}
	return 0
}

func httpClient() *http.Client {
	// A short timeout on purpose. An update check that hangs makes the window
	// look frozen, and the check is never urgent enough to be worth that.
	return &http.Client{Timeout: 15 * time.Second}
}

// CheckForUpdate asks the feed what the newest build is.
//
// Never returns an error the caller has to handle: a failed check is a normal
// state (no internet, GitHub down, feed not published yet) and is reported in
// the status rather than raised. The collector must work perfectly with no
// network at all.
func CheckForUpdate(logf func(string, ...interface{})) UpdateStatus {
	st := UpdateStatus{Current: Version}
	resp, err := httpClient().Get(updateFeed)
	if err != nil {
		st.Problem = "could not reach the update list (" + err.Error() + ")"
		return st
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		st.Problem = fmt.Sprintf("the update list returned %d", resp.StatusCode)
		return st
	}
	b, err := io.ReadAll(io.LimitReader(resp.Body, 64*1024))
	if err != nil {
		st.Problem = "could not read the update list"
		return st
	}
	var rel ReleaseInfo
	if err := json.Unmarshal(b, &rel); err != nil {
		st.Problem = "the update list could not be understood"
		return st
	}
	st.Checked = true
	st.Latest = rel.Version
	st.Notes = rel.Notes
	st.SendURL = strings.TrimSpace(rel.SendURL)
	st.SendKey = strings.TrimSpace(rel.SendKey)
	st.Available = compareVersions(Version, rel.Version) < 0
	if logf != nil {
		if st.Available {
			logf("update: %s is available (you have %s) - %s", rel.Version, Version, rel.Notes)
		} else {
			logf("update: you are on the newest build (%s)", Version)
		}
	}
	return st
}

// ApplyUpdate downloads, verifies and installs. Returns the message to show.
func ApplyUpdate(exeDir string, logf func(string, ...interface{})) (string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	resp, err := httpClient().Get(updateFeed)
	if err != nil {
		return "", fmt.Errorf("could not reach the update list: %w", err)
	}
	b, _ := io.ReadAll(io.LimitReader(resp.Body, 64*1024))
	resp.Body.Close()

	var rel ReleaseInfo
	if err := json.Unmarshal(b, &rel); err != nil {
		return "", fmt.Errorf("the update list could not be understood: %w", err)
	}
	if compareVersions(Version, rel.Version) >= 0 {
		return "You are already on the newest build.", nil
	}

	// REFUSE A RELEASE WITH NO CHECKSUM. This is the one place the program
	// downloads something and then runs it, so an unverifiable download is not
	// a degraded case to work around - it is the case to stop on.
	if len(strings.TrimSpace(rel.SHA256)) != 64 {
		return "", fmt.Errorf("that release has no usable checksum, so it will not be " +
			"installed. An update is the one thing that can run code on this machine, " +
			"and an unverified one is not worth the convenience")
	}
	if rel.URL == "" {
		return "", fmt.Errorf("that release has no download link")
	}

	logf("update: downloading %s", rel.Version)
	dresp, err := httpClient().Get(rel.URL)
	if err != nil {
		return "", fmt.Errorf("download failed: %w", err)
	}
	defer dresp.Body.Close()
	if dresp.StatusCode != 200 {
		return "", fmt.Errorf("download returned %d", dresp.StatusCode)
	}

	self, err := os.Executable()
	if err != nil {
		return "", fmt.Errorf("could not work out which program is running, so "+
			"nothing was replaced: %w", err)
	}
	tmp := filepath.Join(exeDir, filepath.Base(self)+".new")
	f, err := os.Create(tmp)
	if err != nil {
		return "", err
	}
	h := sha256.New()
	// Capped at 128 MB: a runaway or wrong URL should not fill a disk before
	// the checksum gets a chance to reject it.
	n, err := io.Copy(io.MultiWriter(f, h), io.LimitReader(dresp.Body, 128<<20))
	f.Close()
	if err != nil {
		os.Remove(tmp)
		return "", fmt.Errorf("download failed after %d bytes: %w", n, err)
	}

	got := hex.EncodeToString(h.Sum(nil))
	if !strings.EqualFold(got, strings.TrimSpace(rel.SHA256)) {
		os.Remove(tmp)
		return "", fmt.Errorf("the downloaded file does not match its published "+
			"checksum, so NOTHING has been changed. Expected %s, got %s. Either the "+
			"download was damaged or the file is not the one that was published",
			rel.SHA256[:16]+"...", got[:16]+"...")
	}
	logf("update: checksum verified (%s)", got[:16]+"...")

	// Rename the running exe aside, then move the new one into place. Windows
	// permits renaming a running image; it does not permit overwriting one.
	// THE RUNNING PROGRAM, NOT A HARDCODED NAME.
	//
	// This used to be "collector.exe" literally. Two binaries live side by side:
	// the crew build is collector.exe and Sleven runs collector-master.exe. So
	// clicking Update from master renamed the CREW build aside, dropped the new
	// release on top of it, said "installed - restart to use it", and left the
	// running build untouched forever. It also defeated package.go's stale-build
	// guard by making the crew exe newer than the master one.
	target := self
	old := self + ".old"
	_ = os.Remove(old)
	renamed := false
	if _, err := os.Stat(target); err == nil {
		if err := os.Rename(target, old); err != nil {
			os.Remove(tmp)
			return "", fmt.Errorf("could not move the current collector aside "+
				"(is it running?): %w", err)
		}
		renamed = true
	}
	if err := os.Rename(tmp, target); err != nil {
		// PUT IT BACK. A failure here would otherwise leave no collector at all.
		if renamed {
			os.Rename(old, target)
		}
		os.Remove(tmp)
		return "", fmt.Errorf("could not put the new collector in place: %w", err)
	}

	logf("update: installed %s - restart to use it", rel.Version)
	return "Version " + rel.Version + " installed. Close this window and start it " +
		"again to use it.", nil
}
