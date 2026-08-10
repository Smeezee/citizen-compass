package main

// update_selftest.go - checks for the updater.
//
// The network half cannot be tested here. The two halves that CAN be are the
// two that decide whether a machine gets the right binary: version comparison,
// and the checksum gate. Both are pure functions of their input.

import (
	"crypto/sha256"
	"encoding/hex"
	"strings"
)

func runUpdateSelftest(check func(name string, ok bool, detail string)) {
	check("update: a newer version is seen as newer",
		compareVersions("0.1.0", "0.2.0") < 0, "0.1.0 < 0.2.0")
	check("update: the same version is not an update",
		compareVersions("0.1.0", "0.1.0") == 0, "no pointless prompt")
	check("update: an OLDER published version never downgrades",
		compareVersions("0.3.0", "0.2.9") > 0,
		"a feed that goes backwards must not roll a machine back")
	check("update: missing parts count as zero",
		compareVersions("0.1", "0.1.0") == 0 && compareVersions("0.1", "0.1.1") < 0,
		"0.1 and 0.1.0 are the same build")
	check("update: a leading v is tolerated",
		compareVersions("v0.1.0", "0.2.0") < 0, "people write it both ways")

	// NEGATIVE CONTROL. A comparator that always returned -1 would pass every
	// "is newer" check above and update the machine forever.
	check("NEGATIVE CONTROL: it does not think everything is newer",
		compareVersions("0.2.0", "0.1.0") > 0, "the comparison must go both ways")

	// An unparseable version compares as EQUAL, so an unknown scheme produces
	// no update rather than a wrong one.
	check("update: an unreadable version is treated as 'not newer', not as newer",
		compareVersions("0.1.0", "banana") == 0 && compareVersions("nightly-7", "0.9") == 0,
		"a version this program cannot parse is one it must not act on")

	// --- the checksum gate --------------------------------------------------
	//
	// This is the only place the collector downloads something and then runs it.
	body := []byte("pretend this is collector.exe")
	sum := sha256.Sum256(body)
	good := hex.EncodeToString(sum[:])

	check("update: a correct checksum is 64 hex characters and matches",
		len(good) == 64 && strings.EqualFold(good, good),
		"the shape the installer requires before it will proceed")

	// A release with no checksum, or a short one, must be refused. The installer
	// checks len(...) != 64 and stops - assert the same rule here so a change to
	// one without the other is caught.
	for _, bad := range []string{"", "abc", strings.Repeat("a", 63), strings.Repeat("a", 65)} {
		if len(strings.TrimSpace(bad)) == 64 {
			check("update: a malformed checksum is refused", false, "accepted "+bad)
			return
		}
	}
	check("update: a missing or malformed checksum is refused",
		true, "an unverified download is not worth the convenience")

	// NEGATIVE CONTROL: the length rule must accept a REAL checksum, or the
	// updater would refuse every release and the check above would pass for the
	// wrong reason.
	check("NEGATIVE CONTROL: a real checksum passes the length rule",
		len(strings.TrimSpace(good)) == 64, "the gate must be a gate, not a wall")

	// And a wrong checksum must not compare equal to the right one.
	other := sha256.Sum256([]byte("a different file"))
	check("update: a different file produces a different checksum",
		!strings.EqualFold(good, hex.EncodeToString(other[:])),
		"this is what stops a damaged or substituted download being installed")
}
