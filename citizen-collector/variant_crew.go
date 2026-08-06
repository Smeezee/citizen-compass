//go:build !master

package main

// variant_crew.go - the crew build (WO-COLLECT-01 rev 5 addendum, 2026-08-06).
//
// Built by default:   go build -o collector.exe .
//
// "Two builds from one source ... Same codebase, a build flag. Not two
// projects." This file and variant_master.go are the flag. Everything else in
// the package is shared, so a change to capture or logging cannot drift between
// the two builds - there is only one of each.
//
// The crew build is capture, read, export. It deliberately does NOT contain
// calibration, zone tuning, the review pen, or the package generator. Those
// live behind the master tag so they are absent from the shipped binary rather
// than merely hidden in it - a menu item that is compiled out cannot be found
// by a curious crew member, and cannot ship Sleven's paths in its help text.

const BuildVariant = "crew"

// masterOnlyCommands is empty here. main() consults it so that the two variants
// share one entry point.
func masterOnlyCommands() map[string]func() int { return nil }

// BenchFlags is the bench-testing escape hatch, and in this build it does not
// exist.
//
// Rev 5 §3 requires that capture be restricted to the StarCitizen.exe process
// and that testing against other windows sit behind --allow-any-window, which
// must not be present in the crew build.
//
// Note what this is NOT: it is not a flag that defaults to false, and not a
// runtime check that refuses to honour it. `collector.exe --allow-any-window`
// fails with "flag provided but not defined", because the flag is never
// registered in this file. There is no code path in this binary that can set
// allowAny to true.
//
// That distinction is the whole point. A flag that exists but is disabled can
// be enabled by a future edit, a config file, or an environment variable
// somebody adds later. A flag that is not compiled in cannot.
func registerBenchFlags() func() (allowAny bool, windowHint string) {
	return func() (bool, string) { return false, "" }
}
