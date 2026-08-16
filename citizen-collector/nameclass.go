package main

// nameclass.go - is this a person, or is it scenery?
//
// ===========================================================================
// ONE CLASSIFIER, USED WHEREVER A NAME IS ABOUT TO BE WRITTEN
// ===========================================================================
//
// There were two answers to this question in the codebase and they disagreed:
//
//   - safeActor, in gamelog_mine.go, which is DEAD CODE. Four selftest checks
//     certify it, including "NEGATIVE CONTROL: safeActor blocks a bare handle",
//     and it has never had a single caller. A function that is unit-tested and
//     unreachable proves something about the source and nothing about the
//     program.
//
//   - scrubber.Value, in scrub.go, which runs at export and is the only reason
//     no handle has ever left a machine. It judges on reMineAssetish alone, and
//     that pattern does not know about PU_Human-... - so it turned 80 of 85
//     ambient NPC names into player tags. Safe, and it destroyed data Sleven
//     says is worth keeping.
//
// This file is the single answer both of them should have been asking.
//
// ===========================================================================
// SLEVEN'S RULES, 2026-08-16
// ===========================================================================
//
//   - PLAYER HANDLES are swapped for a consistent tag, always. Same person,
//     same tag, so the data still joins.
//   - MISSION NPCs have human names WITH SPACES - bounty and combat targets.
//     Those are worth keeping.
//   - AMBIENT NPC ARCHETYPES are scenery. Keep them cheaply; guards and
//     security types may matter later.
//   - THE RULE IS A HINT, NEVER A VERDICT. Anything not clearly an NPC gets
//     swapped. Losing an NPC name costs nothing; leaking a player name costs
//     everything.
//
// So this fails closed: every branch that says KEEP has to earn it, and the
// default is SWAP.

import (
	"regexp"
	"strings"
)

// NameVerdict is what to do with a name.
type NameVerdict int

const (
	// NameSwap is the ZERO VALUE, on purpose. Anything that falls through
	// every rule, and anything a future edit forgets to classify, gets swapped.
	NameSwap NameVerdict = iota
	// NameKeep means this is provably not a person's handle.
	NameKeep
)

// reNPCArchetype matches the ambient NPC naming CIG ships.
//
// Taken from the data on Sleven's machine rather than invented:
//
//	NPC_Archetypes-Male-Human-Civilians-Utilitarian-Technician_Utilitarian_01_<id>
//	PU_Human-Crusader-Guard-Male-Grunt_01_<id>
//	PU_Pilots-Human-Criminal-Pilot_Light_<id>
//
// A handle cannot look like this: Star Citizen handles are letters, digits,
// underscores and hyphens with no internal "-Male-"/"-Grunt" vocabulary, and
// nobody's handle begins "NPC_Archetypes-".
var reNPCArchetype = regexp.MustCompile(
	`^(?:NPC_Archetypes|PU_Human|PU_Pilots|PU_AI|AIModule|Kopion|Marok|QuasiGrazer|Vanduul)[-_]`)

// reNPCRole catches the same family by its role vocabulary, for prefixes CIG
// adds later. Deliberately specific - these are words that appear in asset
// paths and not in handles.
var reNPCRole = regexp.MustCompile(
	`(?i)[-_](?:male|female)[-_]|[-_](?:grunt|guard|civilians|techie|bartender|pilot|security)(?:[-_]|$)`)

// reMissionNPC matches a human name written with spaces.
//
// THE SPACE IS THE WHOLE SIGNAL, and it is a good one: Star Citizen handles
// cannot contain a space. So "Ruto Vega" is a mission character and cannot be
// somebody's handle, while "RutoVega" could be either and is therefore swapped.
//
// Two or more capitalised words, letters and apostrophes and hyphens only.
var reMissionNPC = regexp.MustCompile(`^[A-Z][a-zA-Z'\-]+(?: [A-Z][a-zA-Z'\-]+)+$`)

// rePseudonym matches a tag this program already wrote.
//
// IDEMPOTENCE. Without this, a value swapped at write time would be swapped
// AGAIN at export - producing a tag of a tag, so the same person would end up
// with two different identities and every join across a session would break.
var rePseudonym = regexp.MustCompile(`^player:[0-9a-f]{8}$`)

// reNotAPerson matches the placeholders the log itself uses.
var reNotAPerson = regexp.MustCompile(
	`(?i)^(?:|unknown|none|null|player|vehicle|hazard|<player>|<unnamed>|<id>)$`)

// ClassifyName decides whether a value may be written as it stands.
//
// Returns the verdict and a short reason, because a decision about somebody's
// name should be explainable without re-reading the regexes.
func ClassifyName(v string) (NameVerdict, string) {
	s := strings.TrimSpace(v)

	switch {
	case reNotAPerson.MatchString(s):
		return NameKeep, "not a name"
	case rePseudonym.MatchString(s):
		// Already swapped. Swapping it again would give one person two tags.
		return NameKeep, "already a tag"
	case reNPCArchetype.MatchString(s):
		return NameKeep, "ambient NPC archetype"
	case reNPCRole.MatchString(s) && !strings.Contains(s, " "):
		return NameKeep, "NPC role vocabulary"
	case reMineAssetish.MatchString(scrubIDs(s)) || reMineAssetish.MatchString(s):
		return NameKeep, "game asset"
	case reMissionNPC.MatchString(s):
		// A handle cannot contain a space, so this is a written character name.
		return NameKeep, "mission NPC (spaced name)"
	}

	// EVERYTHING ELSE IS A PERSON UNTIL PROVEN OTHERWISE. This is the branch
	// that protects strangers, and it is the default rather than a case.
	return NameSwap, "not clearly an NPC - treated as a player"
}

// KeepsName reports whether v may be written as-is. Convenience for callers
// that do not need the reason.
func KeepsName(v string) bool {
	k, _ := ClassifyName(v)
	return k == NameKeep
}
