package main

// livever.go - read the live patch version out of the board's own description.
//
// Q5c, 2026-08-30. The answer R3 was going to be built to compute is already in
// the payload the watcher downloads every four hours:
//
//	data.description:
//	  "Live Version: 4.10.0 ▪ Latest Roadmap Roundup: 08/26/2026 ▪ PTU Version: ø"
//
// board.go's Data struct did not declare `description`, so Go threw it away at
// unmarshal and the watcher reported on cards instead. We have been one full
// patch behind live with the answer arriving on every poll.
//
// # PARSE DEFENSIVELY AND FAIL LOUD
//
// This field is PROSE WITH A STABLE SHAPE, not a schema. RSI can reword it
// tomorrow and nothing will announce that they have. So every value is
// optional, every failure is named, and the one outcome that must never happen
// is an unreadable field rendering as "no change".
//
// That is the same lesson board.go already learned from the `success` envelope:
// RSI answers a dead board with HTTP 200 and the failure in the body, and a
// client that cannot tell "nothing changed" from "I could not look" is worst on
// a tripwire whose whole job is not to miss something.
//
// # ø IS A REAL VALUE AND MEANS "NONE"
//
// PTU Version reads "ø" when there is no PTU build. That is an answer, not a
// parse failure, and it is recorded as one - PTUNone rather than an empty
// string that could equally mean "the field was missing".

import (
	"fmt"
	"regexp"
	"strings"
)

// LiveVersions is what the description says, plus what could not be read.
type LiveVersions struct {
	Live     string // "4.10.0", or "" if unreadable
	PTU      string // "4.11.0", or "" if unreadable or none
	PTUNone  bool   // true when the field explicitly said there is no PTU
	Roundup  string // "08/26/2026", or "" if unreadable
	Problems []string
}

// Readable reports whether the field yielded the one value that matters.
// A caller must branch on this rather than on Live being non-empty, so that
// "could not read" and "no live version" stay distinguishable.
func (v LiveVersions) Readable() bool { return v.Live != "" }

var (
	reLiveVer = regexp.MustCompile(`(?i)Live\s+Version\s*:\s*([0-9]+(?:\.[0-9]+)*)`)
	rePTUVer  = regexp.MustCompile(`(?i)PTU\s+Version\s*:\s*([0-9]+(?:\.[0-9]+)*|ø|none|n/a)`)
	reRoundup = regexp.MustCompile(`(?i)Roundup\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})`)
)

// ParseLiveVersions reads the board description. It never returns an error:
// an unreadable field is a RESULT, carried in Problems, because a caller that
// can ignore an error will, and this one must not.
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
	} else {
		v.Problems = append(v.Problems,
			"I could not read the live version out of: "+clip(s))
	}

	if m := rePTUVer.FindStringSubmatch(s); m != nil {
		got := strings.ToLower(m[1])
		if got == "ø" || got == "none" || got == "n/a" {
			v.PTUNone = true
		} else {
			v.PTU = m[1]
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

// PatchGap compares the live version against what the site says it verified.
//
// BOTH SIDES ARE READ FROM SOMEWHERE ELSE. The live version comes from RSI's
// board; `verified` comes from the page's own data layer, not from a constant
// in this program - a watcher holding its own copy of the number it is checking
// would agree with itself forever. Rule 16, and it is the point of the item.
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

// sameSeries compares on major.minor, because the site records "4.9" and the
// board says "4.9.0". A patch-level difference inside one minor is not the gap
// this is watching for; a minor difference is.
func sameSeries(a, b string) bool {
	return series(a) == series(b)
}

func series(s string) string {
	p := strings.Split(strings.TrimSpace(s), ".")
	if len(p) >= 2 {
		return p[0] + "." + p[1]
	}
	return strings.TrimSpace(s)
}

func clip(s string) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) > 120 {
		return s[:120] + "..."
	}
	return s
}
