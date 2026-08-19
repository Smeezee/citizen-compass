# STOP POINT 1 — the installer technology, the antivirus answer, and a blocker

    from      Code, 2026-08-18
    for       Sleven
    order     V1 §1 / queue item 3a
    status    NOT BUILT. Three things need his ruling first, and one of them is
              a straight blocker on this machine.

---

## 1. THE ANTIVIRUS ANSWER, which is what the stop point is for

**Yes for one shape, no for the other, and the difference is the whole point.**

**An unsigned installer EXE — NSIS, Inno Setup, a self-extracting stub — is
treated materially worse than a bare exe.** That shape is what droppers use;
the stubs are the same stubs; heuristic engines score them accordingly, and
they carry a brand-new file hash with no reputation behind it.

**An MSI is not that shape.** It is data executed by Windows Installer rather
than a self-extracting program, and it is the shape corporate deployment uses,
so it is not inherently suspicious.

**BUT — and this is the part I will not overstate —**

- **Every unsigned download gets SmartScreen.** Mark-of-the-Web plus no
  publisher reputation produces "Windows protected your PC" on a `.exe` and on
  an `.msi` alike. Sleven has ruled the download ships unsigned, so this
  happens today with the bare exe and will happen tomorrow whatever we pick.
  **An installer does not add that problem and does not remove it.**
- **I cannot measure any of this here.** There is no AV bench on this machine
  and no corpus of engines to test against. What I have written above is a
  statement about the shapes, not a measurement, and the project's own standard
  says to mark that difference. **If this matters enough to decide on, the way
  to know is to build one candidate and put it through VirusTotal.** I can
  produce the candidate; the upload is a decision about publishing an artifact
  and it is not mine to take.

**One thing IS measurable and worth weighing:** the collector today is an
unsigned Go .exe, and his wife and his friend have already run it. **A
self-installing exe keeps that exact shape.** An MSI introduces a shape they
have not run before, at the same moment as an update mechanism that has never
been tested end to end.

---

## 2. THE BLOCKER — WiX cannot be built on this machine

    dotnet --version     fails; no SDK is listed
    wix                  not installed
    candle.exe/light.exe not installed (no WiX v3 either)
    signtool.exe         not present

WiX v6 is a .NET global tool. Building it here means installing the .NET SDK and
then fetching WiX from the network — software installed outside this repo, which
hard rule 6 says I ask about every time, and third-party code fetched and run,
which rule 7 has its own opinion about.

**So the MSI route is not "the bigger job". Right now it is not a job I can
start at all without permission to install two toolchains.**

---

## 3. WHAT I RECOMMEND, AND IT IS NOT THE MSI

**A self-installing collector.exe.** The same single file that is downloaded
today, with `--install` and `--uninstall` modes.

It meets every requirement in the order:

| the order says | how |
|---|---|
| ONE downloadable file, no zip | it is the exe that is already downloaded |
| NO ADMIN RIGHTS | copies to `%LOCALAPPDATA%\Programs\CitizenCollector`, writes `HKCU`, never touches `HKLM` or Program Files |
| Start menu entry, desktop shortcut | `shortcut.go` already writes .lnk files and verifies the icon resolves |
| a REAL Add/Remove Programs entry | `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\CitizenCollector` — per-user ARP is a documented, unelevated mechanism |
| uninstaller takes the startup entry with it | it is our code, so it removes exactly what our code created, and it is checkable |
| uninstall asks separately about data | a prompt we write, rather than an MSI feature we would be bending |
| refuse to run from a temp or archive path | `install_location.go` already does this - `GuardInstallLocation` exists and runs today |
| adopt an existing folder install | our code, reading `collector-install-id.txt` and `collector-consent.txt` - the same files we already write |
| reproducible from this repo | `go build`. Nothing else. |
| no runtime the user must fetch | a static Go binary |
| signable later | one exe to sign, exactly as today |

**What it gives up against an MSI:** Windows Installer's own bookkeeping,
upgrade codes, transactional rollback of a failed install, and the corporate
deployment story nobody here needs. Those are real, and for a fan tool
installed by three people they are worth less than not requiring a toolchain
this machine does not have and not changing the file shape his crew already
runs.

**Rejected, with reasons:**

- **NSIS / Inno Setup** — the worst antivirus shape available, and the reason
  this stop point exists.
- **Squirrel / ClickOnce** — .NET runtime dependency; ruled out by "no runtime
  the user must fetch".
- **A self-extracting zip** — no ARP entry, so it fails the first requirement.
- **MSI via WiX** — the right answer if the tooling existed and if the shape
  change were free. Neither is true today. **Worth revisiting the day Sleven
  signs**, because a signed MSI is genuinely the best end state.

---

## 4. THE THIRD THING I NEED, whichever technology wins

**Testing an installer writes outside the repo on THIS machine** —
`%LOCALAPPDATA%\Programs\`, `HKCU\...\Uninstall`, the Start menu folder and the
desktop. Hard rule 6 says I ask before writing any of those, every time, even
having been told something similar before.

I can do it entirely inside a throwaway prefix if he prefers — a temp root and a
scratch registry key — and prove the mechanism without ever touching the real
Start menu. That proves the code and not the integration. **His call which he
wants**, and I would rather ask than discover afterwards that a test left a
shortcut on his desktop.

---

## WHAT I NEED FROM SLEVEN

1. **Self-installing exe, or MSI?** My recommendation is the exe, above.
2. **If MSI: may I install the .NET SDK and WiX on this machine?**
3. **May installer testing write to the real `%LOCALAPPDATA%`, `HKCU` and Start
   menu — or should it stay inside a throwaway prefix?**
4. **Optional:** if the antivirus question is worth settling with evidence
   rather than reasoning, say so and I will produce a candidate binary for
   somebody to put through VirusTotal.

Meanwhile I am carrying on with items 4, 5 and 6, none of which touch the
collector.
