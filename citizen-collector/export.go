package main

// export.go - the SEND MY DATA button.
//
// # WHAT WAS THERE BEFORE
//
// The button existed in the interface and its click handler said:
//
//	toast('Not built yet — coming next.')
//
// Honest, at least. But the one control the whole thing exists for did nothing,
// and on a build handed to someone else that is the difference between a tool
// and a demo.
//
// # WHAT GOES IN THE ZIP, AND WHAT DOES NOT
//
// The dataset always. Screenshots only if the operator asks for them.
//
// That default is deliberate. The dataset is allow-listed, scrubbed and safe to
// send to anyone. A screenshot is not: a frame can carry the player's handle,
// party members' names, chat, and whatever else the HUD was showing. On this
// machine those are Sleven's own. On a tester's machine they are that person's,
// and the difference between "here is my shop data" and "here is my handle and
// everyone I flew with" is a difference they are entitled to be told about
// rather than have decided for them.
//
// So: the zip carries a README naming exactly what is inside, and the frame
// count is stated in the UI BEFORE anything is written.

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// ExportResult is what the UI reports back to the operator.
type ExportResult struct {
	Path        string `json:"path"`
	Bytes       int64  `json:"bytes"`
	Rows        int    `json:"rows"`
	Frames      int    `json:"frames"`
	IncludedPNG bool   `json:"included_png"`
	Quarantined int    `json:"quarantined"`

	// IncludedFiles is exactly what went into the zip. The uploader clears
	// ONLY these - a frame taken while the zip was being written, or one held
	// back by the guard, must survive.
	IncludedFiles []string `json:"-"`

	// IncludedTxnKeys is the dedup key (MineTxn.key()) of every transaction
	// row this export carries. SendExport hands EXACTLY these to
	// MarkTxnsSent once the receiver confirms - never "whatever the store
	// holds by the time the network call returns", because a row mined in
	// the gap between building this zip and getting the receipt was never in
	// the file that went out and must not be marked as if it had been.
	IncludedTxnKeys []string `json:"-"`

	InstallID   string `json:"install_id,omitempty"`
	Note        string `json:"note"`
}

// BuildExport writes one zip the operator can hand over.
//
// includeCaptures is an explicit argument with no default. There is no "true if
// it looks fine" branch: somebody has to decide, and the decision is recorded
// in the README inside the zip.
func BuildExport(exeDir, outDir, capturesDir string, includeCaptures bool,
	logf func(string, ...interface{})) (ExportResult, error) {

	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	var res ExportResult

	// The contributor id lives beside the exe, not in the output folder, so it
	// survives somebody clearing out their captures.
	//
	// A failure here is NOT fatal to the export. An export with no id is honest
	// and still useful - it just cannot be told apart from that person's other
	// exports later. Refusing to hand over their data because a random number
	// could not be generated would be the wrong trade.
	in, idErr := LoadOrCreateInstall(exeDir, logf)
	if idErr != nil {
		res.Note = "no contributor id"
	}

	// Mine first, so the export is never stale. A person clicking SEND expects
	// the file to contain what happened, not what happened last time.
	st, err := MineAll(outDir, in, logf)
	if err != nil {
		return res, fmt.Errorf("could not refresh the dataset before export: %w", err)
	}

	// st.Txns is, by construction, only the rows nobody has confirmed
	// receiving yet - MineAll's dedup pass drops anything already in
	// SentTxnKeys. So this export IS "only unflagged rows" without having to
	// filter anything here; the filtering already happened on the way in.
	res.Rows = len(st.Txns)
	res.InstallID = in.ID
	res.IncludedTxnKeys = txnKeys(st.Txns)

	audit := listCaptures(capturesDir)
	frames := audit.OK
	res.Frames = len(frames)
	res.Quarantined = len(audit.Quaranti)
	res.IncludedPNG = includeCaptures

	// SAY IT OUT LOUD, EVERY TIME. A frame held back silently is the same
	// failure as a frame sent silently - nobody can act on either.
	if len(audit.Quaranti) > 0 {
		logf("export: %d screenshot(s) HELD BACK - they cannot prove they photographed "+
			"the game:", len(audit.Quaranti))
		for _, p := range audit.Quaranti {
			logf("export:   %s - %s", filepath.Base(p), audit.Why[p])
		}
		logf("export: these are not in the zip. Delete them from the captures folder " +
			"if you do not want them on your disk either.")
	}

	// THE NAME MUST BE UNIQUE, AND SECONDS ARE NOT ENOUGH.
	//
	// Found by the selftest, not by reasoning: two exports inside the same
	// second produced the same filename and the second silently replaced the
	// first. Nobody would have noticed until somebody exported twice while
	// deciding whether to include screenshots - which is exactly the moment
	// this tool asks them to - and sent the wrong one.
	stamp := time.Now().UTC().Format("20060102T150405Z")
	dest := filepath.Join(outDir, fmt.Sprintf("citizen-collector-export-%s.zip", stamp))
	for n := 2; n < 1000; n++ {
		if _, err := os.Stat(dest); os.IsNotExist(err) {
			break
		}
		dest = filepath.Join(outDir,
			fmt.Sprintf("citizen-collector-export-%s-%d.zip", stamp, n))
	}

	// Write to a temp name and rename. A partially written zip that already has
	// the final name is a file somebody will send.
	tmp := dest + ".tmp"
	f, err := os.Create(tmp)
	if err != nil {
		return res, err
	}
	zw := zip.NewWriter(f)

	writeBytes := func(inZip string, b []byte) error {
		w, err := zw.Create(inZip)
		if err != nil {
			return err
		}
		_, err = w.Write(b)
		return err
	}

	// 1. the dataset - SCRUBBED. The local copy keeps raw names so a better
	// rule can be re-run later; the copy that leaves the machine never does.
	safe, people := ScrubForExport(st, exeDir, logf)
	if people > 0 {
		logf("export: %d distinct people replaced with stable tokens (player:xxxxxxxx). "+
			"Relationships survive, identities do not.", people)
	}
	data, err := json.MarshalIndent(safe, "", "  ")
	if err != nil {
		zw.Close()
		f.Close()
		os.Remove(tmp)
		return res, err
	}
	if err := writeBytes("gamelog-dataset.json", data); err != nil {
		zw.Close()
		f.Close()
		os.Remove(tmp)
		return res, err
	}

	// 2. the README, which states what is in here and what is not
	if err := writeBytes("README.txt", []byte(exportReadme(safe, len(frames), includeCaptures, len(audit.Quaranti)))); err != nil {
		zw.Close()
		f.Close()
		os.Remove(tmp)
		return res, err
	}

	// 3. screenshots, only on request
	if includeCaptures {
		for _, p := range frames {
			if err := addFile(zw, "captures/"+filepath.Base(p), p); err != nil {
				logf("export: could not add %s: %v", filepath.Base(p), err)
				continue
			}
			// Recorded only on SUCCESS. A file that failed to go in must never
			// end up on the list of things safe to delete.
			res.IncludedFiles = append(res.IncludedFiles, p)
		}
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
	if includeCaptures {
		res.Note = fmt.Sprintf("%d rows and %d screenshots", res.Rows, res.Frames)
	} else {
		res.Note = fmt.Sprintf("%d rows, no screenshots", res.Rows)
	}
	logf("export: wrote %s (%d bytes) - %s", filepath.Base(dest), res.Bytes, res.Note)
	return res, nil
}

// captureAudit is what listCaptures found, split by whether the frame is
// provably a picture of Star Citizen.
type captureAudit struct {
	OK       []string // sidecar proves the window belonged to the game process
	Quaranti []string // it does not, or there is no sidecar to say
	Why      map[string]string
}

// listCaptures returns only frames that PROVE they photographed the game.
//
// # WHY THIS GUARD EXISTS - FOUND 2026-08-08, IN THE CAPTURES FOLDER
//
// Sleven opened the pictures folder and found screenshots of a command prompt,
// a Claude conversation and the Citizen Compass testing website. Reading the
// sidecars rather than guessing: the four oldest frames, from 2026-08-05 22:12
// local, all say
//
//	"exe": "duckduckgo.exe"
//	"how_found": "matched --window against the title"
//	"title": "Citizen Compass v0.3.9 - DuckDuckGo"
//
// The collector was not "seeing his desktop". It matched the window by TITLE,
// found a browser tab whose title contained the search string, and sincerely
// believed that browser was the game. It then photographed it, correctly,
// according to its own rules.
//
// That selection path was removed on 2026-08-07 - every frame from that day
// onward reads "how_found": "process is starcitizen.exe" - so the defect is
// already fixed at the source. **But the four bad PNGs are still on disk, and
// an export with screenshots enabled would have sent them to somebody.** A bug
// fixed in the code is not fixed in the folder.
//
// So the export no longer trusts the capture folder. It asks each frame to
// prove itself, and:
//
//   - no sidecar            -> not sent. Cannot prove what it is.
//   - sidecar names a
//     non-game process      -> not sent, and the process is named in the report.
//   - unreadable sidecar    -> not sent.
//
// FAIL CLOSED. An unprovable frame is treated exactly like a bad one, because
// the cost of being wrong is somebody else's private screen in a file they
// meant to be about spaceships.
func listCaptures(dir string) captureAudit {
	a := captureAudit{Why: map[string]string{}}
	entries, err := os.ReadDir(dir)
	if err != nil {
		return a
	}
	for _, e := range entries {
		if e.IsDir() || !strings.EqualFold(filepath.Ext(e.Name()), ".png") {
			continue
		}
		png := filepath.Join(dir, e.Name())
		side := strings.TrimSuffix(png, filepath.Ext(png)) + ".json"

		b, err := os.ReadFile(side)
		if err != nil {
			a.Quaranti = append(a.Quaranti, png)
			a.Why[png] = "no sidecar, so nothing states what was photographed"
			continue
		}
		// Parsed loosely on purpose: this must keep working against sidecars
		// written by older builds with a different shape. It needs one fact.
		var probe struct {
			Window struct {
				Exe   string `json:"exe"`
				How   string `json:"how_found"`
				Title string `json:"title"`
			} `json:"window"`
		}
		if err := json.Unmarshal(b, &probe); err != nil {
			a.Quaranti = append(a.Quaranti, png)
			a.Why[png] = "sidecar could not be read"
			continue
		}
		if !isGameProcess(probe.Window.Exe) {
			a.Quaranti = append(a.Quaranti, png)
			exe := probe.Window.Exe
			if exe == "" {
				exe = "(unrecorded)"
			}
			a.Why[png] = "photographed " + exe + ", not the game"
			continue
		}
		a.OK = append(a.OK, png)
	}
	sort.Strings(a.OK)
	sort.Strings(a.Quaranti)
	return a
}

func addFile(zw *zip.Writer, inZip, path string) error {
	src, err := os.Open(path)
	if err != nil {
		return err
	}
	defer src.Close()
	w, err := zw.Create(inZip)
	if err != nil {
		return err
	}
	_, err = io.Copy(w, src)
	return err
}

// exportReadme is written INTO the zip so the file explains itself to whoever
// receives it, months later, with no chat window to refer back to.
func exportReadme(st *MineStore, frames int, included bool, quarantined int) string {
	buys, sells := 0, 0
	for _, t := range st.Txns {
		if t.Side == "sell" {
			sells++
		} else {
			buys++
		}
	}
	var b strings.Builder
	fmt.Fprintf(&b, "Citizen Collector export\n")
	fmt.Fprintf(&b, "tool version : %s\n", Version)
	fmt.Fprintf(&b, "schema       : v%d\n", st.SchemaVersion)
	fmt.Fprintf(&b, "generated    : %s\n", st.Generated)
	if st.InstallID != "" {
		fmt.Fprintf(&b, "sent by      : %s\n", st.InstallID)
	} else {
		fmt.Fprintf(&b, "sent by      : (no id - see WHO SENT THIS below)\n")
	}
	b.WriteString("\n")

	fmt.Fprintf(&b, "WHO SENT THIS\n\n")
	if st.InstallID != "" {
		fmt.Fprintf(&b, "  The id above is 16 random bytes generated on the sender's machine.\n")
		fmt.Fprintf(&b, "  It is NOT their name, handle, account, computer name or hardware,\n")
		fmt.Fprintf(&b, "  and it cannot be turned back into any of those.\n\n")
		fmt.Fprintf(&b, "  It exists for one reason. If two exports report the same price at\n")
		fmt.Fprintf(&b, "  the same shop, this is what tells you whether that is two people\n")
		fmt.Fprintf(&b, "  agreeing - which is worth a great deal - or one person sending the\n")
		fmt.Fprintf(&b, "  same thing twice. Merging without it has no right answer.\n\n")
		fmt.Fprintf(&b, "  The sender can read it, change it or delete it at any time, in\n")
		fmt.Fprintf(&b, "  collector-install-id.txt next to the program.\n\n")
	} else {
		fmt.Fprintf(&b, "  This export carries NO id, because one could not be generated or\n")
		fmt.Fprintf(&b, "  saved on the sending machine. The data is still good. It simply\n")
		fmt.Fprintf(&b, "  cannot be matched up with anything else from the same person, so\n")
		fmt.Fprintf(&b, "  treat every row as an independent observation.\n\n")
	}

	fmt.Fprintf(&b, "WHAT IS IN HERE\n\n")
	fmt.Fprintf(&b, "  gamelog-dataset.json\n")
	fmt.Fprintf(&b, "    %d transactions (%d buy, %d sell)\n", len(st.Txns), buys, sells)
	fmt.Fprintf(&b, "    %d locations, %d ship classes, %d quantum destinations\n",
		len(st.Locations), len(st.Ships), len(st.Routes))
	fmt.Fprintf(&b, "    %d object containers, %d spawn locations\n",
		len(st.ObjectContainers), len(st.SpawnLocations))
	fmt.Fprintf(&b, "    Read out of Star Citizen's own Game.log files, including the\n")
	fmt.Fprintf(&b, "    archived sessions the game keeps in its logbackups folder.\n\n")
	fmt.Fprintf(&b, "    These are the rows collected since your last CONFIRMED send, not\n")
	fmt.Fprintf(&b, "    your whole history. Once the receiver of this file confirms it\n")
	fmt.Fprintf(&b, "    arrived intact, these rows are cleared from the local dataset and\n")
	fmt.Fprintf(&b, "    will not appear in the next export - only what happens after this\n")
	fmt.Fprintf(&b, "    point will.\n\n")

	// WHICH NUMBERS ARE FACTS AND WHICH ARE HINTS, IN THE FILE ITSELF.
	//
	// Some of these readers match patterns confirmed against a real in-world
	// session; some match patterns nobody has been able to confirm yet. Both
	// produce plausible-looking values. Whoever receives this file has no way to
	// tell them apart unless it is written down here, next to the data, rather
	// than in a project document they have never seen.
	fmt.Fprintf(&b, "  WHERE EACH PART CAME FROM, AND HOW MUCH TO TRUST IT\n\n")
	for _, e := range st.Extractors {
		mark := "confirmed"
		if !e.Verified {
			mark = "UNCONFIRMED pattern - treat as a hint"
		}
		fmt.Fprintf(&b, "    %-24s %-18s %6d hits  (%s)\n", e.Name, e.Emits, e.Hits, mark)
		if e.Note != "" {
			fmt.Fprintf(&b, "      %s\n", e.Note)
		}
	}
	fmt.Fprintf(&b, "\n    A reader sitting at 0 hits means either that thing was never done,\n")
	fmt.Fprintf(&b, "    or its pattern has stopped matching after a game patch. Those two\n")
	fmt.Fprintf(&b, "    look identical from outside, which is why the count is printed.\n\n")

	if included {
		fmt.Fprintf(&b, "  captures/   %d screenshots\n", frames)
		fmt.Fprintf(&b, "    INCLUDED AT THE OPERATOR'S REQUEST.\n")
		fmt.Fprintf(&b, "    Screenshots are NOT scrubbed. A frame can show your handle,\n")
		fmt.Fprintf(&b, "    the names of players near you, party members and chat. If that\n")
		fmt.Fprintf(&b, "    is not what you meant to send, delete this folder before you\n")
		fmt.Fprintf(&b, "    hand the file over.\n\n")
	} else {
		fmt.Fprintf(&b, "  No screenshots. %d were on disk and none were included.\n\n", frames)
	}
	if quarantined > 0 {
		fmt.Fprintf(&b, "  %d screenshot(s) on the sender's disk were HELD BACK because\n", quarantined)
		fmt.Fprintf(&b, "  their record does not prove they photographed Star Citizen. They\n")
		fmt.Fprintf(&b, "  are not in this file. Stated here so the absence is visible\n")
		fmt.Fprintf(&b, "  rather than looking like they never existed.\n\n")
	}

	fmt.Fprintf(&b, "WHAT IS NOT IN HERE\n\n")
	fmt.Fprintf(&b, "  %s\n\n", strings.ReplaceAll(minePrivacyNote, ". ", ".\n  "))

	fmt.Fprintf(&b, "HOW IT GOT HERE\n\n")
	fmt.Fprintf(&b, "  Nothing was sent anywhere. This file was written to your own disk\n")
	fmt.Fprintf(&b, "  and does nothing until you choose to send it to somebody.\n")
	return b.String()
}
