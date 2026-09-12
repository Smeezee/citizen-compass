package apikeyguard

import (
	"os"
	"strings"
	"testing"
)

// HARD RULE 12, and this package has TWO ways to become useless without anybody
// noticing. It could stop seeing the key - then every caller is silently
// unguarded. Or it could start accepting a declaration it should not - then the
// guard is still there and grants permission to anything. Both directions, and
// the near-misses, on every run.

func set(t *testing.T, key, declared string) {
	t.Helper()
	if key == "<unset>" {
		os.Unsetenv(KeyName)
	} else {
		t.Setenv(KeyName, key)
	}
	if declared == "<unset>" {
		os.Unsetenv(DeclarationName)
	} else {
		t.Setenv(DeclarationName, declared)
	}
}

// THE MISMATCH TABLE, which is the whole design.
func TestTheMismatchTable(t *testing.T) {
	cases := []struct {
		name     string
		key      string
		declared string
		refuse   bool
		why      string
	}{
		{"the ordinary case: nothing set, nothing declared",
			"<unset>", "<unset>", false, ""},
		{"nothing set, subscription declared explicitly",
			"<unset>", "subscription", false, ""},

		// THE ACCIDENT THE GUARD EXISTS FOR.
		{"a key with no declaration",
			"sk-ant-x", "<unset>", true, "NOTHING DECLARED"},
		{"a key while subscription is declared",
			"sk-ant-x", "subscription", true, "NOTHING DECLARED"},

		// THE LEGITIMATE RUN THE AMENDMENT EXISTS FOR - claude --bare.
		{"a key, declared api",
			"sk-ant-x", "api", false, ""},

		// DECLARED AND CANNOT DO IT.
		{"api declared, no key",
			"<unset>", "api", true, "but ANTHROPIC_API_KEY is not set at all"},
		{"api declared, empty key",
			"", "api", true, "is set to an EMPTY value"},

		// AN EMPTY KEY CANNOT BILL, so it is not the accident.
		{"empty key, nothing declared",
			"", "<unset>", false, ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			set(t, c.key, c.declared)
			msg := Look().Refusal("a-program")
			if c.refuse && msg == "" {
				t.Fatalf("expected a refusal and got none")
			}
			if !c.refuse && msg != "" {
				t.Fatalf("expected no refusal, got: %s", msg)
			}
			if c.refuse && c.why != "" && !strings.Contains(msg, c.why) {
				t.Errorf("the refusal does not say why (%q): %s", c.why, msg)
			}
		})
	}
}

// A TYPO IN THE THING THAT GRANTS PERMISSION MUST NEVER BE GENEROUS. Rule 19.
func TestANearMissDeclarationIsRefusedNotGuessed(t *testing.T) {
	for _, bad := range []string{"API-KEY", "apikey", "yes", "1", "true",
		"metered", "sub", "subscriptions", "a p i"} {
		t.Run(bad, func(t *testing.T) {
			set(t, "sk-ant-x", bad)
			r := Look()
			if r.Understood {
				t.Fatalf("%q was accepted as a declaration - the guard now grants "+
					"permission to a typo", bad)
			}
			msg := r.Refusal("p")
			if msg == "" {
				t.Fatal("an unrecognised declaration produced no refusal")
			}
			if !strings.Contains(msg, "does not recognise") {
				t.Errorf("the refusal does not say the declaration was the problem: %s", msg)
			}
		})
	}
}

// CASE AND WHITESPACE ARE NORMALISED, AND THE NORMALISATION IS STATED. Rule 17
// allows it only when it is spelled out and checked - so it is checked.
func TestDeclarationIsTrimmedAndLowercased(t *testing.T) {
	for _, ok := range []string{"api", "API", " api ", "\tApi\n"} {
		set(t, "sk-ant-x", ok)
		r := Look()
		if !r.WantsAPI() {
			t.Errorf("%q did not read as an api declaration", ok)
		}
		if msg := r.Refusal("p"); msg != "" {
			t.Errorf("%q was refused: %s", ok, msg)
		}
	}
}

// AN ALLOWED METERED RUN MUST SAY SO. Permitting quietly and refusing quietly
// are the same defect.
func TestAnAllowedMeteredRunAnnouncesItself(t *testing.T) {
	set(t, "sk-ant-x", "api")
	note := Look().Notice("run_something.exe")
	if note == "" {
		t.Fatal("a run that will bill a metered account said nothing")
	}
	for _, want := range []string{"METERED", "run_something.exe", DeclarationName} {
		if !strings.Contains(note, want) {
			t.Errorf("the notice does not mention %q: %s", want, note)
		}
	}
}

func TestTheOrdinaryCaseSaysNothingAtAll(t *testing.T) {
	set(t, "<unset>", "<unset>")
	r := Look()
	if r.Refusal("p") != "" || r.Notice("p") != "" {
		t.Fatal("the ordinary case is not silent, so every clean run now prints " +
			"something and the real messages become wallpaper")
	}
}

// THE VALUE MUST NEVER APPEAR, in a refusal or in a notice.
func TestTheValueIsNeverInAnyMessage(t *testing.T) {
	const secret = "sk-ant-THIS-MUST-NOT-APPEAR-9f3a2b"
	for _, declared := range []string{"<unset>", "api", "nonsense"} {
		set(t, secret, declared)
		r := Look()
		for label, msg := range map[string]string{
			"refusal": r.Refusal("p"), "notice": r.Notice("p"),
		} {
			if msg == "" {
				continue
			}
			if strings.Contains(msg, secret) {
				t.Fatalf("the %s CONTAINS THE VALUE (declared=%s)", label, declared)
			}
			if strings.Contains(msg, secret[:12]) {
				t.Fatalf("the %s contains a fragment of the value (declared=%s)",
					label, declared)
			}
		}
	}
}

// The struct holds no field that could carry a value.
func TestResultCarriesNoValue(t *testing.T) {
	const secret = "sk-ant-leak-check-771"
	set(t, secret, "api")
	r := Look()
	if strings.Contains(r.Declared, secret) {
		t.Fatal("the Result struct holds the key value")
	}
}
