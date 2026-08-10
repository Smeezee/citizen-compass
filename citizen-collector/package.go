package main

// package.go - the button that makes a copy to give somebody.
//
// # WHY THIS IS A BUTTON AND NOT A SCRIPT
//
// make-package.ps1 does the same job and works. It also requires remembering a
// PowerShell command with an execution-policy flag, from the right folder, on
// the day you happen to want it. A thing you do rarely is exactly the thing you
// should not have to remember how to do.
//
// This was specced in variant_master.go as "Generate crew package" and never
// built. It is master-only on purpose: the crew build is what other people run,
// and a copy of it should not be able to make more copies of itself.
//
// # THE STALE-BUILD GUARD, WHICH IS THE WHOLE REASON TO BE CAREFUL
//
// The package ships collector.exe - the CREW build. Sleven runs
// collector-master.exe. Those are two files, built separately, and nothing
// forces them to be the same age.
//
// So the obvious failure is: master gets rebuilt, crew does not, somebody
// clicks this, and a friend receives a build from last week that is missing the
// fix the whole test was for. That is not hypothetical - a stale binary cost
// this project a full day on 2026-08-07, and the tell was a timestamp nobody
// looked at.
//
// So this compares the two and REFUSES rather than warns. A warning on a button
// people click once a month is a warning nobody reads.
//
// # WHAT IS DELIBERATELY LEFT OUT
//
// The install id and the scrub salt above all. If a friend inherited Sleven's
// id, his reports would count as Sleven's and every agreement number in the
// merged dataset would be wrong - silently, and in the direction that looks
// like success.

import (
	"archive/zip"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// PackageResult is what the button reports back.
type PackageResult struct {
	Path  string `json:"path"`
	Bytes int64  `json:"bytes"`
	Note  string `json:"note"`
}

// packageExcluded is checked by name at the top level of the folder. Anything
// not explicitly included is already left out - this list exists so the reason
// for each omission is written down where somebody will read it.
var packageExcluded = map[string]string{
	"collector-install-id.txt":  "the recipient must get their own, or their reports count as yours",
	"collector-scrub-salt.bin":  "your pseudonym salt; sharing it would let your tokens be matched to theirs",
	"collector-consent.txt":     "your agreement is not theirs to inherit - they get asked",
	"collector-auto.log":        "your session history",
	"gamelog-dataset.json":      "your data",
	"collector-master.exe":      "your build, with your tools in it",
	"captures":                  "your screenshots",
}

// BuildCrewPackage writes a zip somebody else can run.
//
// # THERE IS NO LONGER A CHOICE HERE, AND THAT IS THE FIX
//
// This used to take a withRuntime flag, and the window asked which one to make:
// "For any PC - about 200 MB, nothing to install" or "Small - only if they
// already have WebView2". That was an honest description of a real trade-off
// right up until the browser fallback landed, and then it became a trap.
//
// Sleven hit it the same evening: he clicked the button, picked the option that
// said it worked on any PC - because that is what he wanted - and got 271 MB
// he could not send. The labels were steering him toward the wrong answer with
// perfect confidence.
//
// The small package now works on any machine, because a machine without
// WebView2 gets the browser interface instead of nothing. So the 200 MB option
// is not a trade-off any more; it is just the same program with half a gigabyte
// of dead weight attached. An option that is never the right answer is not an
// option, it is a way to make a mistake.
//
// One package. ~6 MB. Fits Discord. Works everywhere.
func BuildCrewPackage(exeDir string, logf func(string, ...interface{})) (PackageResult, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	var res PackageResult

	crew := filepath.Join(exeDir, "collector.exe")
	crewInfo, err := os.Stat(crew)
	if err != nil {
		return res, fmt.Errorf("collector.exe is not here - the package needs the crew "+
			"build, not just this one (%w)", err)
	}

	// THE GUARD. Refuse, do not warn.
	if self, err := os.Executable(); err == nil {
		if selfInfo, err := os.Stat(self); err == nil {
			if crewInfo.ModTime().Before(selfInfo.ModTime().Add(-2 * time.Minute)) {
				return res, fmt.Errorf(
					"collector.exe is older than the build you are running "+
						"(%s vs %s). Packaging it would hand somebody a stale collector "+
						"and the difference would be invisible to them. Rebuild the crew "+
						"binary first",
					crewInfo.ModTime().Format("2006-01-02 15:04"),
					selfInfo.ModTime().Format("2006-01-02 15:04"))
			}
		}
	}

	readme := filepath.Join(exeDir, "README-FOR-TESTERS.txt")
	if _, err := os.Stat(readme); err != nil {
		return res, fmt.Errorf("README-FOR-TESTERS.txt is missing - a build handed over "+
			"with no explanation is not a test, it is an imposition (%w)", err)
	}

	stamp := time.Now().UTC().Format("20060102")
	dest := filepath.Join(exeDir, fmt.Sprintf("citizen-collector-%s.zip", stamp))
	for n := 2; n < 100; n++ {
		if _, err := os.Stat(dest); os.IsNotExist(err) {
			break
		}
		dest = filepath.Join(exeDir, fmt.Sprintf("citizen-collector-%s-%d.zip", stamp, n))
	}

	tmp := dest + ".tmp"
	f, err := os.Create(tmp)
	if err != nil {
		return res, err
	}
	zw := zip.NewWriter(f)
	fail := func(e error) (PackageResult, error) {
		zw.Close()
		f.Close()
		os.Remove(tmp)
		return res, e
	}

	if err := addFile(zw, "collector.exe", crew); err != nil {
		return fail(err)
	}
	if err := addFile(zw, "README.txt", readme); err != nil {
		return fail(err)
	}

	// A FRESH settings file. Copying this machine's would ship whatever
	// experiment was left switched on.
	//
	// EXCEPT the send address, which is the one pair of settings that MUST
	// travel. Without it every recipient's SEND button writes a zip to their own
	// disk and stops there, and the data comes back by hand over Discord,
	// forever, for every person, after every session. That is not a smaller
	// version of the design - it is the absence of it.
	//
	// The key is shared deliberately, and it is the opposite call from the
	// install id and the scrub salt a few lines above. Those identify a person
	// and must never be inherited. This one opens a door that can only ADD:
	// the receiver has no route that lists, reads or deletes, so a leaked key
	// costs junk in a bucket rather than every contributor's data. It is a
	// closed door, not authentication, and it is written down here so nobody
	// later "fixes" it by stripping it out.
	sendURL, sendKey := sendAddressFrom(exeDir)
	w, err := zw.Create("collector-settings.txt")
	if err != nil {
		return fail(err)
	}
	if _, err := w.Write([]byte(crewSettings(sendURL, sendKey))); err != nil {
		return fail(err)
	}
	if strings.TrimSpace(sendURL) == "" {
		// LOUD, because the package still works and the failure is months away.
		// Somebody plays for a week, presses the button, and nothing reaches
		// anyone - and the only sign was a line in a log nobody read.
		logf("package: WARNING - no send_url is set on this machine, so the copy " +
			"you are about to hand over cannot send anything back. Its SEND button " +
			"will write a zip to that person's own disk and stop. Set send_url and " +
			"send_key in collector-settings.txt and make the package again.")
		res.Note = "NO SEND ADDRESS - the recipient's data cannot come back on its own"
	}

	if err := zw.Close(); err != nil {
		f.Close()
		os.Remove(tmp)
		return res, err
	}
	if err := f.Close(); err != nil {
		os.Remove(tmp)
		return res, err
	}
	if err := os.Rename(tmp, dest); err != nil {
		os.Remove(tmp)
		return res, err
	}

	if fi, err := os.Stat(dest); err == nil {
		res.Bytes = fi.Size()
	}
	res.Path = dest
	res.Note = "runs on any Windows machine, nothing to install"

	// Say what was held back, every time. Somebody will eventually wonder why
	// their friend's collector had no data in it, and the answer should already
	// be in the log rather than needing to be worked out.
	logf("package: wrote %s (%d bytes) - %s", filepath.Base(dest), res.Bytes, res.Note)
	var held []string
	for name := range packageExcluded {
		if _, err := os.Stat(filepath.Join(exeDir, name)); err == nil {
			held = append(held, name)
		}
	}
	for _, h := range held {
		logf("package: left out %s - %s", h, packageExcluded[h])
	}
	return res, nil
}

// sendAddressFrom reads this machine's send address, so the package can carry
// it. Read from the file rather than taken as an argument because the packager
// is a button with no parameters, and a second source for the same value is a
// second thing to keep in step.
func sendAddressFrom(exeDir string) (url, key string) {
	s, _ := loadSettings(exeDir)
	u, _ := s.str("send_url")
	k, _ := s.str("send_key")
	return strings.TrimSpace(u), strings.TrimSpace(k)
}

func crewSettings(sendURL, sendKey string) string {
	return crewSettingsTemplate +
		"\n# Where a finished export is sent when the button is pressed. Blank means\n" +
		"# nothing is ever uploaded and the zip simply lands next to the program.\n" +
		"send_url = " + sendURL + "\n" +
		"send_key = " + sendKey + "\n" +
		"\n# Clear the pictures that were sent, but ONLY after the far end confirms\n" +
		"# it received a byte-for-byte identical copy. Never before.\n" +
		"clear_after_send = true\n"
}

const crewSettingsTemplate = `# citizen-collector settings
#
# Plain text. One setting per line, "name = value".
# Lines starting with # are notes and are ignored.
# Delete this file to go back to the defaults.

# Watch and capture automatically while the game is running.
auto = true

# Take a picture every this many SECONDS even when nothing changes.
interval_seconds = 60

# How often to check the game log, in seconds.
poll_seconds = 2

# Never take two pictures closer together than this, in seconds.
debounce_seconds = 3

# Take pictures on menu changes, loading screens and spawning too. Off by
# default - those turned out to be almost all of the useless ones.
capture_low_value = false

# While a shop or inventory terminal is open, keep taking pictures this often
# so a list longer than the screen is recorded as you scroll. 0 = one picture.
burst_seconds = 2

# Never more than this many pictures for one terminal.
burst_max_frames = 24

# Where the pictures go. Relative names are next to this file.
out = captures
`

// packageIsAvailable reports whether this build may make packages. Crew builds
// may not: a copy should not be able to make more copies of itself.
func packageIsAvailable() bool { return strings.EqualFold(BuildVariant, "master") }
