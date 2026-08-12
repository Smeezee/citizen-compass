#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_rebind_device_capture.py - let a rebind capture a stick, not just a key.

THE BUG: the rebind flow listened for keydown and mousedown only. Sleven, at a
friend's machine with a real HOTAS: "It says press a key or mouse button. But
when I actually click it with the flight sticks, it's not doing what it's
supposed to do."

WHY THIS IS A PATCH SCRIPT AND NOT AN EDIT TO keybinds.src.html

The order scoped this to keybinds.src.html. IT CANNOT BE DONE THERE. fireDev(),
poll() and startPoll() all live inside the DEVICE PANEL block, and
inject_engine.py rewrites that block from device_engine.js on every build. I
edited keybinds.src.html first, built, and the build silently reverted all three
- `grep` for the new guard found 0 occurrences in both the source and the built
page, with the build reporting success throughout.

That is the "patching only the source layer can silently do nothing" hazard the
2A pass-1 order warned about, arriving for real. device_engine.js is the single
writer for this code; this is the only place the change can live.

WHAT CHANGES, AND WHY EACH ONE IS NEEDED

1. fireDev() gets a rebind branch FIRST. It is already the one place a real
   device press has been turned into the game's own token - js1_button3,
   js1_hat1_up, xi_a - by the polling code above it. A rebind wants exactly that
   string, so it takes it from here rather than growing a second mapping beside
   it. Hats and the axis/button dual identity therefore come through correct for
   free, because nothing about their token production changes.

2. poll() must run during a rebind WHATEVER TAB IS SELECTED. It opens with
   `if(dev==="KBM"...) return`, so on the Keyboard/Mouse tab - which is where the
   action browser lives - the gamepad loop is not running at all. Without this,
   "press a joystick control" silently does nothing, which is precisely the
   symptom reported.

3. startPoll() has the same gate, so the loop can be started the moment a cell
   begins listening rather than only when somebody switches tabs.

BOTH HOSTS GET THIS. device_engine.js is injected into keybinds.src.html and
_layer.src.html alike. The index page has no rebind UI, so `window.KBREBIND` is
undefined there and every guard below is written to fall through to the existing
behaviour rather than assume the object exists.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_rebind_device_capture.py
"""
import io
import sys

P = "device_engine.js"
s = io.open(P, encoding="utf-8", newline="").read()


def sub(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit("ANCHOR %s appears %d times, expected 1" % (why, n))
    s = s.replace(old, new)


# ---------------------------------------- 1. the seam: fireDev already has the token
sub("""function fireDev(p,label,sc,press){
  var ro=$(ID_+'ro');""",
    """function fireDev(p,label,sc,press){
  /* REBIND FIRST, LIVE DISPLAY SECOND.
     This is the one place a joystick, HOTAS or gamepad press has already become
     the game's own token. A rebind needs exactly that string, so it is taken
     from here rather than reimplemented - which is also why hats arrive as
     their full compound token (js1_hat1_up) without special handling. */
  if(window.KBREBIND && KBREBIND.listening()){
    KBREBIND.capture(sc);
    return;
  }
  var ro=$(ID_+'ro');""", "firedev-seam")

# ---------------------------------------- 2. the loop must run during a rebind
sub("""function poll(){
  if(dev==="KBM"||(typeof OPEN!=="undefined"&&!OPEN)){ rafId=null; return; }""",
    """function poll(){
  /* A REBIND POLLS REGARDLESS OF THE SELECTED TAB. The action browser lists
     keyboard, mouse, joystick and gamepad bindings in ONE list, and nothing in
     the UI tells anybody to switch tabs before rebinding a stick input.
     Requiring it would be an undocumented precondition; not requiring it means
     this gate cannot depend on `dev` alone. */
  var rebinding = !!(window.KBREBIND && KBREBIND.listening());
  if((dev==="KBM"&&!rebinding)||(typeof OPEN!=="undefined"&&!OPEN&&!rebinding)){
    rafId=null; return; }""", "poll-gate")

# ---------------------------------------- 3. and so must the starter
sub("""function startPoll(){ if(rafId===null&&dev!=="KBM") rafId=requestAnimationFrame(poll); }""",
    """function startPoll(){
  /* Same reasoning as poll(): a rebind needs the loop running even on the
     Keyboard/Mouse tab, or the first stick press is never sampled and the cell
     simply sits there listening forever. */
  var rebinding = !!(window.KBREBIND && KBREBIND.listening());
  if(rafId===null&&(dev!=="KBM"||rebinding)) rafId=requestAnimationFrame(poll);
}""", "startpoll-gate")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: fireDev rebind seam, poll and startPoll ungated during a rebind")
