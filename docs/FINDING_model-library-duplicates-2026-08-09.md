# FINDING — the 235-file model library contains only 213 distinct models. Two ships share one file, and the file Code offered as a stand-in for the Cutlass Black is one of them.

    from      C3 (Cowork), 2026-08-09
    for       Sleven + C1 + Code
    prompted  docs/handoff_archive/20260809_173955_update-2B-holo-viewer-...md, which
              reports no base Cutlass Black and no Constellation Aquila in the library
              and offers the Best In Show 2949 edition as a possible stand-in.
    method    md5 of all 235 .glb in testing/_deploy/models

---

## 1. Code's report is confirmed, and I checked it rather than took it

No `Cutlass_Black.glb`. No `Constellation_Aquila.glb`. What exists:

    Cutlass_Black_Best_In_Show_Edition_2949   Cutlass_Blue   Cutlass_Red   Cutlass_Steel
    Constellation_Andromeda   Constellation_Phoenix   Constellation_Phoenix_Emerald   Constellation_Taurus

So 27 of the 35 derived hardpoints have no hull to sit on. That part stands.

## 2. The stand-in is not safe, and the reason is new

**`Cutlass_Black_Best_In_Show_Edition_2949.glb` and `Cutlass_Steel.glb` are the same
file** — byte-identical, md5 `d346da6d75be81f7a0597a8444d9cae4`, 728,552 bytes each.

The Cutlass Steel is not a paint. It is a troop transport with a different rear section and
different doors. **A Black-family livery and a Steel cannot both be that geometry**, so at
least one of those two names is pointing at the wrong hull — and nothing in the library says
which.

Code's framing was "one line from Sleven confirming the hull is identical and it works."
**The honest position is weaker than that.** We do not currently know what airframe that
file is. Confirming "BIS 2949 is the same airframe as a base Cutlass Black" is true in the
game and still would not make the substitution safe, because the question is whether *this
file* is a Cutlass Black at all.

Two other things point the same way: the file is 728 KB against 1.83 MB for the Cutlass Blue
and 1.23 MB for the Red, so it is markedly lighter than its siblings; and there is no
Aquila-shaped candidate at all — the Andromeda, Phoenix and Taurus are three distinct files
and the Aquila's scanning nose and rover bay make it a genuinely different airframe, so
there is nothing to substitute even carelessly.

## 3. The wider number

    235 files
    213 distinct models
     22 files sharing 16 models

Most of those groups look like liveries of one airframe and are fine — Carrack and Carrack
Expedition, Caterpillar and its two editions, Avenger Titan and Renegade, Ursa and Fortuna,
Nox and Kue, Pulse and LX, F8C and Executive Edition, Mustang Alpha and Vindicator, the two
Argo Mole editions, the three Ballistas.

**Four groups pair up ships I would not expect to share geometry.** Flagging, not ruling —
whether two hulls are the same airframe is a question about the game, and the game changes:

    Cutlass_Black_Best_In_Show_Edition_2949  +  Cutlass_Steel
    F7A_Hornet_Mk_I                          +  F7C_Hornet_Mk_I
    Mustang_Gamma                            +  Mustang_Omega
    C8_Pisces                                +  C8R_Pisces

Each of those is a pair where the two ships differ in the game by more than paint. **Ten
seconds each from someone who has flown them settles all four**, and I would rather ask than
assert from training data that has a cutoff.

## 4. Why this matters past the viewer

Every one of these files feeds the ship pages, not just the holo viewer. If a name points at
the wrong hull, the site shows the wrong ship under the right name — **and it looks entirely
correct**, which is the failure shape this project keeps logging. It is worth a checker in
the auditor layer: flag any two ship slugs resolving to one model file, so a new duplicate
announces itself instead of being found by someone md5ing the folder two years from now.

That is a flag-only check, consistent with the standing rule that auditors never auto-fix.

## 5. What I would do about the viewer, and the alternatives

**Ship it with two ships and say so** — which is what Code built. The page already names the
hulls it cannot show. Costs nothing, hides nothing, and the viewer is honest on day one.
This is what I would do.

**Substitute BIS 2949 for the Cutlass Black** — do not, on the current evidence. Not until
somebody establishes what that file actually is. Markers on the wrong hull still look like
markers.

**Get the two missing models** — the real fix, and it is not a viewer job. Base Cutlass Black
and Constellation Aquila are absent from a 235-ship library, which is itself worth knowing
regardless of the viewer.

## 6. What I checked and what I did not

**Checked:** md5 of all 235 files; sizes of the Cutlass and Constellation families;
that no file named for a base Cutlass Black or an Aquila exists under any casing.

**Did NOT check:**
- **Which name in each duplicate pair is the wrong one.** The hash proves two names share one
  file; it cannot say which name is correct.
- Whether the duplication comes from the import pipeline or from the source data. Nobody has
  traced it.
- `data-layer/ship_resolution.json` carries no dimensions, so it cannot settle any of the four
  pairs. I looked; there is no ships.json in the repo to compare published dimensions against.
- My reading of which four pairs are suspicious is from knowing the ships, not from the repo.
  **Treat §3's four as questions, not findings.**
