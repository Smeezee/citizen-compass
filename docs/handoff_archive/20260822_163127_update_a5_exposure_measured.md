# Update - A5, static-asset exposure measured

A5 done. MEASURED AND REPORTED ONLY - nothing changed, per the order.

`docs/FINDING_static-asset-exposure-2026-08-22.md`. Every figure came from
fetching the deployed sites with curl today, not from reading config.

Testing site: everything is fetchable. Models 200 `model/gltf-binary` 765,808
bytes, images 200, fonts 200, `loadout_data.gen.js` 200 at 3,636,252 bytes. All
six subpages 200. Nothing returned 401, 403 or any challenge.

**And it is worse than CURRENT-STATE.md recorded.** That note said the password
gate does not cover static assets. Measured today it does not cover the HTML
either: `GET /` with no password and no session returned 421,413 bytes of the
real site, carrying Avenger 20 times, Hammerhead 5, Polaris 5, Redeemer 6,
alongside the word "Password". The gate is a CSS rule plus a `localStorage`
flag. The content is delivered before any password is entered.

Live Netlify site does NOT have the property: `/` is 200, `/models/*` and
`/images/*` are 404, and the served bytes reference no separate assets at all.
The exposure came in with the 3D viewer and is testing-site only.

Volume: 235 models / 341.8 MB / mean 1.49 MB; 241 images / 4.0 MB.

The Referer/Origin check is reported honestly as very weak - one curl header
flag defeats it, and it breaks users whose Referer is stripped. It buys hotlink
prevention and casual-save friction, not protection.

Recommendation: fix the DESCRIPTION now, not the exposure. The most wrong thing
today is a gate presenting itself as a password while delivering the whole page
to anyone who asks - the same defect class this project hunts, something
reporting a protection it does not provide. The Worker route waits, partly
because no CIG-sourced asset is on this site yet.

Not implemented. Awaiting Sleven's decision.

Next: A6 - sweep, deploy to testing, verify from the served bytes.
