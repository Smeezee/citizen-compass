# ADDENDUM to ORDER_the-ship-page-2026-08-22-FINAL — tabbed layers, and a name collision found after the order was written

    from    C1, 2026-08-22, while the L-run was in progress
    for     Code
    status  GO. Folds into the run you are already on. **Read §1 NOW if you have
              not finished L9** - it changes how the page is laid out and it is
              cheaper to know before than to retrofit after.
    ledger  same file. Items are numbered M-, continuing after L17.

---

## 0. A DEFECT FOUND AFTER THE ORDER WAS WRITTEN. Check your L1-L5 work against it.

**22 ship display names are duplicated across 51 records.** `Name` is a label;
`ClassName` is the key.

    AEGS_Hammerhead      "Aegis Hammerhead"   crew 9   relays: body, cockpit, tail
    AEGS_Hammerhead_GS   "Aegis Hammerhead"   crew 8   a different layout entirely

    worst offenders: RSI Apollo Medivac x4 · Grey's Shiv x4 ·
                     RSI Apollo Triage x4 · Aegis Idris-P x3 ·
                     Polaris, Carrack, Caterpillar, Valkyrie, Zeus Mk II CL,
                     Cutlass Blue and 12 more at x2

**How it was found, because the method matters:** two extractions of the same
ship disagreed. One took the first record with that name, one took the last.
**Neither was wrong; the key was.**

**KEY ON `ClassName` EVERYWHERE.** If any L1-L5 output is keyed or grouped on
`Name`, 51 records silently collapse into 29 and a ship shows another variant's
loadout under its own name. **Go back and check. Report what you found.**
Display the `Name`, join on the `ClassName`.
*Control:* both Hammerhead records survive the pipeline as distinct entries.

## 1. RULING - THE SHIP PAGE IS TABBED LAYERS, SMALL BY DEFAULT

Sleven, 2026-08-22: *"The ship page should be small, and there should be ways to
get this information if people want to get it... I want it available, but I don't
want it to be like they have to see it."*

**One page. One URL. Quiet tabs. Each tab addressable.**

**The default view carries the model, the swappable components, and the readout.
Nothing else.** That is what somebody came for.

Everything else sits behind a row of **plain text labels** - no icons, no colour,
no badges, nothing competing with the ship:

    Loadout   Engineering   Liveries   Crew   Where to buy   Specs

- **`#engineering` and friends are real URL fragments.** "Where are the
  Caterpillar's fuses" is answered with a link, not directions.
- **The default tab is ALWAYS Loadout.** It never remembers what was last opened -
  somebody arriving from a shared link sees what everybody else sees.
- **A tab only exists when there is data behind it.** 25 ships have no mount data;
  some have no relays. **Those ships show no such tab** rather than a tab that
  opens onto an apology. Same honesty rule as everywhere else, applied to
  navigation.

*Rejected - collapsed sections down one page:* still conceptually long, feels
heavy even closed, and cannot be linked to.
*Rejected - separate sub-pages per layer:* reloads the 3D model on every move
between layers, and the model is the expensive part.

## 2. THE PART THAT ACTUALLY KEEPS IT SMALL

**Tabs alone hide data; they do not make a page light.** If everything still
downloads, nothing was saved.

**One generated file per layer, fetched the first time its tab is opened.** The
default page ships loadout data and nothing else. Engineering data arrives when
Engineering is opened, and never otherwise.

**This is the future-proofing, not a nicety.** Every idea in
`docs/IDEA_unused-ship-data.md` becomes another tab and another file, and **the
default page gets no heavier however many are added.** Build the loader once, as
a pattern, so adding a layer later is a data file and a label - not a rebuild.
*Control:* with the network watched, opening a ship fetches the loadout layer and
**nothing else**; opening Engineering fetches exactly one more file; reopening it
fetches nothing.

## 3. THE WORK

**M1. THE TAB SHELL.** Per §1. Labels, fragments, lazy per-layer loading per §2,
tabs suppressed where there is no data.
*Control:* a ship with no relays renders no Engineering tab. A direct link to
`#engineering` on that ship lands on Loadout without erroring.

**M2. THE ENGINEERING LAYER - relays and fuses.**
Structure is **ship → relay → fuse slots**. A relay's `HardpointName` says where
it sits; its `ClassName` says how many fuses it holds - `RELAY_1slot`,
`RELAY_2slot`, `RELAY_3slot`. Every fuse is the same part,
`Fuse_subItem_standard`, so **what varies is how many and where**.

    305 records carry relays · 1,419 fuse slots
    Aegis Idris-P   15 relays / 37 fuses    Drake Vulture  1 relay / 2 fuses
    RSI Polaris     12 relays / 26 fuses    MISC Prospector 1 relay / 2 fuses

Strip the `hardpoint_relay_` prefix for display; the remainder is the location and
it reads true - the Caterpillar has a relay on the **jump drive**, one on the
**tractor beam**, one per cargo module; the Polaris splits **port and starboard**
engine relays; the Idris pairs bridge, engineering, medbay and mess hall left and
right.

**A working prototype exists and Sleven has approved its shape** - one row per
relay, location on the left, one bar per fuse slot on the right, sortable by
fuses / relays / crew / name.
**One bar means a one-slot relay. Do NOT draw empty positions** - a greyed slot
reads as "a fuse is missing here", which is a real state in game and is not what
the data says. That exact mistake was made and corrected in the prototype.

**M3. PLAIN-LANGUAGE HOVER, and this is a page-wide pattern, not a fuse feature.**
Hovering a value explains it in one sentence a person who has never read a game
file can understand. On the fuse gauge: *"This relay holds 3 fuses. If one blows,
engine room is where you go to swap it."*
**The readout is full of values like `EM 818` and `IR 5,890` that mean nothing to
a newcomer.** A hover that says it plainly is cheaper than a help page nobody
reads. **Reachable by keyboard, not hover alone**, or it does not exist for
anyone who does not use a mouse.

**M4. WHAT IS NOT ESTABLISHED, and must not be implied.**
Fuse **ratings and failure behaviour are not in this data** - only counts and
positions. Whether a blown relay disables the components near it **is not
stated**. Ship-level `PenetrationMultiplier` reads `{Fuse: 0.7, Components: 0.4}`,
which **suggests** damage reaches fuses before components. **Suggests. Say so, or
say nothing.**

**M5. THE OTHER LAYERS - shells only, populated later.**
`Liveries` (L7 already builds the data), `Crew` (802 seat ports, 241 pilot, 22
bedding), `Where to buy` (the shop layer already shipped), `Specs` (dimensions,
mass, career, role). **Build the tab mechanism to carry them. Do not populate
Crew or Specs in this run** unless the layers above are finished and the run has
time.

**M6. LEDGER + PUNCH LIST.** Add to `docs/PRE-LIVE-PUNCH-LIST.md`: the layers
that exist as shells, and the `Name`-vs-`ClassName` collision as a class of
defect to check for wherever ships are grouped anywhere in the project.

## 4. WHAT MUST NOT HAPPEN

- **Do not key or group ships on `Name`.** §0.
- **Do not draw empty fuse positions.** M2.
- **Do not load a layer nobody opened.** §2.
- **Do not show a tab with nothing behind it.** §1.
- **Do not let the default tab be remembered.** §1.
- **Do not claim fuse behaviour the data does not state.** M4.
- **Do not deploy the live site. Do not cut a release. Do not `git add -A`.**

## 5. REPORT

- Whether any L1-L5 output was keyed on `Name`, and what you had to redo.
- The network trace for §2: what a default ship page fetches, and what opening
  one tab adds.
- Anything here you think is wrong. **§2's per-layer loading is the part most
  worth arguing with** - if the layers turn out small enough that splitting them
  costs more than it saves, **measure it and say so** rather than building a
  loader that earns nothing.
