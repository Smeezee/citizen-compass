package main

// livebuild.go - the LIVE and PTU version, from RSI's roadmap board description:
//
//	"Live Version: 4.10.0 ▪ Latest Roadmap Roundup: 08/26/2026 ▪ PTU Version: ø"
//
// A TWIN, STATED. roadmap-watcher/livever.go parses the same field with the same
// two patterns; this copy exists because two `package main` programs cannot
// import each other. Folding both into one shared package is a named follow-up,
// not something to discover later as drift.
//
// FAILS LOUD. An unreadable description is an ERROR, never "no change", and ø
// (or none / n/a) is a real value meaning there is no PTU.

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
)

// THE SHAPES ACCEPTED, STATED (rule 17 - exact forms, not similarity). Measured on
// the live board 2026-09-13 19:58:
//
//	"Live Version: 4.10.0 ([more info](...)) ▪ ... ▪ PTU Version: Alpha 4.10.1 PTU - 12578875"
//
// The 08-30 shape was a bare "PTU Version: 4.11.0" or "ø". Both are accepted: an
// optional literal "Alpha ", the dotted version, an optional literal " PTU" / " LIVE",
// and an optional " - <build number>". The build number is kept in the recorded
// value, so a new PTU build under the same version is still a change. Anything else
// fails loud - which is how this rewording was found: the first real -check said
// "DID NOT LOOK - could not read a PTU version", not "quiet".
var (
	reLive = regexp.MustCompile(`(?i)Live\s+Version\s*:\s*(?:Alpha\s+)?([0-9]+(?:\.[0-9]+)*)(?:\s+LIVE)?(?:\s*-\s*([0-9]+))?`)
	rePTU  = regexp.MustCompile(`(?i)PTU\s+Version\s*:\s*(?:(?:Alpha\s+)?([0-9]+(?:\.[0-9]+)*)(?:\s+PTU)?(?:\s*-\s*([0-9]+))?|(ø|none|n/a))`)
)

const ptuNone = "none"

func withBuild(version, build string) string {
	if build == "" {
		return version
	}
	return version + " (" + build + ")"
}

// ParseBuild -> (live, ptu, error). ptu is "none" when the board says so; a build
// number, when the board gives one, rides along as "4.10.1 (12578875)".
func ParseBuild(description string) (string, string, error) {
	d := strings.TrimSpace(description)
	m := reLive.FindStringSubmatch(d)
	if m == nil {
		return "", "", fmt.Errorf("could not read a live version out of %q", clip(d))
	}
	p := rePTU.FindStringSubmatch(d)
	if p == nil {
		return "", "", fmt.Errorf("could not read a PTU version out of %q", clip(d))
	}
	ptu := ptuNone
	if p[1] != "" {
		ptu = withBuild(p[1], p[2])
	}
	return withBuild(m[1], m[2]), ptu, nil
}

// FetchBuild reads the board and parses its description. RSI answers a failed
// board with HTTP 200 and success 0, so the envelope is checked, not the status.
func FetchBuild(client *http.Client, ua, url string) (string, string, error) {
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return "", "", err
	}
	req.Header.Set("User-Agent", ua)
	req.Header.Set("Accept", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(io.LimitReader(resp.Body, maxBody))
	if err != nil {
		return "", "", err
	}
	if resp.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var b struct {
		Success int    `json:"success"`
		Msg     string `json:"msg"`
		Data    struct {
			Description string `json:"description"`
		} `json:"data"`
	}
	if err := json.Unmarshal(raw, &b); err != nil {
		return "", "", fmt.Errorf("not JSON: %v", err)
	}
	if b.Success != 1 {
		return "", "", fmt.Errorf("the board says it FAILED: success=%d %q", b.Success, b.Msg)
	}
	return ParseBuild(b.Data.Description)
}

func clip(s string) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) > 120 {
		return s[:120] + "..."
	}
	return s
}
