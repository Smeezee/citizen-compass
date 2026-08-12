#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_device_diag.py - let the page say what it can actually see.

WHY THIS IS INSTRUMENTATION AND NOT ANOTHER FIX

/stick-test uses none of our detection code - a bare navigator.getGamepads()
on a plain requestAnimationFrame loop - and on the friend's machine it reported
both VKB sticks, every button and every axis, perfectly. So the browser, the
drivers, the HID mode and the permissions are all exonerated, and the fault is
in this page.

Three speculative fixes have already shipped against that symptom. C1 checked
and ruled out three more causes in the source, and stated plainly there was no
fourth hypothesis worth inventing. So this adds no fix at all: it makes the page
report what it sees, so a screenshot from the machine that actually has the
hardware becomes the diagnosis.

WHAT IT EXPOSES, AND WHY EACH ONE

  ccDiag.devices   what navigator.getGamepads() returns RIGHT NOW, re-read on
                   every call. If this is empty while /stick-test on the same
                   machine shows two sticks, the difference between the two
                   pages is the bug and the list of differences is short.
  ccDiag.tab       which device-mode tab is selected. poll() gates on it.
  ccDiag.polls     A REAL LIVENESS COUNT, incremented inside poll() itself.
                   Not rafId - I checked, and rafId is not a liveness signal:
                   it sat unchanged at 2 for three seconds while poll() had run
                   zero times, which reads identically to a healthy loop.
                   A number that climbs is proof; a handle is not.
  ccDiag.lastSeen  when the 400ms presence check last noticed a CHANGE, so a
                   stick that appears and is then forgotten is distinguishable
                   from one that was never seen.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_device_diag.py
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


# A real count of poll() bodies executed. See the header for why rafId is not
# an acceptable substitute.
sub("""function poll(){""",
    """var ccPollCount = 0;
var ccLastPresence = null;

/* What can this page see, right now? Read fresh every call - a cached answer
   is the one thing that would make this lie. */
window.ccDiag = function(){
  var g = navigator.getGamepads ? navigator.getGamepads() : [], names = [], i;
  for(i=0;i<g.length;i++) if(g[i]) names.push({
    id: g[i].id, index: g[i].index, mapping: g[i].mapping || '(none)',
    axes: g[i].axes.length, buttons: g[i].buttons.length
  });
  return {
    devices: names,
    tab: (typeof dev !== 'undefined') ? dev : '(unknown)',
    panelOpen: (typeof OPEN !== 'undefined') ? !!OPEN : null,
    capture: (typeof capture !== 'undefined') ? !!capture : null,
    rebinding: !!(window.KBREBIND && KBREBIND.listening()),
    polls: ccPollCount,
    lastPresenceChange: ccLastPresence
  };
};

function poll(){
  ccPollCount++;""",
    "diag-api")

sub("""  ccPresenceSig = sig;
  devDom = null;""",
    """  ccPresenceSig = sig;
  ccLastPresence = new Date().toLocaleTimeString();
  devDom = null;""",
    "presence-stamp")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: ccDiag() plus a real poll counter")
