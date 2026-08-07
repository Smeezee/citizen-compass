# Bundled WebView2 runtime - where it came from and what was checked

    obtained   2026-08-07
    ruled by   Sleven, 2026-08-07, after the provenance question was raised
    for        WO-UI-01 §3 - "bundled WebView UI. Size is not a constraint."

**The payload is gitignored. This record is tracked.** Same separation
`data-layer/external-sources/` uses: the bulk is regenerable, the record of
where it came from must survive.

---

## Why it is bundled at all

The WebView2 runtime happens to be installed on the development machine
(151.0.4129.59). Sleven's ruling:

> The runtime being installed here is a trap, not a convenience: the
> runtime-missing path cannot occur on this machine and will never be exercised
> by normal testing. Bundling makes the failure impossible rather than rare.

---

## Source - NOT Microsoft, and that was a deliberate decision

    package    WebView2.Runtime.X64
    version    151.0.4129.59
    publisher  ProKn1fe          <- a third-party NuGet account, NOT Microsoft
    url        https://api.nuget.org/v3-flatcontainer/webview2.runtime.x64/
               151.0.4129.59/webview2.runtime.x64.151.0.4129.59.nupkg
    size       256,734,355 bytes (244.8 MB)
    sha256     03AE426A5B9482F765B98C0A100D44DCDDF1B3735188A0BF5E981517F3564381

**Microsoft's own fixed-version download could not be used.** The link on
`developer.microsoft.com/microsoft-edge/webview2` is generated client-side by a
version/architecture picker, and unlike the Evergreen bootstrapper
(`fwlink 2124701`) there is no stable URL for it. Guessing a CDN URL and calling
it official was refused - a wrong guess wastes time, and a *working* guess is
worse, because nobody would then check what it actually served.

The risk was put to Sleven explicitly - a 250 MB repackaged browser engine, of
unverified provenance, shipped inside every crew copy, running on other people's
machines, on a build that is deliberately unsigned. **He chose this source.**

---

## What was verified, by evidence rather than by trust

Because the publisher is not Microsoft, the contents were checked rather than
assumed.

### Every binary is authentically Microsoft-signed

    binaries checked                 35
    Authenticode Valid + Microsoft   35 / 35

    Signer  CN=Microsoft Corporation, O=Microsoft Corporation,
            L=Redmond, S=Washington, C=US
    Issuer  CN=Microsoft Code Signing PCA 2024, O=Microsoft Corporation, C=US
    Expires 2027-04-15

**This is the finding that matters.** Authenticode covers the file contents, so
any modification by the repackager - to the main executable or to any single
DLL - would have invalidated the signature. All 35 are valid. The repackager
redistributed authentic Microsoft binaries without altering them.

That does not make the *channel* Microsoft, and this file exists so nobody later
assumes it was.

### Version matches what it claims

    msedgewebview2.exe   ProductVersion 151.0.4129.59
                         FileVersion    151.0.4129.59
                         CompanyName    Microsoft Corporation

### Payload

    80 files, 502.1 MB extracted, at
    citizen-collector/webview2-runtime/151.0.4129.59/

### The one script in the payload was read, not run

`show_third_party_software_licenses.bat` (270 bytes) - Microsoft's credits
display, invoking `msedgewebview2.exe --embedded-browser-webview=show-credits`.
Read only. Nothing from this download has been executed (hard rule 7); the
runtime is loaded by WebView2 at run time, which is the entire point of
bundling it and is what Sleven authorised.

---

## Two distribution landmines that come WITH fixed-version mode

Both are from Microsoft's own distribution documentation and both must be
handled by the packager in §8, not discovered in the field.

### 1. Windows 10 needs an ACL grant that Windows 11 does not

From Fixed Version 120 onward, an **unpackaged Win32 app on Windows 10** must
grant the app-container SIDs read access or the runtime will not start:

    icacls {runtime path} /grant *S-1-15-2-2:(OI)(CI)(RX)
    icacls {runtime path} /grant *S-1-15-2-1:(OI)(CI)(RX)

**Sleven's machine is Windows 11, where this does not apply.** So this failure
cannot occur where it will be tested and will land on the first crew member
running Windows 10 - the same shape as the trap that motivated bundling in the
first place, in a second place.

### 2. Fixed Version cannot run from a network location or UNC path

A crew member who unzips onto a mapped drive gets a program that does not start.
Needs detecting, with a plain-English sentence (§9), not a stack trace.

---

## Re-obtaining it

    Invoke-WebRequest -UseBasicParsing -OutFile wv2.nupkg `
      -Uri https://api.nuget.org/v3-flatcontainer/webview2.runtime.x64/151.0.4129.59/webview2.runtime.x64.151.0.4129.59.nupkg

Confirm the sha256 above, expand it (a `.nupkg` is a zip), and copy
`contentFiles/any/any/WebView2/` to
`citizen-collector/webview2-runtime/151.0.4129.59/`.

**Re-check the signatures after any re-download.** The hash pins this exact
artifact; the signature check is what makes a substituted one detectable.
