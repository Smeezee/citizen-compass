
# Update - H5 answered: 21 ships. And two of the order's premises are wrong.

Committed: E2 `664616f`, E1 `e1a1d7c`, H2/H3/H5 `3f33dd7`, ledger `f0a0c48`.

## H5 - THE DELIVERABLE. Twenty-one ships.

Ships that fly in game, are not an edition of something we have, and have no
geometry in any of the three libraries:

    Aegis Tiburon              Anvil Arrow           Anvil F7 Hornet Mk Wikelo
    Anvil F8A Lightning        Argo MOTH             Drake Command Module
    Drake Pitbull              Gatac Tyilui          Grey's Basher
    Greycat PTV                Greycat UTV           Mirai Fury
    MISC Starlite              Origin 85X Limited    Origin M80
    RSI Aurora Mk I SE         RSI Aurora Mk II      RSI Hermes
    RSI Mantis                 Power Suit            Vanduul Mauler Destroyer

The order said this number is the only honest input to a decision about RSI's
models, and that it might be small enough that the answer is no. **It is 21.**

## The forty orphans are NOT mostly a name-matching failure

     1  resolved by exact match      Nox_Kue.glb -> XIAN_Nox_Kue
    25  MODELS FOR SHIPS CIG HAS NOT BUILT
    14  genuinely unresolved

Kraken, Galaxy, Orion, Pioneer, Liberator, Hull D, Hull E, Zeus Mk II MR, three
Rangers, three G12s - all in `LOADOUT_UNRELEASED`. No ports, no ship page,
nothing to wire them to. **The model library is running ahead of the game
data.** Different problem, and a better one.

My first pass resolved **zero**, which is the defect in one line: the model
files are bare ship names and the ship records are not. `Kraken.glb` against
"Drake Kraken". Stripping a ship's own manufacturer from the front of its own
name is canonicalisation, not fuzzy matching - and it makes collisions
possible, so a stem reducing to more than one ship is refused as ambiguous.

**The six pairs the order says match "by eye" do not match exactly** - the file
says "Edition" and the ship does not. Refused, and named for a human. "By eye"
is what produced Dragonfly Black -> Yellowjacket.

## The Cutlass Black already has a model

The order and the errata both say the live page "cannot render" the Cutlass
Black or the Constellation Aquila. **The Cutlass Black renders.** What it lacked
was markers - that is E1, and it now says so in its own words: "This ship's 42
changeable ports are listed on the left. We have no measured positions for them
yet." Only the Aquila genuinely needs a Fan Kit model.

## Where the run is

Done: the B5/B6 corrections, H1, E4, E2, E1, H2, H3 analysis, H5.

Not done: H3's WIRING (92 editions to their base hulls, plus the page saying
which hull it is showing), H4 (needs a `.ctm` decoder this repo does not
vendor), H6, H7, H8, H9.
