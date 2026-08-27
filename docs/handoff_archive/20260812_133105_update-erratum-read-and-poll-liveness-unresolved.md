# Update — erratum read and verified. Its §3 is a real risk, still unresolved, and headless cannot settle it.

## The erratum checks out

Read `docs/ERRATUM-joystick-rebind-seam-2026-08-10.md`. **The message I received
contained only its header block** — no body — so I read the filed document
instead. Its claims verified against the working tree rather than taken on
trust: the hooks are at `device_engine.js` lines **464, 492, 545**, all three
guarded `!!(window.KBREBIND && KBREBIND.listening())`, exactly as it says.

**One gap in the amendment itself.** Its stated purpose is *"Amending it rather
than leaving a wrong order in the repo for the next re-run"* — but the erratum
is a **separate file**, and `prompt-code-keybind-rebind-joystick-2026-08-10.md`
contains **zero** references to it. A future session re-running that order reads
§1's *"cleanest seam is probably inside fireDev"*, edits `keybinds.src.html`,
builds, and walks into the same silent revert. The wrong order is still in the
repo, just with a correction filed beside it that nothing points to. One line at
the top of §1 would close it. Not editing C1's document myself — one writer.

## §3: the risk is structurally real

Confirmed by reading `poll()`:

```js
renderDevice();
rafId=requestAnimationFrame(poll);
```

`renderDevice()` runs **before** the re-arm, and unconditionally — pad or no
pad. If it throws, the re-arm never runs and the loop dies after one frame,
silently. `renderDevice()` calls `buildDevice()`/`paintDevice()` with **no
container guard**. So the mechanism the erratum describes exists.

## But it cannot be settled headless, and I nearly reported that it was

I thought the erratum was wrong that this needs a real browser — `renderDevice()`
runs whether or not a stick is connected, so an empty-handed browser should
answer it. I built the test. It reported:

```
+2.8s  poll ran 0 times   listening=true
POLL LOOP IS DEAD - renderDevice() threw, the re-arm never ran.
```

**That conclusion is wrong.** Two things did not fit: `uncaught errors seen:
none` — a throw inside a rAF callback would surface — and `rafId` climbing
1 → 2, meaning rAF was *requested* and never *fired*.

So I ran a control on a page with nothing in it but a rAF loop:

```
plain requestAnimationFrame fired 1 times in 2500ms
```

**`requestAnimationFrame` does not run in this headless setup.** The zero
invocations were the environment, not the code. Had I stopped one step earlier I
would have filed a confident report of a bug that my own test could not see.

Worth recording as the mirror image of what this project usually catches: not a
check that passes without looking, but one that **fails without looking**, and
reads as a finding.

## What would settle it, in about ten seconds

A **visible** browser, not a stick — that part of the erratum can be narrowed.
Open `/keybinds`, click a binding on the Keyboard/Mouse tab to start a rebind,
and watch whether the live device readout keeps updating for a few seconds. If
it freezes, `renderDevice()` is throwing and the fix needs a guard in
`renderDevice` — **not** a try/catch around `poll()`, which would hide it.

## Master order received

`docs/prompt-code-MASTER-clear-the-queue-2026-08-10.md` is on disk and carries
the go-ahead to commit, push and deploy. Joystick work is its item **1c**,
already done and live. Remaining: **1a/1b** holo viewer fixes and the 167-ship
fleet dataset, **1d** the dead `#kbbq` search under Capture-ON and the End key,
**§2** fonts (licence now closed, chrome-only), **§3** the collector shortcut
ordering — which is the bug I found and proposed yesterday.
