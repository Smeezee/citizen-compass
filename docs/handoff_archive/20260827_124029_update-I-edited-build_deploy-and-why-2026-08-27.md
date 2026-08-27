# Update — I have edited `testing/_src/build_deploy.py`. Read this before your next build.

**C1, 2026-08-27 12:47 local. Rule 14 notice, not a request.**

Sleven told me to stop asking and wire it in. I did. **One block added, nothing
removed, nothing reordered.** Backup at `/tmp/bd.bak` on the mount.

## Where, and why there rather than anywhere else

`build_deploy.py`, immediately after `_fleet = json.loads(rd(_holo))` — about
line 1185, before `_by_file` is built.

**Because that is where the ship page's markers are actually born, and it was
the one place no overlay reached.** `build_holo_data.py` has read
`alignment_overlay.json` for weeks, and it feeds `holo_data.gen.js` — the HOLO
page. The loadout page's markers come from this block, which read
`hardpoints_fleet.json` **raw**. So every alignment correction ever made moved
one page and not the other, and the page Sleven actually opens is the one it
missed. That is worth knowing independently of anything I did today.

The block applies `alignment_overlay_client.json` with the **same match-or-die
rule** your other overlay uses: an entry naming a ship or a port that is not
present exits the build. It prints how many ports moved, or says the overlay is
absent and the markers stay derived.

**It is inert if the file is missing.** Delete
`data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json` and the
build behaves exactly as it did this morning. That is the revert.

## What it does, measured on real hulls before you run anything

Simulated against the current `loadout_marker.gen.js`, in normalised units where
1.0 is the hull's longest half-extent:

    DRAK_Vulture   4 of 6 markers move
      hardpoint_weapon_nose_left    moves 1.102
      hardpoint_weapon_nose_right   moves 1.102
      hardpoint_cm_launcher_left    moves 0.368

    AEGS_Gladius   9 of 18 markers move
      hardpoint_gun_left_wing       moves 0.629   -> -0.445
      hardpoint_gun_right_wing      moves 0.630   -> +0.446
      hardpoint_missilerack_*_outer moves 0.15    -> +-0.703
      hardpoint_countermeasure_*    moves 0.660   -> +-0.071

**The Vulture's nose guns were more than a full half-extent from where the game
puts them.** Note the old positions were already SYMMETRIC (-0.544 / +0.545) —
the name-based placer got left-versus-right right and the position wrong, which
is exactly why this looked plausible for so long.

## What I need from you

**Run the build and let the guard speak.** My entries are emitted only from the
intersection with the fleet record, so by construction none can miss — and by
construction is weaker than a test. If it exits, the construction is wrong and I
want to know.

If you would rather this block lived somewhere else, or read the file through a
helper next to your other loaders, **move it — it is your file and I am handing
it straight back.** I put it inline to keep the change small enough to revert by
eye.

## Separately: `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST AND CANNOT

It exits in `merge_join` before reaching any overlay:

    7 recovered ship(s) collide with ships already placed. Refusing to emit
      ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

`holo_data.gen.js` is stamped 08-17; `hardpoints_fleet.json` is 08-27 02:52.
**This is NOT from your M5 import** — the fleet file predates it by ten hours.
It is older breakage that nobody has hit because `build_deploy.py` does not call
this generator. I have not touched it beyond the two-overlay change, which sits
after the failure point and is currently unreachable. Recording it so it stops
being invisible; it is not urgent and it is not yours unless you want it.

*C1*
