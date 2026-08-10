package main

// scrub.go - keep the raw locally, anonymise at the door.
//
// # WHAT SLEVEN ASKED FOR
//
//	"If it pulls their actual name or their in game name or any type of
//	 personal information, we just take it. And then we have another program
//	 that goes through and... scrubs it... Collecting the data is the main
//	 focus. The secondary thing would be making sure that their names are not
//	 listed in any of our public data."
//
// He is right that this is simpler, and right that it is better data. The
// shape-guessing scrubber written earlier today throws information away that
// cannot be recovered: when it writes "<player>" it loses whether the same
// person appears twice, so "A killed B, then B killed A" and "four strangers
// died" are indistinguishable afterwards. Deciding at collection time is
// deciding forever, with no way to improve later.
//
// # WHERE THIS PUTS THE BOUNDARY, AND WHY NOT WHERE HE PUT IT
//
// He said the line is "our public data". This code draws it one step earlier,
// at the EXPORT - the moment a file is built to be handed to somebody.
//
// The reason is not squeamishness, it is that the export is the only boundary
// that still exists on a machine that is not his. On his own disk, raw names
// are his own business: his logs, his hardware, his call, and nothing here
// stops him reading them. But this tool is about to run on his wife's machine
// and his friend's. A file on THEIR disk, built for the express purpose of
// being sent, containing the handles of strangers who never agreed to anything,
// is a different object - and "we'll scrub it before publishing" is a promise
// made by someone who is not holding the file.
//
// One more thing worth saying plainly: this reverses a rule he set himself -
// "other players' names: stripped before the file exists, never written." He
// can reverse his own rule. It should be on the record that it was reversed
// deliberately rather than quietly dropped, so nobody later finds raw handles
// and assumes a bug.
//
// # PSEUDONYMS, NOT REDACTION
//
// A name does not become "<player>". It becomes "player:3f9a1c22" - the same
// person, same token, for the whole dataset. So every relationship survives
// (who fought whom, how often, in which zone) and no identity does.
//
// The salt is random per install and never leaves the machine. That means two
// contributors reporting the same stranger produce DIFFERENT tokens - which
// costs a little cross-referencing and buys the guarantee that pooling
// everyone's exports cannot rebuild a picture of one person's movements.

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// reMineAssetish matches a value shaped like something CIG shipped, rather than
// like a person.
//
// NOTE the <id> in the character classes. Values reach here AFTER scrubIDs, so a
// real asset name looks like "AEGS_Vanguard_Harbinger_<id>". The first version
// omitted the angle brackets and therefore rejected every scrubbed asset name as
// a person - safe, and completely wrong. Found by the selftest, not by reading it.
// # THE THIRD BRANCH WAS A HOLE, AND THE TESTS PASSED FOR THE WRONG REASON
//
// It used to end with `[a-z][a-z0-9]*(?:_[a-z0-9<>]+){2,}` - lowercase start,
// two or more underscore-separated segments - meant to match item classes like
// behr_rifle_ballistic_01. That is ALSO the exact shape of a very large share of
// Star Citizen handles, which allow letters, digits and underscores:
//
//	dark_wolf_77          passed through UNSCRUBBED
//	space_cowboy_42       passed through UNSCRUBBED
//	the_real_slim_shady   passed through UNSCRUBBED
//
// The selftest could not catch it: all three fixture handles (Jeri_Blade,
// DukeSP, Sleven-K) carry an uppercase letter or a hyphen, so every one failed
// the regex by accident rather than by design. A check that passes for the
// wrong reason is the same defect as a check that cannot fail.
//
// Item classes now need a KNOWN CIG PREFIX, not merely a lowercase shape. That
// costs an occasional real item being pseudonymised, which is a wasted row.
// The other direction costs a stranger their handle in a public file.
var reMineAssetish = regexp.MustCompile(
	`^(?:NPC_[A-Za-z0-9_<>\-]+|(?:AEGS|ANVL|ARGO|BANU|CNOU|CRUS|DRAK|ESPR|GAMA|GRIN|` +
		`KRIG|MISC|MRAI|ORIG|RSI|TMBL|VNCL|XIAN|XNAA|GLSN|APAR)_[A-Za-z0-9_<>]+|` +
		`(?:behr|gmni|klwe|apar|hrst|kbar|lbco|ksar|amrs|vncl|crlf|grin|drak|` +
		`aegs|rsi|misc|anvl|argo|banu|cnou|crus|espr|gama|krig|mrai|orig|tmbl|` +
		`xian|xnaa|glsn|vgl|kegn|kegr|utnv|mrck|dfnc|sctl|pwr|cool|shld|qdrv|` +
		`ftnk|thrst|whd|smlt|frtl)_[a-z0-9_<>]+)$`)

const scrubSaltFile = "collector-scrub-salt.bin"

// loadOrCreateSalt returns the per-install pseudonym salt.
//
// If it cannot be created the caller MUST fall back to redaction rather than
// hashing with a fixed value: an unsalted hash of a handle is reversible by
// anyone with a list of handles, which is a worse outcome than "<player>"
// while looking more sophisticated.
func loadOrCreateSalt(dir string) ([]byte, error) {
	p := filepath.Join(dir, scrubSaltFile)
	if b, err := os.ReadFile(p); err == nil && len(b) >= 16 {
		return b, nil
	}
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return nil, fmt.Errorf("no secure random source for the pseudonym salt: %w", err)
	}
	if err := os.WriteFile(p, b, 0o600); err != nil {
		return b, err // usable now, not stable later - caller reports it
	}
	return b, nil
}

// pseudonym turns one name into a stable, unreversible token.
func pseudonym(salt []byte, name string) string {
	h := sha256.New()
	h.Write(salt)
	h.Write([]byte(strings.ToLower(strings.TrimSpace(name))))
	return "player:" + hex.EncodeToString(h.Sum(nil))[:8]
}

// scrubber replaces person-shaped values on their way out.
type scrubber struct {
	salt   []byte
	ok     bool // false = fall back to flat redaction
	mapped map[string]string
}

func newScrubber(exeDir string, logf func(string, ...interface{})) *scrubber {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	s := &scrubber{mapped: map[string]string{}}
	salt, err := loadOrCreateSalt(exeDir)
	if err != nil || len(salt) < 16 {
		logf("scrub: no salt available (%v) - names will be REDACTED rather than "+
			"pseudonymised. The export stays safe; it just loses the ability to tell "+
			"one person from another.", err)
		return s
	}
	s.salt, s.ok = salt, true
	return s
}

// Value returns what may travel in place of v.
//
// A value that looks like a game asset passes through untouched. Anything else
// is treated as a person - FAIL CLOSED, because the cost of misjudging in that
// direction is a stranger's handle in a file built to be sent.
func (s *scrubber) Value(v string) string {
	v = strings.TrimSpace(v)
	if v == "" || strings.EqualFold(v, "unknown") {
		return v
	}
	if reMineAssetish.MatchString(scrubIDs(v)) || reMineAssetish.MatchString(v) {
		return scrubIDs(v)
	}
	if !s.ok {
		return "<player>"
	}
	if t, seen := s.mapped[v]; seen {
		return t
	}
	t := pseudonym(s.salt, v)
	s.mapped[v] = t
	return t
}

// ScrubForExport returns a copy of the store with every person replaced.
//
// A COPY, deliberately. The local dataset keeps the raw values so a better
// scrubber can be re-run over old data later - which is the whole argument for
// deciding late instead of early, and it only works if the raw is still there.
func ScrubForExport(st *MineStore, exeDir string, logf func(string, ...interface{})) (*MineStore, int) {
	sc := newScrubber(exeDir, logf)
	out := *st // shallow copy; every map touched below is rebuilt

	// SentTxnKeys MUST NOT TRAVEL. Found while adding it, not after shipping
	// it - which is the point of writing this down here rather than trusting
	// the next person to remember.
	//
	// A key is TS|Side|Market|Shop|Item|Price|Amount, built from Txns BEFORE
	// scrubbing (see txnKeys in gamelog_mine.go - it has to be, or it would
	// never match the raw rows dedupAgainstSent compares it against). The
	// shallow copy above would otherwise carry that map, RAW SHOP AND ITEM
	// TEXT INCLUDED, straight into the zip - the exact failure this file
	// exists to prevent, and it would have shipped it silently: nothing about
	// "the export contains data" would look wrong from outside.
	//
	// A receiver has no use for a sender's own already-sent bookkeeping
	// anyway, which is the other reason this is a clean cut rather than a
	// scrub-in-place: there is nothing here worth keeping, scrubbed or not.
	out.SentTxnKeys = nil

	// SCRUB BY FIELD, NOT BY SWEEP.
	//
	// The first version of this ran every part of every composite key through
	// the scrubber, and the selftest caught it immediately: "Bullet" became a
	// pseudonym, so did the zone "ObjectContainer-ugf_lta_a_0002", so did the
	// NPC archetype, so did the destroyed ship class. It was safe and it was
	// useless - the same over-correction as the ID audit that once ate build
	// numbers and prices.
	//
	// Only three fields in a death can hold a person: victim, killer, weapon.
	// The weapon is in that list because the game sometimes writes the actor's
	// name there, which is exactly the kind of thing you only learn by reading
	// real logs. Zone, class and damage type are game vocabulary and are left
	// alone deliberately.
	//
	//	key = Zone | Victim | Killer | Weapon | Class | DamageType
	//	        0      1        2        3       4         5
	const (
		fVictim = 1
		fKiller = 2
		fWeapon = 3
	)
	deaths := make(map[string]int, len(st.Deaths))
	for k, n := range st.Deaths {
		parts := strings.Split(k, "|")
		for _, i := range []int{fVictim, fKiller, fWeapon} {
			if i < len(parts) {
				parts[i] = sc.Value(parts[i])
			}
		}
		deaths[strings.Join(parts, "|")] += n
	}
	out.Deaths = deaths

	// "SHIP_CLASS @ zone". Neither half is person-capable in the game's own
	// vocabulary, but the ship half is free text now that the raw is kept, so
	// it is checked. The zone is not touched.
	losses := make(map[string]int, len(st.VehicleLosses))
	for k, n := range st.VehicleLosses {
		ship, zone, found := strings.Cut(k, " @ ")
		if !found {
			losses[sc.Value(k)] += n
			continue
		}
		losses[sc.Value(ship)+" @ "+zone] += n
	}
	out.VehicleLosses = losses

	// Locations are place names from the game. They are NOT scrubbed - doing so
	// was the bug above. They already went through scrubIDs on the way in.
	out.Locations = st.Locations

	txns := make([]MineTxn, 0, len(st.Txns))
	for _, t := range st.Txns {
		t.Shop = sc.Value(t.Shop)
		t.Item = sc.Value(t.Item)
		txns = append(txns, t)
	}
	out.Txns = txns

	return &out, len(sc.mapped)
}
