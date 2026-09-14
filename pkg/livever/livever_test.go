package livever

import "testing"

func TestParseLiveVersionsRealPayload(t *testing.T) {
	v := ParseLiveVersions("Live Version: 4.10.0 - Latest Roadmap Roundup: 08/26/2026 - PTU Version: A,")
	if !v.Readable() || v.Live != "4.10.0" {
		t.Fatalf("live: got %q, readable=%v", v.Live, v.Readable())
	}
	if !v.PTUNone || v.PTU != "" {
		t.Errorf("A, should mean NONE: PTU=%q none=%v", v.PTU, v.PTUNone)
	}
	if v.Roundup != "08/26/2026" {
		t.Errorf("roundup: got %q", v.Roundup)
	}
	if len(v.Problems) != 0 {
		t.Fatalf("clean payload reported problems: %v", v.Problems)
	}
}

func TestParseLiveVersionsWithRealPTU(t *testing.T) {
	v := ParseLiveVersions("Live Version: 4.10.0 - PTU Version: 4.11.0")
	if v.PTU != "4.11.0" || v.PTUNone {
		t.Fatalf("PTU: got %q none=%v", v.PTU, v.PTUNone)
	}
}

func TestParseLiveVersionsSeptemberShape(t *testing.T) {
	v := ParseLiveVersions("Live Version: 4.10.0 ([more info](https://robertsspaceindustries.com/comm-link/transmission/21242-Alpha-410-Siege-Of-Orison)) " +
		"- Latest Roadmap Roundup: 09/09/2026 ([more info](https://x)) " +
		"- PTU Version: Alpha 4.10.1 PTU - 12578875")
	if v.Live != "4.10.0" || v.PTU != "4.10.1" || v.PTUBuild != "12578875" || v.PTUNone ||
		v.Roundup != "09/09/2026" || len(v.Problems) != 0 {
		t.Fatalf("got %+v", v)
	}
}

func TestParseLiveVersionsFailsLoud(t *testing.T) {
	for _, s := range []string{"", "   ", "Roadmap updates weekly.", "LiveVersion 4.10.0"} {
		v := ParseLiveVersions(s)
		if v.Readable() {
			t.Fatalf("%q was read as %q", s, v.Live)
		}
		if len(v.Problems) == 0 {
			t.Fatalf("%q produced no problem text", s)
		}
	}
}

func TestParseBuildSeptember(t *testing.T) {
	d := "Live Version: 4.10.0 ([more info](x)) - PTU Version: Alpha 4.10.1 PTU - 12578875"
	live, ptu, err := ParseBuild(d)
	if err != nil || live != "4.10.0" || ptu != "4.10.1 (12578875)" {
		t.Fatalf("got live=%q ptu=%q err=%v", live, ptu, err)
	}
	if _, _, err := ParseBuild(""); err == nil {
		t.Fatal("empty should error")
	}
	if live, ptu, err := ParseBuild("Live Version: 4.10.0 - PTU Version: A,"); err != nil || live != "4.10.0" || ptu != "none" {
		t.Fatalf("A, -> none: live=%q ptu=%q err=%v", live, ptu, err)
	}
}

func TestPatchGap(t *testing.T) {
	live := ParseLiveVersions("Live Version: 4.10.0 - PTU Version: A,")
	behind, line := PatchGap(live, "4.9")
	if !behind {
		t.Fatalf("should be behind: %s", line)
	}
	behind, line = PatchGap(live, "4.10")
	if behind {
		t.Fatalf("should be level: %s", line)
	}
	behind, line = PatchGap(ParseLiveVersions("nothing useful"), "4.9")
	if behind || !contains(line, "NOT KNOWN") {
		t.Fatalf("unreadable: %s", line)
	}
}

func contains(s, sub string) bool {
	return stringsContains(s, sub)
}

func stringsContains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}