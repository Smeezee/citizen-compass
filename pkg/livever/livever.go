// Package livever parses RSI roadmap board description prose for LIVE/PTU/roundup.
// Shared by roadmap-watcher and rsi-watcher so the twins cannot drift.
package livever

import (
	"fmt"
	"regexp"
	"strings"
)

// LiveVersions is what the description says, plus what could not be read.
type LiveVersions struct {
	Live      string // "4.10.0", or "" if unreadable
	LiveBuild string // build number on the Live line when present
	PTU       string // "4.11.0", or "" if unreadable or none
	PTUNone   bool   // true when the field explicitly said there is no PTU
	PTUBuild  string // "12578875" when the board gives a build number, else ""
	Roundup   string // "08/26/2026", or "" if unreadable
	Problems  []string
}

// Readable reports whether the field yielded the live version that matters.
func (v LiveVersions) Readable() bool { return v.Live != "" }

// WithBuild formats "4.10.1 (12578875)" when a build number is present.
func WithBuild(version, build string) string {
	if build == "" {
		return version
	}
	return version + " (" + build + ")"
}

var (
	// Live: optional Alpha, dotted version, optional LIVE, optional - build.
	reLiveVer = regexp.MustCompile(`(?i)Live\s+Version\s*:\s*(?:Alpha\s+)?([0-9]+(?:\.[0-9]+)*)(?:\s+LIVE)?(?:\s*-\s*([0-9]+))?`)
	// PTU: Alpha? version PTU? - build?  OR  A, / ø / none / n/a
	rePTUVer = regexp.MustCompile(`(?i)PTU\s+Version\s*:\s*(?:(?:Alpha\s+)?([0-9]+(?:\.[0-9]+)*)(?:\s+PTU)?(?:\s*-\s*([0-9]+))?|(A,|ø|none|n/a))`)
	reRoundup = regexp.MustCompile(`(?i)Roundup\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})`)
)

// ParseLiveVersions reads the board description. Unreadable fields are Results
// in Problems — never a silent "no change".
func ParseLiveVersions(description string) LiveVersions {
	var v LiveVersions
	s := strings.TrimSpace(description)
	if s == "" {
		v.Problems = append(v.Problems,
			"the board carried no description field at all - either RSI stopped "+
				"sending it or the struct stopped asking for it")
		return v
	}

	if m := reLiveVer.FindStringSubmatch(s); m != nil {
		v.Live = m[1]
		v.LiveBuild = m[2]
	} else {
		v.Problems = append(v.Problems,
			"I could not read the live version out of: "+Clip(s))
	}

	if m := rePTUVer.FindStringSubmatch(s); m != nil {
		if m[1] == "" {
			v.PTUNone = true
		} else {
			v.PTU = m[1]
			v.PTUBuild = m[2]
		}
	} else {
		v.Problems = append(v.Problems, "I could not read the PTU version")
	}

	if m := reRoundup.FindStringSubmatch(s); m != nil {
		v.Roundup = m[1]
	} else {
		v.Problems = append(v.Problems, "I could not read the roundup date")
	}
	return v
}

// ParseBuild is the rsi-watcher shape: (live, ptu, error). ptu is "none" when
// the board says so; build numbers ride in the strings as "4.10.1 (12578875)".
func ParseBuild(description string) (string, string, error) {
	v := ParseLiveVersions(description)
	if !v.Readable() {
		return "", "", fmt.Errorf("could not read a live version out of %q", Clip(strings.TrimSpace(description)))
	}
	if !v.PTUNone && v.PTU == "" {
		return "", "", fmt.Errorf("could not read a PTU version out of %q", Clip(strings.TrimSpace(description)))
	}
	ptu := "none"
	if !v.PTUNone {
		ptu = WithBuild(v.PTU, v.PTUBuild)
	}
	return WithBuild(v.Live, v.LiveBuild), ptu, nil
}

// PatchGap compares live against the site's last_verified_patch.
func PatchGap(v LiveVersions, verified string) (behind bool, line string) {
	switch {
	case !v.Readable():
		return false, "PATCH GAP: NOT KNOWN - I could not read the live version. " +
			strings.Join(v.Problems, "; ")
	case strings.TrimSpace(verified) == "":
		return false, fmt.Sprintf("PATCH GAP: NOT KNOWN - live is %s but the "+
			"page's own last_verified_patch could not be read", v.Live)
	case sameSeries(v.Live, verified):
		return false, fmt.Sprintf("patch: live %s, site verified against %s - level",
			v.Live, verified)
	default:
		return true, fmt.Sprintf("PATCH GAP: live is %s and the site says its "+
			"numbers were verified against %s", v.Live, verified)
	}
}

func sameSeries(a, b string) bool { return series(a) == series(b) }

func series(s string) string {
	p := strings.Split(strings.TrimSpace(s), ".")
	if len(p) >= 2 {
		return p[0] + "." + p[1]
	}
	return strings.TrimSpace(s)
}

// Clip shortens a string for error messages.
func Clip(s string) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) > 120 {
		return s[:120] + "..."
	}
	return s
}