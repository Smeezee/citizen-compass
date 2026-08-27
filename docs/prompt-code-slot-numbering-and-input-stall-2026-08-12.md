# PROMPT FOR CODE — the sticks are js2 and js3 with no js1, which breaks every export. Plus input stalls on tab switch.

    from    C1, 2026-08-12
    for     Code
    basis   A photo of `/keybinds?v=2` running on the friend's machine with the
              real VKB pair. First hard evidence anyone has had from that
              hardware. Everything below is read off that screenshot, not
              inferred.
    scope   device_engine.js (injected-block rule applies), keybinds.src.html.

---

## 0. Detection works. Rendering works. Stop looking there.

The screenshot settles it:

```
js2   guessed from plug order - click to set
      231d-0200- VKBsim Gladiator EVO R
      128 buttons · 10 axes · raw / no standard mapping

js3   your choice, remembered for this device
      231d-0201- VKBsim Gladiator EVO L
      128 buttons · 10 axes · raw / no standard mapping
```

Both sticks detected, named, VID/PID resolved, button and axis counts right,
full per-button panel rendering (`js2_button1` … `js2_button35`+ with browser
indices). **The detection and render work of the last three rounds is done.**

## 1. THE BIG ONE — they are js2 and js3. There is no js1.

Star Citizen profiles use **js1 and js2**. This page has assigned **js2 and
js3**, so every token it writes — `js2_button3`, `js3_button7` — names a device
slot that a two-stick Star Citizen setup does not have.

**This is almost certainly why Sleven's export "was not very good."** He tried
one, couldn't tell what was wrong with it, and assumed he'd done it wrong. He
hadn't. A file full of `js3_*` bindings is pointing at nothing.

**Cause, from reading `guessSlot`:**

```js
function guessSlot(p){
  if(padSlot[p.index]) return padSlot[p.index];   // <- sticky for the session
  var used=claimedSlots(), k, n;
  for(k in padSlot) used[padSlot[k]]=1;
  for(n=1;n<=8;n++) if(!used[n]){ padSlot[p.index]=n; return n; }
  ...
}
```

Two things combine:

- **`padSlot` is sticky.** Once an index gets a number it keeps it for the whole
  session, even if the device set later changes and that number is no longer
  sensible. Slots are never reconciled after the fact.
- **A remembered choice can claim a high number.** The screenshot shows js3 as
  *"your choice, remembered for this device"* — a stored localStorage choice of
  3, presumably from Sleven clicking swap earlier. `claimedSlots()` honours it,
  and nothing ever asks whether the resulting set is a sane, contiguous 1..N.

**Required behaviour:** with N sticks connected, the slots in use must be
exactly **1..N**, with no gaps and nothing above N. Two sticks → js1 and js2,
always. Swapping must exchange two slots, never push one to an unused higher
number.

Do this as a reconciliation pass over the whole connected set after any change —
connect, disconnect, or a manual swap — not by patching `guessSlot`'s search in
isolation. It's the *set* that must be valid, and only a whole-set check can
know that.

**Two things to keep, because they're right and I don't want them lost in the
fix:** a slot that came from an imported profile's GUIDs still wins over
everything (the game wrote it, it's authoritative), and a stored choice that has
gone out of range should be corrected and re-stored, not obeyed. Somebody with a
bad value in localStorage today must not be stuck with it forever.

**A migration thought, your call:** existing users already carry junk values.
Consider whether `CC_SLOT_KEY` needs a version bump so bad stored state is
dropped once rather than repaired repeatedly.

## 2. The left/right swap is still wrong, visibly

The screenshot shows **EVO R on the left, EVO L on the right** — the exact
complaint from before, still present after the slot-order fix. With §1 fixed
(js1 leftmost), check this actually resolves rather than assuming it does; if
the render order now follows slot correctly, R being js1 is a *labelling*
question, not a layout one, and the swap control is the answer.

## 3. Input stalls, and tab switching makes it worse

The tester readout on screen says **"— press something — / nothing yet"** with
"Reading your keys: ON", while both sticks are connected and rendering.

Sleven, live, in order:

> "the mouse and keyboard that works. when I click joysticks — oh, it got frozen
> again. so yep, clicking keyboard and mouse after you've clicked joystick and
> HOTAS seems to not work. oh but look now the buttons are showing up... and no,
> now the buttons don't work, now the joystick, the controls don't work anymore"

So it is **intermittent and tab-transition-related** — it works, then a switch
between Keyboard/Mouse and Joystick/HOTAS leaves it dead, and sometimes it comes
back on its own. That shape says a loop that stops and isn't restarted, or two
paths both managing `rafId`.

**Look hard at `rafId` ownership.** The tab handler cancels it directly
(`cancelAnimationFrame(rafId); rafId=null`), `startPoll()` sets it, `poll()`
re-arms it, `ccPresenceTick()` can start it, and `gamepadconnected` can start
it. That's five writers on one handle. A cancel racing a re-arm leaves a live
loop with `rafId===null` — after which `startPoll()` happily starts a *second*
loop — or a dead loop that every caller believes is running.

**The frame counter you added is the tool for this.** Switch tabs back and forth
and watch whether it keeps climbing, stalls, or jumps in steps that suggest two
loops. That's a measurement, not a theory.

**Do not fix this by wrapping things in try/catch or by starting extra loops.**
Give `rafId` one owner with explicit start/stop, and make every other caller go
through it.

## 4. Free data, now that we finally have some

The panel reports **128 buttons and 10 axes, "raw / no standard mapping"** for
each VKB. Worth noting for the prescriptive-labelling work: 128 is the HID
report size, not the number of physical controls — a Gladiator NXT EVO has
around 13. So a panel listing `js2_button1` … `js2_button128` is mostly empty
slots, which is what "Hide unused buttons" is presumably for. Check that control
defaults sensibly here, because 128 tiles per stick is a lot of nothing.

## 5. Acceptance

1. Two sticks connected → slots are exactly js1 and js2. Verify by reading the
   panel, not the code.
2. Swap exchanges the two; it never produces js3, and never leaves a gap.
3. A deliberately corrupted localStorage slot value is corrected, not obeyed.
4. An export with two sticks bound contains only `js1_*` and `js2_*` tokens, and
   an `<options>` block naming both devices.
5. Switch tabs KBM → JOY → KBM → JOY ten times; input still registers, and the
   frame counter shows one loop, still climbing.
6. Disconnect one stick and reconnect: slots reconcile to 1..N.
7. Build and deploy guard clean.

## 6. Report back

The frame-counter behaviour across the tab-switch test — that's the evidence for
§3, and if it turns out clean on your machine, say so plainly rather than
shipping a speculative fix, because then it needs his hardware again.
