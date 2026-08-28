# Update — Rule 15's subprocess half was still open in `build_deploy.py`, and it fails with exit code 0. Fixed, plus a second deploy.

**2026-08-27 22:43 local · Code (background session)** — follow-on to the 22:33
deploy. Version `09886d94-64ab-455d-b221-a8a1b019425d`.

## The defect: six `_sp.run(..., text=True)` calls with no `encoding=`

`testing/_src/build_deploy.py` had **seven** subprocess calls. One — the holo
gate at line 455 — already carried `encoding="utf-8"`. The other six did not.

**This is the same defect that stopped `run_all_controls.py` at control 14 of
98 two hours ago**, in the file that builds the page.

## Proven by behaviour, not by reading it — and the failure shape is worse than a crash

I ran a child that prints `San'tok.yāi` through both call shapes and recorded
what came back:

    BEFORE-shape (text=True, no encoding)   returncode=0   stdout=None
    AFTER-shape  (encoding=utf-8)           returncode=0   stdout="San'tok.yāi\nLINE-AFTER-THE-NAME\n"

**`returncode=0` and `stdout=None`.** The reader thread dies, prints a traceback
naming no ship, and `subprocess.run` returns *successfully* with the output
thrown away. It does not raise in the parent.

That matters because of what the build does next:

    sys.stdout.write(_r.stdout)                       -> TypeError, no ship named
    sys.stdout.write(_r.stdout or "(the gate produced no stdout)\n")   -> prints
                                                         that, and CARRIES ON

**The second shape is rule 12 exactly.** A gate whose entire output was eaten by
cp1252 reports "no stdout" and the build continues, because the returncode it is
judged on is 0. The pass/fail signal itself survives — only the *reason* is
destroyed — but the line that would have named the failing ship is the line that
cannot be read.

The build has not hit this yet only because the children that print ship names
have so far printed ASCII ones. **`XNAA_SanTokYai` is now in the marker set**,
so that was a matter of time.

All six fixed with `encoding="utf-8", errors="replace"`, matching the style of
the one site that already had it, with the reason written at the first.

## Honest limit on my verification

I intended to prove the fix inert by rebuilding and comparing byte hashes.
**I cannot claim that, because C1 wrote to `data-layer/derived/` between my
two builds** — 20:23:55, 20:25:47 and 20:26:29, in the five minutes between my
deploy and my rebuild. The comparison is confounded and I am not going to
present it as clean.

What I can state: the change adds two keyword arguments to six subprocess calls
and touches no data path, and the probe above shows the AFTER shape returns the
same string a working BEFORE would have. **Inertness is argued, not measured.**

## Which is also why there was a second deploy

Disk moved under the first one. Between the two builds:

    hulls added        38 -> 41
    ports moved      1575 -> 1720
    hull markers   6403 on 270 -> 6412 on 271

Against the last commit, the deployed state is now **265 -> 271 hulls, 6300 ->
6412 markers, 6 hulls added** (`AEGS_Gladius_PIR`, `BANU_Defender`,
`MRAI_Pulse_LX`, `ORIG_600i_Executive_Edition`, `RSI_Hermes`, `TMBL_Nova`) and
**87 hulls whose coordinates changed**.

C1 appears to still be working. **The deployed page is a snapshot of an actively
moving dataset and will be stale again shortly** — that is not a fault, but it
should not be read as a final number.

## Verified on the served site after the second deploy

    Aopoa San'tok.yāi   10 dots, 10 visible, model loaded, spread 205x140px
    Tumbril Nova         2 dots,  2 visible, model loaded, spread 0x30px

San'tok.yāi deliberately: it is the exact name this whole rule exists for, and
it now renders end to end through a build that can read its own children.

Nova's two dots sit in a vertical line (x-spread 0). It is a tank with two
stacked mounts, so that is plausible rather than clustered — **but I have not
proven it and am not going to call it verified.**

`_verify_deployed_links.mjs`: SWEEP CLEAN, canary reporting. 4 browser checks
GREEN, deploy guard clean, 1 file uploaded.

## Housekeeping

Two probe files moved to `_to_delete/probes-2026-08-27/` per rule 1, not deleted.
Nothing committed, nothing pushed, live site untouched.
