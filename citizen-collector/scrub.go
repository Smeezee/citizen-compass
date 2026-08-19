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

	// ONE CLASSIFIER. See nameclass.go - the rules about NPC archetypes,
	// mission characters and already-swapped tags live there and are shared
	// with the write-time path, so the two cannot drift.
	// A TAG PASSES THROUGH UNTOUCHED, not through scrubIDs.
	//
	// scrubIDs eats any run of six or more digits, and a tag is eight hex
	// characters - so player:2860302f became player:<id>f. Silent, and it gave
	// one person two identities depending on whether their tag happened to
	// contain enough digits.
	if rePseudonym.MatchString(v) {
		return v
	}
	if KeepsName(v) {
		return scrubIDs(v)
	}
	if !s.ok {
		return "<player>"
	}
	return s.Tag(v)
}

// Tag mints a pseudonym WITHOUT consulting the classifier.
//
// THE CLASSIFIER IS NOT THE LAST WORD, AND THIS IS THE DOOR FOR THAT.
//
// Value() keeps a spaced name because a handle "cannot" contain a space. When
// the log itself has called that name a player - `nickname="..." playerGEID=` -
// that hint is beaten by evidence, and the caller needs a way to say so. Before
// this existed the override in MineStore.swap looked right and did nothing:
// swap decided to swap, called Value, and Value kept the name on the very rule
// being overridden. Caught by a check driving the real path rather than by
// reading either function.
func (s *scrubber) Tag(v string) string {
	v = strings.TrimSpace(v)
	if rePseudonym.MatchString(v) {
		return v
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
	// NORMALISE logf HERE, not only inside newScrubber.
	//
	// newScrubber took a nil logf and quietly replaced its OWN copy with a
	// no-op, which made this function look nil-safe when it was not: the first
	// time anything in ScrubForExport itself logged - the prose-scan line added
	// 2026-08-16 - it dereferenced nil and took the process down. Two selftest
	// callers and any future one pass nil. Fixed at the parameter so the next
	// log line added below cannot reintroduce it.
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
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

	// FREE TEXT THAT CAN NAME SOMEBODY.
	//
	// Contracts and Objectives had never been scrubbed and had never been
	// looked at - they were simply not in this walk. A PvP bounty names its
	// target, so "Eliminate <somebody>" is a mission objective with a handle
	// in it. Scanned token by token rather than replaced wholesale, or the
	// sentence is destroyed along with the name.
	prose := 0
	scanMap := func(in map[string]int) map[string]int {
		if len(in) == 0 {
			return in
		}
		outm := make(map[string]int, len(in))
		for k, n := range in {
			cleaned, hits := sc.ScrubProse(k)
			prose += hits
			outm[cleaned] += n
		}
		return outm
	}
	out.Contracts = scanMap(st.Contracts)
	out.Objectives = scanMap(st.Objectives)
	out.GameTips = scanMap(st.GameTips)
	if prose > 0 {
		logf("scrub: replaced %d name(s) found inside mission text - contracts, "+
			"objectives or tips", prose)
	}

	txns := make([]MineTxn, 0, len(st.Txns))
	for _, t := range st.Txns {
		t.Shop = sc.Value(t.Shop)
		t.Item = sc.Value(t.Item)
		txns = append(txns, t)
	}
	out.Txns = txns

	return &out, len(sc.mapped)
}

// reHandleShaped matches a token that a person's handle looks like and English
// prose does not: it contains a digit or an underscore.
//
// THIS IS THE PROSE RULE, and it is deliberately narrow. A mission title reads
// "Adagio Holdings in Need of Salvagers" - every word of that is capitalised
// English and swapping on capitalisation alone would destroy the sentence while
// protecting nobody. Handles like 8mole5duro, KDog79 and mrDonkey6511 carry a
// digit or an underscore; "Adagio" does not.
//
// A handle with no digit and no underscore - "Corjack" - is NOT caught by this
// rule. It is caught by the known-people rule below if that person has appeared
// anywhere structured, which is the common case. Where neither fires, the token
// is REPORTED rather than silently passed, so the gap is visible instead of
// theoretical.
var reHandleShaped = regexp.MustCompile(`^[A-Za-z][A-Za-z0-9_]*[0-9_][A-Za-z0-9_]*$`)

// reProseToken splits prose into things that could be a name.
//
// A TAG THIS SCANNER ALREADY WROTE MATCHES FIRST, and that ordering is the
// whole point of the alternation. Without it "player:dd0e64c6" splits at the
// colon into "player" and "dd0e64c6" - and the second half is digit-bearing,
// so a second pass tags the tag and produces "player:player:2ccacea7". One
// person then holds two identities and every join in the dataset quietly
// stops matching. Caught by the idempotence check in scrub_policy_selftest.go,
// which is why that check exists rather than being assumed.
var reProseToken = regexp.MustCompile(`player:[0-9a-f]{8}|[A-Za-z][A-Za-z0-9_\-']*`)

// ScrubProse replaces people named inside free text, and leaves the text.
//
// Two rules, in order:
//
//  1. anybody this scrubber has ALREADY identified elsewhere in the dataset -
//     the reliable one, because a PvP bounty target has almost certainly also
//     appeared as a victim or a killer
//  2. anything shaped like a handle rather than like a word
//
// Returns the text and how many tokens it replaced.
func (s *scrubber) ScrubProse(v string) (string, int) {
	if v == "" {
		return v, 0
	}
	n := 0
	out := reProseToken.ReplaceAllStringFunc(v, func(tok string) string {
		// 0. already a tag - leave it exactly as it is.
		if rePseudonym.MatchString(tok) {
			return tok
		}
		// 1. somebody already known to be a person.
		if t, seen := s.mapped[tok]; seen {
			n++
			return t
		}
		// 2. shaped like a handle rather than a word, and not game vocabulary.
		if reHandleShaped.MatchString(tok) && !KeepsName(tok) {
			n++
			return s.Value(tok)
		}
		return tok
	})
	return out, n
}
