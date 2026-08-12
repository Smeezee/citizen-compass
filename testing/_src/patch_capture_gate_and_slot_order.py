#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_capture_gate_and_slot_order.py - two things that made a working stick
look broken.

# 1. THE CAPTURE TOGGLE WAS SILENCING THE STICKS

Button and hat events fired only when the page-level `capture` flag was on:

    else if(typeof capture==="undefined"||capture){      <- buttons
    if(dir && (typeof capture==="undefined"||capture))   <- hats

Naming does NOT go through that flag - it comes from renderDevice() - so with
Capture OFF the panel still listed both sticks by name and relayed nothing from
them. Sleven, on a real HOTAS pair: "it's recognizing the sticks. It's just not
relaying the actual information from them." That is this, exactly.

It is worse in combination: the top search box is dead while Capture is ON, so
the advice was to turn Capture off - which silently disabled the sticks. Two
bugs that each have an innocent explanation add up to "nothing works and I do
not know why".

THE FIX: a rebind never depends on that toggle. While KBREBIND.listening() is
true, device input fires regardless - the same reasoning already applied to the
`dev` and `OPEN` gates, for the same reason: nothing in the UI says the toggle
affects rebinding, so it must not.

Outside a rebind the flag keeps its exact current meaning over the live tester
readout, which is what it was always for.

# 2. THE PANEL RENDERED IN USB ORDER, NOT SLOT ORDER

buildDevice() walked `list` straight from pads(), which is
navigator.getGamepads() order - OS enumeration, i.e. plug order. The LABELS were
right, because slotOf()/slotSource() resolve js1/js2 properly, so the panel
confidently showed "js1" above the stick sitting in the js2 column. Sleven: "the
right stick on the left and the left stick on the right".

THE FIX: sort by resolved slot immediately before rendering. Nothing about how
identity is RESOLVED changes - profile GUIDs, then the remembered choice, then a
guess that admits it is a guess. Only the render order, which was reading the
wrong thing.

Standard-mapping gamepads (xi) have no js slot and sort after the sticks, in
their existing relative order, so a controller never pushes a stick out of
place.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_capture_gate_and_slot_order.py
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


# ---------------------------------------------- 1. buttons ignore the toggle
sub("""        else if(typeof capture==="undefined"||capture){""",
    """        /* A REBIND IS NOT SUBJECT TO THE CAPTURE TOGGLE. That toggle governs
           the live tester readout; nothing in the UI ever said it also
           disables rebinding, and with it OFF the panel named both sticks
           while relaying nothing from them. */
        else if(ccInputAllowed()){""",
    "button-gate")

# ---------------------------------------------- 1. hats ignore it too
sub("""          if(dir && (typeof capture==="undefined"||capture))""",
    """          if(dir && ccInputAllowed())""",
    "hat-gate")

# the one place that decides it, so the two call sites cannot drift apart
sub("""/* ---- DEVICE PRESENCE ---""",
    """/* Is device input allowed to fire right now?
   Two reasons it may be: the Capture toggle is on (live tester readout), or a
   rebind is listening (which the toggle has no business affecting). One
   function so the button and hat call sites cannot drift apart. */
function ccInputAllowed(){
  if(window.KBREBIND && KBREBIND.listening()) return true;
  return (typeof capture === "undefined" || capture);
}

/* ---- DEVICE PRESENCE ---""",
    "input-allowed")

# ---------------------------------------------- 2. render in slot order
sub("""  if(!list.length){ host.innerHTML=emptyPanel(); devDom=null; return; }

  h='<div class="dvhead">';""",
    """  if(!list.length){ host.innerHTML=emptyPanel(); devDom=null; return; }

  /* RENDER IN SLOT ORDER, NOT PLUG ORDER. pads() returns
     navigator.getGamepads() order, which is OS enumeration - so js1 could be
     drawn on the right of js2 while both were labelled correctly. Sorting here
     changes only the layout; identity is still resolved by profile GUID, then
     remembered choice, then an admitted guess. Standard-mapping gamepads have
     no js slot and settle after the sticks without displacing them. */
  list = list.slice().sort(function(a,b){
    var sa = isStd(a) ? 99 : slotOf(a), sb = isStd(b) ? 99 : slotOf(b);
    if(sa !== sb) return sa - sb;
    return a.index - b.index;
  });

  h='<div class="dvhead">';""",
    "slot-order")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: rebind ignores the Capture toggle; panel renders in slot order")
