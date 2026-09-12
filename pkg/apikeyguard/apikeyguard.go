// Package apikeyguard stops an unattended process when the billing it will
// actually use is not the billing anybody declared.
//
// # WHY THIS EXISTS
//
// Anthropic's guidance: a set ANTHROPIC_API_KEY bills a pay-as-you-go account
// rather than a subscription, and an unattended run doing that LOOKS LIKE
// NOTHING HAPPENED - no error, no prompt, no line in a log anybody reads. On
// 2026-09-09 the variable was confirmed unset in every scope on this machine,
// and three metered API clients found installed in the project venv, undeclared
// and unused, were removed. This is the half that survives somebody forgetting.
//
// # THE AMENDMENT THAT SHAPES IT, AND IT ARRIVED AFTER THE FIRST VERSION SHIPPED
//
// The first version refused on PRESENCE: any key at all, always. That was wrong,
// and Sleven found the reason before it cost anything. `claude --bare` REQUIRES
// ANTHROPIC_API_KEY and deliberately ignores subscription login:
//
//	"Set ANTHROPIC_API_KEY before running it, because bare mode doesn't use
//	 your subscription login"
//	"In bare mode, Claude Code never reads OAuth credentials or the system
//	 keychain."
//
// So a legitimate reason to set that variable exists. His words on what that
// means for a guard:
//
//	"A guard that refuses on presence alone will one day block a run somebody
//	 meant to make, and the fix at that moment will be to switch the guard off.
//	 A control that gets switched off in a hurry is worse than no control,
//	 because everyone believes it is still there."
//
// # SO IT REFUSES A MISMATCH, NOT A KEY
//
// The run DECLARES which billing it intends, in CC_ANTHROPIC_BILLING. The guard
// compares that declaration against what the environment actually holds:
//
//	declared              usable key   verdict
//	--------              ----------   -------
//	subscription / unset  no           allowed - the ordinary case
//	subscription / unset  YES          REFUSED - an undeclared key. The accident.
//	api                   YES          allowed, and SAID OUT LOUD in the log
//	api                   no           REFUSED - declared metered, cannot do it
//	anything else         -            REFUSED - the declaration is not understood
//
// UNSET MEANS SUBSCRIPTION because that is the safe default and the true state
// of every entry point in this project today. A run that wants metered billing
// has to say so, and saying so is one variable.
//
// AN UNRECOGNISED DECLARATION IS REFUSED RATHER THAN GUESSED AT - hard rule 19.
// "API", "apikey", "yes", "1" and a trailing space must not quietly become
// permission; a typo in the thing that grants permission is the worst possible
// place for a near-match.
//
// THE ALLOWED METERED RUN IS THE OTHER HALF OF "MAKE IT LOUD". Refusing quietly
// and permitting quietly are the same defect. When a run is allowed to bill, the
// guard says so in the log, so the line exists before the invoice does.
//
// # WHAT IT NEVER DOES
//
// It never reads, logs, prints or returns the VALUE of the key. Presence and
// emptiness are the only facts it reports about it. A guard that leaks the thing
// it guards is worse than no guard.
package apikeyguard

import (
	"fmt"
	"os"
	"strings"
)

// KeyName is the variable that bills. DeclarationName is the variable that says
// whether that is intended. Written once here so a second spelling cannot
// appear in a caller.
const (
	KeyName         = "ANTHROPIC_API_KEY"
	DeclarationName = "CC_ANTHROPIC_BILLING"
)

// The only two things a declaration may say. Exact match, lowercased and
// trimmed, and nothing else is accepted.
const (
	BillingSubscription = "subscription"
	BillingAPI          = "api"
)

// ExitCode is what a refusing process exits with. 78 is EX_CONFIG from
// sysexits.h - "found in an unconfigured or misconfigured state" - chosen so a
// refusal is distinguishable in a scheduler's history from an ordinary failure,
// which is exit 1 everywhere else in this project.
const ExitCode = 78

// Result is what was found. It carries no key value and never will.
type Result struct {
	KeyPresent bool   // ANTHROPIC_API_KEY exists in the environment
	KeyEmpty   bool   // it exists and is the empty string
	Declared   string // CC_ANTHROPIC_BILLING, trimmed and lowercased; "" if unset
	Understood bool   // the declaration is one this guard recognises
}

// UsableKey reports whether there is a key that could actually bill. An empty
// variable cannot, and calling it "a key" would make the mismatch table lie.
func (r Result) UsableKey() bool { return r.KeyPresent && !r.KeyEmpty }

// WantsAPI reports whether the run declared metered billing.
func (r Result) WantsAPI() bool { return r.Declared == BillingAPI }

// Look reads the environment. Separated from the acting half so the decision can
// be driven with input that must fail it - hard rule 12 - without a process
// having to exit to prove it.
func Look() Result {
	v, ok := os.LookupEnv(KeyName)
	d := strings.ToLower(strings.TrimSpace(os.Getenv(DeclarationName)))
	return Result{
		KeyPresent: ok,
		KeyEmpty:   ok && v == "",
		Declared:   d,
		Understood: d == "" || d == BillingSubscription || d == BillingAPI,
	}
}

// Refusal returns the message a refusing process must print, or "" when the
// declaration and the environment agree. The message names the program, so a
// line in a scheduler's log says which unattended thing stopped and why.
func (r Result) Refusal(program string) string {
	head := func(why string) string {
		return fmt.Sprintf("REFUSING TO START: %s, and %s will not run.\n", why, program)
	}
	tail := fmt.Sprintf(
		"  The value of %s has NOT been read, logged or printed, and this guard "+
			"never will.\n"+
			"  Exit code %d (EX_CONFIG) - a refusal, not a crash.",
		KeyName, ExitCode)

	if !r.Understood {
		return head(fmt.Sprintf(
			"%s is set to something this guard does not recognise", DeclarationName)) +
			fmt.Sprintf(
				"  It must be exactly %q or %q, or left unset (which means %q).\n"+
					"  A near-match is refused rather than guessed at: a typo in the "+
					"variable that GRANTS permission is the worst possible place to be "+
					"generous.\n",
				BillingSubscription, BillingAPI, BillingSubscription) + tail
	}

	if r.WantsAPI() && !r.UsableKey() {
		missing := "is not set at all"
		if r.KeyPresent {
			missing = "is set to an EMPTY value"
		}
		return head(fmt.Sprintf(
			"this run declared %s=%s but %s %s",
			DeclarationName, BillingAPI, KeyName, missing)) +
			"  It cannot do what it declared, and a run that fails halfway through " +
			"for this reason is far harder to read than one that refuses now.\n" + tail
	}

	if !r.WantsAPI() && r.UsableKey() {
		return head(fmt.Sprintf(
			"%s is set and NOTHING DECLARED that this run should bill a metered "+
				"API account", KeyName)) +
			fmt.Sprintf(
				"  An unattended run with that variable set bills pay-as-you-go and "+
					"looks like nothing happened - no error, no prompt, no line anybody "+
					"reads.\n"+
					"  If that is wanted, say so: set %s=%s. If it is not, unset %s in "+
					"the scope this process inherits.\n",
				DeclarationName, BillingAPI, KeyName) + tail
	}

	return ""
}

// Notice returns a line an ALLOWED run must still say out loud, or "" when there
// is nothing to say. Permitting quietly and refusing quietly are the same
// defect: if a run is going to bill, the log should hold that fact before the
// invoice does.
func (r Result) Notice(program string) string {
	if r.Refusal(program) != "" {
		return ""
	}
	if r.WantsAPI() {
		return fmt.Sprintf(
			"BILLING NOTICE: %s declared %s=%s and %s is set, so this run bills a "+
				"METERED API account rather than a subscription. Declared "+
				"deliberately - this is not a warning that something is wrong, it is "+
				"the record that it was intended.",
			program, DeclarationName, BillingAPI, KeyName)
	}
	if r.KeyPresent && r.KeyEmpty {
		return fmt.Sprintf(
			"NOTE: %s is present but EMPTY. It cannot bill anything, so this run "+
				"proceeds on the subscription path - but something on this machine is "+
				"setting that name, which is worth knowing.", KeyName)
	}
	return ""
}

// Enforce is the whole guard for a caller: one line at the top of main().
//
// logln is where the refusal or notice ALSO goes - the process's own log file -
// because a refusal nobody sees is the same failure in a different coat, and an
// unattended process's stderr usually goes nowhere. Pass nil when there is no
// log yet; stderr still gets it.
func Enforce(program string, logln func(string)) {
	r := Look()
	if msg := r.Refusal(program); msg != "" {
		fmt.Fprintln(os.Stderr, msg)
		if logln != nil {
			logln(msg)
		}
		os.Exit(ExitCode)
	}
	if note := r.Notice(program); note != "" {
		fmt.Fprintln(os.Stderr, note)
		if logln != nil {
			logln(note)
		}
	}
}
