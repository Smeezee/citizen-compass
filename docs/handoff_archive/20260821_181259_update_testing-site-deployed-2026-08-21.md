# UPDATE — the testing site is deployed and ready for review

    from  Code, 2026-08-21
    url   https://citizencompasstesting.citizencompass-contact.workers.dev
    sha   0e866b8

**The live site was not touched.** Its worker still returns 404.

Two files moved: `/index.html` and `/hardpoint_data.gen.js`. 495 assets were
already uploaded and left alone — exactly and only what I1 changed.

Verified from the origin, not from the exit code:

    /                       200, 1,626,034 bytes, stamped "testing 2026-08-21"
    id="cc-kb", cc-ship::after, id="cc-gate"      all present
    /models/Hammerhead.glb  200, 3,608,636 bytes
    /hardpoint_data.gen.js  200, sha256 identical to what the build wrote

`_verify_find_deployed.mjs`: 27 of 27 against the deployed origin.

**Stated limit:** the gate's markup and script are present in the served bytes.
Whether a browser then blocks is not proven from here — no browser on this
machine, none installed (rule 7). That is check 4 on the deploy script's list
and it is yours to do.

## The deploy exposed a defect in my own I6 sweep

The link sweep reported **449 references before the deploy and 449 after** —
despite index.html gaining a `<script src="hardpoint_data.gen.js">`. A sweep
that reports the same number after you add a file is not reporting on that file.

The inline-JS stripper was removing whole `<script>` elements, so self-closing
`<script src="...">` tags vanished with their src. The sweep was blind to
**every generated data file on the site** — find_data, hardpoint_data,
kb_actions, kb_modes, loadout_data, holo_data, sc_export, find_checksum. Those
are exactly the files whose absence breaks a page while it still serves 200.

Fixed: 449 → **457 references, all 200**. The deployed site was fine; the sweep
was not. I6's clean result stands but was narrower than it read.

Added a named floor so it cannot return quietly.

## What to look at

- A ship with a **3D badge** → the Loadout panel now fills from a file. Try it
  with the API down; it should not care.
- **HoverQuad, X1, X1 Force** — mounts that used to read "S0" and
  "<= PLACEHOLDER =>" now read "not stated".
- **/find** — no server needed.
- **/holo, /download, /stick-test** are reachable by URL only. Nothing links to
  them. Worth deciding on before the flip.
