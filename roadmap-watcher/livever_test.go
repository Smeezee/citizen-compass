package main

// livever_test.go - the parser must fail LOUD, and the negative cases are the
// reason this file exists.
//
// An unreadable description rendering as "no change" is the failure mode the
// whole item is guarding against, so most of what follows is malformed input.

import "testing"

func TestParseLiveVersionsRealPayload(t *testing.T) {
	v := ParseLiveVersions("Live Version: 4.10.0 ▪ Latest Roadmap Roundup: 08/26/2026 ▪ PTU Version: ø")
	if !v.Readable() || v.Live != "4.10.0" {
		t.Fatalf("live: got %q, readable=%v", v.Live, v.Readable())
	}
	if !v.PTUNone || v.PTU != "" {
		t.Errorf("ø should mean NONE, not unreadable: PTU=%q none=%v", v.PTU, v.PTUNone)
	}
	if v.Roundup != "08/26/2026" {
		t.Errorf("roundup: got %q", v.Roundup)
	}
	if len(v.Problems) != 0 {
		t.Errorf("clean payload reported problems: %v", v.Problems)
	}
}

func TestParseLiveVersionsWithRealPTU(t *testing.T) {
	v := ParseLiveVersions("Live Version: 4.10.0 ▪ PTU Version: 4.11.0")
	if v.PTU != "4.11.0" || v.PTUNone {
		t.Fatalf("PTU: got %q none=%v", v.PTU, v.PTUNone)
	}
}

// THE ONE THAT MATTERS. An empty or reworded field must be UNREADABLE, never
// silently level.
func TestParseLiveVersionsFailsLoud(t *testing.T) {
	for _, s := range []string{
		"",
		"   ",
		"Roadmap updates weekly.",
		"LiveVersion 4.10.0", // no colon, not the shape
	} {
		v := ParseLiveVersions(s)
		if v.Readable() {
			t.Fatalf("%q was read as %q - it should be unreadable", s, v.Live)
		}
		if len(v.Problems) == 0 {
			t.Fatalf("%q produced no problem text - a silent failure", s)
		}
	}
}

func TestPatchGap(t *testing.T) {
	live := ParseLiveVersions("Live Version: 4.10.0 ▪ PTU Version: ø")

	behind, line := PatchGap(live, "4.9")
	if !behind {
		t.Fatalf("4.10.0 vs 4.9 should be behind: %s", line)
	}

	behind, line = PatchGap(live, "4.10")
	if behind {
		t.Fatalf("4.10.0 vs 4.10 should be level: %s", line)
	}

	// UNREADABLE MUST NOT RENDER AS LEVEL. Without this, a reworded description
	// would look exactly like a site that is up to date - which is the failure
	// the item names in as many words.
	behind, line = PatchGap(ParseLiveVersions("nothing useful"), "4.9")
	if behind {
		t.Fatalf("unreadable should not claim a gap: %s", line)
	}
	if !contains(line, "NOT KNOWN") {
		t.Fatalf("unreadable must SAY so, got: %s", line)
	}

	// And an unreadable verified side is equally not a clean bill.
	_, line = PatchGap(live, "")
	if !contains(line, "NOT KNOWN") {
		t.Fatalf("missing last_verified_patch must say NOT KNOWN, got: %s", line)
	}
}

func contains(s, sub string) bool {
	return len(s) >= len(sub) && (func() bool {
		for i := 0; i+len(sub) <= len(s); i++ {
			if s[i:i+len(sub)] == sub {
				return true
			}
		}
		return false
	})()
}
