# The holo viewer prototype, extracted so it can be READ

    from    C1, 2026-08-23
    source  Downloads\citizen-compass-holo-viewer_1.html
            sha256 5e91d8e41cb250ca8acd795a81759b9234fa565fa2cec181cd9323fcbe6eac1a
            13,314,680 bytes, built 2026-08-09 by C3, byte-identical to
            citizen-compass-holo-viewer.html - the `_1` is only Chrome's
            duplicate-name suffix from a re-download.

## Why this folder exists

`ORDER_every-ship-is-a-hologram-2026-08-22.md` H1 says to port the prototype's
rendering into `cc_viewer.js`. **The prototype was a 13.3 MB blob in Downloads,
outside the repo, so "port it" meant "reimplement it from screenshots."** It does
not any more.

## What was stripped, and what is left

    13,314,602 chars total
    12,478,956   four base64 model blobs   -> replaced with "<MODEL_BLOB_STRIPPED>"
       603,445   vendored three.js         -> not copied, we already vendor it
        26,375   TrackballControls         -> not copied
        27,578   postprocessing passes     -> not copied

    viewer.js    60,670 B   THE PROTOTYPE. All of it.
    viewer.css    5,725 B   the whole look
    viewer.html 111,427 B   markup with scripts and style removed

**Two thirds of a megabyte of code turned out to be 66 KB of ours and the rest
vendored.** The thing everyone has been describing from screenshots is smaller
than the ledger file.

## Where each ordered item lives in `viewer.js`

    buildGeometry / edgesFor / edgeOpacity    the six render styles (H1)
    rebuildMarkers / markerSize               marker shape + kind coding (H1e)
    updateLabels                              THE LABELS - and where H1b's
                                              collision fix goes
    sideLabel                                 left/right naming - where the
                                              `left top` vs `right_top` defect
                                              in H1d lives
    openDetail / closeDetail                  the click readout panel (H1d)
    frameShip                                 auto-frame (E4 on the live page)
    applyHot / visibleHP                      the Guns/Racks/CM/Turret filters
    buildLoadout                              the left list, incl. the missile
                                              grouping H1c wants
    ungzip                                    models are gzipped base64 inline

## Read this before porting

- **The models are inline and gzipped.** That is a demo technique and it does not
  scale to 316 ships. The live page already loads `.glb` per ship on demand and
  that architecture stays; only the RENDERING comes across.
- **The depth-only pre-pass and `FrontSide` are load-bearing** and the reason is
  measured, not stylistic: without them a 353,731-vertex mesh went to 63.7% pure
  white pixels. See section 5 of `PROTOTYPE_holographic-ship-viewer.md`.
- **This is a snapshot for reading, not a second copy to maintain.** Rule 14 —
  one writer per artifact. Do not edit these files and expect anything to happen;
  the live page is `testing/_src/`. If the prototype itself is ever rebuilt, this
  folder is regenerated from it, not hand-patched.
