# Update: three commits pushed. WebView2 bundling hit a provenance fork.

**2026-08-07.** Pushed `1eadf97..d314540` - `8594ed3`, `c6a74a2`, `d314540`.
Level with origin, nothing matching `wrangler`/`.env`/`password`/`secret`/`.dump`
in any of the three diffs.

## Correction to a number I gave

I said the fixed-version runtime was **~130 MB**. Microsoft's own distribution
doc says **"The Fixed Version binaries are over 250 MB."** My figure was wrong.
It does not change Sleven's ruling - the reasoning was that size is irrelevant
against a 100 GB game - but the number should be right in the record.

## The official download cannot be fetched headlessly

`developer.microsoft.com/microsoft-edge/webview2` builds the fixed-version link
**client-side from a version/architecture picker**. There is no `fwlink` for it
(unlike the Evergreen bootstrapper, 2124701, and the Evergreen standalone
installer, which do have stable links). Fetching the page returns the picker UI,
not a URL.

I will not guess a CDN URL and present it as official - an invented link that
happens to 404 wastes an hour, and one that happens to *work* is worse, because
nobody would check what it actually served.

## A programmatic source exists, but it is NOT Microsoft

NuGet carries `WebView2.Runtime.X64` **151.0.4129.59** - exactly the version
this machine runs - described as "Webview2 runtime for Fixed Version
distribution". 1.18 M downloads.

**It is published by a third-party account (`ProKn1fe`), not Microsoft.**

That is a supply-chain decision, not a technical one, so it is Sleven's:

- **what it is:** a repackage of a 250 MB browser engine
- **where it goes:** shipped inside every crew copy, run on other people's
  machines, on a build that is **deliberately unsigned**
- **what it defeats:** the whole point of bundling is removing an
  install-time failure. Trading a rare missing-runtime error for an
  un-provenanced browser binary is a different bargain than the one ruled on.

The project's standard is that unverifiable provenance is stated, not assumed.
Same rule that keeps `data-layer/external-source-manifests/` tracked.

## Two distribution landmines found in the docs - both affect §8

1. **Windows 10 + Fixed Version 120 or later, unpackaged Win32 app** requires
   these to be run on the *user's* machine or the runtime will not start:

   ```
   icacls {path} /grant *S-1-15-2-2:(OI)(CI)(RX)
   icacls {path} /grant *S-1-15-2-1:(OI)(CI)(RX)
   ```

   Sleven is on Windows 11, where this does not apply - **so this failure cannot
   occur on the machine where it will be tested, and will land on the first crew
   member running Windows 10.** That is precisely the trap Sleven identified
   about the installed runtime, in a second place.

2. **Fixed Version cannot run from a network location or UNC path.** A crew
   member who unzips to a mapped drive gets a program that does not start.

Both need handling inside the packager and a plain-English error, not discovery
in the field.

3. Extraction must be `expand {cab} -F:* {dest}` - Microsoft explicitly warns
   that File Explorer produces the wrong folder structure.

## Not blocked on this

The runtime is a drop-in payload. I am proceeding with §6 (continuous detection)
and §7 (follow-the-game) now, and building the runtime resolution - env var
`WEBVIEW2_BROWSER_EXECUTABLE_FOLDER` / `browserExecutableFolder`, presence
check, plain-English failure - so the CAB drops in whenever its provenance is
settled.
